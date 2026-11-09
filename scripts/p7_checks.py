#!/usr/bin/env python3
"""Deterministic structural checks of report v2 vs v1 + REDTEAM checklist + privacy grep. Usage: p7_checks.py v1.md v2.md v2.pdf"""
import re,sys,subprocess
N=lambda t:t.replace('−','-').replace('–','-').replace('—','-').replace('\r\n','\n')
v1,v2=N(open(sys.argv[1]).read()),N(open(sys.argv[2]).read()); pdf=sys.argv[3]; fails=[]
def ck(name,ok,info=''):
    print(('PASS ' if ok else 'FAIL ')+name+(' | '+info if info else ''));
    if not ok: fails.append(name)
ck('title',v2.split('\n',1)[0].strip()=='# Can a Monitor Tell When an AI Agent Has Actually Finished Its Task?',v2.split('\n',1)[0])
for sec in ['Abstract','Introduction','Related Work','Methodology','Results','Discussion','Conclusion','Reproducibility','Author Contributions','Appendix A','Limitations and Dual-Use','Appendix B','LLM Usage Statement','References']:
    ck('section '+sec,re.search(r'^#+ .*'+re.escape(sec),v2,re.M) is not None)
ab=v2.split('## Abstract',1)[1].split('\n## ',1)[0]; w=len(ab.split()); ck('abstract 150-250 words',150<=w<=250,str(w))
ck('no [NATHAN]','NATHAN' not in v2)
ck('no utm','utm_' not in v2)
for h in ['underpowered','inconclusive','exploratory','post hoc|post-hoc','circular|not independent','BM25','near chance|chance','human','Bonferroni','preregist']:
    a,b=len(re.findall(h,v1,re.I)),len(re.findall(h,v2,re.I)); ck(f'hedge "{h}" kept',b>=1 if a else True,f'v1 {a} v2 {b}')
ck('LLM stmt: labels read by AI, not human',re.search(r'not checked by a human',v2) is not None)
llm=v2.split('LLM Usage Statement',1)[1].split('\n## ',1)[0] if 'LLM Usage Statement' in v2 else ''
for k in ['designed and ran','number']: ck('LLM stmt has '+k,k in llm)
ck('affiliation','University of North Carolina at Greensboro' in v2)
ck('contributions','designed and directed the project' in v2)
items={'B1 fields':['Greensboro'],'M1 post hoc in abstract':None,'M2 plant a 0.802':['0.802'],'M3 d rule 0.25':['0.25|25%|25 percent'],'M3 dev baseline 0.678':['0.678'],
 'M4 Bonferroni overlap -0.016, +0.279':[r'0\.016, \+?0\.279'],'M4 BM25 gaps':['0.024','0.026'],'M5 run noise 0.738':['0.738'],'M5 -0.058':['0.058'],'M6 single repeat 0.702':['0.702'],
 'M7 26 of 99':[r'\b26\b'],'M8 shared jobs':[r'same (45 )?(test )?EARNED|built from|share'],'M9 106 UNKNOWN':[r'106'],'M10 Figure 1':['Figure 1'],'M10 Table 1':['Table 1'],'M10 contributions':['contributions are'],
 'm1 fixed sentence':['Everything in the brief'],'m2 permutations':[r'2,?000 permutations'],'m3 0-100':[r'0-100|0 to 100'],'m4 0.107 or 0.278':[r'0\.107|0\.278'],'m5 55 truncated':[r'\b55\b'],'m6 voice (we count)':None}
for k,pats in items.items():
    if k.startswith('M1'): ok=re.search(r'post hoc|post-hoc|after (seeing|inspect|looking)',ab,re.I) is not None
    elif k.startswith('m6'): n=len(re.findall(r'\b[Ww]e\b|\bour\b',v2.split('## References')[0])); ok=n<=3; k+=f' ({n})'
    else: ok=all(re.search(p,v2) for p in pats)
    ck('REDTEAM '+k,ok)
ck('figure image line','![Figure 1](fig/fig3_all_scorers.png)' in v2)
txt=subprocess.run(['pdftotext','-layout',pdf,'-'],capture_output=True,text=True).stdout; pages=txt.split('\f')
body_end=next((i+1 for i,p in enumerate(pages) if re.search(r'Author Contributions',p)),None)
ck('body <= 8 pages (Author Contributions starts on page)',body_end is not None and body_end<=8,f'{body_end} of {len(pages)-1}')
priv=re.findall(r'[A-Za-z]:\\\S+|/(?:mnt|srv|home)/\S+|[\w.+-]+@[\w-]+\.\w+|\b\w+\.(?:py|jsonl|json)\b|private/|USER|Desktop',txt,re.I)
ck('privacy grep',not priv,str(priv[:10]))
print('FAILS',len(fails),fails)
