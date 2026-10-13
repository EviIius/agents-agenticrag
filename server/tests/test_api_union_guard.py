"""Only provably disjoint additive discriminator choices pass the contract guard."""

from copy import deepcopy
from typing import Any

from tests.test_phase4_guards import compare


def document(tags: list[str]) -> dict[str, Any]:
    return {
        "union": {
            "oneOf": [{"$ref": "#/schemas/" + tag} for tag in tags],
            "discriminator": {
                "propertyName": "kind",
                "mapping": {tag: "#/schemas/" + tag for tag in tags},
            },
        },
        "schemas": {
            tag: {"required": ["kind"], "properties": {"kind": {"const": tag}}} for tag in tags
        },
    }


def test_api_allows_new_disjoint_variant_and_preserves_all_original_contracts() -> None:
    before = document(["one", "two"])
    after = document(["one", "two", "three"])
    assert not compare(before, after)
    assert compare(before, document(["one", "three"]))
    broken = deepcopy(after)
    broken["schemas"]["one"]["properties"]["kind"]["const"] = "changed"
    assert compare(before, broken)
    ambiguous = deepcopy(after)
    ambiguous["schemas"]["three"]["properties"]["kind"] = {"type": "string"}
    assert compare(before, ambiguous)
    duplicate = deepcopy(after)
    duplicate["union"]["oneOf"].append({"$ref": "#/schemas/one"})
    assert compare(before, duplicate)
    missing_required = deepcopy(after)
    missing_required["schemas"]["three"]["required"] = []
    assert compare(before, missing_required)
    no_discriminator = deepcopy(after)
    del no_discriminator["union"]["discriminator"]
    assert compare(before, no_discriminator)
    assert compare(
        {"oneOf": [{"type": "string"}]}, {"oneOf": [{"type": "string"}, {"type": "number"}]}
    )
    assert compare({"type": "string"}, {"type": "number"})
