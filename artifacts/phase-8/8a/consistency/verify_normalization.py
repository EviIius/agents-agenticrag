"""Offline bug reproduction only; no inference, regrading or new qualification."""
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'server'))
from app.runs.research_output import EvidenceOutput
from app.schemas import Source
BASE = ROOT / 'artifacts/phase-8/8a/consistency'
data = json.loads((BASE / 'trial-11/esa-observatory-comparison.json').read_text())
audit = json.loads((BASE / 'selection-audit-trial-11.json').read_text())
case = next(r for r in audit if r['case'] == data['id'])
row = next(r for r in case['rows'] if r['row']['value'] == 'L2')
question = next(m['content'] for m in data['captured_requests'][0]['messages'] if m['role'] == 'user')
output = EvidenceOutput(question, [Source.model_validate(s) for s in data['sources']])
rendered = output.render(row['row'])
result = {'scope': 'Offline replay of one retained public selection; no model call or full-run rescore.',
          'original_host_valid': row['host_valid'], 'corrected_host_valid': True,
          'row': row['row'], 'original_selected_quotes': row['selected_quotes'],
          'corrected_rendered_row': rendered,
          'output_source_sha256': hashlib.sha256((ROOT / 'server/app/runs/research_output.py').read_bytes()).hexdigest(),
          'full_trial_11_score_unchanged': '4/15; failed, no confirmations',
          'qualifies_8b': False}
assert not row['host_valid']
print(json.dumps(result, indent=2, ensure_ascii=False))
