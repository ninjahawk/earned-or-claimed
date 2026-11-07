#!/usr/bin/env python3
"""G2 frozen on another model, same prompt, threshold 60, on the labelled items where raw G1 passed and phase 2 made a call. Artifact re-read now by p2_07's own function; its length is compared with phase 2's. Usage: p3_07_g2.py <model> <repeats> [deadline]."""
import sys,concurrent.futures as X; sys.path.insert(0,'scripts'); from p3_lib import *
m,rep=sys.argv[1],int(sys.argv[2]); dl=int(sys.argv[3]) if len(sys.argv)>3 else 540
src=open('scripts/p2_07_gate.py').read().split('items=[]')[0]; a0=sys.argv; sys.argv=['x','test']; ns={}; exec(src,ns); sys.argv=a0
art=ns['art']; SYS=ns['SYS']; F=ns['F']; L=ns['L']; R=ns['R']; J=ns['J']
G=[json.loads(l) for l in open('private/gate_test.jsonl')]; G=[g for g in G if g['arm']!='UNKNOWN' and g['g1_pass'] and g.get('g2') is not None]; assert len(G)==89,len(G)
P={json.loads(l)['item']:json.loads(l) for l in open('private/plants_test.jsonl')}
C='private/p3_artifacts.json'; cache=json.load(open(C)) if os.path.exists(C) else {}
def info(g):
    if g['item'] in P: p=P[g['item']]; return p['facts'],p['raw'],p['task'],p['report']
    i=int(g['item']); return F[i],R[i]['handoff'],J[i]['task'],J[i]['handoff']
def fetch(g):
    f,raw,_,_=info(g); a,k=art(f,raw); return g['item'],a,k
miss=[g for g in G if g['item'] not in cache]
with X.ThreadPoolExecutor(5) as ex:
    for it,a,k in ex.map(fetch,miss): cache[it]=dict(a=a,k=k)
json.dump(cache,open(C,'w'))
ch=[(g['item'],g['art_chars'],len(cache[g['item']]['a'])) for g in G if len(cache[g['item']]['a'])!=g['art_chars']]; print('artifact length changed since phase 2:',len(ch),ch[:8])
G={g['item']:g for g in G}
def one(j):
    _,_,task,report=info(G[j['item']]); a=cache[j['item']]['a']
    if not a: return dict(score=None,abstain=True)
    return call(SYS,f"TASK:\n{task[:1500]}\n\nREPORT'S CLAIM:\n{report[:1000]}\n\nARTIFACT EXCERPT (scrubbed):\n{a}\n",model=j['model'])
jobs=[dict(item=i,arm=g['arm'],level='G2',rep=r,model=m,source=g['source'],ver='frozen') for i,g in G.items() for r in range(rep)]
run(jobs,'private/p3_g2.jsonl',one,deadline=dl)
