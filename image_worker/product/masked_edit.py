"""CPU-only brush rasterization, context fitting and exact protected-pixel compositing."""

import hashlib
import math

from reference_contract import digest, owned, read_json, validate_reference


def selection_valid(value):
    if not isinstance(value, dict) or set(value) != {"version", "strokes"} or value["version"] != 1:
        raise ValueError("Invalid selection version")
    strokes = value["strokes"]
    if not isinstance(strokes, list) or not 1 <= len(strokes) <= 32:
        raise ValueError("Invalid brush strokes")
    total = 0
    for stroke in strokes:
        if not isinstance(stroke, dict) or set(stroke) != {"radius", "points"}:
            raise ValueError("Invalid stroke")
        radius, points = stroke["radius"], stroke["points"]
        if (
            type(radius) not in (int, float)
            or not math.isfinite(radius)
            or not 0.005 <= radius <= 0.25
        ):
            raise ValueError("Invalid brush size")
        if not isinstance(points, list) or not 1 <= len(points) <= 128:
            raise ValueError("Invalid stroke points")
        total += len(points)
        for point in points:
            if (
                not isinstance(point, list)
                or len(point) != 2
                or any(
                    type(n) not in (int, float) or not math.isfinite(n) or not 0 <= n <= 1
                    for n in point
                )
            ):
                raise ValueError("Invalid selection coordinates")
    if total > 512:
        raise ValueError("Selection is too detailed")
    return value


def raster(size, selection):
    from PIL import Image, ImageDraw

    selection_valid(selection)
    width, height = size
    if not 1 <= min(size) <= max(size) <= 2048:
        raise ValueError("Invalid reference size")
    mask = Image.new("L", size, 0)
    drawing = ImageDraw.Draw(mask)
    for stroke in selection["strokes"]:
        radius = max(1, round(stroke["radius"] * min(size)))
        points = [(round(x * (width - 1)), round(y * (height - 1))) for x, y in stroke["points"]]
        if len(points) > 1:
            drawing.line(points, fill=255, width=2 * radius + 1, joint="curve")
        for x, y in points:
            drawing.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)
    if mask.getbbox() is None:
        raise ValueError("Empty selection")
    return mask


def context(source, selection):
    from PIL import Image

    mask = raster(source.size, selection)
    left, top, right, bottom = mask.getbbox()
    margin = max(16, round(max(right - left, bottom - top) * 0.2))
    box = (
        max(0, left - margin),
        max(0, top - margin),
        min(source.width, right + margin),
        min(source.height, bottom + margin),
    )
    crop = source.crop(box)
    scale = min(1024 / crop.width, 1024 / crop.height)
    size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
    offset = ((1024 - size[0]) // 2, (1024 - size[1]) // 2)
    canvas = Image.new("RGB", (1024, 1024), (127, 127, 127))
    canvas.paste(crop.resize(size, Image.Resampling.LANCZOS), offset)
    viewport = (*offset, offset[0] + size[0], offset[1] + size[1])
    return canvas, mask, box, viewport


def composite(source, generated, selection):
    from PIL import Image, ImageChops, ImageFilter

    if generated.size != (1024, 1024):
        raise ValueError("Invalid native dimensions")
    _, mask, box, viewport = context(source, selection)
    patch = (
        generated.convert("RGB")
        .crop(viewport)
        .resize((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
    )
    candidate = source.copy()
    candidate.paste(patch, box[:2])
    # Blending is contained INSIDE the hard mask. No blur leaks onto protected pixels.
    alpha = ImageChops.multiply(mask.filter(ImageFilter.GaussianBlur(3)), mask)
    result = Image.composite(candidate, source, alpha)
    protected = ImageChops.invert(mask)
    channels = ImageChops.difference(source, result).split()
    changed = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    changed = changed.point(lambda n: 255 if n else 0)
    if ImageChops.multiply(changed, protected).getbbox():
        raise ValueError("Protected pixels changed")
    preserved = Image.composite(source, Image.new("RGB", source.size), protected)
    return result, {
        "version": 1,
        "reference_dimensions": list(source.size),
        "context_box": list(box),
        "native_viewport": list(viewport),
        "mask_sha256": hashlib.sha256(mask.tobytes()).hexdigest(),
        "protected_sha256": hashlib.sha256(preserved.tobytes()).hexdigest(),
        "protected_pixels": mask.histogram()[0],
        "outside_changed_pixels": 0,
        "changed_pixels": changed.histogram()[255],
        "feather": "3px Gaussian contained inside selection",
    }


def read_rgb(path, size=None):
    from PIL import Image

    if path.is_symlink() or not 0 < path.stat().st_size <= 32 * 1024**2:
        raise ValueError("Invalid image input")
    with Image.open(path) as image:
        if image.format != "PNG" or not 1 <= min(image.size) <= max(image.size) <= 2048:
            raise ValueError("Invalid image dimensions")
        if size is not None and image.size != size:
            raise ValueError("Image dimensions changed")
        image.load()
        return image.convert("RGB")


def verify_composite(root):
    from PIL import ImageChops

    request = read_json(owned(root, "input.json"))
    if request.get("mode") != "edit" or not request.get("selection"):
        raise ValueError("Explicit selected edit required")
    reference = validate_reference(owned(root, "inputs"), request["reference"])
    source = read_rgb(reference)
    native = owned(root, "working/native.png")
    output = read_rgb(owned(root, "working/image.png"), source.size)
    expected, proof = composite(source, read_rgb(native, (1024, 1024)), request["selection"])
    if ImageChops.difference(expected, output).getbbox():
        raise ValueError("Composite pixels do not match the admitted selection")
    metadata = read_json(owned(root, "working/metadata.json"))
    if metadata.get("composition") != proof or metadata.get("native_sha256") != digest(native):
        raise ValueError("Composite provenance changed")
    return proof
