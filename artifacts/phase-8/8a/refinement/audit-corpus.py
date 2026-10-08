"""Read-only analysis of the unchanged recorded corpus and prior selections."""
import asyncio
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'server'))
sys.path.insert(0, str(ROOT/'server/evals/research'))
from regrade import cases, facts
from app.search.fixtures import Fixtures
from app.search.extract import extract_async
from app.search.merge import merge
from app.search.rank import bm25
from app.search.chunk import chunk

async def main():
 rows=[]
 before=json.loads((ROOT/'artifacts/phase-8/8a/eval/report.json').read_text())['results']
 for case, prior in zip(cases(),before,strict=True):
  folder=ROOT/'artifacts/phase-8/gate/web-fixtures'/case['id']/'0'
  fixtures=Fixtures(folder);saved=json.loads((folder/'run.json').read_text())['web'];batches=[]
  for query in saved['queries']:
   for provider in ['ollama','searxng','exa','ddgs']:
    try: batch=fixtures.search(provider,query,saved.get('freshness','any'))
    except (ValueError,FileNotFoundError): continue
    if batch:batches.append(batch);break
  alltext=[];pages=[]
  for row in merge(batches,[])[:8]:
   try:page=await extract_async(fixtures.page(row.url))
   except (ValueError,FileNotFoundError,TypeError):pages.append({'url':row.url,'readable':False});continue
   alltext.append(page.text);pages.append({'url':row.url,'readable':True,'chars':len(page.text)})
  source_text='\n'.join(p['text'] for s in prior['sources'] for p in s['passages'])
  body='\n'.join(alltext)
  rows.append({'id':case['id'],'returned_pages':pages,
   'regex_facts_available_somewhere':facts(body,case),
   'regex_facts_in_previous_answer_evidence':facts(source_text,case),
   'missing_in_corpus_regexes':[q for q in case['expect']['must_include'] if not re.search(q,body)]})
 out=ROOT/'artifacts/phase-8/8a/refinement/corpus-audit.json';out.write_text(json.dumps(rows,indent=2)+'\n')
 print('\n'.join(f"{x['id']}: readable {sum(p['readable'] for p in x['returned_pages'])}; all-facts regex {x['regex_facts_available_somewhere']}; previously selected {x['regex_facts_in_previous_answer_evidence']}" for x in rows))
asyncio.run(main())
