"""Materialize the reviewed harness correction without changing trial inputs."""

import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ORIGINAL = OUT.parent / "search-repair"


def main():
    assert not (OUT / "cases.json").exists(), "Retest already prepared; do not overwrite."
    spec = importlib.util.spec_from_file_location(
        "offline_verifier", ORIGINAL / "verify_harness.py"
    )
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = (ORIGINAL / "experiment.py").read_text()
    corrected = helper.proposed_patch(source)
    (OUT / "experiment.py").write_text(corrected)
    for name in ("cases.json", "prompts.json", "execution.json", "validate.py"):
        shutil.copyfile(ORIGINAL / name, OUT / name)
    shutil.copytree(ORIGINAL / "fixtures", OUT / "fixtures")
    (OUT / "preparation.json").write_text(
        json.dumps(
            {
                "previous_trial": "b5b4292; invalid planner instrumentation retained",
                "change": (
                    "Reviewed request-bound schema observation, error recording and protocol gate"
                ),
                "unchanged_inputs": ["cases.json", "prompts.json", "execution.json", "fixtures/"],
                "new_output_directory": str(OUT.relative_to(ROOT)),
                "production_edits": [],
                "real_model_calls": 0,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
