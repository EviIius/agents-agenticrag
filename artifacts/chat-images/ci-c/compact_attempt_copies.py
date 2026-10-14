"""Keep exact duplicate regenerated attempt bytes by verified canonical references."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not (OUT/'duplicate-attempt-references.json').exists(), 'Archive references already exist; never overwrite them'
    candidates=sorted(p for p in (OUT/'attempts').rglob('*') if p.is_file() and 'regenerated' in p.parts)
    selected=set(candidates);canonical={}
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p not in selected:canonical.setdefault(digest(p),p)
    records=[]
    for p in candidates:
        sha=digest(p);target=canonical.get(sha)
        if target is None:canonical[sha]=p;continue
        assert target.read_bytes()==p.read_bytes()
        records.append({'original_copy':str(p.relative_to(ROOT)),'canonical_copy':str(target.relative_to(ROOT)),'sha256':sha,'bytes':p.stat().st_size})
        p.unlink()
    for r in records:assert digest(ROOT/r['canonical_copy'])==r['sha256']
    result={'method':'Exact duplicate bytes only; each removed redundant copy resolves to a retained file with a verified SHA-256. Logs, traces, source and novel outputs remain.','references':records,'copies_avoided':len(records),'bytes_avoided':sum(r['bytes'] for r in records)}
    (OUT/'duplicate-attempt-references.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='references'}))
if __name__=='__main__':main()
