#!/usr/bin/env sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
VENV_PATH="$PROJECT_ROOT/.venv"

if [ ! -x "$VENV_PATH/bin/python" ]; then
  python3 -m venv "$VENV_PATH"
fi

"$VENV_PATH/bin/python" -m pip install --upgrade pip
"$VENV_PATH/bin/python" -m pip install -e "${PROJECT_ROOT}[documents]"

printf '\nAgenticRAG is ready. Start the workbench with:\n  .venv/bin/python -m agenticrag serve\n'
