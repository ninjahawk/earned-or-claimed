# FACTS.md: every number, with CI, spread, source, status. No prose, no title.
Conventions: AUROC vs test EARNED (n = 45) unless stated, 95% percentile CI over 2000 resamples clustered by source job. Higher score = more suspect. 'planted' = scripted edit of a real report, never an observed failure. * = Sonnet/Opus: also label readers, so circular against EARNED. Status: PREREG = rule committed before the data it judges; POST HOC = chosen or run after test data was seen. 'supported' = paired CI excludes 0 (the P4/P5 rule). Every P5 cell is EXPLORATORY by its own prereg power rule.

## 1. Corpus and labels (source: report/NUMBERS-TRACE.md 'Corpus and labels', data/export_counts.json, data/label_counts.json)
| fact | value | source | status |
|---|---|---|---|
| closed delegations / excluded workflows (privacy) / privacy-dropped / kept | 506 / 138 / 92 / 276 | data/export_counts.json | fixed before labels |
| claim population; EARNED, UNEARNED, UNKNOWN | 219; 98, 15, 106 | data/label_counts.json | labels frozen before monitors |
| natural UNEARNED dev / test | 8 / 7 (prereg minimum 15: UNDERPOWERED) | data/label_counts.json | PREREG minimum |
| label re-read agreement (AI reader, not human) | 35/42, kappa 0.743 | data/handcheck_stats.json, LABELS-CHECK.md | no human check yet |
| existence check on all 15 natural UNEARNED | catches 0 of 15 (14 all cited present, upper bound; 1 nothing checkable) | data/p3_corrections.json, RESULTS-P3.md step 1 | descriptive |

## 2. Phase 2 primary (PREREG-P2, Haiku, 3 repeats; source data/test_results.json)
| cell | value | status |
|---|---|---|
| planted c+d+e (45 vs 45) L1 | 0.517 [0.402, 0.623] | PREREG |
| planted c+d+e L2 | 0.538 [0.433, 0.649] | PREREG |
| gap L2 - L1 | +0.022 [-0.080, +0.141], rule outcome 'inconclusive' | PREREG; c, d, e are L2-blind by construction |
| planted a L1 / L2 (15 vs 45) | 0.387 [0.220, 0.553] / 0.802 [0.691, 0.900] | PREREG cells, per-type |
| planted b L1 / L2 (15 vs 45) | 0.384 [0.217, 0.548] / 0.467 [0.295, 0.635] | PREREG cells, per-type |
| planted c L1 / L2 (15 vs 45) | 0.407 [0.242, 0.578] / 0.553 [0.382, 0.715] | PREREG cells, per-type |
| planted d L1 / L2 (15 vs 45) | 0.645 [0.485, 0.785] / 0.560 [0.423, 0.698] | PREREG cells, per-type |
| planted e L1 / L2 (15 vs 45) | 0.497 [0.324, 0.668] / 0.501 [0.337, 0.675] | PREREG cells, per-type |
| natural L1 / L2 / gap (7 vs 45) | 0.492 / 0.497 / +0.005 [-0.168, +0.176] | PREREG, UNDERPOWERED; RESULTS.md |
| Haiku omnibus run SD (score scale, L1 / L2) | 3.86 / 2.43 | data/test_results.json stability |

## 3. Plant d, P3 + P4 (POST HOC; .75 bar set after Haiku's 0.645; source data/p4_paired.json, data/p4_tm_repeats.json, RESULTS-P3.md)
| scorer (15 d vs 45 EARNED) | AUROC | repeats, spread | status |
|---|---|---|---|
| Haiku omnibus L1 | 0.645 [0.485, 0.785] | 3; single runs 0.607 (phase 2 rep 0) and 0.733 (fresh) | POST HOC bar: FAIL |
| word overlap, no model | 0.842 [0.723, 0.943] | n/a | POST HOC control |
| BM25, no model (computed in P5) | 0.921 [0.845, 0.982] | n/a | POST HOC, data/p5_bm25_d.json |
| Haiku task-match tm1 | 0.897 [0.807, 0.973] | 5; per repeat 0.842, 0.794, 0.867, 0.861, 0.907, SD 0.041 | POST HOC; repeats PREREG-P4 |
| Sonnet* omnibus L1 | 0.889 [0.774, 0.972] | 3 | POST HOC, circular |
| Opus* omnibus L1 | 0.936 [0.824, 0.999] | 1 | POST HOC, circular |
| Sonnet* task-match | 0.950 [0.881, 0.997] | 4; per repeat 0.944, 0.956, 0.94, 0.947, SD 0.007 | POST HOC, circular |
| paired difference | value | supported? |
|---|---|---|
| Haiku task-match - Haiku omnibus | +0.252 [+0.141, +0.378] | yes |
| Haiku task-match - Word overlap (no model) | +0.055 [-0.080, +0.199] | no |
| Sonnet task-match - Word overlap (no model) * | +0.107 [+0.000, +0.232] | no |
| Word overlap (no model) - Haiku omnibus | +0.197 [+0.013, +0.387] | yes |
| Sonnet omnibus - Haiku omnibus * | +0.244 [+0.134, +0.357] | yes |
| Sonnet task-match - Sonnet omnibus * | +0.061 [-0.006, +0.150] | no |
| Haiku task-match - BM25 (P5, post hoc) | -0.024 [-0.120, +0.074] | no |
| permutation: chance any of the 5 P3 d cells passes the bar by luck | 0.01 | RESULTS-P3.md control 2 |
| placebo a+b vs EARNED, Haiku L1 | 0.386 [0.253, 0.523]; Haiku d vs a+b 0.753 [0.579, 0.893] | POST HOC (DP3-1) |

## 4. P5 extension (PREREG-P5.md, committed 22f5634 before any call; source data/p5_results.json, reading data/p5_reading.txt)
Items: test EARNED 45; planted d2 45 (report of another task, same workflow, most similar task); planted p 28 (key deliverable line removed). Calls: {'haiku_omni': 590, 'haiku_tm': 590, 'sonnet_omni*': 236, 'sonnet_tm*': 236}. Recount: scripts/p5_07_recount.py, 28 checks, 0 mismatches, largest CI difference 0.009.
Dev baselines, no model, written into the prereg before any call: overlap d2 0.678 [0.592, 0.766], BM25 d2 0.780 [0.702, 0.860], overlap p 0.496 [0.445, 0.544], BM25 p 0.521 [0.486, 0.564].

### d2 (45 planted vs 45 EARNED, 30 positive clusters; prereg MDE at 80% power 0.141: EXPLORATORY)
| scorer | AUROC | per-repeat AUROCs (SD) | EARNED mean / planted mean score |
|---|---|---|---|
| word overlap (no model) | 0.644 [0.547, 0.741] | n/a | n/a |
| BM25 (no model) | 0.801 [0.712, 0.882] | n/a | n/a |
| Haiku omnibus L1 v3 | 0.594 [0.506, 0.693] | 0.602, 0.565, 0.542, 0.592, 0.6 (0.023) | 47.83 / 52.55 |
| Haiku task-match tm1 | 0.775 [0.693, 0.860] | 0.702, 0.762, 0.756, 0.758, 0.738 (0.022) | 11.73 / 32.55 |
| Sonnet* omnibus | 0.865 [0.797, 0.933] | 0.858, 0.855 (0.001) | 40.47 / 68.28 |
| Sonnet* task-match | 0.899 [0.835, 0.952] | 0.894, 0.908 (0.007) | 7.22 / 42.12 |
| paired cell | diff [95% CI] | 99.17% Bonferroni CI | bootstrap SD | verdict |
|---|---|---|---|---|
| PRIMARY Haiku task-match tm1 - word overlap (no model) | +0.132 [+0.028, +0.245] | [-0.016, +0.279] | 0.0538 | supported (exploratory) |
| PRIMARY Haiku task-match tm1 - BM25 (no model) | -0.026 [-0.132, +0.085] | [-0.170, +0.130] | 0.056 | not supported |
| PRIMARY Haiku task-match tm1 - Haiku omnibus L1 v3 | +0.182 [+0.083, +0.274] | [+0.050, +0.305] | 0.049 | supported (exploratory); survives Bonferroni |
| Haiku omnibus L1 v3 - word overlap (no model) | -0.050 [-0.173, +0.086] | [-0.214, +0.151] | 0.066 | not supported |
| Haiku omnibus L1 v3 - BM25 (no model) | -0.208 [-0.343, -0.061] | [-0.378, -0.008] | 0.07 | reversed (exploratory) |
| Sonnet* task-match - word overlap (no model) | +0.255 [+0.156, +0.351] | [+0.116, +0.382] | 0.0498 | supported (exploratory) |
| Sonnet* task-match - BM25 (no model) | +0.098 [+0.018, +0.181] | [-0.016, +0.223] | 0.0421 | supported (exploratory) |
| Sonnet* task-match - Sonnet* omnibus | +0.034 [-0.023, +0.092] | [-0.040, +0.109] | 0.0295 | not supported |

### p (28 planted vs 45 EARNED, 28 positive clusters; prereg MDE at 80% power 0.146: EXPLORATORY)
| scorer | AUROC | per-repeat AUROCs (SD) | EARNED mean / planted mean score |
|---|---|---|---|
| word overlap (no model) | 0.514 [0.435, 0.591] | n/a | n/a |
| BM25 (no model) | 0.544 [0.467, 0.619] | n/a | n/a |
| Haiku omnibus L1 v3 | 0.541 [0.451, 0.629] | 0.553, 0.516, 0.548, 0.524, 0.541 (0.014) | 47.83 / 49.9 |
| Haiku task-match tm1 | 0.551 [0.441, 0.661] | 0.5, 0.498, 0.576, 0.568, 0.515 (0.034) | 11.73 / 13.04 |
| Sonnet* omnibus | 0.527 [0.431, 0.624] | 0.542, 0.513 (0.014) | 40.47 / 42.77 |
| Sonnet* task-match | 0.534 [0.457, 0.617] | 0.528, 0.548 (0.01) | 7.22 / 10.38 |
| paired cell | diff [95% CI] | 99.17% Bonferroni CI | bootstrap SD | verdict |
|---|---|---|---|---|
| PRIMARY Haiku task-match tm1 - word overlap (no model) | +0.037 [-0.106, +0.187] | [-0.141, +0.222] | 0.0722 | not supported |
| PRIMARY Haiku task-match tm1 - BM25 (no model) | +0.007 [-0.119, +0.139] | [-0.168, +0.189] | 0.0672 | not supported |
| PRIMARY Haiku task-match tm1 - Haiku omnibus L1 v3 | +0.010 [-0.122, +0.148] | [-0.169, +0.198] | 0.0678 | not supported |
| Haiku omnibus L1 v3 - word overlap (no model) | +0.027 [-0.088, +0.149] | [-0.139, +0.190] | 0.0621 | not supported |
| Haiku omnibus L1 v3 - BM25 (no model) | -0.003 [-0.122, +0.120] | [-0.171, +0.159] | 0.0609 | not supported |
| Sonnet* task-match - word overlap (no model) | +0.020 [-0.066, +0.108] | [-0.102, +0.140] | 0.0446 | not supported |
| Sonnet* task-match - BM25 (no model) | -0.010 [-0.086, +0.072] | [-0.124, +0.103] | 0.0415 | not supported |
| Sonnet* task-match - Sonnet* omnibus | +0.008 [-0.088, +0.106] | [-0.123, +0.140] | 0.0499 | not supported |

Reading, as printed by scripts/p5_read.py (committed with the prereg):
```
== d2: planted d2 (report of another task, same workflow). vs test EARNED. EXPLORATORY: smallest detectable gap at 80 pct power is 0.141 > 0.10.
  word overlap (no model): AUROC 0.644 [0.547, 0.741] NEAR
  BM25 (no model): AUROC 0.801 [0.712, 0.882] PASS
  Haiku omnibus: AUROC 0.594 [0.506, 0.693] NEAR; per-repeat 0.542-0.602, SD 0.023
  Haiku task-match: AUROC 0.775 [0.693, 0.860] PASS; per-repeat 0.702-0.762, SD 0.022
  Sonnet* omnibus: AUROC 0.865 [0.797, 0.933] PASS; per-repeat 0.855-0.858, SD 0.001
  Sonnet* task-match: AUROC 0.899 [0.835, 0.952] PASS; per-repeat 0.894-0.908, SD 0.007
  No-model baselines blind (CI lower bound <= 0.5): neither.
  PRIMARY Haiku task-match - word overlap (no model): +0.132 [+0.028, +0.245] -> supported (exploratory); does not survive 6-cell Bonferroni
  PRIMARY Haiku task-match - BM25 (no model): -0.026 [-0.132, +0.085] -> not supported; does not survive 6-cell Bonferroni
  PRIMARY Haiku task-match - Haiku omnibus: +0.182 [+0.083, +0.274] -> supported (exploratory); survives 6-cell Bonferroni
  secondary Haiku omnibus - word overlap (no model): -0.050 [-0.173, +0.086] -> not supported
  secondary Haiku omnibus - BM25 (no model): -0.208 [-0.343, -0.061] -> reversed (exploratory)
  secondary Sonnet* task-match - word overlap (no model): +0.255 [+0.156, +0.351] -> supported (exploratory)
  secondary Sonnet* task-match - BM25 (no model): +0.098 [+0.018, +0.181] -> supported (exploratory)
  secondary Sonnet* task-match - Sonnet* omnibus: +0.034 [-0.023, +0.092] -> not supported
  ANSWER: Haiku task-match works here and beats word overlap (no model) only; it is not shown to beat the other baseline. Exploratory (underpowered by the prereg rule).
== p: planted p (key deliverable line removed). vs test EARNED. EXPLORATORY: smallest detectable gap at 80 pct power is 0.146 > 0.10.
  word overlap (no model): AUROC 0.514 [0.435, 0.591] FAIL
  BM25 (no model): AUROC 0.544 [0.467, 0.619] FAIL
  Haiku omnibus: AUROC 0.541 [0.451, 0.629] FAIL; per-repeat 0.516-0.553, SD 0.014
  Haiku task-match: AUROC 0.551 [0.441, 0.661] FAIL; per-repeat 0.498-0.576, SD 0.034
  Sonnet* omnibus: AUROC 0.527 [0.431, 0.624] FAIL; per-repeat 0.513-0.542, SD 0.014
  Sonnet* task-match: AUROC 0.534 [0.457, 0.617] FAIL; per-repeat 0.528-0.548, SD 0.010
  No-model baselines blind (CI lower bound <= 0.5): word overlap (no model), BM25 (no model).
  PRIMARY Haiku task-match - word overlap (no model): +0.037 [-0.106, +0.187] -> not supported; does not survive 6-cell Bonferroni
  PRIMARY Haiku task-match - BM25 (no model): +0.007 [-0.119, +0.139] -> not supported; does not survive 6-cell Bonferroni
  PRIMARY Haiku task-match - Haiku omnibus: +0.010 [-0.122, +0.148] -> not supported; does not survive 6-cell Bonferroni
  secondary Haiku omnibus - word overlap (no model): +0.027 [-0.088, +0.149] -> not supported
  secondary Haiku omnibus - BM25 (no model): -0.003 [-0.122, +0.120] -> not supported
  secondary Sonnet* task-match - word overlap (no model): +0.020 [-0.066, +0.108] -> not supported
  secondary Sonnet* task-match - BM25 (no model): -0.010 [-0.086, +0.072] -> not supported
  secondary Sonnet* task-match - Sonnet* omnibus: +0.008 [-0.088, +0.106] -> not supported
  ANSWER: Haiku task-match does not clear the bar here and is not shown to beat either baseline. Where the baseline is blind, the narrow monitor is blind too on this plant. Exploratory (underpowered by the prereg rule).
Always: planted items only; post hoc in design history (tm1, overlap and the .75 bar were chosen after seeing test data); Sonnet* helped make the EARNED labels, so its rows are not independent; no natural-failure claim; no confirmatory claim.
```

## 5. P5 step 3: P3 d cell at full report length (POST HOC, exploratory; source data/p5_full.json)
13 planted d vs 35 EARNED (P3 step 4 covered set). Full stored reports are at most 4054 chars (median 2556), so P3's [:12000] run was already untruncated; P5 repeats it with no cap. Haiku only.
| scorer | AUROC | per-repeat | EARNED mean score |
|---|---|---|---|
| omni_2000 (phase 2, 3 reps) | 0.615 [0.429, 0.776] | 0.609, 0.604, 0.603 | 47.79 |
| omni_full (P3 [:12000], 3 reps) | 0.738 [0.565, 0.883] | 0.681, 0.768, 0.722 | 33.02 |
| omni_full (P5 no cap, 3 reps) | 0.680 [0.499, 0.851] | 0.657, 0.652, 0.696 | 34.04 |
| tm_2000 (P3+P4, 5 reps) | 0.893 [0.797, 0.975] | 0.833, 0.777, 0.858, 0.859, 0.893 | 9.62 |
| tm_full (P5 no cap, 3 reps) | 0.927 [0.779, 1.000] | 0.931, 0.815, 0.905 | 5.09 |
| paired | diff [95% CI] | supported? |
|---|---|---|
| omni_full (P5 no cap, 3 reps) - omni_2000 (phase 2, 3 reps) | +0.065 [-0.087, +0.232] | no |
| tm_full (P5 no cap, 3 reps) - tm_2000 (P3+P4, 5 reps) | +0.034 [-0.153, +0.181] | no |
| tm_full (P5 no cap, 3 reps) - omni_full (P5 no cap, 3 reps) | +0.247 [+0.016, +0.469] | yes |
| tm_2000 (P3+P4, 5 reps) - omni_2000 (phase 2, 3 reps) | +0.278 [+0.145, +0.438] | yes |
| omni_full (P5 no cap, 3 reps) - omni_full (P3 [:12000], 3 reps) | -0.058 [-0.165, +0.072] | no |

## 6. What stays open
- Natural failures: 7 test UNEARNED < 15 prereg minimum; no P5 number is about natural failures. No fresh data exists (about 17 newer jobs; 138 excluded jobs stay excluded for privacy).
- Human label check: private/second_reader_sheet.md (15 natural UNEARNED + 15 EARNED, Y/N) is unanswered; key private/second_reader_key_p5.json. Until answered, all labels are AI-read.
- Every P5 cell is EXPLORATORY: the prereg power rule (MDE 0.141 on d2, 0.146 on p) cannot detect a 0.10 gap at this n.
- Everything is on one test split already seen in P2-P4; tm1, overlap and the .75 bar were chosen after seeing it. No confirmatory claim exists anywhere in this study.
- BM25 (no model) is never beaten by Haiku task-match: d2 paired -0.026 [-0.132, +0.085]; on P3's d BM25 alone reaches 0.921 [0.845, 0.982], above Haiku task-match 0.897 (paired -0.024 [-0.120, +0.074]). Only Sonnet* task-match beats BM25 (d2 +0.098 [+0.018, +0.181]), and Sonnet* is circular.
- Plant p: no scorer, model or not, separates it from EARNED (all CIs include 0.5). Text-level monitors here do not see a removed artifact line; an existence check on the cited artifacts would be the natural tool and was not run on p.
- Sonnet*/Opus* rows are circular against EARNED (they helped make the labels); only Haiku and no-model rows are label-independent.
- One deployment, one operator, one provider for all models.
