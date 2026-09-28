from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path
from typing import Any

from _bootstrap import SRC  # noqa: F401
from agenticrag.agent import AgentConfig, BoundedAgenticRAGWorkflow
from agenticrag.agent_tools import ReadOnlyToolGateway, ToolBudget
from agenticrag.domain import SourceDraft
from agenticrag.errors import ConfigurationError, WorkflowError
from agenticrag.experiments import ExperimentCase, ExperimentRunner, summarize_experiments
from agenticrag.ingestion import Ingestor
from agenticrag.retrieval import HybridRetriever
from agenticrag.skills import SkillRegistry
from agenticrag.store import SQLiteCorpusStore
from fakes import DeterministicEmbedding


class AgentChat:
    label = "test:agent-chat"

    def __init__(
        self,
        *,
        accept_review: bool = True,
        fabricated_citation: bool = False,
        plan_id: str = "o1",
        contradictory_review: bool = False,
        finish_abstained: bool = False,
    ) -> None:
        self.calls: list[dict[str, Any]] = []
        self.accept_review = accept_review
        self.fabricated_citation = fabricated_citation
        self.plan_id = plan_id
        self.contradictory_review = contradictory_review
        self.finish_abstained = finish_abstained

    def complete(self, messages, **kwargs):  # type: ignore[no-untyped-def]
        self.calls.append({"messages": messages, "options": kwargs})
        index = len(self.calls)
        if index == 1:
            return json.dumps(
                {
                    "obligations": [{"id": self.plan_id, "question": "How much memory?"}],
                    "skills": ["evidence-analysis"],
                }
            )
        if index == 2:
            return json.dumps(
                {
                    "action": "search",
                    "purpose": "Find the memory specification",
                    "arguments": {"query": "Atlas memory"},
                }
            )
        if index == 3 or (self.fabricated_citation and index > 3):
            content = messages[1].content
            match = re.search(r'"chunk_id":"([^"]+)"', content)
            if match is None:
                raise AssertionError("Expected retained evidence")
            chunk_id = "chunk_fabricated" if self.fabricated_citation else match.group(1)
            return json.dumps(
                {
                    "action": "finish",
                    "purpose": "Answer from retrieved evidence",
                    "arguments": {
                        "answer": "Atlas has 64 GB of memory.",
                        "citations": [chunk_id],
                        "abstained": self.finish_abstained,
                        "obligations": [
                            {"id": "o1", "supported": True, "evidence_ids": [chunk_id]}
                        ],
                    },
                }
            )
        if index == 4:
            return json.dumps(
                {
                    "accepted": self.accept_review,
                    "unsupported_claims": ["memory amount"] if self.contradictory_review or not self.accept_review else [],
                    "missing_obligations": [] if self.accept_review else ["o1"],
                    "feedback": "Supported." if self.accept_review else "Gather better evidence.",
                }
            )
        raise AssertionError("Unexpected model call")


class AgenticWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = SQLiteCorpusStore(":memory:")
        self.store.initialize()
        self.embedder = DeterministicEmbedding()
        Ingestor(self.store, self.embedder).ingest_source(
            SourceDraft(
                "private",
                "/corpus/atlas.md",
                "text/markdown",
                "# Atlas\n\nAtlas has 64 GB of memory.",
                ("owner",),
            )
        )
        self.temporary = tempfile.TemporaryDirectory()
        skill = Path(self.temporary.name, "evidence-analysis")
        skill.mkdir()
        Path(skill, "SKILL.md").write_text(
            "---\nname: evidence-analysis\ndescription: Check evidence carefully.\n---\n"
            "Search every obligation and cite only retrieved evidence.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()
        self.store.close()

    def _workflow(self, chat: AgentChat, *, max_steps: int = 4) -> BoundedAgenticRAGWorkflow:
        return BoundedAgenticRAGWorkflow(
            HybridRetriever(self.store, self.embedder),
            chat,
            self.store,
            skill_registry=SkillRegistry(self.temporary.name),
            config=AgentConfig(max_steps=max_steps),
        )

    def test_agent_loads_skill_calls_tool_and_passes_evidence_review(self) -> None:
        chat = AgentChat()
        result = self._workflow(chat).run(
            "How much memory does Atlas have?", scopes=("owner",), collection="private"
        )
        self.assertFalse(result.abstained)
        self.assertEqual(result.answer, "Atlas has 64 GB of memory.")
        self.assertEqual(len(result.citations), 1)
        kinds = [event.kind for event in result.events]
        self.assertIn("skill_loaded", kinds)
        self.assertIn("tool_called", kinds)
        self.assertIn("review_completed", kinds)
        self.assertEqual(len(chat.calls), 4)
        action_messages = chat.calls[1]["messages"]
        self.assertIn("Trusted operator-selected skills", action_messages[0].content)
        self.assertIn("Search every obligation", action_messages[0].content)
        self.assertNotIn("Search every obligation", action_messages[1].content)

    def test_host_assigns_stable_obligation_ids_when_model_uses_numbers(self) -> None:
        chat = AgentChat(plan_id="1")
        result = self._workflow(chat).run(
            "How much memory does Atlas have?", scopes=("owner",), collection="private"
        )
        self.assertFalse(result.abstained)
        self.assertIn('"id":"o1"', chat.calls[1]["messages"][1].content)

    def test_complete_cited_answer_is_not_mislabelled_as_abstained(self) -> None:
        result = self._workflow(AgentChat(finish_abstained=True)).run(
            "How much memory does Atlas have?", scopes=("owner",), collection="private"
        )
        self.assertFalse(result.abstained)
        self.assertEqual(len(result.citations), 1)

    def test_simple_fact_question_is_not_overplanned(self) -> None:
        class OverPlanChat(AgentChat):
            def complete(self, messages, **kwargs):  # type: ignore[no-untyped-def]
                if not self.calls:
                    self.calls.append({"messages": messages, "options": kwargs})
                    return json.dumps({
                        "obligations": [
                            {"id": f"o{i}", "question": f"Find Atlas fact {i}"}
                            for i in range(1, 5)
                        ],
                        "skills": ["evidence-analysis"],
                    })
                return super().complete(messages, **kwargs)

        result = self._workflow(OverPlanChat()).run(
            "What is Atlas memory?", scopes=("owner",), collection="private"
        )
        self.assertFalse(result.abstained)
        self.assertEqual(result.events[0].detail["obligation_count"], 1)
        self.assertTrue(result.events[0].detail["host_simplified"])

    def test_empty_authorized_corpus_abstains_before_model_call(self) -> None:
        chat = AgentChat()
        result = self._workflow(chat).run(
            "Who is president?", scopes=("guest",), collection="private"
        )
        self.assertTrue(result.abstained)
        self.assertIn("no authorized sources", result.answer)
        self.assertEqual(chat.calls, [])

    def test_repeated_action_returns_safe_abstention(self) -> None:
        class LoopChat:
            label = "test:loop"

            def __init__(self) -> None:
                self.calls = 0

            def complete(self, messages, **kwargs):  # type: ignore[no-untyped-def]
                del messages, kwargs
                self.calls += 1
                if self.calls == 1:
                    return json.dumps({"obligations": [{"id": "1", "question": "How much memory?"}], "skills": []})
                return json.dumps({"action": "search", "purpose": "Try again", "arguments": {"query": "Atlas memory"}})

        chat = LoopChat()
        result = self._workflow(chat).run(
            "How much memory does Atlas have?", scopes=("owner",), collection="private"
        )
        self.assertTrue(result.abstained)
        self.assertIn("stalled", [event.detail.get("kind") for event in result.events])

    def test_invalid_decision_gets_one_bounded_repair_opportunity(self) -> None:
        class RepairChat:
            label = "test:repair"

            def __init__(self) -> None:
                self.inner = AgentChat()
                self.calls = 0

            def complete(self, messages, **kwargs):  # type: ignore[no-untyped-def]
                self.calls += 1
                if self.calls == 2:
                    return json.dumps({"action": "search", "query": "Atlas memory"})
                return self.inner.complete(messages, **kwargs)

        chat = RepairChat()
        result = self._workflow(chat, max_steps=4).run(
            "How much memory does Atlas have?", scopes=("owner",), collection="private"
        )
        self.assertFalse(result.abstained)
        self.assertEqual(chat.calls, 5)
        self.assertIn("validation_rejected", [event.kind for event in result.events])

    def test_fabricated_agent_citation_is_rejected_before_review(self) -> None:
        chat = AgentChat(fabricated_citation=True)
        result = self._workflow(chat).run(
            "How much memory does Atlas have?", scopes=("owner",), collection="private"
        )
        self.assertTrue(result.abstained)
        self.assertEqual(result.citations, ())
        self.assertIn("validation_rejected", [event.kind for event in result.events])
        self.assertNotIn("review_completed", [event.kind for event in result.events])

    def test_rejected_review_abstains_at_hard_step_cap(self) -> None:
        chat = AgentChat(accept_review=False)
        result = self._workflow(chat, max_steps=2).run(
            "How much memory does Atlas have?", scopes=("owner",), collection="private"
        )
        self.assertTrue(result.abstained)
        self.assertIn("budget_exhausted", [event.kind for event in result.events])

    def test_conflicting_review_fields_cannot_approve_an_answer(self) -> None:
        chat = AgentChat(contradictory_review=True)
        result = self._workflow(chat, max_steps=2).run(
            "How much memory does Atlas have?", scopes=("owner",), collection="private"
        )
        self.assertTrue(result.abstained)
        reviews = [event for event in result.events if event.kind == "review_completed"]
        self.assertFalse(reviews[0].detail["accepted"])

    def test_agent_events_are_scored_in_experiment_summary(self) -> None:
        case = ExperimentCase(
            "agent-1", "How much memory does Atlas have?", "private", ("owner",)
        )
        records = ExperimentRunner().run([case], [self._workflow(AgentChat())])
        summary = summarize_experiments(records, [case])[0]
        self.assertEqual(summary["tool_call_count"], 1)
        self.assertEqual(summary["tool_failure_rate"], 0.0)
        self.assertEqual(summary["review_count"], 1)
        self.assertEqual(summary["review_rejection_rate"], 0.0)
        self.assertEqual(summary["skill_load_count"], 1)

    def test_tools_are_read_only_bounded_and_acl_preserving(self) -> None:
        gateway = ReadOnlyToolGateway(
            HybridRetriever(self.store, self.embedder),
            self.store,
            scopes=("guest",),
            collection="private",
            budget=ToolBudget(max_searches=1),
        )
        result = gateway.execute("search", {"query": "Atlas memory"})
        self.assertEqual(result.output["hits"], [])
        with self.assertRaisesRegex(WorkflowError, "budget exhausted"):
            gateway.execute("search", {"query": "Atlas"})
        with self.assertRaisesRegex(WorkflowError, "allowlisted"):
            gateway.execute("shell", {"command": "whoami"})

    def test_safe_calculator_rejects_code_execution(self) -> None:
        gateway = ReadOnlyToolGateway(
            HybridRetriever(self.store, self.embedder),
            self.store,
            scopes=("owner",),
            collection="private",
        )
        self.assertEqual(gateway.execute("calculate", {"expression": "(64 * 2) + 1"}).output["result"], "129")
        with self.assertRaisesRegex(WorkflowError, "invalid or unsafe"):
            gateway.execute("calculate", {"expression": "__import__('os').system('whoami')"})

    def test_lookup_requires_a_source_observed_through_authorized_search(self) -> None:
        gateway = ReadOnlyToolGateway(
            HybridRetriever(self.store, self.embedder),
            self.store,
            scopes=("owner",),
            collection="private",
        )
        with self.assertRaisesRegex(WorkflowError, "returned by search"):
            gateway.execute(
                "lookup",
                {"source_version_id": "version_unknown", "start_char": 0, "end_char": 5},
            )
        search = gateway.execute("search", {"query": "Atlas memory"})
        source_version_id = search.output["hits"][0]["source_version_id"]
        lookup = gateway.execute(
            "lookup",
            {"source_version_id": source_version_id, "start_char": 0, "end_char": 7},
        )
        self.assertEqual(lookup.output["content"], "# Atlas")


class SkillRegistryTests(unittest.TestCase):
    def test_skill_hash_and_frontmatter_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory, "review")
            folder.mkdir()
            Path(folder, "SKILL.md").write_text(
                "---\nname: review\ndescription: Review evidence.\n---\nBe precise.\n",
                encoding="utf-8",
            )
            skill = SkillRegistry(directory).load("review")
            self.assertEqual(skill.name, "review")
            self.assertEqual(len(skill.sha256), 64)

    def test_unknown_frontmatter_fields_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory, "bad")
            folder.mkdir()
            Path(folder, "SKILL.md").write_text(
                "---\nname: bad\ndescription: Bad.\ncommand: whoami\n---\nDo things.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ConfigurationError, "only name and description"):
                SkillRegistry(directory).discover()

    def test_standard_agent_skill_metadata_and_provenance_are_supported(self) -> None:
        with tempfile.TemporaryDirectory() as project, tempfile.TemporaryDirectory() as standard:
            folder = Path(standard, "ad-creative")
            folder.mkdir()
            Path(folder, "SKILL.md").write_text(
                "---\nname: ad-creative\ndescription: Generate reviewed ad variants.\n"
                "metadata:\n  version: 1.0.0\n---\nCreate truthful variants.\n",
                encoding="utf-8",
            )
            metadata = SkillRegistry(project, additional_roots=(standard,)).metadata()
            self.assertEqual(metadata[0]["name"], "ad-creative")
            self.assertEqual(metadata[0]["source"], "agent-skills")


if __name__ == "__main__":
    unittest.main()
