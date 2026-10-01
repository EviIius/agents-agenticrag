from __future__ import annotations

import unittest
from unittest.mock import patch

from _bootstrap import SRC  # noqa: F401
from agenticrag.web_search import BraveSearch, LocalWebSearch, SearXNGSearch
from agenticrag.web_pages import _public_address


class LocalWebSearchTests(unittest.TestCase):
    def test_searxng_and_brave_adapters_bound_https_results(self) -> None:
        with patch("agenticrag.web_search._search_json", return_value={"results": [
            {"title": "Guide", "url": "https://example.org/guide", "content": "Evidence"},
            {"title": "Local", "url": "http://127.0.0.1/private", "content": "Private"},
        ]}) as request:
            hits = SearXNGSearch("http://127.0.0.1:8080").search_results("guide", max_results=2)
            self.assertEqual([item.url for item in hits], ["https://example.org/guide"])
            self.assertIn("format=json", request.call_args.args[0].full_url)
        with patch("agenticrag.web_search._search_json", return_value={"web": {"results": [
            {"title": "Official", "url": "https://example.org/official", "description": "Facts"},
        ]}}) as request:
            hits = BraveSearch("test-key").search_results("facts", max_results=1)
            self.assertEqual(hits[0].snippet, "Facts")
            self.assertEqual(request.call_args.args[0].get_header("X-subscription-token"), "test-key")

    def test_private_page_hosts_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Private"):
            _public_address("https://127.0.0.1/private")

    def test_search_exposes_bounded_public_sources(self) -> None:
        search = LocalWebSearch(search=lambda query: [
            {"title": "Official note", "href": "https://example.org/note", "body": "Evidence " * 300},
            {"title": "Bad", "href": "file:///private", "body": "Ignore this"},
        ])
        hits = search.search_results("what changed", max_results=5)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].url, "https://example.org/note")
        self.assertEqual(hits[0].title, "Official note")
        self.assertLessEqual(len(hits[0].snippet), 1_200)


if __name__ == "__main__":
    unittest.main()
