#!/usr/bin/env python3
"""Fig 1 (v2): AUROC [95% CI] of every scorer on plant d (P3/P4, data/p4_paired.json + data/p5_bm25_d.json) and on d2 / p (P5,
data/p5_results.json). Committed data only; no new numbers."""
import json,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5})
P=json.load(open('data/p4_paired.json'))['auroc']; B=json.load(open('data/p5_bm25_d.json')); T=json.load(open('data/p5_results.json'))['types']
d={'Word overlap':P['Word overlap (no model)'],'BM25':B['bm25'],'Haiku omnibus':P['Haiku omnibus'],'Haiku task-match':P['Haiku task-match'],
   'Sonnet* omnibus':P['Sonnet omnibus'],'Sonnet* task-match':P['Sonnet task-match']}
k5={'Word overlap':'overlap','BM25':'bm25','Haiku omnibus':'haiku_omni','Haiku task-match':'haiku_tm','Sonnet* omnibus':'sonnet_omni*','Sonnet* task-match':'sonnet_tm*'}
cols={'Word overlap':'#7f8c8d','BM25':'#34495e','Haiku omnibus':'#e74c3c','Haiku task-match':'#2e86c1','Sonnet* omnibus':'#f1948a','Sonnet* task-match':'#85c1e9'}
mk={'Word overlap':'D','BM25':'D','Haiku omnibus':'o','Haiku task-match':'o','Sonnet* omnibus':'s','Sonnet* task-match':'s'}
panels=[('d: wrong-job report\n(15 vs 45)',d),('d2: same-workflow swap\n(45 vs 45)',{k:T['d2']['auroc'][v] for k,v in k5.items()}),('p: deliverable line removed\n(28 vs 45)',{k:T['p']['auroc'][v] for k,v in k5.items()})]
f,ax=plt.subplots(figsize=(6.6,2.9)); n=len(cols); w=.12
for gi,(lab,vals) in enumerate(panels):
    for j,k in enumerate(cols):
        a,lo,hi=vals[k]; x=gi+(j-(n-1)/2)*w
        ax.errorbar(x,a,yerr=[[a-lo],[hi-a]],fmt=mk[k],color=cols[k],capsize=2,ms=4,lw=1,label=k if gi==0 else None)
ax.axhline(.5,ls=':',c='k',lw=.8); ax.set_xticks(range(3)); ax.set_xticklabels([p[0] for p in panels]); ax.set_ylim(.35,1.02)
ax.set_ylabel('AUROC vs test EARNED'); ax.spines[['top','right']].set_visible(False)
ax.legend(fontsize=7,ncol=3,loc='lower left',frameon=False); f.tight_layout(); f.savefig('report/v3/fig/fig3_scorers.png',dpi=220)
