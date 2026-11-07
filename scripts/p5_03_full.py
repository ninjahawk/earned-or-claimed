#!/usr/bin/env python3
"""P5 step 3 (exploratory): P3 headline cell (plant d vs EARNED) at FULL report length, no report slice; task slice [:1500]
unchanged; frozen omnibus L1 v3 and tm1 system prompts. Items: P3 step 4 covered set (private/p3_full_items.json).
Haiku, 3 repeats each. Writes private/p5_full.jsonl."""
import sys; sys.path.insert(0,'scripts'); import p3_lib; from p3_lib import *; import p3_prompts as Q
p3_lib.GUARD=57.0
dl=int(sys.argv[1]) if len(sys.argv)>1 else 560
FR={json.loads(l)['id']:json.loads(l) for l in open('private/full_reports.jsonl')}; keep=set(json.load(open('private/p3_full_items.json')))
I={x['item']:dict(x,full=to_report(FR[x['source']]['full'])) for x in test_items() if x['item'] in keep}; assert len(I)==48
print('full chars median/max',sorted(len(v['full']) for v in I.values())[24],max(len(v['full']) for v in I.values()))
jobs=[dict(item=k,arm=x['arm'],level=lv,rep=r,model=HAIKU_,source=x['source'],ver=v) for k,x in sorted(I.items()) for lv,v in(('L1nocap','v3'),('TMnocap','tm1')) for r in range(3)]
SYS={'L1nocap':PP.V['v3']['L1'],'TMnocap':Q.TM['tm1']}
fn=lambda j:call(SYS[j['level']],f"TASK GIVEN TO WORKER:\n{I[j['item']]['task'][:1500]}\n\nWORKER'S FINAL REPORT:\n{I[j['item']]['full']}\n",model=j['model'])
run(jobs,'private/p5_full.jsonl',fn,deadline=dl)
