import io,json,unittest
from unittest.mock import patch
from _bootstrap import SRC
from agenticrag.config import ProviderConfig,ProviderRole
from agenticrag.providers.base import ChatMessage
from agenticrag.providers.openai_compatible import OpenAICompatibleChat
from agenticrag.providers.openai_responses import OpenAIResponsesChat
from agenticrag.errors import ProviderError

class Response(io.BytesIO):
    def __init__(self,body,content_type='application/x-ndjson'):
        super().__init__(body);from email.message import Message
        self.headers=Message();self.headers['Content-Type']=content_type

class CompletionTests(unittest.TestCase):
    def config(self,runtime='ollama',kind='local'):
        return ProviderConfig(kind,ProviderRole.CHAT,'https://api.openai.com/v1' if kind=='openai' else 'http://127.0.0.1:11434/v1','qwen3:30b', 'test' if kind=='openai' else None,90,runtime=runtime)
    def test_native_ollama_uses_one_plain_request_and_bounded_context(self):
        requests=[]
        def transport(request,timeout):requests.append(request);return b'{"message":{"content":"Ready"}}'
        chat=OpenAICompatibleChat(self.config(),transport)
        self.assertEqual(chat.complete([ChatMessage('user','hello')]),'Ready')
        payload=json.loads(requests[0].data)
        self.assertEqual(payload['options']['num_ctx'],16384);self.assertNotIn('tools',payload)
        self.assertNotIn('format',payload);self.assertEqual(requests[0].full_url,'http://127.0.0.1:11434/api/chat')
    def test_native_stream_emits_tokens_as_they_arrive(self):
        frames=[{'message':{'content':'Hello '}},{'message':{'content':'world'},'done':True}]
        body='\n'.join(json.dumps(x) for x in frames).encode()
        tokens=[]
        with patch('agenticrag.providers.openai_compatible.urlopen',return_value=Response(body)):
            self.assertEqual(OpenAICompatibleChat(self.config()).stream_complete([ChatMessage('user','hi')],tokens.append),'Hello world')
        self.assertEqual(tokens,['Hello ','world'])
    def test_openai_compatible_sse(self):
        body=b'data: {"choices":[{"delta":{"content":"Ready"}}]}\n\ndata: {"choices":[],"usage":{"total_tokens":4}}\n\ndata: [DONE]\n'
        with patch('agenticrag.providers.openai_compatible.urlopen',return_value=Response(body,'text/event-stream')):
            self.assertEqual(OpenAICompatibleChat(self.config('lm-studio')).stream_complete([ChatMessage('user','hi')],lambda t:None),'Ready')
    def test_output_limit_is_reported_as_incomplete(self):
        body=b'data: {"choices":[{"delta":{"content":"partial"}}]}\n\ndata: {"choices":[{"finish_reason":"length"}]}\n\ndata: [DONE]\n'
        with patch('agenticrag.providers.openai_compatible.urlopen',return_value=Response(body,'text/event-stream')):
            with self.assertRaisesRegex(ProviderError,'incomplete'):
                OpenAICompatibleChat(self.config('lm-studio')).stream_complete([ChatMessage('user','hi')],lambda t:None)
    def test_responses_stream_and_failures(self):
        body=b'data: {"type":"response.output_text.delta","delta":"Ready"}\n\ndata: {"type":"response.completed"}\n'
        with patch('agenticrag.providers.openai_responses.urlopen',return_value=Response(body,'text/event-stream')):
            self.assertEqual(OpenAIResponsesChat(self.config('openai','openai')).stream_complete([ChatMessage('user','hi')],lambda t:None),'Ready')
        with patch('agenticrag.providers.openai_responses.urlopen',return_value=Response(body.split(b'\n\n')[0],'text/event-stream')):
            with self.assertRaisesRegex(ProviderError,'before completion'):OpenAIResponsesChat(self.config('openai','openai')).stream_complete([ChatMessage('user','hi')],lambda t:None)
    def test_unicode_page_url_is_percent_encoded_before_http_request(self):
        from agenticrag.web_pages import _public_address
        with patch('agenticrag.web_pages.socket.getaddrinfo',return_value=[(2,1,6,'',('93.184.216.34',443))]):
            host,ip,path=_public_address('https://example.org/season–2025?q=é')
        self.assertTrue(path.isascii());self.assertIn('%E2%80%93',path);self.assertIn('%C3%A9',path)

class PageStructureTests(unittest.TestCase):
    def test_preserves_bold_winners_and_table_rows_while_excluding_chrome(self):
        from agenticrag.web_pages import _Text
        parser=_Text()
        parser.feed('<html class="vector-feature-language-in-header-disabled"><body><main><table class="wikitable sticky-header"><tr><th>West</th><th>East</th></tr><tr><td><b>Winner</b></td><td>Loser</td></tr></table><div id="footer">Unrelated navigation</div></main></body></html>')
        text=''.join(parser.main_parts)
        self.assertIn('**Winner',text);self.assertIn('Loser',text);self.assertIn(' | ',text)
        self.assertNotIn('Unrelated navigation',text)
