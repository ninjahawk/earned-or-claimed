#!/usr/bin/env python3
"""P5 step 2: frozen omnibus L1 v3 and frozen task-match tm1, unchanged, on test EARNED + planted d2 + p.
Usage: p5_02_run.py haiku|sonnet [deadline_s]. Haiku reps 0-4, Sonnet* reps 0-1. Writes private/p5_runs.jsonl (resumable)."""
import sys; sys.path.insert(0,'scripts'); import p3_lib; from p3_lib import *; import p3_prompts as Q; import p5_stats as S5
p3_lib.GUARD=57.0  # job line 58 minus 1 point of headroom
assert json.load(open('data/FROZEN.json'))['version']=='v3' and json.load(open('data/FROZEN_P3.json'))['task_match']=='tm1'
who=sys.argv[1]; dl=int(sys.argv[2]) if len(sys.argv)>2 else 3000
m,reps={'haiku':(HAIKU_,range(5)),'sonnet':(SONNET,range(2))}[who]
I,_=S5.split_items('test'); print({a:sum(x['arm']==a for x in I.values()) for a in('EARNED','d2','p')})
jobs=[dict(item=k,arm=x['arm'],level=lv,rep=r,model=m,source=x['cluster'],ver=v) for k,x in sorted(I.items()) for lv,v in(('L1','v3'),('TM','tm1')) for r in reps]
def fn(j):
    x=I[j['item']]
    if j['level']=='L1': return call(PP.V['v3']['L1'],PP.prompt('L1',x['task'],x['report'],''),model=j['model'])
    return call(Q.TM['tm1'],Q.tm_prompt(x['task'],x['report']),model=j['model'])
run(jobs,'private/p5_runs.jsonl',fn,deadline=dl)
