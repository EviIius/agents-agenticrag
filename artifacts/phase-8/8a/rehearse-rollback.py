"""Rehearse schema 8 -> 9 -> restored schema 8 using synthetic data only."""
import hashlib
import json
import shutil
import sqlite3
import subprocess
import tarfile
import tempfile
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/phase-8/8a"
PYTHON = ROOT / "server/.venv/bin/python"


def hashes(dbfile):
    with sqlite3.connect(dbfile) as db:
        return {name: hashlib.sha256(repr(sorted(db.execute('SELECT * FROM "'+name+'"').fetchall(),key=repr)).encode()).hexdigest()
                for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}


def boot(source, data):
    code = '''import asyncio,json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import httpx
from app.config import Settings
from app.main import create_app
async def main():
 app=create_app(Settings(data_dir=Path(sys.argv[2]),transcribe_home=None,log_level='CRITICAL'),static_dir=Path(sys.argv[3]))
 async with app.router.lifespan_context(app):
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost') as client:
   health=await client.get('/api/health')
   shell=await client.get('/')
   version=await app.state.store.one('PRAGMA user_version')
   print(json.dumps({'health':health.status_code,'shell':shell.status_code,'schema':version['user_version']}))
asyncio.run(main())'''
    result = subprocess.run([str(PYTHON),'-c',code,str(source/'server'),str(data),str(ROOT/'server/app/static')],capture_output=True,text=True)
    if result.returncode:
        raise RuntimeError('Synthetic rollback boot failed: '+result.stderr[-500:])
    return json.loads(result.stdout)


def main():
    clock=monotonic()
    with tempfile.TemporaryDirectory(prefix='workbench-research-rollback-') as directory:
        temp=Path(directory);old=temp/'previous';old.mkdir();data=temp/'data';data.mkdir()
        archive=temp/'source.tar'
        with archive.open('wb') as file:
            subprocess.run(['git','archive','d74067e'],cwd=ROOT,stdout=file,check=True)
        with tarfile.open(archive) as file:
            file.extractall(old,filter='data')
        shutil.copy2(ROOT/'server/tests/fixtures/db/phase3.db',data/'workbench.db')
        prior=boot(old,data)
        backup=temp/'backup.db'
        with sqlite3.connect(data/'workbench.db') as db, sqlite3.connect(backup) as dest:
            db.backup(dest)
        before=hashes(backup)
        upgraded=boot(ROOT,data)
        with sqlite3.connect(data/'workbench.db') as db:
            assert db.execute('SELECT COUNT(*) FROM chats WHERE research_enabled!=0').fetchone()[0]==0
            assert db.execute('SELECT COUNT(*) FROM messages WHERE research_json IS NOT NULL OR activity_json IS NOT NULL').fetchone()[0]==0
            db.execute('UPDATE chats SET research_enabled=1')
            db.commit()
        for suffix in ('','-wal','-shm'):
            (data/('workbench.db'+suffix)).unlink(missing_ok=True)
        shutil.copy2(backup,data/'workbench.db')
        restored=boot(old,data)
        equal=before==hashes(data/'workbench.db')
        assert prior['schema']==restored['schema']==8 and upgraded['schema']==9
        print(json.dumps({'prior':prior,'upgraded':upgraded,'restored':restored,'equal':equal,'changed_tables':[k for k,v in before.items() if hashes(data/'workbench.db').get(k)!=v]},indent=2),flush=True)
        assert all(x['health']==x['shell']==200 for x in (prior,upgraded,restored)) and equal
    result={'previous_commit':'d74067e','prior':prior,'upgraded':upgraded,'restored':restored,
            'old_row_hashes_identical':equal,'seconds':monotonic()-clock,'synthetic_only':True,
            'production_data_read_or_modified':False,'temporary_copy_removed':True}
    (OUT/'rollback.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
