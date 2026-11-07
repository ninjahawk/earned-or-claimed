#!/usr/bin/env python3
"""Stub tests for p5_read.py: every verdict branch and every ANSWER branch."""
import sys; sys.path.insert(0,'scripts'); import p5_read as P
def T(tm,ov,bm,om,d_ov,d_bm,d_om,mde=.14):
    c=lambda d:dict(diff=d[0],ci=[d[1],d[2]],ci_bonf=[d[1]-.03,d[2]+.03])
    t=dict(auroc=dict(overlap=ov,bm25=bm,haiku_omni=om,haiku_tm=tm),spread=dict(haiku_tm=[.8,.9,.04]),mde80=mde,
           paired={'haiku_tm - overlap':c(d_ov),'haiku_tm - bm25':c(d_bm),'haiku_tm - haiku_omni':c(d_om)})
    return t
pos=(.2,.1,.3); neg=(-.2,-.3,-.1); nul=(.02,-.1,.14); edge=(.05,.01,.1)
cases={
 'beats both':dict(d2=T([.9,.8,.97],[.7,.6,.8],[.7,.6,.8],[.6,.5,.7],pos,pos,pos),p=T([.5,.4,.6],[.5,.45,.55],[.5,.45,.56],[.6,.5,.7],nul,nul,neg)),
 'beats one, blind baseline':dict(d2=T([.9,.8,.97],[.55,.45,.65],[.8,.7,.9],[.6,.5,.7],pos,nul,pos,mde=.09),p=T([.5,.4,.6],[.5,.45,.55],[.5,.45,.56],[.6,.5,.7],pos,nul,nul)),
 'above chance, blind baseline':dict(d2=T([.7,.55,.8],[.5,.4,.6],[.5,.4,.6],[.6,.5,.7],pos,pos,nul),p=T([.5,.4,.6],[.5,.45,.55],[.5,.45,.56],[.6,.5,.7],nul,nul,nul)),
 'works, adds nothing':dict(d2=T([.85,.76,.93],[.85,.76,.93],[.84,.75,.92],[.7,.6,.8],nul,nul,edge),p=T([.6,.45,.72],[.5,.45,.55],[.5,.45,.56],[.6,.5,.7],pos,pos,nul)),
}
seen=set()
for n,c in cases.items():
    s=P.read(dict(types=c)); print('#',n); print(s); print()
    for k in('supported','reversed','not supported','beats both','beats word overlap (no model) only','adds nothing','is blind too','works where','does not clear the bar here, though','does not clear the bar here and is not','EXPLORATORY','powered for','reads above chance','survives','does not survive'):
        if k in s: seen.add(k)
need={'supported','reversed','not supported','beats both','beats word overlap (no model) only','adds nothing','is blind too','works where','does not clear the bar here, though','does not clear the bar here and is not','EXPLORATORY','powered for','reads above chance','survives','does not survive'}
assert need<=seen, need-seen
assert P.verdict(dict(ci=[0,.1]))=='not supported' and P.verdict(dict(ci=[.001,.1]))=='supported' and P.verdict(dict(ci=[-.1,-.001]))=='reversed'
assert P.cls([.75,.51,.9])=='PASS' and P.cls([.74,.51,.9])=='NEAR' and P.cls([.75,.5,.9])=='NEAR' and P.cls([.7,.4,.8])=='FAIL'
print('ALL BRANCHES COVERED')
