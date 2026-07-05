"""
font_creator — hand-drawn square Kufic designs on a numbered grid.
Grid: 30×30 cells, 50px per cell, 4 quadrants on a 3000×3000 canvas.
Layout: top-left, top-right, bottom-left, bottom-right.

To fill cells, edit assets/font_creator_cells.json and run this script.
To use the visual editor, open font_creator/grid_editor_thick.html in a browser.
"""

import json, os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from shared.common import save_tiff, make_preview

PNG_DIR      = os.path.join(os.path.dirname(__file__), "out", "png")
PREVIEWS_DIR = os.path.join(os.path.dirname(__file__), "previews")
ASSETS_DIR   = os.path.join(os.path.dirname(__file__), "../../assets")
os.makedirs(PNG_DIR,      exist_ok=True)
os.makedirs(PREVIEWS_DIR, exist_ok=True)

CANVAS  = 3000
HALF    = 1500
CELL_PX = 50
GRID_N  = 30
DPI     = 300
INK     = (0, 127, 255, 255)

QUAD_ORIGINS = {
    "top_left":     (0,    0),
    "top_right":    (HALF, 0),
    "bottom_left":  (0,    HALF),
    "bottom_right": (HALF, HALF),
}

# ---------------------------------------------------------------------------
# Cell data — (col, row) tuples per word, 0-indexed within each 30×30 quadrant
# Loaded from assets/font_creator_cells.json
# ---------------------------------------------------------------------------
with open(os.path.join(ASSETS_DIR, "font_creator_cells.json")) as _f:
    _cells_raw = json.load(_f)
CELLS = {word: [tuple(cell) for cell in cells] for word, cells in _cells_raw.items()}


def fill_cells(draw, word, cells):
    ox, oy = QUAD_ORIGINS[word]
    for col, row in cells:
        x0 = ox + col * CELL_PX; y0 = oy + row * CELL_PX
        draw.rectangle([x0, y0, x0 + CELL_PX - 1, y0 + CELL_PX - 1], fill=INK)


def render_grid(show_grid=True) -> Image.Image:
    EN_FONT     = "/System/Library/Fonts/Helvetica.ttc"
    fn_num      = ImageFont.truetype(EN_FONT, 26)
    GRID_COLOR  = (200, 200, 200, 255)
    MAJOR_COLOR = (130, 130, 130, 255)
    NUM_COLOR   = (80,  80,  80,  255)
    DIV_COLOR   = (30,  30,  30,  255)

    img  = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    for word in ("top_left", "top_right", "bottom_left", "bottom_right"):
        ox, oy = QUAD_ORIGINS[word]
        fill_cells(draw, word, CELLS[word])

        if show_grid:
            for i in range(GRID_N + 1):
                x = ox + i * CELL_PX; y = oy + i * CELL_PX
                color = MAJOR_COLOR if i % 5 == 0 else GRID_COLOR
                w     = 2            if i % 5 == 0 else 1
                draw.line([(x, oy), (x, oy + HALF)], fill=color, width=w)
                draw.line([(ox, y), (ox + HALF, y)], fill=color, width=w)

            for col in range(GRID_N):
                cx = ox + col * CELL_PX + CELL_PX // 2
                bb = draw.textbbox((0,0), str(col), font=fn_num)
                draw.text((cx-(bb[2]-bb[0])//2, oy+8), str(col), font=fn_num, fill=NUM_COLOR)

            for row in range(GRID_N):
                ry = oy + row * CELL_PX + CELL_PX // 2
                bb = draw.textbbox((0,0), str(row), font=fn_num)
                draw.text((ox+8, ry-(bb[3]-bb[1])//2), str(row), font=fn_num, fill=NUM_COLOR)

    draw.line([(HALF, 0), (HALF, CANVAS)], fill=DIV_COLOR, width=5)
    draw.line([(0, HALF), (CANVAS, HALF)], fill=DIV_COLOR, width=5)
    return img


def render_design() -> Image.Image:
    img  = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for word in CELLS:
        fill_cells(draw, word, CELLS[word])
    return img


if __name__ == "__main__":
    grid_img = render_grid(show_grid=True)
    grid_path = os.path.join(PNG_DIR, "hand_grid.png")
    grid_img.save(grid_path, format="PNG")
    print(f"Saved: {grid_path}")

    design   = render_design()
    png_path = os.path.join(PNG_DIR, "font_creator.png")
    save_tiff(design, png_path, DPI)

    make_preview(
        png_path,
        os.path.join(PREVIEWS_DIR, "preview_font_creator.jpg"),
        cx=0.5, cy=0.25,
        logo_w=940,
    )
