"""Synthetic schema-14 lifecycle/retry rehearsals. All network/model work blocked."""

import asyncio
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tarfile
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PRIVATE = Path.home() / ".local/share/workbench/qa/photo-editing-pe1-c-prep-20261020"
sys.path.insert(0, str(ROOT / "server"))

import httpx

from app.config import Settings
from app.main import create_app
from tests.test_photo_references import EditFake


def snapshot(path):
    with sqlite3.connect(path) as db:
        return {name: {"columns": [row[1] for row in db.execute(f'PRAGMA table_info("{name}")')],
                       "rows": sorted([list(row) for row in db.execute(f'SELECT * FROM "{name}"')], key=repr)}
                for name, in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}


def immutable(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for name in ["image-references", "images"] for p in (path / name).rglob("*")
            if p.is_file() and p.name in {"original", "reference.png", "reference.json", "input.json", "image.png", "metadata.json", "export.png"}}


async def seed(data):
    shutil.copytree(PRIVATE / "cpu-data", data)
    app = create_app(Settings(data_dir=data, dev=True, image_home=None,
                              transcribe_home=None, legacy_db=PRIVATE / "missing.db"))
    ids = {}
    async with app.router.lifespan_context(app), httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://localhost") as client:
        ref = await app.state.store.one("SELECT * FROM image_references ORDER BY id LIMIT 1")
        async def accept(label):
            response = await client.post(f"/api/chats/{ref['chat_id']}/images", json={"request_key": uuid4().hex,
                "prompt": "Synthetic rollback " + label, "count": 1, "seeds": [42], "reference_id": ref["id"]})
            assert response.status_code == 202, response.text
            body = response.json()
            ids[label] = {"chat": ref["chat_id"], "message": body["assistant"]["id"], "job": body["assistant"]["images"][0]["id"]}
        engine = EditFake(); engine.release.set(); app.state.images.engine = engine
        await accept("complete")
        await asyncio.gather(*list(app.state.images.tasks.values()))
        assert (await app.state.images.get(ids["complete"]["job"])).state == "complete"
        engine.fail = True
        await accept("failed")
        await asyncio.gather(*list(app.state.images.tasks.values()))
        assert (await app.state.images.get(ids["failed"]["job"])).state == "failed"
        engine.fail = False; engine.release.clear()
        await accept("cancelled")
        await client.post(f"/api/images/jobs/{ids['cancelled']['job']}/cancel", json={})
        await accept("queued")
    # Model the accepted-before-execution crash point after the fake worker is reaped.
    with sqlite3.connect(data / "workbench.db") as db:
        db.execute("UPDATE image_jobs SET state='queued',stage='Queued' WHERE id=?", (ids["queued"]["job"],))
        db.commit()
    return ids


CHILD = r'''
import asyncio,json,sys,socket
from pathlib import Path
from uuid import uuid4
def blocked(*a,**k):raise RuntimeError('Network forbidden in synthetic rollback rehearsal')
socket.socket.connect=blocked;socket.socket.connect_ex=blocked
sys.path.insert(0,sys.argv[1]+'/server')
import httpx
from app.config import Settings
from app.main import create_app
from app.schemas import ImageStatus
calls=[]
class Capture:
 def status(self):return ImageStatus(available=True,**({'editing_available':True} if sys.argv[4]!='old' else {}))
 async def run(self,manifest,scratch,progress):
  spec=json.loads(manifest.read_text());calls.append({'method':'plain_generation','keys':sorted(spec),'has_reference': 'reference' in spec});raise ValueError('Synthetic capture; no worker')
 async def run_edit(self,manifest,scratch,progress):
  spec=json.loads(manifest.read_text());assert (manifest.parent/'inputs/original').is_file();calls.append({'method':'pixel_edit','keys':sorted(spec),'has_reference':'reference' in spec});raise ValueError('Synthetic capture; no worker')
async def main():
 data=Path(sys.argv[2]);ids=json.loads(Path(sys.argv[3]).read_text())
 app=create_app(Settings(data_dir=data,dev=False,image_home=None,transcribe_home=None,legacy_db=data/'missing.db',allowed_hosts=''))
 async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://localhost') as client:
  assert (await client.get('/api/health')).json()['ok']
  assert (await app.state.store.one('PRAGMA user_version'))['user_version']==14
  queued=await app.state.images.get(ids['queued']['job']);assert queued.state=='interrupted'
  assert (await client.get('/api/images/jobs/'+ids['complete']['job']+'/output/png')).status_code==200
  app.state.images.engine=Capture()
  old=ids['complete']
  response=await client.post('/api/chats/'+old['chat']+'/messages/'+old['message']+'/images/retry',json={'request_key':uuid4().hex,'seeds':[43]})
  assert response.status_code==202,response.text
  await asyncio.gather(*list(app.state.images.tasks.values()))
  assert len(calls)==1
  refs=await app.state.store.rows('SELECT * FROM image_job_references')
  result={'application_started':True,'schema':14,'queued_edit_quiesced':True,'retry':calls[0],'reference_pins':len(refs),'native_calls':0,'network_blocked':True}
 print(json.dumps(result))
asyncio.run(main())
'''


def main():
    attempt = sys.argv[1] if len(sys.argv) > 1 else "initial"
    if not attempt.isalnum():
        raise ValueError("Simple recorded attempt label required")
    seed_dir = PRIVATE / "rollback-seed"
    if seed_dir.exists():
        ids = json.loads((PRIVATE / "rollback-ids.json").read_text())
    else:
        ids = asyncio.run(seed(seed_dir))
    ids_file = PRIVATE / "rollback-ids.json"
    ids_file.write_text(json.dumps(ids))
    old = PRIVATE / "previous-source"
    old.mkdir(mode=0o700, exist_ok=True)
    archive = PRIVATE / "previous-source.tar"
    subprocess.run(["git", "archive", "--format=tar", "-o", str(archive), "c0d65ee0", "server/app", "shared"], cwd=ROOT, check=True)
    with tarfile.open(archive) as bundle:
        bundle.extractall(old, filter="data")
    before = snapshot(seed_dir / "workbench.db")
    files = immutable(seed_dir)
    results = []
    for label, source in [("old", old), ("candidate", ROOT)]:
        data = PRIVATE / ("rollback-" + label + "-" + attempt)
        shutil.copytree(seed_dir, data)
        result = subprocess.run([sys.executable, "-c", CHILD, str(source), str(data), str(ids_file), label],
                                cwd=source / "server", capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=30)
        (OUT / ("rollback-" + label + "-" + attempt + ".txt")).write_bytes(result.stdout + result.stderr)
        assert result.returncode == 0, result.stderr.decode()
        observed = json.loads(result.stdout)
        after = snapshot(data / "workbench.db")
        # Retries intentionally add rows; every original nonvolatile row stays.
        preserved = 0
        for table, item in before.items():
            if table in {"image_jobs", "image_events", "chats", "settings", "meta"} or table.startswith(("messages_fts", "chats_fts", "message_search", "chat_search")):
                continue
            assert item["columns"] == after[table]["columns"], table
            assert all(row in after[table]["rows"] for row in item["rows"]), table
            preserved += 1
        domain_rows = {}
        for table, mutable in [("chats", {"updated_at", "current_leaf_id"}),
                               ("image_jobs", {"state", "stage", "updated_at", "error_code", "error_message"})]:
            columns = before[table]["columns"]
            identity = columns.index("id")
            original = {row[identity]: row for row in before[table]["rows"]}
            present = {row[identity]: row for row in after[table]["rows"]}
            for key, row in original.items():
                assert key in present, (table, key)
                for index, column in enumerate(columns):
                    if column not in mutable:
                        assert row[index] == present[key][index], (table, column)
            domain_rows[table] = {"original_rows": len(original),
                                  "immutable_columns_preserved": [c for c in columns if c not in mutable],
                                  "allowed_lifecycle_columns": sorted(mutable)}
        for name, digest in files.items():
            assert hashlib.sha256((data / name).read_bytes()).hexdigest() == digest
        observed.update(label=label, original_tables_with_row_subset_preserved=preserved,
                        immutable_reference_output_files=len(files), immutable_files_preserved=True, domain_projection=domain_rows)
        results.append(observed)
    assert results[0]["retry"]["method"] == "plain_generation" and not results[0]["retry"]["has_reference"]
    assert results[1]["retry"]["method"] == "pixel_edit" and results[1]["retry"]["has_reference"]
    summary = {"completed": True, "native_calls": 0, "synthetic_data_only": True, "cases": results,
               "old_binary_rollback_safe": False,
               "reason": "Previous schema-13 server starts on schema 14 but its image retry drops the reference and selects ordinary generation.",
               "candidate_backend_retains_reference_on_retry": True,
               "next": "Use a schema-14-aware compatibility backend for rollback; verify previous UI against it before release."}
    (OUT / "rollback.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"native_calls": 0, "old_binary_rollback_safe": False, "candidate_retry_preserves_pixels": True}))


main()
