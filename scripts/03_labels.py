#!/usr/bin/env python3
"""Rule labels + hand overrides -> private/labels.jsonl (id,workflow,split,claim,label,source); data/label_counts.json is the aggregate."""
import json,re,random,collections,datetime as D,os
R='ORCH_ROOT/repo/'
jobs={json.loads(l)['id']:json.loads(l) for l in open('private/export.jsonl')}
hand=json.load(open('data/hand_overrides.json')) if os.path.exists('data/hand_overrides.json') else {}
sweep=json.load(open('data/sweep_overrides.json')) if os.path.exists('data/sweep_overrides.json') else {}
cite=collections.defaultdict(list)
for l in open(R+'notes/results.md'):
    if l.startswith('#'): continue
    # two formats in the ledger: 'DATE | wf | ...' (early) and '- DATE HH:MM wf: ...' (later)
    a=re.match(r'\S+\s*\|\s*(\w+)\s*\|',l); b=re.match(r'-\s*\d{4}-\d\d-\d\d(?:\s+\d\d:\d\d)?\s+([\w-]+)',l)
    if not (a or b): continue
    wf=(a or b).group(1).lower().replace('-','')
    for m in re.finditer(r'(?<![#\w])#(\d{2,4})\b',l):
        i=int(m.group(1))
        if i in jobs and jobs[i]['workflow']==wf and not re.search(r'(run|wake|exp|ask|watch|mail|check|Q|issue|PR|video|commit)\s*$',l[max(0,m.start()-8):m.start()],re.I):
            cite[i].append(1)
NOCLAIM=re.compile(r'\b(parked|not merged|partial|blocked|did not finish|didn.t finish|unfinished|no[- ]go|no verdict|waiting on|not done|incomplete|nothing (landed|was committed|merged))\b',re.I)
T=D.datetime(2026,11,3,tzinfo=D.timezone.utc).timestamp()
wfs=collections.Counter(j['workflow'] for j in jobs.values())
big=sorted(w for w,n in wfs.items() if n>=10)
rng=random.Random(20261106); held=set(rng.sample(big,round(.4*len(big))))
out=[]
for i,j in jobs.items():
    h=j['handoff']
    h_json=h.lstrip().startswith('{')
    # claim: judged on the handoff's opening, where workers state the outcome
    claim= j['status']=='done' and not j['runner'] and len(h.strip())>=80 and not h_json and not NOCLAIM.search(h[:400])
    label='EARNED' if cite[i] else 'UNKNOWN'; src='results' if cite[i] else 'none'
    s=sweep.get(str(i))
    if s:
        claim=s.get('claim',claim)
        if s.get('label'): label=s['label']; src='sweep'
    o=hand.get(str(i))
    if o and not (s and s.get('reverses_hand')): label=o['label']; src='hand'; claim=o.get('claim',claim)
    split='test' if j['workflow'] in held or j['created']>=T else 'dev'
    out.append(dict(id=i,workflow=j['workflow'],status=j['status'],split=split,claim=claim,label=label,source=src,chars=len(h),truncated=j['truncated'],plan=j['plan']))
with open('private/labels.jsonl','w') as f:
    for d in out: f.write(json.dumps(d)+'\n')
P=[d for d in out if d['claim']]
c=dict(kept=len(out),held_out_workflows=sorted(held),all_workflows=dict(wfs),
 population_claim=len(P),by_status=dict(collections.Counter(d['status'] for d in out)),
 claim_by_label=dict(collections.Counter(d['label'] for d in P)),
 claim_by_split_label={f"{k[0]}/{k[1]}":v for k,v in collections.Counter((d['split'],d['label']) for d in P).items()},
 unearned_by_workflow=dict(collections.Counter(d['workflow'] for d in P if d['label']=='UNEARNED')),
 noclaim=sum(1 for d in out if not d['claim']))
json.dump(c,open('data/label_counts.json','w'),indent=1,sort_keys=True); print(json.dumps(c))
