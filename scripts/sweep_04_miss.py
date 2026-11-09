#!/usr/bin/env python3
"""Step 4: miss rate. Fresh Sonnet with read-only tools searches a copy of the same sources for one job.
Hits go to private/sweep_miss_candidates.jsonl, then through sweep_03_decide.py. Usage: sweep_04_miss.py nocand|fill N"""
import sys,json,os,re,glob,shutil,sqlite3,random
import os,sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from private_terms import *
sys.path.insert(0,'scripts'); import sweep_lib as S
from sweep_03_defn import DEFN
mode=sys.argv[1]; N=int(sys.argv[2]) if len(sys.argv)>2 else 30
R='ORCH_ROOT/repo/'; T='/tmp/sweep_src'
EX=EXCLUDED_WORKFLOWS
c=sqlite3.connect("file:ORCH_ROOT/state/orchestrator.db?mode=ro",uri=True); c.row_factory=sqlite3.Row
TXT={r['id']:dict(r) for r in c.execute("select id,workflow,task,handoff,finished,created from delegations")}
M=json.load(open('private/sweep_mask_map.json'))
C=[json.loads(l) for l in open('private/sweep_candidates.jsonl')]
if not os.path.exists(T+'/.ok'):
    shutil.rmtree(T,ignore_errors=True); os.makedirs(T+'/notes/archive'); os.makedirs(T+'/db'); os.makedirs(T+'/reports')
    shutil.copytree(R+'reports/incidents',T+'/reports/incidents')
    for f in ('incidents.md','results.md','yt_verdicts.tsv'): shutil.copy(R+'notes/'+f,T+'/notes/')
    for w in sorted({TXT[v['id']]['workflow'] for v in M.values()}|{'system'}):
        if w in EX: continue
        if os.path.exists(R+f'notes/{w}.md'): shutil.copy(R+f'notes/{w}.md',T+'/notes/')
        if os.path.isdir(R+f'notes/archive/{w}'): shutil.copytree(R+f'notes/archive/{w}',T+f'/notes/archive/{w}')
    with open(T+'/db/runs.txt','w') as f:
        for r in c.execute("select id,workflow,started,summary from runs where summary is not null"):
            if r['workflow'] in EX or re.search(r'\bApart\b',r['summary']): continue
            f.write(f"run {r['id']} {r['workflow']} {r['started']:.0f}: "+r['summary'].replace('\n',' ')+'\n')
    with open(T+'/db/events.txt','w') as f:
        for r in c.execute("select id,at,source,workflow,msg from events where msg is not null"):
            if r['workflow'] in EX or re.search(r'\bApart\b',r['msg']): continue
            f.write(f"event {r['id']} {r['source']} {r['at']:.0f}: "+r['msg'].replace('\n',' ')+'\n')
    os.makedirs(T+'/judges'); [shutil.copy(x,T+'/judges/') for x in glob.glob('/mnt/host/Desktop/Robot30/docs/judges/VERDICT*.md')]
    open(T+'/.ok','w').write('1')
PR="""Search the files in the current directory for written statements about one finished job, under the definition below. Do not decide the job's label; report every line that could be such a statement.

DEFINITION
{d}

Sources: reports/incidents/, notes/ (incl. notes/archive/), db/runs.txt and db/events.txt (the last-but-one column is a unix timestamp), judges/. Search by the job id (forms: #{i}, delegation {i}, job {i}, HANDOFF-delegation-{i}) and by the job's specific artifacts named in its task and handoff (video numbers, features, reports, commits). Use grep with a line-number result; no more than 12 tool calls. Only lines dated after the claim count.

JOB ID: {i}
JOB TASK: {task}
JOB HANDOFF, written {at}: {h}

Reply as JSON only: {{"hits":[{{"path":"...","line":<number>,"date":"YYYY-MM-DD","text":"<the line, verbatim, up to 600 characters>"}}]}} (empty list if none)."""
S_=random.Random(20261106)
nocand=sorted(M[d['mask']]['id'] for d in C if not d['lines'])
if mode=='nocand': pick=S_.sample(nocand,min(N,len(nocand)))
else:
    D=[json.loads(l) for l in open('private/sweep_decisions.jsonl')]
    une={d['mask'] for d in D if d['decision']=='UNEARNED'}
    pool=sorted(M[d['mask']]['id'] for d in C if d['lines'] and d['mask'] not in une)
    pick=S_.sample(pool,min(N,len(pool)))
Pth='private/sweep_miss_search.jsonl'; have={json.loads(l)['id'] for l in open(Pth)} if os.path.exists(Pth) else set()
rev={v['id']:m for m,v in M.items()}
import datetime as DT
def fn(i):
    j=TXT[i]; fin=j['finished'] or j['created']
    o,cost=S.ask(S.SONNET,PR.format(d=DEFN,i=i,task=j['task'],h=j['handoff'],at=str(DT.datetime.fromtimestamp(fin))[:16]),system='You are a careful search assistant with read-only tools. Reply with one JSON object at the end.',tools='Read,Grep,Glob',extra=('--allowedTools','Read,Grep,Glob','--max-budget-usd','0.40'),cwd=T,timeout=280,tries=1)
    return dict(id=i,mask=rev[i],mode=mode,hits=o.get('hits',[]),error=o.get('error'),cost=cost),cost
cost,left=S.pool([i for i in pick if i not in have],fn,Pth,workers=6)
print('mode',mode,'picked',len(pick),'cost %.2f unfinished %d meter %s'%(cost,len(left),S.weekly()))
