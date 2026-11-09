In an agent swarm, a coordinator that trusts a worker's "done" report can pass false completion claims downstream; in one deployed hierarchy, neither reading the report nor checking cited files for existence reliably caught these failures, while external evidence improved detection when it directly exposed a planted nonexistent file, but not a planted out-of-run commit.

I studied 219 completion claims from 276 delegated jobs across 15 workflows. Independent records supported 98 EARNED claims, contradicted 15 UNEARNED claims, and left 106 UNKNOWN. A file-existence check caught 0 of 15 UNEARNED claims: 14 cited only existing items, and one cited nothing checkable.

A report-only Haiku monitor performed near chance on natural UNEARNED cases (AUROC 0.492, n = 7) and on pooled planted c+d+e failures (0.517 [0.402, 0.623]). Adding evidence improved detection of a planted renamed file from 0.387 to 0.802 [0.691, 0.900], but barely helped on planted out-of-run commits (0.384 to 0.467).

A narrower Haiku task-match prompt detected planted wrong-task reports better than the omnibus prompt: AUROC 0.897 versus 0.645, a paired gain of +0.252 [+0.141, +0.378]. The gain persisted on harder same-workflow swaps (+0.182 [+0.083, +0.274]), but task-match was no better than a free BM25 baseline.

No tested scorer separated planted omissions from earned reports (AUROC 0.514–0.551). These results come from scripted edits of real reports in one deployment.