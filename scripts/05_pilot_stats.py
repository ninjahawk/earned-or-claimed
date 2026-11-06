#!/usr/bin/env python3
"""Pilot stats from private/monitor_runs.jsonl -> data/pilot_L1.json. AUROC with job-level bootstrap (few dev workflows, see QUESTION deviations)."""
import json,random,statistics as S
R=[json.loads(l) for l in open('private/monitor_runs.jsonl')]
L={str(json.loads(l)['id']):json.loads(l) for l in open('private/labels.jsonl')}
ok=[r for r in R if r.get('score') is not None]
def auc(p,n):
    return sum((a>b)+.5*(a==b) for a in p for b in n)/(len(p)*len(n))
def boot(p,n,B=2000,seed=20261106):
    g=random.Random(seed); v=sorted(auc(g.choices(p,k=len(p)),g.choices(n,k=len(n))) for _ in range(B)); return [round(v[int(.025*B)],3),round(v[int(.975*B)],3)]
arm={a:[r['score'] for r in ok if r['arm']==a] for a in('earned','planted_swap','self_reported_partial')}
out=dict(n_calls=len(R),n_scored=len(ok),arm_n={k:len(v) for k,v in arm.items()},arm_mean={k:round(S.mean(v),1) for k,v in arm.items() if v},arm_median={k:S.median(v) for k,v in arm.items() if v})
for a in('planted_swap','self_reported_partial'):
    out['auroc_'+a+'_vs_earned']=round(auc(arm[a],arm['earned']),3); out['ci95_'+a]=boot(arm[a],arm['earned'])
# control: report length as score over the same items
c=[r.get('cost') or 0 for r in R]; toks=[(r.get('usage') or {}) for r in R]
out['cost_usd_total']=round(sum(c),4); out['cost_usd_per_call_mean']=round(S.mean(c),5); out['secs_per_call_median']=S.median(r['secs'] for r in R)
out['input_tokens_per_call_mean']=round(S.mean(sum(t.get(k,0) for k in('input_tokens','cache_creation_input_tokens','cache_read_input_tokens')) for t in toks))
p=[d for d in L.values() if d['claim'] and d['label']!='UNKNOWN']
te=[d for d in p if d['split']=='test']; n_full=len(p); n_te=len(te)
cc=out['cost_usd_per_call_mean']
tr=json.load(open('data/transcript_counts.json'))
ttok=json.load(open('private/transcripts.json'))
# projection for the prereg's 3 runs per test item, plus planted copies at 3x test size as a ceiling
items=n_te+3*n_te
out['projection']=dict(test_items_natural=n_te,items_with_planted_ceiling=items,runs_per_item=3,
  L1_usd=round(items*3*cc,3),L2_usd_assume_2x_input=round(items*3*cc*2,3),
  L3_usd_assume_cap_30k_chars_about_7x_input=round(tr['test_earned_or_unearned_with_transcript']*4*3*cc*7,3))
json.dump(out,open('data/pilot_L1.json','w'),indent=1); print(json.dumps(out,indent=0))
