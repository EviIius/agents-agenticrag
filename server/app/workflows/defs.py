"""Definition drafts, optimistic writes and immutable snapshot identities."""

from __future__ import annotations

from uuid import uuid4

from ..db.core import Store
from ..errors import AppError
from .graph import GraphDoc, StartConfig, StartNode, canonical, execution_hash
from .graph_schemas import DefCreate, Definition, DefSave, Snapshot
from .jobs import now
from .template_graphs import template_graph


class Conflict(AppError):
    def __init__(self, current: Definition) -> None:
        super().__init__("workflow_conflict", "This workflow changed on another device.", 409)
        self.current = current


def check_size(graph: GraphDoc) -> None:
    if len(canonical(graph.model_dump(by_alias=True)).encode()) > 512 * 1024:
        raise AppError("workflow_size", "Keep this workflow document under 512 KB.", 422)


class Definitions:
    def __init__(self, store: Store) -> None:
        import asyncio

        self.store = store
        self.lock = asyncio.Lock()

    async def get(self, identifier: str) -> Definition:
        row = await self.store.one("SELECT * FROM workflow_defs WHERE id=?", (identifier,))
        if not row:
            raise AppError("not_found", "This workflow is not available.", 404)
        row["graph"] = GraphDoc.model_validate_json(row.pop("graph_json"))
        return Definition(**row)

    async def list_defs(self) -> list[Definition]:
        return [
            await self.get(row["id"])
            for row in await self.store.rows(
                "SELECT id FROM workflow_defs WHERE archived_at IS NULL ORDER BY u"
                "pdated_at DESC,id DESC"
            )
        ]

    async def create(self, body: DefCreate) -> Definition:
        if body.graph and body.template_id:
            raise AppError("workflow_input", "Choose a template or a workflow document.", 422)
        graph = body.graph or (
            template_graph(body.template_id)
            if body.template_id
            else GraphDoc.model_validate(
                {
                    "nodes": [
                        StartNode(
                            id="n_start",
                            key="start",
                            title="Start",
                            kind="start",
                            config=StartConfig(),
                        )
                    ]
                }
            )
        )
        graph = graph.model_copy(deep=True)
        if body.default_model:
            graph.settings.default_model = body.default_model
        check_size(graph)
        identifier, clock = uuid4().hex, now()
        await self.store.execute(
            (
                "INSERT INTO workflow_defs(id,name,graph_json,graph_hash,template_"
                "id,created_at,updated_at) VALUES(?,?,?,?,?,?,?)"
            ),
            (
                identifier,
                body.name,
                canonical(graph.model_dump(by_alias=True)),
                execution_hash(graph),
                body.template_id,
                clock,
                clock,
            ),
        )
        return await self.get(identifier)

    async def save(self, identifier: str, body: DefSave) -> Definition:
        check_size(body.graph)
        async with self.lock:
            current = await self.get(identifier)
            if current.archived_at:
                raise AppError(
                    "workflow_archived", "Duplicate this archived workflow before editing.", 409
                )
            if current.version != body.version and not body.force:
                raise Conflict(current)
            clock = now()
            await self.store.batch(
                [
                    (
                        (
                            "UPDATE workflow_defs SET name=?,description=?,icon=?,graph_json=?"
                            ",graph_hash=?,version=version+1,updated_at=? WHERE id=?"
                        ),
                        (
                            body.name,
                            body.description,
                            body.icon,
                            canonical(body.graph.model_dump(by_alias=True)),
                            execution_hash(body.graph),
                            clock,
                            identifier,
                        ),
                    ),
                ]
            )
            return await self.get(identifier)

    async def duplicate(self, identifier: str) -> Definition:
        source = await self.get(identifier)
        result = await self.create(
            DefCreate(name=(source.name[:73] + " (copy)"), graph=source.graph)
        )
        return await self.save(
            result.id,
            DefSave(
                name=result.name,
                description=source.description,
                icon=source.icon,
                graph=result.graph,
                version=1,
            ),
        )

    async def archive(self, identifier: str) -> None:
        await self.get(identifier)
        await self.store.execute(
            "UPDATE workflow_defs SET archived_at=?,updated_at=? WHERE id=?",
            (now(), now(), identifier),
        )

    async def snapshots(self, identifier: str) -> list[Snapshot]:
        await self.get(identifier)
        rows = await self.store.rows(
            (
                "SELECT s.*,COUNT(r.id) run_count FROM workflow_def_snapshots s LE"
                "FT JOIN workflow_graph_runs r ON r.snapshot_id=s.id WHERE s.def_i"
                "d=? GROUP BY s.id ORDER BY s.created_at DESC,s.id DESC"
            ),
            (identifier,),
        )
        return [
            Snapshot(
                **{k: v for k, v in row.items() if k != "graph_json"},
                graph=GraphDoc.model_validate_json(row["graph_json"]),
            )
            for row in rows
        ]

    async def label(self, identifier: str, snapshot_id: str, label: str | None) -> Snapshot:
        snapshots = await self.snapshots(identifier)
        if not any(s.id == snapshot_id for s in snapshots):
            raise AppError("not_found", "This saved version is not available.", 404)
        await self.store.execute(
            "UPDATE workflow_def_snapshots SET label=? WHERE id=? AND def_id=?",
            (label, snapshot_id, identifier),
        )
        return next(s for s in await self.snapshots(identifier) if s.id == snapshot_id)
