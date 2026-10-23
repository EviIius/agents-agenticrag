"""Private mask partition and independent RGB audit. No model imports/network."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "image_worker/product"))
from masked_edit import context, raster, read_rgb
from PIL import Image, ImageChops, ImageDraw

PARTS = ("hat", "front", "rear")


def no_native(event, args):
    if event == "import" and args[0].split(".")[0] in {
        "mlx",
        "mflux",
        "torch",
        "transformers",
    }:
        raise RuntimeError("Native imports forbidden in CPU analysis")
    if event.startswith("socket."):
        raise RuntimeError("Network forbidden in CPU analysis")


sys.addaudithook(no_native)


def delta(a, b):
    r, g, b = ImageChops.difference(a, b).split()
    return ImageChops.lighter(ImageChops.lighter(r, g), b).point(
        lambda value: 255 if value else 0
    )


def partition(selection, regions, size):
    targets = regions["target_regions"]
    groups = {
        "hat": (targets["crown hair"], targets["side hair"]),
        "front": (targets["front hand"],),
        "rear": (targets["rear hand"],),
    }
    centers = {
        part: [
            ((b[0] + b[2]) / 2 / size[0], (b[1] + b[3]) / 2 / size[1]) for b in boxes
        ]
        for part, boxes in groups.items()
    }
    assignments = {}
    for i, stroke in enumerate(selection["strokes"]):
        if stroke.get("operation") == "erase":
            continue
        x = sum(p[0] for p in stroke["points"]) / len(stroke["points"])
        y = sum(p[1] for p in stroke["points"]) / len(stroke["points"])
        assignments[i] = min(
            PARTS,
            key=lambda part: min(
                (x - cx) ** 2 + (y - cy) ** 2 for cx, cy in centers[part]
            ),
        )
    result, earlier = {}, []
    for part in PARTS:
        strokes = [
            s
            for i, s in enumerate(selection["strokes"])
            if s.get("operation") == "erase" or assignments[i] == part
        ]
        # Higher-priority painted strokes own any overlap. Original erasures
        # remain ordered; the union is checked against the original raster below.
        strokes += [{**s, "operation": "erase"} for s in earlier]
        result[part] = {"version": 1, "strokes": strokes}
        earlier += [
            s
            for i, s in enumerate(selection["strokes"])
            if s.get("operation") != "erase" and assignments[i] == part
        ]
    masks = {part: raster(size, result[part]) for part in PARTS}
    union = Image.new("L", size, 0)
    for mask in masks.values():
        assert ImageChops.multiply(union, mask).getbbox() is None, "Regions overlap"
        union = ImageChops.lighter(union, mask)
    assert ImageChops.difference(union, raster(size, selection)).getbbox() is None
    return result, masks, union


def prepare(root):
    baseline = root / "baseline"
    request = json.loads((baseline / "input.json").read_text())
    regions = json.loads((baseline / "regions.json").read_text())
    source = read_rgb(baseline / "reference.png")
    selections, _masks, union = partition(request["selection"], regions, source.size)
    face = Image.new("L", source.size, 0)
    ImageDraw.Draw(face).polygon([tuple(p) for p in regions["face_polygon"]], fill=255)
    assert ImageChops.multiply(union, face).getbbox() is None
    face.save(root / "face.png")
    union.save(root / "union.png")
    prompts = json.loads((baseline / "region-instructions.json").read_text())
    assert set(prompts) == set(PARTS)
    assert all(
        isinstance(p, str) and 0 < len(p.strip()) <= 4000 for p in prompts.values()
    )
    observations = {}
    for part in PARTS:
        signatures = []
        for engine in ("flux", "qwen"):
            job = root / part / engine
            current = {
                **request,
                "prompt": prompts[part],
                "selection": selections[part],
            }
            with (job / "input.json").open("x") as stream:
                json.dump(current, stream, indent=2)
                stream.write("\n")
            canvas, mask, box, viewport = context(source, current["selection"])
            canvas.save(job / "cpu-context.png")
            mask.save(job / "cpu-mask.png")
            signatures.append(
                {
                    "request_sha256": hashlib.sha256(
                        (job / "input.json").read_bytes()
                    ).hexdigest(),
                    "context_sha256": hashlib.sha256(canvas.tobytes()).hexdigest(),
                    "mask_sha256": hashlib.sha256(mask.tobytes()).hexdigest(),
                    "box": box,
                    "viewport": viewport,
                    "selected_pixels": mask.histogram()[255],
                }
            )
        assert signatures[0] == signatures[1]
        observations[part] = signatures[0]
    proof = {
        "identical_pairs": True,
        "disjoint_regions": True,
        "union_equals_previous_mask": True,
        "selected_pixels": union.histogram()[255],
        "manual_face_pixels": face.histogram()[255],
        "manual_face_selected_pixels": 0,
        "regions": observations,
        "native_calls": 0,
    }
    (root / "cpu-preflight.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps({k: v for k, v in proof.items() if k != "regions"}))


def finish(root):
    source = read_rgb(root / "baseline/reference.png")
    union = Image.open(root / "union.png").convert("L")
    face = Image.open(root / "face.png").convert("L")
    records = {}
    for engine in ("flux", "qwen"):
        combined = source.copy()
        parts = {}
        for part in PARTS:
            job = root / part / engine
            output = read_rgb(job / "working/image.png", source.size)
            export = read_rgb(job / "working/export.png", source.size)
            mask = Image.open(job / "cpu-mask.png").convert("L")
            changes = delta(source, output)
            assert (
                ImageChops.multiply(changes, ImageChops.invert(mask)).getbbox() is None
            )
            assert ImageChops.multiply(changes, face).getbbox() is None
            assert delta(output, export).getbbox() is None
            combined.paste(output, (0, 0), mask)
            parts[part] = {
                "outside_changed_pixels": 0,
                "manual_face_changed_pixels": 0,
                "export_pixels_equal_composite": True,
            }
        changes = delta(source, combined)
        assert ImageChops.multiply(changes, ImageChops.invert(union)).getbbox() is None
        assert ImageChops.multiply(changes, face).getbbox() is None
        combined.save(root / f"{engine}-combined.png")
        records[engine] = {
            "parts": parts,
            "outside_changed_pixels": 0,
            "manual_face_changed_pixels": 0,
            "protected_pixels": union.histogram()[0],
            "combined_png_bytes": (root / f"{engine}-combined.png").stat().st_size,
        }
    (root / "pixel-audit.json").write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps({"passed": True, "native_calls": 0, "engines": records}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "finish"))
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "finish":
        expected = json.loads((args.root / "scope.json").read_text())["files"][
            "scope-source/cpu.py"
        ]
        assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == expected
    {"prepare": prepare, "finish": finish}[args.action](args.root)
