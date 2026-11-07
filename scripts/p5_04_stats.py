#!/usr/bin/env python3
"""P5 step 2 numbers: AUROC per scorer and plant type vs test EARNED, per-repeat spread, paired cells (95% and 6-cell
Bonferroni CI), as PREREG-P5.md. Writes data/p5_results.json and data/p5_reading.txt (p5_read.py output)."""
import sys,json,collections,statistics as St
sys.path.insert(0,'scripts'); import p5_stats as S; import p5_read
HK,SN='claude-haiku-5-5','claude-sonnet-5-5'
it,bm=S.split_items('test'); bl=S.baselines(it,bm)
raw=collections.defaultdict(lambda:collections.defaultdict(dict))
for r in map(json.loads,open('private/p5_runs.jsonl')):
    if r.get('score') is None: continue
    k={(HK,'L1'):'haiku_omni',(HK,'TM'):'haiku_tm',(SN,'L1'):'sonnet_omni*',(SN,'TM'):'sonnet_tm*'}[(r['model'],r['level'])]
    raw[k][r['item']][r['rep']]=r['score']
SC={k:{i:St.mean(v.values()) for i,v in d.items()} for k,d in raw.items()}; SC.update(bl)
reps={k:sorted({r for v in d.values() for r in v}) for k,d in raw.items()}
calls={k:sum(len(v) for v in d.values()) for k,d in raw.items()}
CELLS=p5_read.PRIMARY+p5_read.SECONDARY
out=dict(n={t:sum(x['arm']==t for x in it.values()) for t in('EARNED','d2','p')},reps=reps,calls=calls,types={})
pw=json.load(open('data/p5_dev_baselines.json'))['power']
for t in('d2','p'):
    items=S.cells_for(it,t); dr=S.draws(items); P=[i for i,(c,_) in items.items() if c=='pos']; N=[i for i,(c,_) in items.items() if c=='neg']
    assert all(i in SC[k] for k in SC for i in items), 'missing scores'
    T=dict(auroc={k:S.cell(SC[k],items,dr) for k in SC},spread={},paired={},mde80=pw[t]['mde80'],n_pos=len(P),n_neg=len(N),pos_clusters=len({items[i][1] for i in P}))
    for k,d in raw.items():
        a=[S.auc([d[i][r] for i in P],[d[i][r] for i in N]) for r in reps[k]]
        T['spread'][k]=[round(min(a),3),round(max(a),3),round(St.pstdev(a),3) if len(a)>1 else 0.0]; T.setdefault('per_repeat',{})[k]=[round(x,3) for x in a]
    for x,y in CELLS:
        c=S.paired(SC[x],SC[y],items,dr); cb=S.paired(SC[x],SC[y],items,dr,alpha=.05/6)
        T['paired'][f'{x} - {y}']=dict(diff=c['diff'],ci=c['ci'],ci_bonf=cb['ci'],boot_sd=c['sd'])
    # EARNED scale per model (mean score), printed for scale shift
    T['earned_mean']={k:round(St.mean(SC[k][i] for i in N),2) for k in raw}; T['pos_mean']={k:round(St.mean(SC[k][i] for i in P),2) for k in raw}
    out['types'][t]=T
json.dump(out,open('data/p5_results.json','w'),indent=1)
txt=p5_read.read(out); open('data/p5_reading.txt','w').write(txt+'\n'); print(txt); print('calls',calls)
