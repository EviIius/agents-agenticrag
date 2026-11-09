"""Compiled invented-structure checks; never initializes Accessibility or an app."""

import copy
import json
import subprocess
import sys


def tree(count: int) -> list[dict[str, object]]:
    nodes: list[dict[str, object]] = [
        {"path": [], "role": "AXWindow", "children": 1},
        {"path": [0], "role": "AXGroup", "children": count},
    ]
    for i in range(count):
        nodes.extend([
            {"path": [0, i], "role": "AXGroup", "children": 1},
            {"path": [0, i, 0], "role": "AXGroup", "children": 1},
            {"path": [0, i, 0, 0], "role": "AXTextArea", "children": 0},
        ])
    return nodes


spec = {"nodes": tree(8), "boundary": [0], "paths": [[0, i, 0, 0] for i in range(8)]}
cases: list[tuple[str, list[dict[str, object]], bool]] = [
    ("one-area", tree(1), True), ("two-areas", tree(2), True),
    ("eight-areas", tree(8), True), ("nine-areas-refused", tree(9), False),
    ("empty-pane-refused", tree(0), False),
]
for name, index, field, value in [
    ("modal-root", 0, "role", "AXSheet"),
    ("changed-ancestry", 1, "role", "AXScrollArea"),
    ("text-field-in-pane", 4, "role", "AXTextField"),
    ("non-leaf-area", 4, "children", 1),
    ("unexpected-parent", 3, "role", "AXRow"),
    ("extra-parent-child", 3, "children", 2),
    ("oversized-child-index", 4, "path", [0, 32, 0, 0]),
    ("wrong-depth", 4, "path", [0, 0, 0]),
]:
    changed = copy.deepcopy(tree(2))
    changed[index][field] = value
    cases.append((name, changed, False))
duplicated = tree(1)
duplicated.append(duplicated[-1].copy())
cases.append(("duplicate-area-path", duplicated, False))
results = []
for name, shape, accepted in cases:
    process = subprocess.run(
        [sys.argv[1], "--boundary-fixture"],
        input=json.dumps({"expected": spec, "current": shape}).encode(),
        capture_output=True, timeout=2,
    )
    assert (process.returncode == 0) == accepted, name
    if accepted:
        assert json.loads(process.stdout)["native_executed"] is False
    results.append({"case": name, "passed": True, "expected_acceptance": accepted})
print(json.dumps({"checks": results, "passed": len(results), "native_calls": 0}, indent=2))
