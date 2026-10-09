"""Read retained comparison reports; never run inference or alter grades."""

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
index = json.loads((OUT / "pairs.json").read_text())
rows = []
for entry in index["results"]:
    if entry.get("setup_invalid") or not entry["reports"]:
        continue
    label = entry["label"]
    report = json.loads((ROOT / entry["reports"][0]).read_text())
    review_path = OUT / (label + "-review.json")
    review = json.loads(review_path.read_text()) if review_path.exists() else {}
    row = {
        "label": label,
        "report": entry["reports"][0],
        "elapsed_seconds": entry["elapsed_seconds"],
        "review": str(review_path.relative_to(ROOT)) if review else None,
    }
    if entry["suite"] == "everyday":
        row.update({k: review.get(k) for k in ["score", "overall_gate", "all_explicit_formats_pass", "no_invented_source_facts", "no_obeyed_embedded_instructions"]})
        results = report["results"]
        for key in ["first_delta_ms", "first_visible_text_ms"]:
            values = [r["observed"][key] for r in results if r["observed"].get(key) is not None]
            row[key + "_p50"] = statistics.median(values)
        rates = [r["message"]["stats"]["tokens_per_sec"] for r in results if r["message"].get("stats") and r["message"]["stats"].get("tokens_per_sec")]
        row["native_tokens_per_second_p50"] = statistics.median(rates)
    else:
        row["metrics"] = report["metrics"]
        row["gates"] = report.get("gates", report["metrics"].get("gates"))
        row["semantic_gate"] = review.get("semantic_gate")
    rows.append(row)
summary = {
    "execution_complete": index.get("full_execution_complete", False),
    "valid_suites_completed": len(rows),
    "expected_suites": 18,
    "rows": rows,
    "limitations": "Manual reviews remain distinct from automated gates. First delta may be reasoning. No regrading, model judges or statistical significance claim.",
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: summary[k] for k in ["execution_complete", "valid_suites_completed", "expected_suites"]}))
