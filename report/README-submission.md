# Submission README: "Did It Actually Happen? Checking Workers' 'Done' Claims in a Deployed Agent Hierarchy"
Apart Research Swarm Alignment sprint, Track 4. Author: Nathan Langley ([NATHAN: affiliation]).

## Preexisting work (declared, not judged)
- The orchestrator ("Orchestrator") that produced the data: its code, delegation database, results ledger, incident reports, verifier notes, sentinel monitor files, logs and job runner. All were built and running before the sprint.
- The corpus itself: 506 delegations closed between 24 Oct and 6 Nov 2026, of which 219 are completion claims. It was used read-only.
- No code written before the sprint is in the study repository. The study uses the orchestrator's job runner and the `claude -p` CLI as tools.

## Sprint work (judged), with git dates from the study repository
- 2026-11-06 16:56 ET: rules copy and frozen preregistration (3d7ec82).
- 2026-11-06 17:00-17:03: scrubbed export, rule labels, hand-check, L1 pilot (cbc8e95, ffe418b, 3b490a4).
- 2026-11-06 17:42: natural label sweep with blind AI readers (5bd754c).
- 2026-11-06 18:37-19:03: phase 2 (L2 evidence facts, planted false completions, frozen prompts, test runs, results; 936837f..e1f6915).
- 2026-11-06 19:18-20:14: phase 3 (other models, task-match, controls, truncation, L3, absent-item; 65c4633..16f16e5).
- 2026-11-07: phase 4 task-match repeats (prereg f2b2b66 before any call, run 71f6315), figures, and this report.

## Files
- REPORT.pdf: the submission.
- REPORT.md, NUMBERS-TRACE.md (every number traced to its file and script) and the figures are in the study repository, which is not public.

## How to submit (Nathan, about 10 minutes)
1. Fill the [NATHAN: ...] fields in REPORT.md (affiliation, author contributions, LLM usage statement, optional repo link), then ask me to re-render. Or edit the PDF source yourself; the render script is `scripts/p4_render.py`.
2. Read the abstract, §4.1 and Appendix A. The template asks that the final text be "primarily written by your team", so rewrite in your own words wherever you want to.
3. Open https://apartresearch.com/sprints/swarm-alignment-2026, then the submission form on that page.
4. Use this exact title: "Did It Actually Happen? Checking Workers' 'Done' Claims in a Deployed Agent Hierarchy". Choose Track 4, upload REPORT.pdf, and list yourself as the author with your affiliation.
5. Submit before Sun 8 Nov 23:59 AoE (Mon 06:59 ET). To fix something later, resubmit with the same title; the new submission replaces the old one. Check the confirmation email for the right PDF.
