"""Rehearse candidate/previous application startup on copied synthetic data only."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
BASE = 'b9ef4a4c'
OUT = Path(__file__).parent


def child(root: Path, data: Path, destination: Path) -> dict:
    script = '''
import asyncio, json, sys, sqlite3
from pathlib import Path
sys.path.insert(0, sys.argv[1] + '/server')
import httpx
from app.main import create_app
from app.config import Settings
async def main():
    data=Path(sys.argv[2])
    app=create_app(Settings(data_dir=data,dev=False,image_home=None,transcribe_home=None))
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost') as client:
            health=await client.get('/api/health')
            legacy=await client.get('/api/workflows')
            assert health.status_code==200 and health.json()['ok']
            assert legacy.status_code==200 and len(legacy.json()['runs'])==1
            if hasattr(app.state,'workflow_graphs'):
                created=await client.post('/api/workflows/defs',json={'name':'Fake rollback workflow'})
                assert created.status_code==201
                run=await client.post('/api/workflows/defs/'+created.json()['id']+'/runs',json={'request_key':'fake-rollback-run','inputs':{}})
                assert run.status_code==202
                await app.state.workflow_graphs.tasks[run.json()['id']]
                assert (await app.state.workflow_graphs.get(run.json()['id'])).state=='complete'
            version=(await app.state.store.one('PRAGMA user_version'))['user_version']
            result={'health':health.json(),'legacy_runs':len(legacy.json()['runs']),'schema_version':version,'graph_engine':hasattr(app.state,'workflow_graphs')}
    Path(sys.argv[3]).write_text(json.dumps({'result':result,'openapi':app.openapi()}))
asyncio.run(main())
'''
    result = subprocess.run([sys.executable, '-c', script, str(root), str(data), str(destination)], cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return json.loads(destination.read_text())


def main() -> None:
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='fake-workflow-wsb-rollback-') as temp:
        folder=Path(temp)
        old=folder/'previous'
        old.mkdir()
        archive=folder/'previous.tar'
        with archive.open('wb') as handle:
            subprocess.run(['git','archive',BASE,'server/app','server/pyproject.toml','server/uv.lock','shared'],cwd=ROOT,stdout=handle,check=True)
        subprocess.run(['tar','-xf',str(archive),'-C',str(old)],check=True)
        data=folder/'data'
        data.mkdir(mode=0o700)
        dbpath=data/'workbench.db'
        shutil.copyfile(ROOT/'server/tests/fixtures/db/phase3.db',dbpath)
        with sqlite3.connect(dbpath) as db:
            for migration in sorted((old/'server/app/db/migrations').glob('*.sql')):
                number=int(migration.name.split('_')[0])
                if 4<number<=10:
                    db.executescript(migration.read_text()+f'\nPRAGMA user_version={number};')
            spec={'request_key':'fake-fallback-request','template':'brief_images','brief':'Fake circle','model':{'connection_id':'fake-connection','model_id':'fake-chat'},'review_prompt':False,'seeds':[42]}
            db.execute("INSERT INTO workflow_runs(id,request_key,input_json,state,stage,created_at,updated_at) VALUES('fake-fallback','fake-fallback-request',?,'complete','Ready for review','2026-10-12','2026-10-12')",(json.dumps(spec),))
            db.execute("INSERT INTO workflow_steps(run_id,position,kind,label,state,output_json) VALUES('fake-fallback',0,'prompt','Fake draft','complete','{\"text\":\"Fake circle\"}')")
            db.commit()
            with sqlite3.connect(folder/'before.db') as backup:
                db.backup(backup)
        before_hash=hashlib.sha256((folder/'before.db').read_bytes()).hexdigest()
        current=child(ROOT,data,folder/'current.json')
        assert current['result']['schema_version']==11 and current['result']['graph_engine']
        # Restore the backup as a whole; do not attempt a reverse migration.
        shutil.rmtree(data)
        data.mkdir(mode=0o700)
        shutil.copyfile(folder/'before.db',dbpath)
        restored_hash=hashlib.sha256(dbpath.read_bytes()).hexdigest()
        assert restored_hash==before_hash
        previous=child(old,data,folder/'previous.json')
        assert previous['result']['schema_version']==10 and not previous['result']['graph_engine']
        sys.path.insert(0,str(ROOT/'scripts'))
        from check_api_additive import compare
        errors=compare(previous['openapi'],current['openapi'])
        assert not errors, errors
        output={'baseline':BASE,'synthetic_only':True,'candidate':current['result'],'restored_previous':previous['result'],'backup_sha256':before_hash,'restored_sha256':restored_hash,'api_errors':errors,'seconds':round(time.monotonic()-start,3),'commands':['git archive b9ef4a4c server/app server/pyproject.toml server/uv.lock shared','create a copied synthetic v10 data folder and SQLite backup','start candidate app lifecycle; check health, legacy list and a blank graph run','restore whole copied backup','start previous application source; check health, legacy list and schema v10','compare previous/current complete OpenAPI contracts'],'live_service_changed':False}
        (OUT/'rollback-api.json').write_text(json.dumps(output,indent=2)+'\n')
        (OUT/'openapi-previous.json').write_text(json.dumps(previous['openapi'],indent=2)+'\n')
        (OUT/'openapi-candidate.json').write_text(json.dumps(current['openapi'],indent=2)+'\n')
        print(json.dumps(output,indent=2))


if __name__=='__main__':
    main()
