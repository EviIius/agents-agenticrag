#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
. scripts/tool-env.sh
command -v uv >/dev/null || { echo 'Install uv (https://docs.astral.sh/uv/), then rerun make setup.'; exit 1; }
command -v npm >/dev/null || { echo 'Install Node >=22.12 and npm, then rerun make setup.'; exit 1; }
uv sync --directory server --locked
npm ci --prefix web
cd web
npx playwright install chromium webkit
