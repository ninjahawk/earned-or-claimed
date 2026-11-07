#!/usr/bin/env python3
"""P5 step 3 numbers: same 48 items (13 plant d, 35 EARNED), Haiku, 2000-char vs full report. Clustered bootstrap by
source job, seed 20261107, B 2000 (p5_stats). Writes data/p5_full.json."""
import sys,json,collections,statistics as St
sys.path.insert(0,'scripts'); import p5_stats as S
HK='claude-haiku-5-5'; keep=set(json.load(open('private/p3_full_items.json')))
raw=collections.defaultdict(lambda:collections.defaultdict(dict)); ARM={}; SRC={}
def add(f,lv,name,model=HK):
    for r in map(json.loads,open('private/'+f)):
        if r.get('score') is None or r['item'] not in keep or r['level']!=lv or r.get('model',HK)!=model: continue
        raw[name][r['item']][r['rep']]=r['score']; ARM[r['item']]=r['arm']; SRC[r['item']]=r['source']
add('test_runs.jsonl','L1','omni_2000 (phase 2, 3 reps)'); add('p3_full.jsonl','L1full','omni_full (P3 [:12000], 3 reps)')
add('p5_full.jsonl','L1nocap','omni_full (P5 no cap, 3 reps)'); add('p3_tm_test.jsonl','TM','tm_2000 (P3+P4, 5 reps)'); add('p4_tm_repeats.jsonl','TM','tm_2000 (P3+P4, 5 reps)')
add('p5_full.jsonl','TMnocap','tm_full (P5 no cap, 3 reps)')
SC={k:{i:St.mean(v.values()) for i,v in d.items()} for k,d in raw.items()}
items={i:('pos' if ARM[i]=='plant_d' else 'neg',SRC[i]) for i in keep}; assert collections.Counter(c for c,_ in items.values())=={'pos':13,'neg':35}
for k in SC: assert set(SC[k])==keep,(k,len(SC[k]))
dr=S.draws(items); P=[i for i in items if items[i][0]=='pos']; N=[i for i in items if items[i][0]=='neg']
out=dict(n_d=13,n_EARNED=35,reps={k:sorted({r for v in d.values() for r in v}) for k,d in raw.items()},auroc={},per_repeat={},earned_mean={},paired={})
for k,d in raw.items():
    out['auroc'][k]=S.cell(SC[k],items,dr); out['earned_mean'][k]=round(St.mean(SC[k][i] for i in N),2)
    out['per_repeat'][k]=[round(S.auc([d[i][r] for i in P],[d[i][r] for i in N]),3) for r in out['reps'][k]]
K=list(raw); g=lambda s:[k for k in K if k.startswith(s)]
pairs=[(g('omni_full (P5')[0],g('omni_2000')[0]),(g('tm_full')[0],g('tm_2000')[0]),(g('tm_full')[0],g('omni_full (P5')[0]),(g('tm_2000')[0],g('omni_2000')[0]),(g('omni_full (P5')[0],g('omni_full (P3')[0])]
for x,y in pairs: out['paired'][f'{x} - {y}']=S.paired(SC[x],SC[y],items,dr)
json.dump(out,open('data/p5_full.json','w'),indent=1); print(json.dumps(out,indent=1))
