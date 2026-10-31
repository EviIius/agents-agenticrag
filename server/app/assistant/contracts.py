"""Host-owned observations and small immutable desktop action contracts."""

import hashlib
import json
from typing import Literal

from pydantic import Field, model_validator

from ..schemas import Input


class Contract(Input):
    model_config = {"extra": "forbid", "frozen": True, "strict": True}


class DesktopRect(Contract):
    x: float = Field(allow_inf_nan=False)
    y: float = Field(allow_inf_nan=False)
    width: float = Field(gt=0, allow_inf_nan=False)
    height: float = Field(gt=0, allow_inf_nan=False)


class DesktopFrame(Contract):
    bounds: DesktopRect  # absolute screen points, including negative display origins
    scale: float = Field(gt=0, le=4, allow_inf_nan=False)
    capture_width: int = Field(gt=0, le=16384)
    capture_height: int = Field(gt=0, le=16384)
    crop: DesktopRect  # pixels within the original window capture
    image_width: int = Field(gt=0, le=4096)
    image_height: int = Field(gt=0, le=4096)

    @model_validator(mode="after")
    def fits(self) -> "DesktopFrame":
        if (
            self.crop.x < 0
            or self.crop.y < 0
            or self.crop.x + self.crop.width > self.capture_width
            or self.crop.y + self.crop.height > self.capture_height
            or abs(self.capture_width - self.bounds.width * self.scale) > 1
            or abs(self.capture_height - self.bounds.height * self.scale) > 1
        ):
            raise ValueError("Capture, crop and display scale disagree.")
        return self


class DesktopPoint(Contract):
    x: float = Field(ge=0, allow_inf_nan=False)
    y: float = Field(ge=0, allow_inf_nan=False)
    space: Literal["image_pixels", "normalized_1000"]


def screen_point(frame: DesktopFrame, point: DesktopPoint) -> tuple[float, float]:
    width, height = (
        (1000, 1000)
        if point.space == "normalized_1000"
        else (frame.image_width, frame.image_height)
    )
    if point.x >= width or point.y >= height:
        raise ValueError("Point is outside the observation.")
    return (
        frame.bounds.x + (frame.crop.x + point.x / width * frame.crop.width) / frame.scale,
        frame.bounds.y + (frame.crop.y + point.y / height * frame.crop.height) / frame.scale,
    )


class DesktopElement(Contract):
    id: str = Field(min_length=1, max_length=80)
    label: str = Field(max_length=200)
    value: str = Field(default="", max_length=4000)
    role: Literal["text", "editor", "button"] = "text"
    enabled: bool = True
    commits: bool | None = None  # host classification; unknown fails closed
    bounds: DesktopRect | None = None  # absolute screen points for a coordinate target


class DesktopParticipant(Contract):
    id: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=120)
    address: str = Field(min_length=1, max_length=200)


class DesktopConversation(Contract):
    id: str = Field(min_length=1, max_length=120)
    participants: tuple[DesktopParticipant, ...] = Field(min_length=1, max_length=8)
    latest_id: str = Field(min_length=1, max_length=120)
    incoming: str = Field(max_length=4000)


class DesktopObservation(Contract):
    app_id: str = Field(min_length=1, max_length=120)
    app_name: str = Field(min_length=1, max_length=120)
    window_id: str = Field(min_length=1, max_length=120)
    revision: int = Field(ge=0)
    frame: DesktopFrame
    elements: tuple[DesktopElement, ...] = Field(max_length=50)
    conversation: DesktopConversation | None = None


def digest(value: Contract) -> str:
    return hashlib.sha256(
        json.dumps(value.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class DesktopAction(Contract):
    kind: Literal["click", "type_text", "key", "scroll", "send_reply"]
    app_id: str = Field(min_length=1, max_length=120)
    window_id: str = Field(min_length=1, max_length=120)
    observation: str = Field(pattern=r"^[a-f0-9]{64}$")
    target_id: str = Field(min_length=1, max_length=120)
    text: str = Field(default="", max_length=4000)
    key: Literal["Tab", "Escape"] | None = None
    point: DesktopPoint | None = None
    delta: int = Field(default=0, ge=-10, le=10)

    @model_validator(mode="after")
    def arguments(self) -> "DesktopAction":
        if self.kind in {"type_text", "send_reply"} and not self.text.strip():
            raise ValueError("Text is required.")
        if self.kind not in {"type_text", "send_reply"} and self.text:
            raise ValueError("Unexpected text.")
        if (self.kind == "key") != (self.key is not None):
            raise ValueError("Provide a key only for key actions.")
        if self.kind != "click" and self.point:
            raise ValueError("Only clicks accept coordinates.")
        if self.kind != "scroll" and self.delta:
            raise ValueError("Only scroll actions accept a delta.")
        return self


class TaskCreate(Input):
    request_key: str = Field(pattern=r"^[A-Za-z0-9_-]{8,100}$")
    text: str = Field(min_length=1, max_length=4000, pattern=r"\S")
    fixture: Literal["messages", "notes"]  # explicit demo selection, no intent heuristic
    parent_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{32}$")


class TaskDecision(Input):
    approval_id: str
    revision: int = Field(ge=0, strict=True)
    decision: Literal["approve", "cancel"]
    text: str | None = Field(default=None, min_length=1, max_length=4000, pattern=r"\S")


class DesktopStep(Contract):
    label: str
    state: Literal["complete", "awaiting_approval", "running", "failed"]


class DesktopApproval(Contract):
    id: str
    action: DesktopAction
    expires_at: float


State = Literal[
    "queued",
    "running",
    "awaiting_approval",
    "needs_input",
    "complete",
    "cancelled",
    "failed",
    "interrupted",
    "outcome_unknown",
]
TERMINAL = {"needs_input", "complete", "cancelled", "failed", "interrupted", "outcome_unknown"}


class DesktopTask(Contract):
    id: str
    chat_id: str
    parent_id: str | None = None
    text: str
    fixture: Literal["messages", "notes"]
    state: State
    revision: int = 0
    stage: str = "Queued"
    observation: DesktopObservation | None = None
    approval: DesktopApproval | None = None
    approved_action: DesktopAction | None = None
    steps: tuple[DesktopStep, ...] = Field(default=(), max_length=4)
    error: str | None = None
    created_at: str
    fake: Literal[True] = True  # no native implementation exists in AS0


class TaskEvent(Contract):
    type: Literal["assistant.snapshot"] = "assistant.snapshot"
    task: DesktopTask


class TaskList(Contract):
    tasks: list[DesktopTask]
