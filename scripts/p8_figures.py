#!/usr/bin/env python3
"""v3 figures. Every number is read from data/*.json; nothing typed.
Fig 1 (hero): 219 completion claims by record label + existence check on the 15 natural UNEARNED.
Fig 2: Haiku L1 (report only) vs L2 (report + evidence facts), AUROC [95% CI], plants a-e and natural."""
import json,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.edgecolor':'#444','axes.linewidth':.6})
BLUE,RED,GREY,DARK='#2a6f97','#c0392b','#b8bec4','#1d2b36'
L=json.load(open('data/label_counts.json'))['claim_by_label']; C=json.load(open('data/p3_corrections.json'))['first_table']
E,U,K=L['EARNED'],L['UNEARNED'],L['UNKNOWN']; N=E+U+K
present=C['corrected']['all_cited_artifacts_present']; nochk=C['corrected']['no_checkable_artifact_cited']; caught=C['existence_check_catches_of_15']
assert present+nochk+caught==U
f=plt.figure(figsize=(7.0,1.9)); ax=f.add_axes([.02,.36,.62,.40])
x=0
for v,c,lab in [(E,BLUE,'EARNED'),(U,RED,'UNEARNED'),(K,GREY,'UNKNOWN')]:
    ax.barh(0,v,left=x,color=c,height=.8,edgecolor='white',lw=1.2)
    if v>=40: ax.text(x+v/2,0,f'{v}',ha='center',va='center',color='white' if c!=GREY else DARK,fontsize=13,fontweight='bold')
    ax.text(x+v/2,-.75,{'EARNED':'EARNED\nresults ledger cites\nthe delivered result','UNEARNED':'UNEARNED\nrecords say\nit did not hold','UNKNOWN':'UNKNOWN\nno record either way'}[lab],ha='center',va='top',fontsize=7.2,color=DARK)
    if lab=='UNEARNED': ax.text(x+v/2,0,f'{v}',ha='center',va='center',color='white',fontsize=9,fontweight='bold')
    x+=v
ax.set_xlim(0,N); ax.set_ylim(-.6,.6); ax.axis('off')
ax.text(0,.68,f'{N} "done" claims from one deployed agent orchestrator',fontsize=9.5,fontweight='bold',color=DARK,va='bottom')
ax2=f.add_axes([.68,.04,.31,.92]); ax2.axis('off'); ax2.set_xlim(0,1); ax2.set_ylim(0,1)
ax2.text(.5,.97,f'Existence check on\nthe {U} UNEARNED claims',ha='center',va='top',fontsize=8.6,fontweight='bold',color=DARK)
ax2.text(.5,.52,f'{caught} / {U}',ha='center',va='center',fontsize=30,fontweight='bold',color=RED)
ax2.text(.5,.31,'caught',ha='center',va='center',fontsize=9,color=RED)
ax2.text(.5,.14,f'{present}: every cited file / commit exists\n{nochk}: nothing checkable cited',ha='center',va='center',fontsize=7.2,color=DARK)
ax2.add_patch(plt.Rectangle((.04,.03),.92,.96,fill=False,ec='#c9cdd1',lw=.8))
f.savefig('report/v3/fig/fig1_claims.png',dpi=250); plt.close(f)
T=json.load(open('data/test_results.json')); P=T['planted']['per_type']; nat=T['natural']
names={'a':'a: cited file\nrenamed','b':'b: commits from\noutside the run','c':'c: fabricated\ntest log','d':'d: another job\'s\nreport','e':'e: disclosure\nremoved'}
groups=[(names[k],P[k]) for k in 'abcde']+[(f'natural\n(n = {nat["n_pos"]})',nat)]
f,ax=plt.subplots(figsize=(7.0,2.7))
for i,(lab,r) in enumerate(groups):
    for j,(lv,c,m) in enumerate([('L1',GREY,'o'),('L2',BLUE,'s')]):
        a=r[lv]['auroc']; lo,hi=r[lv]['ci95']; xx=i+(j-.5)*.28
        ax.errorbar(xx,a,yerr=[[a-lo],[hi-a]],fmt=m,color=c if lv=='L2' else '#6c757d',ms=5,capsize=2.5,lw=1.1,label=({'L1':'L1: report only','L2':'L2: report + evidence facts'}[lv] if i==0 else None))
        if lv=='L2' and lab.startswith('a'): ax.annotate(f'{a:.3f}',(xx,a),xytext=(8,0),textcoords='offset points',va='center',fontsize=7.5,color=BLUE,fontweight='bold')
        if lv=='L1' and lab.startswith('a'): ax.annotate(f'{a:.3f}',(xx,a),xytext=(8,0),textcoords='offset points',va='center',ha='left',fontsize=7.5,color='#6c757d')
ax.axhline(.5,ls=':',c='k',lw=.8); ax.text(4.5,.505,'chance',fontsize=7,va='bottom',ha='right')
ax.axvspan(-.5,1.5,color='#eaf2f8',zorder=-1); ax.text(.5,1.0,'failure leaves a trace in the evidence',ha='center',fontsize=7.2,color=BLUE)
ax.axvspan(1.5,4.5,color='#f7f7f7',zorder=-1); ax.text(3,1.0,'evidence facts unchanged by construction',ha='center',fontsize=7.2,color='#555')
ax.set_xticks(range(len(groups))); ax.set_xticklabels([g[0] for g in groups],fontsize=7.5); ax.set_xlim(-.5,len(groups)-.5); ax.set_ylim(.15,1.05)
ax.set_ylabel('AUROC vs 45 test EARNED'); ax.spines[['top','right']].set_visible(False)
ax.legend(fontsize=7.3,loc='lower right',frameon=False,ncol=2); f.tight_layout(); f.savefig('report/v3/fig/fig2_evidence.png',dpi=250)
print('fig1',E,U,K,caught,present,nochk); print('fig2',{k:(P[k]['L1']['auroc'],P[k]['L2']['auroc']) for k in 'abcde'},nat['L1']['auroc'],nat['L2']['auroc'])
