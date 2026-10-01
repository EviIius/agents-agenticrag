from __future__ import annotations
import threading
import unittest
from unittest.mock import patch
from _bootstrap import SRC
from agenticrag.conversations import ConversationStore
from agenticrag.domain import SourceDraft
from agenticrag.ingestion import Ingestor
from agenticrag.store import SQLiteCorpusStore
from agenticrag.providers.base import ChatMessage
from agenticrag.web_chat import WebChat, read_span
from agenticrag.web_search import WebHit
from agenticrag.errors import WorkflowError
from fakes import StaticChat, DeterministicEmbedding

class Search:
    label='test-search'
    def __init__(self,hits=None): self.calls=[];self.hits=hits or (WebHit('NBA History','https://example.org/finals','UNTRUSTED SNIPPET'),)
    def search_results(self,query,*,max_results):self.calls.append(query);return self.hits

class WebChatTests(unittest.TestCase):
    def setUp(self):
        self.store=SQLiteCorpusStore(':memory:');self.store.initialize()
        self.registry=ConversationStore(':memory:');self.project=self.registry.get_project('default')
        self.chat=StaticChat('The Bucks defeated the Suns in 2021 [1].')
        self.search=Search()
        self.text='NBA Finals official results. In 2021 Milwaukee Bucks defeated Phoenix Suns. '*4
    def tearDown(self):self.store.close();self.registry.close()
    def run_chat(self,**kwargs):
        return WebChat(self.chat,self.store,search=self.search,registry=self.registry,project=self.project).run(
            'Who lost the 2021 NBA Finals?',scopes=['private'],collection='research',**kwargs)
    def test_one_completion_no_private_corpus_or_old_report_contamination(self):
        Ingestor(self.store,DeterministicEmbedding()).ingest_source(SourceDraft('research','private.md','text/plain','Private recipes and research IDs.',('private',)))
        with patch('agenticrag.web_chat.fetch_public_page',return_value=('https://example.org/finals',self.text)):
            result=self.run_chat(history=[ChatMessage('assistant','Private recipes and research IDs.')])
        self.assertEqual(len(self.search.calls),1);self.assertEqual(len(self.chat.calls),1)
        prompt='\n'.join(m.content for m in self.chat.calls[0][0])
        self.assertNotIn('Private recipes',prompt);self.assertNotIn('UNTRUSTED SNIPPET',prompt)
        self.assertIsNone(self.chat.calls[0][1]['response_schema'])
        citation=result.citations[0]
        source=self.store.get_source(citation.source_version_id,scopes=['private'])
        self.assertEqual(source.text[citation.start_char:citation.end_char],result.evidence[0].chunk.text)
        self.assertEqual(self.store._metadata('embedding_provider_label'),'test:embedding')
    def test_no_readable_pages_produces_no_generated_facts(self):
        with patch('agenticrag.web_chat.fetch_public_page',side_effect=OSError('blocked')):
            result=self.run_chat()
        self.assertTrue(result.abstained);self.assertFalse(result.citations);self.assertFalse(self.chat.calls)
        self.assertEqual(result.events[1].kind,'web_page_failed')
    def test_partial_page_failure_keeps_successful_snapshot(self):
        self.search=Search((WebHit('blocked','https://example.org/blocked',''),WebHit('history','https://example.org/finals','')))
        def read(url):
            if url.endswith('blocked'):raise ValueError('HTTP 403')
            return url,self.text
        with patch('agenticrag.web_chat.fetch_public_page',side_effect=read):result=self.run_chat()
        self.assertEqual(len(result.citations),1);self.assertEqual(len(self.chat.calls),1)
        self.assertTrue(any(e.kind=='web_page_failed' for e in result.events))
    def test_reads_are_parallel_and_bounded(self):
        self.search=Search(tuple(WebHit(str(i),f'https://example.org/{i}','') for i in range(8)))
        barrier=threading.Barrier(4)
        def read(url):barrier.wait(timeout=2);return url,self.text
        with patch('agenticrag.web_chat.fetch_public_page',side_effect=read) as fetch:result=self.run_chat()
        self.assertEqual(fetch.call_count,4);self.assertEqual(len(result.citations),4)
    def test_declined_web_calls_neither_search_nor_reader(self):
        with patch('agenticrag.web_chat.fetch_public_page') as fetch:result=self.run_chat(permission=lambda q:False)
        self.assertFalse(fetch.called);self.assertFalse(self.search.calls);self.assertEqual(result.workflow,'chat')
    def test_topic_domain_is_considered_before_page_read_limit(self):
        self.search=Search(tuple(WebHit(str(i),f'https://example.org/{i}','') for i in range(5))+
                           (WebHit('NBA','https://www.nba.com/history',''),))
        def read(url):return url,self.text
        with patch('agenticrag.web_chat.fetch_public_page',side_effect=read) as fetch:result=self.run_chat()
        self.assertEqual(fetch.call_count,4)
        self.assertEqual(result.citations[0].logical_path,'https://www.nba.com/history')
    def test_large_pages_share_one_context_budget_and_disclose_omissions(self):
        self.search=Search(tuple(WebHit(str(i),f'https://example.org/{i}','') for i in range(4)))
        def read(url):return url, self.text*200
        with patch('agenticrag.web_chat.fetch_public_page',side_effect=read):result=self.run_chat()
        lengths=[len(item.chunk.text) for item in result.evidence]
        self.assertEqual(sum(lengths),24000);self.assertEqual(max(lengths),12000)
        prompt='\n'.join(m.content for m in self.chat.calls[0][0])
        self.assertIn('PARTIAL excerpt',prompt)
        for item,citation in zip(result.evidence,result.citations):
            text=self.store.get_source(citation.source_version_id,scopes=['private']).text
            self.assertEqual(text[citation.start_char:citation.end_char],item.chunk.text)
    def test_cancel_prevents_any_completion(self):
        cancelled=threading.Event();cancelled.set()
        with self.assertRaises(WorkflowError):self.run_chat(cancelled=cancelled)
        self.assertFalse(self.chat.calls);self.assertFalse(self.search.calls)
    def test_source_span_is_exact_even_when_relevance_window_is_not_first(self):
        text=('Unrelated navigation. '*1000)+self.text
        offset,span=read_span(text,'NBA Finals Bucks Suns')
        self.assertGreater(offset,0);self.assertEqual(text[offset:offset+len(span)],span)
    def test_missing_inline_citations_are_disclosed_without_repair_call(self):
        self.chat=StaticChat('Bucks defeated the Suns.')
        with patch('agenticrag.web_chat.fetch_public_page',return_value=('https://example.org/finals',self.text)):result=self.run_chat()
        self.assertIn('did not place inline citations',result.answer);self.assertEqual(len(self.chat.calls),1)
    def test_common_citation_notations_are_normalized_without_inference(self):
        self.chat=StaticChat('A sourced fact【1】. Another fact [1, 1].')
        with patch('agenticrag.web_chat.fetch_public_page',return_value=('https://example.org/finals',self.text)):result=self.run_chat()
        self.assertIn('fact[1]',result.answer);self.assertNotIn('did not place inline citations',result.answer)
        self.assertEqual(len(self.chat.calls),1)
    def test_unsafe_or_unknown_markers_are_not_clickable_sources(self):
        self.chat=StaticChat('A fact [9], a supported fact [1].')
        with patch('agenticrag.web_chat.fetch_public_page',return_value=('https://example.org/finals',self.text)):result=self.run_chat()
        self.assertNotIn('[9]',result.answer);self.assertIn('[1]',result.answer)

if __name__=='__main__':unittest.main()
