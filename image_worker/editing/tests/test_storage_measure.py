"""Synthetic filesystem checks only; do not load weights or invoke a worker."""

import importlib.util
import os
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "storage_measure.py"
spec = importlib.util.spec_from_file_location("pe1_storage_measure", SOURCE)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
StorageMeter = module.StorageMeter


def test_tracks_temporary_high_water_after_cleanup(tmp_path):
    moments = iter([10.0, 10.1, 10.2, 10.3, 10.4])
    meter = StorageMeter(tmp_path, clock=lambda: next(moments))
    assert meter.sample()["logical_bytes"] == 0
    (tmp_path / "original").write_bytes(b"a" * 100)
    (tmp_path / "reference.png").write_bytes(b"b" * 200)
    meter.sample()
    (tmp_path / ".partial.png").write_bytes(b"c" * 500)
    assert meter.sample()["logical_bytes"] == 800
    (tmp_path / ".partial.png").unlink()
    assert meter.sample()["logical_bytes"] == 300
    report = meter.report()
    assert report["peak_observed_logical_bytes"] == 800
    assert report["largest_sample_gap_seconds"] == pytest.approx(0.1)
    assert "not a proven absolute peak" in report["limits"]


def test_atomic_rename_does_not_double_count(tmp_path):
    meter = StorageMeter(tmp_path)
    (tmp_path / ".partial.png").write_bytes(b"a" * 1024)
    meter.sample()
    os.replace(tmp_path / ".partial.png", tmp_path / "image.png")
    row = meter.sample()
    assert row["logical_bytes"] == 1024 and row["file_count"] == 1
    assert meter.report()["peak_observed_logical_bytes"] == 1024


def test_hardlinks_have_separate_logical_and_unique_totals(tmp_path):
    (tmp_path / "original").write_bytes(b"a" * 123)
    os.link(tmp_path / "original", tmp_path / "pinned-original")
    row = StorageMeter(tmp_path).sample()
    assert row["logical_bytes"] == 246
    assert row["unique_inode_bytes"] == 123
    assert row["file_count"] == 2 and row["unique_inode_count"] == 1
    assert (
        row["reported_allocated_bytes"]
        == (tmp_path / "original").stat().st_blocks * 512
    )


def test_includes_nested_files_without_reading_contents(tmp_path, monkeypatch):
    (tmp_path / "working").mkdir()
    (tmp_path / "working/image.png").write_bytes(b"synthetic" * 3)
    monkeypatch.setattr(
        Path, "read_bytes", lambda _: pytest.fail("must not read contents")
    )
    report = StorageMeter(tmp_path)
    assert report.sample()["logical_bytes"] == 27
    assert "image.png" not in str(report.report())


@pytest.mark.parametrize("directory", [False, True])
def test_refuses_symlink_children(tmp_path, directory):
    outside = tmp_path.parent / ("outside-dir" if directory else "outside-file")
    if directory:
        outside.mkdir()
    else:
        outside.write_bytes(b"not case data")
    (tmp_path / "link").symlink_to(outside, target_is_directory=directory)
    with pytest.raises(ValueError, match="symlinks"):
        StorageMeter(tmp_path).sample()


def test_refuses_symlink_root(tmp_path):
    (tmp_path / "real").mkdir()
    (tmp_path / "link").symlink_to(tmp_path / "real", target_is_directory=True)
    with pytest.raises(ValueError, match="private case directory"):
        StorageMeter(tmp_path / "link")


def test_bounds_samples_and_requires_observation(tmp_path):
    meter = StorageMeter(tmp_path, limit=1)
    with pytest.raises(ValueError, match="No storage observations"):
        meter.report()
    meter.sample()
    with pytest.raises(ValueError, match="sample budget"):
        meter.sample()


def test_counts_metadata_logical_bytes(tmp_path):
    meter = StorageMeter(tmp_path)
    (tmp_path / "metadata.json").write_bytes(b"{}")
    row = meter.sample()
    assert row["logical_bytes"] == row["unique_inode_bytes"] == 2
    assert row["reported_allocated_bytes"] >= 0
