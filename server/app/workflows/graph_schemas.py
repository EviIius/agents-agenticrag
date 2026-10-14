"""Additive Workflow Studio API types; legacy types are unchanged."""

from typing import Any, Literal

from pydantic import Field

from ..schemas import ErrorDetail, Input
from .graph import GraphDoc, Issue, ModelRef

DefIcon = Literal[
    "workflow",
    "image",
    "audio",
    "library",
    "file",
    "sparkles",
    "globe",
    "mail",
    "calendar",
    "star",
    "briefcase",
    "folder",
]


class DefCreate(Input):
    name: str = Field("Untitled workflow", min_length=1, max_length=80)
    template_id: Literal["brief_images", "meeting_pack"] | None = None
    graph: GraphDoc | None = None
    default_model: ModelRef | None = None


class DefSave(Input):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field("", max_length=1000)
    icon: DefIcon = "workflow"
    graph: GraphDoc
    version: int = Field(ge=1)
    force: bool = False


class Definition(Input):
    id: str
    name: str
    description: str
    icon: DefIcon
    graph: GraphDoc
    graph_hash: str
    version: int
    template_id: str | None
    archived_at: str | None
    created_at: str
    updated_at: str


class Snapshot(Input):
    id: str
    def_id: str
    graph_hash: str
    graph: GraphDoc
    label: str | None
    created_at: str
    run_count: int = 0


class DefConflict(Input):
    error: ErrorDetail
    current: Definition


class SnapshotLabel(Input):
    label: str | None = Field(None, max_length=80)


class ValidationBody(Input):
    graph: GraphDoc | None = None


class ValidationResult(Input):
    issues: list[Issue]
    graph: GraphDoc | None = None


class GraphSubmit(Input):
    request_key: str = Field(min_length=1, max_length=160)
    inputs: dict[str, Any] = Field(default_factory=dict)
    mode: Literal["run", "test"] = "run"
    node_id: str | None = None
    source_run_id: str | None = None
    samples: dict[str, Any] = Field(default_factory=dict)


class ReusePlan(Input):
    eligible: bool
    reason: str | None = None
    source_run_id: str | None = None
    node_ids: list[str] = Field(default_factory=list)


class Decision(Input):
    node_id: str
    decision: Literal["approve", "reject"]
    value: str | None = Field(default=None, max_length=20000)
    chosen: list[int] | None = Field(default=None, max_length=20)


class GraphResume(Input):
    skip_node_id: str | None = None
    prompt: str | None = Field(None, max_length=4000)


class NodeState(Input):
    state: Literal[
        "pending", "running", "paused", "complete", "failed", "cancelled", "interrupted", "skipped"
    ]
    attempt: int
    port: str | None
    output: dict[str, Any] | None
    error: str | None
    started_at: str | None
    finished_at: str | None
    reused_from: str | None = None
    warnings: list[str] = Field(default_factory=list)
    progress: dict[str, Any] | None = None


class ResultItem(Input):
    label: str
    type: str
    value: Any


class ResultSection(Input):
    node_id: str
    label: str
    items: list[ResultItem]


class RunV2(Input):
    id: str
    kind: Literal["template", "graph"]
    def_id: str | None
    def_name: str
    graph_hash: str | None
    snapshot_id: str | None = None
    mode: Literal["run", "test"] = "run"
    parent_run_id: str | None = None
    state: Literal[
        "queued",
        "running",
        "paused",
        "cancelling",
        "cancelled",
        "complete",
        "failed",
        "interrupted",
    ]
    stage: str
    error: str | None
    created_at: str
    updated_at: str
    inputs: dict[str, Any]
    graph: GraphDoc
    nodes: dict[str, NodeState]
    results: list[ResultSection] = Field(default_factory=list)
    source_available: bool


class RunPage(Input):
    paused_count: int = 0
    items: list[RunV2]
    next_cursor: str | None = None


class Template(Input):
    id: str
    name: str
    description: str
    icon: Literal["workflow", "image", "audio"]
    graph: GraphDoc


class BlockEntry(Input):
    kind: str
    label: str
    category: str
    available: bool
    reason: str | None = None


class BlockCatalog(Input):
    blocks: list[BlockEntry]
