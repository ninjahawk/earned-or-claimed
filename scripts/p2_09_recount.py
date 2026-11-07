#!/usr/bin/env python3
"""Independent recount from raw runs with rank-sum AUROC (different formula from p2_08) and direct file reads; writes data/recount.json, fails if anything differs from data/test_results.json."""
import json,collections,statistics as S
def ranksum(p,n):
    a=sorted([(x,1) for x in p]+[(x,0) for x in n]); r=0;i=0
    while i<len(a):
        j=i
        while j<len(a) and a[j][0]==a[i][0]: j+=1
        rk=(i+1+j)/2
        r+=sum(rk for k in range(i,j) if a[k][1]); i=j
    return (r-len(p)*(len(p)+1)/2)/(len(p)*len(n))
M=collections.defaultdict(list);A={}
for l in open('private/test_runs.jsonl'):
    r=json.loads(l)
    if r.get('score') is not None: M[r['item'],r['level']].append(r['score']); A[r['item']]=r['arm']
assert all(len(v)==3 for v in M.values()),'repeats'
T=json.load(open('data/test_results.json'))
def au(arms,lv):
    return ranksum([S.mean(v) for (i,x),v in M.items() if x==lv and A[i] in arms],[S.mean(v) for (i,x),v in M.items() if x==lv and A[i]=='EARNED'])
out={};bad=[]
sets=dict(natural=(['UNEARNED'],T['natural']),cde=(['plant_c','plant_d','plant_e'],T['planted']['lead_types_cde']))
for t in 'abcde': sets[t]=(['plant_'+t],T['planted']['per_type'][t])
for k,(arms,row) in sets.items():
    for lv in('L1','L2'):
        v=round(au(arms,lv),3); out[f'{k}/{lv}']=v
        if v!=row[lv]['auroc']: bad.append((k,lv,v,row[lv]['auroc']))
    n=sum(1 for (i,x) in M if x=='L1' and A[i] in arms); out[f'{k}/n']=n
    if n!=row['n_pos']: bad.append((k,'n'))
G=[json.loads(l) for l in open('private/gate_test.jsonl')]
for arm,row in [('UNEARNED',T['gate']['natural']['UNEARNED']),('EARNED',T['gate']['natural']['EARNED'])]+[('plant_'+t,T['gate']['planted'][t]) for t in 'abcde']:
    x=[g for g in G if g['arm']==arm]; g2=sum(g['g1_pass'] and (g.get('g2') or 0)<60 for g in x)
    out[f'gate/{arm}']=[len(x),sum(g['g1_pass'] for g in x),g2]
    if [len(x),sum(g['g1_pass'] for g in x),g2]!=[row['n'],row['g1_pass'],row['g2_pass']]: bad.append((arm,'gate'))
out['mismatches']=bad; json.dump(out,open('data/recount.json','w'),indent=1); print(out); assert not bad
