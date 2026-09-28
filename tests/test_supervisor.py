from __future__ import annotations

import json
import re
import unittest
from unittest.mock import patch

from _bootstrap import SRC  # noqa: F401
from agenticrag.domain import ExternalSource, RAGResult, SourceDraft
from agenticrag.ingestion import Ingestor
from agenticrag.retrieval import HybridRetriever
from agenticrag.store import SQLiteCorpusStore
from agenticrag.supervisor import SupervisorAgentWorkflow
from fakes import DeterministicEmbedding


class ManagerChat:
    label = "test:manager"

    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages, **kwargs):  # type: ignore[no-untyped-def]
        del messages, kwargs
        self.calls += 1
        if self.calls == 1:
            return json.dumps(
                {
                    "assignments": [
                        {
                            "id": "1",
                            "agent": "web_researcher",
                            "task": "Find the current primary source.",
                            "skills": [],
                        }
                    ]
                }
            )
        if self.calls == 2:
            return json.dumps(
                {
                    "answer": "The current primary source supports the finding.",
                    "abstained": False,
                    "used_delegations": ["d1"],
                    "caveats": [],
                }
            )
        if self.calls == 3:
            return json.dumps({"accepted": True, "unsupported_claims": [], "feedback": "Supported."})
        raise AssertionError("Unexpected manager call")


class FakeWebSearch:
    def search(self, query):  # type: ignore[no-untyped-def]
        self.query = query
        return type(
            "Result",
            (),
            {
                "answer": "A primary source supports the finding.",
                "sources": (ExternalSource("web_1", "Primary", "https://example.test/source"),),
                "elapsed_ms": 7,
            },
        )()


class SupervisorTests(unittest.TestCase):
    def test_abstained_corpus_specialist_uses_validated_fixed_fallback(self) -> None:
        class FallbackChat:
            label = "test:fallback-manager"

            def __init__(self) -> None:
                self.calls = 0

            def complete(self, messages, **kwargs):  # type: ignore[no-untyped-def]
                del kwargs
                self.calls += 1
                if self.calls == 1:
                    return json.dumps({"assignments": [
                        {"id": "task", "agent": "corpus_researcher", "task": "Who supplies scopes?", "skills": []}
                    ]})
                if self.calls == 2:
                    match = re.search(r'"chunk_id":"([^"]+)"', messages[1].content)
                    if match is None:
                        raise AssertionError("Fallback needs retrieved evidence")
                    return json.dumps({"answer": "The authenticated application supplies scopes.",
                                       "citations": [match.group(1)], "abstained": False})
                if self.calls == 3:
                    return json.dumps({"answer": "The authenticated application supplies scopes.",
                                       "abstained": False, "used_delegations": ["d1"], "caveats": []})
                if self.calls == 4:
                    return json.dumps({"accepted": True, "unsupported_claims": [], "feedback": "Supported."})
                raise AssertionError("Unexpected model call")

        store = SQLiteCorpusStore(":memory:")
        store.initialize()
        embedder = DeterministicEmbedding()
        Ingestor(store, embedder).ingest_source(SourceDraft(
            "research", "/corpus/scopes.md", "text/markdown",
            "The authenticated application supplies scopes.", ("owner",),
        ))
        chat = FallbackChat()
        workflow = SupervisorAgentWorkflow(
            HybridRetriever(store, embedder), chat, store,
            selected_skills=("evidence-analysis",),
        )
        child = RAGResult(
            workflow="bounded_agentic_rag", provider=chat.label, embedding_provider=embedder.label,
            question="Who supplies scopes?", answer="Could not verify.", abstained=True,
            citations=(), evidence=(), events=(), elapsed_ms=1,
        )
        try:
            with patch("agenticrag.supervisor.BoundedAgenticRAGWorkflow.run", return_value=child):
                result = workflow.run("Who supplies scopes?", scopes=("owner",), collection="research")
        finally:
            store.close()
        self.assertFalse(result.abstained)
        self.assertEqual(len(result.citations), 1)
        self.assertEqual(chat.calls, 4)
        self.assertIn("corpus_specialist_fallback", [e.detail.get("phase") for e in result.events])

    def test_manager_can_assign_two_bounded_tasks_to_one_specialist(self) -> None:
        class DuplicateChat:
            label = "test:duplicate-manager"

            def complete(self, messages, **kwargs):  # type: ignore[no-untyped-def]
                del messages, kwargs
                return json.dumps({"assignments": [
                    {"id": "1", "agent": "corpus_researcher", "task": "Find the policy", "skills": []},
                    {"id": "1", "agent": "corpus_researcher", "task": "Find the exception", "skills": []},
                ]})

        store = SQLiteCorpusStore(":memory:")
        store.initialize()
        workflow = SupervisorAgentWorkflow(
            HybridRetriever(store, DeterministicEmbedding()), DuplicateChat(), store
        )
        try:
            assignments = workflow._plan("Compare policy and exception")
        finally:
            store.close()
        self.assertEqual([item["id"] for item in assignments], ["d1", "d2"])

    def test_manager_delegates_to_web_specialist_and_runs_final_critic(self) -> None:
        store = SQLiteCorpusStore(":memory:")
        store.initialize()
        chat = ManagerChat()
        web = FakeWebSearch()
        workflow = SupervisorAgentWorkflow(
            HybridRetriever(store, DeterministicEmbedding()),
            chat,
            store,
            web_search=web,  # type: ignore[arg-type]
        )
        try:
            result = workflow.run("What is current?", scopes=("owner",), collection="research")
        finally:
            store.close()
        self.assertFalse(result.abstained)
        self.assertEqual(chat.calls, 3)
        self.assertEqual(result.delegations[0].agent, "web_researcher")
        self.assertEqual(result.delegations[0].id, "d1")
        self.assertEqual(result.external_sources[0].url, "https://example.test/source")
        self.assertIn("delegation_completed", [event.kind for event in result.events])
        self.assertIn("review_completed", [event.kind for event in result.events])

    def test_explicit_web_run_uses_web_when_manager_chooses_empty_corpus(self) -> None:
        class CorpusFirstChat(ManagerChat):
            def complete(self, messages, **kwargs):  # type: ignore[no-untyped-def]
                if self.calls == 0:
                    self.calls += 1
                    return json.dumps({"assignments": [
                        {"id": "1", "agent": "corpus_researcher", "task": "Find a source.", "skills": []}
                    ]})
                return super().complete(messages, **kwargs)

        store = SQLiteCorpusStore(":memory:")
        store.initialize()
        chat = CorpusFirstChat()
        workflow = SupervisorAgentWorkflow(
            HybridRetriever(store, DeterministicEmbedding()), chat, store,
            web_search=FakeWebSearch(),  # type: ignore[arg-type]
        )
        try:
            result = workflow.run("What is current?", scopes=("owner",), collection="research")
        finally:
            store.close()
        self.assertFalse(result.abstained)
        self.assertEqual([item.agent for item in result.delegations], ["web_researcher"])
        self.assertEqual(result.external_sources[0].id, "web_1")

    def test_supervisor_abstains_before_planning_with_no_authorized_sources(self) -> None:
        store = SQLiteCorpusStore(":memory:")
        store.initialize()
        chat = ManagerChat()
        workflow = SupervisorAgentWorkflow(
            HybridRetriever(store, DeterministicEmbedding()), chat, store
        )
        try:
            result = workflow.run("What is current?", scopes=("owner",), collection="research")
        finally:
            store.close()
        self.assertTrue(result.abstained)
        self.assertIn("no authorized sources", result.answer)
        self.assertEqual(chat.calls, 0)


if __name__ == "__main__":
    unittest.main()
