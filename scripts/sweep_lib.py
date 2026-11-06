"""Shared helpers for the natural label sweep: isolated `claude -p` calls, meter guard, resumable jsonl pools."""
import json,os,re,subprocess,threading,time,concurrent.futures as F
STOP=35.0  # job line is 36: stop launching readers here
EMPTY='/tmp/sweep_empty'; os.makedirs(EMPTY,exist_ok=True)
_m={'t':0,'v':0.0,'stop':False}; _l=threading.Lock(); _w=threading.Lock()
SONNET,OPUS='claude-sonnet-5-5','claude-opus-5-5'
def weekly():
    with _l:
        if time.time()-_m['t']>45:
            try:
                o=subprocess.run(['python3','-c','from orchestrator import meter; print(meter.meters(fresh=0)["weekly"])'],cwd='ORCH_ROOT/repo',capture_output=True,text=True,timeout=60).stdout.strip()
                _m['v']=float(o); _m['stop']=_m['v']>=STOP
            except Exception: pass
            _m['t']=time.time()
        return _m['v']
def stopped():
    weekly(); return _m['stop']
def ask(model,prompt,system="You answer only from the user's message. Reply with one JSON object and nothing else.",tools='',extra=(),cwd=EMPTY,timeout=300,tries=3):
    cmd=['claude','-p','--model',model,'--system-prompt',system,'--setting-sources','','--strict-mcp-config','--no-session-persistence','--disable-slash-commands','--output-format','json','--tools',tools,*extra]
    last=''
    for a in range(tries):
        try:
            p=subprocess.run(cmd,input=prompt,capture_output=True,text=True,cwd=cwd,timeout=timeout)
            d=json.loads(p.stdout); r=d.get('result') or ''
            m=re.search(r'\{.*\}',r,re.S)
            if m: return json.loads(m.group(0)),float(d.get('total_cost_usd') or 0)
            last='noparse:'+r[:200]
        except Exception as e: last=repr(e)[:200]
        time.sleep(3+5*a)
    return {'error':last},0.0
def pool(items,fn,path,workers=8):
    """fn(item)->dict appended to path. Stops launching once the meter guard trips; reports what is unfinished."""
    cost=[0.0]; left=[]
    def run(it):
        if stopped(): left.append(it); return
        d,c=fn(it); cost[0]+=c
        with _w:
            with open(path,'a') as f: f.write(json.dumps(d)+'\n')
    with F.ThreadPoolExecutor(workers) as ex: list(ex.map(run,items))
    return cost[0],left
