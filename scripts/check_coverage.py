"""Enforce line coverage using Python's tracer; no extra dependency is needed."""
import dis
import json
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
TARGETS = [ROOT / 'server/app' / name for name in ('providers', 'runs', 'search')]
hits: dict[str, set[int]] = {}

def trace(frame, event, arg):
    filename = frame.f_code.co_filename
    if event == 'line' and any(filename.startswith(str(folder)+'/') for folder in TARGETS):
        hits.setdefault(filename, set()).add(frame.f_lineno)
    return trace

def executable(code):
    lines = {line for _, line in dis.findlinestarts(code) if line is not None and line > 0}
    for constant in code.co_consts:
        if isinstance(constant, types.CodeType): lines |= executable(constant)
    return lines

sys.settrace(trace)
result = pytest.main(['-q', *sys.argv[1:]])
sys.settrace(None)
reports = []
failed = result != 0
for folder in TARGETS:
    total = covered = 0
    for path in sorted(folder.glob('*.py')):
        if not path.read_text().strip(): continue
        lines = executable(compile(path.read_text(), str(path), 'exec'))
        # Definition lines are executed on import; pytest can import modules before tracing
        # only when this harness itself imports them, which it intentionally never does.
        seen = hits.get(str(path), set())
        total += len(lines); covered += len(lines & seen)
        reports.append({'file':str(path.relative_to(ROOT)), 'covered':len(lines & seen),
                        'total':len(lines), 'missing':sorted(lines-seen)})
    percent=100*covered/max(total,1)
    print(f'{folder.name} line coverage: {covered}/{total} = {percent:.1f}%')
    if total and percent < 80: failed=True
output=ROOT/'artifacts/coverage.json'
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(reports,indent=2)+'\n')
raise SystemExit(1 if failed else 0)
