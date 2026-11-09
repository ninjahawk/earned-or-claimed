#!/usr/bin/env python3
"""Scrub assertions over ALL exported rows and hand-check agreement -> data/scrub_check.json, data/handcheck_stats.json."""
import json,re,collections
J=[json.loads(l) for l in open('private/export.jsonl')]
P={'email':r'[\w.+-]+@[\w-]+\.\w+','handle':r'(?<!\w)@[A-Za-z_][\w.]{2,}','owner':r'(?i)\bnathan\b|\blangley\b|USER','win_path':r'[A-Za-z]:\\','desktop_path':r'(?i)desktop[\\/]','mnt_path':r'/mnt/(pc|host)|/home/\w+|ORCH_ROOT','channel':r'(?i)REDACTED_CHANNEL','store':r'(?i)REDACTED_STORE','url':r'https?://','ip':r'\b\d{1,3}(\.\d{1,3}){3}\b','excluded_terms':r'(?i)\b(REDACTED_TOPIC)\b','finance':r'(?i)\$\s?\d|\b(stripe|paypal|payout|revenue|invoice|salary)\b','host_run_path':r'(?i)orchestrator[\\/]host[\\/]'}
txt=[(j['id'],j['task']+' '+j['handoff']) for j in J]
res={k:sum(1 for _,t in txt if re.search(v,t)) for k,v in P.items()}
sample=open('private/scrub-test.txt').read()
res={'rows_all':len(txt),'hits_all_rows':res,'hits_50_row_sample':{k:len(re.findall(v,sample)) for k,v in P.items()}}
json.dump(res,open('data/scrub_check.json','w'),indent=1); print(res)
v=json.load(open('data/handcheck_v2.json'))
L={str(json.loads(l)['id']):json.loads(l) for l in open('private/labels.jsonl')}
def now(d): return 'NOCLAIM' if not d['claim'] else d['label']
cats=['EARNED','UNKNOWN','NOCLAIM','CLAIM','UNCLEAR']
draw=collections.Counter(); after=collections.Counter()
for i,x in v.items():
    draw[(x['rule'],x['hand'])]+=1
    n=now(L[i]); h=x['hand']
    ok= (n==h) or (h=='CLAIM' and n!='NOCLAIM')
    after['agree' if ok else 'disagree']+=1
agree_draw=sum(c for (r,h),c in draw.items() if r==h)
n=sum(draw.values())
strata={r:dict(n=sum(c for (a,h),c in draw.items() if a==r),agree=sum(c for (a,h),c in draw.items() if a==r and h==r)) for r in('EARNED','UNKNOWN','NOCLAIM')}
# Cohen's kappa on rule at draw vs hand, treating CLAIM/UNCLEAR as distinct categories
pa=agree_draw/n; rm=collections.Counter(); hm=collections.Counter()
for (r,h),c in draw.items(): rm[r]+=c; hm[h]+=c
pe=sum(rm[k]*hm[k] for k in rm)/n**2
out=dict(n=n,reader='Claude Opus 5.5, the same agent that wrote the rule; NOT an independent human',agree_at_draw=agree_draw,pct=round(100*pa,1),kappa=round((pa-pe)/(1-pe),3),strata=strata,after_fixes=dict(after),confusion={f'{r}->{h}':c for (r,h),c in draw.items()})
json.dump(out,open('data/handcheck_stats.json','w'),indent=1); print(out)
