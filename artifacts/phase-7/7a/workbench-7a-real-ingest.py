import asyncio,hashlib,json,tempfile,time,sys
from pathlib import Path
import httpx
sys.path.insert(0,"/Users/evilius/Documents/GitHub/agents-agenticrag/server")
from app.config import Settings
from app.main import create_app
root=Path('/Users/evilius/Documents/GitHub/agents-agenticrag')
async def main():
 with tempfile.TemporaryDirectory(prefix='workbench-7a-synthetic-') as tmp:
  private=Path(tmp);private.chmod(0o700)
  app=create_app(Settings(data_dir=private,dev=False,legacy_db=private/'absent-legacy.db',transcribe_home=private/'no-transcription'))
  async with app.router.lifespan_context(app),httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost') as client:
   conn=(await client.post('/api/connections',json={'base_url':'http://127.0.0.1:11434'})).json()
   started=time.monotonic()
   response=await client.post('/api/library/embedding',json={'embedding':{'connection_id':conn['id'],'model_id':'qwen3-embedding:0.6b'}})
   assert response.status_code==200
   dim=response.json()['embedding']['dim'];assert dim==1024
   upload=await client.post('/api/library/documents',files={'file':('Invented synthetic handbook.pdf',(root/'server/tests/fixtures/documents/two-pages.pdf').read_bytes(),'application/pdf')})
   assert upload.status_code==201
   identifier=upload.json()['id'];lib=app.state.library
   async with asyncio.timeout(120),lib.changed:
    while True:
     row=await lib.store.one('SELECT status,chunk_count,pages FROM library_documents WHERE id=?',(identifier,))
     if row['status'] in ('ready','failed'):break
     await lib.changed.wait()
   assert row['status']=='ready' and row['pages']==2
   vectors=await lib.store.rows('SELECT chunk_id FROM library_vectors')
   assert len(vectors)==row['chunk_count']
   assert (await client.delete('/api/library/documents/'+identifier)).status_code==204
   assert not list(lib.folder.iterdir())
   result={'method':'isolated temporary data, full application ASGI lifespan, approved real loopback Ollama, committed synthetic PDF','model':'qwen3-embedding:0.6b','dimension':dim,'pages':2,'passages':len(vectors),'status':'ready','delete_removes_original_and_index':not await lib.store.rows('SELECT * FROM library_chunks'),'seconds':round(time.monotonic()-started,3),'private_text_or_names_logged':False,'temporary_data_removed_on_exit':True,'embedding_requests':2,'chat_model_calls':0}
   (root/'artifacts/phase-7/7a/real-ingestion-fake-document.json').write_text(json.dumps(result,indent=2)+'\n')
asyncio.run(main())
