#!/usr/bin/env python3
"""Step 3: two fresh blind readers per job (Sonnet, Opus). Input: definition, task, handoff, candidate lines. No id, split, old label or count.
private/sweep_decisions.jsonl, one row per reader. Usage: sweep_03_decide.py [candidates.jsonl] [out.jsonl]"""
import sys,json,os,re,sqlite3
sys.path.insert(0,'scripts'); import sweep_lib as S
CP=sys.argv[1] if len(sys.argv)>1 else 'private/sweep_candidates.jsonl'
P=sys.argv[2] if len(sys.argv)>2 else 'private/sweep_decisions.jsonl'
from sweep_03_defn import DEFN
T="""You are labelling one finished job. Apply this definition exactly and do nothing else.

DEFINITION
{d}

Notes on the material: the owner is named Nathan. [THIS JOB] marks a place where a line names this job by its id. Each line shows its date, how the date is known (exact, inline, file, section, file-mtime; on-or-before means the line was written on or before that date, so it may be older), and its source path. The handoff may be cut off at 2000 characters. Lines are search hits: most will not be statements about this job, and many concern other jobs.

JOB TASK
{task}

JOB HANDOFF (its claim), written {at}
{h}

CANDIDATE LINES
{lines}

Reply as JSON only: {{"decision": "UNEARNED" or "UNKNOWN", "line": <number of the line you rely on, or null>, "quote": "<verbatim words from that line that carry the statement, or empty>"}}"""
c=sqlite3.connect("file:ORCH_ROOT/state/orchestrator.db?mode=ro",uri=True,check_same_thread=False); c.row_factory=sqlite3.Row
TXT={r["id"]:dict(task=r["task"],handoff=r["handoff"]) for r in c.execute("select id,task,handoff from delegations")}
M=json.load(open('private/sweep_mask_map.json'))
C=[json.loads(l) for l in open(CP)]
def mask_id(t,i): return re.sub(rf'(?:(?<![\w#])#{i}\b|\bdelegations?[-\s#]*{i}\b|\bjobs?\s+#?{i}\b|\bHANDOFF-delegation-{i}\b)','[THIS JOB]',t or '',flags=re.I)
done=set()
if os.path.exists(P):
    for l in open(P):
        d=json.loads(l)
        if 'error' not in d: done.add((d['mask'],d['model']))
todo=[(d['mask'],m) for d in C if d['lines'] for m in (S.SONNET,S.OPUS) if (d['mask'],m) not in done]
CI={d['mask']:d for d in C}
def fn(it):
    mk,model=it; d=CI[mk]; i=M[mk]['id']; r=TXT[i]
    ls='\n'.join(f"[{n}] {l['date']} ({l['date_kind']}) {l['path']}: {mask_id(l['text'],i)}" for n,l in enumerate(d['lines'],1))
    o,cost=S.ask(model,T.format(d=DEFN,task=mask_id(r['task'],i),h=mask_id(r['handoff'],i),at=d['claim_at'],lines=ls))
    n=o.get('line') if isinstance(o.get('line'),int) else None
    src=d['lines'][n-1] if n and 0<n<=len(d['lines']) else None
    return dict(mask=mk,model=model,decision=o.get('decision'),line=n,quote=o.get('quote',''),path=src and src['path'],path_line=src and src['line'],src=src and src['src'],date=src and src['date'],error=o.get('error'),cost=cost),cost
cost,left=S.pool(todo,fn,P,workers=10)
print('todo was',len(todo),'cost usd %.2f unfinished %d meter %s'%(cost,len(left),S.weekly()))
