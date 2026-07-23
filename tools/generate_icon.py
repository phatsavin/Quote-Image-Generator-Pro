from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PNG_PATH = ASSETS / "QuoteImageGeneratorPro.png"
ICO_PATH = ASSETS / "QuoteImageGeneratorPro.ico"
SIZE = 1024


def vertical_gradient(
    size: tuple[int, int],
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(
            round(top[index] * (1 - ratio) + bottom[index] * ratio)
            for index in range(3)
        )
        draw.line((0, y, width, y), fill=color)
    return image


def draw_quote_mark(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    color: tuple[int, int, int, int],
) -> None:
    center_x, center_y = center
    draw.ellipse(
        (center_x - 78, center_y - 62, center_x + 78, center_y + 94),
        fill=color,
    )
    draw.polygon(
        (
            (center_x - 58, center_y - 15),
            (center_x - 30, center_y - 135),
            (center_x + 38, center_y - 148),
            (center_x + 4, center_y - 22),
        ),
        fill=color,
    )


def build_icon() -> Image.Image:
    base = vertical_gradient((SIZE, SIZE), (25, 64, 101), (3, 10, 18)).convert(
        "RGBA"
    )
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (28, 28, SIZE - 28, SIZE - 28),
        radius=220,
        fill=255,
    )
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    canvas.paste(base, (0, 0), mask)

    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        (510, -170, 1120, 440),
        fill=(232, 187, 93, 58),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    canvas = Image.alpha_composite(canvas, glow)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (54, 54, SIZE - 54, SIZE - 54),
        radius=195,
        outline=(224, 181, 92, 255),
        width=16,
    )

    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (154, 190, 870, 862),
        radius=86,
        fill=(0, 0, 0, 150),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    canvas = Image.alpha_composite(canvas, shadow)
    draw = ImageDraw.Draw(canvas)

    photo = vertical_gradient((700, 646), (70, 116, 153), (12, 31, 49)).convert(
        "RGBA"
    )
    photo_mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(photo_mask).rounded_rectangle(
        (0, 0, photo.width - 1, photo.height - 1),
        radius=75,
        fill=255,
    )
    canvas.paste(photo, (162, 176), photo_mask)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (162, 176, 862, 822),
        radius=75,
        outline=(239, 209, 137, 155),
        width=10,
    )
    draw.ellipse((652, 244, 790, 382), fill=(245, 208, 120, 235))
    draw.polygon(
        (
            (168, 650),
            (360, 434),
            (485, 558),
            (602, 448),
            (856, 690),
            (856, 816),
            (168, 816),
        ),
        fill=(9, 25, 40, 235),
    )
    draw.polygon(
        (
            (168, 700),
            (342, 565),
            (454, 658),
            (548, 592),
            (856, 772),
            (856, 816),
            (168, 816),
        ),
        fill=(4, 16, 27, 255),
    )

    quote_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    quote_shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(quote_shadow)
    draw_quote_mark(shadow_draw, (380, 425), (0, 0, 0, 170))
    draw_quote_mark(shadow_draw, (646, 425), (0, 0, 0, 170))
    quote_shadow = quote_shadow.filter(ImageFilter.GaussianBlur(24))
    quote_layer = Image.alpha_composite(quote_layer, quote_shadow)
    quote_draw = ImageDraw.Draw(quote_layer)
    draw_quote_mark(quote_draw, (365, 402), (225, 178, 83, 255))
    draw_quote_mark(quote_draw, (631, 402), (244, 211, 139, 255))
    canvas = Image.alpha_composite(canvas, quote_layer)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (278, 642, 746, 670),
        radius=14,
        fill=(255, 255, 255, 240),
    )
    draw.rounded_rectangle(
        (336, 702, 688, 726),
        radius=12,
        fill=(255, 255, 255, 195),
    )
    draw.rounded_rectangle(
        (405, 756, 619, 778),
        radius=11,
        fill=(231, 192, 105, 225),
    )
    return canvas


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    icon = build_icon()
    icon.resize((512, 512), Image.Resampling.LANCZOS).save(PNG_PATH)
    icon.save(
        ICO_PATH,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


if __name__ == "__main__":
    main()
