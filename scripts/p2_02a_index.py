#!/usr/bin/env python3
"""Read-only evidence index. git log --all on each PC repo via ssh and VM repos locally. Sensitive project trees are left out. Writes private/idx/*."""
import subprocess,re,json,os,glob,concurrent.futures as F
import os,sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from private_terms import *
SENS=re.compile(PRIVATE_TOPICS,re.I)
FMT='C%x09%H%x09%ct'
pc=[l.strip() for l in open('private/idx/pc_repos.txt') if l.strip() and not SENS.search(l)]
def dump(r):
    host,p=r
    cmd=['git','-c','safe.directory=*','-C',p,'log','--all',f'--format={FMT}','--name-only','--no-renames']
    try:
        if host=='pc':
            q=' '.join(f'"{x}"' if ' ' in x or '%' in x or '*' in x else x for x in cmd)
            o=subprocess.run(['ssh','pc',q],capture_output=True,text=True,timeout=280,errors='replace')
        else: o=subprocess.run(cmd,capture_output=True,text=True,timeout=280,errors='replace')
    except Exception as e: return r,None,str(e)[:80]
    return r,o.stdout,o.stderr[:80]
vm=['ORCH_ROOT/repo']+[os.path.dirname(g) for g in glob.glob('ORCH_ROOT/work/*/.git') if not SENS.search(g) and 'apart-swarm' not in g]
C={} # sha -> [repo,ct,[files]]
stat=[]
with F.ThreadPoolExecutor(6) as ex:
    for r,o,e in ex.map(dump,[('pc',p) for p in pc]+[('vm',p) for p in vm]):
        n=0
        if o:
            cur=None
            for l in o.splitlines():
                if l.startswith('C\t'):
                    _,h,t=l.split('\t'); cur=h; n+=1
                    if h not in C: C[h]=[r[0]+':'+r[1],int(t),[]]
                elif l.strip() and cur: C[cur][2].append(l.strip())
        stat.append(dict(repo=r[1],host=r[0],commits=n,err=e if not n else ''))
json.dump(C,open('private/idx/commits.json','w'))
json.dump(stat,open('private/idx/repo_stats.json','w'),indent=0)
print(len(C),'commits',len(stat),'repos',sum(1 for s in stat if not s['commits']),'empty/failed')
files=set()
for l in open('private/idx/pc_files_raw.txt',errors='replace'):
    if SENS.search(l): continue
    files.add(l.strip().replace('\\','/').lower())
for root in ['ORCH_ROOT/repo']+vm[1:]:
    for d,ds,fs in os.walk(root):
        ds[:]=[x for x in ds if x not in('.git','node_modules','__pycache__','venv')]
        for f in fs: files.add(os.path.join(d,f).lower())
json.dump(sorted(files),open('private/idx/files.json','w'))
print(len(files),'files')
