# NUMBERS-TRACE.md: every number in REPORT.pdf -> where it comes from
All paths are relative to the study repo root. "R2" = RESULTS.md (built by scripts/p2_11_results.py from data/test_results.json etc.). "R3" = RESULTS-P3.md (built by scripts/p3_12_results.py from data/p3_results.json). Every planted number is planted. Every natural test number is UNDERPOWERED (7 < 15). * = Sonnet/Opus: label readers, so circular against EARNED (R3:16, notes/jobs.md "AT P3 HANDOFF"). This caveat is carried in the report beside each one (Table 1 column and footnote, Fig. 1 caption, §4.4 "Sonnet*", App. C "Sonnet*", abstract "they also helped produce the labels").

## Corpus and labels
| Number in report | Source |
|---|---|
| 506 closed, 138 excluded workflows, 92 privacy, 276 kept | data/export_counts.json (all_closed, excluded_workflow, dropped_privacy, kept); scripts/01_export.py |
| 15 workflows | data/label_counts.json all_workflows (15 keys) |
| 219 claim population; EARNED 98, UNEARNED 15, UNKNOWN 106; dev 8 / test 7 | data/label_counts.json population_claim, claim_by_label, claim_by_split_label; scripts/03_labels.py; HANDOFF-sweep.md count table |
| UNEARNED 2 -> 15 by sweep | HANDOFF-sweep.md count table; data/sweep_counts.json |
| 45 test EARNED | data/label_counts.json claim_by_split_label test/EARNED |
| 4 workflows hold the 7 test UNEARNED | R2:41 ("7 UNEARNED in 4 workflows") |
| 42-item re-read, 35 agree, kappa 0.743 | data/handcheck_stats.json; LABELS-CHECK.md |
| At least 2 cited jobs later contradicted | LABELS-CHECK.md "Label noise" |
| 7 rest on AI judge verdicts only; 7 one fix chain (dev); 2 not defended; 13-15 in substance; sweep landed on 15; cap 16.2 vs 7.7 lines/job | ORCH_ROOT/repo/notes/jobs.md:31 (REPORT MUST SAY); HANDOFF-sweep.md |
| Dates 24 Oct - 6 Nov 2026 | QUESTION.md "Unit and population" |
| 2000-character report cap | QUESTION.md D7 |
| Seed 20261106; 3 of 7 workflows >=10 jobs held out (40%); time holdout 3 Nov | QUESTION.md "Split"; data/label_counts.json held_out_workflows + all_workflows counts >=10: forge, hoi, jspace, robot30, store, youtube, ytreal = 7 |
| 12,000-char transcript excerpt (L3) | scripts/p3_lib.py transcript_excerpt cap=12000; R3:155 |
| 15 plants per type on test | data/plants_test_counts.json; scripts/p2_03_plants.py N=15 |
| Preexisting/sprint dates: first study commit 2026-11-06 16:56 -0500 | `git log --reverse` first commit 3d7ec82 |

## Section 4.1, Table 1, Figure 1 (plant d vs EARNED, planted, post hoc)
| Number | Source |
|---|---|
| Haiku omnibus 0.645 [0.485, 0.785] | data/p4_paired.json auroc "Haiku omnibus"; = R3:28; scripts/p4_paired.py |
| Word overlap 0.842 [0.723, 0.943] | data/p4_paired.json; = R3:91 |
| Haiku task-match 0.897 [0.807, 0.973], 5 repeats | data/p4_paired.json "Haiku task-match" (CI from this script's bootstrap; data/p4_tm_repeats.json gives the same 0.897 with [0.803, 0.971] from a second bootstrap) |
| Sonnet omnibus* 0.889 [0.774, 0.972] | data/p4_paired.json; = R3:32 |
| Opus omnibus* 0.936 [0.824, 0.999], 1 repeat | data/p4_paired.json; = R3:34 |
| Sonnet task-match* 0.950 [0.881, 0.997], 4 repeats | data/p4_paired.json; data/p4_tm_repeats.json mean_all 0.950 |
| Paired +0.252 [+0.141, +0.378]; +0.197 [+0.013, +0.387]; +0.055 [-0.080, +0.199]; +0.107 [+0.000, +0.232]* | data/p4_paired.json diff |
| Per-repeat Haiku TM 0.842, 0.794, 0.867, 0.861, 0.907, SD 0.041; Sonnet 0.944, 0.956, 0.940, 0.947, SD 0.007 | data/p4_tm_repeats.json per_repeat_auroc, per_repeat_sd; scripts/p4_tm_stats.py |
| Phase-3 3-repeat Haiku TM 0.864 (replaced) | data/p4_tm_repeats.json mean_old3; = R3:36 |
| Haiku omnibus one run 0.733 vs 0.607 | R3:93 (fresh run) and R3:30 |
| Bar .75 set after 0.645 | R3:11, R3:167 |
| Permutation: 2000 permutations, chance any of 5 cells passes 0.01 | R3:89 |
| Placebo a+b vs EARNED Haiku 0.386 [0.253, 0.523]; Haiku d vs a+b 0.753 [0.579, 0.893] | R3:96 |
| Phase 4: 180 calls | private/p4_tm_repeats.jsonl (60 items x 3); scripts/p4_tm_repeats.py output "ran 180" |
| Pre-commitment of repeat reporting | PREREG-P4-repeats.md, commit f2b2b66 (before any call) |

## Section 4.2, Figure 2, Table C1 (Haiku phase 2, preregistered)
| Number | Source |
|---|---|
| c+d+e L1 0.517 [0.402, 0.623], L2 0.538 [0.433, 0.649], gap +0.022 [-0.080, +0.141], inconclusive | R2:5, R2:20; data/test_results.json planted.lead_types_cde |
| Per-type rows c, d, e, a, b (Table C1, Fig. 2) | R2:21-25; data/test_results.json planted.per_type |
| a L2 0.387 -> 0.802; b gap +0.083 [-0.083, +0.282] | R2:24-25 |
| Natural L1 0.492, L2 0.497, gap +0.005 [-0.168, +0.176] | R2:6, R2:36-37; data/test_results.json natural |
| 16 cells, 1 MOVE Sonnet c G2 +0.133 [+0.022, +0.301], 0.62 expected (0.616), 1 more c stop / 3 fewer EARNED stops | R3:22, R3:61 |
| Run SD 3.86 / 2.43 | R2:45; data/test_results.json stability |

## Section 4.3 (natural, all 15)
| Number | Source |
|---|---|
| 14 present (upper bound), 1 nothing checkable, 0 missing; existence check catches 0 of 15; 7 rest on a name with 10+ matches | R3:100-107; data/p3_corrections.json; scripts/p3_01_corrections.py |
| Gate stopped 18 of 45 EARNED vs 19 of 45 planted c+d+e; threshold 60 | R2:61; data/gate_discrimination.json |
| Previews reported passing, owner found defects (example) | LABELS-CHECK.md (jobs 426, 458), paraphrased, no quote |

## Section 4.4 (exploratory)
| Number | Source |
|---|---|
| Truncation 13 vs 35; Haiku 0.615 -> 0.738, +0.123 [-0.042, +0.304]; Sonnet* 0.878 -> 0.962; EARNED mean 47.8 -> 33.0 | R3:147-150 |
| L3 7 vs 42, 0.340 [0.146, 0.560]; dev 0.927 | R3:155 |
| L1 dev 0.784 -> test 0.492 | R2:43, R2:36 |
| Absent-item below 0.5 on c and e | R3:159-162 |

## Appendices
| Number | Source |
|---|---|
| Plant e regex 1.0, 0 of 45 EARNED | R3:131 |
| Style AUROC 0.847 (dev e) | R2:29 |
| Task-match dev -> test: Haiku 0.944 -> 0.842, Sonnet* 0.997 -> 0.944 | R3:90 |
| Overlap c 0.571, e 0.663 | R3:91 |
| 4,417 phase-3 calls | R3:167 |
| Prompts verbatim | scripts/p2_prompts.py (V['v3'] built from BASE, GOAL, RUBRIC, SCHEMA; frozen data/FROZEN.json), scripts/p3_prompts.py TM['tm1'] (data/FROZEN_P3.json) |
| Abstract: 242 words | scripts count in HANDOFF-report.md |

## References (each fetched 2026-11-07, title and authors checked against arxiv.org/abs meta tags)
2312.06942, 2502.14143, 2503.11926, 2506.15740, 2503.13657, 2605.16626 (arXiv abs pages), metr.org/blog/2025-06-05-recent-reward-hacking/ (HTTP 200, title "Recent Frontier Models Are Reward Hacking - METR"). The "Omission Attacks" Apart project was not cited: no URL could be found and fetched in this job.

## Removed for lack of a trace
None of the drafted numbers was left untraced. The draft's "a fix that did not fix" example was removed because it had no source.

## P5 extension (job #657, 2026-11-07; not yet in REPORT.pdf). All numbers: FACTS.md, generated by scripts/p5_08_facts.py
| Number | Source |
|---|---|
| Prereg before any call | PREREG-P5.md, commit 22f5634 (plants, dev baselines, power, p5_read.py + stub tests) |
| d2 45, p 28 test plants; dev d2 53, p 46 | data/p5_plants_test_counts.json, data/p5_plants_dev_counts.json; scripts/p5_01_plants.py |
| Dev baselines overlap/BM25 on d2, p | data/p5_dev_baselines.json auroc; scripts/p5_stats.py dev |
| MDE 0.141 (d2), 0.146 (p): all cells exploratory | data/p5_dev_baselines.json power |
| Every d2/p AUROC, per-repeat AUROC, paired cell, Bonferroni CI | data/p5_results.json; scripts/p5_04_stats.py; reading data/p5_reading.txt |
| 1652 calls (Haiku 590+590, Sonnet* 236+236) | data/p5_results.json calls; private/p5_runs.jsonl |
| Recount 28 checks, 0 mismatches, max CI diff 0.009 | data/p5_recount.json; scripts/p5_07_recount.py (rank-sum AUROC, own BM25/overlap, seed 7) |
| BM25 on P3 d 0.921 [0.845, 0.982]; Haiku TM - BM25 -0.024 [-0.120, +0.074] | data/p5_bm25_d.json (post hoc, no model) |
| Full-length rerun of P3 d cell (13 vs 35): omnibus 0.680, tm1 0.927; full texts <= 4054 chars | data/p5_full.json; scripts/p5_03_full.py, p5_05_full_stats.py; private/p5_full.jsonl |
| Second-reader sheet, 30 rows (15 natural UNEARNED + 15 EARNED) | private/second_reader_sheet.md (private), key private/second_reader_key_p5.json; scripts/p5_06_sheet.py |
