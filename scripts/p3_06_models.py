#!/usr/bin/env python3
"""L1, L2 v3 on one model, same inputs. Usage: p3_06_models.py <model> <repeats> [first_rep] [deadline]. Writes private/p3_runs.jsonl."""
import sys; sys.path.insert(0,'scripts'); from p3_lib import *
m,rep=sys.argv[1],int(sys.argv[2]); first=int(sys.argv[3]) if len(sys.argv)>3 else 0; dl=int(sys.argv[4]) if len(sys.argv)>4 else 540
assert json.load(open('data/FROZEN.json'))['version']=='v3'
it=test_items(); assert len(it)==127; I={x['item']:x for x in it}
jobs=[dict(item=x['item'],arm=x['arm'],level=lv,rep=r,model=m,source=x['source'],ver='v3') for x in it for lv in('L1','L2') for r in range(first,first+rep)]
fn=lambda j:call(PP.V['v3'][j['level']],PP.prompt(j['level'],I[j['item']]['task'],I[j['item']]['report'],I[j['item']]['ft']),model=j['model'])
run(jobs,'private/p3_runs.jsonl',fn,deadline=dl)
