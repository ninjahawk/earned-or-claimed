#!/usr/bin/env python3
"""Step 5, optional: second narrow check. Usage: p3_13_absent.py dev|test ver repeats [deadline]. Test refuses unless data/FROZEN_P3.json names the version. Writes private/p3_ab_<split>.jsonl, prints AUROC vs EARNED per arm and model."""
import sys,random,collections,statistics as St; sys.path.insert(0,'scripts'); from p3_lib import *; import p3_prompts as Q
split,ver,rep=sys.argv[1],sys.argv[2],int(sys.argv[3]); dl=int(sys.argv[4]) if len(sys.argv)>4 else 540
if split=='test': assert json.load(open('data/FROZEN_P3.json')).get('absent')==ver,'not frozen'
it=test_items(split)
if split=='dev': it=[x for x in it if x['arm'] in('EARNED','UNEARNED','plant_c','plant_d','plant_e')]
I={x['item']:x for x in it}; SRC={x['item']:x['source'] for x in it}; A={x['item']:x['arm'] for x in it}; out=f'private/p3_ab_{split}.jsonl'
jobs=[dict(item=x['item'],arm=x['arm'],level='AB',rep=r,model=m,source=x['source'],ver=ver) for m in(HAIKU_,SONNET) for x in it for r in range(rep)]
run(jobs,out,lambda j:call(Q.AB[ver],Q.tm_prompt(I[j['item']]['task'],I[j['item']]['report']),model=j['model']),deadline=dl)
R=[json.loads(l) for l in open(out)]; res={}
for m in(HAIKU_,SONNET):
    d=collections.defaultdict(list)
    for r in R:
        if r['model']==m and r.get('score') is not None: d[r['item']].append(r['score'])
    s={i:St.mean(v) for i,v in d.items()}; E=sorted(i for i in s if A[i]=='EARNED'); res[m]={'EARNED_mean':round(St.mean(s[i] for i in E),1)}
    for arm in sorted(set(A.values())-{'EARNED'}):
        P=sorted(i for i in s if A[i]==arm)
        if not P: continue
        rng=random.Random(20261107); by=collections.defaultdict(lambda:[[],[]])
        for i in P: by[SRC[i]][0].append(i)
        for i in E: by[SRC[i]][1].append(i)
        ks=sorted(by); v=[]
        for _ in range(2000):
            a,b=[],[]
            if arm=='UNEARNED': a=rng.choices(P,k=len(P)); b=rng.choices(E,k=len(E))
            else:
                for k in rng.choices(ks,k=len(ks)): a+=by[k][0]; b+=by[k][1]
            if a and b: v.append(auc([s[i] for i in a],[s[i] for i in b]))
        v.sort(); res[m][arm]=dict(auroc=round(auc([s[i] for i in P],[s[i] for i in E]),3),ci95=[round(v[int(.025*len(v))],3),round(v[min(len(v)-1,int(.975*len(v)))],3)],n=len(P))
print(json.dumps(res,indent=0))
if split=='test': json.dump(dict(version=ver,repeats=rep,n_earned=45,results=res,note='Text check, not an evidence result. Natural row UNDERPOWERED (7 < 15). Planted rows planted. No bar, no reading.'),open('data/p3_absent.json','w'),indent=1)
