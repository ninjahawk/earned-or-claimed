#!/usr/bin/env python3
"""L2 facts for every kept job (private/facts.jsonl), the first table (data/first_table.json), and the 50-row facts scrub test."""
import sys,json,random,re,collections
sys.path.insert(0,'scripts'); from p2_lib import *
ix=Index(); R=raw_rows(); L=labels(); out={}
for i,d in L.items():
    r=R[i]; f=facts(ix,r['handoff'],r['created'],r['finished']); f['id']=i; out[i]=f
with open('private/facts.jsonl','w') as w:
    for f in out.values(): w.write(json.dumps(f)+'\n')
# first table
U=[i for i,d in L.items() if d['label']=='UNEARNED' and d['claim']]
tab=collections.Counter(); per={'dev':collections.Counter(),'test':collections.Counter()}
for i in U:
    f=out[i]; c='no_checkable_artifact_cited' if not(f['commits'] or f['files']) else ('existence_detectable_cited_item_missing' if existence_miss(f) else 'all_cited_artifacts_present')
    tab[c]+=1; per[L[i]['split']][c]+=1
hist=sum(out[i]['files_hist_only']>0 for i in U)
ft=dict(n=len(U),table=dict(tab),by_split={k:dict(v) for k,v in per.items()},with_a_cited_file_only_in_git_history=hist,
 note='Existence checked 2026-11-06, not at job time. A miss can be an extraction or index miss rather than a false claim; the miss rate on dev EARNED below is the noise estimate.',
 dev_earned_noise=dict(n=sum(1 for i,d in L.items() if d['split']=='dev' and d['label']=='EARNED' and d['claim']),
   any_miss=sum(1 for i,d in L.items() if d['split']=='dev' and d['label']=='EARNED' and d['claim'] and existence_miss(out[i])),
   no_artifact=sum(1 for i,d in L.items() if d['split']=='dev' and d['label']=='EARNED' and d['claim'] and not(out[i]['commits'] or out[i]['files']))))
json.dump(ft,open('data/first_table.json','w'),indent=1); print(json.dumps(ft,indent=0))
# facts scrub test: 50 rows
rng=random.Random(20261107); s=rng.sample(list(out.values()),50)
bad=0
with open('private/facts-scrub-test.txt','w') as w:
    for f in s:
        t=facts_text(f); w.write(f"--- {f['id']}\n{t}\n")
        if re.search(r'[/\\]|\b[0-9a-f]{7,40}\b|\.\w{2,4}\b(?!\s)',t.replace('.',' . ')) : bad+=1
print('facts scrub hits',bad)
