#!/usr/bin/env python3
"""Read-only export + scrub. Writes private/export.jsonl, private/scrub-test.txt, data/export_counts.json."""
import sqlite3,re,json,random,collections,os,sys
DB="file:ORCH_ROOT/state/orchestrator.db?mode=ro"
EX={'REDACTED_TOPIC','REDACTED_TOPIC','REDACTED_TOPIC','jobs','REDACTED_TOPIC','REDACTED_TOPIC','REDACTED_TOPIC','REDACTED_TOPIC'}
# row dropped entirely if any of these appear (rule 4)
DROP=[r'[\w.+-]+@[\w-]+\.\w+', r'(?<!\w)@[A-Za-z_][\w.]{2,}',
 r'\b(REDACTED_TOPIC|REDACTED_TOPIC|REDACTED_TOPIC|REDACTED_TOPIC|REDACTED_TOPIC?|REDACTED_TOPIC|REDACTED_TOPIC|canvas lms|exam|assessment|interview|job search|cover letter|resume\.\w+|my resume|applicants?|REDACTED_TOPIC|linkedin|REDACTED_TOPIC|reels?)\b',
 r'\bnami\b|\bjuno\b|\bigl?2?\b',
 r'\$\s?\d|\b(stripe|paypal|payout|revenue|profit|bank account|banking|visa|mastercard|invoice|payment|salary|tax|refund|finance|financial|earnings|credit card|adsense|sales?)\b',
 r'\b(REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|prof|mrs|mr|dr|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME|REDACTED_NAME)\b',
 r'\b(virginia|oak street|main street)\b',r'\b(password|api[_ ]?key|token=|oauth)\b']
DROP=re.compile('|'.join(DROP),re.I)
SUBS=[(r'\b(?:Nathan(?:\s+Langley)?|Langley)\b','[OWNER]'),(r'\bUSER\w*\b','[USER]'),(r'\bORCH\b','[ORCH]'),
 (r'(?i)render\s*distance(\s+review)?','[CHANNEL]'),(r'(?i)fair\s*little\s*goods(\.com)?','[STORE]'),
 (r'(?i)[A-Z]:[\\/](?:[^\s`"\')]|\\ )*','[PATH]'),(r'(?:/mnt/(?:pc|host)|/home/\w+|ORCH_ROOT)[^\s`"\')]*','[PATH]'),
 (r'(?i)\bDesktop[\\/][^\s`"\')]*','[PATH]'),(r'https?://\S+','[URL]'),(r'\b\d{1,3}(?:\.\d{1,3}){3}\b','[IP]'),
 (r'\b(UC[\w-]{20,})\b','[CHANNEL]'),(r'\b(?=[\w-]*[a-z])(?=[\w-]*[A-Z])(?=[\w-]*\d)[\w-]{11}\b','[VIDID]')]
SUBS=[(re.compile(a),b) for a,b in SUBS]
def scrub(s):
    for a,b in SUBS: s=a.sub(b,s or '')
    return s
VERIF=re.compile(r'results\.md|results ledger|\bincidents?\b|verify run|verifier|\bjudge[sd]?\b|\bverdict|\bledger\b|\badversar',re.I)
def unleak(s):
    return ' '.join(x for x in re.split(r'(?<=[.!?\n])\s+',s) if not VERIF.search(x)).strip()
RUNNER=re.compile(r'^\s*(runner unit|host job |killed|stopped by|session (exit|died)|hit your session limit)',re.I)
def main():
    c=sqlite3.connect(DB,uri=True); c.row_factory=sqlite3.Row
    os.makedirs('private',exist_ok=True); os.makedirs('data',exist_ok=True)
    n=collections.Counter(); out=[]
    for r in c.execute("select id,created,workflow,task,plan,status,ref,finished,actual,handoff from delegations where status in('done','stopped','failed') order by id"):
        n['all_closed']+=1
        if r['workflow'] in EX: n['excluded_workflow']+=1; continue
        if 'apart' in (r['task'] or '').lower(): n['self']+=1; continue
        if DROP.search((r['task'] or '')+' '+(r['handoff'] or '')): n['dropped_privacy']+=1; continue
        h=r['handoff'] or ''
        d=dict(id=r['id'],created=r['created'],workflow=r['workflow'],plan=r['plan'],status=r['status'],ref=r['ref'],actual=r['actual'],
               runner=bool(RUNNER.search(h)) or len(h.strip())<40,
               task=VERIF.sub('[...]',scrub(r['task'])),handoff=unleak(scrub(h)),truncated=len(h)>=2000)
        out.append(d); n['kept']+=1; n['kept_'+r['status']]+=1
    with open('private/export.jsonl','w') as f:
        for d in out: f.write(json.dumps(d)+'\n')
    rng=random.Random(20261106); s=rng.sample(out,50)
    with open('private/scrub-test.txt','w') as f:
        for d in s: f.write(f"--- {d['id']} {d['workflow']}\nTASK: {d['task']}\nHANDOFF: {d['handoff']}\n")
    # residual proper-noun scan over ALL kept rows
    txt=' '.join(d['task']+' '+d['handoff'] for d in out)
    low=set(re.findall(r'\b[a-z]{3,}\b',txt))
    caps=collections.Counter(w for w in re.findall(r'(?<![\w/.-])[A-Z][a-z]{2,}\b|\b[A-Z]{2,}[a-z]+\b|\b[a-z]+[A-Z]\w+\b',txt) if w.lower() not in low)
    with open('private/scrub-test.txt','a') as f:
        f.write('\n=== residual capitalised tokens not seen lowercase\n'+' '.join(f'{w}:{k}' for w,k in caps.most_common()))
    n['by_workflow']=dict(collections.Counter(d['workflow'] for d in out))
    json.dump(n,open('data/export_counts.json','w'),indent=1,sort_keys=True); print(dict(n))
main()
