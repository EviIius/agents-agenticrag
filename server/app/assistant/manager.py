"""Durable fake desktop tasks and one-time approvals, independent of HTTP lifetime."""

import asyncio
import json
import time
from collections.abc import AsyncIterator
from typing import Any

from ..db.connections import now, uid
from ..db.core import Store
from ..errors import AppError
from .contracts import (
    TERMINAL,
    DesktopApproval,
    DesktopTask,
    State,
    TaskCreate,
    TaskDecision,
    TaskEvent,
    digest,
)
from .driver import DesktopDriver, ProposalSource, UnknownOutcome, validate_action


class DesktopTasks:
    def __init__(self, store: Store, driver: DesktopDriver, proposer: ProposalSource) -> None:
        if not driver.fake:
            raise ValueError("AS0 has no native desktop implementation.")
        self.store, self.driver, self.proposer = store, driver, proposer
        self.allowed = frozenset({"fake.messages", "fake.notes"})
        self.jobs: dict[str, asyncio.Task[None]] = {}
        self.stops: dict[str, asyncio.Task[DesktopTask]] = {}
        self.locks: dict[str, asyncio.Lock] = {}
        self.desktop = asyncio.Lock()
        self.changed = asyncio.Condition()

    def lock(self, identifier: str) -> asyncio.Lock:
        return self.locks.setdefault(identifier, asyncio.Lock())

    async def get(self, identifier: str) -> DesktopTask:
        row = await self.store.one(
            "SELECT snapshot_json FROM assistant_tasks WHERE id=?", (identifier,)
        )
        if not row:
            raise AppError("not_found", "Computer task not found.", 404)
        return DesktopTask.model_validate_json(row["snapshot_json"])

    async def listing(self, chat_id: str) -> list[DesktopTask]:
        return [
            DesktopTask.model_validate_json(r["snapshot_json"])
            for r in await self.store.rows(
                "SELECT snapshot_json FROM (SELECT snapshot_json,updated_at,id FROM "
                "assistant_tasks WHERE chat_id=? ORDER BY "
                "state IN ('queued','running','awaiting_approval') DESC,"
                "updated_at DESC,id DESC LIMIT 50) ORDER BY updated_at,id",
                (chat_id,),
            )
        ]

    async def save(self, task: DesktopTask, **changes: Any) -> DesktopTask:
        # Validate all snapshots before persistence; model_copy alone does not validate.
        payload = task.model_dump(mode="json")
        payload.update(changes)
        payload["revision"] = task.revision + 1
        task = DesktopTask.model_validate_json(json.dumps(payload))
        raw = task.model_dump_json()
        async with self.changed:
            await self.store.batch(
                [
                    (
                        "UPDATE assistant_tasks SET "
                        "snapshot_json=?,state=?,updated_at=? WHERE id=?",
                        (raw, task.state, now(), task.id),
                    ),
                    (
                        "INSERT INTO assistant_events(task_id,snapshot_json) VALUES (?,?)",
                        (task.id, raw),
                    ),
                ]
            )
            self.changed.notify_all()
        return task

    async def create(self, chat_id: str, body: TaskCreate) -> DesktopTask:
        async with self.lock("create"):
            old = await self.store.one(
                "SELECT id,chat_id,request_json FROM assistant_tasks WHERE request_key=?",
                (body.request_key,),
            )
            if old:
                if old["chat_id"] != chat_id or old["request_json"] != body.model_dump_json():
                    raise AppError(
                        "assistant_conflict", "That request key belongs to another task.", 409
                    )
                return await self.get(old["id"])
            if not await self.store.one("SELECT id FROM chats WHERE id=?", (chat_id,)):
                raise AppError("not_found", "Chat not found.", 404)
            if body.parent_id and not await self.store.one(
                "SELECT id FROM messages WHERE id=? AND chat_id=?", (body.parent_id, chat_id)
            ):
                raise AppError("assistant_parent", "The source message is not in this chat.", 422)
            count = await self.store.one(
                "SELECT count(*) AS total FROM assistant_tasks "
                "WHERE state IN ('queued','running','awaiting_approval')"
            )
            if count and count["total"] >= 8:
                raise AppError(
                    "assistant_busy", "Finish or stop a computer task before adding more.", 409
                )
            task = DesktopTask(
                id=uid(),
                chat_id=chat_id,
                parent_id=body.parent_id,
                text=body.text,
                fixture=body.fixture,
                state="queued",
                created_at=now(),
            )
            await self.store.execute(
                "INSERT INTO assistant_tasks VALUES (?,?,?,?,?,?,?,?,0)",
                (
                    task.id,
                    chat_id,
                    body.parent_id,
                    body.request_key,
                    body.model_dump_json(),
                    task.model_dump_json(),
                    task.state,
                    now(),
                ),
            )
            task = await self.save(task)
            self.jobs[task.id] = asyncio.create_task(self.prepare(task.id))
            return task

    async def prepare(self, identifier: str) -> None:
        try:
            async with asyncio.timeout(30), self.lock(identifier):
                task = await self.get(identifier)
                task = await self.save(task, state="running", stage="Opening fake app")
                app_id = "fake." + task.fixture
                async with self.desktop:
                    if app_id not in self.allowed:
                        raise AppError("assistant_permission", "This app is not allowed.", 403)
                    await self.driver.open(app_id)
                    observation = await self.driver.observe(app_id)
                if observation.conversation and len(observation.conversation.participants) != 1:
                    raise AppError(
                        "assistant_ambiguous", "Choose one recipient before preparing a reply.", 409
                    )
                if task.fixture == "messages" and not observation.conversation:
                    raise AppError(
                        "assistant_source", "The selected conversation is unavailable.", 409
                    )
                if observation.app_id != app_id:
                    raise AppError(
                        "assistant_target", "The observed app does not match the task.", 409
                    )
                action = await self.proposer.propose(task, observation)
                validate_action(observation, action, self.allowed, commit=True)
                approval = DesktopApproval(id=uid(), action=action, expires_at=time.time() + 300)
                await self.store.execute(
                    "INSERT INTO assistant_approvals VALUES (?,?,?,?,?)",
                    (approval.id, task.id, digest(action), "pending", approval.expires_at),
                )
                await self.save(
                    task,
                    state="awaiting_approval",
                    stage="Review the fake action",
                    observation=observation.model_dump(mode="json"),
                    approval=approval.model_dump(mode="json"),
                    steps=[
                        {"label": "Opened " + observation.app_name, "state": "complete"},
                        {
                            "label": "Read selected conversation"
                            if observation.conversation
                            else "Read note editor",
                            "state": "complete",
                        },
                        {
                            "label": (
                                "Review reply" if observation.conversation else "Review note"
                            ),
                            "state": "awaiting_approval",
                        },
                    ],
                )
        except asyncio.CancelledError:
            raise
        except AppError as exc:
            task = await self.get(identifier)
            await self.save(
                task, state="needs_input", stage=exc.message, error=exc.code, approval=None
            )
        except Exception:
            task = await self.get(identifier)
            await self.save(
                task, state="failed", stage="Could not prepare this computer task.", approval=None
            )

    async def decide(self, identifier: str, body: TaskDecision) -> DesktopTask:
        if body.decision == "cancel":
            return await self.cancel(identifier)
        async with self.lock(identifier):
            task = await self.get(identifier)
            approval = task.approval
            if (
                task.state != "awaiting_approval"
                or not approval
                or body.revision != task.revision
                or body.approval_id != approval.id
            ):
                raise AppError("assistant_stale", "This approval is no longer current.", 409)
            cancellation = await self.store.one(
                "SELECT cancel_requested FROM assistant_tasks WHERE id=?", (identifier,)
            )
            if cancellation and cancellation["cancel_requested"]:
                raise AppError("assistant_stale", "This task is stopping.", 409)
            record = await self.store.one(
                "SELECT * FROM assistant_approvals WHERE id=?", (approval.id,)
            )
            if (
                not record
                or record["state"] != "pending"
                or record["binding"] != digest(approval.action)
            ):
                raise AppError("assistant_stale", "This approval is no longer current.", 409)
            if time.time() >= approval.expires_at:
                await self.invalidate(task, "Approval expired. Start a new task.")
                return await self.get(identifier)
            action = approval.action
            if body.text is not None:
                action = type(action).model_validate({**action.model_dump(), "text": body.text})
            # One task worker owns dispatch; HTTP disconnect cannot cancel an accepted action.
            task = await self.save(
                task,
                state="running",
                stage="Checking the selected app",
                approved_action=action.model_dump(mode="json"),
                approval=DesktopApproval(
                    id=approval.id, action=action, expires_at=approval.expires_at
                ).model_dump(mode="json"),
            )
            await self.store.execute(
                "UPDATE assistant_approvals SET state='consumed',binding=? WHERE id=?",
                (digest(action), approval.id),
            )
            self.jobs[identifier] = asyncio.create_task(self.commit(identifier))
            return task

    async def invalidate(self, task: DesktopTask, reason: str) -> None:
        if task.approval:
            await self.store.execute(
                "UPDATE assistant_approvals SET state='expired' WHERE id=?", (task.approval.id,)
            )
        await self.save(
            task, state="needs_input", stage=reason, error="assistant_stale", approval=None
        )

    async def commit(self, identifier: str) -> None:
        dispatched = False
        try:
            async with asyncio.timeout(30), self.lock(identifier), self.desktop:
                task = await self.get(identifier)
                if task.state != "running" or not task.approval:
                    return
                cancellation = await self.store.one(
                    "SELECT cancel_requested FROM assistant_tasks WHERE id=?", (identifier,)
                )
                if cancellation and cancellation["cancel_requested"]:
                    await self.save(task, state="cancelled", stage="Stopped", approval=None)
                    return
                approval_id = task.approval.id
                action = task.approval.action
                fresh = await self.driver.observe(action.app_id)
                if not task.observation or digest(fresh) != digest(task.observation):
                    await self.invalidate(
                        task, "The app or incoming message changed. Start a new task."
                    )
                    return
                validate_action(fresh, action, self.allowed, commit=True)
                task = await self.save(task, stage="Performing the fake action")
                dispatched = True
                receipt = await self.driver.act(approval_id, action)
                after = await self.driver.observe(action.app_id)
                if action.kind == "type_text":
                    verified = any(
                        e.id == action.target_id and e.value == action.text for e in after.elements
                    )
                else:
                    verified = bool(receipt) and after.revision > fresh.revision
                if (
                    after.app_id != fresh.app_id
                    or after.window_id != fresh.window_id
                    or not verified
                ):
                    raise UnknownOutcome
                await self.save(
                    task,
                    state="complete",
                    stage="Fake action complete",
                    observation=after.model_dump(mode="json"),
                    approval=None,
                    steps=[
                        s.model_copy(update={"state": "complete"}).model_dump(mode="json")
                        for s in task.steps
                    ],
                )
        except asyncio.CancelledError:
            if dispatched:
                task = await self.get(identifier)
                await self.save(
                    task,
                    state="outcome_unknown",
                    stage="Stopped. Check the app before trying again.",
                    approval=None,
                )
            raise
        except UnknownOutcome:
            task = await self.get(identifier)
            await self.save(
                task,
                state="outcome_unknown",
                stage="Could not confirm the action. Check the app before trying again.",
                approval=None,
            )
        except AppError as exc:
            task = await self.get(identifier)
            await self.save(
                task,
                state="outcome_unknown" if dispatched else "needs_input",
                stage=exc.message,
                error=exc.code,
                approval=None,
            )
        except Exception:
            task = await self.get(identifier)
            await self.save(
                task,
                state="outcome_unknown" if dispatched else "failed",
                stage="Could not confirm this computer task.",
                approval=None,
            )

    async def cancel(self, identifier: str) -> DesktopTask:
        task = await self.get(identifier)
        if task.state in TERMINAL:
            return task
        # Intent is durable before signalling the worker. HTTP lifetime cannot undo Stop.
        await self.store.execute(
            "UPDATE assistant_tasks SET cancel_requested=1 WHERE id=?", (identifier,)
        )
        if identifier not in self.stops:
            self.stops[identifier] = asyncio.create_task(self.stop_task(identifier))
        return await asyncio.shield(self.stops[identifier])

    async def stop_task(self, identifier: str) -> DesktopTask:
        # Cancel before taking the task lock so a queued/running worker cannot outlive Stop.
        job = self.jobs.get(identifier)
        if job and not job.done():
            job.cancel()
            await asyncio.gather(job, return_exceptions=True)
        async with self.lock(identifier):
            task = await self.get(identifier)
            if task.state in TERMINAL:
                return task
            await self.store.execute(
                "UPDATE assistant_approvals SET state='cancelled' WHERE task_id=? AND "
                "state='pending'",
                (identifier,),
            )
            return await self.save(task, state="cancelled", stage="Stopped", approval=None)

    async def cancel_chat(self, chat_id: str) -> None:
        for row in await self.store.rows(
            "SELECT id FROM assistant_tasks WHERE chat_id=? "
            "AND state IN ('queued','running','awaiting_approval')",
            (chat_id,),
        ):
            await self.cancel(row["id"])

    async def recover(self) -> None:
        for row in await self.store.rows(
            "SELECT snapshot_json,cancel_requested FROM assistant_tasks "
            "WHERE state IN ('queued','running','awaiting_approval')"
        ):
            task = DesktopTask.model_validate_json(row["snapshot_json"])
            record = await self.store.one(
                "SELECT state FROM assistant_approvals WHERE task_id=? AND state='consumed'",
                (task.id,),
            )
            state: State = (
                "outcome_unknown"
                if record
                else "cancelled"
                if row["cancel_requested"]
                else "interrupted"
            )
            await self.store.execute(
                "UPDATE assistant_approvals SET state='expired' WHERE task_id=? AND "
                "state='pending'",
                (task.id,),
            )
            await self.save(
                task,
                state=state,
                stage="Stopped"
                if state == "cancelled"
                else "Interrupted. Review the app before starting another task.",
                approval=None,
            )

    async def tail(self, identifier: str, after: int = 0) -> AsyncIterator[tuple[int, TaskEvent]]:
        while True:
            async with self.changed:
                rows = await self.store.rows(
                    "SELECT id,snapshot_json FROM assistant_events WHERE task_id=? AND "
                    "id>? ORDER BY id",
                    (identifier, after),
                )
                task = await self.get(identifier)
                if not rows and task.state not in TERMINAL:
                    await self.changed.wait()
                    continue
            for row in rows:
                after = row["id"]
                yield after, TaskEvent(task=DesktopTask.model_validate_json(row["snapshot_json"]))
            if task.state in TERMINAL:
                return

    async def close(self) -> None:
        # Shutdown interrupts work; it is not a user's Cancel or an automatic resume.
        await asyncio.gather(*self.stops.values(), return_exceptions=True)
        workers = [job for job in self.jobs.values() if not job.done()]
        for job in workers:
            job.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        await self.recover()
