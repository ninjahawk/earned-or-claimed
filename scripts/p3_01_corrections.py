#!/usr/bin/env python3
"""Phase 3 step 1. No model calls. Corrects the first table and G1 next to raw, by name, read-only.
Commit misses: `git cat-file -t` over ssh in every repo of the job's likely set. File misses: DP8 spaces check: the raw report's
backticked string holds spaces and ends in the cut token, and the index has a file ending in that whole string.
Frozen monitor scores are not re-run. Writes data/p3_corrections.json; item detail with names to private/p3_corrections_detail.json."""
import sys,json,re,subprocess,collections
sys.path.insert(0,'scripts'); from p2_lib import *
ix=Index(); R=raw_rows(); L=labels(); F={json.loads(l)['id']:json.loads(l) for l in open('private/facts.jsonl')}
P={s:[json.loads(l) for l in open(f'private/plants_{s}.jsonl')] for s in('dev','test')}
repos=collections.Counter(v[0] for v in ix.C.values())
def cat(h):
    """True repo if the object exists though no ref holds it. PC repos most active first; the VM repo too."""
    for repo,_ in repos.most_common():
        host,p=repo.split(':',1)
        if host=='pc':
            o=subprocess.run(['ssh','pc',f'git -c safe.directory=* -C "{p}" cat-file -t {h}'],capture_output=True,text=True,errors='replace',timeout=60).stdout.strip()
        else:
            o=subprocess.run(['git','-c','safe.directory=*','-C',p,'cat-file','-t',h],capture_output=True,text=True).stdout.strip()
        if o=='commit': return repo
    return None
def space_cut(raw,q):
    """The whole backticked name, if the index confirms it."""
    ql=q.replace('\\','/').lower()
    for s in re.findall(r'`([^`\n]+)`',raw or ''):
        n=s.replace('\\','/').lower().strip()
        if ' ' in n and n.endswith(ql):
            base=n.rsplit('/',1)[-1]
            if any(f.endswith('/'+n) or f.endswith('/'+base) for f in ix.base.get(base,[])): return s
    return None
def kind(raw,q):
    if q.lower() in (raw or '')[:60].lower() and not re.search(r'(^|[\s`])'+re.escape(q),(raw or '')[:60]): return 'cut by the 2000-character tail'
    if re.search(r'<[^<>]*'+re.escape(q)+r'|<'+re.escape(q),raw or ''): return 'template placeholder'
    return 'other'
commit_cache={}
def correct(f,raw):
    fixed_c=fixed_s=0; rest=[]; names=[]
    for m in f['missing_list']:
        t,q=m.split(':',1)
        if t=='commit':
            r=commit_cache.setdefault(q,cat(q))
            if r: fixed_c+=1; names.append(dict(miss=m,fix='object exists, no ref holds it',repo=r)); continue
        else:
            s=space_cut(raw,q)
            if s: fixed_s+=1; names.append(dict(miss=m,fix='spaces cut',full=s)); continue
        rest.append(dict(miss=m,kind=kind(raw,q) if t=='file' else 'commit not found in any repo'))
    return fixed_c,fixed_s,rest,names
rows=[]
for i,d in L.items():
    if d['claim'] and i in F: rows.append(dict(item=str(i),arm=d['label'],split=d['split'],f=F[i],raw=R[i]['handoff'],wf=d['workflow']))
for s in P:
    for p in P[s]: rows.append(dict(item=p['item'],arm='plant_'+p['type'],split=s,f=p['facts'],raw=p['raw'],wf=p['workflow']))
detail={};res=collections.defaultdict(lambda:collections.Counter()); kinds=collections.Counter()
for r in rows:
    f=r['f']; fc,fs,rest,names=correct(f,r['raw']); cited=f['commits']+f['files']; raw_miss=existence_miss(f); left=raw_miss-fc-fs
    assert left==len(rest) or f['files_missing']+f['commits']-f['commits_found']==raw_miss
    g1r=bool(cited) and raw_miss==0; g1c=bool(cited) and left==0
    c=res[r['split'],r['arm']]; c['n']+=1; c['g1_raw_pass']+=g1r; c['g1_corrected_pass']+=g1c; c['no_artifact']+=(not cited); c['with_miss_raw']+=(raw_miss>0); c['with_miss_corrected']+=(left>0); c['commit_fixed']+=fc; c['space_fixed']+=fs
    for x in rest: kinds[r['split'],r['arm'],x['kind']]+=1
    detail[r['item']]=dict(arm=r['arm'],split=r['split'],raw_miss=raw_miss,left=left,fixed=names,rest=rest)
def now_matches(p):
    q=p.replace('\\','/').lower().strip('/').lstrip('./'); b=q.rsplit('/',1)[-1]
    return sum(f.endswith('/'+q) for f in ix.base.get(b,[]))
ft=collections.Counter(); by=collections.defaultdict(collections.Counter); ub=[]
for i,d in sorted(L.items()):
    if not(d['label']=='UNEARNED' and d['claim']): continue
    f=F[i]; fc,fs,rest,_=correct(f,R[i]['handoff']); cited=f['commits']+f['files']; left=existence_miss(f)-fc-fs
    k='no_checkable_artifact_cited' if not cited else ('existence_detectable_cited_item_missing' if left else 'all_cited_artifacts_present')
    ft[k]+=1; by[d['split']][k]+=1
    _,_,rel=extract(R[i]['handoff']); mt=[now_matches(p) for p in rel if ix.now(p)]
    ub.append(dict(split=d['split'],relative_files_passing=len(mt),max_matches=max(mt) if mt else 0,with_10plus_matches=sum(m>=10 for m in mt),commits_found=f['commits_found'],commits_in_window=f['commits_in_window']))
raw_ft=json.load(open('data/first_table.json'))
out=dict(first_table=dict(raw=raw_ft['table'],corrected=dict(ft),corrected_by_split={k:dict(v) for k,v in by.items()},
   existence_check_catches_of_15=ft['existence_detectable_cited_item_missing'],
   commit_632=dict(hash='1a82e92',cat_file='commit',no_ref_contains_it=True,caveat='#632 stays UNEARNED as labelled; the label caveat in HANDOFF-sweep.md stands. The report was right about this commit.'),
   upper_bound=dict(rows=ub,jobs_resting_on_a_name_with_10plus_matches=sum(u['with_10plus_matches']>0 for u in ub),note='"Present" is an upper bound: a relative cite passes if any file in the index ends with that path, so a common name passes on an unrelated file. It also does not show the file came from this run.')),
 commit_misses_checked={k:v for k,v in commit_cache.items()},
 g1={f'{s}/{a}':dict(c) for (s,a),c in sorted(res.items())},remaining_miss_kinds={'/'.join(k):v for k,v in sorted(kinds.items())},
 notes=['Corrected G1 uses the frozen facts; frozen monitor scores and L2 facts are not re-run, so L2 still saw the raw numbers.','G2 was only called where raw G1 passed: items whose G1 flips under correction have no G2 score.','plant a keeps its renamed file: the rename is the plant.'])
json.dump(out,open('data/p3_corrections.json','w'),indent=1); json.dump(detail,open('private/p3_corrections_detail.json','w'),indent=1)
print(json.dumps(out['first_table'],indent=0)[:1800]); print(out['commit_misses_checked']); 
for k,v in out['g1'].items():
    if k.startswith('test'): print(k,v)
print(out['remaining_miss_kinds'])
