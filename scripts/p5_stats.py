#!/usr/bin/env python3
"""P5 stats, shared. AUROC (higher score = more suspect), clustered percentile bootstrap (seed 20261107, B 2000; clusters =
report-source job: EARNED -> own id, d2 -> partner y, p -> x, resampled jointly for both classes), paired differences on
the same draws. No-model baselines: word overlap (Jaccard over [a-z]{4,}, as P3 control 4) and BM25 (task as query, report
as document, k1 1.5, b 0.75, tokens [a-z0-9]{3,}, IDF over all scrubbed claim reports of the split); both on full stored text,
suspicion = minus similarity.
Usage: p5_stats.py dev   -> data/p5_dev_baselines.json (no model) + power numbers for the prereg."""
import sys,json,re,math,random,collections,statistics as S
sys.path.insert(0,'scripts')
SEED=20261107;B=2000
def auc(P,N):
    if not P or not N: return None
    return sum((p>q)+.5*(p==q) for p in P for q in N)/(len(P)*len(N))
W4=lambda s:set(re.findall(r'[a-z]{4,}',(s or '').lower()))
def overlap(task,rep): a,b=W4(task),W4(rep); return -len(a&b)/max(1,len(a|b))
TOK=lambda s:re.findall(r'[a-z0-9]{3,}',(s or '').lower())
class BM25:
    def __init__(s,docs,k1=1.5,b=.75):
        s.k1,s.b=k1,b; D=[TOK(d) for d in docs]; s.N=len(D); s.avg=sum(map(len,D))/max(1,s.N); df=collections.Counter(t for d in D for t in set(d))
        s.idf={t:math.log(1+(s.N-n+.5)/(n+.5)) for t,n in df.items()}
    def score(s,q,d):
        d=TOK(d); tf=collections.Counter(d); L=len(d); out=0.
        for t in set(TOK(q)):
            if t in tf: f=tf[t]; out+=s.idf.get(t,math.log(1+(s.N+.5)/.5))*f*(s.k1+1)/(f+s.k1*(1-s.b+s.b*L/s.avg))
        return out
def draws(items,seed=SEED,b=B):
    """items: dict item->(cls in {'pos','neg'}, cluster). Returns list of (pos list, neg list) per resample; joint cluster draw."""
    by=collections.defaultdict(lambda:[[],[]])
    for i,(c,k) in items.items(): by[k][0 if c=='pos' else 1].append(i)
    ks=sorted(by,key=str); rng=random.Random(seed); out=[]
    for _ in range(b):
        P,N=[],[]
        for k in rng.choices(ks,k=len(ks)): P+=by[k][0]; N+=by[k][1]
        if P and N: out.append((P,N))
    return out
def pct(v,lo=.025,hi=.975): v=sorted(v); return [round(v[int(lo*len(v))],3),round(v[min(len(v)-1,int(hi*len(v)))],3)]
def cell(sc,items,dr):
    P=[i for i,(c,_) in items.items() if c=='pos']; N=[i for i,(c,_) in items.items() if c=='neg']
    return [round(auc([sc[i] for i in P],[sc[i] for i in N]),3)]+pct([auc([sc[i] for i in p],[sc[i] for i in n]) for p,n in dr])
def paired(sx,sy,items,dr,alpha=.05):
    P=[i for i,(c,_) in items.items() if c=='pos']; N=[i for i,(c,_) in items.items() if c=='neg']
    A=lambda s,p,n:auc([s[i] for i in p],[s[i] for i in n]); v=[A(sx,p,n)-A(sy,p,n) for p,n in dr]
    return dict(diff=round(A(sx,P,N)-A(sy,P,N),3),ci=pct(v,alpha/2,1-alpha/2),sd=round(S.pstdev(v),4))
def split_items(split):
    """Items of P5 for a split: EARNED (neg) + plants d2, p (pos). Returns dict item->dict(task,report,arm,cluster)."""
    from p2_lib import raw_rows,labels,to_task,to_report
    R=raw_rows(); L=labels(); it={}
    for i,d in L.items():
        if d['split']==split and d['claim'] and d['label']=='EARNED':
            it[str(i)]=dict(task=to_task(R[i]['task']),report=to_report(R[i]['handoff']),arm='EARNED',cluster=i)
    for l in open(f'private/p5_plants_{split}.jsonl'):
        p=json.loads(l); it[p['item']]=dict(task=p['task'],report=p['report'],arm=p['type'],cluster=p['source'])
    allrep=[to_report(R[i]['handoff']) for i,d in L.items() if d['split']==split and d['claim']]
    return it,BM25(allrep)
def baselines(it,bm):
    return {'overlap':{i:overlap(x['task'],x['report']) for i,x in it.items()},'bm25':{i:-bm.score(x['task'],x['report']) for i,x in it.items()}}
def cells_for(it,t): return {i:('pos' if x['arm']==t else 'neg',x['cluster']) for i,x in it.items() if x['arm'] in(t,'EARNED')}
if __name__=='__main__' and sys.argv[1:]==['dev']:
    it,bm=split_items('dev'); bl=baselines(it,bm); out={'split':'dev','n':collections.Counter(x['arm'] for x in it.values()),'auroc':{},'paired_overlap_minus_bm25':{}}
    for t in('d2','p'):
        items=cells_for(it,t); dr=draws(items)
        for k in bl: out['auroc'][f'{k}/{t}']=cell(bl[k],items,dr)
        out['paired_overlap_minus_bm25'][t]=paired(bl['overlap'],bl['bm25'],items,dr)
    # power: SE of a model-vs-baseline paired AUROC difference measured in P4 (Haiku tm1 - overlap on plant d, 15 pos
    # clusters vs 45 EARNED), scaled by sqrt(15/n_pos_clusters); MDE at 80% power, two-sided .05 = 2.80 x SE.
    p4=json.load(open('data/p4_paired.json'))['diff']['Haiku task-match - Word overlap (no model)']; se15=(p4[2]-p4[1])/3.92
    ti,_=split_items('test'); out['power']={'se_p4_15pos':round(se15,4)}
    for t in('d2','p'):
        k=len({x['cluster'] for x in ti.values() if x['arm']==t}); se=se15*math.sqrt(15/k)
        out['power'][t]=dict(test_pos_items=sum(x['arm']==t for x in ti.values()),test_pos_clusters=k,se=round(se,4),mde80=round(2.8*se,3),detects_0_10=2.8*se<=.10)
    json.dump(out,open('data/p5_dev_baselines.json','w'),indent=1); print(json.dumps(out,indent=1))
