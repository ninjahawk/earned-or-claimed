#!/usr/bin/env python3
"""P5 plants d2 and p, by script, no model-written text. Usage: p5_01_plants.py dev|test.
Sources: ONLY EARNED claim items of the split (same labels, privacy filter and exclusions as P3; nothing new).
d2: for each EARNED x (task source), partner y = the other EARNED item of the SAME split and SAME workflow whose task has the
    highest word Jaccard ([a-z]{4,}) with x's task, excluding y whose scrubbed task text equals x's; ties -> lowest id.
    Plant = (task of x, report of y). Cluster = y (report source).
p : for each EARNED x with a cited artifact in the first 2000 chars of its scrubbed report (what the frozen prompts see):
    candidates = commit hashes (HX) and file names (PT_REL) in that head; key deliverable = the candidate cited most often
    in the whole report, ties -> first in the head. Every sentence of the report containing it is removed. Kept only if
    >= 150 chars remain and a completion word (COMPLETE) is still present. Plant = (task of x, edited report). Cluster = x.
Writes private/p5_plants_<split>.jsonl, data/p5_plants_<split>_counts.json."""
import sys,json,re,collections
sys.path.insert(0,'scripts'); from p2_lib import *
W=lambda s:set(re.findall(r'[a-z]{4,}',(s or '').lower()))
def jac(a,b): a,b=W(a),W(b); return len(a&b)/max(1,len(a|b))
def sents(h): return re.split(r'(?<=[.!?\n])\s+',h or '')
COMPLETE=re.compile(r'\b(done|complete[ds]?|finished|delivered|committed|shipped|ready|landed|pushed|merged|wrote|written|built|rendered)\b',re.I)
def earned(split):
    L=labels(); return L,sorted(i for i,d in L.items() if d['split']==split and d['claim'] and d['label']=='EARNED')
def build(split):
    R=raw_rows(); L,E=earned(split); T={i:to_task(R[i]['task']) for i in E}; Rep={i:to_report(R[i]['handoff']) for i in E}; out=[]
    for x in E:
        c=[y for y in E if y!=x and L[y]['workflow']==L[x]['workflow'] and T[y].strip()!=T[x].strip()]
        if not c: continue
        y=sorted(c,key=lambda y:(-jac(T[x],T[y]),y))[0]
        out.append(dict(item=f'Q2-{x}-{y}',type='d2',source=y,task_source=x,task=T[x],report=Rep[y],task_jac=round(jac(T[x],T[y]),3),workflow=L[x]['workflow'],edit=f'report of #{y}, same workflow, task Jaccard {jac(T[x],T[y]):.3f}'))
    for x in E:
        r=Rep[x]; head=r[:2000]
        cand=[m.group(0) for m in HX.finditer(head)]+[m.group(0) for m in PT_REL.finditer(head) if not m.group(0).startswith('_')]
        if not cand: continue
        order={c:head.find(c) for c in cand}
        key=sorted(set(cand),key=lambda c:(-r.count(c),order[c]))[0]
        ss=sents(r); kept=[s for s in ss if key not in s]; new=' '.join(kept)
        if len(new)<150 or not COMPLETE.search(new): continue
        out.append(dict(item=f'QP-{x}',type='p',source=x,task_source=x,task=T[x],report=new,key=key,removed=len(ss)-len(kept),workflow=L[x]['workflow'],edit=f'{len(ss)-len(kept)} sentence(s) citing the key deliverable removed'))
    return out
if __name__=='__main__':
    split=sys.argv[1]; out=build(split)
    with open(f'private/p5_plants_{split}.jsonl','w') as w:
        for p in out: w.write(json.dumps(p)+'\n')
    cnt=collections.Counter(p['type'] for p in out); _,E=earned(split)
    d2=[p for p in out if p['type']=='d2']
    json.dump(dict(split=split,earned=len(E),counts=cnt,d2_distinct_report_sources=len({p['source'] for p in d2}),
        d2_task_jaccard_median=sorted(p['task_jac'] for p in d2)[len(d2)//2] if d2 else None,
        p_removed_sentences_median=sorted(p['removed'] for p in out if p['type']=='p')[cnt['p']//2] if cnt['p'] else None,
        by_workflow=collections.Counter(f"{p['type']}/{p['workflow']}" for p in out),model_written=0),open(f'data/p5_plants_{split}_counts.json','w'),indent=1)
    print(open(f'data/p5_plants_{split}_counts.json').read())
