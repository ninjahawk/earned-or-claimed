#!/usr/bin/env python3
"""Red-team recompute (written fresh 2026-11-08 for REDTEAM.md). Reads ONLY raw private/*.jsonl run + plant + label files
(never FACTS/RESULTS/data summaries). Own AUROC (Mann-Whitney, ties=0.5), own cluster bootstrap (seed 777, B 2000,
one joint draw over source-job clusters), own overlap and BM25 (k1 1.5, b .75 as stated in the methods). Text scrubbing uses
p2_lib.to_task/to_report (the preprocessing the monitors saw), nothing else from the pipeline.
Prints one line per headline number: name, recomputed value [CI], so it can be diffed against the report text."""
import json, collections, random, statistics as S, re, math, sys, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, 'scripts')
from p2_lib import to_task, to_report
J = lambda f: [json.loads(l) for l in open('private/' + f)]
L = {r['id']: r for r in J('labels.jsonl')}
OUT = []
def say(k, v): OUT.append((k, v)); print(f'{k}\t{v}')

def auc(p, n):
    s = 0.0
    for x in p:
        for y in n: s += 1 if x > y else .5 if x == y else 0
    return s / (len(p) * len(n))

def scores(rows, arm_pref=None, level=None, model=None, reps=None, ver=None):
    by = collections.defaultdict(list)
    for r in rows:
        if level and r['level'] != level: continue
        if model and model not in r.get('model', 'claude-haiku-5-5'): continue
        if ver and r['ver'] != ver: continue
        if reps is not None and r['rep'] not in reps: continue
        by[(r['arm'], str(r['item']), r['source'])].append(r['score'])
    return {k: S.mean(v) for k, v in by.items() if all(x is not None for x in v)}

def split(sc, pos_arm, items=None):
    P = {k[1]: (v, k[2]) for k, v in sc.items() if k[0] == pos_arm and (items is None or k[1] in items)}
    N = {k[1]: (v, k[2]) for k, v in sc.items() if k[0] == 'EARNED' and (items is None or k[1] in items)}
    return P, N

def draws(P, N, B=2000, seed=777):
    cl = collections.defaultdict(lambda: ([], []))
    for i, (_, c) in P.items(): cl[str(c)][0].append(i)
    for i, (_, c) in N.items(): cl['E' + str(c) if False else str(c)][1].append(i)
    ks = sorted(cl); rng = random.Random(seed); out = []
    while len(out) < B:
        p, n = [], []
        for k in (rng.choice(ks) for _ in ks): p += cl[k][0]; n += cl[k][1]
        if p and n: out.append((p, n))
    return out

def pct(v, lo=.025, hi=.975):
    v = sorted(v); f = lambda q: v[min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))]
    return f'[{f(lo):.3f}, {f(hi):.3f}]'

def cell(name, P, N, dr=None):
    dr = dr or draws(P, N)
    a = auc([v for v, _ in P.values()], [v for v, _ in N.values()])
    bs = [auc([P[i][0] for i in p], [N[i][0] for i in n]) for p, n in dr]
    say(name, f'{a:.3f} {pct(bs)} (npos {len(P)}, nneg {len(N)})'); return a

def paired(name, PX, NX, PY, NY, bonf=None):
    dr = draws(PX, NX)
    d = auc([v for v, _ in PX.values()], [v for v, _ in NX.values()]) - auc([v for v, _ in PY.values()], [v for v, _ in NY.values()])
    bs = [auc([PX[i][0] for i in p], [NX[i][0] for i in n]) - auc([PY[i][0] for i in p], [NY[i][0] for i in n]) for p, n in dr]
    extra = f' bonf6 {pct(bs, .05/12, 1-.05/12)}' if bonf else ''
    say(name, f'{d:+.3f} {pct(bs)}{extra}')

# ---- labels
cl = collections.Counter(r['label'] for r in L.values() if r['claim'])
say('claims', sum(cl.values())); say('labels', dict(cl))
say('kept_jobs', len(L)); say('workflows', len({r['workflow'] for r in L.values()}))
say('UNEARNED_by_split', dict(collections.Counter(r['split'] for r in L.values() if r['claim'] and r['label'] == 'UNEARNED')))
say('test_EARNED', sum(1 for r in L.values() if r['claim'] and r['label'] == 'EARNED' and r['split'] == 'test'))
say('truncated_claims', sum(1 for r in L.values() if r['claim'] and r['truncated']))

# ---- phase 2 (test_runs, Haiku v3, 3 reps)
T = J('test_runs.jsonl')
s1, s2 = scores(T, level='L1'), scores(T, level='L2')
def pooled(sc):
    P = {}
    for a in ('plant_c', 'plant_d', 'plant_e'):
        P.update({a + k: v for k, v in split(sc, a)[0].items()})
    return P, split(sc, 'x')[1]
P1, N1 = pooled(s1); P2, N2 = pooled(s2)
cell('P2 cde L1', P1, N1); cell('P2 cde L2', P2, N2); paired('P2 cde L2-L1', P2, N2, P1, N1)
for a in 'abcde':
    for lv, sc in (('L1', s1), ('L2', s2)): cell(f'P2 {a} {lv}', *split(sc, 'plant_' + a))
for lv, sc in (('L1', s1), ('L2', s2)): cell(f'P2 natural {lv}', *split(sc, 'UNEARNED'))
paired('P2 natural L2-L1', *split(s2, 'UNEARNED'), *split(s1, 'UNEARNED'))
for lv in ('L1', 'L2'):
    by = collections.defaultdict(list)
    for r in T:
        if r['level'] == lv and r['score'] is not None: by[r['item']].append(r['score'])
    say(f'run SD {lv} (mean per-item stdev / pstdev)', f'{S.mean(S.stdev(v) for v in by.values() if len(v)>1):.2f} / {S.mean(S.pstdev(v) for v in by.values()):.2f} items {len(by)}')
# placebo
Pab = {**{('a' + k): v for k, v in split(s1, 'plant_a')[0].items()}, **{('b' + k): v for k, v in split(s1, 'plant_b')[0].items()}}
cell('placebo a+b vs EARNED Haiku L1', Pab, N1)
Pd = split(s1, 'plant_d')[0]
cell('d vs a+b Haiku L1', Pd, Pab)

# ---- phase 3/4 d cells
R3 = J('p3_runs.jsonl'); TM = J('p3_tm_test.jsonl') + J('p4_tm_repeats.jsonl')
son, opu = scores(R3, level='L1', model='sonnet'), scores(R3, level='L1', model='opus')
cell('Sonnet omnibus d', *split(son, 'plant_d')); cell('Opus omnibus d', *split(opu, 'plant_d'))
htm = scores(TM, model='haiku'); stm = scores(TM, model='sonnet')
cell('Haiku TM d (5 reps)', *split(htm, 'plant_d')); cell('Sonnet TM d', *split(stm, 'plant_d'))
reps = sorted({r['rep'] for r in TM if 'haiku' in r['model']})
say('Haiku TM d per-rep', [round(auc(*[[v for v, _ in x.values()] for x in split(scores(TM, model='haiku', reps=[k]), 'plant_d')]), 3) for k in reps])
# lexical on phase-2 d plants (task/report texts from plants_test), EARNED from export
from p2_lib import raw_rows  # read-only orchestrator.db rows: the raw source the export was made from
E = {str(k): v for k, v in raw_rows().items()}
W4 = lambda s: set(re.findall(r'[a-z]{4,}', (s or '').lower()))
ov = lambda t, r: -len(W4(t) & W4(r)) / max(1, len(W4(t) | W4(r)))
TOK = lambda s: re.findall(r'[a-z0-9]{3,}', (s or '').lower())
class BM:
    def __init__(s, docs, k1=1.5, b=.75):
        D = [TOK(d) for d in docs]; s.N = len(D); s.avg = sum(map(len, D)) / s.N; s.k1, s.b = k1, b
        df = collections.Counter(t for d in D for t in set(d)); s.idf = {t: math.log(1 + (s.N - f + .5) / (f + .5)) for t, f in df.items()}
    def score(s, q, d, uniq=True):  # uniq=True: each query term counted once (the report's variant); False: repeats count
        tf = collections.Counter(TOK(d)); Ln = sum(tf.values()); o = 0
        for t in (set(TOK(q)) if uniq else TOK(q)):
            if t in tf: f = tf[t]; o += s.idf.get(t, math.log(1 + (s.N + .5) / .5)) * f * (s.k1 + 1) / (f + s.k1 * (1 - s.b + s.b * Ln / s.avg))
        return -o
def lex_items(split_, plantfile, types):
    it = {}
    for i, r in L.items():
        if r['split'] == split_ and r['claim'] and r['label'] == 'EARNED':
            it[str(i)] = ('EARNED', to_task(E[str(i)]['task']), to_report(E[str(i)]['handoff']), i)
    for p in J(plantfile):
        if p['type'] in types: it[p['item']] = (p['type'], p['task'], p['report'], p['source'])
    bm = BM([to_report(E[str(i)]['handoff']) for i, r in L.items() if r['split'] == split_ and r['claim']])
    return it, bm
it, bm = lex_items('test', 'plants_test.jsonl', ('d',))
for nm, fn in (('overlap', ov), ('BM25', bm.score), ('BM25 query-tf variant', lambda t, r: bm.score(t, r, uniq=False))):
    sc = {(a, k, c): fn(t, r) for k, (a, t, r, c) in it.items()}
    cell(f'{nm} d', *split(sc, 'd'))
    paired(f'Haiku TM - {nm} on d', *split({('d' if k[0]=='plant_d' else k[0], k[1], k[2]): v for k, v in htm.items()}, 'd'), *split(sc, 'd'))
ho = scores(T, level='L1')
paired('Haiku TM - Haiku omnibus on d', *split(htm, 'plant_d'), *split(ho, 'plant_d'))
sco = {(a, k, c): ov(t, r) for k, (a, t, r, c) in it.items()}
paired('overlap - Haiku omnibus on d', *split(sco, 'd'), *split({('d' if k[0]=='plant_d' else k[0], k[1], k[2]): v for k, v in ho.items()}, 'd'))

# ---- phase 5 d2/p
R5 = J('p5_runs.jsonl')
c5 = {'Haiku omnibus': scores(R5, level='L1', model='haiku'), 'Haiku task-match': scores(R5, level='TM', model='haiku'),
      'Sonnet omnibus': scores(R5, level='L1', model='sonnet'), 'Sonnet task-match': scores(R5, level='TM', model='sonnet')}
say('P5 calls', {k: sum(1 for r in R5 if r['level'] == lv and m in r['model']) for k, lv, m in (('HO', 'L1', 'haiku'), ('HT', 'TM', 'haiku'), ('SO', 'L1', 'sonnet'), ('ST', 'TM', 'sonnet'))})
it5, bm5 = lex_items('test', 'p5_plants_test.jsonl', ('d2', 'p'))
c5['Word overlap'] = {(a, k, c): ov(t, r) for k, (a, t, r, c) in it5.items()}
c5['BM25'] = {(a, k, c): bm5.score(t, r) for k, (a, t, r, c) in it5.items()}
c5q = {(a, k, c): bm5.score(t, r, uniq=False) for k, (a, t, r, c) in it5.items()}
for t in ('d2', 'p'): cell(f'P5 {t} BM25 query-tf variant (sensitivity)', *split(c5q, t))
for t in ('d2', 'p'):
    P, _ = split(c5['BM25'], t); say(f'P5 {t} n/clusters', f'{len(P)} / {len({c for _, c in P.values()})}')
    for k, sc in c5.items(): cell(f'P5 {t} {k}', *split(sc, t))
    for x, y in (('Haiku task-match', 'Word overlap'), ('Haiku task-match', 'BM25'), ('Haiku task-match', 'Haiku omnibus'), ('Haiku omnibus', 'BM25'), ('Sonnet task-match', 'BM25'), ('Haiku omnibus', 'Word overlap')):
        paired(f'P5 {t} {x} - {y}', *split(c5[x], t), *split(c5[y], t), bonf=True)

# ---- truncation subset (13 d / 35 EARNED)
F5 = J('p5_full.jsonl'); sub = {str(r['item']) for r in F5}
o2000 = scores(T, level='L1'); ofull = scores(F5, level='L1nocap'); t2000 = htm; tfull = scores(F5, level='TMnocap')
for nm, sc in (('omni 2000', o2000), ('omni nocap', ofull), ('TM 2000', t2000), ('TM nocap', tfull)):
    cell(f'trunc {nm}', *split(sc, 'plant_d', sub))
paired('trunc omni nocap-2000', *split(ofull, 'plant_d', sub), *split(o2000, 'plant_d', sub))
paired('trunc TM nocap-2000', *split(tfull, 'plant_d', sub), *split(t2000, 'plant_d', sub))
paired('trunc nocap TM-omni', *split(tfull, 'plant_d', sub), *split(ofull, 'plant_d', sub))
FR = {str(json.loads(l).get('id', json.loads(l).get('item'))): json.loads(l) for l in open('private/full_reports.jsonl')}
srcs = {int(k) for k in sub if k.isdigit()} | {r['source'] for r in F5 if r['arm'] == 'plant_d'}
lens = [len(to_report(FR[str(i)]['full'])) for i in srcs if str(i) in FR]
if lens: say('trunc uncapped len max/median (subset sources, scrubbed)', f'{max(lens)} / {sorted(lens)[len(lens)//2]} n {len(lens)}')
# run-to-run check: the same uncapped omnibus input, phase-3 [:12000] run vs phase-5 no-cap run
F3 = J('p3_full.jsonl'); o3 = scores(F3, level='L1full', model='haiku')
cell('trunc omni P3[:12000] same inputs', *split(o3, 'plant_d', sub))
paired('trunc omni P5nocap - P3[:12000] (identical text)', *split(ofull, 'plant_d', sub), *split(o3, 'plant_d', sub))
paired('trunc TM2000 - omni2000', *split(t2000, 'plant_d', sub), *split(o2000, 'plant_d', sub))
