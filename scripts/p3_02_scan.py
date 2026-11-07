# Read-only scanner, run on the VM and, through stdin, on the PC. Finds the longest text holding each job's stored report.
# Sources: session transcripts (final assistant text), HANDOFF notes, runner files. Prints JSON {id: [{kind,path,full}]} to stdout.
import json,os,glob,re,sys,time
W=json.loads(WANTED)
ROOTS=ROOTSLIST
SINCE=1792800000  # 2026-10-24 UTC minus a margin
norm=lambda s:re.sub(r'\s+',' ',s or '').strip()
H={i:norm(x) for i,x in W.items()}
def hits(text,kind,path,out):
    n=norm(text)
    if len(n)<40: return
    for i,h in H.items():
        if h in n and n.endswith(h[-60:]):
            out.setdefault(i,[]).append(dict(kind=kind,path=path,full=text,bytes=len(text)))
def last_texts(p):
    sz=os.path.getsize(p)
    with open(p,'rb') as f:
        f.seek(max(0,sz-400000)); b=f.read()
    T=[]
    for l in b.split(b'\n'):
        if b'"assistant"' not in l[:4000] and b'"result"' not in l[:200]: continue
        try: d=json.loads(l)
        except Exception: continue
        if d.get('type')=='assistant':
            t=''.join(c.get('text','') for c in (d.get('message',{}).get('content') or []) if isinstance(c,dict) and c.get('type')=='text')
            if t.strip(): T.append(t)
        elif d.get('type')=='result' and d.get('result'): T.append(d['result'])
    return T[-2:]
out={};seen=0
for root,pat,kind in ROOTS:
    for p in glob.iglob(os.path.join(root,pat),recursive=True):
        try:
            if os.path.getmtime(p)<SINCE: continue
            if kind=='transcript':
                for t in last_texts(p): hits(t,kind,p,out)
            elif os.path.getsize(p)<2000000:
                hits(open(p,errors='replace').read(),kind,p,out)
            seen+=1
        except Exception: pass
print(json.dumps(dict(seen=seen,hits=out)))
