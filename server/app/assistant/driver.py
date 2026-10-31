"""Driver boundary and synthetic AS0 implementation; no macOS API imports."""

import asyncio
from typing import Protocol

from ..errors import AppError
from .contracts import (
    DesktopAction,
    DesktopConversation,
    DesktopElement,
    DesktopFrame,
    DesktopObservation,
    DesktopParticipant,
    DesktopRect,
    DesktopTask,
    digest,
    screen_point,
)


class UnknownOutcome(Exception):
    """A dispatched operation may have committed. Never replay it automatically."""


class DesktopDriver(Protocol):
    fake: bool

    async def open(self, app_id: str) -> None: ...
    async def observe(self, app_id: str) -> DesktopObservation: ...
    async def act(self, action_id: str, action: DesktopAction) -> str | None: ...


class ProposalSource(Protocol):
    async def propose(
        self, task: DesktopTask, observation: DesktopObservation
    ) -> DesktopAction: ...


def validate_action(
    observation: DesktopObservation,
    action: DesktopAction,
    allowed: frozenset[str],
    *,
    commit: bool = False,
) -> None:
    if observation.app_id not in allowed or action.app_id not in allowed:
        raise AppError("assistant_permission", "This app is not allowed.", 403)
    if (
        action.app_id != observation.app_id
        or action.window_id != observation.window_id
        or action.observation != digest(observation)
    ):
        raise AppError("assistant_stale", "The app changed. Review the task again.", 409)
    if action.kind == "send_reply":
        thread = observation.conversation
        if (
            not commit
            or not thread
            or len(thread.participants) != 1
            or action.target_id != thread.id
        ):
            raise AppError("assistant_permission", "Choose one conversation before sending.", 403)
        return
    element = next((e for e in observation.elements if e.id == action.target_id), None)
    if not element or not element.enabled:
        raise AppError("assistant_target", "That control is no longer available.", 409)
    if action.kind == "type_text" and (element.role != "editor" or element.commits is not False):
        raise AppError("assistant_permission", "Text can only go into a verified editor.", 403)
    if action.kind in {"click", "key"} and element.commits is not False:
        raise AppError("assistant_permission", "This action needs a separate send approval.", 403)
    if action.point:
        x, y = screen_point(observation.frame, action.point)
        bounds = element.bounds
        if not bounds or not (
            bounds.x <= x < bounds.x + bounds.width and bounds.y <= y < bounds.y + bounds.height
        ):
            raise AppError("assistant_target", "The point does not belong to that control.", 422)


class FakeDesktopDriver:
    """One shared driver for two invented apps. It cannot launch or send anything."""

    fake = True

    def __init__(self) -> None:
        frame = DesktopFrame(
            bounds=DesktopRect(x=0, y=0, width=800, height=600),
            scale=2,
            capture_width=1600,
            capture_height=1200,
            crop=DesktopRect(x=0, y=0, width=1600, height=1200),
            image_width=800,
            image_height=600,
        )
        self.windows = {
            "fake.messages": DesktopObservation(
                app_id="fake.messages",
                app_name="Fake Messages",
                window_id="messages-window",
                revision=0,
                frame=frame,
                elements=(DesktopElement(id="send", label="Send", role="button", commits=True),),
                conversation=DesktopConversation(
                    id="synthetic-thread",
                    participants=(
                        DesktopParticipant(
                            id="synthetic-alex",
                            name="Alex (synthetic)",
                            address="alex@example.invalid",
                        ),
                    ),
                    latest_id="synthetic-incoming-1",
                    incoming="Can we meet at 3 pm?",
                ),
            ),
            "fake.notes": DesktopObservation(
                app_id="fake.notes",
                app_name="Fake Notes",
                window_id="notes-window",
                revision=0,
                frame=frame,
                elements=(
                    DesktopElement(
                        id="editor",
                        label="Note",
                        role="editor",
                        commits=False,
                        bounds=DesktopRect(x=0, y=0, width=800, height=600),
                    ),
                ),
            ),
        }
        self.permission = True
        self.executed: list[tuple[str, DesktopAction]] = []
        self.opened: list[str] = []
        self.receipts: dict[str, str] = {}
        self.hold: asyncio.Event | None = None
        self.active = asyncio.Event()
        self.reaped = asyncio.Event()
        self.uncertain = False

    def check(self) -> None:
        if not self.permission:
            raise AppError(
                "assistant_permission", "Computer access is unavailable or revoked.", 403
            )

    async def open(self, app_id: str) -> None:
        self.check()
        if app_id not in self.windows:
            raise AppError("assistant_permission", "This app is not allowed.", 403)
        self.opened.append(app_id)

    async def observe(self, app_id: str) -> DesktopObservation:
        self.check()
        return self.windows[app_id]

    async def act(self, action_id: str, action: DesktopAction) -> str | None:
        self.check()
        self.active.set()
        self.reaped.clear()
        try:
            if self.hold:
                await self.hold.wait()
            self.check()
            observation = await self.observe(action.app_id)
            validate_action(observation, action, frozenset(self.windows), commit=True)
            if action_id in self.receipts:
                raise UnknownOutcome
            if action.kind not in {"type_text", "send_reply"}:
                raise AppError(
                    "assistant_unsupported", "This demo does not execute that action.", 422
                )
            self.executed.append((action_id, action))
            elements = observation.elements
            if action.kind == "type_text":
                elements = tuple(
                    e.model_copy(update={"value": action.text}) if e.id == action.target_id else e
                    for e in elements
                )
            self.windows[action.app_id] = observation.model_copy(
                update={
                    "revision": observation.revision + 1,
                    "elements": elements,
                }
            )
            self.receipts[action_id] = "fake-receipt-" + action_id
            if self.uncertain:
                raise UnknownOutcome
            return self.receipts[action_id]
        finally:
            self.reaped.set()


class ScriptedProposal:
    """Explicit fixture, not natural-language interpretation or a model."""

    async def propose(self, task: DesktopTask, observation: DesktopObservation) -> DesktopAction:
        await asyncio.sleep(0)
        fixture = task.fixture
        return DesktopAction(
            kind="send_reply" if fixture == "messages" else "type_text",
            app_id=observation.app_id,
            window_id=observation.window_id,
            observation=digest(observation),
            target_id=observation.conversation.id if observation.conversation else "editor",
            text="I can meet at 3 pm."
            if fixture == "messages"
            else "A synthetic note from Aether.",
        )
