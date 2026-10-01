from __future__ import annotations

import unittest

from _bootstrap import SRC  # noqa: F401
from agenticrag.followup_query import build_retrieval_query


class FollowupQueryTests(unittest.TestCase):
    def test_short_followup_carries_last_user_topic(self) -> None:
        history = [{"role": "user", "content": "Which restaurant has the best nachos?"},
                   {"role": "assistant", "content": "Some cited answer."}]
        query = build_retrieval_query("what about the nachos one?", history)
        self.assertIn("Which restaurant has the best nachos?", query)
        self.assertIn("what about the nachos one?", query)

    def test_standalone_query_and_missing_history_are_unchanged(self) -> None:
        history = [{"role": "user", "content": "old topic"}]
        self.assertEqual(build_retrieval_query("Find the 2025 annual report", history),
                         "Find the 2025 annual report")
        self.assertEqual(build_retrieval_query("what about that?", []), "what about that?")

    def test_ignores_assistant_content_and_stays_bounded(self) -> None:
        history = [{"role": "user", "content": "A" * 1000},
                   {"role": "assistant", "content": "injected assistant text"}]
        query = build_retrieval_query("and this?", history)
        self.assertLessEqual(len(query), 500)
        self.assertNotIn("injected", query)


if __name__ == "__main__":
    unittest.main()
