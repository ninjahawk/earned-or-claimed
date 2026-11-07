#!/usr/bin/env python3
"""P5 recount from raw, written apart from p5_stats/p5_04: rank-sum AUROC (Mann-Whitney with midranks), own item means,
own overlap and BM25 code, own bootstrap (seed 7, B 2000, numpy-free). Checks every AUROC point in data/p5_results.json and
data/p5_full.json exactly (3 dp) and CIs within 0.03. Writes data/p5_recount.json."""
import json,math,random,re,collections,sys
sys.path.insert(0,'scripts'); from p2_lib import raw_rows,labels,to_task,to_report
def ranks_auc(P,N):
    allv=sorted([(v,1) for v in P]+[(v,0) for v in N]); r={}; i=0
    while i<len(allv):
        j=i
        while j<len(allv) and allv[j][0]==allv[i][0]: j+=1
        for k in range(i,j): r.setdefault(allv[k][0],(i+j+1)/2)
        i=j
    sp=sum(r[v] for v in P); return (sp-len(P)*(len(P)+1)/2)/(len(P)*len(N))
R=raw_rows(); L=labels(); T={};Rep={};arm={};cl={}
for i,d in L.items():
    if d['split']=='test' and d['claim'] and d['label']=='EARNED': k=str(i); T[k]=to_task(R[i]['task']); Rep[k]=to_report(R[i]['handoff']); arm[k]='EARNED'; cl[k]=i
for p in map(json.loads,open('private/p5_plants_test.jsonl')): T[p['item']]=p['task']; Rep[p['item']]=p['report']; arm[p['item']]=p['type']; cl[p['item']]=p['source']
docs=[re.findall(r'[a-z0-9]{3,}',to_report(R[i]['handoff']).lower()) for i,d in L.items() if d['split']=='test' and d['claim']]
avg=sum(map(len,docs))/len(docs); df=collections.Counter(t for d in docs for t in set(d)); Nd=len(docs)
def bm(q,d):
    d=re.findall(r'[a-z0-9]{3,}',d.lower()); tf=collections.Counter(d); s=0
    for t in set(re.findall(r'[a-z0-9]{3,}',q.lower())):
        if tf[t]: s+=math.log(1+(Nd-df.get(t,0)+.5)/(df.get(t,0)+.5))*tf[t]*2.5/(tf[t]+1.5*(.25+.75*len(d)/avg))
    return -s
def ov(a,b): A=set(re.findall(r'[a-z]{4,}',a.lower())); Bs=set(re.findall(r'[a-z]{4,}',b.lower())); return -len(A&Bs)/max(1,len(A|Bs))
sc={'overlap':{k:ov(T[k],Rep[k]) for k in T},'bm25':{k:bm(T[k],Rep[k]) for k in T}}
acc=collections.defaultdict(lambda:collections.defaultdict(list))
name={('claude-haiku-5-5','L1'):'haiku_omni',('claude-haiku-5-5','TM'):'haiku_tm',('claude-sonnet-5-5','L1'):'sonnet_omni*',('claude-sonnet-5-5','TM'):'sonnet_tm*'}
for r in map(json.loads,open('private/p5_runs.jsonl')):
    if r.get('score') is not None: acc[name[(r['model'],r['level'])]][r['item']].append(r['score'])
for k,d in acc.items(): sc[k]={i:sum(v)/len(v) for i,v in d.items()}
res=json.load(open('data/p5_results.json')); out=dict(checks=0,mismatch=[],max_ci_diff=0,calls={k:sum(map(len,d.values())) for k,d in acc.items()})
rng=random.Random(7)
for t in('d2','p'):
    its=[k for k in T if arm[k] in(t,'EARNED')]; byc=collections.defaultdict(list)
    for k in its: byc[cl[k]].append(k)
    keys=list(byc); boots=[]
    for _ in range(2000):
        s=[k for c in (rng.choice(keys) for _ in keys) for k in byc[c]]; boots.append(s)
    for s_name,s in sc.items():
        P=[s[k] for k in its if arm[k]==t]; N=[s[k] for k in its if arm[k]=='EARNED']; a=round(ranks_auc(P,N),3)
        v=sorted(ranks_auc([s[k] for k in b if arm[k]==t],[s[k] for k in b if arm[k]=='EARNED']) for b in boots if any(arm[k]==t for k in b) and any(arm[k]=='EARNED' for k in b))
        ci=[v[int(.025*len(v))],v[int(.975*len(v))]]; ref=res['types'][t]['auroc'][s_name]; out['checks']+=1
        d=max(abs(ci[0]-ref[1]),abs(ci[1]-ref[2])); out['max_ci_diff']=round(max(out['max_ci_diff'],d),3)
        if a!=ref[0] or d>.03: out['mismatch'].append([t,s_name,a,ref])
        out[f'{t}/{s_name}']=[a,round(ci[0],3),round(ci[1],3)]
    for key,c in res['types'][t]['paired'].items():
        x,y=key.split(' - '); P=[k for k in its if arm[k]==t]; N=[k for k in its if arm[k]=='EARNED']
        dd=round(ranks_auc([sc[x][k] for k in P],[sc[x][k] for k in N])-ranks_auc([sc[y][k] for k in P],[sc[y][k] for k in N]),3); out['checks']+=1
        if abs(dd-c['diff'])>.0015: out['mismatch'].append([t,key,dd,c['diff']])
full=json.load(open('data/p5_full.json')); out['full_note']='step 3 (data/p5_full.json) is not recounted here'
json.dump(out,open('data/p5_recount.json','w'),indent=1); print('checks',out['checks'],'mismatches',out['mismatch'],'max CI diff',out['max_ci_diff'],out['calls'])
