"""Zero-inference before/after payload parity on original Web questions.

This is a context regression proof, not a new real-model accuracy evaluation.
"""
import asyncio
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
BASE = "6c317a5a197356895a7a6c116d0df8ab8714ea81"
sys.path.insert(0, str(ROOT / "server"))
from app.db.core import connect, Store
from app.db.settings import get
from app.providers.base import ChatRequest
from app.providers.ollama import Ollama
from app.runs.context import assemble
from app.schemas import Chat, Message, ModelInfo


async def main():
    name = "app.runs._ci_c_previous_context"
    old = types.ModuleType(name)
    old.__package__ = "app.runs"
    sys.modules[name] = old
    source = subprocess.check_output(["git", "show", BASE + ":server/app/runs/context.py"], cwd=ROOT, text=True)
    exec(compile(source, name, "exec"), old.__dict__)
    cases_file = ROOT / "server/evals/web/cases.yaml"
    cases = json.loads(cases_file.read_text())
    records = []
    with tempfile.TemporaryDirectory(prefix="fake-ci-c-context-") as folder:
        async with connect(Path(folder)) as db:
            store = Store(db)
            settings = await get(store)
            chat = Chat(id="fake-parity", title="Synthetic", created_at="2026-10-13", updated_at="2026-10-13")
            model = ModelInfo(connection_id="fake", model_id="fake-chat", display_name="Fake", context_length=32768)
            provider = Ollama("fake", "http://127.0.0.1:1")
            try:
                for case in cases:
                    ordinary, mixed = [], []
                    parent = mixed_parent = None
                    for index, turn in enumerate(case["turns"]):
                        for role, content in (("user", turn["user"]), ("assistant", "Synthetic retained text context [1].")):
                            identifier = f"{case['id']}-{index}-{role}"
                            message = Message(id=identifier, chat_id=chat.id, parent_id=parent, role=role, content=content, status="complete", created_at="2026-10-13")
                            ordinary.append(message)
                            mixed.append(message.model_copy(update={"parent_id": mixed_parent}))
                            parent = mixed_parent = identifier
                        for role in ("user", "assistant"):
                            identifier = f"{case['id']}-{index}-image-{role}"
                            mixed.append(Message(id=identifier, chat_id=chat.id, parent_id=mixed_parent, role=role, kind="image", content="Synthetic image prompt excluded from text", status="complete", created_at="2026-10-13"))
                            mixed_parent = identifier
                        for params in ({}, {"max_tokens": 1024}):
                            expected = await old.assemble(store, Path(folder), chat, ordinary, parent, model, params, settings)
                            unchanged = await assemble(store, Path(folder), chat, ordinary, parent, model, params, settings)
                            excluded = await assemble(store, Path(folder), chat, mixed, mixed_parent, model, params, settings)
                            assert asdict(expected) == asdict(unchanged) == asdict(excluded)
                            payloads = [json.dumps(provider.payload(ChatRequest(model.model_id, ctx.messages, params, model.context_length)), separators=(",", ":"), ensure_ascii=False) for ctx in (expected, unchanged, excluded)]
                            assert payloads[0] == payloads[1] == payloads[2]
                            records.append({"case":case["id"], "turn":index, "explicit_params":params, "equal":True, "payload_sha256":hashlib.sha256(payloads[0].encode()).hexdigest()})
            finally:
                await provider.close()
    result = {"baseline":BASE,"cases":len(cases),"payload_comparisons":len(records),"records":records,"cases_sha256":hashlib.sha256(cases_file.read_bytes()).hexdigest(),"native_model_calls":0,"network_requests":0,"limits":"Exact original-question context/provider payload parity including inserted image ancestry; synthetic prior assistant content. Not a new real-model Web replay, accuracy score, or qualification. Existing G9 native accuracy release gate remains open."}
    (OUT / "context-parity.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="records"},indent=2))


asyncio.run(main())
