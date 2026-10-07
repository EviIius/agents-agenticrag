"""One unscored replay of a retained public final-answer payload, no tool loop.

Serialize after a full eval. This diagnoses a failed selector; it cannot qualify
Research or count as a full/confirmation run. Every request and frame is retained.
"""

import asyncio
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "server"))
from app.runs.research_output import PROMPT, EvidenceOutput, dates, literal  # noqa: E402
from app.schemas import Source  # noqa: E402


async def main(case_file, destination):
    if destination.exists():
        raise SystemExit("Choose a new empty diagnostic destination.")
    case = json.loads(case_file.read_text())
    request = case["captured_requests"][-1]
    assert "tools" not in request and "format" in request
    assert request["options"] == {"num_ctx": 32768}
    assert request["model"] == "qwen3:30b-a3b-workbench-32k"
    question = next(
        c["turns"][0]["user"]
        for c in json.loads((ROOT / "server/evals/research/cases.yaml").read_text())
        if c["id"] == case["id"]
    )
    output = EvidenceOutput(question, [Source.model_validate(s) for s in case["sources"]])
    request["messages"][-1]["content"] = (
        request["messages"][-1]["content"].split("\n\n<evidence_catalog", 1)[0]
        + "\n\n" + output.catalog() + "\n\n" + PROMPT
    )
    request["format"] = output.schema()
    destination.mkdir()
    (destination / "request.json").write_text(json.dumps(request, indent=2) + "\n")
    text, frames = "", []
    started = datetime.now(UTC).isoformat()
    async with httpx.AsyncClient(timeout=300) as client:
        qualification = next(
            q for q in json.loads((ROOT / "server/app/runs/research-qualified.json").read_text())
            if q["context_length"] == request["options"]["num_ctx"]
        )
        version = (await client.get("http://127.0.0.1:11434/api/version")).json()["version"]
        tag = next(
            t for t in (await client.get("http://127.0.0.1:11434/api/tags")).json()["models"]
            if t["name"] == request["model"]
        )
        assert version == qualification["runtime_version"]
        assert tag["digest"] == qualification["digest"]
        async with client.stream("POST", "http://127.0.0.1:11434/api/chat", json=request) as reply:
            reply.raise_for_status()
            with (destination / "response.ndjson").open("w") as stream:
                async for line in reply.aiter_lines():
                    if not line.strip():
                        continue
                    stream.write(line + "\n")
                    stream.flush()
                    frame = json.loads(line)
                    frames.append(frame)
                    text += frame.get("message", {}).get("content", "")
    checks = []
    try:
        result = json.loads(text)
        for row in result.get("rows", []):
            try:
                rendered = output.render(row)
                checks.append({"row": row, "valid": True, "rendered": rendered})
            except Exception as exc:
                selected = [output.units[key] for key in row.get("evidence", []) if key in output.units]
                evidence = "\n".join(u.heading + "\n" + u.text for u in selected)
                checks.append({"row": row, "valid": False, "exception_type": type(exc).__name__,
                               "label_literal": literal(row.get("label", ""), question) or literal(row.get("label", ""), evidence),
                               "value_literal": literal(row.get("value", ""), evidence),
                               "dates_in_selected_evidence": sorted(dates(evidence))})
        parse_error = None
    except Exception as exc:
        parse_error = type(exc).__name__
    report = {"scope": "One unscored current-selector preflight from previously selected public evidence, not a benchmark or confirmation. No tools or additional production calls.",
              "recorded_at": started, "original_case": case["id"], "request_sha256": hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest(),
              "native_calls": 1, "parse_error": parse_error, "rows": checks,
              "runtime_version": version, "model_digest": tag["digest"],
              "raw_answer": text, "completed": bool(frames and frames[-1].get("done")),
              "limitation": "New stochastic output under the same retained request; not a recovery of the lost original final stream."}
    (destination / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"raw_answer", "rows"}}, indent=2))


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()))
