from contextlib import closing
import asyncio,hashlib,json,os,shutil,sqlite3,subprocess,sys,tempfile,time
from pathlib import Path
root=Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
base=Path.home()/'.local/share/workbench'
started=time.monotonic()
with tempfile.TemporaryDirectory(prefix='workbench-7a-rollback-',dir=base/'tools') as temporary:
 private=Path(temporary);private.chmod(0o700)
 data=private/'data';shutil.copytree(base/'data',data,ignore=shutil.ignore_patterns('backups','*-wal','*-shm'))
 # Use SQLite backup so current WAL is included; never print names, text or rows.
 with closing(sqlite3.connect((base/'data/workbench.db').as_uri()+'?mode=ro',uri=True)) as original, closing(sqlite3.connect(data/'workbench.db')) as copy:
  original.backup(copy)
 backup=private/'before.db';shutil.copy2(data/'workbench.db',backup)
 with closing(sqlite3.connect(backup)) as db:
  version=db.execute('PRAGMA user_version').fetchone()[0]
  tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
  columns={t:[r[1] for r in db.execute(f'PRAGMA table_info("{t}")')] for t in tables}
 def hashes(path):
  with closing(sqlite3.connect(path)) as db:
   return {t:hashlib.sha256(repr(sorted(db.execute('SELECT '+','.join('"'+c+'"' for c in cs)+f' FROM "{t}"').fetchall(),key=repr)).encode()).hexdigest() for t,cs in columns.items()}
 before=hashes(backup)
 sys.path.insert(0,str(root/'server'))
 from app.db.core import connect
 async def migrate():
  async with connect(data) as db:
   return (await (await db.execute('PRAGMA user_version')).fetchone())[0]
 migrated=asyncio.run(migrate());assert migrated==8 and hashes(data/'workbench.db')==before
 # The complete new application starts on the copied data; no port is rebound.
 boot='''import asyncio,sys,httpx
from pathlib import Path
from app.main import create_app
from app.config import Settings
async def main():
 app=create_app(Settings(data_dir=Path(sys.argv[1]),dev=False))
 async with app.router.lifespan_context(app):
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://localhost") as client:
   assert (await client.get("/api/health")).status_code==200
asyncio.run(main())
'''
 subprocess.run([sys.executable,'-c',boot,str(data)],cwd=root/'server',check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 for suffix in ('-wal','-shm'):(data/('workbench.db'+suffix)).unlink(missing_ok=True)
 shutil.copy2(backup,data/'workbench.db');assert hashes(data/'workbench.db')==before
 previous=private/'previous';previous.mkdir()
 archive=subprocess.run(['git','archive','c1ecc2b','server/app','shared'],cwd=root,capture_output=True,check=True)
 subprocess.run(['tar','-x','-C',str(previous)],input=archive.stdout,check=True)
 subprocess.run([sys.executable,'-c',boot,str(data)],cwd=previous/'server',check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 with closing(sqlite3.connect(data/'workbench.db')) as db: restored=db.execute('PRAGMA user_version').fetchone()[0];assert restored==version
 result={'method':'private copy of current data folder; online SQLite backup; new application ASGI startup; restore backup; previous commit ASGI startup','previous_commit':'c1ecc2b','schema_before':version,'schema_after':migrated,'schema_restored':restored,'preexisting_column_hashes_unchanged':True,'web_citations_unchanged':True,'new_and_previous_health':200,'seconds':round(time.monotonic()-started,3),'private_copy_removed_on_exit':True,'real_content_logged':False,'network_model_calls':0}
(root/'artifacts/phase-7/7a/rollback.json').write_text(json.dumps(result,indent=2)+'\n')
