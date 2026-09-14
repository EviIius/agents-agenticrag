from __future__ import annotations

import json
import unittest

from _bootstrap import SRC  # noqa: F401
from agenticrag.domain import ExternalSource
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
                            "id": "current_web",
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
                    "used_delegations": ["current_web"],
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
        self.assertEqual(result.external_sources[0].url, "https://example.test/source")
        self.assertIn("delegation_completed", [event.kind for event in result.events])
        self.assertIn("review_completed", [event.kind for event in result.events])


if __name__ == "__main__":
    unittest.main()
