from __future__ import annotations

import unittest

from _bootstrap import SRC  # noqa: F401
from agenticrag.domain import SourceDraft
from agenticrag.errors import AuthorizationError, IngestionError
from agenticrag.ingestion import Ingestor, TextChunker
from agenticrag.store import SQLiteCorpusStore
from fakes import DeterministicEmbedding


class SQLiteCorpusStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = SQLiteCorpusStore(":memory:")
        self.store.initialize()
        self.embedder = DeterministicEmbedding()
        self.ingestor = Ingestor(
            self.store,
            self.embedder,
            TextChunker(max_chars=240, overlap_chars=20),
        )

    def tearDown(self) -> None:
        self.store.close()

    def _source(self, text: str, scopes: tuple[str, ...] = ("owner",)) -> SourceDraft:
        return SourceDraft(
            collection="private",
            logical_path="/corpus/atlas.md",
            media_type="text/markdown",
            text=text,
            scopes=scopes,
        )

    def test_identical_ingestion_is_idempotent_and_changed_content_versions(self) -> None:
        first = self.ingestor.ingest_source(self._source("# Atlas\nAtlas uses server S-1."))
        repeated = self.ingestor.ingest_source(self._source("# Atlas\nAtlas uses server S-1."))
        changed = self.ingestor.ingest_source(self._source("# Atlas\nAtlas uses server S-2."))
        self.assertEqual(first.id, repeated.id)
        self.assertNotEqual(first.id, changed.id)

        hits = self.store.lexical_search(
            "S-2",
            embedding_label=self.embedder.label,
            scopes=("owner",),
            collection="private",
            limit=10,
        )
        self.assertTrue(hits)
        self.assertTrue(all(hit.chunk.source_version_id == changed.id for hit in hits))
        old_hits = self.store.lexical_search(
            "S-1",
            embedding_label=self.embedder.label,
            scopes=("owner",),
            collection="private",
            limit=10,
        )
        self.assertEqual(old_hits, [])

    def test_adjacent_query_terms_prioritize_the_relevant_sentence(self) -> None:
        self.ingestor.ingest_source(self._source("# Architecture\n" + "architecture source " * 12))
        self.ingestor.ingest_source(
            SourceDraft(
                "private", "/corpus/scopes.md", "text/markdown",
                "The authenticated application supplies scopes.", ("owner",),
            )
        )
        hits = self.store.lexical_search(
            "According to the architecture source, who supplies scopes?",
            embedding_label=self.embedder.label,
            scopes=("owner",), collection="private", limit=10,
        )
        self.assertIn("supplies scopes", hits[0].chunk.text)

    def test_scope_is_applied_before_lexical_vector_and_source_fetch(self) -> None:
        version = self.ingestor.ingest_source(self._source("Atlas has 64 GB of memory."))
        lexical = self.store.lexical_search(
            "Atlas memory",
            embedding_label=self.embedder.label,
            scopes=("guest",),
            collection="private",
            limit=10,
        )
        vector = self.store.vector_search(
            self.embedder.embed(["Atlas memory"])[0],
            embedding_label=self.embedder.label,
            scopes=("guest",),
            collection="private",
            limit=10,
        )
        self.assertEqual(lexical, [])
        self.assertEqual(vector, [])
        with self.assertRaises(AuthorizationError):
            self.store.get_source(version.id, scopes=("guest",))

        authorized = self.store.get_source(version.id, scopes=("owner",))
        self.assertEqual(authorized.text, "Atlas has 64 GB of memory.")

    def test_source_listing_returns_only_current_authorized_versions(self) -> None:
        first = self.ingestor.ingest_source(self._source("Atlas version one."))
        current = self.ingestor.ingest_source(self._source("Atlas version two."))
        self.assertNotEqual(first.id, current.id)
        self.assertEqual(self.store.list_sources(scopes=("guest",), collection="private"), [])
        sources = self.store.list_sources(scopes=("owner",), collection="private")
        self.assertTrue(all(source.title for source in sources))
        self.assertEqual([source.id for source in sources], [current.id])
        self.assertIsNone(sources[0].text)

    def test_permission_change_creates_immutable_version(self) -> None:
        private = self.ingestor.ingest_source(self._source("Atlas inventory."))
        shared = self.ingestor.ingest_source(self._source("Atlas inventory.", ("owner", "team")))
        self.assertNotEqual(private.id, shared.id)
        self.assertEqual(private.sha256, shared.sha256)
        team_hits = self.store.lexical_search(
            "inventory",
            embedding_label=self.embedder.label,
            scopes=("team",),
            collection="private",
            limit=10,
        )
        self.assertTrue(team_hits)
        self.assertTrue(all(hit.chunk.source_version_id == shared.id for hit in team_hits))

    def test_embedding_dimension_change_requires_new_index_generation(self) -> None:
        self.ingestor.ingest_source(self._source("Atlas inventory."))

        class ChangedEmbedding:
            label = "test:changed"

            def embed(self, texts: list[str]) -> list[list[float]]:
                return [[1.0, 2.0] for _ in texts]

        with self.assertRaisesRegex(IngestionError, "new index generation"):
            Ingestor(self.store, ChangedEmbedding()).ingest_source(
                SourceDraft("private", "/corpus/other.md", "text/markdown", "Other source.", ("owner",))
            )

    def test_query_provider_must_match_index_generation(self) -> None:
        self.ingestor.ingest_source(self._source("Atlas inventory."))
        with self.assertRaisesRegex(IngestionError, "does not match"):
            self.store.vector_search(
                self.embedder.embed(["Atlas"])[0],
                embedding_label="other:model@localhost",
                scopes=("owner",),
                collection="private",
                limit=10,
            )


if __name__ == "__main__":
    unittest.main()
