#!/bin/sh
set -eu
cd /Users/evilius/Documents/GitHub/agents-agenticrag
. scripts/tool-env.sh
export UV_PROJECT_ENVIRONMENT=/Users/evilius/.local/share/workbench/tools/library-probe/development/.venv
for port in 5173 18080; do
 if lsof -t -iTCP:$port -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Test port $port occupied; stopped."
  exit 1
 fi
done
restore_service() {
 /Users/evilius/.local/share/workbench/tools/library-probe/development/.venv/bin/python - <<'PY'
import os,subprocess,time
for port,marker in ((8787,'tests.serve_app:app'),(18080,'tests.fake_runtime:app'),(5173,'agents-agenticrag/web/node_modules/.bin/vite')):
 result=subprocess.run(['lsof','-t',f'-iTCP:{port}','-sTCP:LISTEN'],capture_output=True,text=True)
 for pid in set(result.stdout.split()):
  command=subprocess.run(['ps','-p',pid,'-o','command='],capture_output=True,text=True).stdout
  cwd=subprocess.run(['lsof','-a','-p',pid,'-d','cwd','-Fn'],capture_output=True,text=True).stdout
  if marker not in command:continue
  if '/Users/evilius/Documents/GitHub/agents-agenticrag' not in cwd:continue
  try:os.kill(int(pid),15)
  except ProcessLookupError:pass
  for _ in range(50):
   try:os.kill(int(pid),0)
   except ProcessLookupError:break
   time.sleep(.1)
PY
 launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/dev.agenticrag.workbench.plist" >/dev/null 2>&1 || true
 /Users/evilius/.local/share/workbench/tools/library-probe/development/.venv/bin/python - <<'PY'
import httpx,json,time
from pathlib import Path
result={}
for _ in range(50):
 try:
  with httpx.Client(timeout=10) as client:
   result={'local':client.get('http://127.0.0.1:8787/api/health').status_code,'tailscale':client.get('https://jakes-mac-mini.tailc4d343.ts.net/api/health').status_code}
  if result=={'local':200,'tailscale':200}:break
 except httpx.HTTPError:pass
 time.sleep(.2)
result['live_interpreter']=str((Path.home()/'.local/share/workbench/app/server/.venv/bin/python').resolve())
Path('artifacts/phase-7/7b/service-restored.json').write_text(json.dumps(result,indent=2)+'\n')
assert result.get('local')==result.get('tailscale')==200
PY
}
trap restore_service EXIT HUP INT TERM
launchctl bootout "gui/$(id -u)/dev.agenticrag.workbench"
make e2e > artifacts/phase-7/7b/e2e.txt 2>&1
