import json,tempfile,threading,time,unittest
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from _bootstrap import SRC
from agenticrag.server import WorkbenchState,make_handler
from agenticrag.config import ProviderRole
from agenticrag.runtimes import RuntimeSelection
from agenticrag.web_search import WebHit
from fakes import StaticChat

class Search:
 label='Fixture Search'
 def search_results(self,q,*,max_results):return (WebHit('Finals','https://example.org/finals','Snippet'),)

class ServerTests(unittest.TestCase):
 def setUp(self):
  self.directory=tempfile.TemporaryDirectory();self.state=WorkbenchState(str(Path(self.directory.name)/'corpus.db'))
  self.state._providers[ProviderRole.CHAT]=RuntimeSelection('ollama',ProviderRole.CHAT,'http://127.0.0.1:11434/v1','fixture','prompt')
  self.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.state));self.server.daemon_threads=True
  self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
  self.origin=f'http://127.0.0.1:{self.server.server_port}'
  self.chat=StaticChat('The Bucks won against the Suns [1].')
  self.patches=[patch('agenticrag.server.build_chat_provider',return_value=self.chat),patch('agenticrag.server.configured_search_provider',return_value=Search()),patch('agenticrag.server.local_web_search_available',return_value=True),patch('agenticrag.web_chat.fetch_public_page',return_value=('https://example.org/finals','The Bucks defeated the Suns in the 2021 Finals. '*8))]
  for p in self.patches:p.start()
 def tearDown(self):
  self.server.shutdown();self.server.server_close();self.thread.join();self.state.runs.close();self.state.conversations.close();self.directory.cleanup()
  for p in self.patches:p.stop()
 def request(self,path,payload=None,method='POST',headers=None):
  request=Request(self.origin+path,data=json.dumps(payload).encode() if payload is not None else None,method=method if payload is not None else 'GET',headers=headers or {'Content-Type':'application/json','Origin':self.origin})
  with urlopen(request,timeout=4) as response:return json.load(response)
 def saved_chat(self):return self.request('/api/v1/chats',{'collection':'research','scopes':['private']})['id']
 def payload(self,chat=None):return {'question':'Who lost the 2021 NBA Finals?','workflow':'chat','collection':'research','scopes':['private'],**({'chat_id':chat} if chat else {})}
 def wait(self,id,status=None):
  for _ in range(100):
   run=self.request('/api/v1/runs/'+id)
   if status is None and run['status'] in {'completed','failed','stopped'}:return run
   if status and any(e.get('event',{}).get('kind')==status for e in run['events']):return run
   time.sleep(.02)
  self.fail('Request did not reach expected state')
 def test_removed_workflows_and_settings_are_rejected(self):
  for workflow in ['agent','fixed','auto','ask','deep_research']:
   with self.assertRaises(HTTPError) as error:self.request('/api/v1/ask',{**self.payload(),'workflow':workflow})
   self.assertEqual(error.exception.code,400)
  with self.assertRaises(HTTPError):self.request('/api/v1/ask',{**self.payload(),'effort':'deep'})
  bootstrap=self.request('/api/v1/bootstrap');self.assertNotIn('capabilities',bootstrap);self.assertNotIn('workflows',bootstrap)
 def test_offline_chat_needs_no_search_or_embedding(self):
  self.request('/api/v1/projects/default/settings',{'web_mode':'off'},'PUT')
  result=self.request('/api/v1/ask',self.payload(self.saved_chat()))
  self.assertEqual(result['workflow'],'chat');self.assertFalse(result['citations']);self.assertEqual(len(self.chat.calls),1)
 def test_on_search_saves_exact_sources_and_library_without_embedding(self):
  self.request('/api/v1/projects/default/settings',{'web_mode':'on'},'PUT')
  result=self.request('/api/v1/ask',self.payload(self.saved_chat()));id=result['citations'][0]['source_version_id']
  source=self.request('/api/v1/sources/'+id+'?scope=private');self.assertIn('Bucks',source['text'])
  saved=self.request('/api/v1/web-sources/'+id+'/save',{'project_id':'default'})
  self.assertEqual(saved['source']['collection'],'research');self.assertEqual(saved['source']['text'],None)
  self.assertEqual(self.request('/api/v1/web-sources/'+id+'/save',{'project_id':'default'})['status'],'already_saved')
 def test_ask_permission_and_durable_history(self):
  id='a'*32;chat=self.saved_chat()
  self.request('/api/v1/runs',{**self.payload(chat),'run_id':id})
  self.wait(id,'web_approval_requested');self.assertFalse(self.chat.calls)
  self.request('/api/v1/runs/'+id+'/web-approval',{'allow':True})
  result=self.wait(id);self.assertEqual(result['status'],'completed');self.assertEqual(len(result['result']['citations']),1)
  reopened=self.request('/api/v1/chats/'+chat);self.assertEqual(len(reopened['messages']),2)
 def test_cancel_while_awaiting_approval(self):
  id='b'*32;self.request('/api/v1/runs',{**self.payload(self.saved_chat()),'run_id':id})
  self.wait(id,'web_approval_requested');self.request('/api/v1/runs/'+id+'/cancel',{})
  self.assertEqual(self.wait(id)['status'],'stopped');self.assertFalse(self.chat.calls)
 def test_host_origin_and_source_scope_boundaries(self):
  with self.assertRaises(HTTPError) as error:self.request('/api/v1/chats',{'collection':'research','scopes':['private']},headers={'Content-Type':'application/json','Origin':'https://evil.example'})
  self.assertEqual(error.exception.code,403)
  self.request('/api/v1/projects/default/settings',{'web_mode':'on'},'PUT')
  result=self.request('/api/v1/ask',self.payload())
  with self.assertRaises(HTTPError) as error:self.request('/api/v1/sources/'+result['citations'][0]['source_version_id']+'?scope=guest')
  self.assertEqual(error.exception.code,403)

if __name__=='__main__':unittest.main()
