"""Supplemental audit for retained public compressed pages and native streams."""
import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'artifacts/phase-8/8a'
GATE = ROOT / 'artifacts/phase-8/gate'
KEY = re.compile(r'\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16})\b')
failures = []
streams = compressed = files = 0
for folder in (OUT, GATE / 'web-fixtures', GATE / 'provider-fixtures'):
    for path in folder.rglob('*'):
        if not path.is_file() or path.name == 'public-evidence-audit.json':
            continue
        files += 1
        data = path.read_bytes()
        if path.suffix == '.gz':
            data = gzip.decompress(data)
            compressed += 1
        if path.suffix == '.ndjson':
            streams += 1
            for line in data.decode().splitlines():
                json.loads(line)
        if KEY.search(data.decode(errors='replace')):
            failures.append(str(path.relative_to(ROOT)))
frozen = json.loads((GATE / 'frozen-inputs.json').read_text())['files']
protected = [name for name in frozen if name in {
    'server/evals/research/cases.yaml', 'server/evals/research/probe_cases.json',
    'server/evals/research/tools.json', 'server/evals/web/run_eval.py',
    'server/evals/web/cases.yaml', 'server/pyproject.toml', 'server/uv.lock',
    'web/package.json', 'web/package-lock.json'
} or name.startswith('server/app/search/') and name.endswith('.py')]
mismatches = [name for name in protected if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != frozen[name]]
pages = json.loads((GATE / 'web-fixtures/pages-manifest.json').read_text())
for page in pages:
    data = gzip.decompress((GATE / 'web-fixtures' / page['file']).read_bytes())
    assert hashlib.sha256(data).hexdigest() == page['sha256']
result = {'files': files, 'compressed_files_checked': compressed, 'native_streams_checked': streams,
          'original_public_page_hashes_verified': len(pages), 'protected_inputs_checked': len(protected),
          'protected_input_mismatches': mismatches, 'key_shaped_findings': failures,
          'limits': 'Collection boundary is authored synthetic prompts/public pages; scanner cannot certify privacy or provenance. Images separately reviewed. No private-marker corpus read.'}
(OUT/'public-evidence-audit.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
assert not failures and not mismatches and streams == 280
