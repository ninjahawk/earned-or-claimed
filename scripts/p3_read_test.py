#!/usr/bin/env python3
"""Synthetic-input tests of p3_read: every combination of the five classes with both overlap values, and every MOVE pattern over the 16 cells with scale and stability flags. No model."""
import sys,itertools as I
sys.path.insert(0,'scripts'); from p3_read import *
KS=['omni_haiku','omni_sonnet','omni_opus','tm_haiku','tm_sonnet']
cells=[f'{k}/{p}/{l}' for k,_ in STRONG for p in PLANTS for l in LEVELS]; assert len(cells)==16
assert klass(.75,.51)=='PASS' and klass(.75,.5)=='NEAR' and klass(.74,.51)=='NEAR' and klass(.74,.5)=='FAIL'
base=dict(tm_fall={'haiku':False,'sonnet':False},overlap_separates=True,not_narrow=[],scale_unusable={},haiku_unstable=False,mde=.2,false_move_rate=.01)
na=0
for vals in I.product(CLS,repeat=5):
    c=dict(zip(KS,vals))
    for ov,fall in I.product((True,False),(True,False)):
        f=dict(base,overlap_separates=ov,tm_fall={'haiku':fall,'sonnet':False}); t=' '.join(conclusion_a(c,f)); na+=1
        om=[k for k in KS[:3] if c[k]=='PASS']; tm=[k for k in KS[3:] if c[k]=='PASS']
        assert t.startswith('(A)') and 'says nothing about evidence, in either direction' in t
        assert ('no arm here saw' in t)==(not om and not tm)
        assert ('the omnibus prompt missed' in t)==(not om and bool(tm))
        assert ('not by Haiku' in t)==(bool(om) and c['omni_haiku']!='PASS')
        assert ('not an easy mismatch' in t)==(not om and not tm and not ov)
        assert t.count('unreplicated')==len(om)+len(tm)
        assert ('possible non-transfer' in t)==fall
        assert ('Opus omnibus L1 (1 repeat)' in t)==(c['omni_opus']=='PASS')
nb=0
for bits in I.product((False,True),repeat=16):
    m=dict(zip(cells,bits)); un=(sum(bits)%3==0); f=dict(base,scale_unusable={'sonnet':un,'opus':False},haiku_unstable=(sum(bits)%2==0)); t=' '.join(conclusion_b(m,f)); nb+=1
    counted=[x for x,b in m.items() if b and not(x.endswith('/G2') and x.startswith('sonnet') and un)]
    assert t.startswith('(B)')
    assert ('is weakened for' in t)==bool(counted)
    assert ('No change detected at this power' in t)==(not counted)
    if not counted: assert 'is not strengthened by this' in t and '0.200' in t
    assert 'says nothing about evidence' not in t.replace('may not say the null says nothing about evidence','')
    assert 'may not say the null says nothing about evidence' in t
    if counted: assert 'planted only' in t and 'monitor weakness' in t
assert 'Haiku\'s row is the only one independent of labels' in conclusion_c()[0]
assert all(s for s in read(dict(classes=dict(zip(KS,['FAIL']*5)),moves={},flags=base)))
print('p3_read tests pass:',na,'A cases,',nb,'B cases')
