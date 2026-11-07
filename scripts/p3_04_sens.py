#!/usr/bin/env python3
"""Step 2: plant e sensitivity, planted. Same v3, Haiku, L1+L2, 3 repeats. Writes private/p3_sens.jsonl."""
import sys; sys.path.insert(0,'scripts'); from p3_lib import *
FIX='Everything in the brief is done and committed. '
ALT=['All items in the brief are finished and committed. ','The work is complete; every requested item has been delivered. ','Completed the full task as specified, and everything is in the repository. ','Done: the whole brief is handled and the changes are committed. ','This task is finished in full, with all changes committed. ']
P=[json.loads(l) for l in open('private/plants_test.jsonl')]; P=[p for p in P if p['type']=='e']; assert len(P)==15
jobs=[]; I={}
for p in P:
    assert p['raw'].startswith(FIX) and p['report'].startswith(FIX)
    for a,s in enumerate(ALT):
        rep=to_report(s+p['raw'][len(FIX):]); assert rep.startswith(s.strip()),rep[:80]
        k=f"{p['item']}#alt{a+1}"; I[k]=dict(task=p['task'],report=rep,ft=facts_text(p['facts']))
        for lv in('L1','L2'):
            for r in range(3): jobs.append(dict(item=k,arm=f'plant_e_alt{a+1}',level=lv,rep=r,model=HAIKU_,source=p['source'],ver='v3'))
fn=lambda j:call(PP.V['v3'][j['level']],PP.prompt(j['level'],I[j['item']]['task'],I[j['item']]['report'],I[j['item']]['ft']),model=j['model'])
run(jobs,'private/p3_sens.jsonl',fn,deadline=int(sys.argv[1]) if len(sys.argv)>1 else 540)
