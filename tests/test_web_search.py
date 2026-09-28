from __future__ import annotations

import unittest

from _bootstrap import SRC  # noqa: F401
from agenticrag.web_search import LocalWebSearch
from agenticrag.web_pages import _public_address
from agenticrag.workflows import WebAnswerWorkflow


class LocalWebSearchTests(unittest.TestCase):
    def test_web_answer_reports_search_and_generation_timing(self) -> None:
        class Chat:
            label = "local:test"

            def complete(self, messages, **kwargs):
                self.messages = messages
                return "Verified answer [1]"

            def last_call_metrics(self):
                return {"request_attempts": 1, "prompt_tokens": 150, "completion_tokens": 8}

        chat = Chat()
        search = LocalWebSearch(search=lambda query: [
            {"title": "Source", "href": "https://example.org/source", "body": "Verified evidence"},
        ])
        result = WebAnswerWorkflow(chat, web_search=search).run(
            "What happened?", scopes=("private",), collection="research",
        )
        self.assertEqual([event.kind for event in result.events], ["web_search_completed", "generation_completed"])
        self.assertEqual(result.events[1].detail["workflow_model_calls"], 1)
        self.assertEqual(result.events[1].detail["prompt_tokens"], 150)
        self.assertGreater(result.events[0].detail["finding_chars"], 0)

    def test_public_page_text_is_bounded_and_cited(self) -> None:
        search = LocalWebSearch(
            search=lambda query: [{"title": "Guide", "href": "https://example.org/guide", "body": "Summary"}],
            fetch_page=lambda url: ("https://example.org/final", "Verified article text. " * 300),
        )
        result = search.search("guide")
        self.assertIn("Fetched page text (untrusted):", result.answer)
        self.assertEqual(result.sources[0].url, "https://example.org/final")
        self.assertLess(len(result.answer), 4_000)

    def test_private_page_hosts_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Private"):
            _public_address("https://127.0.0.1/private")

    def test_search_exposes_bounded_public_sources(self) -> None:
        search = LocalWebSearch(search=lambda query: [
            {"title": "Official note", "href": "https://example.org/note", "body": "Evidence " * 300},
            {"title": "Bad", "href": "file:///private", "body": "Ignore this"},
        ])
        result = search.search("what changed")
        self.assertEqual(len(result.sources), 1)
        self.assertEqual(result.sources[0].url, "https://example.org/note")
        self.assertIn("[1] Official note", result.answer)
        self.assertLess(len(result.answer), 1_500)


if __name__ == "__main__":
    unittest.main()
