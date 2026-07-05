"""
squared_thick — hand-drawn square Kufic design on a 50×50 grid, CELL_PX=60.
Canvas: 6000×6000 px → cropped to ink bbox + 1-cell padding, forced square.
DPI: 300.

Cell data sourced from font_creator/grid_editor_thick.html (storage key: font_creator_thick_v1).
All 4 words are 33×33 cells.
"""

import json, os, sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from shared.common import save_tiff, make_preview

PNG_DIR      = os.path.join(os.path.dirname(__file__), "out", "png")
PREVIEWS_DIR = os.path.join(os.path.dirname(__file__), "previews")
ASSETS_DIR   = os.path.join(os.path.dirname(__file__), "../../assets")
os.makedirs(PNG_DIR,      exist_ok=True)
os.makedirs(PREVIEWS_DIR, exist_ok=True)

N       = 50
CELL_PX = 60
HALF    = N * CELL_PX   # 3000
CANVAS  = HALF * 2      # 6000
DPI     = 300
INK     = (0, 127, 255, 255)

QUAD_ORIGINS = {
    "top_left":     (0,    0),
    "top_right":    (HALF, 0),
    "bottom_left":  (0,    HALF),
    "bottom_right": (HALF, HALF),
}

with open(os.path.join(ASSETS_DIR, "squared_cells.json")) as _f:
    _cells_raw = json.load(_f)
CELLS = {word: [tuple(cell) for cell in cells] for word, cells in _cells_raw.items()}


def render() -> Image.Image:
    """Render all 4 words, crop to ink bbox + 1-cell padding, force square."""
    img  = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for word, cells in CELLS.items():
        ox, oy = QUAD_ORIGINS[word]
        for col, row in cells:
            x0 = ox + col * CELL_PX; y0 = oy + row * CELL_PX
            draw.rectangle([x0, y0, x0 + CELL_PX - 1, y0 + CELL_PX - 1], fill=INK)

    arr   = np.array(img)
    alpha = arr[:, :, 3]
    rows  = np.any(alpha > 0, axis=1)
    cols  = np.any(alpha > 0, axis=0)
    r0 = int(np.argmax(rows));        r1 = int(len(rows)  - np.argmax(rows[::-1])  - 1)
    c0 = int(np.argmax(cols));        c1 = int(len(cols)  - np.argmax(cols[::-1])  - 1)
    ink_w = c1 - c0 + 1; ink_h = r1 - r0 + 1
    print(f"Ink bbox: {ink_w} × {ink_h} px")

    side       = max(ink_w, ink_h)
    pad        = CELL_PX
    final_side = side + pad * 2

    square   = Image.new("RGBA", (final_side, final_side), (0, 0, 0, 0))
    ink_crop = img.crop((c0, r0, c1 + 1, r1 + 1))
    square.paste(ink_crop, ((final_side - ink_w) // 2, (final_side - ink_h) // 2), ink_crop)

    assert square.size[0] == square.size[1], "Canvas is not square!"
    print(f"Square canvas: {square.size[0]} × {square.size[1]} px")
    print(f"Physical at {DPI} DPI: {square.size[0]/DPI*25.4:.1f} × {square.size[1]/DPI*25.4:.1f} mm")
    return square


if __name__ == "__main__":
    img      = render()
    png_path = os.path.join(PNG_DIR, "squared_thick.png")
    save_tiff(img, png_path, DPI)

    make_preview(
        png_path,
        os.path.join(PREVIEWS_DIR, "preview_squared_thick.jpg"),
        cx=0.5, cy=0.27,
        logo_frac=0.16,
    )
