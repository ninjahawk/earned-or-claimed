#!/usr/bin/env python3
"""Phase 3 step 4, leak filter re-validated on full text before any monitor sees it. No model calls. Data: private/full_reports.jsonl.
Prints what the frozen filter catches, what a wider wording net still finds after it, whether label-source text is quoted in the filtered report (8-word shingles), and privacy DROP hits (those items leave the full-text test).
Writes data/p3_leakcheck.json; the sample itself to private/p3_leakcheck_sample.txt."""
import sys,json,re,random,collections
sys.path.insert(0,'scripts'); from p2_lib import *
_src=open('scripts/01_export.py').read().split('def main')[0]; _n={}; exec(_src,_n); DROP=_n['DROP']
L=labels(); R=raw_rows(); FR={json.loads(l)['id']:json.loads(l) for l in open('private/full_reports.jsonl')}
WIDE=re.compile(r"unearned|sentinel|true.positive|false.positive|\baudit|\bverif(y|ied|ication)\b|\breject|\bflagged\b|post.?mortem|caught by|fails? review|\bre-?run\b.*\b(because|after)\b|\borchestrator (said|found|rejected)\b",re.I)
def shingles(t,n=8):
    w=re.findall(r'[a-z0-9]+',t.lower()); return {' '.join(w[k:k+n]) for k in range(len(w)-n+1)}
src=collections.defaultdict(list)
ev=json.load(open('private/evidence.json'))
for i,v in ev.items():
    src[int(i)]+=[x[1] if isinstance(x,list) else x for x in v.get('neg',[])]+v.get('results',[])
for f in('private/sweep_statements.jsonl','private/sweep_decisions.jsonl','private/sweep_miss_decisions.jsonl'):
    for l in open(f):
        try: d=json.loads(l)
        except Exception: continue
        i=d.get('id') or d.get('job')
        if i is not None: src[int(str(i).lstrip('#'))].append(json.dumps(d))
rng=random.Random(20261108); byl=collections.defaultdict(list)
for i,x in FR.items(): byl[L[i]['label']].append(i)
out={}; sample=open('private/p3_leakcheck_sample.txt','w'); allrows={}
for lb,ids in sorted(byl.items()):
    ids=sorted(ids); s=ids if lb=='UNEARNED' else rng.sample(ids,min(25,len(ids)))
    c=collections.Counter(); wide=collections.Counter()
    for i in ids:
        full=FR[i]['full']; sc=scrub(full); fil=unleak(sc); stored=to_report(R[i]['handoff'])
        c['n']+=1; c['longer']+=len(full)>len(R[i]['handoff'] or '')+20
        c['sent_removed']+=sum(1 for x in re.split(r'(?<=[.!?\n])\s+',sc) if VERIF.search(x))
        c['items_filter_caught']+=bool(VERIF.search(sc)); c['verif_left_after_filter']+=bool(VERIF.search(fil))
        hit=WIDE.findall(fil); c['items_wide_hit']+=bool(WIDE.search(fil))
        c['items_wide_hit_not_in_stored']+=bool(WIDE.search(fil)) and not WIDE.search(stored)
        dropped=bool(DROP.search(full)); c['privacy_drop_hit']+=dropped
        q=shingles(fil)&set().union(*[shingles(t) for t in src.get(i,[])]) if src.get(i) else set()
        c['items_quoting_label_source']+=bool(q); c['max_shingles_quoted']=max(c['max_shingles_quoted'],len(q))
        allrows[i]=dict(label=lb,split=L[i]['split'],drop=dropped,longer=len(full)>len(R[i]['handoff'] or '')+20,chars_filtered=len(fil),over_12000=len(fil)>12000,quoted=len(q),wide=bool(WIDE.search(fil)))
        if i in s:
            sample.write(f"=== {i} {lb} chars={len(fil)} quoted={len(q)}\nWIDE: {[m.group(0) for m in WIDE.finditer(fil)][:6]}\nQUOTED: {sorted(q)[:3]}\nCONTEXT: {[fil[max(0,m.start()-100):m.end()+100] for m in WIDE.finditer(fil)][:4]}\n")
    out[lb]=dict(c)
elig=collections.Counter()
for i,r in allrows.items():
    k=f"{r['split']}/{r['label']}"; elig[k+'/covered_longer']+=r['longer']; elig[k+'/usable_longer_no_drop']+=r['longer'] and not r['drop']
P=[json.loads(l) for l in open('private/plants_test.jsonl')]
d=[p for p in P if p['type']=='d']; elig['test/plant_d/usable_longer_no_drop']=sum(p['source'] in allrows and allrows[p['source']]['longer'] and not allrows[p['source']]['drop'] for p in d)
json.dump(dict(by_label=out,eligible=dict(elig),wide_regex=WIDE.pattern),open('data/p3_leakcheck.json','w'),indent=1); json.dump(allrows,open('private/p3_full_flags.json','w'))
print(json.dumps(out,indent=0)); print(dict(elig))
