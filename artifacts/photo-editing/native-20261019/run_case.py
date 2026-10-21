"""One explicitly approved PE0 attempt. No automatic next case, retry or model load."""
import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx

SOURCE=Path(os.environ['AETHER_PE0_SOURCE']).resolve()
OUT=SOURCE/'artifacts/photo-editing/native-20261019'
ROOT=Path.home()/'.local/share/workbench/qa/photo-editing-pe0-prep-20261019'
BASE=Path.home()/'.local/share/workbench'
sys.path[:0]=[str(ROOT/'worker'),str(SOURCE/'server')]
from app.capacity import Capacity
from controller import EditEngine, run_case

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def write_new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())


def preflight():
    frozen=json.loads((OUT/'execution-manifest.json').read_text())['files']
    assert all(sha(SOURCE/name)==digest for name,digest in frozen.items())
    prep=json.loads((SOURCE/'artifacts/photo-editing/prep-20261019/private-preparation.json').read_text())
    assert all(sha(ROOT/'worker'/name)==digest for name,digest in prep['source_copies'].items())
    assert all(sha(ROOT/'worker'/name)==sha(BASE/'image-worker/product'/name)==digest for name,digest in prep['existing_selectors'].items())
    with httpx.Client(timeout=5,trust_env=False) as client:
        version=client.get('http://127.0.0.1:11434/api/version');version.raise_for_status()
        assert version.json()=={'version':'0.35.0'}
        active=client.get('http://127.0.0.1:8787/api/runs/active');active.raise_for_status()
        if active.json(): raise ValueError('Human chat is active; no trial worker started')
        loaded=client.get('http://127.0.0.1:11434/api/ps');loaded.raise_for_status()
        rows=loaded.json()['models']
    expected=json.loads((ROOT/'worker/trial.json').read_text())['required_chat']
    if len(rows)!=1 or rows[0].get('digest')!=expected['digest'] or rows[0].get('context_length')!=32768 or not EditEngine.qualified(rows):
        raise ValueError('Required qualified chat residency is absent; no trial worker started')
    return [{'digest':r['digest'],'context_length':r['context_length'],'resident_bytes':r['size_vram']} for r in rows]


class Measured(EditEngine):
    def __init__(self,case):
        super().__init__(ROOT/'worker',Capacity(BASE/'data/native.lock'))
        self.case=case;self.events=[];self.swaps=[];self.residency=[];self.stops=[]
        self.pid=None;self.rss=[];self.started=time.monotonic()

    async def loaded(self):
        rows=await super().loaded()
        self.residency.append({'seconds':time.monotonic()-self.started,'models':[{'digest':r.get('digest'),'context_length':r.get('context_length'),'resident_bytes':r.get('size_vram')} for r in rows]})
        return rows

    async def swap(self):
        value=await super().swap()
        self.swaps.append({'seconds':time.monotonic()-self.started,'used_mib':value})
        return value

    async def run(self,manifest,output,progress):
        async def observed(event):
            self.events.append({'seconds':time.monotonic()-self.started,**event})
            await progress(event)
        return await super().run(manifest,output,observed)

    async def stop(self,child):
        await super().stop(child)
        try: os.kill(child.pid,0);absent=False
        except ProcessLookupError: absent=True
        self.stops.append({'pid':child.pid,'exit_code':child.returncode,'worker_reaped':child.returncode is not None,'process_absent':absent,'lease_held':self.capacity.busy})
        if not absent: raise RuntimeError('Worker PID still present after reaping')

    async def sample_rss(self):
        while True:
            if self.pid:
                def sample():
                    result=subprocess.run(['/bin/ps','-o','rss=','-p',str(self.pid)],capture_output=True,text=True)
                    raw=result.stdout.strip()
                    return int(raw)*1024 if raw.isdigit() else None
                self.rss.append({'seconds':time.monotonic()-self.started,'bytes':await asyncio.to_thread(sample)})
            await asyncio.sleep(0.5)


async def main(case):
    before=preflight()
    case_folder=ROOT/'cases'/case
    log=OUT/'cases'/case
    if log.exists(): raise RuntimeError('Retained attempt exists; no retry')
    log.mkdir(parents=True)
    interpreter=Path((ROOT/'worker/.python').read_text().strip())
    stage=subprocess.run([str(interpreter),str(OUT/'stage_case.py'),str(ROOT),case],capture_output=True,text=True)
    (log/'stage.txt').write_text(stage.stdout+stage.stderr)
    if stage.returncode: raise RuntimeError('CPU staging failed; no worker started')
    write_new(log/'request.json',json.loads((case_folder/'request.json').read_text()))
    engine=Measured(case)
    original=asyncio.create_subprocess_exec
    launches=ROOT/'worker-launches.jsonl'
    async def spawning(*args,**kwargs):
        is_worker=len(args)>1 and str(args[1])==str(ROOT/'worker/worker.py')
        count=len(launches.read_text().splitlines()) if launches.exists() else 0
        if is_worker and count>=6: raise RuntimeError('Native six-invocation limit exhausted')
        child=await original(*args,**kwargs)
        if is_worker:
            engine.pid=child.pid
            with launches.open('a') as stream:
                stream.write(json.dumps({'case':case,'pid':child.pid,'ordinal':count+1,'worker_sha256':sha(ROOT/'worker/worker.py')})+'\n');stream.flush();os.fsync(stream.fileno())
        return child
    asyncio.create_subprocess_exec=spawning
    sampler=asyncio.create_task(engine.sample_rss())
    result=None;failure=None
    try:
        result=await run_case(ROOT,case,engine)
    except BaseException as error:
        failure=type(error).__name__
        raise
    finally:
        sampler.cancel();await asyncio.gather(sampler,return_exceptions=True)
        asyncio.create_subprocess_exec=original
        files={p.relative_to(case_folder).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in case_folder.rglob('*') if p.is_file()}
        record={'case':case,'result':result,'failure_type':failure,'loaded_before':before,'elapsed_seconds':time.monotonic()-engine.started,'events':engine.events,'swap_samples':engine.swaps,'residency_samples':engine.residency,'rss_samples':engine.rss,'rss_note':'0.5-second sampled process RSS, not true peak or GPU peak; native MLX peak is in worker metadata','cleanup':engine.stops,'capacity_released':not engine.capacity.busy,'storage':files,'storage_bytes':sum(v['bytes'] for v in files.values()),'total_worker_invocations':len(launches.read_text().splitlines()) if launches.exists() else 0}
        write_new(log/'session.json',record)
        for filename in ('image.png','metadata.json','.image.partial.png','.metadata.partial.json'):
            file=case_folder/'output'/filename
            if file.exists(): shutil.copy2(file,log/filename)
        if launches.exists(): shutil.copy2(launches,OUT/'worker-launches.jsonl')
        outcome=ROOT/'attempts'/(case+'.result.json')
        if outcome.exists(): shutil.copy2(outcome,log/'result.json')
        print(json.dumps({'case':case,'passed':bool(result and result.get('passed')),'failure_type':failure,'worker_invocations':record['total_worker_invocations'],'elapsed_seconds':record['elapsed_seconds']}),flush=True)


if __name__=='__main__':
    case=sys.argv[1]
    if case not in {'portrait','background','clothing','mug','cancel','recovery'}: raise ValueError('Unknown frozen case')
    asyncio.run(main(case))
