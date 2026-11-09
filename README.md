<div align="center">

# Earned or Claimed?

*Auditing 219 "done" reports from a deployed agent swarm: what a coordinator can and cannot learn from a worker's completion report.*

![219 completion claims and the existence check](media/fig1.png)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Monitor](https://img.shields.io/badge/Monitor-Claude_Haiku_5.5-d97757)](https://www.anthropic.com/claude)
[![Apart Research](https://img.shields.io/badge/Apart_Research-Swarm_Alignment_Sprint-6cb8e0)](https://apartresearch.com/sprints/swarm-alignment-2026)
[![Track](https://img.shields.io/badge/Track-4-e8a13c)](https://apartresearch.com/sprints/swarm-alignment-2026)
[![Preregistered](https://img.shields.io/badge/Preregistered-yes-8a63d2)](PREREG-P2.md)
[![License](https://img.shields.io/badge/License-Apache_2.0-green)](LICENSE)

**[📄 The paper](report/REPORT-final.pdf)** · **[🧪 Preregistrations](PREREG-P2.md)** · **[📊 Results](RESULTS.md)** · **[🏆 Apart Swarm Alignment Sprint](https://apartresearch.com/sprints/swarm-alignment-2026)**

Nathan Langley · University of North Carolina at Greensboro<br>
*Submitted to the Swarm Alignment Hackathon, an Apart Research Sprint · November 2026*

</div>

---

## Getting started & staying tuned with us.

Star us, and you will receive all release notifications from GitHub without any delay!

<a href="https://star-history.com/#ninjahawk/earned-or-claimed&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ninjahawk/earned-or-claimed&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ninjahawk/earned-or-claimed&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ninjahawk/earned-or-claimed&type=Date" />
 </picture>
</a>

---

## Overview

In an agent swarm, a coordinator can delegate work, receive a completion report, and pass that report downstream without independently establishing that the requested work happened. A worker's "done" claim becomes a coordination signal, even when the evidence behind it is missing or contradictory.

Earned or Claimed? examines that gap in a deployed agent hierarchy. The study collected 219 completion claims from 276 delegated jobs across 15 workflows and compared them against independent records. Of those claims, 98 were supported, 15 were contradicted, and 106 could not be resolved. A file-existence check caught none of the 15 contradicted completions.

The study then tested whether language-model monitors could distinguish earned completion from false reports. A general Claude Haiku 5.5 monitor performed near chance on natural UNEARNED claims and on the preregistered pooled planted comparison. Adding external evidence substantially improved detection when a planted report cited a nonexistent file, but not when it cited an out-of-run commit.

A narrower prompt asking whether the report matched the assigned task performed better on planted wrong-task reports. It did not outperform a free BM25 baseline. No tested scorer reliably separated planted omissions from earned reports.

The central distinction is between *reporting completion* and *establishing completion*. Neither a completed runner status, a plausible report, nor the existence of cited artifacts necessarily establishes that the delegated task was fulfilled.

## What the audit shows that the completion report does not

The value of the audit is the gap between what workers claim and what independent records can establish. Three findings from the deployment and planted-failure experiments:

**1. A completed job is not necessarily an earned completion.** The orchestrator recorded 276 eligible jobs across 15 workflows. Of those, 219 had both a completed runner status and a final report claiming completion. Independent records supported 98 EARNED claims, contradicted 15 UNEARNED claims, and left 106 UNKNOWN.

| Label    | Claims | Meaning                                          |
| -------- | ------ | ------------------------------------------------ |
| EARNED   | 98     | Results ledger supported the requested outcome   |
| UNEARNED | 15     | Incident or review notes contradicted completion |
| UNKNOWN  | 106    | Neither supporting nor contradicting evidence    |
| Total    | 219    |                                                  |

UNKNOWN does not mean failure. It means the available records cannot establish the outcome.

A file-existence check caught 0 of 15 UNEARNED claims. In 14 cases, every cited item existed; the remaining claim contained nothing checkable. The failure was not simply fabricated paths. A real artifact can exist without satisfying the assigned task.


**2. External evidence helps when the monitor detects a concrete contradiction.** A general report-only Haiku monitor scored AUROC 0.492 on natural UNEARNED cases (7 versus 45 EARNED). Adding evidence produced 0.497, a paired difference of +0.005 [-0.168, +0.176].

On the preregistered pooled planted c+d+e comparison, with 45 planted cases against 45 EARNED controls, L1 scored 0.517 [0.402, 0.623] and L2 scored 0.538 [0.433, 0.649]. The paired difference was +0.022 [-0.080, +0.141]. The pooled result was inconclusive, and these planted conditions did not alter the facts available to L2.

The evidence-sensitive planted cases were more informative:

| Planted failure        | L1 AUROC [95% CI]    | L2 AUROC [95% CI]    |
| ---------------------- | -------------------- | -------------------- |
| a: renamed file        | 0.387 [0.220, 0.553] | 0.802 [0.691, 0.900] |
| b: out-of-run commit   | 0.384 [0.217, 0.548] | 0.467 [0.295, 0.635] |
| c: fabricated test log | 0.407 [0.242, 0.578] | 0.553 [0.382, 0.715] |
| d: wrong-task report   | 0.645 [0.485, 0.785] | 0.560 [0.423, 0.698] |
| e: removed disclosure  | 0.497 [0.324, 0.668] | 0.501 [0.337, 0.675] |

For planted a, the report cited a file that did not exist, and evidence substantially improved detection. For planted b, commit-timing evidence could expose the mismatch, but the monitor barely improved.

Only one of the two trace-leaving planted failure types showed a clear improvement. Providing evidence was not sufficient; the monitor also had to use it effectively.

![Report-only vs report + evidence, by planted failure type](media/fig2.png)

**3. A narrower question detects wrong-task reports better, but omissions remain difficult.** On planted wrong-task reports, Haiku's general omnibus monitor scored AUROC 0.645 [0.485, 0.785]. A task-match prompt asking whether the report matched the assigned task scored 0.897 [0.807, 0.973], a paired gain of +0.252 [+0.141, +0.378].

The free BM25 baseline scored 0.921 [0.845, 0.982]. Haiku task-match minus BM25 was -0.024 [-0.120, +0.074], providing no supported advantage over the baseline.

A harder exploratory condition, planted d2, swapped reports between the most similar tasks within the same workflow:

| Scorer              | Planted d2 AUROC [95% CI] |
| ------------------- | ------------------------- |
| Word overlap        | 0.644 [0.547, 0.741]      |
| BM25                | 0.801 [0.712, 0.882]      |
| Haiku omnibus       | 0.594 [0.506, 0.693]      |
| Haiku task-match    | 0.775 [0.693, 0.860]      |
| Sonnet\* omnibus    | 0.865 [0.797, 0.933]      |
| Sonnet\* task-match | 0.899 [0.835, 0.952]      |

Haiku task-match exceeded Haiku omnibus by +0.182 [+0.083, +0.274]. The improvement survived the six-cell Bonferroni correction, with an adjusted interval of [+0.050, +0.305]. It did not outperform BM25.

The planted omission condition, p, removed a key deliverable line from a report. Across 28 planted cases and 45 EARNED controls, no tested scorer separated omissions from earned reports:

| Scorer           | Planted p AUROC [95% CI] |
| ---------------- | ------------------------ |
| Word overlap     | 0.514 [0.435, 0.591]     |
| BM25             | 0.544 [0.467, 0.619]     |
| Haiku omnibus    | 0.541 [0.451, 0.629]     |
| Haiku task-match | 0.551 [0.441, 0.661]     |
| Sonnet\* omnibus | 0.527 [0.431, 0.624]     |

The narrower task-match question improved detection of wrong-task swaps. It did not solve missing-deliverable detection, and the tested Haiku monitor showed no advantage over the free BM25 baseline.

![Six scorers on wrong-task swaps and removed deliverables](media/fig3.png)

## Reading the figures

- **Figure 1 — Completion claims and existence checks.** EARNED means independently supported, UNEARNED means contradicted, and UNKNOWN means unresolved. UNKNOWN is not a failure label. File existence is a separate check, not proof of task completion.
- **Figure 2 — Report-only versus evidence-assisted monitoring.** L1 reads the completion report; L2 also receives external evidence. AUROC measures separation between planted failures and EARNED controls. Confidence intervals indicate uncertainty. The plotted failure types differ in whether the additional evidence exposes the alteration.
- **Figure 3 — Task consistency and omissions.** Scorers include word overlap, BM25, and language-model judgments. The wrong-task comparisons test whether a report belongs to the assigned task; the omission comparison tests whether removing a deliverable can be detected.
- **Asterisks mark circular comparisons.** Sonnet\* and Opus\* helped assign EARNED labels, so comparisons involving those models are not independent validation.
- **The plotted results are detection measurements, not completion rates.** An AUROC near 0.5 indicates little separation in the tested comparison; it does not establish that the underlying claims were true or false.

## Method

```
deployed agent hierarchy
    276 eligible delegated jobs across 15 workflows
        ↓
    completed runner status + final "done" report
        ↓
    219 completion claims
        ↓
    independent records
        ├── EARNED:   98
        ├── UNEARNED: 15
        └── UNKNOWN:  106
        ↓
    natural failure evaluation
        ├── file-existence check
        ├── L1: report-only Haiku monitor
        └── L2: report + external evidence
        ↓
    scripted edits of real reports
        ├── a: renamed file
        ├── b: out-of-run commit
        ├── c: fabricated test log
        ├── d: wrong-task report
        ├── d2: same-workflow wrong-task swap
        ├── e: removed disclosure
        └── p: removed deliverable
        ↓
    scorer comparisons
        ├── word overlap / BM25
        ├── Haiku omnibus / task-match
        └── Sonnet* omnibus / task-match
        ↓
    AUROC + confidence intervals
        → figures and per-condition results
```

**Claim labeling.** A completion claim was EARNED when the results ledger supported the requested outcome, UNEARNED when incident or review notes contradicted completion, and UNKNOWN when neither supporting nor contradicting records were available. UNKNOWN claims were not treated as failures.

**Existence checks.** Cited artifacts were checked for existence independently of whether they satisfied the task. This deliberately tests a weaker condition than completion correctness.

**Monitor comparisons.** L1 used the completion report alone. L2 additionally received external evidence. Natural UNEARNED cases and scripted planted failures were evaluated separately. The preregistered pooled comparison used planted c+d+e against EARNED controls; those edits did not change the facts supplied to L2.

**Task-match evaluation.** The narrower Haiku task-match prompt asked whether a report matched the assigned task, rather than asking for a general completion judgment. This prompt was selected post hoc after the test split had been seen. The d2 same-workflow swaps were exploratory, with paired comparisons and Bonferroni-adjusted intervals reported separately.

**Omission evaluation.** The planted p condition removed a key deliverable line from otherwise real reports and compared scorer discrimination against EARNED controls.

The study used scripted edits of real reports from one deployment, rather than claiming that every planted failure occurred naturally.

## Validation

The natural UNEARNED comparison contained 7 failures against 45 EARNED cases, below the preregistered minimum of 15 natural UNEARNED cases. Its result is underpowered.

The preregistered pooled c+d+e comparison was inconclusive: L1 scored 0.517 [0.402, 0.623], L2 scored 0.538 [0.433, 0.649], and the paired difference was +0.022 [-0.080, +0.141]. Because the planted alterations did not change L2's available facts, this comparison cannot establish whether useful external evidence improves monitoring.

The planted renamed-file condition provided a direct contradiction and produced a substantial improvement with evidence. The planted out-of-run commit condition did not produce a comparable improvement.

The task-match improvement on planted d2 survived Bonferroni correction, but the prompt was selected post hoc and the d2 experiment is exploratory. Neither the original wrong-task comparison nor the harder d2 comparison demonstrated that Haiku task-match outperformed BM25.

The planted omission comparison remained near chance for every tested scorer. Sonnet\* and Opus\* comparisons are circular because those models contributed to EARNED labeling.

The preregistration, aggregate results, and figure-generation code are included for inspection.

## Setup / Reproduce

Requirements: Python 3.11+, NumPy, SciPy, and Matplotlib. The committed aggregate and per-condition results in `data/` are sufficient to regenerate the three figures.

```bash
git clone https://github.com/ninjahawk/earned-or-claimed
cd earned-or-claimed

pip install numpy scipy matplotlib

# Regenerate all three figures from data/*.json
python scripts/p9_figures.py

# Build the paper (requires pandoc and xelatex)
python report/latex/build.py
```

**Figures.** `scripts/p9_figures.py` regenerates `media/fig1.png`, `media/fig2.png`, and `media/fig3.png` from the JSON results in `data/`.

**Paper.** The paper source is in `report/latex`. Building it requires `pandoc` and `xelatex`. The submitted PDF is [report/REPORT-final.pdf](report/REPORT-final.pdf).

**Monitor reruns.** Re-executing the monitors requires the original raw reports. Those remain private because they contain personal task data. Aggregate and per-condition results are available in `data/`, but the released data do not support independent reruns of the original monitor inputs.

## Limitations

The study examines one deployed agent hierarchy. Its natural UNEARNED sample was smaller than preregistered, and the natural monitor comparison was underpowered. Results should not be generalized to all agent swarms or completion-reporting systems.

Planted failures were produced by scripted edits of real reports. They provide controlled comparisons but do not establish the frequency or distribution of naturally occurring failures. In particular, the pooled c+d+e comparison did not give the evidence-assisted monitor new facts about the planted alteration.

The task-match prompt was selected after the test split had been seen, and the harder same-workflow d2 results are exploratory. BM25 performed at least as well as Haiku task-match in the tested wrong-task comparisons. Comparisons involving Sonnet\* or Opus\* are circular where those models contributed to the EARNED labels.

File-existence checks establish only whether cited items exist, not whether they satisfy a task. Conversely, UNKNOWN claims cannot be interpreted as failed work. The available independent records do not resolve them.

Raw reports remain private, limiting full independent reproduction of the monitor runs. The released aggregates and per-condition results support inspection and figure regeneration, not reconstruction of the original private inputs.

## Acknowledgements

This study was submitted to the [Swarm Alignment Hackathon](https://apartresearch.com/sprints/swarm-alignment-2026), an Apart Research Sprint, in November 2026.

The deployed orchestrator whose records were studied existed before the sprint; all study code in this repository was written during the sprint.

Licensed under Apache 2.0.
