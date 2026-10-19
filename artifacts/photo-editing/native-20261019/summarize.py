"""Read retained PE0 evidence and health metadata; never invoke a model."""

import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path

import httpx

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parents[2]
MAIN = Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
BASE = Path.home() / '.local/share/workbench'
PRIVATE = BASE / 'qa/photo-editing-pe0-prep-20261019'
ORDER = ('portrait', 'background', 'clothing', 'mug', 'cancel', 'recovery')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def verify(root, files):
    assert all((root / name).is_file() and sha(root / name) == digest for name, digest in files.items())
    return {'count': len(files), 'preserved': True}


def main():
    launches = [json.loads(line) for line in (PRIVATE / 'worker-launches.jsonl').read_text().splitlines()]
    assert [row['case'] for row in launches] == list(ORDER)
    assert [row['ordinal'] for row in launches] == list(range(1, 7))
    assert (OUT / 'worker-launches.jsonl').read_bytes() == (PRIVATE / 'worker-launches.jsonl').read_bytes()
    reservations = list((PRIVATE / 'attempts').glob('*.reserved.json'))
    assert len(reservations) == 6
    rows, unique_payloads = [], {}
    for case in ORDER:
        folder = OUT / 'cases' / case
        session = read(folder / 'session.json')
        assert session['failure_type'] is None and session['result']['passed'] is True
        assert session['total_worker_invocations'] == ORDER.index(case) + 1
        assert session['capacity_released'] and len(session['cleanup']) == 1
        assert all(stop['worker_reaped'] and stop['process_absent'] and stop['lease_held'] for stop in session['cleanup'])
        for name, item in session['storage'].items():
            path = PRIVATE / 'cases' / case / name
            assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes']
            if name in ('inputs/original', 'inputs/reference.png', 'output/image.png'):
                unique_payloads[item['sha256']] = item['bytes']
        spec = read(PRIVATE / 'worker/trial.json')['required_chat']
        for sample in session['residency_samples']:
            models = sample['models']
            assert len(models) == 1 and models[0]['digest'] == spec['digest']
            assert models[0]['context_length'] == 32768
            assert 0 < models[0]['resident_bytes'] <= 21827095100
        growth = max(row['used_mib'] for row in session['swap_samples']) - session['swap_samples'][0]['used_mib']
        assert growth <= 512
        row = {'case': case, 'protocol_resource_pass': True, 'total_seconds': session['elapsed_seconds'],
               'swap_growth_mib': growth, 'retained_case_bytes': session['storage_bytes'],
               'input_bytes': sum(item['bytes'] for name, item in session['storage'].items() if name in ('inputs/original', 'inputs/reference.png')),
               'reaped_before_capacity_release': True, 'qualified_32k_resident_throughout_samples': True}
        if case == 'cancel':
            assert session['result']['planned_cancellation']
            assert not list((PRIVATE / 'cases/cancel/output').iterdir())
            assert [event.get('completed_steps') for event in session['events'] if event['type'] == 'denoising'] == [0, 1]
            row.update(planned_cancellation=True, mlx_peak_bytes=None, output_bytes=0,
                       peak_note='No completed metadata emitted on cancellation; no native MLX peak claimed.')
        else:
            meta = read(folder / 'metadata.json')
            assert sha(folder / 'image.png') == meta['sha256']
            review = read(folder / 'visual-review.json')
            assert review['continue'] is True and review['output_sha256'] == meta['sha256']
            assert [event.get('completed_steps') for event in session['events'] if event['type'] == 'denoising'] == [0, 1, 2, 3, 4]
            row.update(generate_decode_seconds=meta['generate_seconds'], initialization_seconds=meta['initialization_seconds'],
                       mlx_peak_bytes=meta['mlx_peak_bytes'], cache_limit_bytes=meta['cache_limit_bytes'],
                       output_bytes=(folder / 'image.png').stat().st_size, output_sha256=meta['sha256'],
                       operator_review='Codex visual inspection; human quality acceptance pending')
        rows.append(row)

    for name in ('reference.png', 'reference.json', 'derivative.json'):
        shutil.copy2(PRIVATE / 'cases/clothing/inputs' / name, OUT / 'cases/clothing' / name)
    assert sha(SOURCE / 'artifacts/image-trial/i0/images/cold/photograph-42.png') == 'a92e224a55b36971f95e7e6bdbd160d02adb176d5d1f12c96687faaaa7e914d5'
    storage = {
        'case_directories_logical_bytes': sum(row['retained_case_bytes'] for row in rows),
        'finished_output_png_bytes': sum(row['output_bytes'] for row in rows),
        'input_original_and_working_bytes_with_per_case_duplicates': sum(row['input_bytes'] for row in rows),
        'unique_original_working_and_output_payload_bytes_by_sha256': sum(unique_payloads.values()),
        'measurement': 'File sizes after each attempt, reverified at closeout. Excludes weights, diagnostic copies and filesystem allocation/compression. Disk high-water was not sampled during native calls; do not claim a measured temporary-storage peak.',
        'revision_format': 'Every completed revision is a whole PNG, not a delta.',
    }
    write('summary.json', {'worker_invocations': 6, 'reserved_attempts': 6, 'budget_exhausted': True,
                           'cases': rows, 'storage': storage, 'human_quality_acceptance': 'pending',
                           'technical_scope': 'One frozen synthetic six-call sequence; no concurrency or arbitrary-photo qualification.'})

    frozen = read(SOURCE / 'artifacts/production-followups/executed-source.json')['files']
    static = read(SOURCE / 'artifacts/production-followups/build-manifest.json')['files']
    prep = read(SOURCE / 'artifacts/photo-editing/prep-20261019/private-preparation.json')
    result = {'production_source': verify(SOURCE, frozen), 'main_source': verify(MAIN, frozen),
              'installed_server': verify(BASE / 'app', {k: v for k, v in frozen.items() if k.startswith('server/app/')}),
              'installed_static': verify(BASE / 'app/server/app/static', static),
              'executed_source': verify(SOURCE, read(OUT / 'execution-manifest.json')['files']),
              'private_worker': verify(PRIVATE / 'worker', prep['source_copies']),
              'private_selectors': verify(PRIVATE / 'worker', prep['existing_selectors']),
              'installed_selectors': verify(BASE / 'image-worker/product', prep['existing_selectors']),
              'main_commit': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=MAIN, text=True).strip(),
              'worker_invocations': len(launches), 'reserved_attempts': len(reservations),
              'native_approval_exists': (PRIVATE / 'approval.json').is_file(),
              'stopped_trial_ledgers': {}}
    assert result['main_commit'] == 'c0d65ee02747f2834944fd6f60539b67b7d2f442'
    assert sha(SOURCE / 'image_worker/product/worker.py') == sha(BASE / 'image-worker/product/worker.py')
    prior = read(SOURCE / 'artifacts/production-followups/preservation-final.json')['stopped_trial_ledgers']
    for name, relative in [('Hermes', 'hermes-h0-20261017/native-2'), ('PydanticAI', 'pydantic-p0-20261018/native'), ('N1', 'native-agent-n1-20261018'), ('C1', 'native-agent-c1-20261018')]:
        assert sha(BASE / 'qa' / relative / 'ledger.json') == prior[name]['sha256']
        result['stopped_trial_ledgers'][name] = prior[name]
    assert subprocess.check_output(['git', 'rev-parse', 'codex/native-agent-loop'], cwd=SOURCE, text=True).strip().startswith('376205a3')
    with httpx.Client(timeout=5, trust_env=False) as client:
        for name, url in [('local', 'http://127.0.0.1:8787/api/health'), ('https', 'https://jakes-mac-mini.tailc4d343.ts.net/api/health')]:
            response = client.get(url)
            response.raise_for_status()
            assert response.json()['ok']
            result[name + '_health'] = {'ok': True, 'seconds': response.elapsed.total_seconds()}
        version = client.get('http://127.0.0.1:11434/api/version')
        version.raise_for_status()
        assert version.json() == {'version': '0.35.0'}
        result['ollama_version'] = version.json()['version']
    write('preservation-final.json', result)
    gallery(rows, storage)
    print(json.dumps({'cases': rows, 'storage': storage, 'preservation': result}, indent=2))


def gallery(rows, storage):
    pairs = [
        ('background', 'Garden background', 'cases/portrait/image.png', 'Original synthetic portrait',
         'Requested background change works. Hair/face lighting becomes warmer and fabric detail changes.'),
        ('clothing', 'Red shirt and upright reference', 'cases/clothing/reference.png', 'Normalized reference · 768 × 1024',
         'Shirt becomes red. Square output reconstructs framing; skin, contrast and fabric detail also change.'),
        ('mug', 'Green mug', '../../image-trial/i0/images/cold/photograph-42.png', 'Retained original synthetic scene',
         'Mug becomes green. Notebook, framing and scene closely align; fine texture/highlights still differ.'),
        ('recovery', 'Recovery after cancellation', 'cases/portrait/image.png', 'Original synthetic portrait',
         'Scheduled recovery completes with the same decoded pixels as the earlier garden edit; PNG metadata/file hashes differ. The lighting and fabric drift recur.'),
    ]
    sections = []
    by_case = {row['case']: row for row in rows}
    for case, title, original, label, note in pairs:
        row = by_case[case]
        prompt = read(OUT / 'cases' / case / 'request.json')['prompt']
        sections.append(f'''<section><h2>{html.escape(title)}</h2><p>{html.escape(note)}</p>
<div class="pair"><figure><a href="{original}"><img src="{original}" alt="{html.escape(label)}"></a><figcaption>{html.escape(label)}</figcaption></figure>
<figure><a href="cases/{case}/image.png"><img src="cases/{case}/image.png" alt="{html.escape(title)} result"></a><figcaption>Edited · 1024 × 1024 · {row['generate_decode_seconds']:.1f} s · {row['output_bytes']/1e6:.2f} MB PNG</figcaption></figure></div>
<details><summary>Exact edit request</summary><p>{html.escape(prompt)}</p></details></section>''')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PE0 photo-reference trial · 19 October 2026</title><style>
*{box-sizing:border-box}body{margin:0;background:#191a1c;color:#efefef;font:16px/1.55 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:28px 20px 64px}h1{font-size:clamp(26px,4vw,40px);line-height:1.2}h2{margin:0 0 8px}p{max-width:90ch;color:#cbccd1}.note{border-left:4px solid #91a9ff;padding:12px 20px;background:#24262d}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img{display:block;width:100%;height:auto;aspect-ratio:1;object-fit:contain;background:#101113;border-radius:8px}figcaption{font-size:14px;padding:8px 0;color:#c7c9d1}section{margin:38px 0;padding-top:22px;border-top:1px solid #494b52}a{color:#a8bcff}summary{cursor:pointer;color:#a8bcff}details p{padding:8px 16px}small{color:#b2b5be}@media(max-width:600px){main{padding:20px 14px 40px}.pair{gap:10px}figcaption{font-size:12px}.note{padding:10px 14px}}
</style><main><small>ISOLATED PE0 · SIX CALLS · SYNTHETIC IMAGES ONLY</small>
<h1>Photo-reference editing: actual results</h1><p>19 October 2026. Click any image to inspect its unmodified full-resolution PNG. Left is the reference; right is the edit.</p>
<div class="note"><strong>Technical checks passed; your quality review is pending.</strong><p>The existing model can edit from reference pixels. Portrait edits visibly alter unrelated lighting and fine detail. These results do not establish precise Photoshop-style preservation, guaranteed likeness or arbitrary-photo quality.</p></div>
<p>Four edits took 16.9–20.4 seconds for generation/decode, with about 17.4 GiB observed MLX peak and no measured swap growth while Qwen stayed resident at 32K. Cancellation and recovery passed. Each finished PNG is about 1.30–1.67 MB.</p>
''' + ''.join(sections) + f'''<section><h2>Storage and controls</h2><p>All six private case directories retain {storage['case_directories_logical_bytes']/1e6:.2f} MB of logical files, including repeated input copies, cancelled input and metadata. The five finished PNGs total {storage['finished_output_png_bytes']/1e6:.2f} MB. Trial evidence duplicates and model weights are additional. Temporary disk high-water was not sampled.</p><p>Cancellation occurred after denoising step 1; no completed image was left. Every worker was reaped before releasing the shared capacity lease. This is one frozen sequence, not a concurrency, endurance or real-person likeness test.</p><p><a href="summary.json">Measured summary</a> · <a href="preservation-final.json">Source and live-app preservation</a></p></section>
<small>Codex visual observations are separate from Jake’s acceptance. No photo-editing feature was published by this trial.</small></main></html>'''
    (OUT / 'review.html').write_text(page)


if __name__ == '__main__':
    main()
