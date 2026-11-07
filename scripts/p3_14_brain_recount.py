import json,random,collections
W='ORCH_ROOT/work/apart-swarm/private/'
def rows(f):
    for l in open(W+f):
        yield json.loads(l)
arm={};src={}
scores=collections.defaultdict(lambda:collections.defaultdict(list)); nulls=collections.Counter()
HK,SN,OP='claude-haiku-5-5','claude-sonnet-5-5','claude-opus-5-5'
for r in rows('test_runs.jsonl'):
    arm[r['item']]=r['arm'];src[r['item']]=r['source']
    if r.get('score') is None: nulls['hk'+r['level']]+=1;continue
    scores[('Haiku',r['level'])][r['item']].append(r['score'])
for r in rows('p3_runs.jsonl'):
    n={HK:'HaikuFresh',SN:'Sonnet',OP:'Opus'}[r['model']]
    if r.get('score') is None: nulls[n+r['level']]+=1;continue
    scores[(n,r['level'])][r['item']].append(r['score'])
for r in rows('p3_tm_test.jsonl'):
    n={HK:'Haiku',SN:'Sonnet'}[r['model']]
    if r.get('score') is None: nulls[n+'TM']+=1;continue
    scores[(n,'TM')][r['item']].append(r['score'])
def auc(P,N):
    # direct pair count, not rank sum
    w=0
    for p in P:
        for q in N: w+= 1 if p>q else .5 if p==q else 0
    return w/(len(P)*len(N))
def boot(m,pos,neg,B=3000,seed=7):
    # cluster by source, resample sources, python only
    rnd=random.Random(seed);bys=collections.defaultdict(lambda:([],[]))
    for i in pos: bys[src[i]][0].append(m[i])
    for i in neg: bys[src[i]][1].append(m[i])
    ks=list(bys);out=[]
    for _ in range(B):
        P=[];N=[]
        for k in rnd.choices(ks,k=len(ks)):
            P+=bys[k][0];N+=bys[k][1]
        if P and N: out.append(auc(P,N))
    out.sort();return out[int(.025*len(out))],out[int(.975*len(out))]
items=lambda a:[i for i in arm if arm[i]==a]
E=items('EARNED');print('n EARNED',len(E),'nulls',dict(nulls))
for t in 'cd':
    pos=items('plant_'+t)
    print('plant',t,'n',len(pos))
    for k in [('Haiku','L1'),('Haiku','L2'),('Sonnet','L1'),('Sonnet','L2'),('Opus','L1'),('Opus','L2'),('Haiku','TM'),('Sonnet','TM')]:
        d=scores[k];m={i:sum(v)/len(v) for i,v in d.items()}
        reps=collections.Counter(len(d[i]) for i in pos+E if i in d)
        miss=[i for i in pos+E if i not in m]
        P=[m[i] for i in pos if i in m];N=[m[i] for i in E if i in m]
        a=auc(P,N);lo,hi=boot(m,[i for i in pos if i in m],[i for i in E if i in m])
        print(f'  {k[0]:7}{k[1]:3} auc {a:.3f} [{lo:.3f},{hi:.3f}] pass {a>=.75 and lo>.5} reps {dict(reps)} missing {len(miss)}')
