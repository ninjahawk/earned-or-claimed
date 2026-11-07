#!/usr/bin/env python3
"""ADV Q1/Q2 (post hoc, report job #656): paired AUROC differences on plant d vs EARNED, same items, source-clustered bootstrap (seed 20261107, B 2000, as p3_09_stats). Scores: Haiku omnibus L1 (phase 2, mean of 3), Sonnet/Opus omnibus L1, Haiku TM (mean of 5 incl. P4 repeats), Sonnet TM (mean of 4), word overlap (no model, p3_09_stats control 4). Writes data/p4_paired.json."""
import json,random,re,collections,statistics as S
SEED=20261107;B=2000;HK,SN,OP='claude-haiku-5-5','claude-sonnet-5-5','claude-opus-5-5'
Sc=collections.defaultdict(lambda:collections.defaultdict(dict));ARM={};SRC={}
def load(f): return [r for r in map(json.loads,open('private/'+f)) if r.get('score') is not None]
for r in load('test_runs.jsonl'):
    if r['level']=='L1': Sc['Haiku omnibus'][r['item']][r['rep']]=r['score']
    ARM[r['item']]=r['arm'];SRC[r['item']]=r['source']
for r in load('p3_runs.jsonl'):
    if r['level']=='L1' and r['model'] in(SN,OP): Sc[{SN:'Sonnet omnibus',OP:'Opus omnibus'}[r['model']]][r['item']][r['rep']]=r['score']
for f in ('p3_tm_test.jsonl','p4_tm_repeats.jsonl'):
    for r in load(f): Sc[{HK:'Haiku task-match',SN:'Sonnet task-match'}[r['model']]][r['item']][r['rep']]=r['score']
M={k:{i:S.mean(v.values()) for i,v in d.items()} for k,d in Sc.items()}
J={json.loads(l)['id']:json.loads(l) for l in open('private/export.jsonl')};PP={json.loads(l)['item']:json.loads(l) for l in open('private/plants_test.jsonl')}
W=lambda t:set(re.findall(r'[a-z]{4,}',(t or '').lower()))
def jac(i):
    t,r=(PP[i]['task'],PP[i]['report']) if i in PP else (J[int(i)]['task'],J[int(i)]['handoff']);a,b=W(t),W(r);return -len(a&b)/max(1,len(a|b))
pos=sorted(i for i in ARM if ARM[i]=='plant_d');neg=sorted(i for i in ARM if ARM[i]=='EARNED')
M['Word overlap (no model)']={i:jac(i) for i in pos+neg}
def auc(P,N): return sum(1 if p>q else .5 if p==q else 0 for p in P for q in N)/(len(P)*len(N))
def A(k,a,b): return auc([M[k][i] for i in a],[M[k][i] for i in b])
by=collections.defaultdict(lambda:[[],[]])
for i in pos: by[SRC[i]][0].append(i)
for i in neg: by[SRC[i]][1].append(i)
ks=sorted(by);rng=random.Random(SEED);samples=[]
for _ in range(B):
    a,b=[],[]
    for k in rng.choices(ks,k=len(ks)): a+=by[k][0];b+=by[k][1]
    if a and b: samples.append((a,b))
def ci(v): v=sorted(v);return [round(v[int(.025*len(v))],3),round(v[min(len(v)-1,int(.975*len(v)))],3)]
out={'n_d':len(pos),'n_EARNED':len(neg),'auroc':{},'diff':{}}
for k in M: out['auroc'][k]=[round(A(k,pos,neg),3)]+ci([A(k,a,b) for a,b in samples])
for x,y in [('Haiku task-match','Haiku omnibus'),('Haiku task-match','Word overlap (no model)'),('Sonnet task-match','Word overlap (no model)'),('Word overlap (no model)','Haiku omnibus'),('Sonnet omnibus','Haiku omnibus'),('Sonnet task-match','Sonnet omnibus')]:
    out['diff'][f'{x} - {y}']=[round(A(x,pos,neg)-A(y,pos,neg),3)]+ci([A(x,a,b)-A(y,a,b) for a,b in samples])
json.dump(out,open('data/p4_paired.json','w'),indent=1);print(json.dumps(out,indent=1))
