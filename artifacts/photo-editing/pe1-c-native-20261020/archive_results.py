"""Archive only synthetic PE1-C output and measured provenance; no inference."""
import hashlib
import json
import shutil
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PRIVATE=Path.home()/'.local/share/workbench/qa/photo-editing-pe1-c-prep-20261020/native'
summary=json.loads((PRIVATE/'summary.json').read_text())
assert summary['passed'] and summary['native_image_requests']==4 and summary['preload_requests']==1
assert not (PRIVATE/'HALTED').exists()
for name in ['summary.json','storage.json','launches.jsonl']:
 shutil.copy2(PRIVATE/name,OUT/name)
shutil.copy2(ROOT/'artifacts/photo-editing/pe1-c-prep-20261020/native-execution-manifest.json',OUT/'executed-source.json')
rows=[]
for case in summary['cases']:
 label=case['case'];job=PRIVATE/'data/images'/case['job_id'];dest=OUT/'cases'/label
 dest.mkdir(mode=0o700,parents=True,exist_ok=False)
 request=json.loads((job/'input.json').read_text())
 shutil.copy2(PRIVATE/(label+'.json'),dest/'case.json')
 for name in ['input.json','storage.json']: shutil.copy2(job/name,dest/name)
 for name in ['original','reference.png','reference.json']:
  shutil.copy2(job/'inputs'/name,dest/name)
 output=job/'output';meta=None
 if output.is_dir():
  for name in ['image.png','export.png','metadata.json']: shutil.copy2(output/name,dest/name)
  meta=json.loads((output/'metadata.json').read_text())
 assert not (job/'working').exists()
 files={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in dest.iterdir() if p.is_file()}
 row={'case':label,'state':case['state'],'original_bytes':files['original']['bytes'],'working_reference_bytes':files['reference.png']['bytes'],'output_png_bytes':files.get('image.png',{}).get('bytes',0),'export_png_bytes':files.get('export.png',{}).get('bytes',0),'output_metadata_bytes':files.get('metadata.json',{}).get('bytes',0),'files':files,'native_initialization_seconds':meta.get('initialization_seconds') if meta else None,'generation_decode_seconds':meta.get('generate_seconds') if meta else None,'mlx_peak_bytes':meta.get('mlx_peak_bytes') if meta else None,'mlx_cache_bytes':meta.get('mlx_cache_bytes') if meta else None,'observed_job_storage':case['storage'],'scope':'Synthetic fixture only; cancelled case has no accepted output.'}
 rows.append(row)
segments=[]
for event in summary['events']:
 if event['type']=='initializing': segments.append([])
 assert segments
 segments[-1].append(event)
assert len(segments)==4
for row,segment in zip(rows,segments,strict=True):
 steps=[e['completed_steps'] for e in segment if e['type']=='denoising']
 assert steps==([0,1] if row['case']=='cancel' else [0,1,2,3,4]),steps
 row['real_progress_events']=segment
 assert (segment[-1]['type']=='finished')==(row['case']!='cancel')
assert len(summary['reaping'])==4 and all(all(r.values()) for r in summary['reaping'])
store=json.loads((PRIVATE/'storage.json').read_text())
aggregate={'passed':True,'native_image_invocations':4,'empty_message_preloads':1,'case_results':rows,'all_workers_reaped_with_lease_held':True,'capacity_released':summary['capacity_released'],'health_samples':len(summary['health_seconds']),'maximum_observed_health_seconds':max(summary['health_seconds']),'observed_swap_mib_range':[min(summary['swap_mib']),max(summary['swap_mib'])],'storage':store,'sampling_limits':'Observed high-water samples, not an absolute physical APFS peak; allocation deduplicates hard-linked inodes only. Cancel retains inputs for retry. Native PNG plus separate sanitized export both count as retained outputs.'}
(OUT/'results.json').write_text(json.dumps(aggregate,indent=2)+'\n')
print(json.dumps({'passed':True,'cases':[{k:r[k] for k in ['case','state','native_initialization_seconds','generation_decode_seconds','mlx_peak_bytes','original_bytes','working_reference_bytes','output_png_bytes','export_png_bytes']} for r in rows],'maximum_health_seconds':aggregate['maximum_observed_health_seconds'],'swap_mib_range':aggregate['observed_swap_mib_range'],'observed_storage':{k:v for k,v in store.items() if k not in ['samples','limits']}}))
