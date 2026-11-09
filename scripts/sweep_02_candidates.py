#!/usr/bin/env python3
"""Step 2: scripted candidate search. Same rules for every job; decides no labels.
For each job in scope: lines naming its id or its artifacts, in the listed sources, not dated before its claim. private/sweep_candidates.jsonl."""
import json,re,os,glob,sqlite3,subprocess,collections,datetime as D
import os,sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from private_terms import *
R='ORCH_ROOT/repo/'; CH=[188,200,218,226,230,247,289,293,306,313,322,336]
VD='/mnt/host/Desktop/Robot30/docs/judges/'
EX=EXCLUDED_WORKFLOWS
c=sqlite3.connect("file:ORCH_ROOT/state/orchestrator.db?mode=ro",uri=True); c.row_factory=sqlite3.Row
DL={r['id']:dict(r) for r in c.execute("select id,created,finished,workflow,status,task,handoff from delegations")}
M=json.load(open('private/sweep_mask_map.json'))
cl={json.loads(l)['mask']:json.loads(l) for l in open('private/sweep_claims.jsonl')}
jobs={v['id']:m for m,v in M.items() if v['group']!='B' or cl.get(m,{}).get('claim_reread')}
unread=[]
day=lambda t:D.datetime.fromtimestamp(t).date()
LEAD=re.compile(r'^[\s\-*|#]*(?:(20\d\d)-)?(\d\d)-(\d\d)\b')
def blame(rel):
    try:
        o=subprocess.run(['git','-C',R,'blame','--line-porcelain','--',rel],capture_output=True,text=True,timeout=120,errors='replace').stdout
        return [int(x.split()[1]) for x in o.split('\n') if x.startswith('author-time ')]
    except Exception: return []
S=[]  # dict(path,line,end,scope,kind,exact,day,dk,text,src)
def addfile(fp,rel,scope,cls,fname_day=None,prefix=''):
    try: L=open(fp,errors='replace').read().split('\n')
    except Exception as e: unread.append(f'{rel}: {e}'); return
    bl=blame(rel) if rel.startswith(('notes','reports')) else []
    sect=None;i=0
    while i<len(L):
        l=L[i]; st=i; b=l
        while i+1<len(L) and re.match(r'^\s{2,}\S',L[i+1]) and b.strip() and not b.lstrip().startswith('#'): i+=1; b+=' '+L[i].strip()
        i+=1
        if not b.strip(): continue
        m=LEAD.match(b); dk='inline'
        def mk(m):
            try: return D.date(int(m.group(1) or 2026),int(m.group(2)),int(m.group(3)))
            except ValueError: return None
        d=mk(m) if m else None
        if b.lstrip().startswith('#'):
            s=re.search(r'(?:(20\d\d)-)?(\d\d)-(\d\d)\b',b); sect=mk(s) if s else None
        if not d:
            if fname_day: d,dk=fname_day,'file'
            elif sect: d,dk=sect,'section'
            elif st<len(bl): d,dk=day(bl[st]),'on-or-before(git)'
            else: d,dk=None,'unknown'
        S.append(dict(path=rel,line=st+1,end=i,scope=scope,exact=None,day=d,dk=dk,text=prefix+b,src=cls))
for f in sorted(glob.glob(R+'reports/incidents/*.md')):
    n=os.path.basename(f); m=re.match(r'(\d{4})-(\d\d)-(\d\d)',n)
    addfile(f,'reports/incidents/'+n,'*','incident',D.date(*map(int,m.groups())) if m else None,f'[report {n[:-3]}] ')
addfile(R+'notes/incidents.md','notes/incidents.md','*','incident')
addfile(R+'notes/results.md','notes/results.md','*','results')
addfile(R+'notes/yt_verdicts.tsv','notes/yt_verdicts.tsv','yt','yt_verdicts')
wfs=sorted({DL[i]['workflow'] for i in jobs})
for w in wfs:
    if os.path.exists(R+f'notes/{w}.md'): addfile(R+f'notes/{w}.md',f'notes/{w}.md',w,'wf_notes')
    for f in sorted(glob.glob(R+f'notes/archive/{w}/*.md')):
        m=re.match(r'(\d{4})-(\d\d)-(\d\d)',os.path.basename(f))
        addfile(f,f'notes/archive/{w}/{os.path.basename(f)}',w,'wf_archive',None)
for f in sorted(glob.glob(R+'notes/archive/system/*.md')):
    addfile(f,'notes/archive/system/'+os.path.basename(f),'*','system_archive')
for r in c.execute("select id,workflow,purpose,started,finished,summary from runs where summary is not null"):
    if r['workflow'] in EX or re.search(r'\bApart\b',r['summary']): continue
    t=r['finished'] or r['started']
    S.append(dict(path=f'db:runs:{r["id"]}',line=1,end=1,scope='*',exact=t,day=day(t),dk='exact',text=r['summary'],src='run'))
NOISE={'ledger','budget','context','plan','host','daemon'}
for r in c.execute("select id,at,source,workflow,msg from events where msg is not null"):
    if r['workflow'] in EX or re.search(r'\bApart\b',r['msg']): continue
    # machine watch lines are not statements; 'run #N exit' events duplicate runs.summary, searched above
    if re.match(r'#\d+ EXPECT\b|run #\d+ exit',r['msg']): continue
    S.append(dict(path=f'db:events:{r["id"]}',line=1,end=1,scope='*',exact=r['at'],day=day(r['at']),dk='exact',text=r['msg'],src='event_noise' if r['source'] in NOISE else 'event'))
# judge-fix chains: statement text of the chain job and its verdict file reach the jobs before it
vlines=collections.defaultdict(list)
if os.path.isdir(VD):
    for f in sorted(glob.glob(VD+'VERDICT*.md')):
        n=os.path.basename(f)[:-3]; ts=os.path.getmtime(f)
        try:
            for k,l in enumerate(open(f,errors='replace'),1):
                if re.search(r'\b(FAIL|REJECT|NOT MET|BLOCK|NOT PASS|does not|missing|wrong|false|stale)\b',l,re.I) and l.strip():
                    vlines[n].append(dict(path='Robot30/docs/judges/'+os.path.basename(f),line=k,end=k,scope='robot30',exact=ts,day=day(ts),dk='file-mtime',text=f'[{n}] '+l.strip(),src='judge_verdict'))
        except Exception as e: unread.append(f'{n}: {e}')
else: unread.append(VD+': not a directory')
for v in vlines.values(): S.extend(v)
chain=collections.defaultdict(list)
for x in CH:
    X=DL[x]; prev=[i for i in sorted(DL,reverse=True) if i<x and DL[i]['workflow']==X['workflow'] and DL[i]['status']=='done'][:3]
    ls=[dict(path=f'db:delegations:{x}:task',line=1,end=1,exact=X['created'],day=day(X['created']),dk='exact',text=X['task'] or '',src='judge_chain')]
    for k,hl in enumerate((X['handoff'] or '').split('\n')[:40],1):
        if hl.strip(): ls.append(dict(path=f'db:delegations:{x}:handoff',line=k,end=k,exact=X['finished'] or X['created'],day=day(X['finished'] or X['created']),dk='exact',text=hl,src='judge_chain'))
    for vn in set(re.findall(r'VERDICT-[\w-]+',(X['task'] or ''))): ls+=vlines.get(vn,[])[:15]
    for i in prev: chain[i]+=ls
# terms
TOK=re.compile(r'(?<![\w.-])(?:[A-Za-z]+\d[\w.-]*|\d+[A-Za-z][\w.-]*|[A-Za-z]+-[\w-]+|[0-9a-f]{7,12}|\d{3})(?![\w-])')
FN=re.compile(r'\b[\w-]+\.(?:md|py|gd|mp4|png|json|blend|ps1|tsv|jsonl|pdf|tscn)\b')
SHA=re.compile(r'\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,12}\b')
BAD=re.compile(r'^(\d+[hmskK]|\d+fps|\d+[pP]|\d+[dD]|\d+x\d*|x\d+|v\d|r\d|claude-.*|sonnet.*|opus.*|non-.*|self-.*|side-.*|end-.*|re-.*|by-.*|one-.*|two-.*|host-.*|vm-.*|\d+-.*|CLAUDE\.md|HANDOFF.*|RESPONSE\.md|README\.md|SPEC\.md|result\.json|\d{3}p)$',re.I)
def terms(j):
    t=j['task'] or ''; h=j['handoff'] or ''
    a=set(x.rstrip('.') for x in TOK.findall(t)); a|=set(FN.findall(t))|set(FN.findall(h))|set(SHA.findall(h))|set(SHA.findall(t))
    return {x for x in a if not BAD.match(x) and len(x)>=2}
ALLT={i:terms(DL[i]) for i in DL}
dfw=collections.Counter(); dfg=collections.Counter()
for i,ts in ALLT.items():
    for x in ts: dfg[x]+=1; dfw[(DL[i]['workflow'],x)]+=1
WORDS=lambda t:set(w.lower() for w in re.findall(r'\b[A-Za-z]{6,}\b',t or ''))
dfword=collections.Counter(w for i in DL for w in WORDS(DL[i]['task']))
sent=collections.defaultdict(list)
for fn in ('true_positives','false_positives'):
    p=f'ORCH_ROOT/state/sentinel/{fn}.jsonl'
    try:
        for l in open(p):
            try: d=json.loads(l)
            except ValueError: continue
            if str(d.get('job','')).isdigit(): sent[int(d['job'])].append(d.get('note') or '')
    except Exception as e: unread.append(f'{p}: {e}')
DEF=re.compile(r"fail|reject|missing|wrong|stale|false|defect|broken|\bbug|not done|did not|didn't|never|no result|flicker|redo|rework|contradict|wasn't|empty|unmet|below|incident|not met|bad\b|doesn't|does not",re.I)
YT=re.compile(r'youtube|REDACTED_CHANNEL|video|short|\bYT\b',re.I)
SK=re.compile(r'(run|wake|check|EXPECT|exp|video|issue|PR|ask|watch|mail|Q|sub)\s*$',re.I)
def idpat(i): return re.compile(rf'(?:(?<![\w#])#{i}\b|\bdelegations?[-\s#]*{i}\b|\bjobs?\s+#?{i}\b|#\d+\s*[/+,&]\s*#?{i}\b|\bHANDOFF-delegation-{i}\b)',re.I)
def win(t,m,n=350):
    if len(t)<=2*n+40: return t
    a=max(0,m.start()-n); return ('…' if a else '')+t[a:m.end()+n]+('…' if m.end()+n<len(t) else '')
CAP=30
out=[];cover=collections.Counter()
for i,mask in jobs.items():
    j=DL[i]; w=j['workflow']; fin=j['finished'] or j['created']; fd=day(fin)
    ts=[x for x in ALLT[i] if dfw[(w,x)]<=6 and dfg[x]<=10]
    for n in sent.get(i,[]): ts+=[x for x in SHA.findall(n)]
    ts=sorted(set(ts),key=lambda x:(not re.search(r'\d',x),len(x)))[:20]
    num=[x for x in ts if x.isdigit()]; strong=[re.escape(x) for x in ts if not x.isdigit()]
    rs=re.compile(r'(?<![\w-])(?:'+'|'.join(strong)+r')(?![\w-])') if strong else None
    rn=re.compile(r'(?<![\w#-])(?:'+'|'.join(num)+r')(?![\w-])') if num else None
    wd=[x for x in WORDS(j['task']) if dfword[x]<=3][:10]
    rw=re.compile(r'\b(?:'+'|'.join(map(re.escape,wd))+r')\b',re.I) if wd else None
    pid=idpat(i)
    yt=w in('youtube','ytreal')
    hits=[]
    pool=[s for s in S if s['scope'] in('*',w) or (s['scope']=='yt' and yt)]
    for s in pool:
        if s['exact'] is not None:
            if s['exact']<=fin: continue
        elif s['day'] and s['day']<fd: continue
        t=s['text']; tier=None; m=None
        for q in pid.finditer(t):
            if not SK.search(t[max(0,q.start()-8):q.start()]): m=q; tier=1; break
        if s['src']=='event_noise' and not (tier and DEF.search(win(t,m,220))): continue
        if not tier and rs:
            q=rs.search(t)
            if q: m=q; tier=2 if DEF.search(win(t,q,220)) else 4
        if not tier and rn and s['scope'] in('yt',w) or (not tier and rn and YT.search(t)):
            q=rn.search(t)
            if q: m=q; tier=2 if DEF.search(win(t,q,220)) else 4
        if not tier and rw and s['scope'] in (w,):
            q=rw.search(t)
            if q and DEF.search(win(t,q,220)): m=q; tier=3
        if tier: hits.append((tier,s,m))
    seen=set(); L=[]
    for x in chain.get(i,[]):
        if x['exact'] and x['exact']<=fin: continue
        k=(x['path'],x['line'])
        if k not in seen: seen.add(k); L.append(dict(path=x['path'],line=x['line'],end=x['end'],date=str(x['day']),date_kind=x['dk'],tier=2,src=x['src'],text=x['text'][:700]))
    for tier,s,m in sorted(hits,key=lambda h:(h[0],str(h[1]['day']))):
        k=(s['path'],s['line'])
        if k in seen: continue
        seen.add(k); L.append(dict(path=s['path'],line=s['line'],end=s['end'],date=str(s['day']),date_kind=s['dk'],tier=tier,src=s['src'],text=win(s['text'],m)))
    # a candidate line is an id/artifact match with a defect word nearby; other id/artifact lines are context only
    for l in L: l['defect_word']=bool(DEF.search(l['text']))
    L.sort(key=lambda d:(not d['defect_word'],d['tier']))
    trig=any(l['defect_word'] for l in L)
    tot=len(L); L=L[:CAP+(10 if i in sent else 0)]
    out.append(dict(mask=mask,triggered=trig,lines=L if trig else [],context_nontrigger=[] if trig else L,total_hits=tot,dropped_by_cap=tot-len(L),terms=ts,sentinel_pointer=i in sent,claim_at=str(D.datetime.fromtimestamp(fin))[:16],sources_searched=sorted({s['src'] for s in pool})+(['judge_chain'] if i in chain else [])))
with open('private/sweep_candidates.jsonl','w') as f:
    for d in out: f.write(json.dumps(d)+'\n')
json.dump(dict(unreadable=unread,sources=len(S),chain_targets=len(chain)),open('private/sweep_search_meta.json','w'))
n=len(out); w=sum(1 for d in out if d['lines']); print('jobs',n,'with lines',w,'lines',sum(len(d['lines']) for d in out),'defect lines',sum(l['defect_word'] for d in out for l in d['lines']),'capped jobs',sum(1 for d in out if d['dropped_by_cap']),'tier1 jobs',sum(any(l['tier']==1 for l in d['lines']) for d in out),'source blocks',len(S),'unreadable',unread[:5],'chars',sum(len(l['text']) for d in out for l in d['lines']))
