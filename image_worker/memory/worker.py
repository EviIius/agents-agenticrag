"""Isolated synthetic trial worker. JSON-line events are emitted after actual work."""

import argparse
import contextlib
import hashlib
import importlib.metadata
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

EVENT_STREAM = sys.stdout
STARTED = time.monotonic()


def emit(kind: str, **fields: object) -> None:
    EVENT_STREAM.write(
        json.dumps({"type": kind, "elapsed_seconds": time.monotonic() - STARTED, **fields}) + "\n"
    )
    EVENT_STREAM.flush()


def atomic_json(path: Path, data: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("x") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True, type=Path)
    parser.add_argument("--requests", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", choices=("generate", "edit"), default="generate")
    args = parser.parse_args()
    spec = json.loads(Path(__file__).with_name("trial.json").read_text())
    requests = json.loads(args.requests.read_text())
    if not isinstance(requests, list) or not requests:
        raise ValueError("At least one request is required")
    known = {case["id"]: case["prompt"] for case in spec["cases"]}
    known[spec["edit"]["id"]] = spec["edit"]["prompt"]
    for request in requests:
        if request.get("case") not in known or request.get("prompt") != known[request["case"]]:
            raise ValueError("Only the frozen synthetic prompts are allowed")
        if request.get("seed") not in spec["seeds"]:
            raise ValueError("Unsupported trial seed")
        if args.mode == "edit" and not Path(request.get("reference", "")).is_file():
            raise ValueError("Missing reference image")
        if args.mode == "generate" and request["case"] == spec["edit"]["id"]:
            raise ValueError("Reference edit requires edit mode")
    if not args.model_path.is_dir():
        raise ValueError("Missing pinned model snapshot")
    args.output.mkdir(parents=True, exist_ok=True)
    emit("imports_start")
    import mlx.core as mx
    from mflux.models.common.config import ModelConfig
    from mflux.models.flux2.variants import Flux2Klein, Flux2KleinEdit
    from mlx import nn
    from mlx.utils import tree_flatten
    from PIL import Image

    if importlib.metadata.version("mflux") != spec["mflux"]:
        raise RuntimeError("MFLUX version differs from the frozen trial")
    config = ModelConfig.flux2_klein_4b()
    if config.model_name != spec["model"] or args.model_path.name != spec["revision"]:
        raise RuntimeError("Model configuration/revision differs from the frozen trial")
    if not mx.metal.is_available():
        raise RuntimeError("Metal is unavailable")
    cache_limit = spec["resource"]["cache_limit_bytes"]
    previous_limit = mx.set_cache_limit(cache_limit)
    emit("cache_policy_set", requested_bytes=cache_limit, previous_bytes=previous_limit)

    def verify_cache_limit() -> int:
        # This API returns the old setting; reapply the SAME declared setting.
        previous = mx.set_cache_limit(cache_limit)
        if previous != cache_limit:
            mx.set_cache_limit(previous)
            raise RuntimeError("The declared unused-allocation cache policy changed")
        return previous

    def chat_presence(job: str, when: str) -> dict:
        started = time.monotonic()
        with urllib.request.urlopen("http://127.0.0.1:11434/api/ps", timeout=5) as response:
            models = json.load(response).get("models", [])
        target = spec["chat_probe"]["model"]
        matching = [
            row for row in models if row.get("name") == target or row.get("model") == target
        ]
        unrelated = [row for row in models if row not in matching]
        snapshot = {
            "target": target,
            "loaded": bool(matching),
            "matching_models": matching,
            "other_loaded_model_count": len(unrelated),
            "lookup_seconds": time.monotonic() - started,
        }
        emit("chat_residency", job=job, when=when, **snapshot)
        if unrelated:
            raise RuntimeError("Another model is loaded; stop without evicting it")
        if not matching:
            raise RuntimeError("Intended chat residency is absent; stop without reloading it")
        return snapshot

    model_class = Flux2KleinEdit if args.mode == "edit" else Flux2Klein
    emit("initialization_start")
    load_started = time.monotonic()
    model = model_class(
        model_config=config, model_path=str(args.model_path), quantize=spec["quantization"]
    )
    # MLX evaluates lazily: include materialization in initialization timing.
    mx.eval(model.parameters())
    mx.synchronize()
    quantized = {}
    for name in ("vae", "transformer", "text_encoder"):
        component = getattr(model, name)
        layers = [
            layer
            for _, layer in tree_flatten(
                component.leaf_modules(), is_leaf=lambda value: isinstance(value, nn.Module)
            )
            if hasattr(layer, "bits")
        ]
        quantized[name] = {
            "layers": len(layers),
            "bits": sorted({layer.bits for layer in layers}),
            "group_sizes": sorted({layer.group_size for layer in layers}),
        }
    if model.bits != spec["quantization"] or any(
        8 not in item["bits"] for item in quantized.values()
    ):
        raise RuntimeError("Requested 8-bit component quantization was not applied")
    verify_cache_limit()
    load_seconds = time.monotonic() - load_started
    emit(
        "initialized",
        load_seconds=load_seconds,
        quantized_components=quantized,
        mlx_active_bytes=mx.get_active_memory(),
        mlx_peak_bytes=mx.get_peak_memory(),
        mlx_cache_bytes=mx.get_cache_memory(),
    )

    class Progress:
        job: str = ""

        def call_before_loop(self, **kwargs: object) -> None:
            mx.synchronize()
            emit("denoising_start", job=self.job, steps=spec["steps"])

        def call_in_loop(self, t: int, latents: object, **kwargs: object) -> None:
            mx.eval(latents)
            mx.synchronize()
            if time.monotonic() - generate_started > spec["resource"]["maximum_generation_seconds"]:
                raise RuntimeError("Generation latency exceeds the frozen resource bound")
            emit(
                "generation_progress",
                job=self.job,
                completed_steps=t + 1,
                steps=spec["steps"],
                mlx_active_bytes=mx.get_active_memory(),
                mlx_peak_bytes=mx.get_peak_memory(),
                mlx_cache_bytes=mx.get_cache_memory(),
                cache_limit_verified_bytes=verify_cache_limit(),
            )

        def call_after_loop(self, **kwargs: object) -> None:
            emit("decode_start", job=self.job)

    progress = Progress()
    model.callbacks.register(progress)
    for index, request in enumerate(requests):
        job = f"{request['case']}-{request['seed']}"
        output = args.output / f"{job}.png"
        metadata = args.output / f"{job}.json"
        if output.exists() or metadata.exists():
            raise ValueError("Refusing to overwrite prior output")
        progress.job = job
        mx.reset_peak_memory()
        presence_before = chat_presence(job, "before")
        verify_cache_limit()
        generate_started = time.monotonic()
        emit("generation_start", job=job, resident_model_reuse=index > 0)
        kwargs = {
            "seed": request["seed"],
            "prompt": request["prompt"],
            "width": spec["width"],
            "height": spec["height"],
            "num_inference_steps": spec["steps"],
            "guidance": spec["guidance"],
        }
        if args.mode == "edit":
            kwargs["image_paths"] = [request["reference"]]
        result = model.generate_image(**kwargs)
        mx.synchronize()
        temporary = output.with_name(output.stem + ".partial.png")
        result.save(temporary)
        if time.monotonic() - generate_started > spec["resource"]["maximum_generation_seconds"]:
            raise RuntimeError("Generation/decode latency exceeds the frozen resource bound")
        with Image.open(temporary) as image:
            image.load()
            if image.format != "PNG" or image.size != (spec["width"], spec["height"]):
                raise RuntimeError("Invalid image output")
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
        details = {
            "job": job,
            "prompt": request["prompt"],
            "model": spec["model"],
            "revision": spec["revision"],
            "mflux": spec["mflux"],
            "seed": request["seed"],
            "width": spec["width"],
            "height": spec["height"],
            "steps": spec["steps"],
            "guidance": spec["guidance"],
            "quantization": model.bits,
            "quantized_components": quantized,
            "compute_precision": str(result.precision),
            "generate_seconds": time.monotonic() - generate_started,
            "initialization_seconds": load_seconds,
            "resident_model_reuse": index > 0,
            "sha256": digest,
            "reference": request.get("reference"),
            "reference_sha256": hashlib.sha256(Path(request["reference"]).read_bytes()).hexdigest()
            if request.get("reference")
            else None,
            "mlx_active_bytes": mx.get_active_memory(),
            "mlx_peak_bytes": mx.get_peak_memory(),
            "mlx_cache_bytes": mx.get_cache_memory(),
            "cache_limit_requested_bytes": cache_limit,
            "cache_limit_verified_bytes": verify_cache_limit(),
            "chat_loaded_before": presence_before["loaded"],
            "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }
        os.replace(temporary, output)
        atomic_json(metadata, details)
        directory = os.open(args.output, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        emit("completed", **details)
        chat_presence(job, "after")
    emit("worker_finished", completed=len(requests))


if __name__ == "__main__":
    try:
        with contextlib.redirect_stdout(sys.stderr):
            main()
    except Exception as error:
        emit("failed", error_type=type(error).__name__, message=str(error))
        raise
