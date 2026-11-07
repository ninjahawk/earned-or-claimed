#!/usr/bin/env python3
"""P5 step 4: second-reader sheet for Nathan, PRIVATE. All 15 natural UNEARNED (dev+test) + 15 random EARNED (seed
20261107), shuffled, labels hidden, key apart. One line each: task, claim (first sentence of the report with a completion
word), evidence (first cited file or commit in text order; handoff files skipped when anything else is cited), Y/N = did the claimed result really hold.
Writes private/second_reader_sheet.md (old 20-row sheet kept as private/second_reader_sheet_p2.md) and private/second_reader_key_p5.json."""
import sys,json,random,re,os,shutil
sys.path.insert(0,'scripts'); from p2_lib import *; from p5_01_plants import COMPLETE,sents
R=raw_rows(); L=labels(); rng=random.Random(20261107)
U=sorted(i for i,d in L.items() if d['claim'] and d['label']=='UNEARNED'); E=sorted(i for i,d in L.items() if d['claim'] and d['label']=='EARNED')
assert len(U)==15,len(U); pick=U+rng.sample(E,15); rng.shuffle(pick)
if os.path.exists('private/second_reader_sheet.md') and not os.path.exists('private/second_reader_sheet_p2.md'): shutil.copy('private/second_reader_sheet.md','private/second_reader_sheet_p2.md')
c=lambda s,n:re.sub(r'\s+',' ',(s or '')).replace('|','/').strip()[:n]
rows=[]
for i in pick:
    h=R[i]['handoff'] or ''; cl=next((s for s in sents(visible(h)) if COMPLETE.search(s)),sents(h)[0] if h else '')
    hs,abss,rel=extract(h); nh=lambda v:[x for x in v if not re.search(r'(?i)handoff',x)]; fo=lambda v:sorted(v,key=lambda x:(h.find(x) if x in h else 10**9)); ev=(fo(nh(abss)+nh(rel)+hs) or fo(abss+rel) or ['(none cited)'])[0]
    rows.append((i,c(R[i]['task'],170),c(cl,230),c(ev,120)))
with open('private/second_reader_sheet.md','w') as w:
    w.write("# Second reader, 30 rows, about 10 minutes. PRIVATE: never published.\n"
            "For each row: did the claimed result really hold? Put Y (it held) or N (it did not) in the last column; ? if you can't tell.\n"
            "Labels are hidden; the key is kept apart. The claim is the first completion sentence of the report; evidence is the first thing it cites.\n\n"
            "| # | job | task | claim | evidence | Y/N |\n|---|---|---|---|---|---|\n")
    for n,(i,t,cl,ev) in enumerate(rows,1): w.write(f"| {n} | #{i} | {t} | {cl} | `{ev}` | |\n")
json.dump({n:dict(id=i,label=L[i]['label'],split=L[i]['split'],workflow=L[i]['workflow']) for n,(i,*_) in enumerate(rows,1)},open('private/second_reader_key_p5.json','w'),indent=0)
print(len(rows),'rows')
