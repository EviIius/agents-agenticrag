"""Production follow-ups: reviewed title/copy repairs, private fallback, unchanged service."""
import argparse
import asyncio
import gzip
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime
from contextlib import closing

ROOT = Path(os.environ['PRODUCTION_FOLLOWUPS_SOURCE']).resolve()
OUT = Path(__file__).parent
BASE = Path.home() / '.local/share/workbench'
PLIST = Path.home() / 'Library/LaunchAgents/dev.agenticrag.workbench.plist'
TAILSCALE = '/Applications/Tailscale.app/Contents/MacOS/Tailscale'
DOMAIN = f'gui/{os.getuid()}'
PYTHON = BASE / 'app/server/.venv/bin/python'
REPORT = OUT / 'result.json'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def command(args, *, cwd=None):
    result = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True)
    if result.returncode:
        # Never print copy errors that might contain user filenames.
        raise RuntimeError(f'Command failed: {Path(str(args[0])).name}, exit {result.returncode}')
    return result.stdout

def clone(source, target):
    command(['/bin/cp', '-cRp', source, target])

def database(path):
    import sqlite_vec
    db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    return db

def backup(source, target):
    target.touch(mode=0o600, exist_ok=False)
    with closing(database(source)) as db, closing(sqlite3.connect(target)) as dest:
        db.backup(dest)
        dest.commit()
    target.chmod(0o600)

def projections(path, original=None):
    result = {}
    with closing(database(path)) as db:
        if original is None:
            tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            original = {t: [r[1] for r in db.execute('PRAGMA table_info("' + t + '")')] for t in tables}
        for table, columns in original.items():
            rows = db.execute('SELECT ' + ','.join('"' + c + '"' for c in columns) + ' FROM "' + table + '"')
            hashes = []
            for row in rows:
                value = json.dumps(list(row), ensure_ascii=False, separators=(',', ':'), default=lambda b: {'bytes': b.hex()})
                hashes.append(hashlib.sha256(value.encode()).hexdigest())
            digest = hashlib.sha256(''.join(sorted(hashes)).encode()).hexdigest()
            result[table] = {'rows': len(hashes), 'sha256': digest}
    if path == OUT / 'data/workbench.db':
        # SQLite may create empty WAL/SHM files even for a read-only connection.
        # Only the private durable snapshot is normalized; live journals stay intact.
        wal = path.with_name(path.name + '-wal')
        assert not wal.exists() or wal.stat().st_size == 0
        for suffix in ['-wal', '-shm']:
            path.with_name(path.name + suffix).unlink(missing_ok=True)
    return original, result

def tree(path):
    h = hashlib.sha256(); count = 0; size = 0
    for p in sorted(path.rglob('*')):
        if p.is_file() and not p.is_symlink():
            h.update(str(p.relative_to(path)).encode()); h.update(sha(p).encode())
            count += 1; size += p.stat().st_size
    return {'files': count, 'logical_bytes': size, 'sha256': h.hexdigest()}

def curl(url):
    raw = command(['/usr/bin/curl', '--silent', '--show-error', '--max-time', '15', '-w', '\n%{http_code}', url])
    body, status = raw.rsplit(b'\n', 1)
    return int(status), body

def health():
    status, body = curl('http://127.0.0.1:8787/api/health')
    return status == 200 and json.loads(body).get('ok') is True

def start():
    command(['launchctl', 'bootstrap', DOMAIN, PLIST])
    for _ in range(80):
        try:
            if health():
                return
        except (RuntimeError, ValueError):
            pass
        time.sleep(0.25)
    raise RuntimeError('Service did not become healthy')

def stop():
    command(['launchctl', 'bootout', DOMAIN, PLIST])
    for _ in range(80):
        state = subprocess.run(['launchctl', 'print', DOMAIN + '/dev.agenticrag.workbench'], capture_output=True)
        if state.returncode != 0:
            return
        time.sleep(0.1)
    raise RuntimeError('Service did not stop')

def idle():
    code, body = curl('http://127.0.0.1:8787/api/runs/active')
    if code != 200 or json.loads(body):
        raise RuntimeError('Chat generation is active; deployment stopped')
    with closing(database(BASE / 'data/workbench.db')) as db:
        for table, field, states in [
            ('image_jobs', 'state', ['queued', 'preparing', 'running', 'cancelling']),
            ('workflow_runs', 'state', ['queued', 'running', 'waiting']),
            ('library_documents', 'status', ['queued', 'extracting', 'embedding']),
            ('transcripts', 'status', ['queued', 'transcribing', 'cleaning']),
        ]:
            marks = ','.join('?' for _ in states)
            if db.execute(f'SELECT count(*) FROM {table} WHERE {field} IN ({marks})', states).fetchone()[0]:
                raise RuntimeError('Background work is active; deployment stopped')

CHILD = '''
import asyncio,json,sys,socket
from pathlib import Path
def blocked(*a,**k): raise RuntimeError('Network access forbidden in copied-data rehearsal')
socket.socket.connect=blocked
socket.socket.connect_ex=blocked
sys.path.insert(0,sys.argv[1]+'/server')
import httpx
from app.main import create_app
from app.config import Settings
async def main():
 app=create_app(Settings(data_dir=Path(sys.argv[2]),dev=False,image_home=None,transcribe_home=None,allowed_hosts=''))
 async with app.router.lifespan_context(app):
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost') as client:
   assert (await client.get('/api/health')).json()['ok']
   assert (await client.get('/api/workflows')).status_code==200
   version=(await app.state.store.one('PRAGMA user_version'))['user_version']
   assert version==int(sys.argv[3])
   if version==13:
    assert (await client.get('/api/workflows/defs')).status_code==200
    assert (await client.get('/api/workflows/templates')).status_code==200
 print(json.dumps({'schema_version':version,'application_started':True,'inference_requests':0}))
asyncio.run(main())
'''

def boot_copy(app, data, version, log):
    result = subprocess.run([str(PYTHON), '-c', CHILD, str(app), str(data), str(version)], cwd=app / 'server', capture_output=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
    # The child emits no document/user text. Keep lifecycle logs private.
    log.write_bytes(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError('Copied-data lifecycle rehearsal failed')
    return json.loads(result.stdout)

def protected():
    result = {}
    for name in ['app/server/.venv', 'app/transcribe']:
        root = BASE / name
        files = [p for p in root.rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix != '.pyc']
        h = hashlib.sha256()
        for p in sorted(files):
            h.update(str(p.relative_to(root)).encode()); h.update(sha(p).encode())
        result[name] = {'files':len(files),'sha256':h.hexdigest()}
    env = plistlib.loads(PLIST.read_bytes()).get('EnvironmentVariables',{})
    worker = Path(env['WORKBENCH_IMAGE_HOME'])
    result['image_worker_controls'] = {name:sha(worker/name) for name in ['worker.py','config.json','.python']}
    return result

def candidate():
    source_path = ROOT / 'artifacts/production-followups/executed-source.json'
    build_path = ROOT / 'artifacts/production-followups/build-manifest.json'
    frozen = json.loads(source_path.read_text())['files']
    built = json.loads(build_path.read_text())['files']
    assert all(sha(ROOT/name) == digest for name, digest in frozen.items())
    static = ROOT/'server/app/static'
    assert {str(p.relative_to(static)) for p in static.rglob('*') if p.is_file()} == set(built)
    assert all(sha(static/name) == digest for name, digest in built.items())
    return {'source_manifest_sha256':sha(source_path), 'build_manifest_sha256':sha(build_path), 'source_files':len(frozen), 'build_files':len(built)}

def prepare():
    record = {'published': False, 'source_commit': command(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(), 'created_at': datetime.now(UTC).isoformat(), 'grounding_status': 'Unchanged prompts/contracts; no new factual qualification or native inference', 'native_calls': 0}
    record['candidate'] = candidate()
    frozen = json.loads((ROOT / 'artifacts/production-followups/executed-source.json').read_text())['files']
    assert all(sha(ROOT / name) == digest for name, digest in frozen.items())
    record['frozen_source_verified'] = len(frozen)
    built_manifest = json.loads((ROOT / 'artifacts/production-followups/build-manifest.json').read_text())['files']
    assert all(sha(ROOT/'server/app/static'/name)==digest for name,digest in built_manifest.items())
    service = plistlib.loads(PLIST.read_bytes())
    assert service['Label'] == 'dev.agenticrag.workbench'
    argv = service['ProgramArguments']
    assert argv[argv.index('--host') + 1] == '127.0.0.1' and argv[argv.index('--port') + 1] == '8787'
    assert argv[argv.index('--workers') + 1] == '1'
    assert sha(ROOT / 'server/uv.lock') == sha(BASE / 'app/server/uv.lock')
    assert sha(ROOT / 'server/pyproject.toml') == sha(BASE / 'app/server/pyproject.toml')
    route = command([TAILSCALE, 'serve', 'status']).decode()
    assert 'http://127.0.0.1:8787' in route
    assert health()
    idle()
    record['controller_sha256'] = sha(OUT/'release-controller.py')
    (OUT / 'route-before.txt').write_text(route)
    shutil.copy2(PLIST, OUT / 'service-before.plist')
    record['plist_sha256'] = sha(PLIST)
    record['protected_before'] = protected()
    clone(BASE / 'app', OUT / 'app')
    clone(BASE / 'data', OUT / 'data')
    # Convert the live/WAL snapshot to a durable consistent SQLite backup.
    for suffix in ['', '-wal', '-shm']:
        (OUT / 'data' / ('workbench.db' + suffix)).unlink(missing_ok=True)
    backup(BASE / 'data/workbench.db', OUT / 'data/workbench.db')
    record['app_backup'] = tree(OUT / 'app')
    record['data_backup'] = tree(OUT / 'data')
    original, rows = projections(OUT / 'data/workbench.db')
    clone(OUT / 'data', OUT / 'rehearsal-data')
    start_time = time.monotonic()
    record['candidate_rehearsal'] = boot_copy(ROOT, OUT / 'rehearsal-data', 13, OUT / 'candidate-rehearsal.log')
    _, migrated = projections(OUT / 'rehearsal-data/workbench.db', original)
    assert rows == migrated, 'Old-column projections changed on copied-data upgrade'
    shutil.rmtree(OUT / 'rehearsal-data')
    clone(OUT / 'data', OUT / 'rehearsal-data')
    restored = sha(OUT / 'rehearsal-data/workbench.db')
    assert restored == sha(OUT / 'data/workbench.db')
    record['previous_rehearsal'] = boot_copy(OUT / 'app', OUT / 'rehearsal-data', 13, OUT / 'previous-rehearsal.log')
    _, previous_rows = projections(OUT / 'rehearsal-data/workbench.db', original)
    assert previous_rows == rows, 'Previous app changed copied-data projections'
    record['rollback_rehearsal'] = {'seconds': round(time.monotonic() - start_time, 3), 'whole_data_restore_verified': True, 'database_restore_sha256': restored, 'old_tables_preserved': len(rows)}
    record['preexisting_rows'] = rows
    REPORT.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'prepared': True, 'source_files': len(frozen), 'old_tables': len(rows), 'candidate_schema': 13, 'previous_schema': 13, 'native_calls': 0}))

def verify(record):
    assert candidate() == record['candidate']
    before_route = (OUT / 'route-before.txt').read_text()
    assert command([TAILSCALE, 'serve', 'status']).decode() == before_route
    assert sha(PLIST) == record['plist_sha256']
    assert protected() == record['protected_before']
    with closing(database(BASE / 'data/workbench.db')) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 13
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
    # Old-row equality is checked while quiescent, before clients can resume.
    assert record['migration_old_rows_preserved'] is True
    target = BASE / 'app/server/app/static'
    built = ROOT / 'server/app/static'
    files = [p for p in built.rglob('*') if p.is_file()]
    assert all(sha(p) == sha(target / p.relative_to(built)) for p in files)
    server_files = [p for p in (ROOT / 'server/app').rglob('*') if p.is_file() and 'static' not in p.relative_to(ROOT / 'server/app').parts and '__pycache__' not in p.parts and p.suffix != '.pyc']
    assert all(sha(p) == sha(BASE / 'app' / p.relative_to(ROOT)) for p in server_files)
    checks = {}
    for origin in ['http://127.0.0.1:8787', 'https://jakes-mac-mini.tailc4d343.ts.net']:
        for endpoint in ['/api/health', '/api/workflows/defs', '/api/workflows/templates', '/api/images/status']:
            code, body = curl(origin + endpoint)
            assert code == 200
            if endpoint == '/api/health': assert json.loads(body)['ok']
            if endpoint == '/api/images/status': assert json.loads(body)['available']
            checks[origin + endpoint] = code
        for name in ['index.html', 'sw.js']:
            code, body = curl(origin + '/' + name)
            assert code == 200 and hashlib.sha256(body).hexdigest() == sha(built / name)
            checks[origin + '/' + name] = '200 + exact build hash'
        code, _ = curl(origin + '/design')
        assert code == 404
        checks[origin + '/design'] = code
    record.update(schema_version=13, integrity_check='ok', foreign_key_check='ok', preexisting_tables_preserved=len(record['preexisting_rows']), static_files_verified=len(files), server_files_verified=len(server_files), checks=checks, service_identity_unchanged=True, tailscale_route_unchanged=True)

def restore(record):
    subprocess.run(['launchctl', 'bootout', DOMAIN, str(PLIST)], capture_output=True)
    # Same schema: retain any accepted live messages/files on rollback.
    os.replace(BASE / 'app', OUT / 'failed-app')
    clone(OUT / 'app', BASE / 'app')
    record['rollback_kept_live_data'] = True
    shutil.copy2(OUT / 'service-before.plist', PLIST)
    start()
    record['rolled_back'] = True
    record['restored_health'] = True

def publish():
    record = json.loads(REPORT.read_text())
    assert not record['published']
    assert sha(OUT/'release-controller.py') == record['controller_sha256']
    assert candidate() == record['candidate']
    assert tree(OUT / 'app') == record['app_backup']
    assert tree(OUT / 'data') == record['data_backup']
    idle()
    down_at = time.monotonic()
    stop()
    try:
        # Refresh the complete data snapshot after the service has stopped.
        shutil.rmtree(OUT / 'data')
        clone(BASE / 'data', OUT / 'data')
        for suffix in ['', '-wal', '-shm']:
            (OUT / 'data' / ('workbench.db' + suffix)).unlink(missing_ok=True)
        backup(BASE / 'data/workbench.db', OUT / 'data/workbench.db')
        _, record['preexisting_rows'] = projections(OUT / 'data/workbench.db')
        record['data_backup'] = tree(OUT / 'data')
        record['database_backup_sha256'] = sha(OUT / 'data/workbench.db')
        REPORT.write_text(json.dumps(record, indent=2) + '\n')
        command(['rsync', '-a', '--delete', '--exclude=.venv/', '--exclude=tests/', '--exclude=evals/', '--exclude=__pycache__/', '--exclude=app/static/', str(ROOT / 'server') + '/', str(BASE / 'app/server') + '/'])
        command(['rsync', '-a', '--delete', str(ROOT / 'shared') + '/', str(BASE / 'app/shared') + '/'])
        # Keep old hashed assets for already-open clients, publish entry files last.
        built = ROOT / 'server/app/static'; target = BASE / 'app/server/app/static'
        for p in built.rglob('*'):
            if p.is_file() and p.name not in ['index.html', 'sw.js']:
                dest = target / p.relative_to(built); dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest)
        for name in ['index.html', 'sw.js']:
            shutil.copy2(built / name, target / name)
        # No schema change; no explicit migration or data rewrite.
        columns, _ = projections(OUT / 'data/workbench.db')
        _, after = projections(BASE / 'data/workbench.db', columns)
        assert after == record['preexisting_rows'], 'Old-column projections changed during migration'
        record['migration_old_rows_preserved'] = True
        start()
        record['restart_to_healthy_seconds'] = round(time.monotonic() - down_at, 3)
        verify(record)
        record.update(published=True, published_at=datetime.now(UTC).isoformat(), runtime_dependencies_unchanged=True, transcribe_and_image_workers_unchanged=True)
    except BaseException as exc:
        record['publication_error_type'] = type(exc).__name__
        restore(record)
        raise
    finally:
        REPORT.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k:record[k] for k in ['published','schema_version','preexisting_tables_preserved','server_files_verified','static_files_verified','restart_to_healthy_seconds','native_calls']}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('action', choices=['prepare', 'publish', 'verify', 'rollback'])
    action = parser.parse_args().action
    if action == 'prepare': prepare()
    elif action == 'publish': publish()
    elif action == 'verify': verify(json.loads(REPORT.read_text())); print('verified')
    else:
        record = json.loads(REPORT.read_text()); restore(record); REPORT.write_text(json.dumps(record,indent=2)+'\n'); print('restored')
