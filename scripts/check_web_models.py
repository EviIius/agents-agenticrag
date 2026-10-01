"""Explicit local-model regression: one real search, shared immutable pages, one completion per model."""
from __future__ import annotations
import argparse,json,re,time
from dataclasses import replace
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from urllib.request import urlopen
from agenticrag.config import ProviderRole
from agenticrag.runtimes import RuntimeSelection
from agenticrag.providers.openai_compatible import build_chat_provider
from agenticrag.store import SQLiteCorpusStore
from agenticrag.web_chat import WebChat
from agenticrag.web_pages import fetch_public_page
from agenticrag.web_search import configured_search_provider,WebHit

QUESTION='Who lost the NBA Finals in 2021, and which team defeated them? Give the losing team, winning team, year, and series score with sources.'

def correct_roles(answer):
 # Accept both prose and an explicitly labeled table, preserving direction.
 plain=answer.replace('**','')
 prose=bool(re.search(r'(?:losing team.{0,10}Phoenix Suns|Phoenix Suns.{0,40}lost|Phoenix Suns.{0,25}were defeated)',plain,re.I|re.S)) and bool(re.search(r'(?:winning team.{0,10}Milwaukee Bucks|defeated by.{0,10}Milwaukee Bucks|lost.{0,40}Milwaukee Bucks|Milwaukee Bucks.{0,40}defeated.{0,10}Phoenix Suns)',plain,re.I|re.S))
 headers=None
 for line in plain.splitlines():
  if not line.strip().startswith('|'):continue
  cells=[cell.strip().lower() for cell in line.strip().strip('|').split('|')]
  if 'losing team' in cells and 'winning team' in cells:headers=cells
  elif headers and len(cells)==len(headers):
   if cells[headers.index('losing team')]=='phoenix suns' and cells[headers.index('winning team')]=='milwaukee bucks':return True
 return prose

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--pages',type=Path,help='Use recorded canonical pages instead of live search; never pass private text')
 parser.add_argument('--output',type=Path,default=Path('.data/web-chat-check.json'))
 parser.add_argument('--model',action='append')
 args=parser.parse_args()
 if args.pages:
  pages=json.loads(args.pages.read_text());search_label='Recorded public pages'
 else:
  search=configured_search_provider();search_label=search.label
  hits=search.search_results('2021 NBA Finals losing team winning team series score',max_results=8)
  pages={}
  def read(hit):
   try:return hit.url,fetch_public_page(hit.url)
   except (OSError,ValueError):return hit.url,None
  with ThreadPoolExecutor(max_workers=4) as pool:
   for url,page in pool.map(read,hits[:4]):
    if page:pages[url]=page
 if not pages:raise SystemExit('No readable public pages; no model checks run')
 class Search:
  label=search_label
  def search_results(self,q,*,max_results):return tuple(WebHit('Recorded result',url,'') for url in pages)
 models=args.model or [row['name'] for row in json.load(urlopen('http://127.0.0.1:11434/api/tags',timeout=5))['models'] if 'embed' not in row['name'].lower()]
 models.sort(key=lambda model:('70b' in model,model))
 results=[]
 for model in models:
  config=RuntimeSelection('ollama',ProviderRole.CHAT,'http://127.0.0.1:11434/v1',model,'prompt',timeout_seconds=120).provider_config()
  started=time.monotonic();first=[]
  def token(value):
   if not first:first.append(time.monotonic()-started)
  try:
   with SQLiteCorpusStore(':memory:') as store:
    store.initialize()
    with patch('agenticrag.web_chat.fetch_public_page',side_effect=lambda url:pages[url]):
     result=WebChat(build_chat_provider(config),store,search=Search()).run(QUESTION,scopes=['private'],collection='review',on_token=token)
   answer=result.answer
   # Check direction, not simply whether both team names occur.
   correct=correct_roles(answer)
   row={'model':model,'seconds':round(time.monotonic()-started,2),'first_token_seconds':round(first[0],2) if first else None,'correct_roles':correct,'series_score':bool(re.search(r'4\s*[–−\-]\s*2|Milwaukee Bucks\s+4,\s+Phoenix Suns\s+2',answer)),'linked_citation':bool(re.search(r'\[\d+\]',answer)),'source_count':len(result.citations),'answer':answer}
  except Exception as exc:row={'model':model,'error':str(exc),'seconds':round(time.monotonic()-started,2)}
  results.append(row);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(results,indent=2,ensure_ascii=False));print(json.dumps({key:value for key,value in row.items() if key!='answer'}),flush=True)
 return 0 if all(row.get('correct_roles') and row.get('series_score') and row.get('linked_citation') for row in results) else 1

if __name__=='__main__':raise SystemExit(main())
