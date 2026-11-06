#!/usr/bin/env python3
"""Step 5a: reader rows -> per-job decision, mechanical quote check. private/sweep_tally.json."""
import json,re,collections
M=json.load(open('private/sweep_mask_map.json'))
norm=lambda s:re.sub(r'\W+',' ',s or '').lower().strip()
def load(cp,dp):
    C={json.loads(l)['mask']:json.loads(l) for l in open(cp)}
    R=collections.defaultdict(dict)
    for l in open(dp):
        d=json.loads(l); R[d['mask']][d['model']]=d
    out={}
    for m,r in R.items():
        ds={k:v['decision'] for k,v in r.items()}
        res='UNKNOWN'; note=''
        if len(ds)==2 and set(ds.values())=={'UNEARNED'}:
            ok=True
            for v in r.values():
                t=C[m]['lines'][v['line']-1]['text'] if v['line'] and 0<v['line']<=len(C[m]['lines']) else ''
                i=M[m]['id']; t=re.sub(rf'(?:(?<![\w#])#{i}\b|\bdelegations?[-\s#]*{i}\b|\bjobs?\s+#?{i}\b|\bHANDOFF-delegation-{i}\b)','[THIS JOB]',t,flags=re.I)  # readers saw the mask
                if not norm(v['quote'].strip('…. ')) or norm(v['quote'].strip('…. '))[:80] not in norm(t): ok=False
            res='UNEARNED' if ok else 'UNKNOWN'; note='' if ok else 'quote_check_failed'
        elif len(ds)==2 and len(set(ds.values()))==2: note='disagree'
        out[m]=dict(id=M[m]['id'],group=M[m]['group'],result=res,note=note,readers=r)
    return out
A=load('private/sweep_candidates.jsonl','private/sweep_decisions.jsonl')
B=load('private/sweep_miss_candidates.jsonl','private/sweep_miss_decisions.jsonl')
json.dump(dict(main=A,miss=B),open('private/sweep_tally.json','w'))
for name,T in (('main',A),('miss',B)):
    print(name,'jobs',len(T),collections.Counter(v['result'] for v in T.values()),collections.Counter(v['note'] for v in T.values()))
