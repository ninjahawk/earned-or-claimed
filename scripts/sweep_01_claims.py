#!/usr/bin/env python3
import sys; sys.path.insert(0,"scripts")
"""Step 1: claim re-read for group B: one fresh Sonnet per job, scrubbed handoff only. private/sweep_claims.jsonl."""
import json,os,sweep_lib as S
M=json.load(open('private/sweep_mask_map.json'))
W={json.loads(l)['mask']:json.loads(l) for l in open('private/sweep_worklist.jsonl')}
P='private/sweep_claims.jsonl'
done={json.loads(l)['mask'] for l in open(P)} if os.path.exists(P) else set()
todo=[m for m in W if M[m]['group']=='B' and m not in done]
T="""Below is the final message a worker wrote when its job ended. Does it claim the job's work was completed? A claim of completion means it states the work (or a stated deliverable) got done. A message that only reports waiting, a crash, a blocker, a partial result reported as partial, or a negative outcome reported as such is not a claim of completion. Judge only from this text.
Reply as JSON: {"claim": true or false, "quote": "<the words you rely on, copied verbatim; empty if none>"}

FINAL MESSAGE:
"""
def fn(m):
    h=W[m]['handoff'].strip()
    if len(h)<20: return dict(mask=m,claim_reread=False,quote='',note='handoff empty after scrub, no call'),0.0
    r,c=S.ask(S.SONNET,T+h)
    return dict(mask=m,claim_reread=bool(r.get('claim')) if 'error' not in r else None,quote=r.get('quote',''),error=r.get('error')),c
cost,left=S.pool(todo,fn,P)
print('claim step finished; cost usd %.2f; unfinished %d; meter %s'%(cost,len(left),S.weekly()))
