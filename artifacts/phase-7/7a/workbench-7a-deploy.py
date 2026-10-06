"""Deploy the frozen 7A application with private source/database rollback."""
import hashlib
import json
import os
import plistlib
import shutil
import sqlite3
import subprocess
import time
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
BASE = Path.home() / '.local/share/workbench'
APP = BASE / 'app'
DATA = BASE / 'data'
PLIST = Path.home() / 'Library/LaunchAgents/dev.agenticrag.workbench.plist'
LABEL = f'gui/{os.getuid()}/dev.agenticrag.workbench'
TSC = '/Applications/Tailscale.app/Contents/MacOS/Tailscale'
EVIDENCE = ROOT / 'artifacts/phase-7/7a/deployment.json'
result = {'source_commit': '5f43800', 'previous_commit': 'c1ecc2b'}

def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_hashes(folder):
    return {str(p.relative_to(folder)): digest(p) for p in folder.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def stop():
    subprocess.run(['launchctl', 'bootout', LABEL], capture_output=True)
    for _ in range(100):
        if not subprocess.run(['lsof', '-t', '-iTCP:8787', '-sTCP:LISTEN'], capture_output=True).stdout:
            return
        time.sleep(.1)
    raise RuntimeError('listener did not stop')

def start():
    attempts = []
    for _ in range(3):
        p = subprocess.run(['launchctl', 'bootstrap', f'gui/{os.getuid()}', str(PLIST)],
                           capture_output=True, text=True)
        attempts.append({'returncode': p.returncode, 'stderr': p.stderr.strip()})
        for _ in range(50):
            try:
                with httpx.Client(timeout=3) as client:
                    if client.get('http://127.0.0.1:8787/api/health').status_code == 200:
                        return attempts
            except httpx.HTTPError:
                pass
            time.sleep(.2)
    result['bootstrap_attempts'] = attempts
    raise RuntimeError('service health failed')

def sync(src, dst):
    command(['rsync', '-a', '--delete', '--exclude=__pycache__/', '--exclude=*.pyc',
             str(src) + '/', str(dst) + '/'])

def backup(source, target):
    target.touch(mode=0o600)
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as db, closing(sqlite3.connect(target)) as copy:
        db.backup(copy)
    target.chmod(0o600)

def schema(path):
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        return db.execute('PRAGMA user_version').fetchone()[0]

assert json.loads((ROOT/'artifacts/phase-7/7a/service-restored.json').read_text())['local'] == 200
log = (ROOT/'artifacts/phase-7/7a/e2e.txt').read_text()
assert '417 passed' in log and '3 skipped' in log and '✘' not in log
assert json.loads(command(['python3', '/tmp/workbench-6a-source-freeze.py']).stdout) == json.loads((ROOT/'artifacts/phase-7/7a/frozen-source.json').read_text())
plist_bytes = PLIST.read_bytes()
plist = plistlib.loads(plist_bytes)
args = plist['ProgramArguments']
assert plist['Label'] == 'dev.agenticrag.workbench'
assert args[args.index('--host')+1] == '127.0.0.1'
assert args[args.index('--port')+1] == '8787'
assert args[args.index('--workers')+1] == '1'
for name in ['pyproject.toml', 'uv.lock']:
    assert (ROOT/'server'/name).read_bytes() == (APP/'server'/name).read_bytes()
engine_hash = digest(APP/'transcribe/.python')
route_hash = hashlib.sha256(command([TSC,'serve','status']).stdout.encode()).hexdigest()
stamp = datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
fallback = BASE/'tools/library-probe'/f'7a-source-fallback-{stamp}'
fallback.mkdir(mode=0o700)
shutil.copytree(APP/'server/app', fallback/'app', ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(APP/'shared', fallback/'shared')
db_backup = DATA/'backups'/f'workbench-before-library-7a-{stamp}.db'
result.update({'private_source_fallback':str(fallback), 'private_database_backup':str(db_backup),
               'plist_sha256_before':digest(PLIST), 'engine_interpreter_sha256_before':engine_hash})
stopped = False
try:
    stop()
    stopped = True
    backup(DATA/'workbench.db', db_backup)
    result['schema_before'] = schema(db_backup)
    assert result['schema_before'] == 7
    sync(ROOT/'server/app', APP/'server/app')
    sync(ROOT/'shared', APP/'shared')
    result['source_files_match'] = source_hashes(ROOT/'server/app') == source_hashes(APP/'server/app')
    assert result['source_files_match']
    result['bootstrap_attempts'] = start()
    with httpx.Client(timeout=15) as client:
        result['local_health'] = client.get('http://127.0.0.1:8787/api/health').status_code
        result['tailscale_health'] = client.get('https://jakes-mac-mini.tailc4d343.ts.net/api/health').status_code
        result['production_design_status'] = client.get('http://127.0.0.1:8787/design').status_code
        library = client.get('http://127.0.0.1:8787/api/library')
        library.raise_for_status()
        body = library.json()
        result['library_available'] = body['available']
        result['embedding_selection'] = body['embedding']
        result['transcription_ready'] = client.get('http://127.0.0.1:8787/api/transcription/status').json()['ready']
    result['schema_after'] = schema(DATA/'workbench.db')
    result['plist_unchanged'] = PLIST.read_bytes() == plist_bytes
    result['engine_interpreter_unchanged'] = digest(APP/'transcribe/.python') == engine_hash
    result['tailscale_route_unchanged'] = hashlib.sha256(command([TSC,'serve','status']).stdout.encode()).hexdigest() == route_hash
    assert result['local_health'] == result['tailscale_health'] == 200
    assert result['production_design_status'] == 404
    assert result['schema_after'] == 8
    assert result['library_available'] and result['transcription_ready']
    assert result['plist_unchanged'] and result['engine_interpreter_unchanged'] and result['tailscale_route_unchanged']
    result['status'] = 'deployed'
except BaseException as exc:
    result['failure_type'] = type(exc).__name__
    if stopped:
        stop()
        sync(fallback/'app', APP/'server/app')
        sync(fallback/'shared', APP/'shared')
        if db_backup.exists():
            for suffix in ['-wal','-shm']:
                (DATA/('workbench.db'+suffix)).unlink(missing_ok=True)
            shutil.copyfile(db_backup, DATA/'workbench.db')
            (DATA/'workbench.db').chmod(0o600)
        result['rollback_bootstrap_attempts'] = start()
        result['schema_restored'] = schema(DATA/'workbench.db')
    result['status'] = 'rolled_back'
    EVIDENCE.write_text(json.dumps(result,indent=2)+'\n')
    raise
EVIDENCE.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
