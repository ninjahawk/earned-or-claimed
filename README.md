# Earned or claimed? Apart Swarm Alignment sprint entry (Track 4)

## Report: Earned or Claimed? Auditing 219 "Done" Reports From a Deployed Agent Swarm
In an agent swarm, a coordinator that trusts a worker's "done" report can pass false completion claims downstream; in one deployed hierarchy, neither reading the report nor checking cited files for existence reliably caught these failures, while external evidence improved detection when it directly exposed a planted nonexistent file, but not a planted out-of-run commit.
PDF: [report/REPORT-final.pdf](report/REPORT-final.pdf). Figures: `scripts/p8_figures.py`, `scripts/p8_fig3.py`; layout: `scripts/p7_packet.py`.

Work here started Fri 2026-11-06; only this repo's commits are sprint work.

PREEXISTING, not sprint work: the Orchestrator orchestrator, its delegations table, results ledger, incident reports, notes, and logs. They were written before the sprint and serve here as a read-only data source. They are not in this repo.
Monitors use Claude Haiku 5.5 unless stated.
Privacy: the raw data describes a person's life. `private/` is gitignored; nothing goes public without Nathan's explicit yes.
Phase 2 numbers: RESULTS.md. Plan and deviations: PREREG-P2.md, QUESTION.md.
