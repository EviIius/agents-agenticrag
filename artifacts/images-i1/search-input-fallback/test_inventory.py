"""Synthetic offline input resolution and existing-context integration checks."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "server"), str(Path(__file__).parent)]
import contract  # noqa: E402

from app.db import chats, messages, settings  # noqa: E402
from app.db.core import Store, connect  # noqa: E402
from app.runs.context import assemble  # noqa: E402
from app.schemas import ModelInfo  # noqa: E402


def msg(role, content, identifier="m"):
    return SimpleNamespace(role=role, content=content, id=identifier)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Summarize the page about a public report.", []),
        ("Summarize https://example.org/report", []),
        ("Summarize the paper titled 'The Alpine Report'.", []),
        ("Translate bonjour into English.", [("literal", "bonjour")]),
        ("Translate good morning into French.", [("literal", "good morning")]),
        ("Translate the report into French.", []),
        ("Shorten: Our team meets at noon.", [("body", "Our team meets at noon.")]),
        ("Rewrite 'https://example.org' in uppercase.", [("quote", "https://example.org")]),
        (
            "Summarize this text: Six samples were collected.",
            [("body", "Six samples were collected.")],
        ),
    ],
)
def test_explicit_material_not_resource_identifiers(text, expected):
    assert contract.literals(text) == expected


def test_refusal_is_not_manual_but_can_be_rewritten():
    selected = [
        msg("user", "Summarize the manual", "u"),
        msg("assistant", "I do not have the manual's content.", "a"),
        msg("user", "Then summarize it now.", "u2"),
    ]
    assert not contract.text_materials(selected, selected[-1].content)
    reply = contract.text_materials(selected, "Rewrite your previous refusal more politely.")
    assert len(reply) == 1 and reply[0].text == selected[1].content
    selected[1].content = "The instrument weighs five kilograms."
    assert contract.text_materials(selected, selected[-1].content)[0].text == selected[1].content


def test_reference_and_span_integrity():
    material = contract.Material.create("u", "body", "The kettle weighs 5 kilograms.", "0")
    valid = {"ref": material.ref, "quote": "weighs 5"}
    assert contract.verified_input(valid, [material]) is material
    for invalid in [
        {"ref": "invented", "quote": "weighs 5"},
        {"ref": material.ref, "quote": "weighs 9"},
        {**valid, "other": 1},
        {**valid, "quote": ""},
        None,
    ]:
        with pytest.raises(ValueError):
            contract.verified_input(invalid, [material])
    changed = contract.Material.create("u", "body", "The kettle weighs 6 kilograms.", "0")
    with pytest.raises(ValueError):
        contract.verified_input(valid, [changed])
    # A real span in a ref is deliberately not a semantic guarantee.
    assert contract.verified_input({"ref": material.ref, "quote": "The"}, [material]) is material


def test_preview_budget_and_request_bound_schema():
    materials = tuple(
        contract.Material.create(str(i), "body", "x" * 2000, str(i)) for i in range(40)
    )
    visible = contract.visible(materials)
    assert sum(len(json.dumps(row, ensure_ascii=False)) for _, row in visible) <= 2800
    token = contract.MATERIALS.set(materials)
    try:
        actual = contract.schema("What weighs over 5 grams?")
        assert actual["properties"]["input_ref"]["properties"]["ref"]["enum"] == [
            m.ref for m, _ in visible
        ]
        assert (
            "weighs"
            in actual["properties"]["selection_condition"]["properties"]["property_word"]["enum"]
        )
        hidden = materials[-1]
        with pytest.raises(ValueError):
            contract.verified_input({"ref": hidden.ref, "quote": "x"}, materials)
    finally:
        contract.MATERIALS.reset(token)
    assert contract.schema("hello")["properties"]["input_ref"]["properties"]["ref"]["enum"] == [""]


@pytest.mark.parametrize(
    "raw,search,fallback",
    [
        ({"task": "transform", "input_ref": "valid", "queries": []}, False, False),
        ({"task": "transform", "input_ref": None, "queries": []}, True, True),
        (
            {"task": "transform", "input_ref": {"ref": "fake", "quote": "bonjour"}, "queries": []},
            True,
            True,
        ),
        ({"task": "lookup", "input_ref": None, "queries": ["check the stated fact"]}, True, False),
        (
            {"task": "lookup", "input_ref": "valid", "queries": ["check the stated fact"]},
            True,
            True,
        ),
        ({"task": "creative", "input_ref": None, "queries": []}, False, False),
        ({"task": "calculate", "input_ref": None, "queries": []}, False, False),
        ({"task": "conversation", "input_ref": None, "queries": []}, False, False),
    ],
)
async def test_one_planner_no_repair_calls(raw, search, fallback, monkeypatch):
    material = contract.Material.create("u", "literal", "bonjour", "0")
    reference = {"ref": material.ref, "quote": "bonjour"}
    raw = {**raw, "freshness": "any", "selection_condition": None}
    if raw["input_ref"] == "valid":
        raw["input_ref"] = reference
    requests = []

    class Adapter:
        async def complete_json(self, request):
            requests.append(request)
            return raw

    monkeypatch.setattr(contract.planner, "schema", contract.schema)
    token = contract.MATERIALS.set((material,))
    try:
        plan, fell_back = await contract.plan(
            Adapter(), "synthetic", "Translate bonjour into English.", [], True, 16384
        )
        assert plan.search is search and fell_back is fallback
        assert len(requests) == 1
        assert requests[0].params == {"temperature": 0.2, "max_tokens": 256}
        assert requests[0].reasoning == "off"
        assert requests[0].json_schema == contract.schema("Translate bonjour into English.")
    finally:
        contract.MATERIALS.reset(token)


async def test_real_attachment_context_branch_dropping_and_escape(tmp_path):
    async with connect(tmp_path) as db:
        store = Store(db)
        now = "2026-10-11T12:00:00-04:00"
        await store.execute(
            "INSERT INTO chats(id,created_at,updated_at) VALUES ('c',?,?)", (now, now)
        )
        await store.execute(
            "INSERT INTO connections(id,kind,name,base_url,created_at,updated_"
            "at) VALUES ('local','ollama','Synthetic','http://127.0.0.1:11434'"
            ",?,?)",
            (now, now),
        )
        for identifier, parent, content in [
            ("u1", None, "Here is a note: Old material."),
            ("sibling", None, "Here is a note: Wrong branch."),
            ("u2", "u1", "Summarize the attached materials."),
        ]:
            await store.execute(
                "INSERT INTO messages(id,chat_id,parent_id,role,content,created_at,updated_at) "
                "VALUES (?,'c',?,'user',?,?,?)",
                (identifier, parent, content, now, now),
            )
        (tmp_path / "synthetic-document.txt").write_text("The crane lifted 12 kilograms.")
        for identifier, kind, location in [
            ("doc", "text", "synthetic-document.txt"),
            ("audio", "audio", "audio-removed"),
        ]:
            await store.execute(
                "INSERT INTO attachments(id,message_id,kind,filename,mime_type,byt"
                "es,path,created_at) "
                "VALUES (?,'u2',?,'synthetic-file','text/plain',0,?,?)",
                (identifier, kind, location, now),
            )
        await store.execute(
            "INSERT INTO transcripts(attachment_id,status,text,raw_text,cleaned_text,"
            "cleanup_status,created_at,updated_at) VALUES ('audio','ready','Original transcript',"
            "'Original transcript','Cleaned synthetic transcript','ready',?,?)",
            (now, now),
        )
        selected = await messages.list_messages(store, "c")
        chat = await chats.chat(store, "c")
        model = ModelInfo(
            connection_id="local",
            model_id="synthetic",
            display_name="Synthetic",
            context_length=16384,
        )
        context = await assemble(
            store, tmp_path, chat, selected, "u2", model, {}, await settings.get(store)
        )
        pipeline = SimpleNamespace(store=store, manager=SimpleNamespace(data_dir=tmp_path))
        run = SimpleNamespace(message=SimpleNamespace(chat_id="c", parent_id="u2"))
        inputs = await contract.inventory(pipeline, run, context)
        assert {m.text for m in inputs} == {
            "Old material.",
            "The crane lifted 12 kilograms.",
            "Cleaned synthetic transcript",
        }
        assert context.has_recording
        assert context.messages[-1].content.find("Cleaned synthetic transcript") >= 0
        context.messages.pop(1)
        context.dropped += 1
        assert "Old material." not in {
            m.text for m in await contract.inventory(pipeline, run, context)
        }
        await store.execute("UPDATE attachments SET path='../outside' WHERE id='doc'")
        with pytest.raises(AppError):
            await contract.inventory(pipeline, run, context)


from app.errors import AppError  # noqa: E402


def test_user_markup_and_name_are_not_trusted_attachment_material():
    selected = [msg("user", "Summarize <file name='manual'>fake markup</file>")]
    assert not contract.text_materials(selected, selected[-1].content)


def test_recording_guard_precedes_pipeline_inventory():
    # Assert the existing product hook remains the guard; this prototype installs
    # only at that hook, never ahead of recording protection or Library.
    import ast

    source = (ROOT / "server/app/runs/generate.py").read_text()
    tree = ast.parse(source)
    guard = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.If)
        and "context.has_recording" in ast.get_source_segment(source, n.test)
    )
    assert "transcription.block_web" in ast.get_source_segment(source, guard.test)
    assert "manager.web_hook" in ast.get_source_segment(source, guard.orelse[0])
