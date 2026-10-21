"""Isolated PE0 worker. Explicit pixel references; production worker is unchanged."""

import contextlib
import hashlib
import importlib.metadata
import json
import os
import sys
import threading
import time
from pathlib import Path

from contracts import digest, load_request, validate_reference

OUT = sys.stdout
START = time.monotonic()
MODEL = "black-forest-labs/FLUX.2-klein-4B"
REVISION = "e7b7dc27f91deacad38e78976d1f2b499d76a294"


def emit(kind, **fields):
    OUT.write(json.dumps({"type": kind, **fields}) + "\n")
    OUT.flush()


def parent_watch():
    # The server owns the only write end. Abrupt server death closes it; the
    # worker exits even while Python's main thread is inside native Metal work.
    os.read(sys.stdin.fileno(), 1)
    os._exit(71)


def main():
    threading.Thread(target=parent_watch, daemon=True).start()
    request_path, model_path, output = map(Path, sys.argv[1:])
    request, reference = load_request(request_path, output)
    if model_path.name != REVISION or not model_path.is_dir():
        raise ValueError("Pinned model snapshot missing")
    emit("initializing")
    import mlx.core as mx
    from mflux.models.common.config import ModelConfig
    from mflux.models.flux2.variants import Flux2Klein, Flux2KleinEdit
    from mlx import nn
    from mlx.utils import tree_flatten
    from PIL import Image

    if importlib.metadata.version("mflux") != "0.22.0" or not mx.metal.is_available():
        raise ValueError("Unqualified engine or Metal unavailable")
    mx.set_cache_limit(1073741824)
    config = ModelConfig.flux2_klein_4b()
    if config.model_name != MODEL:
        raise ValueError("Unqualified model configuration")
    model_class = Flux2KleinEdit if reference is not None else Flux2Klein
    model = model_class(model_config=config, model_path=str(model_path), quantize=8)
    mx.eval(model.parameters())
    mx.synchronize()
    for name in ("vae", "transformer", "text_encoder"):
        layers = [
            layer
            for _, layer in tree_flatten(
                getattr(model, name).leaf_modules(),
                is_leaf=lambda value: isinstance(value, nn.Module),
            )
            if hasattr(layer, "bits")
        ]
        if not layers or any(layer.bits != 8 for layer in layers):
            raise ValueError("Requested component quantization unavailable")
    initialized = time.monotonic() - START
    generate_started = time.monotonic()

    class Progress:
        def call_before_loop(self, **kwargs):
            emit("denoising", completed_steps=0)

        def call_in_loop(self, t, latents, **kwargs):
            mx.eval(latents)
            mx.synchronize()
            if time.monotonic() - generate_started > 60:
                raise RuntimeError("Generation exceeded qualified latency bound")
            if mx.get_peak_memory() > 24 * 1024**3:
                raise RuntimeError("Generation exceeded allocation safety margin")
            if mx.set_cache_limit(1073741824) != 1073741824:
                raise RuntimeError("Cache policy changed")
            emit("denoising", completed_steps=t + 1)

        def call_after_loop(self, **kwargs):
            emit("decoding")

    model.callbacks.register(Progress())
    arguments = dict(
        seed=request["seed"],
        prompt=request["prompt"],
        width=1024,
        height=1024,
        num_inference_steps=4,
        guidance=1.0,
    )
    if reference is not None:
        validate_reference(request_path.parent, request["reference"])
        arguments["image_paths"] = [str(reference)]
    result = model.generate_image(**arguments)
    mx.synchronize()
    result.save(output / ".image.partial.png")
    if time.monotonic() - generate_started > 60:
        raise RuntimeError("Generation/decode exceeded qualified latency bound")
    with Image.open(output / ".image.partial.png") as image:
        image.load()
        if image.format != "PNG" or image.size != (1024, 1024):
            raise ValueError("Invalid output")
    if mx.get_peak_memory() > 24 * 1024**3 or mx.set_cache_limit(1073741824) != 1073741824:
        raise RuntimeError("Decode exceeded unchanged resource bounds")
    if reference is not None:
        validate_reference(request_path.parent, request["reference"])
    details = {
        "mode": request["mode"],
        "reference": request.get("reference"),
        "prompt": request["prompt"],
        "requested_seed": request["seed"],
        "seed": request["seed"],
        "model": MODEL,
        "revision": REVISION,
        "mflux": "0.22.0",
        "width": 1024,
        "height": 1024,
        "steps": 4,
        "guidance": 1.0,
        "quantization": 8,
        "cache_limit_bytes": 1073741824,
        "initialization_seconds": initialized,
        "generate_seconds": time.monotonic() - generate_started,
        "mlx_peak_bytes": mx.get_peak_memory(),
        "mlx_cache_bytes": mx.get_cache_memory(),
        "sha256": digest(output / ".image.partial.png"),
        "worker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    with (output / ".metadata.partial.json").open("x") as stream:
        json.dump(details, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    with (output / ".image.partial.png").open("rb") as stream:
        os.fsync(stream.fileno())
    os.replace(output / ".image.partial.png", output / "image.png")
    os.replace(output / ".metadata.partial.json", output / "metadata.json")
    fd = os.open(output, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    emit("finished")


if __name__ == "__main__":
    try:
        with contextlib.redirect_stdout(sys.stderr):
            main()
    except Exception:
        # Never send native errors, user prompts or private paths to service logs.
        emit("failed")
        sys.exit(1)
