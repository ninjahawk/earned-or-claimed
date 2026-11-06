#!/usr/bin/env python3
"""Work list for the sweep. Scope: status=done jobs in private/labels.jsonl (A claim+UNKNOWN, B done+no claim, C claim+EARNED).
private/sweep_worklist.jsonl = masked id + text only. private/sweep_mask_map.json = mask -> id, group (not read until the merge)."""
import json,hashlib
L=[json.loads(l) for l in open('private/labels.jsonl')]
X={json.loads(l)['id']:json.loads(l) for l in open('private/export.jsonl')}
def grp(d):
    if d['status']!='done': return None
    if not d['claim']: return 'B'
    return {'UNKNOWN':'A','EARNED':'C'}.get(d['label'])
M={};rows=[]
for d in L:
    g=grp(d)
    if not g: continue
    m=hashlib.sha256(f"sweep20261106:{d['id']}".encode()).hexdigest()[:10]
    M[m]=dict(id=d['id'],group=g)
    rows.append(dict(mask=m,task=X[d['id']]['task'],handoff=X[d['id']]['handoff']))
rows.sort(key=lambda r:r['mask'])
json.dump(M,open('private/sweep_mask_map.json','w'))
with open('private/sweep_worklist.jsonl','w') as f:
    for r in rows: f.write(json.dumps(r)+'\n')
print('work list rows:',len(rows))
