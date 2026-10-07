"""Offline diagnostic for retained public selector output; no inference or regrading."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'server'))
from app.runs.research_output import EvidenceOutput, dates, literal
from app.schemas import Source

folder = ROOT / 'artifacts/phase-8/8a/consistency' / sys.argv[1]
result = []
for path in sorted(folder.glob('*.json')):
    data = json.loads(path.read_text())
    if 'captured_requests' not in data:
        continue
    request = data['captured_requests'][-1]
    question = next(m['content'] for m in data['captured_requests'][0]['messages'] if m['role'] == 'user')
    renderer = EvidenceOutput(question, [Source.model_validate(s) for s in data['sources']])
    raw = ''.join(e.get('text', '') for e in data['provider_events'][-1] if e.get('type') == 'TextDelta')
    match = re.match(r'\s*\{\s*"rows"\s*:\s*\[', raw)
    rows = []
    if match:
        offset = match.end()
        while offset < len(raw):
            offset += len(raw[offset:]) - len(raw[offset:].lstrip(' \n\r\t,'))
            try:
                row, offset = json.JSONDecoder().raw_decode(raw, offset)
            except ValueError:
                break
            selected = [renderer.units[k] for k in row.get('evidence', []) if k in renderer.units]
            text = '\n'.join(u.heading + '\n' + u.text for u in selected)
            try:
                renderer.render(row)
                valid = True
            except Exception:
                valid = False
            rows.append({'row': row, 'host_valid': valid,
                         'label_offered': row.get('label') in renderer.labels,
                         'value_literal': literal(row['value'], text) if row.get('value') else None,
                         'supported_dates': sorted(dates(text)),
                         'selected_quotes': [u.text for u in selected]})
    result.append({'case': data['id'], 'status': data['status'], 'raw_complete': data['required_facts'],
                   'raw_stream_complete_json': bool(raw.strip().endswith('}')), 'rows': rows,
                   'interpretation': 'Literal provenance diagnostic only; entailment, binding and omissions require manual review.'})
print(json.dumps(result, indent=2, ensure_ascii=False))
