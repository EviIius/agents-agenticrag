from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel

from .config import VERSION


class Health(BaseModel):
    ok: bool = True
    version: str = VERSION


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Parameters(Input):
    temperature: float | None = Field(None, ge=0, le=2)
    top_p: float | None = Field(None, ge=0, le=1)
    top_k: int | None = Field(None, ge=1, le=200)
    max_tokens: int | None = Field(None, ge=1, le=32768)
    seed: int | None = None
    reasoning: str | None = None


class ConnectionCreate(Input):
    kind: Literal["ollama"] = "ollama"
    name: str = "Ollama on this Mac"
    base_url: str = "http://127.0.0.1:11434"
    api_key: str | None = None
    force: bool = False


class ConnectionPatch(Input):
    name: str | None = None
    base_url: str | None = None
    enabled: bool | None = None
    max_concurrent: int | None = Field(None, ge=1, le=8)
    keep_alive: str | None = None


class Connection(BaseModel):
    id: str
    kind: Literal["ollama"] = "ollama"
    name: str
    base_url: str
    enabled: bool = True
    has_api_key: bool = False
    max_concurrent: int = 1
    keep_alive: str = "30m"
    reachable: bool | None = None
    model_count: int | None = None
    latency_ms: float | None = None


class Detection(BaseModel):
    kind: Literal["ollama"] = "ollama"
    base_url: str
    reachable: bool
    model_count: int = 0
    error: str | None = None


class ReasoningCaps(BaseModel):
    options: list[str]
    default: str | None = None


class ModelInfo(BaseModel):
    connection_id: str
    model_id: str
    display_name: str
    family: str | None = None
    params: str | None = None
    quant: str | None = None
    size_bytes: int | None = None
    context_max: int | None = None
    context_limit: int | None = None
    context_length: int | None = None
    vision: bool | None = None
    tools: bool | None = None
    reasoning: ReasoningCaps | None = None
    loaded: bool | None = None
    loaded_bytes: int | None = None
    chat_capable: bool = True
    hidden: bool = False
    embedding: bool = False
    params_defaults: dict[str, Any] = Field(default_factory=dict)


class ModelAction(Input):
    connection_id: str
    model_id: str
    context_length: int | None = Field(None, ge=1024)


class ModelPrefs(ModelAction):
    display_name: str | None = None
    params: Parameters | None = None
    vision_override: bool | None = None
    hidden: bool | None = None


class PresetCreate(Input):
    name: str = Field(min_length=1, max_length=80)
    system_prompt: str | None = None
    params: Parameters = Field(default_factory=lambda: Parameters.model_validate({}))


class PresetPatch(Input):
    name: str | None = Field(None, min_length=1, max_length=80)
    system_prompt: str | None = None
    params: Parameters | None = None
    position: int | None = Field(None, ge=0)


class Preset(BaseModel):
    id: str
    name: str
    system_prompt: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    position: int
    created_at: str
    updated_at: str


class FolderCreate(Input):
    name: str = Field(min_length=1, max_length=80)


class FolderPatch(Input):
    name: str | None = Field(None, min_length=1, max_length=80)
    position: int | None = Field(None, ge=0)


class Folder(BaseModel):
    id: str
    name: str
    position: int
    count: int = 0
    created_at: str
    updated_at: str


class BackupStatus(BaseModel):
    last_at: str | None = None
    count: int = 0
    bytes: int = 0
    warning: str | None = None


class LibraryScope(Input):
    collection_ids: list[str] = Field(default_factory=list, max_length=100)


class ChatCreate(Input):
    preset_id: str | None = None
    connection_id: str | None = None
    model_id: str | None = None
    web_enabled: bool | None = None


class ChatPatch(Input):
    library_enabled: bool | None = None
    library_scope: LibraryScope | None = None
    folder_id: str | None = None
    title: str | None = Field(None, min_length=1, max_length=200)
    pinned: bool | None = None
    current_leaf_id: str | None = None
    connection_id: str | None = None
    model_id: str | None = None
    system_prompt: str | None = None
    params: Parameters | None = None
    web_enabled: bool | None = None


class Chat(BaseModel):
    library_enabled: bool = False
    library_scope: LibraryScope | None = None
    folder_id: str | None = None
    folder_name: str | None = None
    id: str
    title: str
    title_source: str = "fallback"
    connection_id: str | None = None
    model_id: str | None = None
    system_prompt: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    web_enabled: bool = False
    current_leaf_id: str | None = None
    pinned: bool = False
    created_at: str
    updated_at: str
    snippet: str | None = None


class ChatList(BaseModel):
    items: list[Chat]
    next_cursor: str | None = None


class DocumentInfo(BaseModel):
    source: Literal["pdf", "docx"]
    pages: int | None
    chars: int
    token_estimate: int


class DocumentText(BaseModel):
    text: str


class AttachmentExtensions(BaseModel):
    text: list[str] = Field(default_factory=list)
    document: list[str] = Field(default_factory=list)


class Attachment(BaseModel):
    id: str
    kind: Literal["image", "text", "audio"]
    filename: str
    mime_type: str
    bytes: int
    transcript: "TranscriptInfo | None" = None
    audio_available: bool = True
    document: DocumentInfo | None = None


class MessageModel(BaseModel):
    connection_id: str
    model_id: str
    display_name: str


class CleanupInfo(BaseModel):
    status: Literal["running", "ready", "failed"]
    model: MessageModel | None = None
    chunks: int = 0
    done: int = 0
    kept_original: int = 0
    changed_words: int = 0
    elapsed_seconds: float | None = None
    error: ErrorDetail | None = None


class TranscriptInfo(BaseModel):
    status: Literal["queued", "transcribing", "ready", "failed", "cancelled"]
    channels: Literal["mix", "split"] = "mix"
    started_at: str | None = None
    error: ErrorDetail | None = None
    duration_seconds: float | None = None
    word_count: int | None = None
    token_estimate: int | None = None
    elapsed_seconds: float | None = None
    speed_x_realtime: float | None = None
    engine_model: str | None = None
    warnings: list[str] = Field(default_factory=list)
    correction_count: int = 0
    cleanup: CleanupInfo | None = None


class TranscriptSegment(BaseModel):
    start: float
    end: float
    speaker: str | None = None
    text: str
    raw_text: str


class Correction(BaseModel):
    found: str
    replaced_with: str
    count: int


class Transcript(BaseModel):
    attachment: Attachment
    text: str
    raw_text: str
    cleaned_text: str | None = None
    segments: list[TranscriptSegment]
    corrections: list[Correction]


class AudioStorage(BaseModel):
    files: int = 0
    bytes: int = 0
    active_files: int = 0


class TranscribeRequest(Input):
    channels: Literal["mix", "split"] = "mix"


class CleanupRequest(Input):
    connection_id: str
    model_id: str


class GlossaryRequest(Input):
    text: str


class Glossary(BaseModel):
    text: str
    terms: list[str]


class EngineCheck(BaseModel):
    name: str
    ok: bool
    detail: str
    blocking: bool


class TranscriptionStatus(BaseModel):
    configured: bool
    ready: bool
    version: str | None = None
    checks: list[EngineCheck] = Field(default_factory=list)
    glossary_terms: int = 0
    audio_extensions: list[str] = Field(default_factory=list)


class TranscriptionStartedData(BaseModel):
    started_at: str


class TranscriptionAttachmentData(BaseModel):
    attachment: Attachment


class CleanupProgressData(BaseModel):
    done: int
    total: int


class TranscriptionQueuedEvent(BaseModel):
    type: Literal["transcription.queued"]
    data: "QueuedData"


class TranscriptionStartedEvent(BaseModel):
    type: Literal["transcription.started"]
    data: TranscriptionStartedData


class TranscriptionAttachmentEvent(BaseModel):
    type: Literal[
        "transcription.done",
        "transcription.failed",
        "transcription.cancelled",
        "cleanup.started",
        "cleanup.done",
        "cleanup.failed",
    ]
    data: TranscriptionAttachmentData


class CleanupProgressEvent(BaseModel):
    type: Literal["cleanup.progress"]
    data: CleanupProgressData


class TranscriptionClosedEvent(BaseModel):
    type: Literal["stream.closed"]
    data: dict[str, Any]


class TranscriptionEvent(
    RootModel[
        Annotated[
            TranscriptionQueuedEvent
            | TranscriptionStartedEvent
            | TranscriptionAttachmentEvent
            | CleanupProgressEvent
            | TranscriptionClosedEvent,
            Field(discriminator="type"),
        ]
    ]
):
    @property
    def type(self) -> str:
        return self.root.type

    @property
    def data(self) -> dict[str, Any]:
        return dict(self.root.model_dump()["data"])


class Stats(BaseModel):
    reasoning_ms: float | None = None
    ttft_ms: float | None = None
    total_ms: float = 0
    prompt_tokens: int | None = None
    completion_tokens: int = 0
    tokens_per_sec: float = 0
    tokens_estimated: bool = True
    load_ms: float | None = None
    finish_reason: Literal["stop", "length", "stopped", "error"] = "stop"
    context_length: int = 8192
    dropped_message_count: int = 0
    params: dict[str, Any] = Field(default_factory=dict)


class Passage(BaseModel):
    page_start: int | None = None
    page_end: int | None = None
    source_url: str
    heading: str = ""
    ord: int
    text: str
    selection_applied: bool = False


class Source(BaseModel):
    n: int
    url: str
    title: str
    site_name: str
    domain: str
    published_at: str | None = None
    fetched_at: str
    kind: Literal["page", "snippet", "document"] = "page"
    document_id: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    passages: list[Passage]
    cited: bool = False


class SelectionCondition(Input):
    property_word: str = Field(min_length=1, max_length=40, pattern=r"^[a-zA-Z]+$")
    operator: Literal["gt", "gte", "lt", "lte", "eq", "ne", "occurred", "not_occurred"]
    value: float | None = Field(default=None, allow_inf_nan=False)


class WebInfo(BaseModel):
    status: Literal["used", "skipped", "failed"]
    freshness: Literal["any", "day", "week", "month", "year"] | None = None
    notice: ErrorDetail | None = None
    queries: list[str] = Field(default_factory=list)
    timings: dict[str, float] = Field(default_factory=dict)
    source_count: int = 0
    plan_fallback: bool = False
    providers: list[str] = Field(default_factory=list)
    ranking: str = "keyword"
    selection_condition: SelectionCondition | None = None


class WebRead(BaseModel):
    url: str
    title: str | None = None
    site_name: str | None = None
    status: Literal["used", "unused", "failed"]
    reason: str | None = None


class LibraryInfo(BaseModel):
    status: Literal["used", "skipped", "failed"]
    notice: ErrorDetail | None = None
    queries: list[str] = Field(default_factory=list)
    timings: dict[str, float] = Field(default_factory=dict)
    source_count: int = 0
    passage_count: int = 0


class Message(BaseModel):
    id: str
    chat_id: str
    parent_id: str | None = None
    role: Literal["user", "assistant"]
    content: str
    reasoning: str | None = None
    status: Literal["complete", "streaming", "stopped", "error", "interrupted"]
    error: ErrorDetail | None = None
    model: MessageModel | None = None
    attachments: list[Attachment] = Field(default_factory=list)
    stats: Stats | None = None
    web: WebInfo | None = None
    library: LibraryInfo | None = None
    created_at: str


class ChatDetail(BaseModel):
    chat: Chat
    messages: list[Message]
    sources: dict[str, list[Source]] = Field(default_factory=dict)
    reads: dict[str, list[WebRead]] = Field(default_factory=dict)


class Send(Input):
    content: str = Field(min_length=1, max_length=500000)
    parent_id: str | None = None
    attachment_ids: list[str] = Field(default_factory=list, max_length=8)
    web: bool | None = None
    library: bool | None = None


class Regenerate(Input):
    connection_id: str | None = None
    model_id: str | None = None
    force_web: bool = False


class RunResponse(BaseModel):
    run_id: str
    assistant_message: Message
    user_message: Message | None = None


class ActiveRun(BaseModel):
    run_id: str
    chat_id: str
    assistant_message_id: str


class ContextInfo(BaseModel):
    used_tokens: int
    context_length: int
    dropped_message_count: int


class Bootstrap(BaseModel):
    attachment_extensions: AttachmentExtensions = Field(default_factory=AttachmentExtensions)
    app_name: str
    version: str
    data_dir: str
    settings: dict[str, Any]
    connections: list[Connection]
    features: dict[str, bool]


class DeleteChats(Input):
    confirmation: Literal["DELETE"]


class QueuedData(BaseModel):
    position: int


class StartedData(BaseModel):
    assistant_message_id: str
    connection_id: str
    model_id: str
    model_loaded: bool | None


class DeltaData(BaseModel):
    text: str


class DoneData(BaseModel):
    message: Message


class MessageErrorData(ErrorDetail):
    message_snapshot: Message


class TitleData(BaseModel):
    chat_id: str
    title: str


class QueuedEvent(BaseModel):
    type: Literal["run.queued"]
    data: QueuedData


class StartedEvent(BaseModel):
    type: Literal["run.started"]
    data: StartedData


class DeltaEvent(BaseModel):
    type: Literal["reasoning.delta", "text.delta"]
    data: DeltaData


class DoneEvent(BaseModel):
    type: Literal["message.done"]
    data: DoneData


class ErrorEvent(BaseModel):
    type: Literal["message.error"]
    data: MessageErrorData


class TitleEvent(BaseModel):
    type: Literal["chat.title"]
    data: TitleData


class ClosedEvent(BaseModel):
    type: Literal["run.closed"]
    data: dict[str, Any]


class ToolEvent(BaseModel):
    type: Literal["tool.started", "tool.finished"]
    data: dict[str, Any]  # Reserved, never emitted.


class SearchEvent(BaseModel):
    type: Literal[
        "search.planning",
        "search.queries",
        "search.skipped",
        "search.results",
        "search.reading",
        "search.read",
        "search.done",
        "search.failed",
        "library.searching",
        "library.results",
        "library.done",
        "library.failed",
    ]
    data: dict[str, Any]


class RunEvent(
    RootModel[
        Annotated[
            QueuedEvent
            | StartedEvent
            | DeltaEvent
            | DoneEvent
            | ErrorEvent
            | TitleEvent
            | ClosedEvent
            | ToolEvent
            | SearchEvent,
            Field(discriminator="type"),
        ]
    ]
):
    @property
    def type(self) -> str:
        return self.root.type

    @property
    def data(self) -> dict[str, Any]:
        return dict(self.root.model_dump()["data"])


class SearchTest(Input):
    provider: Literal["ollama", "searxng", "exa", "ddgs", "brave"]


class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str = ""
    provider: str = ""
    published_at: str | None = None


class SearchStatus(BaseModel):
    provider: str
    configured: bool
    reachable: bool
    error: str | None = None


class SearchTestResult(BaseModel):
    ok: bool
    results: list[SearchResult]
    ms: float
    error: str | None = None


class LegacyStatus(BaseModel):
    available: bool


class LegacyImport(BaseModel):
    imported: int
    skipped: int


class LibraryEmbedding(Input):
    connection_id: str
    model_id: str


class LibrarySelection(Input):
    embedding: LibraryEmbedding | None = None


class LibraryCollection(Input):
    name: str = Field(min_length=1, max_length=120)


class LibraryMove(Input):
    collection_id: str | None = None


class LibraryDelete(Input):
    confirmation: str


class LibraryDocument(BaseModel):
    id: str
    collection_id: str | None = None
    filename: str
    mime_type: str
    bytes: int
    status: Literal["queued", "extracting", "embedding", "ready", "failed", "stale"]
    error: dict[str, str] | None = None
    pages: int | None = None
    chunk_count: int = 0
    token_estimate: int | None = None
    embedding_model: str | None = None
    progress_done: int = 0
    progress_total: int = 0
    created_at: str
    updated_at: str


class LibraryCollectionInfo(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str


class LibraryIndex(BaseModel):
    available: bool
    embedding: dict[str, Any] | None = None
    requires_local: bool
    query_prefix: str
    document_prefix: str
    counts: dict[str, int]
    bytes: int
    documents: list[LibraryDocument]
    collections: list[LibraryCollectionInfo]
    event_id: int


class LibraryText(BaseModel):
    text: str
