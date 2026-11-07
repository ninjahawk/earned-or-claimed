#!/usr/bin/env python3
"""P4 repeats of frozen task-match tm1 on test plant d + EARNED. Haiku reps 3,4; Sonnet rep 3. See PREREG-P4-repeats.md."""
import sys; sys.path.insert(0,'scripts'); import p3_lib; from p3_lib import *; import p3_prompts as Q
p3_lib.GUARD=52.0  # job #656 line 53
ver=json.load(open('data/FROZEN_P3.json'))['task_match']; assert ver=='tm1'
it=[x for x in test_items('test') if x['arm'] in('EARNED','plant_d')]; I={x['item']:x for x in it}
jobs=[dict(item=x['item'],arm=x['arm'],level='TM',rep=r,model=m,source=x['source'],ver=ver) for m,reps in ((HAIKU_,(3,4)),(SONNET,(3,))) for x in it for r in reps]
fn=lambda j:call(Q.TM[ver],Q.tm_prompt(I[j['item']]['task'],I[j['item']]['report']),model=j['model'])
run(jobs,'private/p4_tm_repeats.jsonl',fn,deadline=1500)
