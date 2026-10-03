#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
. scripts/tool-env.sh
exec uv run --directory server python ../scripts/deploy.py "$@"
