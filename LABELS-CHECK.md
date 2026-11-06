# LABELS-CHECK.md
All numbers come from data/*.json, written by scripts/01, 03 and 06. Raw text stays in private/.

## Who checked
The reader is Claude Opus 5.5, the same agent that wrote the rule. This is not an independent or human check, and the agreement below is an upper bound on real reliability. Phase 2 needs a second reader.

## Funnel
- Closed delegations: 506. Excluded workflows: 138. Dropped by privacy filter: 92. Kept: 276 (done 232, stopped 31, failed 13).
- Reported-done population: 212. No claim: 64.
- Labels in reported-done: {'EARNED': 99, 'UNEARNED': 2, 'UNKNOWN': 111}.
- By split: {'dev/EARNED': 52, 'dev/UNKNOWN': 63, 'test/EARNED': 47, 'test/UNEARNED': 2, 'test/UNKNOWN': 48}. Held-out workflows: forge, youtube, ytreal.

## Natural unearned completions left after exclusions: 2
Both are in test and in one workflow (jobs 426 and 458, youtube): previews reported as passing every hard check, then the owner found a missing door and a floating character. Both had a results-ledger line first, so the verifier missed them too.
Most flagged candidates turned out not to be unearned: 7 others were read and left UNKNOWN or no-claim (jobs 190, 396, 433, 569, 577, 620, 633), mostly honest negative results or mixed evidence (data/hand_overrides.json). Job 422 stays EARNED: it disclosed its unmerged part. A further candidate, 580, was removed by the privacy filter. Below the prereg threshold of 15, so the primary comparison is underpowered. With workflow count this low, bootstrap is by job.

## Agreement, fresh stratified sample (n=42), rule as of the draw vs reader
Overall 35/42 = 83.3%, kappa 0.743. After the parser fixes, 36/42 agree.
- EARNED: 19/20. One unclear. Two of the 20 were real but partial (one of two items), so the binary label is coarse.
- UNKNOWN: 12/14. Two were real citations in a format the parser missed; fixed.
- NO-CLAIM regex: 4/8. Half its calls were wrong, and those jobs do claim completion. This is the noisiest part. It shrinks the population rather than poisoning a label, but roughly half of the no-claim done jobs are missing from the population.
An earlier sample (29 sampled plus 10 flagged candidates) found the parser bug and is why this sample exists; its verdicts were not recorded per job, so it gives no agreement figure.

## Label noise that the rule cannot see
- EARNED means a verifier logged it, not that it holds. At least 2 of the 101 cited jobs were later contradicted by the owner. Only incidents that were written down can reveal this, so 2% is a floor.
- Only 2 owner-caught jobs were mapped from incident text; any other defect reports that name a video instead of a job id are not yet mapped.
- UNKNOWN is 111 of 212, excluded from metrics. Unverified work may behave differently from verified work.

## Transcripts
112 of 276 kept jobs link to a local transcript ({'host': 26, 'vm': 86}). In reported-done: 90. Labeled test items with a transcript: 12. Neither natural UNEARNED job links ([]). Level 3 is a small subset and says so. Host transcripts on the PC mount were not scanned, so this may rise.

## Privacy and scrub test
Filter and scrub run before any model sees text. Test: 50-row sample in private/scrub-test.txt, plus pattern assertions over all 276 rows (data/scrub_check.json), plus a residual proper-noun scan.
Leaks found and fixed, retested each time: further person and channel names, video ids, upper-case owner name, host run paths. Final assertions: 0 hits across all rows.
Limit: name detection uses a blocklist built from a vocabulary scan, not a full read of every row. Filter is deliberately broad, so 92 rows are lost. Nothing here is public.
