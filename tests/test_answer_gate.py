from __future__ import annotations

import unittest
from dataclasses import replace

from _bootstrap import SRC  # noqa: F401
from agenticrag.answer_gate import check_answer
from agenticrag.domain import Chunk, Citation, RankedChunk
from agenticrag.errors import WorkflowError


def fixture() -> tuple[Citation, RankedChunk]:
    chunk = Chunk("chunk_a", "version_a", "doc_a", "private", "note.md", 0,
                  "Atlas has 64 GB of memory. It has two drives.", None, 0, 46)
    citation = Citation("chunk_a", "version_a", "note.md", 0, 46,
                        quotes=("Atlas has 64 GB of memory.",))
    return citation, RankedChunk(chunk, 1.0)


class AnswerGateTests(unittest.TestCase):
    def test_verifies_quote_and_adds_single_marker(self) -> None:
        citation, evidence = fixture()
        gate = check_answer("Atlas has 64 GB of memory.", False, (citation,), (evidence,))
        self.assertEqual(gate.answer, "Atlas has 64 GB of memory. [1]")
        self.assertEqual(gate.checks["quote_verification"], "passed")
        self.assertEqual(gate.marker_repairs, 1)

    def test_wrong_quote_is_rejected_even_when_id_exists(self) -> None:
        citation, evidence = fixture()
        with self.assertRaisesRegex(WorkflowError, "quote is absent"):
            check_answer("Atlas has 64 GB.", False,
                         (replace(citation, quotes=("Atlas has 600 GB.",)),), (evidence,))

    def test_numeric_claim_must_appear_in_cited_source(self) -> None:
        citation, evidence = fixture()
        with self.assertRaisesRegex(WorkflowError, "600.*absent"):
            check_answer("Atlas has 600 GB [1].", False, (citation,), (evidence,))
        gate = check_answer("1. Atlas has 64 GB [1].\n2. It has two drives [1].", False,
                            (citation,), (evidence,))
        self.assertIn("2. It has two drives", gate.answer)

    def test_code_indexes_are_not_citations_or_numeric_claims(self) -> None:
        citation, evidence = fixture()
        gate = check_answer("Use `arr[3]`. Atlas has 64 GB [1].", False, (citation,), (evidence,))
        self.assertIn("`arr[3]`", gate.answer)

    def test_abstention_cannot_carry_citations(self) -> None:
        citation, evidence = fixture()
        with self.assertRaisesRegex(WorkflowError, "abstained answer"):
            check_answer("Unknown [1].", True, (citation,), (evidence,))

    def test_web_only_is_explicitly_partially_unverified(self) -> None:
        gate = check_answer("A web answer.", False, (), (), external_sources=True)
        self.assertEqual(gate.checks["numeric_grounding"], "external_unverified")


if __name__ == "__main__":
    unittest.main()
