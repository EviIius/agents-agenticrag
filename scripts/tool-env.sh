#!/bin/sh
# Prefer standard tools; fall back to the isolated build tools on this Mac.
WORKBENCH_TOOLS_DIR="${WORKBENCH_TOOLS_DIR:-$HOME/.local/share/workbench/tools}"
if [ -d "$WORKBENCH_TOOLS_DIR/bin" ]; then
  PATH="$WORKBENCH_TOOLS_DIR/bin:$PATH"
fi
if [ -d "$WORKBENCH_TOOLS_DIR/uv/bin" ]; then
  PATH="$WORKBENCH_TOOLS_DIR/uv/bin:$PATH"
fi
export PATH
