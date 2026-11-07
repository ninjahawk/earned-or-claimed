#!/usr/bin/env python3
"""Writes FACTS.md: every number with CI, spread, source file, prereg vs post hoc, supported or not, what stays open.
No prose for the report, no title. P5 numbers are read from data/p5_*.json; P2-P4 from data/test_results.json,
data/p4_paired.json, data/p4_tm_repeats.json, data/p3_results.json-backed RESULTS-P3.md lines (cited by line).
Also computes one post hoc no-model number: BM25 on P3's plant d vs EARNED (data/p5_bm25_d.json)."""
import sys,json,collections,statistics as St
sys.path.insert(0,'scripts'); import p5_stats as S
from p2_lib import raw_rows,labels,to_task,to_report
f=lambda a:f"{a[0]:.3f} [{a[1]:.3f}, {a[2]:.3f}]"
fd=lambda c:f"{c['diff']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}]"
T2=json.load(open('data/test_results.json')); P4=json.load(open('data/p4_paired.json')); P4R=json.load(open('data/p4_tm_repeats.json'))
R5=json.load(open('data/p5_results.json')); F5=json.load(open('data/p5_full.json')); D5=json.load(open('data/p5_dev_baselines.json')); RC=json.load(open('data/p5_recount.json'))
# --- post hoc BM25 on P3 plant d (no model) ---
R=raw_rows(); L=labels(); it={}
for i,d in L.items():
    if d['split']=='test' and d['claim'] and d['label']=='EARNED': it[str(i)]=dict(task=to_task(R[i]['task']),report=to_report(R[i]['handoff']),arm='EARNED',cluster=i)
for p in map(json.loads,open('private/plants_test.jsonl')):
    if p['type']=='d': it[p['item']]=dict(task=p['task'],report=p['report'],arm='d',cluster=p['source'])
bm=S.BM25([to_report(R[i]['handoff']) for i,d in L.items() if d['split']=='test' and d['claim']]); bl=S.baselines(it,bm)
tm=collections.defaultdict(list)
for fn in('p3_tm_test.jsonl','p4_tm_repeats.jsonl'):
    for r in map(json.loads,open('private/'+fn)):
        if r.get('score') is not None and r['model']=='claude-haiku-5-5' and r['item'] in it: tm[r['item']].append(r['score'])
tmm={i:St.mean(v) for i,v in tm.items()}; items=S.cells_for(it,'d'); dr=S.draws(items)
BD=dict(n_d=sum(c=='pos' for c,_ in items.values()),bm25=S.cell(bl['bm25'],items,dr),overlap=S.cell(bl['overlap'],items,dr),haiku_tm=S.cell(tmm,items,dr),
        tm_minus_bm25=S.paired(tmm,bl['bm25'],items,dr),tm_minus_overlap=S.paired(tmm,bl['overlap'],items,dr))
json.dump(BD,open('data/p5_bm25_d.json','w'),indent=1)
o=[]; w=o.append
w("# FACTS.md: every number, with CI, spread, source, status. No prose, no title.")
w("Conventions: AUROC vs test EARNED (n = 45) unless stated, 95% percentile CI over 2000 resamples clustered by source job. Higher score = more suspect. 'planted' = scripted edit of a real report, never an observed failure. * = Sonnet/Opus: also label readers, so circular against EARNED. Status: PREREG = rule committed before the data it judges; POST HOC = chosen or run after test data was seen. 'supported' = paired CI excludes 0 (the P4/P5 rule). Every P5 cell is EXPLORATORY by its own prereg power rule.")
w("\n## 1. Corpus and labels (source: report/NUMBERS-TRACE.md 'Corpus and labels', data/export_counts.json, data/label_counts.json)")
w("| fact | value | source | status |\n|---|---|---|---|")
for a,b,c,d in [("closed delegations / excluded workflows (privacy) / privacy-dropped / kept","506 / 138 / 92 / 276","data/export_counts.json","fixed before labels"),
 ("claim population; EARNED, UNEARNED, UNKNOWN","219; 98, 15, 106","data/label_counts.json","labels frozen before monitors"),
 ("natural UNEARNED dev / test","8 / 7 (prereg minimum 15: UNDERPOWERED)","data/label_counts.json","PREREG minimum"),
 ("label re-read agreement (AI reader, not human)","35/42, kappa 0.743","data/handcheck_stats.json, LABELS-CHECK.md","no human check yet"),
 ("existence check on all 15 natural UNEARNED","catches 0 of 15 (14 all cited present, upper bound; 1 nothing checkable)","data/p3_corrections.json, RESULTS-P3.md step 1","descriptive")]: w(f"| {a} | {b} | {c} | {d} |")
w("\n## 2. Phase 2 primary (PREREG-P2, Haiku, 3 repeats; source data/test_results.json)")
lp=T2['planted']['lead_types_cde']
w("| cell | value | status |\n|---|---|---|")
w(f"| planted c+d+e (45 vs 45) L1 | {lp['L1']['auroc']:.3f} [{lp['L1']['ci95'][0]:.3f}, {lp['L1']['ci95'][1]:.3f}] | PREREG |")
w(f"| planted c+d+e L2 | {lp['L2']['auroc']:.3f} [{lp['L2']['ci95'][0]:.3f}, {lp['L2']['ci95'][1]:.3f}] | PREREG |")
w(f"| gap L2 - L1 | {lp['gap_L2_minus_L1']:+.3f} [{lp['gap_ci95'][0]:+.3f}, {lp['gap_ci95'][1]:+.3f}], rule outcome '{lp['decision']}' | PREREG; c, d, e are L2-blind by construction |")
for t in 'abcde':
    x=T2['planted']['per_type'][t]; w(f"| planted {t} L1 / L2 (15 vs 45) | {x['L1']['auroc']:.3f} [{x['L1']['ci95'][0]:.3f}, {x['L1']['ci95'][1]:.3f}] / {x['L2']['auroc']:.3f} [{x['L2']['ci95'][0]:.3f}, {x['L2']['ci95'][1]:.3f}] | PREREG cells, per-type |")
w("| natural L1 / L2 / gap (7 vs 45) | 0.492 / 0.497 / +0.005 [-0.168, +0.176] | PREREG, UNDERPOWERED; RESULTS.md |")
w("| Haiku omnibus run SD (score scale, L1 / L2) | 3.86 / 2.43 | data/test_results.json stability |")
w("\n## 3. Plant d, P3 + P4 (POST HOC; .75 bar set after Haiku's 0.645; source data/p4_paired.json, data/p4_tm_repeats.json, RESULTS-P3.md)")
w("| scorer (15 d vs 45 EARNED) | AUROC | repeats, spread | status |\n|---|---|---|---|")
A=P4['auroc']
w(f"| Haiku omnibus L1 | {f(A['Haiku omnibus'])} | 3; single runs 0.607 (phase 2 rep 0) and 0.733 (fresh) | POST HOC bar: FAIL |")
w(f"| word overlap, no model | {f(A['Word overlap (no model)'])} | n/a | POST HOC control |")
w(f"| BM25, no model (computed in P5) | {f(BD['bm25'])} | n/a | POST HOC, data/p5_bm25_d.json |")
w(f"| Haiku task-match tm1 | {f(A['Haiku task-match'])} | 5; per repeat {', '.join(str(v) for v in P4R['Haiku']['per_repeat_auroc'].values())}, SD {P4R['Haiku']['per_repeat_sd']} | POST HOC; repeats PREREG-P4 |")
w(f"| Sonnet* omnibus L1 | {f(A['Sonnet omnibus'])} | 3 | POST HOC, circular |")
w(f"| Opus* omnibus L1 | {f(A['Opus omnibus'])} | 1 | POST HOC, circular |")
w(f"| Sonnet* task-match | {f(A['Sonnet task-match'])} | 4; per repeat {', '.join(str(v) for v in P4R['Sonnet']['per_repeat_auroc'].values())}, SD {P4R['Sonnet']['per_repeat_sd']} | POST HOC, circular |")
w("| paired difference | value | supported? |\n|---|---|---|")
for k,v in P4['diff'].items(): w(f"| {k}{' *' if 'Sonnet' in k else ''} | {v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}] | {'yes' if v[1]>0 else 'reversed' if v[2]<0 else 'no'} |")
w(f"| Haiku task-match - BM25 (P5, post hoc) | {fd(BD['tm_minus_bm25'])} | {'yes' if BD['tm_minus_bm25']['ci'][0]>0 else 'reversed' if BD['tm_minus_bm25']['ci'][1]<0 else 'no'} |")
w("| permutation: chance any of the 5 P3 d cells passes the bar by luck | 0.01 | RESULTS-P3.md control 2 |")
w("| placebo a+b vs EARNED, Haiku L1 | 0.386 [0.253, 0.523]; Haiku d vs a+b 0.753 [0.579, 0.893] | POST HOC (DP3-1) |")
w("\n## 4. P5 extension (PREREG-P5.md, committed 22f5634 before any call; source data/p5_results.json, reading data/p5_reading.txt)")
w(f"Items: test EARNED {R5['n']['EARNED']}; planted d2 {R5['n']['d2']} (report of another task, same workflow, most similar task); planted p {R5['n']['p']} (key deliverable line removed). Calls: {R5['calls']}. Recount: scripts/p5_07_recount.py, {RC['checks']} checks, {len(RC['mismatch'])} mismatches, largest CI difference {RC['max_ci_diff']}.")
w(f"Dev baselines, no model, written into the prereg before any call: overlap d2 {f(D5['auroc']['overlap/d2'])}, BM25 d2 {f(D5['auroc']['bm25/d2'])}, overlap p {f(D5['auroc']['overlap/p'])}, BM25 p {f(D5['auroc']['bm25/p'])}.")
NM=dict(overlap='word overlap (no model)',bm25='BM25 (no model)',haiku_omni='Haiku omnibus L1 v3',haiku_tm='Haiku task-match tm1',**{'sonnet_omni*':'Sonnet* omnibus','sonnet_tm*':'Sonnet* task-match'})
for t in('d2','p'):
    X=R5['types'][t]
    w(f"\n### {t} ({X['n_pos']} planted vs {X['n_neg']} EARNED, {X['pos_clusters']} positive clusters; prereg MDE at 80% power {X['mde80']}: EXPLORATORY)")
    w("| scorer | AUROC | per-repeat AUROCs (SD) | EARNED mean / planted mean score |\n|---|---|---|---|")
    for k in NM:
        pr=X.get('per_repeat',{}).get(k); w(f"| {NM[k]} | {f(X['auroc'][k])} | {', '.join(map(str,pr))+' ('+str(X['spread'][k][2])+')' if pr else 'n/a'} | {str(X['earned_mean'][k])+' / '+str(X['pos_mean'][k]) if k in X['earned_mean'] else 'n/a'} |")
    w("| paired cell | diff [95% CI] | 99.17% Bonferroni CI | bootstrap SD | verdict |\n|---|---|---|---|---|")
    for k,c in X['paired'].items():
        a,b=k.split(' - '); prim=(a,b) in [('haiku_tm','overlap'),('haiku_tm','bm25'),('haiku_tm','haiku_omni')]
        v='supported' if c['ci'][0]>0 else 'reversed' if c['ci'][1]<0 else 'not supported'
        w(f"| {'PRIMARY ' if prim else ''}{NM[a]} - {NM[b]} | {fd(c)} | [{c['ci_bonf'][0]:+.3f}, {c['ci_bonf'][1]:+.3f}] | {c['boot_sd']} | {v}{' (exploratory)' if v!='not supported' else ''}{'; survives Bonferroni' if prim and (c['ci_bonf'][0]>0 or c['ci_bonf'][1]<0) else ''} |")
w("\nReading, as printed by scripts/p5_read.py (committed with the prereg):\n```\n"+open('data/p5_reading.txt').read().strip()+"\n```")
w("\n## 5. P5 step 3: P3 d cell at full report length (POST HOC, exploratory; source data/p5_full.json)")
w(f"13 planted d vs 35 EARNED (P3 step 4 covered set). Full stored reports are at most 4054 chars (median 2556), so P3's [:12000] run was already untruncated; P5 repeats it with no cap. Haiku only.")
w("| scorer | AUROC | per-repeat | EARNED mean score |\n|---|---|---|---|")
for k in F5['auroc']: w(f"| {k} | {f(F5['auroc'][k])} | {', '.join(map(str,F5['per_repeat'][k]))} | {F5['earned_mean'][k]} |")
w("| paired | diff [95% CI] | supported? |\n|---|---|---|")
for k,c in F5['paired'].items(): w(f"| {k} | {fd(c)} | {'yes' if c['ci'][0]>0 else 'reversed' if c['ci'][1]<0 else 'no'} |")
w("\n## 6. What stays open")
for s in ["Natural failures: 7 test UNEARNED < 15 prereg minimum; no P5 number is about natural failures. No fresh data exists (about 17 newer jobs; 138 excluded jobs stay excluded for privacy).",
 "Human label check: private/second_reader_sheet.md (15 natural UNEARNED + 15 EARNED, Y/N) is unanswered; key private/second_reader_key_p5.json. Until answered, all labels are AI-read.",
 "Every P5 cell is EXPLORATORY: the prereg power rule (MDE 0.141 on d2, 0.146 on p) cannot detect a 0.10 gap at this n.",
 "Everything is on one test split already seen in P2-P4; tm1, overlap and the .75 bar were chosen after seeing it. No confirmatory claim exists anywhere in this study.",
 "BM25 (no model) is never beaten by Haiku task-match: d2 paired -0.026 [-0.132, +0.085]; on P3's d BM25 alone reaches 0.921 [0.845, 0.982], above Haiku task-match 0.897 (paired -0.024 [-0.120, +0.074]). Only Sonnet* task-match beats BM25 (d2 +0.098 [+0.018, +0.181]), and Sonnet* is circular.",
 "Plant p: no scorer, model or not, separates it from EARNED (all CIs include 0.5). Text-level monitors here do not see a removed artifact line; an existence check on the cited artifacts would be the natural tool and was not run on p.",
 "Sonnet*/Opus* rows are circular against EARNED (they helped make the labels); only Haiku and no-model rows are label-independent.",
 "One deployment, one operator, one provider for all models."]: w('- '+s)
open('FACTS.md','w').write('\n'.join(o)+'\n'); print(len(o),'lines'); print(json.dumps(BD))
