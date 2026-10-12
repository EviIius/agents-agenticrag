"""Strict initial block contracts and layout-independent execution ordering."""

import hashlib
import json
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

from ..errors import AppError
from ..schemas import Input, Parameters

Key = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,31}$")]
Identifier = Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")]
Text = Annotated[str, Field(max_length=20000)]


class ModelRef(Input):
    connection_id: str
    model_id: str


ModelChoice = ModelRef | Literal["workflow_default"]


class Point(Input):
    x: float = Field(0, allow_inf_nan=False)
    y: float = Field(0, allow_inf_nan=False)


class StartField(Input):
    name: Key
    label: str = Field(min_length=1, max_length=80)
    type: Literal[
        "short_text", "long_text", "number", "boolean", "choice", "recording", "document", "image"
    ]
    required: bool = False
    default: Any = None
    choices: list[str] = Field(default_factory=list, max_length=40)
    help: str = Field("", max_length=500)


class StartConfig(Input):
    fields: list[StartField] = Field(default_factory=list, max_length=12)


class JsonField(Input):
    name: Key
    type: Literal["string", "number", "boolean"]
    description: str = Field("", max_length=500)


class GenerateConfig(Input):
    model: ModelChoice = "workflow_default"
    instructions: Text = ""
    prompt: Text
    format: Literal["text", "markdown", "json"] = "text"
    json_fields: list[JsonField] = Field(default_factory=list, max_length=20)
    params: Parameters = Field(default_factory=lambda: Parameters.model_validate({}))


class TranscribeConfig(Input):
    recording: Text


class CleanConfig(Input):
    transcript: Text
    model: ModelChoice = "workflow_default"


class ImageConfig(Input):
    prompt: Text
    count: int = Field(1, ge=1, le=3)
    seeds: Literal["auto"] | list[Annotated[int, Field(strict=True, ge=0, le=4294967295)]] = "auto"

    @model_validator(mode="after")
    def seed_count(self) -> "ImageConfig":
        if isinstance(self.seeds, list) and len(self.seeds) != self.count:
            raise ValueError("One seed is required per image")
        return self


class ReviewConfig(Input):
    show: Text
    editable: bool = True
    message: str = Field("Check this result before continuing.", max_length=1000)


class OutputItem(Input):
    label: str = Field(min_length=1, max_length=80)
    ref: Text


class OutputConfig(Input):
    include: list[OutputItem] = Field(default_factory=list, max_length=40)
    formats: list[Literal["md", "json"]] = Field(default=["md", "json"], min_length=1, max_length=2)
    include_sources: bool = True


class NodeBase(Input):
    id: Identifier
    key: Key
    title: str = Field(min_length=1, max_length=80)
    position: Point = Field(default_factory=lambda: Point(x=0, y=0))
    disabled: bool = False


class StartNode(NodeBase):
    kind: Literal["start"]
    config: StartConfig


class GenerateNode(NodeBase):
    kind: Literal["generate"]
    config: GenerateConfig


class TranscribeNode(NodeBase):
    kind: Literal["transcribe"]
    config: TranscribeConfig


class CleanNode(NodeBase):
    kind: Literal["clean_transcript"]
    config: CleanConfig


class ImageNode(NodeBase):
    kind: Literal["generate_image"]
    config: ImageConfig


class ReviewNode(NodeBase):
    kind: Literal["review"]
    config: ReviewConfig


class OutputNode(NodeBase):
    kind: Literal["output"]
    config: OutputConfig


Node = Annotated[
    StartNode | GenerateNode | TranscribeNode | CleanNode | ImageNode | ReviewNode | OutputNode,
    Field(discriminator="kind"),
]


class Edge(Input):
    id: Identifier
    source: Identifier
    source_port: Literal["out", "approved", "rejected"] = "out"
    target: Identifier
    target_port: Literal["in"] = "in"


class Note(Input):
    id: Identifier
    position: Point = Field(default_factory=lambda: Point(x=0, y=0))
    size: dict[Literal["w", "h"], Annotated[float, Field(gt=0, allow_inf_nan=False)]]
    tone: Literal["neutral", "amber", "rose", "teal"] = "neutral"
    text: Text

    @model_validator(mode="after")
    def dimensions(self) -> "Note":
        if set(self.size) != {"w", "h"}:
            raise ValueError("Notes need both width and height")
        return self


class GraphSettings(Input):
    default_model: ModelRef | None = None
    keep_test_runs_days: int = Field(7, ge=1, le=30)


class Viewport(Point):
    zoom: float = Field(1, ge=0.25, le=1.75)


class GraphDoc(Input):
    schema_: Literal["atelier.workflow/1"] = Field("atelier.workflow/1", alias="schema")
    nodes: list[Node] = Field(min_length=1, max_length=40)
    edges: list[Edge] = Field(default_factory=list, max_length=200)
    notes: list[Note] = Field(default_factory=list, max_length=100)
    viewport: Viewport | None = None
    settings: GraphSettings = Field(default_factory=lambda: GraphSettings(keep_test_runs_days=7))


class Issue(Input):
    code: str
    message: str
    node_id: str | None = None
    severity: Literal["error", "warning", "info"] = "error"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def execution_hash(doc: GraphDoc) -> str:
    value = doc.model_dump(by_alias=True, exclude={"notes", "viewport"})
    value["nodes"] = sorted(
        [{k: v for k, v in n.items() if k not in {"position", "title"}} for n in value["nodes"]],
        key=lambda n: n["id"],
    )
    value["edges"] = sorted(value["edges"], key=lambda e: e["id"])
    return digest(value)


def topo_order(doc: GraphDoc) -> list[str]:
    remaining = {n.id for n in doc.nodes}
    result: list[str] = []
    while remaining:
        ready = sorted(
            n
            for n in remaining
            if not any(e.target == n and e.source in remaining for e in doc.edges)
        )
        if not ready:
            raise ValueError("Workflow connections contain a cycle")
        result.extend(ready)
        remaining.difference_update(ready)
    return result


def ancestors(doc: GraphDoc, node_id: str) -> set[str]:
    seen: set[str] = set()
    while True:
        expanded = seen | {e.source for e in doc.edges if e.target == node_id or e.target in seen}
        if expanded == seen:
            return seen
        seen = expanded


def outputs(node: Node) -> dict[str, str]:
    if isinstance(node, StartNode):
        return {f.name: f.type for f in node.config.fields}
    if isinstance(node, GenerateNode):
        return {"text": "text", **{f.name: f.type for f in node.config.json_fields}}
    return {
        "generate": {"text": "text"},
        "transcribe": {
            "transcript": "transcript",
            "text": "text",
            "timestamped_text": "text",
            "segments": "json",
            "filename": "text",
        },
        "clean_transcript": {"text": "text"},
        "generate_image": {"images": "image_list", "prompt": "text"},
        "review": {"value": "text"},
        "output": {},
    }[node.kind]


def validate(doc: GraphDoc) -> list[Issue]:
    from .templating import references

    issues: list[Issue] = []

    def add(code: str, message: str, identifier: str | None = None) -> None:
        issues.append(Issue(code=code, message=message, node_id=identifier))

    ids = [n.id for n in doc.nodes]
    keys = [n.key for n in doc.nodes]
    if len(set(ids)) != len(ids) or len(set(keys)) != len(keys):
        add("duplicate", "Each block needs its own ID and reference name.")
    if len({e.id for e in doc.edges}) != len(doc.edges) or len({n.id for n in doc.notes}) != len(
        doc.notes
    ):
        add("duplicate", "Connection and note IDs must be unique.")
    starts = [n for n in doc.nodes if isinstance(n, StartNode)]
    if len(starts) != 1 or starts[0].disabled:
        add("start", "Keep exactly one enabled Start block.")
    by_id = {n.id: n for n in doc.nodes}
    if len({(e.source, e.source_port, e.target) for e in doc.edges}) != len(doc.edges):
        add("duplicate_connection", "Keep one connection per output-to-input pair.")
    for e in doc.edges:
        if e.source not in by_id or e.target not in by_id:
            add("edge", "A connection points to a missing block.")
            continue
        if isinstance(by_id[e.target], StartNode):
            add("edge", "Start cannot have an incoming connection.", e.target)
        ports = (
            {"approved", "rejected"}
            if isinstance(by_id[e.source], ReviewNode)
            else set()
            if isinstance(by_id[e.source], OutputNode)
            else {"out"}
        )
        if e.source_port not in ports:
            add("port", "Choose an output port offered by this block.", e.source)
    try:
        topo_order(doc)
    except ValueError:
        add("cycle", "Connections cannot lead back to an earlier block.")
    if sum(n.config.count for n in doc.nodes if isinstance(n, ImageNode)) > 12:
        add("images", "Use at most 12 images per run.")
    by_key = {n.key: n for n in doc.nodes}
    for node in doc.nodes:
        if not isinstance(node, StartNode) and not any(e.target == node.id for e in doc.edges):
            add("disconnected", "Connect this block to Start.", node.id)
        if isinstance(node, StartNode):
            names = [f.name for f in node.config.fields]
            if len(set(names)) != len(names):
                add("duplicate_field", "Start input names must be unique.", node.id)
        if isinstance(node, GenerateNode) and node.config.format == "json":
            names = [f.name for f in node.config.json_fields]
            if not names or "text" in names or len(set(names)) != len(names):
                add(
                    "json_fields",
                    "Choose unique JSON fields apart from the reserved text output.",
                    node.id,
                )
        if (
            isinstance(node, GenerateNode)
            and node.config.format != "json"
            and node.config.json_fields
        ):
            add("json_fields", "Choose JSON output before adding JSON fields.", node.id)
        text_fields: list[tuple[str, bool]] = []
        if isinstance(node, GenerateNode):
            text_fields = [(node.config.instructions, False), (node.config.prompt, False)]
        elif isinstance(node, ReviewNode):
            text_fields = [(node.config.show, False)]
        elif isinstance(node, ImageNode):
            text_fields = [(node.config.prompt, False)]
        elif isinstance(node, TranscribeNode):
            text_fields = [(node.config.recording, True)]
        elif isinstance(node, CleanNode):
            text_fields = [(node.config.transcript, True)]
        elif isinstance(node, OutputNode):
            text_fields = [(i.ref, True) for i in node.config.include]
        for text, typed in text_fields:
            try:
                refs = references(text)
            except ValueError:
                add(
                    "reference_syntax",
                    "Use {{block.field}} references or the tagged filter.",
                    node.id,
                )
                continue
            if typed:
                from .templating import exact_reference

                try:
                    exact_reference(text)
                except AppError:
                    add("reference_type", "Choose one typed output reference.", node.id)
            for ref in refs:
                source = by_key.get(ref.key)
                if not source or ref.field not in outputs(source):
                    add("reference", "A referenced output does not exist.", node.id)
                elif source.id not in ancestors(doc, node.id):
                    add("reference_order", "Connect the referenced block upstream first.", node.id)
                elif not typed and outputs(source)[ref.field] in {
                    "recording",
                    "document",
                    "image",
                    "image_list",
                    "transcript",
                }:
                    add(
                        "reference_type",
                        "Use a text field rather than a file or media reference.",
                        node.id,
                    )
                elif typed:
                    expected = (
                        "recording"
                        if isinstance(node, TranscribeNode)
                        else "transcript"
                        if isinstance(node, CleanNode)
                        else None
                    )
                    if expected and outputs(source)[ref.field] != expected:
                        add(
                            "reference_type", "Choose an output of the required file type.", node.id
                        )
        if node.disabled:
            issues.append(
                Issue(
                    code="disabled",
                    message="This block is skipped while disabled.",
                    node_id=node.id,
                    severity="info",
                )
            )
        if isinstance(node, ReviewNode):
            for port in ["approved", "rejected"]:
                if not any(e.source == node.id and e.source_port == port for e in doc.edges):
                    issues.append(
                        Issue(
                            code="branch_ends",
                            message=f"The {port} path ends here.",
                            node_id=node.id,
                            severity="warning",
                        )
                    )
    if not any(isinstance(n, OutputNode) and not n.disabled for n in doc.nodes):
        issues.append(
            Issue(
                code="no_results",
                message="This workflow does not save anything.",
                severity="warning",
            )
        )
    return issues
