"""Verify frozen source, historical inputs/references and the unchanged live app."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
BASE = 'e3042eaeb16fe339d8a152b1d7e681049bbab263'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    frozen=json.loads((OUT/'frozen-source.json').read_text())
    for record in frozen['files']:
        assert sha(ROOT/record['path'])==record['sha256'],record['path']
    entries=subprocess.check_output(['git','ls-tree','-r','-z',BASE],cwd=ROOT).split(b'\0')
    evidence=refs=0
    for entry in entries:
        if not entry:continue
        header,name=entry.split(b'\t',1)
        path=name.decode()
        if not path.startswith(('artifacts/','server/evals/','server/tests/fixtures/','docs/next/workflow-studio/')):continue
        data=(ROOT/path).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        assert blob==header.split()[2].decode(),path
        if path.startswith('docs/next/workflow-studio/'):refs+=1
        else:evidence+=1
    app=Path.home()/'.local/share/workbench/app'
    server=json.loads((ROOT/'artifacts/composer-workflows/unchanged-server.json').read_text())['server_files']
    static=json.loads((ROOT/'artifacts/composer-workflows/release-manifest.json').read_text())['static_files']
    for path,expected in server.items():assert sha(app/path)==expected,path
    for path,expected in static.items():assert sha(app/'server/app/static'/path)==expected,path
    main_head=subprocess.check_output(['git','-C','/Users/evilius/Documents/GitHub/agents-agenticrag','rev-parse','HEAD'],text=True).strip()
    assert main_head=='dce4c49eabefc9a72bb426e6a05706247daf5b63'
    result={'baseline':BASE,'frozen_source_and_test_files_verified':len(frozen['files']),'historical_evidence_eval_and_fixture_blobs_verified':evidence,'provided_reference_files_verified':refs,'installed_server_files_verified':len(server),'installed_current_release_static_files_verified':len(static),'main_head':main_head,'no_merge_or_live_deployment':True,'method':'One Git ls-tree batch; verify the original Git blob of each historical file. Frozen source and installed files use SHA-256.'}
    (OUT/'preservation-final.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
