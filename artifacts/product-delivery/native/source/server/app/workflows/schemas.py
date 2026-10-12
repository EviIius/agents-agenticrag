from typing import Any, Literal

from pydantic import Field, model_validator

from ..schemas import Input, Parameters


class WorkflowModel(Input):
    connection_id: str
    model_id: str
    params: Parameters = Field(default_factory=lambda: Parameters.model_validate({}))


class WorkflowCreate(Input):
    request_key: str = Field(min_length=1, max_length=160)
    template: Literal["brief_images", "meeting_pack"]
    model: WorkflowModel
    brief: str = Field(default="", max_length=20000)
    attachment_id: str | None = None
    cleanup_model: WorkflowModel | None = None
    review_prompt: bool = True
    seeds: list[int] = Field(default_factory=lambda: [42], min_length=1, max_length=3)

    @model_validator(mode="after")
    def valid_inputs(self) -> "WorkflowCreate":
        if any(seed < 0 or seed > 2**32 - 1 for seed in self.seeds):
            raise ValueError("Seeds must be between 0 and 4,294,967,295.")
        if self.cleanup_model and self.cleanup_model.params.model_dump(exclude_none=True):
            raise ValueError("Guarded clean-up uses the existing transcription settings.")
        if self.template == "brief_images":
            if not self.brief.strip() or self.attachment_id or self.cleanup_model:
                raise ValueError("Image workflows need a brief and no recording.")
        elif not self.attachment_id or self.brief:
            raise ValueError("Meeting workflows need a recording, not a brief.")
        return self


class WorkflowResume(Input):
    prompt: str | None = Field(default=None, min_length=1, max_length=4000)
    skip_cleanup: bool = False


class WorkflowStep(Input):
    position: int
    kind: str
    label: str
    state: str
    attempt: int
    output: dict[str, Any] | None = None
    error: str | None = None


class WorkflowRun(Input):
    id: str
    version: int
    input: WorkflowCreate
    state: str
    stage: str
    steps: list[WorkflowStep]
    source_available: bool
    edited_prompt: str | None = None
    error: str | None = None
    created_at: str
    updated_at: str


class WorkflowSnapshot(Input):
    runs: list[WorkflowRun]


class WorkflowChange(Input):
    run: WorkflowRun


class WorkflowSource(Input):
    text: str
    raw_text: str
    segments: list[dict[str, Any]]
    cleaned_text: str | None = None
    attachment_id: str
    filename: str


class WorkflowRecording(Input):
    id: str
    filename: str
    status: str
