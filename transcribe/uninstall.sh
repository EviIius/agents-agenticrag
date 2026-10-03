#!/bin/bash
# Stops and removes the launchd watcher. Recordings, transcripts, models and
# Homebrew packages are left alone.
set -euo pipefail
cd "$(dirname "$0")"
bin/transcribe uninstall-agent
