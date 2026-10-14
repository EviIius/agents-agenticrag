"""Isolated trial listener; captures only its own synthetic Ollama traffic."""
import asyncio
import hashlib
import json
import os
import subprocess
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'server'))
import httpx
import uvicorn
from app.config import Settings
from app.main import create_app
from app.db import connections, settings
from app.schemas import ConnectionCreate

MODEL='qwen3:30b-a3b-workbench-32k'
DATA=Path(os.environ['ATELIER_TRIAL_DATA']).resolve()
assert DATA.is_relative_to(Path.home()/'.local/share/workbench/qa')
assert not (DATA/'workbench.db').exists(), 'Never reuse a trial database'
app=create_app(Settings(data_dir=DATA,dev=True,log_level='WARNING',legacy_db=DATA/'missing-legacy.db',transcribe_home=DATA/'unavailable-transcriber',image_home=DATA/'unavailable-image-worker'))
original=app.router.lifespan_context
captures=[]
started=None

def write(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def runtime_processes():
    listener=subprocess.run(['lsof','-nP','-t','-iTCP:11434','-sTCP:LISTEN'],capture_output=True,text=True,check=True)
    roots={int(line) for line in listener.stdout.splitlines() if line.strip()}
    assert roots, 'Runtime listener PID unavailable'
    rows=[]
    table=subprocess.check_output(['ps','-A','-o','pid=,ppid=,rss=,comm='],text=True)
    for line in table.splitlines():
        parts=line.strip().split(None,3)
        if len(parts)==4:
            rows.append({'pid':int(parts[0]),'ppid':int(parts[1]),'rss_kib':int(parts[2]),'executable':parts[3]})
    chosen=set(roots)
    while True:
        more={r['pid'] for r in rows if r['ppid'] in chosen}
        if more.issubset(chosen):break
        chosen.update(more)
    selected=[r for r in rows if r['pid'] in chosen]
    assert selected and all(pid in {r['pid'] for r in selected} for pid in roots), 'Runtime RSS unavailable'
    return selected

def memory():
    return {'swap':subprocess.check_output(['sysctl','-n','vm.swapusage'],text=True).strip(),
            'vm':subprocess.check_output(['vm_stat'],text=True).strip(),
            'runtime_processes':runtime_processes(),
            'rss_scope':'CPU process RSS in KiB for listener and descendants; not a unified-memory/GPU allocation measurement'}

class ObservedStream(httpx.AsyncByteStream):
    def __init__(self,inner,index):self.inner=inner;self.index=index;self.buffer=b"";self.ended=False
    async def __aiter__(self):
        with (OUT/f'call-{self.index:02d}-response.ndjson').open('ab') as file:
            async for chunk in self.inner:
                file.write(chunk);file.flush()
                record=captures[self.index-1]
                dirty=False
                if 'first_byte_at' not in record:record['first_byte_at']=time.time();dirty=True
                self.buffer+=chunk
                while b'\n' in self.buffer:
                    line,self.buffer=self.buffer.split(b'\n',1)
                    if not line.strip():continue
                    part=json.loads(line)
                    message=part.get('message',{})
                    if message.get('content') and 'first_content_at' not in record:record['first_content_at']=time.time();dirty=True
                    if message.get('thinking') and 'first_reasoning_at' not in record:record['first_reasoning_at']=time.time();dirty=True
                    if part.get('done'):
                        record['done_at']=time.time();record['runtime_finish']=part;self.ended=True;dirty=True
                if dirty:write('requests.json',captures)
                if started is not None and time.monotonic()-started>180:raise TimeoutError('Three-minute inference bound reached')
                yield chunk
    async def aclose(self):
        error=None
        try:
            await self.inner.aclose()
        except BaseException as exc:
            error=type(exc).__name__
            raise
        finally:
            record=captures[self.index-1]
            record.setdefault('closed_at',time.time());record['completed_stream']=self.ended
            record['close_error']=error
            write('requests.json',captures)

class TrialTransport(httpx.AsyncBaseTransport):
    def __init__(self):self.inner=httpx.AsyncHTTPTransport()
    async def handle_async_request(self,request):
        global started
        assert request.url.host=='127.0.0.1' and request.url.port==11434
        if request.url.path!='/api/chat':
            assert request.url.path in {'/api/show','/api/tags','/api/ps','/api/version'}
            return await self.inner.handle_async_request(request)
        if started is None:started=time.monotonic()
        assert time.monotonic()-started<180,'Three-minute inference bound reached'
        assert len(captures)<2,'Two-call bound reached'
        # Do not run concurrently with a native image worker.
        active=subprocess.run(['pgrep','-f','[m]flux.*(generate|workbench_image)'],capture_output=True,text=True)
        assert not active.stdout.strip(),'Image worker is active'
        body=json.loads(request.content)
        assert body['model']==MODEL and len(body['messages'])==2 and body['messages'][0]['role']=='system' and body['messages'][1]['role']=='user'
        assert body.get('stream') is True and not body.get('tools') and not body.get('format')
        index=len(captures)+1
        record={'index':index,'at':time.time(),'elapsed':time.monotonic()-started,'body':body,'body_sha256':hashlib.sha256(request.content).hexdigest(),'memory_before':memory()}
        captures.append(record);write('requests.json',captures)
        response=await self.inner.handle_async_request(request)
        return httpx.Response(response.status_code,headers=response.headers,stream=ObservedStream(response.stream,index),extensions=response.extensions)
    async def aclose(self):await self.inner.aclose()

@asynccontextmanager
async def lifespan(server):
    async with httpx.AsyncClient(trust_env=False,timeout=20) as client:
        version=(await client.get('http://127.0.0.1:11434/api/version')).json()
        tags=(await client.get('http://127.0.0.1:11434/api/tags')).json()
        show=(await client.post('http://127.0.0.1:11434/api/show',json={'model':MODEL})).json()
        installed=(await client.get('http://127.0.0.1:8787/api/models')).json()
        configured=(await client.get('http://127.0.0.1:8787/api/connections')).json()
    selected=next(m for m in installed if m['model_id']==MODEL)
    tag=next(m for m in tags['models'] if m['name']==MODEL)
    current_connection=next(c for c in configured if c['id']==selected['connection_id'])
    assert current_connection['base_url'].rstrip('/')=='http://127.0.0.1:11434'
    assert selected['chat_capable'] and selected['context_length']==32768 and 'completion' in show['capabilities']
    metadata={'model_id':MODEL,'digest':tag['digest'],'version':version,'capabilities':show['capabilities'],'parameters':show.get('parameters'),'context_length':selected['context_length'],'saved_model_defaults':selected['params_defaults'],'keep_alive':current_connection['keep_alive'],'loaded_before':selected['loaded'],'data_dir':str(DATA),'memory_before':memory()}
    write('runtime-metadata.json',metadata)
    async with original(server):
        conn=await connections.create(server.state.store,ConnectionCreate(name='Isolated native trial',base_url='http://127.0.0.1:11434'))
        await settings.patch(server.state.store,{'auto_title':False})
        await server.state.store.execute('UPDATE connections SET keep_alive=? WHERE id=?',(current_connection['keep_alive'],conn.id))
        if selected['params_defaults']:
            await server.state.store.execute('INSERT INTO model_prefs(connection_id,model_id,params_json) VALUES(?,?,?)',(conn.id,MODEL,json.dumps(selected['params_defaults'])))
        adapter=await server.state.registry.adapter(conn.id)
        await adapter.client.aclose()
        adapter.client=httpx.AsyncClient(transport=TrialTransport(),timeout=httpx.Timeout(300,connect=5),trust_env=False)
        server.state.trial_connection=conn.id
        write('host-ready.json',{'connection_id':conn.id,'model_id':MODEL,'data_dir':str(DATA),'native_calls':0})
        try:yield
        finally:
            rows=await server.state.store.rows('SELECT * FROM workflow_graph_attempts ORDER BY rowid')
            write('durable-attempts.json',rows)
            write('host-closeout.json',{'elapsed_seconds':time.monotonic()-started if started else 0,'native_calls':len(captures),'memory_after':memory(),'data_dir':str(DATA),'no_native_images':True})
app.router.lifespan_context=lifespan

@app.get('/trial/status')
async def status():
    return {'native_calls':len(captures),'elapsed':time.monotonic()-started if started else 0,'connection_id':app.state.trial_connection,'model_id':MODEL,'capacity_busy':app.state.capacity.busy}

# Trial metadata must precede the existing SPA catch-all.
app.router.routes.insert(0, app.router.routes.pop())

if __name__=='__main__':uvicorn.run(app,host='127.0.0.1',port=18787,log_level='warning')
