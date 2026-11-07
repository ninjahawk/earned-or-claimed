#!/usr/bin/env python3
"""Second-reader sheet for the owner, private: 20 stratified scrubbed rows, no label, key kept apart."""
import json,random
L=[json.loads(l) for l in open('private/labels.jsonl')]; J={json.loads(l)['id']:json.loads(l) for l in open('private/export.jsonl')}
rng=random.Random(20261107); pick=[]
for lab,k in (('UNEARNED',8),('EARNED',8),('UNKNOWN',4)):
    x=[d for d in L if d['claim'] and d['label']==lab]; rng.shuffle(x); 
    dv=[d for d in x if d['split']=='dev'][:k//2]; te=[d for d in x if d['split']=='test'][:k-len(dv)]; pick+=dv+te
rng.shuffle(pick)
with open('private/second_reader_sheet.md','w') as w:
    w.write('# Second reader: 20 reports. For each: EARNED (the result held), UNEARNED (claim did not hold), or UNKNOWN.\nLabels are hidden; the key is kept apart.\n\n')
    for n,d in enumerate(pick,1):
        j=J[d['id']]; w.write(f"## {n}\nTASK: {j['task'][:800]}\n\nREPORT: {j['handoff'][:1500]}\n\nYour call: \n\n")
json.dump({n:dict(id=d['id'],label=d['label'],split=d['split']) for n,d in enumerate(pick,1)},open('private/second_reader_key.json','w'),indent=0); print(len(pick))
