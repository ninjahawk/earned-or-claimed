#!/usr/bin/env python3
"""AUROC by arm vs EARNED, per level, from a run file. Dev reporting. Usage: p2_05_devstats.py <file> [tag]"""
import sys,json,collections,statistics as S
sys.path.insert(0,'scripts'); from p2_lib import auc
R=[json.loads(l) for l in open(sys.argv[1])]; R=[r for r in R if r.get('score') is not None]
M=collections.defaultdict(list); A={}
for r in R: M[r['item'],r['level']].append(r['score']); A[r['item']]=r['arm']
out={}
for lv in('L1','L2'):
    neg=[S.mean(v) for (i,l),v in M.items() if l==lv and A[i]=='EARNED']
    for arm in sorted(set(A.values())-{'EARNED'}):
        pos=[S.mean(v) for (i,l),v in M.items() if l==lv and A[i]==arm]
        out[f'{lv}/{arm}']=dict(auc=round(auc(pos,neg),3),mean=round(S.mean(pos),1),n=len(pos))
    out[f'{lv}/EARNED_mean']=round(S.mean(neg),1)
for k,v in out.items(): print(k,v)
print('calls',len(R),'cost',round(sum(r.get('cost') or 0 for r in R),3),'tok_in/call',round(S.mean(r['tok_in'] for r in R)))
