"""One isolated, explicitly masked Qwen edit. Never installed as the live worker."""

import contextlib
import importlib.metadata
import json
import os
import sys
import threading
from pathlib import Path
from time import monotonic

OUT = sys.stdout
START = monotonic()
HERE = Path(__file__).resolve().parent


def emit(kind, **fields):
    OUT.write(json.dumps({"type": kind, **fields}) + "\n")
    OUT.flush()


def parent_watch():
    os.read(sys.stdin.fileno(), 1)
    os._exit(71)


def no_network(event, args):
    if event.startswith("socket."):
        raise RuntimeError("Network forbidden in the isolated image worker")


def no_helper(*args, **kwargs):
    raise RuntimeError("Auxiliary generation is forbidden")


def main():
    threading.Thread(target=parent_watch, daemon=True).start()
    sys.addaudithook(no_network)
    from masked_edit import composite, context, read_rgb
    from PIL import Image
    from reference_contract import digest, load_request, validate_reference

    request_path, snapshot, output = map(Path, sys.argv[1:])
    spec = json.loads((HERE / "trial.json").read_text())
    settings, limits = spec["parameters"], spec["limits"]
    if snapshot.name != spec["revision"] or not snapshot.is_dir():
        raise ValueError("Pinned checkpoint missing")
    request, reference = load_request(request_path, output)
    if not request.get("selection"):
        raise ValueError("Explicit mask required")
    source = read_rgb(reference)
    canvas, mask, box, viewport = context(source, request["selection"])
    selected = Image.new("L", canvas.size, 0)
    region = mask.crop(box).resize(
        (viewport[2] - viewport[0], viewport[3] - viewport[1]),
        Image.Resampling.NEAREST,
    )
    selected.paste(region, viewport[:2])
    canvas.save(output / "context.png", format="PNG")
    selected.save(output / "mask.png", format="PNG")
    emit("initializing")
    import mlx.core as mx
    from mflux.models.qwen21.variants.edit.qwen_image_21_edit import QwenImage21Edit
    from mlx import nn
    from mlx.utils import tree_flatten

    if importlib.metadata.version("mflux") != "0.22.0" or not mx.metal.is_available():
        raise ValueError("The existing pinned engine/Metal is required")
    mx.set_memory_limit(limits["mlx_peak_bytes"])
    mx.set_cache_limit(limits["mlx_cache_bytes"])

    def resource_check():
        mx.synchronize()
        if mx.get_peak_memory() > limits["mlx_peak_bytes"]:
            raise RuntimeError("MLX allocation bound exceeded")
        if mx.set_cache_limit(limits["mlx_cache_bytes"]) != limits["mlx_cache_bytes"]:
            raise RuntimeError("Cache policy changed")
        if mx.set_memory_limit(limits["mlx_peak_bytes"]) != limits["mlx_peak_bytes"]:
            raise RuntimeError("Allocation policy changed")

    # Disable all language-generating helpers even if a library path calls one.
    QwenImage21Edit._vision_reply = no_helper
    QwenImage21Edit._rewrite_prompt = no_helper
    QwenImage21Edit.rewrite_prompt = no_helper
    QwenImage21Edit._verify_output = no_helper
    model = QwenImage21Edit(model_path=str(snapshot), quantize=settings["quantize"])
    coverage = {}
    for name in ("transformer", "text_encoder", "vae"):
        layers = [
            layer
            for _, layer in tree_flatten(
                getattr(model, name).leaf_modules(),
                is_leaf=lambda value: isinstance(value, nn.Module),
            )
            if hasattr(layer, "bits")
        ]
        bits = sorted({layer.bits for layer in layers})
        if name == "vae":
            if layers:
                raise ValueError("Decoder should remain unquantized")
        elif not layers or bits != [settings["quantize"]]:
            raise ValueError("Requested quantization unavailable")
        coverage[name] = {"quantized_layers": len(layers), "bits": bits}
    resource_check()
    initialization = monotonic() - START
    if initialization > limits["initialization_seconds"]:
        raise RuntimeError("Initialization exceeded trial allowance")
    emit(
        "initialized",
        initialization_seconds=round(initialization, 3),
        quantization=coverage,
    )
    generate_started = monotonic()

    def generation_check():
        resource_check()
        if monotonic() - generate_started > limits["generation_decode_seconds"]:
            raise RuntimeError("Generation/decode exceeded trial allowance")

    class Progress:
        def call_before_loop(self, **kwargs):
            generation_check()
            emit("denoising", completed_steps=0, mlx_peak_bytes=mx.get_peak_memory())

        def call_in_loop(self, t, latents, **kwargs):
            mx.eval(latents)
            generation_check()
            emit(
                "denoising", completed_steps=t + 1, mlx_peak_bytes=mx.get_peak_memory()
            )

        def call_after_loop(self, **kwargs):
            generation_check()
            emit("decoding", mlx_peak_bytes=mx.get_peak_memory())

    model.callbacks.register(Progress())
    result = model.generate_image(
        seed=request["seed"],
        prompt=request["prompt"],
        width=settings["width"],
        height=settings["height"],
        output_resolution=settings["output_resolution"],
        num_inference_steps=settings["num_inference_steps"],
        guidance=settings["guidance"],
        strength=settings["strength"],
        image_paths=[canvas],
        mask_image=selected,
        negative_prompt=None,
        auto_mask=None,
        enhance_prompt=False,
        verify=False,
        verify_retries=0,
        use_kv_cache=True,
        use_step_cache=False,
        scheduler="linear",
    )
    generation_check()
    result.save(output / "native.png")
    native = read_rgb(output / "native.png", (1024, 1024))
    image, proof = composite(source, native, request["selection"])
    image.save(output / "image.png", format="PNG")
    generation_check()
    validate_reference(request_path.parent / "inputs", request["reference"])
    details = {
        "mode": "edit",
        "model": spec["model"],
        "revision": spec["revision"],
        "mflux": "0.22.0",
        "reference": request["reference"],
        "selection": request["selection"],
        "prompt": request["prompt"],
        "seed": request["seed"],
        "parameters": settings,
        "width": source.width,
        "height": source.height,
        "quantization": coverage,
        "initialization_seconds": initialization,
        "generate_seconds": monotonic() - generate_started,
        "mlx_peak_bytes": mx.get_peak_memory(),
        "mlx_cache_bytes": mx.get_cache_memory(),
        "composition": proof,
        "native_sha256": digest(output / "native.png"),
        "native_bytes": (output / "native.png").stat().st_size,
        "sha256": digest(output / "image.png"),
        "generation_mask_sha256": digest(output / "mask.png"),
        "worker_sha256": digest(Path(__file__)),
        "auxiliary_model_calls": 0,
    }
    with (output / "metadata.json").open("x") as stream:
        json.dump(details, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    for name in ("native.png", "image.png"):
        with (output / name).open("rb") as stream:
            os.fsync(stream.fileno())
    emit("finished")


if __name__ == "__main__":
    try:
        with contextlib.redirect_stdout(sys.stderr):
            main()
    except Exception:  # noqa: BLE001 — private native errors never reach public logs
        emit("failed")
        sys.exit(1)
