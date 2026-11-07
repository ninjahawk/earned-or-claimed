#!/usr/bin/env python3
"""P4 stats: task-match on plant d vs EARNED, per repeat and pooled means (old reps 0-2 + new). Same pair-count AUROC and source-clustered bootstrap as p3_14_brain_recount.py. Writes data/p4_tm_repeats.json."""
import json,random,collections,statistics as S
W='private/'
HK,SN='claude-haiku-5-5','claude-sonnet-5-5'
arm={};src={};sc=collections.defaultdict(lambda:collections.defaultdict(dict))
for f in ('p3_tm_test.jsonl','p4_tm_repeats.jsonl'):
    for l in open(W+f):
        r=json.loads(l)
        if r['arm'] not in('EARNED','plant_d') or r.get('score') is None: continue
        arm[r['item']]=r['arm'];src[r['item']]=r['source'];sc[r['model']][r['item']][r['rep']]=r['score']
def auc(P,N): return sum(1 if p>q else .5 if p==q else 0 for p in P for q in N)/(len(P)*len(N))
def boot(m,pos,neg,B=3000,seed=7):
    rnd=random.Random(seed);bys=collections.defaultdict(lambda:([],[]))
    for i in pos: bys[src[i]][0].append(m[i])
    for i in neg: bys[src[i]][1].append(m[i])
    ks=list(bys);out=[]
    for _ in range(B):
        P=[];N=[]
        for k in rnd.choices(ks,k=len(ks)): P+=bys[k][0];N+=bys[k][1]
        if P and N: out.append(auc(P,N))
    out.sort();return out[int(.025*len(out))],out[int(.975*len(out))]
pos=[i for i in arm if arm[i]=='plant_d'];neg=[i for i in arm if arm[i]=='EARNED']
out={'n_d':len(pos),'n_EARNED':len(neg)}
for name,m,reps in (('Haiku',HK,5),('Sonnet',SN,4)):
    d=sc[m];assert all(len(d[i])==reps for i in pos+neg),name
    per={r:round(auc([d[i][r] for i in pos],[d[i][r] for i in neg]),3) for r in range(reps)}
    def mean_over(rs):
        mm={i:sum(d[i][r] for r in rs)/len(rs) for i in pos+neg}; a=auc([mm[i] for i in pos],[mm[i] for i in neg]); lo,hi=boot(mm,pos,neg); return [round(a,3),round(lo,3),round(hi,3),a>=.75 and lo>.5]
    old=list(range(3))
    out[name]={'reps':reps,'per_repeat_auroc':per,'per_repeat_sd':round(S.stdev(per.values()),3),'per_repeat_range':[min(per.values()),max(per.values())],
               'mean_old3':mean_over(old),'mean_all':mean_over(list(range(reps)))}
json.dump(out,open('data/p4_tm_repeats.json','w'),indent=1);print(json.dumps(out,indent=1))
