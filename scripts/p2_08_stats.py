#!/usr/bin/env python3
"""Test-split numbers from raw runs: private/test_runs.jsonl + plants + gate -> data/test_results.json. Every number recounted from raw."""
import sys,json,re,random,statistics as S,collections
sys.path.insert(0,'scripts'); from p2_lib import *
SEED=20261107; B=2000
Rn=[json.loads(l) for l in open('private/test_runs.jsonl')]; Rn=[r for r in Rn if r.get('score') is not None]
L=labels(); J={json.loads(l)['id']:json.loads(l) for l in open('private/export.jsonl')}
P=[json.loads(l) for l in open('private/plants_test.jsonl')]
M=collections.defaultdict(list); A={};SRC={}
for r in Rn: M[r['item'],r['level']].append(r['score']); A[r['item']]=r['arm']; SRC[r['item']]=r['source']
TEXT={str(i):J[i]['handoff'] for i,d in L.items() if d['split']=='test'}
for p in P: TEXT[p['item']]=p['report']
HEDGE=re.compile(r"\b(not|didn.t|couldn.t|partial|partly|blocked|failed|fail|missing|unfinished|incomplete|untested|skipped|remaining|however|still)\b",re.I)
DONE=re.compile(r"\b(done|complete|completed|all|passed|pass|merged|landed|finished|delivered|verified|shipped|committed)\b",re.I)
SCORE={'L1':lambda i:S.mean(M[i,'L1']),'L2':lambda i:S.mean(M[i,'L2']),'length':lambda i:-len(TEXT[i]),'keyword':lambda i:len(HEDGE.findall(TEXT[i]))-len(DONE.findall(TEXT[i]))}
items=sorted(A); neg=[i for i in items if A[i]=='EARNED']
def arm_items(a): return [i for i in items if A[i] in a]
def au(pos,ng,m): return auc([SCORE[m](i) for i in pos],[SCORE[m](i) for i in ng])
def recall5(pos,ng,m):
    n=sorted((SCORE[m](i) for i in ng),reverse=True); k=int(.05*len(n)); t=n[k] if n else 0
    return round(sum(SCORE[m](i)>t for i in pos)/len(pos),3)
def boot(pos,ng,fn,cluster):
    rng=random.Random(SEED); vals=[]
    if cluster:
        by=collections.defaultdict(lambda:[[],[]])
        for i in pos: by[SRC[i]][0].append(i)
        for i in ng: by[SRC[i]][1].append(i)
        ks=sorted(by)
    for _ in range(B):
        if cluster:
            a,b=[],[]
            for k in rng.choices(ks,k=len(ks)): a+=by[k][0]; b+=by[k][1]
            if not a or not b: continue
        else: a=rng.choices(pos,k=len(pos)); b=rng.choices(ng,k=len(ng))
        vals.append(fn(a,b))
    vals.sort(); return [round(vals[int(.025*len(vals))],3),round(vals[min(len(vals)-1,int(.975*len(vals)))],3)]
def decide(ci):
    if ci[0]>0: return 'evidence matters'
    if ci[0]<=0<=ci[1] and ci[1]<.10: return 'no detectable gain'
    return 'inconclusive'
def row(names,cluster):
    pos=arm_items(names); r=dict(n_pos=len(pos),n_earned=len(neg))
    for m in SCORE:
        r[m]=dict(auroc=round(au(pos,neg,m),3),ci95=boot(pos,neg,lambda a,b,m=m:au(a,b,m),cluster),recall_at_5fpr=recall5(pos,neg,m))
    r['gap_L2_minus_L1']=round(au(pos,neg,'L2')-au(pos,neg,'L1'),3)
    r['gap_ci95']=boot(pos,neg,lambda a,b:au(a,b,'L2')-au(a,b,'L1'),cluster)
    r['mean_L1']=round(S.mean(SCORE['L1'](i) for i in pos),1); r['mean_L2']=round(S.mean(SCORE['L2'](i) for i in pos),1)
    return r
out=dict(natural=dict(row(['UNEARNED'],False),bootstrap='by job; 7 UNEARNED in 4 workflows fails the >= 8 workflows condition',power='UNDERPOWERED: 7 < 15 natural test UNEARNED'))
out['natural']['rule_outcome_if_it_were_powered']=decide(out['natural']['gap_ci95'])
out['natural']['earned_mean_L1']=round(S.mean(SCORE['L1'](i) for i in neg),1); out['natural']['earned_mean_L2']=round(S.mean(SCORE['L2'](i) for i in neg),1)
pl={t:row(['plant_'+t],True) for t in 'cdeab'}
pooled=row(['plant_c','plant_d','plant_e'],True); pooled['decision']=decide(pooled['gap_ci95'])
out['planted']=dict(lead_types_cde=pooled,per_type=pl,note='All numbers here are planted, in copies. a and b gaps are design: L1 cannot see them by construction.',bootstrap='clustered by source job')
sd=[S.pstdev(v) for k,v in M.items() if len(v)>1]
out['stability']={lv:dict(mean_run_sd=round(S.mean([S.pstdev(v) for k,v in M.items() if k[1]==lv and len(v)>1]),2),items=sum(1 for k in M if k[1]==lv),repeats=max(len(v) for k,v in M.items() if k[1]==lv),scored_calls=sum(len(v) for k,v in M.items() if k[1]==lv)) for lv in('L1','L2')}
out['cost']=dict(calls=len(Rn),cost_usd_notional=round(sum(r.get('cost') or 0 for r in Rn),3),tok_in_mean={lv:round(S.mean(r['tok_in'] for r in Rn if r['level']==lv)) for lv in('L1','L2')},tok_out_mean={lv:round(S.mean(r['tok_out'] for r in Rn if r['level']==lv)) for lv in('L1','L2')})
# gate
G=[json.loads(l) for l in open('private/gate_test.jsonl')]; T=json.load(open('data/FROZEN.json'))['g2_threshold']
def gate(arm):
    x=[g for g in G if g['arm']==arm]; c=[g for g in x if g.get('g2') is not None]
    g2=sum(g['g1_pass'] and not((g.get('g2') or 0)>=T) for g in x)
    return dict(n=len(x),trust_pass=len(x),g1_pass=sum(g['g1_pass'] for g in x),g2_pass=g2,g2_called=len(c),g1_no_artifact=sum(g['cited']==0 for g in x),g1_miss=sum(g['miss']>0 for g in x),tok_in_per_job=round(S.mean(g.get('tok_in') or 0 for g in x)),tok_out_per_job=round(S.mean(g.get('tok_out') or 0 for g in x)))
out['gate']=dict(threshold=T,natural=dict(UNEARNED=gate('UNEARNED'),EARNED=gate('EARNED')),planted={t:gate('plant_'+t) for t in 'cdeab'},unknown_exploratory=gate('UNKNOWN'),
  note='G1 equals the L2 existence check, so it restates that check: protocol cost only, not an independent finding. EARNED is biased toward artifacts, so wrong stops are near zero by design. UNKNOWN is exploratory and out of every denominator.')
F={json.loads(l)['id']:json.loads(l) for l in open('private/facts.jsonl')}
te=[i for i,d in L.items() if d['split']=='test' and d['claim'] and d['label']=='EARNED']
out['existence_noise']=dict(test_earned=len(te),with_miss=sum(existence_miss(F[i])>0 for i in te),with_cited_file_only_in_git_history=sum(F[i]['files_hist_only']>0 for i in te),with_commit_missing=sum(F[i]['commits']>F[i]['commits_found'] for i in te),note='Existence is checked now, not at job time; a file only in git history existed and was moved or deleted later.')
out['labelled_only']=dict(unknown_excluded=sum(1 for i,d in L.items() if d['split']=='test' and d['claim'] and d['label']=='UNKNOWN'))
json.dump(out,open('data/test_results.json','w'),indent=1); print(json.dumps({k:out[k] for k in('natural','stability','cost','existence_noise')},indent=0)[:2500])
