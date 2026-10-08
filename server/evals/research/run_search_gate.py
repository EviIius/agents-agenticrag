"""Run the unchanged Search evaluator in isolated 8-0 output directories."""

import argparse
import asyncio
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE.parents[1]
WEB = HERE.parent / "web"
OUT = SERVER.parent / "artifacts/phase-8/gate"
sys.path.insert(0, str(WEB))
import run_eval as web_eval  # noqa: E402


def settings(mode: str, model: str, search_key_db: str) -> argparse.Namespace:
    research = mode.startswith("baseline")
    return argparse.Namespace(
        case="",
        temperature=None,
        cases_file=str(HERE / "cases.yaml" if research else WEB / "cases.yaml"),
        search_key_db=search_key_db,
        providers="ollama,searxng,exa,ddgs",
        model=model,
        url="http://127.0.0.1:11434",
        live=mode == "release-live",
        record=mode == "baseline-record",
        replay_corpus=mode in {"baseline-replay", "release-replay", "release-hybrid"},
        replay_plans=False,
        table_trial="spec",
        evidence_format="spec",
        ranking="hybrid" if mode == "release-hybrid" else "keyword",
        ranking_query="spec",
        question_first=False,
        fill_trial="spec",
        filter_proof="",
        embedding="qwen3-embedding:0.6b",
        fixture_root=str(OUT / "web-fixtures" if research else WEB / "fixtures"),
        planner_trial="spec",
        answer_trial="spec",
    )


async def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "mode",
        choices=[
            "baseline-record",
            "baseline-replay",
            "release-live",
            "release-replay",
            "release-hybrid",
        ],
    )
    parser.add_argument("--model", default="qwen3:30b-a3b-workbench-32k")
    parser.add_argument("--search-key-db", default="")
    args = parser.parse_args()
    config = settings(args.mode, args.model, args.search_key_db)
    folder = OUT / args.mode
    folder.mkdir(parents=True, exist_ok=True)
    # HERE controls report destinations only; product paths, prompts and fixtures
    # remain those imported by the original evaluator before this assignment.
    web_eval.HERE = folder
    frozen = {
        "mode": args.mode,
        "model": args.model,
        "started_at": datetime.now(UTC).isoformat(),
        "search_evaluator_sha256": hashlib.sha256((WEB / "run_eval.py").read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(Path(config.cases_file).read_bytes()).hexdigest(),
        "sampling_overrides": {},
        "research_loop": False,
        "credential_access": "read-only saved web.ollama_api_key only; value omitted",
    }
    (folder / "inputs.json").write_text(json.dumps(frozen, indent=2) + "\n")
    await web_eval.evaluate(config)
    if hashlib.sha256(Path(config.cases_file).read_bytes()).hexdigest() != frozen["cases_sha256"]:
        raise RuntimeError("Cases changed during evaluation")


if __name__ == "__main__":
    asyncio.run(main())
