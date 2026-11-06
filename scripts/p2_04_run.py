#!/usr/bin/env python3
"""Run monitors. Usage: p2_04_run.py <split> <version> <repeats> <outfile> [natural,plants] ; refuses test unless data/FROZEN.json names this version."""
import sys,json,os,concurrent.futures as X
sys.path.insert(0,'scripts'); from p2_lib import *; import p2_prompts as PP
split,ver,rep,outf=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]; parts=(sys.argv[5] if len(sys.argv)>5 else 'natural,plants').split(',')
if split=='test':
    assert json.load(open('data/FROZEN.json'))['version']==ver,'not frozen'
L=labels(); J={json.loads(l)['id']:json.loads(l) for l in open('private/export.jsonl')}
F={json.loads(l)['id']:json.loads(l) for l in open('private/facts.jsonl')}
items=[]
if 'natural' in parts:
    for i,d in L.items():
        if d['split']==split and d['claim'] and d['label'] in('EARNED','UNEARNED'):
            items.append(dict(item=str(i),arm=d['label'],task=J[i]['task'],report=J[i]['handoff'],ft=facts_text(F[i]),source=i))
if 'plants' in parts:
    for l in open(f'private/plants_{split}.jsonl'):
        p=json.loads(l); items.append(dict(item=p['item'],arm='plant_'+p['type'],task=p['task'],report=p['report'],ft=facts_text(p['facts']),source=p['source']))
done=set()
if os.path.exists(outf):
    for l in open(outf):
        r=json.loads(l)
        if r.get('score') is not None: done.add((r['item'],r['level'],r['rep']))
jobs=[(it,lv,k) for it in items for lv in('L1','L2') for k in range(rep) if (it['item'],lv,k) not in done]
print(len(items),'items',len(jobs),'calls')
def go(a):
    it,lv,k=a; r=call(PP.V[ver][lv],PP.prompt(lv,it['task'],it['report'],it['ft']))
    r.update(item=it['item'],arm=it['arm'],level=lv,rep=k,ver=ver,source=it['source']); return r
with X.ThreadPoolExecutor(8) as ex, open(outf,'a') as w:
    for r in ex.map(go,jobs):
        w.write(json.dumps(r)+'\n'); w.flush()
