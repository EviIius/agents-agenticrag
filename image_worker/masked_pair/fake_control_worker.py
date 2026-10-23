"""Finite CPU-only child used to test the actual pair controller."""

import json
import sys
from pathlib import Path


def audit(event, args):
    if event == "import" and args[0].split(".")[0] in {
        "mlx",
        "mflux",
        "torch",
        "transformers",
    }:
        raise RuntimeError("Native imports forbidden in this CPU fixture")
    if event.startswith("socket."):
        raise RuntimeError("Network forbidden")


sys.addaudithook(audit)
from masked_edit import composite, read_rgb
from PIL import Image
from reference_contract import digest, load_request

here = Path(__file__).resolve().parent
case = "flux" if Path(__file__).name.startswith("flux") else "qwen"
spec = json.loads((here / "pair.json").read_text())["engines"][case]
request_path, _snapshot, output = map(Path, sys.argv[1:])
request, reference = load_request(request_path, output)
source = read_rgb(reference)
native = Image.new("RGB", (1024, 1024), "yellow")
native.save(output / "native.png")
image, proof = composite(source, native, request["selection"])
image.save(output / "image.png")
metadata = {
    **request,
    "model": spec["model"],
    "revision": spec["revision"],
    "parameters": spec["parameters"],
    "initialization_seconds": 0.01,
    "generate_seconds": 0.01,
    "mlx_peak_bytes": 1,
    "quantization": {"bits": spec["parameters"]["quantize"]},
    "auxiliary_model_calls": 0,
    "sha256": digest(output / "image.png"),
    "worker_sha256": digest(Path(__file__)),
    "native_bytes": (output / "native.png").stat().st_size,
    "native_sha256": digest(output / "native.png"),
    "width": source.width,
    "height": source.height,
    "composition": proof,
}
(output / "metadata.json").write_text(json.dumps(metadata))
for event in (
    [{"type": "initializing"}, {"type": "initialized"}]
    + [{"type": "denoising", "completed_steps": n} for n in range(spec["steps"] + 1)]
    + [{"type": "decoding"}, {"type": "finished"}]
):
    print(json.dumps(event), flush=True)
