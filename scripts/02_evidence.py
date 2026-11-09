#!/usr/bin/env python3
"""Collect per-job evidence lines from verifier sources into private/evidence.json (raw lines stay private)."""
import json,re,glob,importlib.util,collections
import os,sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from private_terms import *
spec=importlib.util.spec_from_file_location('x','scripts/01_export.py')
src=open('scripts/01_export.py').read().rsplit('main()',1)[0]
ns={}; exec(src,ns); scrub=ns['scrub']
R='ORCH_ROOT/repo/'
EX=sorted(EXCLUDED_WORKFLOWS)
jobs={json.loads(l)['id']:json.loads(l) for l in open('private/export.jsonl')}
ev=collections.defaultdict(lambda:{'results':[],'neg':[]})
for l in open(R+'notes/results.md'):
    if l.startswith('#'):continue
    for i in set(re.findall(r'#(\d{2,4})\b',l)):
        if int(i) in jobs: ev[int(i)]['results'].append(scrub(l.strip())[:300])
NEG=re.compile(r'without (its |a |the )?(result|final|output)|no result|came back empty|empty (output|run|result)|false(ly)? |claimed?|fabricat|not (actually|merged|committed|landed|delivered|published|done)|missing|wrong|bogus|overstat|stale|defect|failed verif|did(n.t| not) (do|run|commit|land|deliver|finish|verify)|never (ran|landed|committed|finished|delivered)|but (no|not|never|the )|nothing (landed|committed)|unverified|rejected|redo|broken|mismatch',re.I)
files=glob.glob(R+'reports/incidents/*.md')+[R+'notes/incidents.md']+[f for f in glob.glob(R+'notes/*.md')+glob.glob(R+'notes/archive/*/*.md') if not any(x in f for x in EX) and not f.endswith('results.md')]
for f in files:
    src_=f.replace(R,'')
    for ln in open(f,errors='ignore'):
        for m in re.finditer(r'#(\d{2,4})\b',ln):
            i=int(m.group(1))
            if i in jobs:
                w=ln[max(0,m.start()-170):m.end()+170]
                if NEG.search(w): ev[i]['neg'].append((src_,scrub(w.strip())))
json.dump(ev,open('private/evidence.json','w'),indent=0)
print('jobs with results',sum(1 for v in ev.values() if v['results']),'neg lines',sum(1 for v in ev.values() if v['neg']),'both',sum(1 for v in ev.values() if v['neg'] and v['results']))
print('done w/ neg',sum(1 for i,v in ev.items() if v['neg'] and jobs[i]['status']=='done'))
