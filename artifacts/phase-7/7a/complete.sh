#!/bin/sh
set -eu
cd /Users/evilius/Documents/GitHub/agents-agenticrag
sh /tmp/workbench-7a-full-browser.sh
/Users/evilius/.local/share/workbench/tools/library-probe/development/.venv/bin/python /tmp/workbench-7a-deploy.py > artifacts/phase-7/7a/deployment.txt 2>&1
python3 /tmp/workbench-7a-preserve-evidence.py
