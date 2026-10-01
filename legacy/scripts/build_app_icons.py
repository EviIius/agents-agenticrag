"""Build the small, high contrast AgenticRAG home-screen mark."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


OUT = Path(__file__).resolve().parents[1] / "src/agenticrag/ui"
SIZE = 1024


def make_icon() -> Image.Image:
    image = Image.new("RGB", (SIZE, SIZE), "#101820")
    pixels = image.load()
    for y in range(SIZE):
        for x in range(SIZE):
            distance = ((x - 510) ** 2 + (y - 530) ** 2) ** 0.5 / 710
            light = max(0, 1 - distance) ** 2
            pixels[x, y] = (
                round(15 + 5 * light), round(22 + 14 * light), round(33 + 25 * light)
            )

    glow = Image.new("RGBA", (SIZE, SIZE))
    pen = ImageDraw.Draw(glow)
    pen.ellipse((215, 220, 820, 830), fill=(43, 110, 255, 64))
    glow = glow.filter(ImageFilter.GaussianBlur(105))
    image = Image.alpha_composite(image.convert("RGBA"), glow)

    pen = ImageDraw.Draw(image)
    # The three dots and connecting arc are a compact evidence network.
    pen.arc((170, 178, 854, 858), 212, 328, fill=(85, 150, 255, 185), width=11)
    for x, y, radius, color in (
        (206, 622, 24, "#4285FF"),
        (781, 622, 24, "#4285FF"),
        (500, 820, 18, "#9CC2FF"),
    ):
        pen.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)

    # A broad geometric A stays legible when iOS reduces the icon to a folder tile.
    pen.line(((326, 710), (506, 294), (688, 710)), fill="#F6F8FB", width=82, joint="curve")
    for x, y in ((326, 710), (506, 294), (688, 710)):
        pen.ellipse((x-41, y-41, x+41, y+41), fill="#F6F8FB")
    pen.line(((403, 570), (608, 570)), fill="#4B8DFF", width=58)
    for x in (403, 608):
        pen.ellipse((x-29, 541, x+29, 599), fill="#4B8DFF")
    return image.convert("RGB")


if __name__ == "__main__":
    icon = make_icon()
    for size in (180, 192, 512):
        icon.resize((size, size), Image.Resampling.LANCZOS).save(
            OUT / f"icon-{size}.png", optimize=True
        )
