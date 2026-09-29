from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from _bootstrap import SRC  # noqa: F401
from agenticrag.evaluation_audit import audit_evaluation_corpus
from agenticrag.experiments import ExperimentCase


class EvaluationAuditTests(unittest.TestCase):
    def test_gold_quote_is_checked_against_named_current_document(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.db"
            with sqlite3.connect(path) as connection:
                connection.executescript(
                    "CREATE TABLE documents (id TEXT, collection_id TEXT, logical_path TEXT, current_version_id TEXT);"
                    "CREATE TABLE source_versions (id TEXT, document_id TEXT, content TEXT, media_type TEXT);"
                    "CREATE TABLE chunks (id TEXT, source_version_id TEXT);"
                    "INSERT INTO documents VALUES ('d1','eval','note.md','v1');"
                    "INSERT INTO source_versions VALUES ('v1','d1','The update was delayed by maintenance.','text/markdown');"
                    "INSERT INTO chunks VALUES ('c1','v1');"
                )
            case = ExperimentCase(
                id="one", question="Why was the update delayed?", collection="eval",
                scopes=("private",), answerable=True, split="dev",
                required_quotes=({"logical_path": "note.md", "quote": "delayed by maintenance"},),
            )
            report = audit_evaluation_corpus(path, [case], min_documents=1, min_chunks=1,
                                             min_questions=1)
            self.assertEqual(report["gold_quotes"], 1)
            self.assertFalse(any("absent from" in issue for issue in report["issues"]))
            wrong = ExperimentCase(**{**case.__dict__, "required_quotes": (
                {"logical_path": "note.md", "quote": "delayed by a network outage"},)})
            report = audit_evaluation_corpus(path, [wrong], min_documents=1, min_chunks=1,
                                             min_questions=1)
            self.assertTrue(any("quote absent" in issue for issue in report["issues"]))


if __name__ == "__main__":
    unittest.main()
