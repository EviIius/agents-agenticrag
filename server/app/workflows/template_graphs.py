"""Editable graph equivalents, using the exact frozen template prompts."""

from typing import Any, cast

from . import templates
from .graph import GraphDoc
from .graph_schemas import Template


def template_graph(
    identifier: str, *, cleanup: bool = False, review: bool = True, seeds: list[int] | None = None
) -> GraphDoc:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    def node(
        key: str, kind: str, title: str, config: dict[str, Any], disabled: bool = False
    ) -> None:
        nodes.append(
            {
                "id": "n_" + key,
                "key": key,
                "kind": kind,
                "title": title,
                "config": config,
                "disabled": disabled,
                "position": {"x": 320, "y": len(nodes) * 160},
            }
        )

    def edge(source: str, target: str, port: str = "out") -> None:
        edges.append(
            {
                "id": f"e_{source}_{target}",
                "source": "n_" + source,
                "target": "n_" + target,
                "source_port": port,
            }
        )

    if identifier == "brief_images":
        node(
            "start",
            "start",
            "Start",
            {
                "fields": [
                    {"name": "brief", "label": "Image brief", "type": "long_text", "required": True}
                ]
            },
        )
        node(
            "draft",
            "generate",
            "Draft image prompt",
            {"instructions": templates.IMAGE_PROMPT, "prompt": "{{start.brief}}"},
        )
        if review:
            node(
                "review",
                "review",
                "Check the prompt",
                {
                    "show": "{{draft.text}}",
                    "editable": True,
                    "message": "Check the prompt before images are made.",
                },
            )
            edge("draft", "review")
        ref = "{{review.value}}" if review else "{{draft.text}}"
        node(
            "images",
            "generate_image",
            "Create images",
            {
                "prompt": ref,
                "count": len(seeds) if seeds else 1,
                "seeds": seeds if seeds else "auto",
            },
        )
        node(
            "save",
            "output",
            "Save results",
            {
                "include": [
                    {"label": "Prompt", "ref": ref},
                    {"label": "Images", "ref": "{{images.images}}"},
                ]
            },
        )
        edge("start", "draft")
        edge("review" if review else "draft", "images", "approved" if review else "out")
        edge("images", "save")
    elif identifier == "meeting_pack":
        node(
            "start",
            "start",
            "Start",
            {
                "fields": [
                    {
                        "name": "recording",
                        "label": "Recording",
                        "type": "recording",
                        "required": True,
                    }
                ]
            },
        )
        node(
            "transcript", "transcribe", "Transcribe recording", {"recording": "{{start.recording}}"}
        )
        node(
            "clean",
            "clean_transcript",
            "Clean up transcript",
            {"transcript": "{{transcript.transcript}}"},
            not cleanup,
        )
        node(
            "pack",
            "generate",
            "Draft meeting pack",
            {
                "instructions": templates.MEETING_PACK,
                "prompt": (
                    "{{transcript.timestamped_text | tagged:original_transcript}}\n{{cl"
                    "ean.text | tagged:cleaned_reading_aid}}"
                ),
                "format": "markdown",
            },
        )
        node(
            "save",
            "output",
            "Save results",
            {
                "include": [{"label": "Meeting pack", "ref": "{{pack.text}}"}],
                "include_sources": True,
            },
        )
        for source, target in [
            ("start", "transcript"),
            ("transcript", "clean"),
            ("clean", "pack"),
            ("transcript", "pack"),
            ("pack", "save"),
        ]:
            edge(source, target)
    else:
        raise ValueError("Unknown workflow template")
    return GraphDoc.model_validate({"schema": "atelier.workflow/1", "nodes": nodes, "edges": edges})


def template_list() -> list[Template]:
    return [
        Template(
            id=key,
            name=name,
            description=description,
            icon=cast(Any, icon),
            graph=template_graph(key),
        )
        for key, name, description, icon in [
            (
                "brief_images",
                "Brief to images",
                "Draft and review an image prompt, then create images.",
                "image",
            ),
            (
                "meeting_pack",
                "Recording to meeting pack",
                "Keep the original transcript and draft a meeting pack for review.",
                "audio",
            ),
        ]
    ]
