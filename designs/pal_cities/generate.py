"""
SVG rendered at 454 DPI (A3 portrait).
Black and white variants.
Canvas: ~4496×7496 px at 454 DPI (proportional to SVG aspect ratio at A3 height).

Requires: cairosvg
"""

import os, sys
import numpy as np
import cairosvg
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from shared.common import save_tiff, make_preview, measure_motif

ASSETS       = os.path.join(os.path.dirname(__file__), "../../assets")
SVG_SRC      = os.path.join(os.path.dirname(__file__), "source", "sourceImage.svg")
PNG_DIR      = os.path.join(os.path.dirname(__file__), "out", "png")
PREVIEWS_DIR = os.path.join(os.path.dirname(__file__), "previews")
os.makedirs(PNG_DIR,      exist_ok=True)
os.makedirs(PREVIEWS_DIR, exist_ok=True)

DPI = 454

# SVG viewBox: 1700.79 × 2834.65 → aspect ratio 0.5998
# At 454 DPI, A3 height = 420mm = 7496px → width = 4496px
TARGET_H_PX = int(420 / 25.4 * DPI)
SCALE       = TARGET_H_PX / 2834.65
TARGET_W_PX = int(1700.79 * SCALE)


def render_svg() -> Image.Image:
    """Render SVG to RGBA at target size."""
    tmp_png = os.path.join(PNG_DIR, "_tmp_render.png")
    cairosvg.svg2png(
        url=SVG_SRC,
        write_to=tmp_png,
        output_width=TARGET_W_PX,
        output_height=TARGET_H_PX,
    )
    img = Image.open(tmp_png).convert("RGBA")
    os.remove(tmp_png)
    print(f"Rendered SVG: {img.size[0]}×{img.size[1]} px at {DPI} DPI")
    return img


def to_black(img: Image.Image) -> Image.Image:
    """Convert any ink to pure black, preserve alpha."""
    _, _, _, a = img.split()
    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(Image.new("RGBA", img.size, (0, 0, 0, 255)), mask=a)
    return result


def to_white(img: Image.Image) -> Image.Image:
    """Convert any ink to pure white, preserve alpha."""
    _, _, _, a = img.split()
    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(Image.new("RGBA", img.size, (255, 255, 255, 255)), mask=a)
    return result


if __name__ == "__main__":
    raw = render_svg()

    black_img = to_black(raw)
    white_img = to_white(raw)

    black_png = os.path.join(PNG_DIR, "pal_cities_black.png")
    white_png = os.path.join(PNG_DIR, "pal_cities_white.png")
    save_tiff(black_img, black_png, DPI)
    save_tiff(white_img, white_png, DPI)

    w_mm, h_mm = measure_motif(black_img, DPI)
    print(f"Motif: {w_mm:.0f} × {h_mm:.0f} mm at {DPI} DPI")

    make_preview(
        black_png,
        os.path.join(PREVIEWS_DIR, "preview_pal_cities_black_on_white.jpg"),
        shirt_name="white_tshirt_front.jpg",
        cx=0.5, cy=0.22,
        logo_frac=0.25,
    )
    make_preview(
        white_png,
        os.path.join(PREVIEWS_DIR, "preview_pal_cities_white_on_black.jpg"),
        shirt_name="black_tshirt_front.jpg",
        cx=0.5, cy=0.22,
        logo_frac=0.25,
    )
