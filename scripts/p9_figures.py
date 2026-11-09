#!/usr/bin/env python3
"""v4 figures, plain paper style (serif, vector PDF). Every number read from data/*.json."""
import json,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix','font.size':9,'axes.linewidth':.6,
  'xtick.major.width':.6,'ytick.major.width':.6,'legend.frameon':False,'pdf.fonttype':42})
C1,C2,G='#1f4e79','#b5523b','#8c8c8c'
L=json.load(open('data/label_counts.json'))['claim_by_label']; C=json.load(open('data/p3_corrections.json'))['first_table']
E,U,K=L['EARNED'],L['UNEARNED'],L['UNKNOWN']
present=C['corrected']['all_cited_artifacts_present']; nochk=C['corrected']['no_checkable_artifact_cited']; caught=C['existence_check_catches_of_15']
f,(a,b)=plt.subplots(1,2,figsize=(6.5,2.1),gridspec_kw={'width_ratios':[1.25,1]})
labs=['EARNED','UNEARNED','UNKNOWN']; vals=[E,U,K]
bars=a.barh(range(3),vals[::-1],height=.6,color=[G,C2,C1])
a.set_yticks(range(3)); a.set_yticklabels(labs[::-1])
for i,v in enumerate(vals[::-1]): a.text(v+2,i,str(v),va='center')
a.set_xlim(0,130); a.set_xlabel('Completion claims (n = %d)'%(E+U+K)); a.set_title('(a) Claims by record label',fontsize=9)
a.spines[['top','right']].set_visible(False)
cats=['Caught by\nexistence check','All cited items\nexist','Nothing\ncheckable']; v2=[caught,present,nochk]
b.bar(range(3),v2,width=.6,color=[C2,G,G]); b.set_xticks(range(3)); b.set_xticklabels(cats,fontsize=8)
for i,v in enumerate(v2): b.text(i,v+.3,str(v),ha='center')
b.set_ylim(0,16.5); b.set_ylabel('UNEARNED claims'); b.set_title('(b) Existence check on the %d UNEARNED'%U,fontsize=9)
b.spines[['top','right']].set_visible(False)
f.tight_layout(); f.savefig('report/latex/fig/fig1.pdf'); f.savefig('media/fig1.png',dpi=200); plt.close(f)
T=json.load(open('data/test_results.json')); P=T['planted']['per_type']; nat=T['natural']
names={'a':'(a) renamed\nfile','b':'(b) out-of-run\ncommit','c':'(c) fabricated\ntest log','d':"(d) other job's\nreport",'e':'(e) disclosure\nremoved'}
groups=[(names[k],P[k]) for k in 'abcde']+[('natural\n(n = %d)'%nat['n_pos'],nat)]
f,ax=plt.subplots(figsize=(6.5,2.6))
for i,(lab,r) in enumerate(groups):
    for j,(lv,c,m,ll) in enumerate([('L1',G,'o','Report only (L1)'),('L2',C1,'s','Report + evidence (L2)')]):
        s=r[lv]['auroc']; lo,hi=r[lv]['ci95']; x=i+(j-.5)*.26
        ax.errorbar(x,s,yerr=[[s-lo],[hi-s]],fmt=m,color=c,ms=4,capsize=2,lw=.9,label=ll if i==0 else None)
ax.axhline(.5,ls='--',c='k',lw=.6); ax.set_xticks(range(len(groups))); ax.set_xticklabels([g[0] for g in groups],fontsize=8)
ax.set_ylim(.15,1.0); ax.set_ylabel('AUROC'); ax.spines[['top','right']].set_visible(False); ax.legend(loc='upper right',fontsize=8)
f.tight_layout(); f.savefig('report/latex/fig/fig2.pdf'); f.savefig('media/fig2.png',dpi=200); plt.close(f)
P4=json.load(open('data/p4_paired.json'))['auroc']; B=json.load(open('data/p5_bm25_d.json')); T5=json.load(open('data/p5_results.json'))['types']
d={'Word overlap':P4['Word overlap (no model)'],'BM25':B['bm25'],'Haiku omnibus':P4['Haiku omnibus'],'Haiku task-match':P4['Haiku task-match'],'Sonnet* omnibus':P4['Sonnet omnibus'],'Sonnet* task-match':P4['Sonnet task-match']}
k5={'Word overlap':'overlap','BM25':'bm25','Haiku omnibus':'haiku_omni','Haiku task-match':'haiku_tm','Sonnet* omnibus':'sonnet_omni*','Sonnet* task-match':'sonnet_tm*'}
sty={'Word overlap':('#bdbdbd','D'),'BM25':('#636363','D'),'Haiku omnibus':(C2,'o'),'Haiku task-match':(C1,'o'),'Sonnet* omnibus':(C2,'s'),'Sonnet* task-match':(C1,'s')}
panels=[("(d) other job's report\n15 vs 45",d),('(d2) same-workflow swap\n45 vs 45',{k:T5['d2']['auroc'][v] for k,v in k5.items()}),('(p) deliverable line removed\n28 vs 45',{k:T5['p']['auroc'][v] for k,v in k5.items()})]
f,ax=plt.subplots(figsize=(6.5,2.7)); n=6; w=.12
for gi,(lab,vals) in enumerate(panels):
    for j,k in enumerate(sty):
        s,lo,hi=vals[k]; x=gi+(j-(n-1)/2)*w; c,m=sty[k]
        ax.errorbar(x,s,yerr=[[s-lo],[hi-s]],fmt=m,color=c,mfc=c if 'Sonnet' not in k else 'white',capsize=1.8,ms=3.8,lw=.8,label=k if gi==0 else None)
ax.axhline(.5,ls='--',c='k',lw=.6); ax.set_xticks(range(3)); ax.set_xticklabels([p[0] for p in panels],fontsize=8); ax.set_ylim(.35,1.02)
ax.set_ylabel('AUROC'); ax.spines[['top','right']].set_visible(False); ax.legend(fontsize=7.5,ncol=3,loc='lower left')
f.tight_layout(); f.savefig('report/latex/fig/fig3.pdf'); f.savefig('media/fig3.png',dpi=200)
print('ok',E,U,K,caught,present,nochk)
