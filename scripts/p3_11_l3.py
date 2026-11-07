#!/usr/bin/env python3
"""QUESTION.md's L3, Haiku. Natural only, labelled test or dev items with a verified transcript. Usage: p3_11_l3.py dev|test <repeats> [deadline]. Test refuses unless data/FROZEN_P3.json names l3."""
import sys; sys.path.insert(0,'scripts'); from p3_lib import *; import p3_prompts as Q
split,rep=sys.argv[1],int(sys.argv[2]); dl=int(sys.argv[3]) if len(sys.argv)>3 else 540
if split=='test': assert json.load(open('data/FROZEN_P3.json')).get('l3')=='v1','not frozen'
E=json.load(open('private/p3_excerpts.json'))
it=[x for x in test_items(split) if x['arm'] in('EARNED','UNEARNED') and x['item'] in E]; I={x['item']:x for x in it}
print({a:sum(x['arm']==a for x in it) for a in('EARNED','UNEARNED')})
jobs=[dict(item=x['item'],arm=x['arm'],level='L3',rep=r,model=HAIKU_,source=x['source'],ver='l3v1') for x in it for r in range(rep)]
fn=lambda j:call(Q.L3,Q.l3_prompt(I[j['item']]['task'],I[j['item']]['report'],E[j['item']]),model=j['model'])
run(jobs,f'private/p3_l3_{split}.jsonl',fn,deadline=dl)
