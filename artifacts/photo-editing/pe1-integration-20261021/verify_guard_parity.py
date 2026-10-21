"""Compare product admission to the frozen native-tested policy; host-only."""
import hashlib
import itertools
import json
import subprocess
import sys
import tarfile
from pathlib import Path

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
PRIVATE=Path.home()/'.local/share/workbench/qa/photo-editing-pe1-integration-20261021'
frozen=PRIVATE/'frozen-C-source'
frozen.mkdir(mode=0o700)
with tarfile.open(PRIVATE/'frozen-C-source.tar') as bundle:bundle.extractall(frozen,filter='data')
manifest=json.loads((ROOT/'artifacts/photo-editing/pe1-c-prep-20261020/native-execution-manifest.json').read_text())['files']
for name,digest in manifest.items():assert hashlib.sha256((frozen/name).read_bytes()).hexdigest()==digest
edit='09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a'
ordinary='f8a791a5edd0075fb64ff3bd94a3140bfa791992db1bdda0daac587f2b6afbcb'
rows=[{'digest':digest,'context_length':context,'size_vram':size,'name':alias} for digest,context,size,alias in itertools.product([edit,ordinary,'unknown'],[32768,65536,'32768'],[0,1,21827095100,21827095101,True,None],['fake-alias','unrelated-name'])]
cases=[[]]+[[row] for row in rows]+[[row,row] for row in rows]
file=PRIVATE/'guard-cases.json';file.write_text(json.dumps(cases))
code="import json,sys;sys.path.insert(0,sys.argv[1]+'/server');from app.images.engine import Engine;cases=json.load(open(sys.argv[2]));print(json.dumps([((not rows) or Engine.qualified_edit(rows)) if sys.argv[3]=='frozen' else Engine.qualified_edit(rows) for rows in cases]))"
results=[]
for root,label in [(frozen,'frozen'),(ROOT,'product')]:
 result=subprocess.run([sys.executable,'-c',code,str(root),str(file),label],capture_output=True,text=True,check=True)
 results.append(json.loads(result.stdout))
assert results[0]==results[1]
(OUT/'guard-parity.json').write_text(json.dumps({'passed':True,'host_only':True,'native_calls':0,'scenarios':len(cases),'frozen_source_files_preserved':len(manifest),'exact_native_tested_policy_preserved':True,'qualification_scope':'Only empty slot or the previously measured strict 32K digest/size arrangement; no model-name inference.'},indent=2)+'\n')
print(json.dumps({'passed':True,'scenarios':len(cases),'native_calls':0}))
