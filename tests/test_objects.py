from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from _bootstrap import SRC  # noqa: F401
from agenticrag.errors import IngestionError
from agenticrag.objects import LocalObjectStore


class LocalObjectStoreTests(unittest.TestCase):
    def test_delete_verifies_and_removes_only_the_requested_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = LocalObjectStore(directory)
            first_path, first_hash = store.put_text("temporary web text")
            second_path, second_hash = store.put_text("permanent library text")
            store.delete(first_path, first_hash)
            self.assertFalse(Path(directory, *first_path.split("/")).exists())
            self.assertEqual(store.get_text(second_path, second_hash), "permanent library text")

    def test_put_is_content_addressed_idempotent_and_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = LocalObjectStore(directory)
            first_path, first_hash = store.put_text("Atlas inventory")
            second_path, second_hash = store.put_text("Atlas inventory")
            self.assertEqual((first_path, first_hash), (second_path, second_hash))
            self.assertEqual(first_hash, hashlib.sha256(b"Atlas inventory").hexdigest())
            self.assertEqual(store.get_text(first_path, first_hash), "Atlas inventory")

    def test_integrity_failure_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = LocalObjectStore(directory)
            relative, sha256 = store.put_text("original")
            target = Path(directory).joinpath(*relative.split("/"))
            target.write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(IngestionError, "integrity"):
                store.get_text(relative, sha256)

    def test_binary_original_is_content_addressed_and_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = LocalObjectStore(directory)
            relative, sha256 = store.put_bytes(b"%PDF-\x00\xff", suffix=".pdf")
            self.assertTrue(relative.endswith(".pdf"))
            self.assertEqual(store.get_bytes(relative, sha256), b"%PDF-\x00\xff")

    def test_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = LocalObjectStore(directory)
            with self.assertRaisesRegex(IngestionError, "safe relative"):
                store.get_text("../outside.txt", "0" * 64)


if __name__ == "__main__":
    unittest.main()
