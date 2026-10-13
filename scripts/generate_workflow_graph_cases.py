"""Shared synthetic editor/server validation vectors; no runtime calls."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from app.workflows.graph import GraphDoc, validate  # noqa: E402
from app.workflows.template_graphs import template_graph  # noqa: E402

cases = []


def case(name, change=lambda raw: None, template="brief_images"):
    raw = template_graph(template).model_dump(by_alias=True)
    change(raw)
    graph = GraphDoc.model_validate(raw)
    cases.append({"name": name, "graph": graph.model_dump(by_alias=True),
                  "issues": [i.model_dump() for i in validate(graph)]})


case("valid images")
case("valid optional clean-up", template="meeting_pack")
case("duplicate key", lambda d: d["nodes"][1].update(key="start"))
case("duplicate block id", lambda d: d["nodes"][1].update(id="n_start"))
case("duplicate edge id", lambda d: d["edges"][1].update(id=d["edges"][0]["id"]))
case("duplicate pair", lambda d: d["edges"].append({**d["edges"][0], "id": "duplicate_pair"}))
case("disabled Start", lambda d: d["nodes"][0].update(disabled=True))
case("two Starts", lambda d: d["nodes"].append({**copy.deepcopy(d["nodes"][0]), "id": "n_second", "key": "second"}))
case("no Start", lambda d: d["nodes"].pop(0))
case("dangling connection", lambda d: d["edges"][0].update(source="missing"))
case("incoming Start", lambda d: d["edges"].append({"id": "back", "source": "n_draft", "target": "n_start", "source_port": "out", "target_port": "in"}))
case("cycle", lambda d: d["edges"].append({"id": "loop", "source": "n_images", "target": "n_draft", "source_port": "out", "target_port": "in"}))
case("unsupported port", lambda d: d["edges"][0].update(source_port="rejected"))
case("output has no port", lambda d: d["edges"].append({"id": "save_out", "source": "n_save", "target": "n_draft", "source_port": "out", "target_port": "in"}))
case("disconnected", lambda d: d["edges"].pop(0))
case("duplicate input", lambda d: d["nodes"][0]["config"]["fields"].append(copy.deepcopy(d["nodes"][0]["config"]["fields"][0])))
case("blank required prompt", lambda d: d["nodes"][1]["config"].update(prompt=" "))
case("blank review", lambda d: d["nodes"][2]["config"].update(show=""))
case("empty JSON fields", lambda d: d["nodes"][1]["config"].update(format="json"))
case("reserved JSON field", lambda d: d["nodes"][1]["config"].update(format="json", json_fields=[{"name": "text", "type": "string"}]))
case("JSON in text format", lambda d: d["nodes"][1]["config"].update(json_fields=[{"name": "name", "type": "string"}]))
case("unknown reference", lambda d: d["nodes"][1]["config"].update(prompt="{{missing.text}}"))
case("unknown field", lambda d: d["nodes"][1]["config"].update(prompt="{{start.missing}}"))
case("downstream reference", lambda d: d["nodes"][1]["config"].update(prompt="{{review.value}}"))
case("invalid expression", lambda d: d["nodes"][1]["config"].update(prompt="{{start.brief + 1}}"))
case("unclosed reference", lambda d: d["nodes"][1]["config"].update(prompt="{{start.brief"))
case("escaped literal", lambda d: d["nodes"][1]["config"].update(prompt=r"\{{missing.text}}"))
case("untyped audio", lambda d: (d["nodes"][0]["config"]["fields"][0].update(type="recording"), d["nodes"][1]["config"].update(prompt="{{start.brief}}")))
case("typed result expression", lambda d: d["nodes"][-1]["config"]["include"][0].update(ref="Prefix {{review.value}}"))
case("typed result tagged", lambda d: d["nodes"][-1]["config"]["include"][0].update(ref="{{review.value | tagged:source}}"))
case("disabled reference warning", lambda d: d["nodes"][1].update(disabled=True))
case("tagged disabled reference", lambda d: (d["nodes"][1].update(disabled=True), d["nodes"][2]["config"].update(show="{{draft.text | tagged:draft}}")))
case("review rejected branch", lambda d: d["edges"][2].update(source_port="rejected"))
case("no output", lambda d: (d["nodes"].pop(), d["edges"].pop()))
case("disabled output", lambda d: d["nodes"][-1].update(disabled=True))
case("wrong transcription reference", lambda d: d["nodes"][1]["config"].update(recording="{{start.recording | tagged:input}}"), "meeting_pack")
case("wrong clean-up reference", lambda d: d["nodes"][2]["config"].update(transcript="{{transcript.text}}"), "meeting_pack")
case("too many images", lambda d: d["nodes"].extend([{**copy.deepcopy(d["nodes"][3]), "id": f"n_image_{i}", "key": f"image_{i}", "config": {"prompt": "Synthetic", "count": 3}} for i in range(4)]))
destination = ROOT / "shared/workflow_graph_cases.json"
destination.write_text(json.dumps(cases, indent=2) + "\n")
print(f"Wrote {len(cases)} synthetic validation cases")
