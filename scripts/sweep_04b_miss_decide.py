#!/usr/bin/env python3
"""Step 4b: agent hits -> checked against the source copy -> private/sweep_miss_candidates.jsonl, for sweep_03_decide.py with the same readers."""
import json,re,sqlite3,datetime as D
T='/tmp/sweep_src/'
c={json.loads(l)['mask']:json.loads(l) for l in open('private/sweep_candidates.jsonl')}
norm=lambda s:re.sub(r'\W+',' ',s).lower().strip()
out=[];st=dict(rows=0,hits=0,not_in_source=0,before_claim=0,already_candidate=0,kept=0)
for l in open('private/sweep_miss_search.jsonl'):
    d=json.loads(l); st['rows']+=1; C=c[d['mask']]; L=[]; cd=C['claim_at'][:10]; ex=norm(' '.join(x['text'] for x in C['lines']))
    for h in d['hits']:
        st['hits']+=1
        t=str(h.get('text',''))
        try: src=open(T+h['path'],errors='replace').read()
        except Exception: src=''
        if norm(t.rstrip('.… '))[:60] not in norm(src): st['not_in_source']+=1; continue
        if str(h.get('date',''))<cd: st['before_claim']+=1; continue
        if norm(t)[:60] and norm(t)[:60] in ex: st['already_candidate']+=1; continue
        st['kept']+=1; L.append(dict(path=h['path'],line=h.get('line'),end=h.get('line'),date=h.get('date'),date_kind='reported by search agent',tier=0,src='miss_search',text=t[:700]))
    out.append(dict(mask=d['mask'],mode=d['mode'],claim_at=C['claim_at'],lines=L))
with open('private/sweep_miss_candidates.jsonl','w') as f:
    for d in out: f.write(json.dumps(d)+'\n')
print(st,'jobs with kept hits',sum(1 for d in out if d['lines']))
