import os, sys
import uharfbuzz as hb
import aggdraw
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from shared.common import save_tiff, make_preview, outer_stroke
from shared.env import (
    PHRASE_B_SINGLE,
    PHRASE_B_VEC_L1, PHRASE_B_VEC_L2, PHRASE_B_VEC_L3,
    PHRASE_B_TAK_L1, PHRASE_B_TAK_L2, PHRASE_B_TAK_L3,
    LATIN_D,
)

ASSETS       = os.path.join(os.path.dirname(__file__), "../../assets")
FONTS_DIR    = os.path.join(ASSETS, "fonts")
PNG_DIR      = os.path.join(os.path.dirname(__file__), "out", "png")
PREVIEWS_DIR = os.path.join(os.path.dirname(__file__), "previews")
os.makedirs(PNG_DIR,      exist_ok=True)
os.makedirs(PREVIEWS_DIR, exist_ok=True)

SIZE = 3000
INK  = (0, 127, 255, 255)
DPI  = 300

TAKWEEN_W   = 5267
TAKWEEN_H   = 7500
TAKWEEN_DPI = 454


# ---------------------------------------------------------------------------
# Latin renderers
# ---------------------------------------------------------------------------

def render_latin(text, font_path, out_path, font_size=700):
    font = ImageFont.truetype(font_path, font_size)
    tmp  = Image.new("RGBA", (SIZE * 2, SIZE * 2), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((SIZE // 2, SIZE // 2), text, font=font, fill=INK)
    ink_bbox = tmp.getbbox()
    cropped  = tmp.crop(ink_bbox)
    pad      = int(cropped.height * 0.40)
    canvas_w = cropped.width  + pad * 2
    canvas_h = cropped.height + pad * 2
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    img.paste(cropped, (pad, pad), cropped)
    save_tiff(img, out_path, DPI)


def render_latin_stroked(text, font_path, out_path, font_size=700, stroke_px=5):
    font = ImageFont.truetype(font_path, font_size)
    tmp  = Image.new("RGBA", (SIZE * 2, SIZE * 2), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((SIZE // 2, SIZE // 2), text, font=font, fill=INK)
    orig    = tmp.crop(tmp.getbbox())
    stroked = outer_stroke(orig, stroke_px)
    pad     = int(orig.height * 0.40)
    img = Image.new("RGBA", (orig.width + pad * 2, orig.height + pad * 2), (0, 0, 0, 0))
    img.paste(stroked, (pad, pad), stroked)
    save_tiff(img, out_path, DPI)


# ---------------------------------------------------------------------------
# Arabic / Pillow renderers
# ---------------------------------------------------------------------------

def render_pillow_arabic(lines, font_path, out_path, font_size=700, line_gap=80, wide=False):
    font = ImageFont.truetype(font_path, font_size)
    line_imgs = []
    for line in lines:
        tmp = Image.new("RGBA", (SIZE * 2, SIZE * 2), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((SIZE // 2, SIZE // 2), line, font=font, fill=INK)
        bb = tmp.getbbox()
        line_imgs.append(tmp.crop(bb) if bb else Image.new("RGBA", (1, 1)))

    max_w  = max(im.width for im in line_imgs)
    scaled = []
    for im in line_imgs:
        scale = min(max_w / im.width, 1.4)
        scaled.append(im.resize((int(im.width * scale), max(1, int(im.height * scale))), Image.LANCZOS))

    total_h = sum(im.height for im in scaled) + line_gap * (len(scaled) - 1)
    total_w = max(im.width for im in scaled)

    if wide:
        pad = int(total_h * 0.5)
        canvas_w = total_w + pad * 2; canvas_h = total_h + pad * 2
    else:
        canvas_w = canvas_h = SIZE

    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    y   = (canvas_h - total_h) // 2
    for im in scaled:
        img.paste(im, ((canvas_w - im.width) // 2, y), im)
        y += im.height + line_gap
    save_tiff(img, out_path, DPI)


# ---------------------------------------------------------------------------
# Takween (A3 portrait, 454 DPI)
# ---------------------------------------------------------------------------

def _stretch_men_connector(img, target_w):
    w, h = img.size
    scale = w / 770.0
    c0 = int(320 * scale); c1 = int(490 * scale)
    needed_extra = target_w - w
    if needed_extra <= 0:
        return img
    new_connector_w = (c1 - c0 + 1) + needed_extra
    left   = img.crop((0,    0, c0,   h))
    middle = img.crop((c0,   0, c1+1, h)).resize((new_connector_w, h), Image.LANCZOS)
    right  = img.crop((c1+1, 0, w,    h))
    out = Image.new("RGBA", (target_w, h), (0, 0, 0, 0))
    out.paste(left,   (0, 0), left)
    out.paste(middle, (c0, 0), middle)
    out.paste(right,  (c0 + new_connector_w, 0), right)
    return out


def render_takween(lines, font_path, out_path, font_size=900, line_gap_frac=0.15, stroke_px=16):
    font = ImageFont.truetype(font_path, font_size)
    pad  = int(TAKWEEN_W * 0.10)

    line_imgs = []
    for line in lines:
        tmp = Image.new("RGBA", (TAKWEEN_W * 2, TAKWEEN_H), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((TAKWEEN_W, TAKWEEN_H // 2), line, font=font, fill=INK)
        bb = tmp.getbbox()
        line_imgs.append(tmp.crop(bb) if bb else Image.new("RGBA", (1, 1)))

    max_ink_w = max(im.width for im in line_imgs[1:])
    target_w  = min(max_ink_w, TAKWEEN_W - pad * 2)
    line_imgs[0] = _stretch_men_connector(line_imgs[0], target_w)
    line_imgs = [outer_stroke(im, stroke_px) for im in line_imgs]

    h_scale = target_w / max_ink_w
    scaled  = []
    for i, im in enumerate(line_imgs):
        if i == 0:
            scaled.append(im.resize((im.width, max(1, int(im.height * h_scale))), Image.LANCZOS))
        else:
            scaled.append(im.resize((target_w, max(1, int(im.height * h_scale))), Image.LANCZOS))

    avg_h   = sum(im.height for im in scaled) / len(scaled)
    gap     = int(avg_h * line_gap_frac)
    total_h = sum(im.height for im in scaled) + gap * (len(scaled) - 1)

    img        = Image.new("RGBA", (TAKWEEN_W, TAKWEEN_H), (0, 0, 0, 0))
    y          = (TAKWEEN_H - total_h) // 2
    right_edge = (TAKWEEN_W + target_w) // 2
    for im in scaled:
        img.paste(im, (right_edge - im.width, y), im)
        y += im.height + gap

    save_tiff(img, out_path, TAKWEEN_DPI)


# ---------------------------------------------------------------------------
# Arabic vector (harfbuzz + fontTools)
# ---------------------------------------------------------------------------

def render_arabic_vector(lines, font_path, out_path, font_size=900, line_gap=-80):
    tt          = TTFont(font_path)
    glyph_set   = tt.getGlyphSet()
    glyph_names = tt.getGlyphOrder()
    upm         = tt['head'].unitsPerEm
    ascender    = tt['OS/2'].sTypoAscender
    scale       = font_size / upm

    with open(font_path, "rb") as f:
        blob = hb.Blob(f.read())
    hb_font = hb.Font(hb.Face(blob))
    hb_font.scale = (upm, upm)

    def shape(text):
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        hb.shape(hb_font, buf)
        return buf.glyph_infos, buf.glyph_positions

    shaped_lines = [(line, *shape(line)) for line in lines]
    line_widths  = [sum(p.x_advance for p in positions) * scale
                    for _, _, positions in shaped_lines]
    max_lw       = max(line_widths)
    total_h      = len(lines) * font_size + (len(lines) - 1) * line_gap
    img    = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    canvas = aggdraw.Draw(img)
    brush  = aggdraw.Brush(INK[:3], opacity=255)
    start_y = (SIZE - total_h) // 2

    for row, (line, infos, positions) in enumerate(shaped_lines):
        lw        = line_widths[row]
        x_scale   = max_lw / lw if lw > 0 else 1.0
        cursor_x  = (SIZE - max_lw) / 2
        baseline_y = start_y + row * (font_size + line_gap) + ascender * scale

        for info, pos in zip(infos, positions):
            name = glyph_names[info.codepoint]
            pen  = RecordingPen()
            glyph_set[name].draw(pen)
            gx, gy = pos.x_offset, pos.y_offset

            def tr(fx, fy, _cx=cursor_x, _gx=gx, _gy=gy, _xs=x_scale):
                return (_cx + (_gx + fx) * scale * _xs,
                        baseline_y - (_gy + fy) * scale)

            path = aggdraw.Path()
            cur  = (0.0, 0.0)
            for op, args in pen.value:
                if op == 'moveTo':
                    cur = tr(*args[0]); path.moveto(*cur)
                elif op == 'lineTo':
                    cur = tr(*args[0]); path.lineto(*cur)
                elif op == 'qCurveTo':
                    pts = [cur] + [tr(*a) for a in args]
                    for i in range(len(pts) - 2):
                        p0, p1, p2 = pts[i], pts[i+1], pts[i+2] if i+2 < len(pts)-1 else pts[-1]
                        if i+2 < len(pts) - 1: p2 = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
                        c1 = (p0[0] + 2/3*(p1[0]-p0[0]), p0[1] + 2/3*(p1[1]-p0[1]))
                        c2 = (p2[0] + 2/3*(p1[0]-p2[0]), p2[1] + 2/3*(p1[1]-p2[1]))
                        path.curveto(*c1, *c2, *p2)
                    cur = pts[-1]
                elif op == 'curveTo':
                    pts = [tr(*a) for a in args]
                    path.curveto(*pts[0], *pts[1], *pts[2]); cur = pts[-1]
                elif op == 'closePath':
                    path.close()

            canvas.path(path, brush)
            cursor_x += pos.x_advance * scale * x_scale

    canvas.flush()
    save_tiff(img, out_path, DPI)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ENG = os.path.join(FONTS_DIR, "english")
    AR  = os.path.join(FONTS_DIR, "arabic")

    render_latin_stroked(
        LATIN_D,
        os.path.join(ENG, "almost-japanese", "Almost Japanese.ttf"),
        os.path.join(PNG_DIR, "almost_japanese.png"),
        font_size=590, stroke_px=5,
    )
    render_latin(
        LATIN_D,
        os.path.join(ENG, "syawal-khidmat", "Syawal Khidmat.ttf"),
        os.path.join(PNG_DIR, "syawal.png"),
        font_size=850,
    )

    render_arabic_vector(
        [PHRASE_B_VEC_L1, PHRASE_B_VEC_L2, PHRASE_B_VEC_L3],
        os.path.join(FONTS_DIR, "ghasedak.thin.otf"),
        os.path.join(PNG_DIR, "ghasedak.png"),
        font_size=900, line_gap=-80,
    )
    KALEEM = os.path.join(AR, "Kaleem-Font-Family", "Kaleem Bold.otf")
    render_pillow_arabic(
        [PHRASE_B_SINGLE],
        KALEEM,
        os.path.join(PNG_DIR, "kaleem_bold.png"),
        font_size=700, line_gap=40, wide=True,
    )

    TAKWEEN = os.path.join(AR, "Takween-Regular.otf")
    takween_png = os.path.join(PNG_DIR, "takween_may.png")
    render_takween(
        [PHRASE_B_TAK_L1, PHRASE_B_TAK_L2, PHRASE_B_TAK_L3],
        TAKWEEN,
        takween_png,
        line_gap_frac=0.08,
    )

    # Centered previews
    for name, logo_frac, cx, cy in [
        ("almost_japanese", 0.14, 0.38, 0.27),
        ("syawal",          0.13, 0.38, 0.27),
        ("ghasedak",        0.09, 0.68, 0.27),
        ("kaleem_bold",     0.30, 0.50, 0.32),
    ]:
        make_preview(
            os.path.join(PNG_DIR, f"{name}.png"),
            os.path.join(PREVIEWS_DIR, f"preview_{name}.jpg"),
            cx=cx, cy=cy, logo_frac=logo_frac,
        )

    # Pocket previews
    for name in ("almost_japanese", "syawal"):
        make_preview(
            os.path.join(PNG_DIR, f"{name}.png"),
            os.path.join(PREVIEWS_DIR, f"preview_{name}_pocket.jpg"),
            cx=0.41, cy=0.28, logo_frac=0.16,
        )

    # Takween previews (centered and pocket)
    make_preview(
        takween_png,
        os.path.join(PREVIEWS_DIR, "preview_takween_may.jpg"),
        cx=0.5, cy=0.25, logo_frac=0.33,
    )
    make_preview(
        takween_png,
        os.path.join(PREVIEWS_DIR, "preview_takween_may_pocket.jpg"),
        cx=0.62, cy=0.28, logo_frac=0.12,
    )
