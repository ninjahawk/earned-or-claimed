# PREREG-P4: task-match repeats (written and committed before any call)
Job #656, 2026-11-07. Post hoc by nature: test data has been seen. Judges asked for variance.
- Run the FROZEN task-match prompt tm1 (data/FROZEN_P3.json), unchanged, on test plant d (15) + EARNED (45) only.
- Haiku: 2 new repeats (rep 3, 4). Sonnet: 1 new repeat (rep 3). Output private/p4_tm_repeats.jsonl; P3 files untouched.
- Report whatever they show: per-repeat AUROC for every repeat (old 0-2 and new), the new means over all repeats (Haiku 5, Sonnet 4) REPLACE the 3-repeat means in the report's headline numbers, with CIs from the same clustered bootstrap as scripts/p3_14_brain_recount.py. The P3 3-repeat numbers are shown beside them.
- If the new mean falls below the .75 bar, or its CI lower bound is <= .5, the report says so in the abstract-level claim and drops "PASS" for that row. No cherry-picking, no further repeats, no prompt changes.
- Script: scripts/p4_tm_repeats.py; stats: scripts/p4_tm_stats.py.
