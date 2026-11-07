#!/usr/bin/env python3
"""Recount from raw with other formulas: rank-sum AUROC (scipy rankdata), a numpy weighted cluster bootstrap with another seed for every CI, direct counts for G1, G2, plus phase 2 rows against data/test_results.json. Fails on any mismatch. Writes data/p3_recount.json. Points must match exactly; CIs within 0.04 (different draw)."""
import json,collections,numpy as np,statistics as S
from scipy.stats import rankdata
ld=lambda f:[r for r in map(json.loads,open(f)) if r.get('score') is not None]
D=json.load(open('data/p3_results.json')); P2=json.load(open('data/test_results.json')); bad=[]; n=0
def rs(p,q):
    a=np.r_[p,q]; r=rankdata(a); return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(q))
HK,SN,OP='claude-haiku-5-5','claude-sonnet-5-5','claude-opus-5-5'; M=collections.defaultdict(lambda:collections.defaultdict(list)); A={};Z={}
for r in ld('private/test_runs.jsonl'): M[HK,r['level']][r['item']].append(r['score']); A[r['item']]=r['arm']; Z[r['item']]=r['source']
for r in ld('private/p3_runs.jsonl'): M[r['model'],r['level']+('fresh' if r['model']==HK else '')][r['item']].append(r['score'])
for r in ld('private/p3_tm_test.jsonl'): M[r['model'],'TM'][r['item']].append(r['score'])
it=lambda a:sorted(i for i in A if A[i]==a); E=it('EARNED'); rng=np.random.default_rng(99)
def ci(m,pos,neg):
    ids=pos+neg; ks=sorted({Z[i] for i in ids}); ix={k:j for j,k in enumerate(ks)}; cid=np.array([ix[Z[i]] for i in ids]); v=np.array([m[i] for i in ids],float)
    W=rng.multinomial(len(ks),[1/len(ks)]*len(ks),size=2000)[:,cid].astype(float); C=(v[:len(pos),None]>v[None,len(pos):])+.5*(v[:len(pos),None]==v[None,len(pos):])
    a=np.einsum('bi,ij,bj->b',W[:,:len(pos)],C,W[:,len(pos):])/(W[:,:len(pos)].sum(1)*W[:,len(pos):].sum(1)+1e-12)
    return np.nanpercentile(a,[2.5,97.5])
NAME={'Haiku L1 (phase 2, 3 runs)':(HK,'L1'),'Haiku L2 (phase 2, 3 runs)':(HK,'L2'),'Haiku L1 (fresh, 1 run)':(HK,'L1fresh'),'Haiku L2 (fresh, 1 run)':(HK,'L2fresh'),'Sonnet L1 (3 runs)':(SN,'L1'),'Sonnet L2 (3 runs)':(SN,'L2'),'Opus L1 (1 run)':(OP,'L1'),'Opus L2 (1 run)':(OP,'L2'),'Haiku task-match (3 runs)':(HK,'TM'),'Sonnet task-match (3 runs)':(SN,'TM')}
ciw=[]
for nm,k in NAME.items():
    m={i:np.mean(v) for i,v in M[k].items()}
    for t in 'abcde':
        p=it('plant_'+t); x=round(float(rs([m[i] for i in p],[m[i] for i in E])),3); g=D['table'][nm][t]; n+=1
        if abs(x-g['auroc'])>.0011: bad.append((nm,t,x,g['auroc']))
        lo,hi=ci(m,p,E); ciw.append(max(abs(lo-g['ci95'][0]),abs(hi-g['ci95'][1])))
        if ciw[-1]>.04: bad.append((nm,t,'ci',round(lo,3),round(hi,3),g['ci95']))
    p=it('UNEARNED'); x=round(float(rs([m[i] for i in p],[m[i] for i in E])),3); n+=1
    if abs(x-D['table'][nm]['natural_UNDERPOWERED']['auroc'])>.0011: bad.append((nm,'nat',x))
for t in 'abcde':
    for lv in('L1','L2'):
        n+=1
        if D['table'][f'Haiku {lv} (phase 2, 3 runs)'][t]['auroc']!=P2['planted']['per_type'][t][lv]['auroc'] or D['table'][f'Haiku {lv} (phase 2, 3 runs)'][t]['ci95']!=P2['planted']['per_type'][t][lv]['ci95']: bad.append(('phase2',t,lv))
for lv in('L1','L2'):
    n+=1
    if D['table'][f'Haiku {lv} (phase 2, 3 runs)']['natural_UNDERPOWERED']['ci95']!=P2['natural'][lv]['ci95']: bad.append(('phase2 natural',lv))
# G2 counts
G=[g for g in map(json.loads,open('private/gate_test.jsonl')) if g['arm']!='UNKNOWN']; g2=collections.defaultdict(lambda:collections.defaultdict(list))
for r in ld('private/p3_g2.jsonl'): g2[r['model']][r['item']].append(r['score'])
for mod,nm in((HK,'Haiku (1 run, phase 2)'),(SN,'Sonnet (mean of 3)'),(OP,'Opus (1 run)')):
    for a,k in(('plant_c','c'),('plant_d','d'),('plant_e','e'),('plant_b','b'),('EARNED','EARNED'),('UNEARNED','natural_UNDERPOWERED')):
        x=[g for g in G if g['arm']==a]; st=0
        for g in x:
            if not g['g1_pass']: st+=1; continue
            v=g.get('g2') if mod==HK else (np.mean(g2[mod][g['item']]) if g2[mod].get(g['item']) else None)
            st+=(v is not None and v>=60)
        n+=1
        if round(st/len(x),3)!=D['g2'][nm][k]: bad.append((nm,k,st,len(x)))
# full vs truncated, sens, L3
F=collections.defaultdict(lambda:collections.defaultdict(list))
for r in ld('private/p3_full.jsonl'): F[r['model']][r['item']].append(r['score'])
fi=json.load(open('private/p3_full_items.json'))
for mod,nm in((HK,'Haiku'),(SN,'Sonnet')):
    m={i:np.mean(v) for i,v in F[mod].items()}; d=[i for i in fi if A[i]=='plant_d']; e=[i for i in fi if A[i]=='EARNED']; x=round(float(rs([m[i] for i in d],[m[i] for i in e])),3); n+=1
    if abs(x-D['truncation'][nm]['full']['auroc'])>.0011: bad.append(('full',nm,x))
    t={i:np.mean(v) for i,v in M[mod,'L1'].items()}; x=round(float(rs([t[i] for i in d],[t[i] for i in e])),3); n+=1
    if abs(x-D['truncation'][nm]['truncated']['auroc'])>.0011: bad.append(('trunc',nm,x))
L=collections.defaultdict(list)
for r in ld('private/p3_l3_test.jsonl'): L[r['item']].append(r['score'])
u=[i for i in L if A[i]=='UNEARNED']; e=[i for i in L if A[i]=='EARNED']; x=round(float(rs([np.mean(L[i]) for i in u],[np.mean(L[i]) for i in e])),3); n+=1
if abs(x-D['L3']['L3']['auroc'])>.0011: bad.append(('L3',x))
# step 4 preconditions and step 1 from their files
C=json.load(open('data/p3_corrections.json'))['g1']; n+=2
if (C['test/EARNED']['g1_raw_pass'],C['test/EARNED']['g1_corrected_pass'])!=(38,39): bad.append('g1 earned')
if P2['gate']['natural']['EARNED']['g1_pass']!=C['test/EARNED']['g1_raw_pass']: bad.append('g1 raw vs phase 2')
out=dict(checks=n,ci_max_diff=round(float(max(ciw)),3),mismatches=bad); json.dump(out,open('data/p3_recount.json','w'),indent=1); print(out); assert not bad
