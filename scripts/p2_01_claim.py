#!/usr/bin/env python3
"""Claim classifier v2, fixed on dev. Writes data/classifier_diff.json: before/after (id, split, label, claim). Does not change labels.jsonl."""
import json,re
OLD=re.compile(r'\b(parked|not merged|partial|blocked|did not finish|didn.t finish|unfinished|no[- ]go|no verdict|waiting on|not done|incomplete|nothing (landed|was committed|merged))\b',re.I)
# v2: only phrases that state the main result did not land; 'partial', 'no-go', 'waiting on', bare 'not merged' misfired on dev (37,104,125,243,374)
NEW=re.compile(r'\b(parked,? not merged|is parked|did not finish|didn.t finish|nothing (landed|was committed|was merged|merged)|no verdict)\b|\(partial\)|\bNot done\b',re.I)
J={json.loads(l)['id']:json.loads(l) for l in open('private/export.jsonl')}
L=[json.loads(l) for l in open('private/labels.jsonl')]
S=json.load(open('data/sweep_overrides.json')); H=json.load(open('data/hand_overrides.json'))
def cl(i,rx):
    j=J[i]; h=j['handoff']
    c=j['status']=='done' and not j['runner'] and len(h.strip())>=80 and not h.lstrip().startswith('{') and not rx.search(h[:400])
    s=S.get(str(i)); o=H.get(str(i))
    if s: c=s.get('claim',c)
    if o and not (s and s.get('reverses_hand')): c=o.get('claim',c)
    return c
diff=[];disagree={'dev':[], 'test':[]}
for d in L:
    i=d['id']; a,b=cl(i,OLD),cl(i,NEW)
    assert a==d['claim'],i
    if a!=b: diff.append(dict(id=i,split=d['split'],label=d['label'],claim_before=a,claim_after=b))
# dev quality: raw regex (no overrides) vs the AI re-read/hand claims, status done, non-runner, fired-by-old
raw={}
for name,rx in (('old',OLD),('new',NEW)):
    ok=n=0
    for d in L:
        i=d['id'];j=J[i]
        if d['split']!='dev' or d['status']!='done' or j['runner'] or not OLD.search(j['handoff'][:400]): continue
        n+=1; ok+= (not rx.search(j['handoff'][:400]))==d['claim']
    raw[name]=dict(agree_on_dev_old_fires=ok,n=n)
out=dict(diff=diff,dev_diff=sum(x['split']=='dev' for x in diff),test_diff=sum(x['split']=='test' for x in diff),raw_regex_agreement_with_reread_on_dev=raw,note='New regex is tuned on these same dev rows, so its agreement is not an estimate. Reference claims are the AI re-read and hand overrides, no human.')
json.dump(out,open('data/classifier_diff.json','w'),indent=1); print(json.dumps(out))
