from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from _bootstrap import SRC  # noqa: F401
from agenticrag.domain import SourceDraft
from agenticrag.experiments import (
    ExperimentCase,
    ExperimentRunner,
    JsonlRunJournal,
    summarize_experiments,
)
from agenticrag.ingestion import Ingestor
from agenticrag.retrieval import HybridRetriever
from agenticrag.store import SQLiteCorpusStore
from agenticrag.workflows import FixedRAGWorkflow
from fakes import DeterministicEmbedding, StaticChat


class CitingChat(StaticChat):
    def __init__(self, chunk_id: str) -> None:
        super().__init__(
            json.dumps(
                {
                    "answer": "Atlas has 64 GB of memory.",
                    "citations": [chunk_id],
                    "quotes": {chunk_id: ["Atlas has 64 GB of memory."]},
                    "abstained": False,
                }
            )
        )


class ExperimentJournalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = SQLiteCorpusStore(":memory:")
        self.store.initialize()
        self.embedding = DeterministicEmbedding()
        Ingestor(self.store, self.embedding).ingest_source(
            SourceDraft(
                "private",
                "/corpus/atlas.md",
                "text/markdown",
                "Atlas has 64 GB of memory.",
                ("owner",),
            )
        )
        self.retriever = HybridRetriever(self.store, self.embedding)
        self.chunk_id = self.retriever.retrieve(
            "Atlas memory", scopes=("owner",), collection="private"
        )[0].chunk.id

    def tearDown(self) -> None:
        self.store.close()

    def test_journal_records_started_and_terminal_manifest(self) -> None:
        case = ExperimentCase(
            "atlas-1",
            "How much memory does Atlas have?",
            "private",
            ("owner",),
            answerable=True,
            required_chunk_ids=(self.chunk_id,),
            expected_answer_contains=("64 GB",),
        )
        workflow = FixedRAGWorkflow(self.retriever, CitingChat(self.chunk_id))
        with tempfile.TemporaryDirectory() as directory:
            journal = JsonlRunJournal(Path(directory) / "runs.jsonl")
            terminal = ExperimentRunner(journal).run([case], [workflow])
            all_records = journal.read()
            self.assertEqual([record.status for record in all_records], ["started", "completed"])
            self.assertEqual(all_records[0].run_id, all_records[1].run_id)
            replayed = journal.terminal_records()
            self.assertEqual(len(replayed), 1)
            self.assertEqual(replayed[0].run_id, terminal[0].run_id)
            self.assertEqual(replayed[0].status, terminal[0].status)
            self.assertEqual(all_records[0].manifest["workflow_version"], "fixed-rag-v1")
            self.assertEqual(all_records[0].embedding_provider, self.embedding.label)

    def test_started_only_run_is_reported_as_incomplete(self) -> None:
        case = ExperimentCase(
            "atlas-1",
            "Question",
            "private",
            ("owner",),
            answerable=True,
            required_chunk_ids=(self.chunk_id,),
            expected_answer_contains=("64 GB",),
        )
        workflow = FixedRAGWorkflow(self.retriever, CitingChat(self.chunk_id))
        started = ExperimentRunner._record("run-incomplete", case, workflow, status="started")
        with tempfile.TemporaryDirectory() as directory:
            journal = JsonlRunJournal(Path(directory) / "runs.jsonl")
            journal.append(started)
            summary = summarize_experiments(journal.latest_records(), [case])[0]
        self.assertEqual(summary["incomplete_count"], 1)
        self.assertEqual(summary["failure_rate"], 1.0)
        self.assertEqual(summary["evidence_recall"], 0.0)
        self.assertEqual(summary["answer_substring_accuracy"], 0.0)

    def test_metrics_report_denominators_and_deterministic_scores(self) -> None:
        answerable = ExperimentCase(
            "atlas-1",
            "How much memory does Atlas have?",
            "private",
            ("owner",),
            answerable=True,
            required_chunk_ids=(self.chunk_id,),
            required_quotes=({"logical_path": "/corpus/atlas.md", "quote": "64 GB of memory"},),
            expected_answer_contains=("64 GB",),
        )
        unanswerable = ExperimentCase(
            "atlas-2",
            "What is the Atlas CPU serial number?",
            "private",
            ("guest",),
            answerable=False,
        )
        workflow = FixedRAGWorkflow(self.retriever, CitingChat(self.chunk_id))
        records = ExperimentRunner().run([answerable, unanswerable], [workflow])
        summary = summarize_experiments(records, [answerable, unanswerable])[0]
        self.assertEqual(summary["failure_rate"], 0.0)
        self.assertEqual(summary["evidence_recall"], 1.0)
        self.assertEqual(summary["quote_evidence_recall"], 1.0)
        self.assertEqual(summary["metric_denominators"]["required_quotes"], 1)
        self.assertEqual(summary["answer_substring_accuracy"], 1.0)
        self.assertEqual(summary["appropriate_abstention"], 1.0)
        self.assertEqual(summary["citation_resolution_rate"], 1.0)
        self.assertEqual(summary["inline_citation_coverage"], 1.0)
        self.assertEqual(summary["metric_denominators"]["answer_cases"], 1)

    def test_corrupt_journal_is_rejected_with_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runs.jsonl"
            path.write_text("{}\nnot-json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 1"):
                JsonlRunJournal(path).read()

    def test_repeated_run_keeps_failures_and_continues_to_next_case(self) -> None:
        class FailingWorkflow:
            name = "failing"
            provider_label = "local:test@loopback"
            embedding_provider_label = None
            manifest = {"workflow_version": "test-v1"}

            def run(self, question, *, scopes, collection):  # type: ignore[no-untyped-def]
                del question, scopes, collection
                raise RuntimeError("unexpected model failure")

        cases = [
            ExperimentCase("first", "First?", "private", ("owner",)),
            ExperimentCase("second", "Second?", "private", ("owner",)),
        ]
        with tempfile.TemporaryDirectory() as directory:
            journal = JsonlRunJournal(Path(directory) / "runs.jsonl")
            records = ExperimentRunner(journal).run(cases, [FailingWorkflow()], repeat=2)
            replayed = journal.latest_records()
        self.assertEqual(len(records), 4)
        self.assertEqual([record.case_id for record in records], ["first", "second", "first", "second"])
        self.assertEqual([record.manifest["repeat_index"] for record in records], [1, 1, 2, 2])
        self.assertTrue(all(record.status == "failed" for record in replayed))
        self.assertTrue(all("RuntimeError" in (record.error_trace or "") for record in replayed))


if __name__ == "__main__":
    unittest.main()
