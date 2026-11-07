#!/usr/bin/env python3
"""Step 4 paired: L1 full vs L1 truncated. Slice [:12000] in place of [:2000]; nothing else changes. Items: covered, longer, no DROP hit: test EARNED, plant d. Natural UNEARNED gated out (6 < 10). Usage: p3_08_full.py [deadline]."""
import sys; sys.path.insert(0,'scripts'); from p3_lib import *
dl=int(sys.argv[1]) if len(sys.argv)>1 else 540
FR={json.loads(l)['id']:json.loads(l) for l in open('private/full_reports.jsonl')}; FL={int(k):v for k,v in json.load(open('private/p3_full_flags.json')).items()}
ok=lambda s:s in FL and FL[s]['longer'] and not FL[s]['drop']
it=[x for x in test_items() if x['arm'] in('EARNED','plant_d') and ok(x['source'])]; print(len([x for x in it if x['arm']=='EARNED']),len([x for x in it if x['arm']=='plant_d']))
I={x['item']:dict(x,full=to_report(FR[x['source']]['full'])) for x in it}
print('over 12000 after filter:',sum(len(v['full'])>12000 for v in I.values()),'median full chars',sorted(len(v['full']) for v in I.values())[len(I)//2])
json.dump(sorted(I),open('private/p3_full_items.json','w'))
jobs=[dict(item=k,arm=x['arm'],level='L1full',rep=r,model=m,source=x['source'],ver='v3') for m in(HAIKU_,SONNET) for k,x in I.items() for r in range(3)]
SYS=PP.V['v3']['L1']
fn=lambda j:call(SYS,f"TASK GIVEN TO WORKER:\n{I[j['item']]['task'][:1500]}\n\nWORKER'S FINAL REPORT:\n{I[j['item']]['full'][:12000]}\n",model=j['model'])
run(jobs,'private/p3_full.jsonl',fn,deadline=dl)
