"""Single-slot native-controller checks with synthetic pixels and CPU doubles."""

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parents[1] / "server"), str(HERE.parent / "masked_pair")]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


helpers = module("pair_helpers", HERE.parent / "masked_pair/test_pair.py")
single = module("single_control", HERE / "control.py")


def test_synthetic_forehead_occlusion_retains_visible_features():
    result = subprocess.run(
        [helpers.PYTHON, str(HERE / "synthetic.py")],
        capture_output=True,
        text=True,
        check=True,
    )
    proof = json.loads(result.stdout)
    assert proof["passed"] and proof["forehead_occlusion_allowed"]
    assert (
        proof["protected_features_changed"]
        == proof["outside_changed_pixels"]
        == proof["native_calls"]
        == 0
    )


@pytest.mark.asyncio
async def test_one_success_consumes_allowance_and_qwen_is_undeclared(tmp_path):
    home, codec = await helpers.setup(tmp_path)
    shutil.copyfile(HERE / "control.py", home / "control.py")
    shutil.copyfile(
        HERE.parent / "masked_pair/fake_control_worker.py", home / "flux_worker.py"
    )
    spec = json.loads((home / "pair.json").read_text())
    spec["order"] = ["flux"]
    spec["engines"] = {"flux": spec["engines"]["flux"]}
    spec["maximum_native_invocations"] = 1
    (home / "pair.json").write_text(json.dumps(spec))
    single.new_json(
        tmp_path / "frozen.json",
        {
            "files": {
                str(p.relative_to(tmp_path)): single.digest(p)
                for p in tmp_path.rglob("*")
                if p.is_file()
            }
        },
    )
    single.new_json(
        tmp_path / "approval.json",
        {
            "maximum_native_invocations": 1,
            "frozen_sha256": single.digest(tmp_path / "frozen.json"),
        },
    )
    try:
        result = await single.run_case(
            tmp_path,
            "flux",
            helpers.Capacity(tmp_path / "native.lock"),
            helpers.OfflineEngine(),
            codec,
        )
        assert result["passed"] and result["worker_reaped"]
        with pytest.raises(ValueError, match="allowance"):
            await single.run_case(
                tmp_path,
                "flux",
                helpers.Capacity(tmp_path / "native.lock"),
                helpers.OfflineEngine(),
                codec,
            )
        with pytest.raises(ValueError, match="Undeclared"):
            await single.run_case(
                tmp_path,
                "qwen",
                helpers.Capacity(tmp_path / "native.lock"),
                helpers.OfflineEngine(),
                codec,
            )
        assert len(list((tmp_path / "attempts").glob("*.reserved.json"))) == 1
    finally:
        await codec.close()
