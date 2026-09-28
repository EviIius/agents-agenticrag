from __future__ import annotations

import unittest

from _bootstrap import SRC  # noqa: F401
from agenticrag.cli import build_parser
from agenticrag.cli import _comparison_config, _model_from_label, _write_json_atomic
from agenticrag.config import ProviderRole
import json
import tempfile
from pathlib import Path


class CompareOptionsTests(unittest.TestCase):
    def test_multiple_models_and_supervisor_can_be_selected(self) -> None:
        args = build_parser().parse_args([
            "compare", "cases.jsonl", "--model", "gemma4:12b-mlx", "--model", "gpt-oss:20b",
            "--include-agent", "--include-supervisor",
        ])
        self.assertEqual(args.model, ["gemma4:12b-mlx", "gpt-oss:20b"])
        self.assertTrue(args.include_agent)
        self.assertTrue(args.include_supervisor)

    def test_comparison_reuses_saved_workbench_runtime_and_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db_path = root / "corpus.db"
            (root / "workbench-providers.json").write_text(json.dumps({
                "version": 1,
                "providers": {"chat": {
                    "runtime": "ollama", "base_url": "http://127.0.0.1:11434/v1",
                    "model": "llama3.3:70b-workbench-16k",
                    "structured_output_mode": "json_object", "timeout_seconds": 90,
                }},
            }))
            config = _comparison_config(str(db_path), ProviderRole.CHAT)
            self.assertEqual(config.model, "llama3.3:70b-workbench-16k")
            self.assertEqual(config.runtime, "ollama")
            self.assertEqual(config.structured_output_mode, "json_object")
            report = root / "workbench-evaluation.json"
            _write_json_atomic(report, {"schema_version": 1, "groups": []})
            self.assertEqual(json.loads(report.read_text())["schema_version"], 1)
            self.assertEqual(_model_from_label(config.label), config.model)
