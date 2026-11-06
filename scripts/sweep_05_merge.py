#!/usr/bin/env python3
"""Step 5b: unmasked merge. Writes data/sweep_overrides.json, reruns 03_labels.py, checks the (id,split) diff, writes data/sweep_counts.json and private/sweep_statements.jsonl."""
import json,re,subprocess,collections,sqlite3,datetime as D
Cn=collections.Counter
HAND_DATE='2026-11-06'  # hand_overrides.json committed 2026-11-06 16:59
T=json.load(open('private/sweep_tally.json')); M=json.load(open('private/sweep_mask_map.json'))
hand=json.load(open('data/hand_overrides.json'))
old={json.loads(l)['id']:json.loads(l) for l in open('private/labels_before_sweep.jsonl')}
cand={json.loads(l)['mask']:json.loads(l) for l in open('private/sweep_candidates.jsonl')}
miss={json.loads(l)['mask']:json.loads(l) for l in open('private/sweep_miss_candidates.jsonl')}
db=sqlite3.connect("file:ORCH_ROOT/state/orchestrator.db?mode=ro",uri=True)
evs=dict(db.execute("select id,source from events"))
OWN=re.compile(r"\bNathan\b|\bowner\b|\bhis (note|words|verdict)\b",re.I); JUD=re.compile(r'\bjudges?\b|VERDICT|REVISE|re-judge|blind|adversar',re.I)
def cls(r,line):
    p=r['path'] or ''
    if p.startswith('reports/incidents') or p=='notes/incidents.md': return 'incident'
    if p.startswith('db:events:') and evs.get(int(p.split(':')[2]))=='nathan': return 'owner_defect'
    if p.startswith('Robot30/docs/judges'): return 'judge'
    if JUD.search(line): return 'judge'
    if OWN.search(line): return 'owner_defect'
    return 'verifier_note'
ov={};stm=[];rev=[];handkept=[];dis=[];datefail=[];handclaim=[]
import os,glob
R='ORCH_ROOT/repo/'
fin={i:(f or c0) for i,f,c0 in db.execute("select id,finished,created from delegations")}
def written_by(p,line):
    # latest possible writing time of a statement line: git commit (notes, reports), mtime (verdict files). db rows were filtered on exact time.
    if p.startswith(('notes/','reports/')):
        o=subprocess.run(['git','-C',R,'blame','--line-porcelain','-L',f'{line},{line}','--',p],capture_output=True,text=True).stdout
        return next((int(x.split()[1]) for x in o.split('\n') if x.startswith('author-time ')),None)
    if p.startswith('Robot30/'): return os.path.getmtime('/mnt/host/Desktop/'+p)
    return None
claims={json.loads(l)['mask']:json.loads(l) for l in open('private/sweep_claims.jsonl')}
for m,c in claims.items():
    if c['claim_reread']:
        ov[str(M[m]['id'])]=dict(claim=True,via='claim_reread')
        if 'claim' in hand.get(str(M[m]['id']),{}): handclaim.append(dict(id=M[m]['id'],hand_claim=hand[str(M[m]['id'])]['claim'],why=hand[str(M[m]['id'])]['why']))
for name,TT,CC in (('main',T['main'],cand),('miss',T['miss'],miss)):
    for m,v in TT.items():
        i=v['id']
        if v['note']=='disagree':
            dis.append(dict(id=i,step=name,readers={k[7:13]:(r['decision'],r['path'],r['path_line']) for k,r in v['readers'].items()}))
        if v['result']!='UNEARNED': continue
        rs=list(v['readers'].values()); lines=[CC[m]['lines'][r['line']-1] for r in rs]; cl=[cls(r,l['text']) for r,l in zip(rs,lines)]
        o=dict(id=i,step=name,group=v['group'],claim_at=CC[m]['claim_at'],classes=cl,statements=[dict(model=r['model'],path=r['path'],line=r['path_line'],date=r['date'],date_kind=l['date_kind'],quote=r['quote'],text=l['text']) for r,l in zip(rs,lines)])
        o['date_ok']=all(s['date']>=o['claim_at'][:10] for s in o['statements'])
        for q in o['statements']:
            w=written_by(q['path'],q['line']); q['written_by']=w and str(D.datetime.fromtimestamp(w))[:19]
            if w and w<fin[i]: o['date_ok']=False
        stm.append(o)
        if not o['date_ok']:
            datefail.append(dict(id=i,claim=str(D.datetime.fromtimestamp(fin[i]))[:19],statement=f"{o['statements'][0]['path']}:{o['statements'][0]['line']}",written_by=o['statements'][0]['written_by'])); continue
        h=hand.get(str(i))
        if h:
            latest=max(s['date'] for s in o['statements'])
            if latest>HAND_DATE: rev.append(dict(id=i,hand=h['label'],statement=o['statements'][0]['path'])); r_=True
            else: handkept.append(dict(id=i,hand=h['label'],statement_date=latest,statement=f"{o['statements'][0]['path']}:{o['statements'][0]['line']}")); continue
        e=dict(label='UNEARNED',claim=True,via='sweep_'+name,source_class=cl,ref=[f"{s['path']}:{s['line']} {s['date']}" for s in o['statements']])
        if h: e['reverses_hand']=True
        ov[str(i)]=e
json.dump(ov,open('data/sweep_overrides.json','w'),indent=1,sort_keys=True)
with open('private/sweep_statements.jsonl','w') as f:
    for s in stm: f.write(json.dumps(s)+'\n')
subprocess.run(['python3','scripts/03_labels.py'],check=True,capture_output=True)
new={json.loads(l)['id']:json.loads(l) for l in open('private/labels.jsonl')}
idsplit=[(i,old.get(i,{}).get('split'),new.get(i,{}).get('split')) for i in sorted(set(old)|set(new)) if old.get(i,{}).get('split')!=new.get(i,{}).get('split')]
def pop(L): P=[d for d in L.values() if d['claim']]; return dict(claim=len(P),by_label=dict(Cn(d['label'] for d in P)),by_split_label={f"{a}/{b}":n for (a,b),n in sorted(Cn((d['split'],d['label']) for d in P).items())},noclaim=sum(not d['claim'] for d in L.values()))
moved=[i for i in new if new[i]['claim'] and not old[i]['claim']]
flip=[i for i in new if old[i]['label']=='EARNED' and new[i]['label']=='UNEARNED']
stm_ok=[x for x in stm if x['date_ok']]
un=[i for i in new if new[i]['claim'] and new[i]['label']=='UNEARNED' and new[i]['source']=='sweep']
already=[i for i in new if new[i]['claim'] and new[i]['label']=='UNEARNED' and new[i]['source']=='hand']
newearn=[i for i in new if new[i]['label']=='EARNED' and old[i]['label']!='EARNED']
s={f"{i}":[x for x in stm_ok if x['id']==i][0] for i in un}
cfinal=[]
for i in un:
    k=s[str(i)]['classes']; cfinal.append(k[0] if k[0]==k[1] else 'mixed:'+'/'.join(sorted(k)))
# coverage by split over the jobs searched
cov=collections.defaultdict(lambda:[0,0,0,0])
for m,c in cand.items():
    sp=new[M[m]['id']]['split']; x=cov[sp]; x[0]+=1; x[1]+=len(c['lines']); x[2]+=c['dropped_by_cap']; x[3]+=bool(c['lines'])
meta=json.load(open('private/sweep_search_meta.json'))
ms=[json.loads(l) for l in open('private/sweep_miss_search.jsonl')]
missres=T['miss']
md={'nocand':[0,0,0],'fill':[0,0,0]}
for r in ms:
    k=r['mode']; md[k][0]+=1; v=missres.get(r['mask'])
    if v and v['result']=='UNEARNED': md[k][1]+=1
    if v and v['note']=='disagree': md[k][2]+=1
# coverage: earliest entry per source vs jobs in scope; verdict files named by chain tasks but absent
day=lambda t:str(D.datetime.fromtimestamp(t))[:10]
srcs={}
srcs['reports/incidents']=min(os.path.basename(f)[:10] for f in glob.glob(R+'reports/incidents/*.md'))
srcs['runs.summary']=day(db.execute("select min(started) from runs where summary is not null").fetchone()[0])
srcs['events']=day(db.execute("select min(at) from events").fetchone()[0])
for x in ('notes/incidents.md','notes/results.md','notes/yt_verdicts.tsv'):
    t=re.findall(r'(?m)^[\s\-*|#]*(?:\d+\t)?(20\d\d-\d\d-\d\d)',open(R+x,errors='replace').read()); srcs[x]=min(t) if t else None
scope=sorted(M[m]['id'] for m in cand); fc=lambda i:day(fin[i])
gap={k:dict(first_entry=v,in_scope_ids_finishing_before=[i for i in scope if v and fc(i)<v][:0] or sum(1 for i in scope if v and fc(i)<v),id_range=[(lambda L:[L[0],L[-1]] if L else [])([i for i in scope if v and fc(i)<v])]) for k,v in srcs.items()}
for w in sorted({new[i]['workflow'] for i in scope}):
    a=sorted(glob.glob(R+f'notes/archive/{w}/*.md')); gap['notes/archive/'+w]=dict(first_file=os.path.basename(a[0])[:10] if a else None,has_current_notes=os.path.exists(R+f'notes/{w}.md'),jobs=sum(1 for i in scope if new[i]['workflow']==w))
named=set(re.findall(r'VERDICT-[\w-]+',' '.join(t or '' for t, in db.execute("select task from delegations where workflow='robot30'"))))
have={os.path.basename(f)[:-3] for f in glob.glob('/mnt/host/Desktop/Robot30/docs/judges/VERDICT*.md')}
C=dict(date_demoted=datefail,hand_kept_no_claim=handclaim,source_coverage=gap,verdict_files_named_not_found=sorted(n.rstrip('-') for n in named-have),verdict_files_found=sorted(have),natural_unearned_total=len(un)+len(already),new_from_sweep=len(un),hand_kept_unearned=len(already),new_from_miss_search=sum(1 for x in stm if x['step']=='miss' and x['id'] in un),
 by_split=dict(Cn(new[i]['split'] for i in un+already)),by_workflow=dict(Cn(new[i]['workflow'] for i in un+already)),
 new_by_split=dict(Cn(new[i]['split'] for i in un)),new_by_workflow=dict(Cn(new[i]['workflow'] for i in un)),
 new_by_source_class=dict(Cn(cfinal)),hand_unearned_source='incident (LABELS-CHECK, D5: jobs 426, 458)',
 resting_only_on_ai_judge=sum(1 for c in cfinal if c=='judge'),
 reader_disagreements=dict(main=sum(d['step']=='main' for d in dis),miss_search=sum(d['step']=='miss' for d in dis),ids=[d['id'] for d in dis]),
 before=pop(old),after=pop(new),
 no_claim_moved=len(moved),no_claim_moved_by_split=dict(Cn(new[i]['split'] for i in moved)),no_claim_moved_labels=dict(Cn(new[i]['label'] for i in moved)),no_claim_rereads=len(claims),no_claim_reread_true=sum(1 for c in claims.values() if c['claim_reread']),
 earned_flipped=sorted(flip),earned_new_by_citation_rule=sorted(newearn),hand_reversals=rev,hand_kept_over_sweep=handkept,
 miss_rate=dict(no_candidate_pool=md['nocand'][0],no_candidate_misses=md['nocand'][1],no_candidate_disagreements=md['nocand'][2],fill_from_candidate_jobs=md['fill'][0],fill_misses=md['fill'][1],fill_disagreements=md['fill'][2],note='30 requested from no-candidate jobs; pool held 6, all used. 24 more drawn from jobs readers left without UNEARNED, new lines only.'),
 moves_by_split=dict(unearned_added=dict(Cn(new[i]['split'] for i in un)),earned_flipped=dict(Cn(new[i]['split'] for i in flip)),no_claim_moved=dict(Cn(new[i]['split'] for i in moved))),
 search_coverage_by_split={k:dict(jobs=v[0],candidate_lines=v[1],lines_per_job=round(v[1]/v[0],1),lines_dropped_by_cap=v[2],jobs_with_lines=v[3]) for k,v in cov.items()},
 sources_unreadable=meta['unreadable'],id_split_diff=idsplit,dates_not_after_claim_day=[x['id'] for x in stm if not x['date_ok']],
 readers='All readers are AI models from one provider (Anthropic): claude-sonnet-5-5, claude-opus-5-5. No human checked any decision.')
json.dump(C,open('data/sweep_counts.json','w'),indent=1,sort_keys=True)
print(json.dumps({k:C[k] for k in ('natural_unearned_total','new_from_sweep','by_split','by_workflow','new_by_split','new_by_workflow','new_by_source_class','resting_only_on_ai_judge','before','after','no_claim_moved','no_claim_moved_by_split','no_claim_moved_labels','earned_flipped','hand_kept_over_sweep','hand_kept_no_claim','date_demoted','moves_by_split','search_coverage_by_split','source_coverage','verdict_files_named_not_found','verdict_files_found','id_split_diff','dates_not_after_claim_day')},indent=0))
