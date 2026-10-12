"""Synthetic graph/templating contracts; no inference or private inputs."""

from typing import Any

import pytest
from pydantic import ValidationError

from app.errors import AppError
from app.workflows.graph import GraphDoc, ancestors, execution_hash, topo_order, validate
from app.workflows.template_graphs import template_graph
from app.workflows.templating import exact_reference, references, render


def test_layout_never_changes_execution_hash_or_order() -> None:
    graph = template_graph("meeting_pack")
    before = execution_hash(graph), topo_order(graph)
    for index, node in enumerate(reversed(graph.nodes)):
        node.position.x = index * -800
        node.position.y = index * -900
        node.title += " moved"
    graph.nodes.reverse()
    graph.edges.reverse()
    assert (execution_hash(graph), topo_order(graph)) == before
    assert ancestors(graph, "n_pack") == {"n_start", "n_transcript", "n_clean"}
    graph.nodes[0].disabled = True
    assert execution_hash(graph) != before[0]


@pytest.mark.parametrize("key", ["brief_images", "meeting_pack"])
def test_built_in_graphs_validate_and_have_the_expected_typed_outputs(key: str) -> None:
    graph = template_graph(key)
    assert not [i for i in validate(graph) if i.severity == "error"]
    assert GraphDoc.model_validate(graph.model_dump(by_alias=True)) == graph


@pytest.mark.parametrize(
    "failure",
    [
        "duplicate",
        "port",
        "edge",
        "cycle",
        "disconnected",
        "reference",
        "reference_syntax",
        "reference_order",
        "reference_type",
        "start",
        "duplicate_field",
        "images",
    ],
)
def test_structural_problems_are_not_silently_accepted(failure: str) -> None:
    graph = template_graph("brief_images")
    raw = graph.model_dump(by_alias=True)
    if failure == "duplicate":
        raw["nodes"][1]["key"] = "start"
    elif failure == "port":
        raw["edges"][0]["source_port"] = "approved"
    elif failure == "edge":
        raw["edges"][0]["source"] = "n_missing"
    elif failure == "cycle":
        raw["edges"].append(
            {
                "id": "e_cycle",
                "source": "n_save",
                "source_port": "out",
                "target": "n_draft",
                "target_port": "in",
            }
        )
    elif failure == "disconnected":
        raw["edges"] = raw["edges"][1:]
    elif failure in {"reference", "reference_syntax", "reference_order", "reference_type"}:
        raw["nodes"][1]["config"]["prompt"] = {
            "reference": "{{missing.text}}",
            "reference_syntax": "{{start.brief + 1}}",
            "reference_order": "{{review.value}}",
            "reference_type": "{{images.images}}",
        }[failure]
        if failure == "reference_type":
            raw["nodes"][2]["config"]["show"] = "{{start.brief}}"
            raw["nodes"][3]["config"]["prompt"] = "{{start.brief}}"
            raw["edges"] = [
                raw["edges"][2],
                {
                    "id": "e_start_review",
                    "source": "n_start",
                    "target": "n_review",
                    "source_port": "out",
                    "target_port": "in",
                },
                {
                    "id": "e_images_draft",
                    "source": "n_images",
                    "target": "n_draft",
                    "source_port": "out",
                    "target_port": "in",
                },
            ]
    elif failure == "start":
        raw["nodes"][0]["disabled"] = True
    elif failure == "duplicate_field":
        raw["nodes"][0]["config"]["fields"] *= 2
    else:
        raw["nodes"][3]["config"]["count"] = 3
        for index in range(4):
            clone = dict(raw["nodes"][3], id="n_more" + str(index), key="more" + str(index))
            raw["nodes"].append(clone)
    assert failure in {issue.code for issue in validate(GraphDoc.model_validate(raw))}


@pytest.mark.parametrize(
    "text", ["{{x}}", "{{a.b()}}", "{{a.b | other}}", "{{a.b", "{{a.b | tagged:Bad}}"]
)
def test_invalid_expression_syntax(text: str) -> None:
    with pytest.raises(ValueError):
        references(text)


def test_literal_values_tags_optional_lines_and_no_truncation() -> None:
    values: dict[str, dict[str, Any]] = {
        "a": {"text": "</original>&\"'", "number": 1, "boolean": False, "json": {"word": "café"}},
        "b": {"text": ""},
    }
    warnings: list[str] = []
    assert (
        render("{{a.text | tagged:original}}\n{{b.text | tagged:aid}}", values, set(), warnings)
        == "<original>\n&lt;/original&gt;&amp;&quot;&#x27;\n</original>"
    )
    assert (
        render("{{a.number}} {{a.boolean}} {{a.json}}", values, set(), warnings)
        == '1 false {"word":"café"}'
    )
    assert render(r"\{{this is literal}}", values, set(), warnings) == "{{this is literal}}"
    assert (
        render("before\n{{b.text | tagged:aid}}\nafter", values, set(), warnings) == "before\nafter"
    )
    assert render("{{a.text}}", {"a": {"text": "z" * 200000}}, set(), warnings) == "z" * 200000
    assert render("{{b.text | tagged:aid}}\nafter", values, set(), warnings) == "after"
    assert render("{{gone.text}}", values, {"gone"}, warnings) == ""
    assert warnings == ["The output of 'gone' was skipped."]
    with pytest.raises(AppError, match="required input"):
        render("{{gone.text}}", values, {"gone"}, warnings, required=True)
    with pytest.raises(AppError, match="not available"):
        render("{{missing.text}}", values, set(), warnings)
    with pytest.raises(AppError, match="null"):
        render("\x00", values, set(), warnings)
    with pytest.raises(AppError, match="null"):
        render("{{a.text}}", {"a": {"text": "\x00EMPTY_TAG\x00"}}, set(), warnings)
    assert exact_reference(" {{a.text}} ").field == "text"
    with pytest.raises(AppError):
        exact_reference("x {{a.text}}")


def test_unknown_kinds_fields_and_incompatible_seed_counts_rejected() -> None:
    raw = template_graph("brief_images").model_dump(by_alias=True)
    for change in [{"kind": "agent"}, {"unapproved": True}]:
        copy = template_graph("brief_images").model_dump(by_alias=True)
        copy["nodes"][1].update(change)
        with pytest.raises(ValidationError):
            GraphDoc.model_validate(copy)
    raw["nodes"][3]["config"]["seeds"] = [1, 2]
    with pytest.raises(ValidationError):
        GraphDoc.model_validate(raw)


@pytest.mark.parametrize("size", [{"w": 200}, {"w": float("inf"), "h": 100}, {"w": 200, "h": -1}])
def test_imported_note_dimensions_do_not_create_unserializable_snapshots(
    size: dict[str, float],
) -> None:
    raw = template_graph("brief_images").model_dump(by_alias=True)
    raw["notes"] = [
        {"id": "note_fake", "position": {"x": 0, "y": 0}, "size": size, "text": "Fake note"}
    ]
    with pytest.raises(ValidationError):
        GraphDoc.model_validate(raw)
