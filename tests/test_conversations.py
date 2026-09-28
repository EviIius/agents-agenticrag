from __future__ import annotations

import tempfile
import unittest
import os
from pathlib import Path

from _bootstrap import SRC  # noqa: F401
from agenticrag.conversations import ConversationStore, conversation_title


class ConversationStoreTests(unittest.TestCase):
    def test_saved_evidence_keeps_retrieval_count_and_uncited_titles(self) -> None:
        store = ConversationStore(":memory:")
        chat = store.create("research", ["private"])
        store.record(chat["id"], "Which source?", {
            "answer": "The first source [1].", "workflow": "fixed", "abstained": False,
            "elapsed_ms": 100, "events": [], "citations": [{"chunk_id": "c1"}],
            "evidence": [
                {"chunk": {"id": "c1", "text": "Cited text", "logical_path": "one.md", "heading": "One"}},
                {"chunk": {"id": "c2", "text": "Uncited text", "logical_path": "two.md", "heading": "Two"}},
            ],
        }, "fixed")
        saved = store.get(chat["id"])["messages"][-1]["result"]
        self.assertEqual(saved["retrieved_count"], 2)
        self.assertEqual(saved["evidence"][0]["chunk"]["text"], "Cited text")
        self.assertEqual(saved["evidence"][1]["chunk"]["logical_path"], "two.md")
        self.assertEqual(saved["evidence"][1]["chunk"]["text"], "")
        store.close()

    def test_web_timing_trace_survives_reopening_chat(self) -> None:
        store = ConversationStore(":memory:")
        chat = store.create("research", ["private"])
        store.record(chat["id"], "Who won?", {
            "answer": "The team won [1].", "workflow": "web_research", "abstained": False,
            "elapsed_ms": 92000, "citations": [], "external_sources": [],
            "events": [
                {"kind": "web_search_completed", "detail": {"elapsed_ms": 1400}},
                {"kind": "generation_completed", "detail": {"elapsed_ms": 90600, "prompt_tokens": 2141}},
                {"kind": "unrelated", "detail": {"text": "discard"}},
            ],
        }, "direct")
        saved = store.get(chat["id"])["messages"][-1]["result"]
        self.assertEqual([event["kind"] for event in saved["events"]], [
            "web_search_completed", "generation_completed",
        ])
        self.assertEqual(saved["events"][1]["detail"]["prompt_tokens"], 2141)
        store.close()

    def test_project_memory_is_editable_and_keeps_chat_provenance(self) -> None:
        store = ConversationStore(":memory:")
        project = store.create_project("Recipes")
        chat = store.create(project["collection"], project["scopes"])
        note = store.create_project_note(project["id"], "Prefer quick dinners.", chat["id"])
        self.assertEqual(note["source_chat_title"], "New conversation")
        self.assertEqual(store.project_for_context(project["collection"], project["scopes"])["id"], project["id"])
        self.assertIsNone(store.project_for_context(project["collection"], ["public"]))
        changed = store.update_project_note(note["id"], "Prefer one-pan dinners.")
        self.assertEqual(changed["content"], "Prefer one-pan dinners.")
        other = store.create("research", ["private"])
        with self.assertRaisesRegex(ValueError, "outside this project"):
            store.create_project_note(project["id"], "Cross-project secret", other["id"])
        store.delete(chat["id"])
        self.assertIsNone(store.list_project_notes(project["id"])[0]["source_chat_id"])
        store.delete_project_note(note["id"])
        self.assertEqual(store.list_project_notes(project["id"]), [])
        activity = store.list_project_note_activity(project["id"])
        self.assertEqual([item["action"] for item in activity], ["deleted", "edited", "created"])
        self.assertNotIn("one-pan", repr(activity))
        store.close()

    def test_projects_group_chats_and_search_saved_messages(self) -> None:
        store = ConversationStore(":memory:")
        self.assertEqual(store.list_projects()[0]["name"], "My library")
        project = store.create_project("Kitchen research")
        chat = store.create(project["collection"], project["scopes"])
        store.record(chat["id"], "How do I make nachos?", {
            "answer": "Add cheese and bake.", "workflow": "direct",
            "abstained": False, "elapsed_ms": 1, "citations": [],
        }, "direct")
        self.assertEqual([item["id"] for item in store.list(collection=project["collection"])], [chat["id"]])
        self.assertEqual([item["id"] for item in store.list(query="cheese")], [chat["id"]])
        self.assertEqual(store.list(query="missing"), [])
        self.assertEqual(store.list(collection="research"), [])
        store.close()

    def test_titles_stay_short_and_keep_first_question(self) -> None:
        self.assertEqual(conversation_title("How do I make nachos? Answer briefly."), "How do I make nachos?")
        self.assertEqual(
            conversation_title("Show a short three-row Markdown table comparing Direct, Fixed RAG, and Agentic"),
            "Show a short three-row Markdown table…",
        )

    def test_reopens_turns_for_model_context_without_crossing_access_labels(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory, "chats.db"))
            store = ConversationStore(path)
            if os.name == "posix":
                self.assertEqual(Path(path).stat().st_mode & 0o777, 0o600)
            chat = store.create("research", ["private"])
            store.record(chat["id"], "How do I make nachos?", {
                "answer": "Layer chips and cheese, then bake.", "workflow": "direct",
                "abstained": False, "elapsed_ms": 20, "citations": [],
            }, "direct")
            store.close()

            reopened = ConversationStore(path)
            history = reopened.history(chat["id"], "research", ["private"])
            self.assertEqual([message.role for message in history], ["user", "assistant"])
            self.assertEqual(history[0].content, "How do I make nachos?")
            self.assertEqual(reopened.get(chat["id"])["title"], "How do I make nachos?")
            with self.assertRaisesRegex(ValueError, "another knowledge base"):
                reopened.history(chat["id"], "research", ["public"])
            reopened.delete(chat["id"])
            self.assertEqual(reopened.list(), [])
            with self.assertRaisesRegex(ValueError, "not found"):
                reopened.get(chat["id"])
            reopened.close()
