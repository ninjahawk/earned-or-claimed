#!/usr/bin/env python3
"""L3 excerpts (no model) + scrub test: 50 rows to private/p3_l3_scrub_test.txt, residual scans to stdout, counts in data/p3_l3_scrub.json."""
import sys,random,collections; sys.path.insert(0,'scripts'); from p3_lib import *
L=labels(); FR={json.loads(l)['id']:json.loads(l) for l in open('private/full_reports.jsonl')}
def local(p): return re.sub(r'^PC_HOME/','PC_MOUNT/',p.replace('\\','/'))
E={}
for i,x in FR.items():
    if x['kind']=='transcript' and L[i]['label'] in('EARNED','UNEARNED'): E[str(i)]=transcript_excerpt(local(x['path']))
json.dump(E,open('private/p3_excerpts.json','w'))
rng=random.Random(20261109); s=rng.sample(sorted(E),50)
with open('private/p3_l3_scrub_test.txt','w') as f:
    for k in s: f.write(f"--- {k} {L[int(k)]['label']}\n{E[k][:1500]}\n...\n{E[k][-500:]}\n")
txt=' '.join(E.values()); low=set(re.findall(r'\b[a-z]{3,}\b',txt)); caps=collections.Counter(w for w in re.findall(r'(?<![\w/.-])[A-Z][a-z]{2,}\b',txt) if w.lower() not in low)
res=dict(n=len(E),empty=sum(not v for v in E.values()),median_chars=sorted(map(len,E.values()))[len(E)//2],verif_left=sum(bool(VERIF.search(v)) for v in E.values()),drop_left=sum(bool(DROP.search(v)) for v in E.values()),USER=sum('USER' in v.lower() for v in E.values()),nathan=sum('nathan' in v.lower() or 'langley' in v.lower() for v in E.values()))
json.dump(res,open('data/p3_l3_scrub.json','w'),indent=1); print(res); print(' '.join(f'{w}:{k}' for w,k in caps.most_common(120)))
