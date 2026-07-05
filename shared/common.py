"""
Shared helpers for all siebdruck design scripts.

Usage:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
    from shared.common import save_tiff, make_preview, measure_motif, outer_stroke
"""

import os
import numpy as np
from PIL import Image

ASSETS = os.path.join(os.path.dirname(__file__), "../assets")
TEMPLATES = os.path.join(ASSETS, "templates")


def save_tiff(img: Image.Image, png_path: str, dpi: int) -> None:
    """
    Save image as PNG under out/png/ and LZW TIFF under out/tiff/.
    png_path must point into an out/png/ directory; the tiff sibling is
    derived automatically by replacing /png/ with /tiff/.
    """
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    img.save(png_path, format="PNG")

    tiff_path = png_path.replace("/png/", "/tiff/").replace(os.sep + "png" + os.sep,
                                                             os.sep + "tiff" + os.sep)
    tiff_path = tiff_path.replace(".png", ".tiff")
    os.makedirs(os.path.dirname(tiff_path), exist_ok=True)
    img.save(tiff_path, format="TIFF", compression="tiff_lzw", dpi=(dpi, dpi))
    print(f"Saved: {png_path}")
    print(f"Saved: {tiff_path}")


def make_preview(
    design_path: str,
    out_path: str,
    shirt_name: str = "white_tshirt_front.jpg",
    cx: float = 0.5,
    cy: float = 0.28,
    logo_frac: float | None = None,
    logo_w: int | None = None,
) -> None:
    """
    Composite design onto a shirt template and save as JPEG.

    Exactly one of logo_frac or logo_w must be given.
    cx/cy are fractions of shirt dimensions for the design's top-left anchor
    (cx anchors horizontal center, cy anchors top edge).
    """
    if (logo_frac is None) == (logo_w is None):
        raise ValueError("Provide exactly one of logo_frac or logo_w")

    shirt = Image.open(os.path.join(TEMPLATES, shirt_name)).convert("RGBA")
    sw, sh = shirt.size

    design = Image.open(design_path).convert("RGBA")
    bb = design.getbbox()
    if bb:
        design = design.crop(bb)

    if logo_frac is not None:
        logo_w = int(sw * logo_frac)

    scale = logo_w / design.width
    logo_h = int(design.height * scale)
    design = design.resize((logo_w, logo_h), Image.LANCZOS)

    px = int(sw * cx) - logo_w // 2
    py = int(sh * cy)
    shirt.alpha_composite(design, dest=(px, py))
    shirt.convert("RGB").save(out_path, quality=92)
    print(f"Saved: {out_path}")


def measure_motif(img: Image.Image, dpi: int) -> tuple[float, float]:
    """
    Return (width_mm, height_mm) of the ink bounding box.
    Ink = any pixel with alpha > 0.
    """
    a = np.array(img)[:, :, 3]
    rows = np.any(a > 0, axis=1)
    cols = np.any(a > 0, axis=0)
    if not rows.any():
        return 0.0, 0.0
    r0, r1 = np.where(rows)[0][[0, -1]]
    c0, c1 = np.where(cols)[0][[0, -1]]
    w_px = int(c1 - c0 + 1)
    h_px = int(r1 - r0 + 1)
    return w_px / dpi * 25.4, h_px / dpi * 25.4


def outer_stroke(img: Image.Image, stroke_px: int) -> Image.Image:
    """Add an outer stroke of stroke_px pixels by compositing shifted copies."""
    w, h = img.size
    stroked = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for dist in range(1, stroke_px + 1):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ox, oy = dx * dist, dy * dist
            src_x = max(0, -ox); src_y = max(0, -oy)
            dst_x = max(0,  ox); dst_y = max(0,  oy)
            region = img.crop((src_x, src_y, src_x + w - abs(ox), src_y + h - abs(oy)))
            stroked.alpha_composite(region, dest=(dst_x, dst_y))
    stroked.alpha_composite(img)
    return stroked
