"""Post-run independent pixel audit; no compositing/model implementation imports."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


def changed(a, b):
    difference = ImageChops.difference(a, b)
    red, green, blue = difference.split()
    return ImageChops.lighter(ImageChops.lighter(red, green), blue).point(
        lambda n: 255 if n else 0
    )


def read(path):
    with Image.open(path) as source:
        source.load()
        return source.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = {}
    for case in ("flux", "qwen"):
        job = args.root / case
        source = read(job / "inputs/reference.png")
        output = read(job / "working/image.png")
        export = read(job / "working/export.png")
        assert source.size == output.size == export.size
        with Image.open(job / "cpu-mask.png") as raw:
            mask = raw.convert("L")
        assert mask.size == source.size
        histogram = mask.histogram()
        assert histogram[0] + histogram[255] == source.width * source.height
        delta = changed(source, output)
        outside = ImageChops.multiply(delta, ImageChops.invert(mask))
        face = Image.new("L", source.size, 0)
        points = json.loads((args.root / "regions.json").read_text())["face_polygon"]
        ImageDraw.Draw(face).polygon([tuple(p) for p in points], fill=255)
        face_delta = ImageChops.multiply(delta, face)
        assert ImageChops.multiply(mask, face).getbbox() is None
        assert outside.getbbox() is None and face_delta.getbbox() is None
        assert changed(output, export).getbbox() is None
        records[case] = {
            "protected_pixels": histogram[0],
            "outside_changed_pixels": outside.histogram()[255],
            "manual_face_pixels": face.histogram()[255],
            "manual_face_changed_pixels": face_delta.histogram()[255],
            "export_pixels_equal_composite": True,
            "dimensions": list(output.size),
        }
    result = {
        "passed": True,
        "scope": "Post-generation direct RGB differences using frozen CPU masks; independent of compositor code",
        "analysis_source_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "native_calls": 0,
        "cases": records,
    }
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
