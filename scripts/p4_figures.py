#!/usr/bin/env python3
"""Report figures from committed data only: data/p4_paired.json (Fig 1), data/test_results.json (Fig 2)."""
import json,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':9})
P=json.load(open('data/p4_paired.json'))['auroc']
order=[('Haiku omnibus','Haiku\nomnibus','#c0392b'),('Word overlap (no model)','Word overlap\n(no model)','#7f8c8d'),('Haiku task-match','Haiku\ntask-match','#2e86c1'),
       ('Sonnet omnibus','Sonnet\nomnibus*','#c0392b'),('Opus omnibus','Opus\nomnibus*\n(1 run)','#c0392b'),('Sonnet task-match','Sonnet\ntask-match*','#2e86c1')]
f,ax=plt.subplots(figsize=(6.3,2.7))
for x,(k,l,c) in enumerate(order):
    a,lo,hi=P[k]; ax.errorbar(x,a,yerr=[[a-lo],[hi-a]],fmt='o',color=c,capsize=4,ms=6); ax.text(x+.12,a,f'{a:.3f}',va='center',fontsize=8)
ax.axhline(.5,ls=':',c='k',lw=.8); ax.axhline(.75,ls='--',c='#999',lw=.8); ax.text(5.45,.755,'bar .75\n(post hoc)',fontsize=7,color='#666',va='bottom',ha='right')
ax.set_xticks(range(len(order))); ax.set_xticklabels([o[1] for o in order],fontsize=8); ax.set_ylim(.4,1.02); ax.set_ylabel('AUROC, plant d vs EARNED')
ax.spines[['top','right']].set_visible(False); f.tight_layout(); f.savefig('report/fig/fig1_plant_d.png',dpi=220)
T=json.load(open('data/test_results.json')); pt=T['planted']['per_type']
rows=[('c+d+e\npooled',T['planted']['lead_types_cde']),('c fake\ntest log',pt['c']),('d wrong\ntask',pt['d']),('e over-\nstated',pt['e']),('a missing\nfile',pt['a']),('b wrong\ncommit',pt['b']),('natural\n(7 vs 45)',T['natural'])]
f,ax=plt.subplots(figsize=(6.3,2.6))
for x,(l,r) in enumerate(rows):
    for dx,lv,c in ((-.13,'L1','#555'),(.13,'L2','#e67e22')):
        a=r[lv]['auroc'];lo,hi=r[lv]['ci95']; ax.errorbar(x+dx,a,yerr=[[a-lo],[hi-a]],fmt='o' if lv=='L1' else 's',color=c,capsize=3,ms=5,label=lv if x==0 else None)
ax.axhline(.5,ls=':',c='k',lw=.8); ax.axvspan(3.5,5.5,color='#eee',zorder=0); ax.text(4.5,.13,'L1-blind by design',ha='center',fontsize=7,color='#666')
ax.axvspan(-.5,3.5,color='#fbfbf0',zorder=0); ax.text(1.5,.13,'L2-blind by construction',ha='center',fontsize=7,color='#666')
ax.set_xticks(range(len(rows))); ax.set_xticklabels([r[0] for r in rows],fontsize=8); ax.set_ylim(.1,1); ax.set_ylabel('AUROC vs 45 EARNED'); ax.legend(['L1 report only','L2 + evidence facts'],fontsize=7,loc='upper right',frameon=False)
h,lb=ax.get_legend_handles_labels(); ax.legend(h,['L1: task + report','L2: + evidence facts'],fontsize=7,loc='upper left',frameon=False)
ax.spines[['top','right']].set_visible(False); f.tight_layout(); f.savefig('report/fig/fig2_visibility.png',dpi=220)
