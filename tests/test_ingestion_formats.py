from __future__ import annotations

import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from _bootstrap import SRC  # noqa: F401
from agenticrag.domain import ProvenanceSpan, SourceDraft
from agenticrag.errors import IngestionError
from agenticrag.ingestion import FileParser, IngestionLimits, Ingestor, TextChunker
from agenticrag.store import SQLiteCorpusStore
from fakes import DeterministicEmbedding


class MultiFormatIngestionTests(unittest.TestCase):
    def test_markdown_has_stable_offsets_and_section_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "guide.md")
            path.write_text("# Install\n\nRun locally.\n\n| A | B |\n| - | - |", encoding="utf-8")
            source = FileParser().parse(path, "docs", ("team",))

        self.assertEqual(source.original_sha256, hashlib.sha256(source.original_bytes).hexdigest())
        self.assertEqual(source.parser_id, "builtin-markdown-v2")
        self.assertEqual(source.provenance[0].kind, "heading")
        self.assertEqual(source.provenance[-1].kind, "table")
        self.assertEqual(source.provenance[-1].section_path, ("Install",))
        for span in source.provenance:
            self.assertEqual(source.text[span.start_char : span.end_char].strip(), source.text[span.start_char : span.end_char])

    def test_docx_preserves_headings_paragraphs_and_tables_without_heavy_dependencies(self) -> None:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Hardware</w:t></w:r></w:p>
<w:p><w:r><w:t>Atlas has 64 GB.</w:t></w:r></w:p>
<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Host</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>RAM</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
</w:body></w:document>"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "inventory.docx")
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("[Content_Types].xml", "<Types/>")
                archive.writestr("word/document.xml", xml)
            source = FileParser().parse(path, "docs", ("team",))

        self.assertIn("Atlas has 64 GB.", source.text)
        table = next(span for span in source.provenance if span.kind == "table")
        self.assertEqual(table.section_path, ("Hardware",))
        self.assertEqual(table.table_id, "table-1")
        self.assertIsNone(table.page_no)

    def test_spoofed_type_and_bounded_files_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory, "fake.pdf")
            pdf.write_text("not a pdf", encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "file signature"):
                FileParser().parse(pdf, "docs", ("team",))

            large = Path(directory, "large.txt")
            large.write_text("12345", encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "limit"):
                FileParser(limits=IngestionLimits(max_file_bytes=4)).parse(
                    large, "docs", ("team",)
                )

    def test_missing_pdf_and_ocr_capabilities_have_actionable_local_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "manual.pdf")
            path.write_bytes(b"%PDF-1.7\n")
            with mock.patch("agenticrag.ingestion.importlib.util.find_spec", return_value=None):
                with self.assertRaisesRegex(IngestionError, "documents.*extra"):
                    FileParser(ocr="never").parse(path, "docs", ("team",))
                with self.assertRaisesRegex(IngestionError, "Docling"):
                    FileParser(ocr="always").parse(path, "docs", ("team",))

    def test_original_hash_parser_identity_and_chunk_provenance_round_trip(self) -> None:
        original = b"binary-original"
        first = SourceDraft(
            "docs",
            "/source.bin",
            "application/octet-stream",
            "# System\n\nAtlas memory.",
            ("team",),
            original_bytes=original,
            original_sha256=hashlib.sha256(original).hexdigest(),
            parser_id="parser-v1",
            provenance=(
                ProvenanceSpan("seg-1", "paragraph", 10, 23, page_no=2, section_path=("System",)),
            ),
        )
        second = SourceDraft(
            **{
                **first.__dict__,
                "text": "# System\n\nAtlas memory normalized.",
                "parser_id": "parser-v2",
                "provenance": (
                    ProvenanceSpan(
                        "seg-2", "paragraph", 10, 34, page_no=2, section_path=("System",)
                    ),
                ),
            }
        )
        provenance_changed = SourceDraft(
            **{
                **first.__dict__,
                "provenance": (
                    ProvenanceSpan(
                        "seg-1", "paragraph", 10, 23, page_no=3, section_path=("System",)
                    ),
                ),
            }
        )
        store = SQLiteCorpusStore(":memory:")
        store.initialize()
        try:
            ingestor = Ingestor(
                store,
                DeterministicEmbedding(),
                TextChunker(max_chars=240, overlap_chars=20),
            )
            v1 = ingestor.ingest_source(first)
            v3 = ingestor.ingest_source(provenance_changed)
            v2 = ingestor.ingest_source(second)
            self.assertEqual(v1.sha256, v2.sha256)
            self.assertNotEqual(v1.id, v2.id)
            self.assertNotEqual(v1.parsed_sha256, v2.parsed_sha256)
            self.assertNotEqual(v1.id, v3.id)
            self.assertEqual(v1.parsed_sha256, v3.parsed_sha256)
            self.assertNotEqual(v1.provenance_sha256, v3.provenance_sha256)
            stored_original = store.connection.execute(
                "SELECT content, byte_size FROM source_objects WHERE sha256 = ?", (v1.sha256,)
            ).fetchone()
            self.assertEqual(bytes(stored_original["content"]), original)
            self.assertEqual(stored_original["byte_size"], len(original))
            hits = store.lexical_search(
                "normalized",
                embedding_label=DeterministicEmbedding.label,
                scopes=("team",),
                collection="docs",
                limit=5,
            )
            self.assertEqual(hits[0].chunk.page_start, 2)
            self.assertEqual(hits[0].chunk.section_path, ("System",))
            self.assertEqual(hits[0].chunk.provenance[0].segment_id, "seg-2")
        finally:
            store.close()

    def test_declared_original_digest_is_verified(self) -> None:
        source = SourceDraft(
            "docs",
            "/bad.txt",
            "text/plain",
            "content",
            ("team",),
            original_bytes=b"content",
            original_sha256="0" * 64,
        )
        store = SQLiteCorpusStore(":memory:")
        store.initialize()
        try:
            with self.assertRaisesRegex(IngestionError, "declared SHA-256"):
                Ingestor(store, DeterministicEmbedding()).ingest_source(source)
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
