"""Phase 3 runner and shared inputs. Reuses p2_lib, p2_prompts; only the model name changes. Concurrency 5, retries in call(), every call written as it returns, resumable, meter guard, deadline."""
import sys,json,os,re,time,subprocess,threading,concurrent.futures as X
sys.path.insert(0,'scripts'); from p2_lib import *; import p2_prompts as PP
HAIKU_='claude-haiku-5-5'; SONNET='claude-sonnet-5-5'; OPUS='claude-opus-5-5'; GUARD=40.0
_DROPNS={}; exec(open(ROOT+'scripts/01_export.py').read().split('def main')[0],_DROPNS); DROP=_DROPNS['DROP']
def weekly():
    try: return float(subprocess.run(['python3','-c','from orchestrator import meter; print(meter.meters(fresh=0)["weekly"])'],cwd='ORCH_ROOT/repo',capture_output=True,text=True,timeout=90).stdout.strip())
    except Exception: return None
def test_items(split='test'):
    L=labels(); J={json.loads(l)['id']:json.loads(l) for l in open(ROOT+'private/export.jsonl')}; F={json.loads(l)['id']:json.loads(l) for l in open(ROOT+'private/facts.jsonl')}; it=[]
    for i,d in L.items():
        if d['split']==split and d['claim'] and d['label'] in('EARNED','UNEARNED'):
            it.append(dict(item=str(i),arm=d['label'],task=J[i]['task'],report=J[i]['handoff'],ft=facts_text(F[i]),source=i))
    for l in open(ROOT+f'private/plants_{split}.jsonl'):
        p=json.loads(l); it.append(dict(item=p['item'],arm='plant_'+p['type'],task=p['task'],report=p['report'],ft=facts_text(p['facts']),source=p['source']))
    return it
def run(jobs,outf,fn,deadline=540):
    """jobs: dicts with item,level,rep,model. fn(job)->dict with score. Skips jobs already scored. Returns what is left."""
    key=lambda r:(r['model'],r['level'],r['item'],r['rep']); done=set()
    if os.path.exists(outf):
        for l in open(outf):
            r=json.loads(l)
            if r.get('score') is not None: done.add(key(r))
    todo=[j for j in jobs if key(j) not in done]; t0=time.time(); lock=threading.Lock(); st=dict(stop=False,last=0,n=0,none=0); print(len(jobs),'jobs',len(todo),'todo',flush=True)
    def go(j):
        if st['stop'] or time.time()-t0>deadline: return
        with lock:
            if time.time()-st['last']>120:
                st['last']=time.time(); m=weekly()
                if m is not None and m>=GUARD: st['stop']=True; print('meter guard',m,flush=True); return
        r=fn(j); r.update({k:v for k,v in j.items() if k in('item','arm','level','rep','model','source','ver')})
        with lock:
            with open(outf,'a') as w: w.write(json.dumps(r)+'\n')
            st['n']+=1; st['none']+=r.get('score') is None
    with X.ThreadPoolExecutor(5) as ex: list(ex.map(go,todo))
    left=0; done=set()
    for l in open(outf) if os.path.exists(outf) else []:
        r=json.loads(l)
        if r.get('score') is not None: done.add(key(r))
    left=sum(key(j) not in done for j in jobs); print('ran',st['n'],'unscored',st['none'],'left',left,'stopped',st['stop'],'secs',round(time.time()-t0),'meter',weekly(),flush=True)
    return left
def transcript_excerpt(path,cap=12000):
    """Worker's own session: assistant text, tool names and short inputs, short results; no prompts. Scrub and leak filter on every line, DROP lines removed, last cap chars."""
    out=[]
    for l in open(path,errors='replace'):
        try: d=json.loads(l)
        except Exception: continue
        c=(d.get('message') or {}).get('content')
        if d.get('type')=='assistant' and isinstance(c,list):
            for x in c:
                if x.get('type')=='text': out.append(x.get('text',''))
                elif x.get('type')=='tool_use': out.append(f"[{x.get('name')}] {json.dumps(x.get('input'))[:200]}")
        elif d.get('type')=='user' and isinstance(c,list):
            for x in c:
                if isinstance(x,dict) and x.get('type')=='tool_result':
                    t=x.get('content'); t=t if isinstance(t,str) else ' '.join(y.get('text','') for y in t or [] if isinstance(y,dict))
                    out.append('-> '+t[:300])
    lines=[]
    for t in out:
        for ln in t.splitlines():
            if not ln.strip() or DROP.search(ln): continue
            u=unleak(scrub(ln))
            if u: lines.append(u)
    return '\n'.join(lines)[-cap:]
