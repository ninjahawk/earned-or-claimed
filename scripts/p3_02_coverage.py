#!/usr/bin/env python3
"""Phase 3 step 4, first part. No model calls. Full-report and transcript coverage on the current 219 claim labels. Read-only on VM and PC.
A job counts as covered only if the stored report is found inside the longer text and at its end. Writes private/full_reports.jsonl (text) and data/p3_coverage.json (counts)."""
import sys,json,re,subprocess,collections,statistics as S
sys.path.insert(0,'scripts'); from p2_lib import *
L=labels(); R=raw_rows(); ids=[i for i,d in L.items() if d['claim']]
W={str(i):(R[i]['handoff'] or '') for i in ids}
src=open('scripts/p3_02_scan.py').read()
def run(roots,remote):
    code=src.replace('WANTED',repr(json.dumps(W))).replace('ROOTSLIST',repr(roots))
    cmd=['ssh','pc','python','-'] if remote else ['python3','-']
    o=subprocess.run(cmd,input=code.encode(),capture_output=True,timeout=570)
    if o.returncode: print(o.stderr[-800:],file=sys.stderr)
    return json.loads(o.stdout.decode('utf8','replace'))
vm=run([['HOME/.claude/projects','**/*.jsonl','transcript'],['ORCH_ROOT/claude-projects','**/*.jsonl','transcript'],['ORCH_ROOT/work','*/HANDOFF*.md','note'],['ORCH_ROOT/vmwork','*/HANDOFF*.md','note'],['ORCH_ROOT/state/hostwork','*','note']],False)
pc=run([['PC_HOME/.claude/projects','**/*.jsonl','transcript'],['PC_HOME/ORCH_HOST_DIR/runs','*.handoff.md','note'],['PC_HOME/ORCH_HOST_DIR/runs','*.json','note']],True)
print('scanned',vm['seen'],pc['seen'],file=sys.stderr)
best={};tr={}
for side in(vm,pc):
    for i,hs in side['hits'].items():
        for h in hs:
            if h['kind']=='transcript': tr.setdefault(i,h['path'])
            if i not in best or h['kind']=='transcript' and best[i]['kind']!='transcript' or (h['kind']==best[i]['kind'] and h['bytes']>best[i]['bytes']): best[i]=h
with open('private/full_reports.jsonl','w') as w:
    for i,h in best.items(): w.write(json.dumps(dict(id=int(i),kind=h['kind'],path=h['path'],full=h['full'],stored=len(W[i])))+'\n')
old={k:v for k,v in json.load(open('private/transcripts.json')).items()}
rows=collections.defaultdict(collections.Counter); stats=[]
for i in ids:
    d=L[i]; k=f"{d['split']}/{d['label']}"; s=str(i); c=rows[k]; c['n']+=1
    longer=s in best and len(best[s]['full'])>len(W[s])+20
    c['stored_cut_ge_1500']+=len(W[s])>=1500; c['full_found']+=(s in best); c['full_longer_than_stored']+=longer
    c['transcript_verified']+=(s in tr); c['transcript_old_map']+=(s in old); c['transcript_any']+=(s in tr or s in old)
    c['plan_vm']+=(d['plan']=='vm')
    stats.append(dict(i=i,k=k,cov=longer,wf=d['workflow'],plan=d['plan'],ln=len(W[s])))
te=[x for x in stats if x['k'].startswith('test/') and not x['k'].endswith('UNKNOWN')]
diff={}
for name,sub in(('covered',[x for x in stats if x['cov']]),('not_covered',[x for x in stats if not x['cov']])):
    diff[name]=dict(n=len(sub),plan=dict(collections.Counter(x['plan'] for x in sub)),workflow=dict(collections.Counter(x['wf'] for x in sub).most_common()),label=dict(collections.Counter(x['k'].split('/')[1] for x in sub)),stored_chars_median=S.median(x['ln'] for x in sub) if sub else None)
out=dict(per_label_split={k:dict(v) for k,v in sorted(rows.items())},how_covered_differs=diff,kinds=dict(collections.Counter(h['kind'] for h in best.values())),scanned=dict(vm=vm['seen'],pc=pc['seen']),
 note='full_found = stored report found at the end of a longer or equal text. Only full_longer_than_stored items can differ between truncated and full. transcript_verified = final assistant text ends in the stored report; transcript_old_map = private/transcripts.json, built before D10.')
json.dump(out,open('data/p3_coverage.json','w'),indent=1)
print(json.dumps(out,indent=0)[:3500])
