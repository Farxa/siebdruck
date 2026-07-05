"""
pal_48 — basketball jersey number design.
LABEL_C over NUMBER_C in Freshman font, white fill, centered on A3 canvas.
Canvas: 3484×4961 px, 454 DPI.
Outputs to designs/pal_48/out/ and previews/.
"""

import os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from shared.common import save_tiff, make_preview
from shared.env import LABEL_C, NUMBER_C

ASSETS       = os.path.join(os.path.dirname(__file__), "../../assets")
FONTS_DIR    = os.path.join(ASSETS, "fonts")
PNG_DIR      = os.path.join(os.path.dirname(__file__), "out", "png")
PREVIEWS_DIR = os.path.join(os.path.dirname(__file__), "previews")
os.makedirs(PNG_DIR,      exist_ok=True)
os.makedirs(PREVIEWS_DIR, exist_ok=True)

W, H       = 3484, 4961
DPI        = 454
FONT_PATH  = os.path.join(FONTS_DIR, "Freshman.ttf")
FONT_SIZE  = 2116
FILL       = (255, 255, 255, 255)
NAME_GAP   = 298


def render_number() -> Image.Image:
    dummy = Image.new("RGBA", (1, 1))
    ddraw = ImageDraw.Draw(dummy)

    num_font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    num_bbox = ddraw.textbbox((0, 0), NUMBER_C, font=num_font)
    num_w    = num_bbox[2] - num_bbox[0]
    num_h    = num_bbox[3] - num_bbox[1]

    # Scale LABEL_C width to match NUMBER_C width
    trial_font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    trial_bbox = ddraw.textbbox((0, 0), LABEL_C, font=trial_font)
    trial_w    = trial_bbox[2] - trial_bbox[0]
    name_size  = int(FONT_SIZE * num_w / trial_w)
    name_font  = ImageFont.truetype(FONT_PATH, name_size)
    name_bbox  = ddraw.textbbox((0, 0), LABEL_C, font=name_font)
    name_w     = name_bbox[2] - name_bbox[0]
    name_h     = name_bbox[3] - name_bbox[1]

    total_h   = name_h + NAME_GAP + num_h
    img       = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw      = ImageDraw.Draw(img)
    block_top = (H - total_h) // 2

    nx = (W - name_w) // 2 - name_bbox[0]
    ny = block_top - name_bbox[1]
    draw.text((nx, ny), LABEL_C, font=name_font, fill=FILL)

    x = (W - num_w) // 2 - num_bbox[0]
    y = block_top + name_h + NAME_GAP - num_bbox[1]
    draw.text((x, y), NUMBER_C, font=num_font, fill=FILL)

    return img


if __name__ == "__main__":
    img      = render_number()
    png_path = os.path.join(PNG_DIR, "pal_48.png")
    save_tiff(img, png_path, DPI)

    make_preview(
        png_path,
        os.path.join(PREVIEWS_DIR, "preview_pal_48.jpg"),
        shirt_name="black_tshirt_back.jpg",
        cx=0.50, cy=0.28,
        logo_w=1050,
    )
