"""Freeze the accepted application-authored workflow prompts from b9ef4a4c."""

import hashlib

from app.workflows import templates
from app.workflows.graph import GenerateNode
from app.workflows.template_graphs import template_graph


def test_workflow_template_prompts_and_graph_copies_keep_the_accepted_hashes() -> None:
    expected = {
        "IMAGE_PROMPT": "4ea62603aa4116829f656f5ccbed309750afa1e4833296781d1bb86c0557e8d4",
        "MEETING_PACK": "2ac20d3003835f98a2471083e1fcf39b273296e34ea3a3a76d3549deebc9929b",
    }
    assert {
        name: hashlib.sha256(getattr(templates, name).encode()).hexdigest() for name in expected
    } == expected, "Application-authored prompt edits require linked before/after evaluations."
    for identifier, name in [("brief_images", "IMAGE_PROMPT"), ("meeting_pack", "MEETING_PACK")]:
        generated = [n for n in template_graph(identifier).nodes if isinstance(n, GenerateNode)]
        assert len(generated) == 1
        assert (
            hashlib.sha256(generated[0].config.instructions.encode()).hexdigest() == expected[name]
        )
