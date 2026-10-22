"""PE3 preparation only: inspect installed source and exercise the CPU processor.

Run with the existing image-worker Python. No model construction, weight reads,
network access, native image invocation, installation or production mutation.
"""

import argparse
import ast
import hashlib
import json
import sys
from importlib import metadata
from pathlib import Path


def boundary(event, args):
    if event == "import" and args[0].split(".")[0] in {"mlx", "mflux"}:
        raise RuntimeError("Model/MLX imports disabled during CPU preflight")
    if event.startswith("socket."):
        raise RuntimeError("Network disabled during CPU preflight")
    if (
        event == "open"
        and isinstance(args[0], str)
        and args[0].endswith((".safetensors", ".pt", ".pth", ".ckpt"))
    ):
        raise RuntimeError("Weight reads disabled during CPU preflight")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Preserve the prior preflight result")
    sys.addaudithook(boundary)
    package = metadata.distribution("mflux")
    if package.version != "0.22.0":
        raise ValueError("Expected the existing pinned MFLUX 0.22.0")
    root = Path(package.locate_file("mflux"))
    edit_path = root / "models/qwen21/variants/edit/qwen_image_21_edit.py"
    source = edit_path.read_text()
    tree = ast.parse(source)
    cls = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "QwenImage21Edit"
    )
    generate = next(
        n
        for n in cls.body
        if isinstance(n, ast.FunctionDef) and n.name == "generate_image"
    )
    params = {n.arg for n in generate.args.args}
    required = {
        "mask_image",
        "auto_mask",
        "strength",
        "enhance_prompt",
        "verify",
        "verify_retries",
        "use_step_cache",
        "use_kv_cache",
        "image_paths",
        "num_inference_steps",
        "scheduler",
        "width",
        "height",
        "guidance",
    }
    if not required <= params:
        raise ValueError("The installed edit API differs from the prepared scope")
    defaults = dict(
        zip(
            [n.arg for n in generate.args.args][-len(generate.args.defaults) :],
            [
                ast.literal_eval(n) if isinstance(n, ast.Constant) else ast.unparse(n)
                for n in generate.args.defaults
            ],
            strict=True,
        )
    )
    for key, value in {
        "auto_mask": None,
        "enhance_prompt": False,
        "verify": False,
        "verify_retries": 0,
    }.items():
        if defaults.get(key) != value:
            raise ValueError("Helper-call default changed")
    markers = (
        "inpaint_mask = self._resolve_mask(mask_image, auto_mask, source, width, height)",
        "latents = (blend_mask * latents + (1 - blend_mask) * noised).astype(latents.dtype)",
        "decoded = keep * decoded.astype(mx.float32) + (1 - keep) * original",
        "if not verify:\n            return image",
    )
    if not all(marker in source for marker in markers):
        raise ValueError(
            "Inspect the changed mask/helper implementation before native use"
        )
    weights_path = root / "models/qwen21/weights/qwen_image21_weight_definition.py"
    weights = ast.parse(weights_path.read_text())
    components = {}
    for n in ast.walk(weights):
        if (
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "ComponentDefinition"
        ):
            values = {k.arg: ast.unparse(k.value) for k in n.keywords}
            components[ast.literal_eval(values["name"])] = values
    if components["vae"].get("skip_quantization") != "True":
        raise ValueError("Inspect the changed VAE quantization rule")
    if any(
        components[n].get("skip_quantization", "False") != "False"
        for n in ("transformer", "text_encoder")
    ):
        raise ValueError("Quantization coverage differs from the proposed trial")

    # This installed PIL backend imports the already-installed torch package.
    # It processes pixels on CPU; no MFLUX, MLX, model or weights are loaded.
    from PIL import Image, ImageChops
    from transformers.models.qwen2_vl.image_processing_pil_qwen2_vl import (
        Qwen2VLImageProcessorPil,
    )

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "product"))
    from masked_edit import composite, context

    processor = Qwen2VLImageProcessorPil.from_pretrained(
        str(args.metadata / "processor"),
        local_files_only=True,
    )
    selection = {"version": 1, "strokes": [{"radius": 0.15, "points": [[0.5, 0.45]]}]}
    cases = []
    for size in ((768, 1024), (1024, 768), (1536, 2048)):
        original = Image.new("RGB", size, (80, 100, 120))
        canvas, mask, box, viewport = context(original, selection)
        model_mask = Image.new("L", canvas.size, 0)
        region = mask.crop(box).resize(
            (viewport[2] - viewport[0], viewport[3] - viewport[1]),
            Image.Resampling.NEAREST,
        )
        model_mask.paste(region, viewport[:2])
        if set(model_mask.tobytes()) != {0, 255}:
            raise ValueError("Explicit generation mask must be black/white")
        data = processor(images=[canvas.convert("RGBA")], return_tensors="np")
        if list(data["pixel_values"].shape) != [4096, 1536] or data[
            "image_grid_thw"
        ].tolist() != [[1, 64, 64]]:
            raise ValueError("Actual CPU processor output differs")
        output, proof = composite(
            original, Image.new("RGB", (1024, 1024), "yellow"), selection
        )
        if (
            proof["outside_changed_pixels"] != 0
            or proof["changed_pixels"] <= 0
            or output.size != size
        ):
            raise ValueError("Final compositor preservation failed")
        if model_mask.crop(viewport).getbbox() != region.getbbox():
            raise ValueError("Model mask context transform differs")
        if ImageChops.difference(canvas, context(original, selection)[0]).getbbox():
            raise ValueError("Context construction is not deterministic")
        cases.append(
            {
                "source_size": list(size),
                "native_size": list(canvas.size),
                "pixel_values_shape": list(data["pixel_values"].shape),
                "image_grid_thw": data["image_grid_thw"].tolist(),
                "explicit_mask_sha256": hashlib.sha256(
                    model_mask.tobytes()
                ).hexdigest(),
                "protected_pixels": proof["protected_pixels"],
                "outside_changed_pixels": proof["outside_changed_pixels"],
            }
        )
    imported = sorted(n for n in sys.modules if n.split(".")[0] in {"mlx", "mflux"})
    if imported:
        raise ValueError("CPU preflight imported a forbidden model module")
    frozen = sorted(
        set(root.rglob("models/qwen21/**/*.py"))
        | {
            root / "models/common/tokenizer/tokenizer_loader.py",
            root / "models/common/weights/loading/weight_applier.py",
            root / "models/common/weights/loading/weight_loader.py",
            root / "models/common/resolution/path_resolution.py",
        }
    )
    result = {
        "passed": True,
        "scope": "CPU/static preflight; not native model qualification",
        "versions": {
            n: metadata.version(n)
            for n in (
                "mflux",
                "mlx",
                "mlx-metal",
                "transformers",
                "torch",
                "Pillow",
                "numpy",
                "huggingface-hub",
                "tokenizers",
                "safetensors",
            )
        },
        "api_parameters": sorted(params),
        "component_definitions": components,
        "helpers_disabled_by_proposed_call": {
            "auto_mask": None,
            "enhance_prompt": False,
            "verify": False,
            "verify_retries": 0,
        },
        "processor_cases": cases,
        "forbidden_model_modules_imported": imported,
        "model_calls": 0,
        "weights_read": False,
        "network_access": False,
        "source_sha256": {str(p.relative_to(root)): sha(p) for p in frozen},
        "metadata_sha256": {
            str(p.relative_to(args.metadata)): sha(p)
            for p in sorted(args.metadata.rglob("*"))
            if p.is_file()
        },
        "preflight_sha256": sha(Path(__file__)),
        "unverified": [
            "checkpoint weight compatibility",
            "native quantization/peak memory",
            "generation latency",
            "accessory quality",
            "chat coexistence",
        ],
    }
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(
        json.dumps(
            {
                k: result[k]
                for k in ("passed", "scope", "versions", "model_calls", "unverified")
            }
        )
    )


if __name__ == "__main__":
    main()
