"""Declared native I1 qualification; synthetic prompts, no automatic trial retries."""
import asyncio
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server"))
from app.config import Settings
from app.db import connections
from app.main import create_app
from app.providers.base import ChatRequest, Finish, ProviderMessage, TextDelta
from app.schemas import ConnectionCreate, ImageCreate

TRIAL = sys.argv[1] if len(sys.argv) > 1 else "corrected-2"
if not TRIAL.replace("-", "").isalnum():
    raise ValueError("Invalid trial identifier")
EVIDENCE = ROOT / "artifacts/images-i1/native" / TRIAL
DATA = Path.home() / ".local/share/workbench/image-worker/product" / ("qualification-data-" + TRIAL)
PROFILE = "qwen3:30b-a3b-workbench-32k"
PROMPT = json.loads((ROOT / "image_worker/memory/trial.json").read_text())["cases"][0]["prompt"]


def write(name, value):
    path = EVIDENCE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


async def main():
    if DATA.exists() or (EVIDENCE / "result.json").exists():
        raise RuntimeError("Refusing an unretained repeated native trial")
    manifest = json.loads((EVIDENCE / "source-manifest.json").read_text())
    for name, digest in manifest.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError("Frozen native candidate changed: " + name)
    app = create_app(Settings(data_dir=DATA, image_home=Path.home() / ".local/share/workbench/image-worker/product"))
    results = {"stages": [], "passed": False, "new_image_calls": 0, "chat_payload": {"model": PROFILE, "messages": [{"role": "user", "content": "Reply with only the word READY."}], "context_length": 32768, "sampling": {}, "keep_alive": "30m"}}
    try:
        async with app.router.lifespan_context(app):
            connection = await connections.create(app.state.store, ConnectionCreate())
            adapter = await app.state.registry.adapter(connection.id)
            async def chat():
                started = time.monotonic()
                text = ""
                async for event in adapter.stream(ChatRequest(PROFILE, [ProviderMessage("user", "Reply with only the word READY.")], {}, 32768)):
                    if isinstance(event, TextDelta): text += event.text
                    if isinstance(event, Finish) and event.reason == "error": raise RuntimeError("Chat failed")
                if text.strip() != "READY": raise RuntimeError("Chat probe failed")
                return {"seconds": time.monotonic() - started, "text": text}
            results["chat_before"] = await chat()
            images = app.state.images
            originals = []
            for stage, seed, cancel_at in [("cancel-initialization",42,"Loading image weights"),("cancel-denoising",42,"Generating image"),("generation",42,None),("version",1337,None)]:
                before = await adapter.json("GET", "/api/ps")
                stream = images.tail(0)
                await anext(stream)
                started = time.monotonic()
                job = await images.submit(ImageCreate(request_key=uuid4().hex,prompt=PROMPT,seed=seed,parent_id=originals[0] if stage=="version" else None))
                results["new_image_calls"] += 1
                cancel_seconds = None
                pending_chat = None
                async with asyncio.timeout(320):
                    while True:
                        _,kind,data = await anext(stream)
                        if kind != "image.updated" or data["job"]["id"] != job.id: continue
                        item = data["job"]
                        if cancel_at and item["stage"] == cancel_at and (cancel_at != "Generating image" or item["completed_steps"] >= 1):
                            cancelling = time.monotonic()
                            await images.cancel(job.id)
                            cancel_seconds = time.monotonic()-cancelling
                            cancel_at = None
                        if stage=="version" and item["stage"] == "Generating image" and pending_chat is None:
                            if not images.capacity.busy: raise RuntimeError("Image does not own capacity")
                            pending_chat = asyncio.create_task(chat())
                            await asyncio.sleep(0)
                            if pending_chat.done(): raise RuntimeError("Native chat was not queued")
                        if item["state"] in {"complete","failed","cancelled","interrupted"}: break
                await stream.aclose()
                task = images.tasks.get(job.id)
                if task: await task
                item = await images.get(job.id)
                row = {"stage":stage,"job":item.model_dump(),"seconds":time.monotonic()-started,"cancel_reap_seconds":cancel_seconds,"models_before":before,"models_after":await adapter.json("GET","/api/ps")}
                if pending_chat: row["queued_chat"] = await pending_chat
                results["stages"].append(row)
                write(stage+".json",row)
                print(json.dumps({"stage":stage,"state":item.state,"seconds":row["seconds"]}),flush=True)
                expected="cancelled" if stage.startswith("cancel-") else "complete"
                if item.state != expected or (cancel_seconds is not None and cancel_seconds > 10): raise RuntimeError("Native stage failed")
                if item.state == "complete":
                    originals.append(job.id)
                    target=EVIDENCE/(stage+"-synthetic")
                    shutil.copytree(images.path(job.id)/"output",target)
                if images.capacity.busy: raise RuntimeError("Capacity not released")
            original=await images.get(originals[0])
            results["original_preserved"] = hashlib.sha256((await images.artifact(original.id,"png")).read_bytes()).hexdigest()==original.sha256
            results["storage"]=(await images.storage()).model_dump()
            results["backup"]=(await app.state.backups.make()).model_dump()
            if results["backup"]["warning"]: raise RuntimeError("Native output backup failed")
            results["chat_after"]=await chat()
            results["passed"] = results["original_preserved"] and results["storage"]["outputs"]==2 and results["storage"]["versions"]==1
    except BaseException as error:
        results["failure_type"]=type(error).__name__
        raise
    finally:
        write("result.json",results)


if __name__=="__main__": asyncio.run(main())
