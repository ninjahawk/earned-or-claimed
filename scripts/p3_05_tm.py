#!/usr/bin/env python3
"""Task-match check. Usage: p3_05_tm.py dev|test <version> <repeats> <models,comma> [deadline]. Dev: plant d + EARNED only. Test: refuses unless data/FROZEN_P3.json names the version; all 127 labelled items."""
import sys; sys.path.insert(0,'scripts'); from p3_lib import *; import p3_prompts as Q
split,ver,rep,models=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4].split(','); dl=int(sys.argv[5]) if len(sys.argv)>5 else 540
if split=='test': assert json.load(open('data/FROZEN_P3.json'))['task_match']==ver,'not frozen'
it=test_items(split)
if split=='dev': it=[x for x in it if x['arm'] in('EARNED','plant_d')]
I={x['item']:x for x in it}
jobs=[dict(item=x['item'],arm=x['arm'],level='TM',rep=r,model=m,source=x['source'],ver=ver) for m in models for x in it for r in range(rep)]
fn=lambda j:call(Q.TM[ver],Q.tm_prompt(I[j['item']]['task'],I[j['item']]['report']),model=j['model'])
run(jobs,f'private/p3_tm_{split}.jsonl',fn,deadline=dl)
