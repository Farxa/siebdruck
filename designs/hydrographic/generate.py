"""
Hydrographic artwork — Water bodies.

Canvas: 5267×7500 px, 454 DPI (A3 portrait).
Outputs to designs/hydrographic/out/ and previews/.
"""

import json, os, sys
import aggdraw
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from shared.common import save_tiff, make_preview, measure_motif

PNG_DIR      = os.path.join(os.path.dirname(__file__), "out", "png")
PREVIEWS_DIR = os.path.join(os.path.dirname(__file__), "previews")
ASSETS_DIR   = os.path.join(os.path.dirname(__file__), "../../assets")
os.makedirs(PNG_DIR,      exist_ok=True)
os.makedirs(PREVIEWS_DIR, exist_ok=True)


def load_polygon_points(filename):
    with open(os.path.join(ASSETS_DIR, filename)) as f:
        data = json.load(f)
    ring = data["features"][0]["geometry"]["coordinates"][0]
    return [(lon, lat) for lon, lat in ring]

W, H = 5267, 7500
DPI  = 454

FRAME_INSET_X = 158
FRAME_INSET_Y = 180
FRAME_WIDTH   = 54

FX0 = float(FRAME_INSET_X)
FY0 = float(FRAME_INSET_Y)
FX1 = float(W - FRAME_INSET_X)
FY1 = float(H - FRAME_INSET_Y)
DW  = FX1 - FX0
DH  = FY1 - FY0

COAST_WIDTH        = 64
LAKE_WIDTH         = 56
JORDAN_WIDTH       = 50
TRIB_WIDTH         = 40
FRAME_WIDTH_STROKE = FRAME_WIDTH

INK = (0, 127, 255)

GEO_WEST  = 34.22
GEO_EAST  = 35.80
GEO_NORTH = 33.35
GEO_SOUTH = 29.40


def geo(lon, lat):
    x = FX0 + (lon - GEO_WEST)  / (GEO_EAST  - GEO_WEST)  * DW
    y = FY0 + (GEO_NORTH - lat) / (GEO_NORTH - GEO_SOUTH) * DH
    return (float(x), float(y))


# ---------------------------------------------------------------------------
# Spline / path helpers
# ---------------------------------------------------------------------------

def catmull_rom_path(points, closed=False):
    path = aggdraw.Path()
    px   = [geo(lon, lat) for lon, lat in points]
    n    = len(px)
    path.moveto(*px[0])
    iters = n if closed else n - 1
    for i in range(iters):
        p0 = px[(i - 1) % n]; p1 = px[i % n]
        p2 = px[(i + 1) % n]; p3 = px[(i + 2) % n]
        t  = 1 / 6
        path.curveto(
            p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t,
            p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t,
            p2[0], p2[1]
        )
    if closed:
        path.close()
    return path


def spline_pts(pts):
    path = aggdraw.Path()
    n = len(pts)
    path.moveto(*pts[0])
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]
        p2 = pts[i + 1];         p3 = pts[min(i + 2, n - 1)]
        t  = 1 / 6
        path.curveto(
            p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t,
            p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t,
            p2[0], p2[1]
        )
    return path


def draw_dashed_polyline(draw, points_geo, width, dash=90, gap=70):
    import math
    px = [geo(lon, lat) for lon, lat in points_geo]
    pen = aggdraw.Pen(INK, width=width, opacity=255)
    drawing = True; remaining = dash
    for i in range(len(px) - 1):
        x0, y0 = px[i]; x1, y1 = px[i + 1]
        seg_len = math.hypot(x1 - x0, y1 - y0)
        if seg_len == 0:
            continue
        dx, dy = (x1 - x0) / seg_len, (y1 - y0) / seg_len
        pos = 0.0
        while pos < seg_len:
            chunk = min(remaining, seg_len - pos)
            ex = x0 + dx * (pos + chunk); ey = y0 + dy * (pos + chunk)
            if drawing:
                path = aggdraw.Path()
                path.moveto(x0 + dx * pos, y0 + dy * pos)
                path.lineto(ex, ey)
                draw.path(path, pen)
            pos += chunk; remaining -= chunk
            if remaining <= 0:
                drawing = not drawing
                remaining = dash if drawing else gap


# ---------------------------------------------------------------------------
# Geographic data
# ---------------------------------------------------------------------------

coastline_points = [
    (35.103, 33.090), (35.092, 32.992), (35.073, 32.922), (35.030, 32.855),
    (34.972, 32.815), (34.940, 32.720), (34.932, 32.625), (34.896, 32.495),
    (34.856, 32.325), (34.806, 32.162), (34.760, 32.063), (34.708, 31.950),
    (34.643, 31.808), (34.553, 31.665), (34.512, 31.545), (34.478, 31.462),
    (34.413, 31.350), (34.266, 31.216), (34.222, 31.155),
]

BEZIER_OVERRIDES = {}

galilee_points = [
    (35.5463, 32.8122), (35.5544, 32.7998), (35.5561, 32.7965), (35.5573, 32.7931),
    (35.5612, 32.7754), (35.5683, 32.7570), (35.5719, 32.7456), (35.5735, 32.7382),
    (35.5762, 32.7219), (35.5786, 32.7149), (35.5816, 32.7097), (35.5843, 32.7075),
    (35.5877, 32.7072), (35.5906, 32.7085), (35.5943, 32.7117), (35.5988, 32.7171),
    (35.6036, 32.7247), (35.6060, 32.7291), (35.6082, 32.7336), (35.6119, 32.7427),
    (35.6133, 32.7471), (35.6154, 32.7551), (35.6164, 32.7625), (35.6172, 32.7839),
    (35.6200, 32.8081), (35.6210, 32.8287), (35.6223, 32.8429), (35.6223, 32.8506),
    (35.6211, 32.8579), (35.6189, 32.8651), (35.6144, 32.8764), (35.6105, 32.8842),
    (35.6078, 32.8879), (35.6048, 32.8904), (35.5996, 32.8921), (35.5945, 32.8919),
    (35.5900, 32.8901), (35.5765, 32.8795), (35.5616, 32.8702), (35.5582, 32.8669),
    (35.5555, 32.8628), (35.5492, 32.8489), (35.5469, 32.8418), (35.5461, 32.8381),
    (35.5453, 32.8336), (35.5451, 32.8261), (35.5463, 32.8122),
]

dead_sea_points        = load_polygon_points("deadsea_gap.geojson")
dead_sea_middle_points = load_polygon_points("deadsea_pans.geojson")
dead_sea_south_points  = load_polygon_points("deadsea_south.geojson")

jordan_river_points = [
    (35.5877, 32.7072), (35.5680, 32.6981), (35.5645, 32.6772), (35.5658, 32.6410),
    (35.5739, 32.5679), (35.5722, 32.5545), (35.5641, 32.5350), (35.5615, 32.5219),
    (35.5617, 32.5126), (35.5674, 32.4878), (35.5671, 32.4605), (35.5656, 32.4470),
    (35.5576, 32.4198), (35.5561, 32.3988), (35.5578, 32.3262), (35.5677, 32.2217),
    (35.5677, 32.2076), (35.5646, 32.1940), (35.5545, 32.1675), (35.5376, 32.0833),
    (35.5261, 32.0507), (35.5235, 32.0364), (35.5252, 32.0183), (35.5372, 31.9860),
    (35.5419, 31.9586), (35.5412, 31.9449), (35.5309, 31.9130), (35.5302, 31.8996),
    (35.5423, 31.8710), (35.5422, 31.8537), (35.5457, 31.8375), (35.5446, 31.8195),
    (35.5456, 31.8068), (35.5515, 31.7828), (35.5612, 31.7585), (35.5480, 31.6000),
    (35.5430, 31.4389),
]

yarmouk_points = [
    (35.5641, 32.6477), (35.5899, 32.6478), (35.5993, 32.6597), (35.6161, 32.6710),
    (35.6710, 32.6890), (35.6818, 32.7042), (35.7570, 32.7385), (35.7923, 32.7486),
    (35.8000, 32.7406),
]

zarqa_points = [
    (35.5433, 32.1156), (35.5782, 32.1326), (35.6242, 32.1779), (35.6521, 32.1935),
    (35.6658, 32.1941), (35.6850, 32.1870), (35.6980, 32.1862), (35.7990, 32.1906),
]

upper_jordan_points = [
    (35.6255, 33.1956), (35.6097, 32.9461), (35.5996, 32.8921),
]

yarkon_points = [
    (34.900, 32.091), (34.840, 32.090), (34.790, 32.092), (34.769, 32.095),
]

kishon_points = [
    (35.190, 32.598), (35.085, 32.640), (35.008, 32.718), (34.988, 32.778),
    (34.985, 32.840),
]

gulf_west_shore = [
    (34.941, 29.553), (34.880, 29.490), (34.845, 29.400),
]
gulf_east_shore = [
    (34.945, 29.400), (34.960, 29.490), (34.979, 29.528),
]
gulf_tip_points = [
    (34.979, 29.528), (34.973, 29.538), (34.965, 29.548), (34.953, 29.553),
    (34.941, 29.553),
]


# ---------------------------------------------------------------------------
# Path builders
# ---------------------------------------------------------------------------

def _build_coastline_path():
    px = [geo(lon, lat) for lon, lat in coastline_points]
    top_entry = (px[0][0], FY0)
    all_pts = [top_entry] + px
    n = len(all_pts)
    path = aggdraw.Path()
    path.moveto(*all_pts[0])
    for i in range(n - 1):
        p1 = all_pts[i]; p2 = all_pts[i + 1]
        if i in BEZIER_OVERRIDES:
            cp1_geo, cp2_geo = BEZIER_OVERRIDES[i]
            cp1 = geo(*cp1_geo); cp2 = geo(*cp2_geo)
            path.curveto(cp1[0], cp1[1], cp2[0], cp2[1], p2[0], p2[1])
        else:
            p0 = all_pts[max(i - 1, 0)]; p3 = all_pts[min(i + 2, n - 1)]
            t = 1 / 6
            path.curveto(
                p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t,
                p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t,
                p2[0], p2[1]
            )
    return path


def build_med_sea_shape():
    path = _build_coastline_path()
    last = geo(*coastline_points[-1])
    path.lineto(FX0, last[1])
    path.lineto(FX0, FY0)
    path.close()
    return path


def build_coastline_stroke():
    return _build_coastline_path()


def build_gulf_shape():
    west_px = [geo(lon, lat) for lon, lat in gulf_west_shore]
    east_px = [geo(lon, lat) for lon, lat in gulf_east_shore]
    tip_px  = [geo(lon, lat) for lon, lat in gulf_tip_points]
    path = aggdraw.Path()
    path.moveto(*west_px[0])
    for pt in west_px[1:]: path.lineto(*pt)
    path.lineto(*east_px[0])
    for pt in east_px[1:]: path.lineto(*pt)
    for pt in tip_px[1:]:  path.lineto(*pt)
    path.close()
    return path


# ---------------------------------------------------------------------------
# Layer renderers
# ---------------------------------------------------------------------------

def _new_draw():
    img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return img, aggdraw.Draw(img)


def render_layer_water():
    img, draw = _new_draw()
    fill  = aggdraw.Brush(INK, opacity=255)
    c_pen = aggdraw.Pen(INK, width=COAST_WIDTH,  opacity=255)
    l_pen = aggdraw.Pen(INK, width=LAKE_WIDTH,   opacity=255)
    j_pen = aggdraw.Pen(INK, width=JORDAN_WIDTH, opacity=255)

    draw.path(build_med_sea_shape(),    fill)
    draw.path(build_coastline_stroke(), c_pen)

    gal_px = [geo(lon, lat) for lon, lat in galilee_points]
    gal_path = aggdraw.Path()
    gal_path.moveto(*gal_px[0])
    for pt in gal_px[1:]: gal_path.lineto(*pt)
    gal_path.close()
    draw.path(gal_path, fill, l_pen)

    for ds_pts in (dead_sea_points, dead_sea_middle_points, dead_sea_south_points):
        ds_px = [geo(lon, lat) for lon, lat in ds_pts]
        ds_path = aggdraw.Path()
        ds_path.moveto(*ds_px[0])
        for pt in ds_px[1:]: ds_path.lineto(*pt)
        ds_path.close()
        draw.path(ds_path, fill, l_pen)

    draw.path(build_gulf_shape(), fill, l_pen)
    draw.path(spline_pts([geo(*pt) for pt in jordan_river_points]), j_pen)
    draw_dashed_polyline(draw, upper_jordan_points, TRIB_WIDTH)
    draw_dashed_polyline(draw, yarmouk_points, TRIB_WIDTH)
    draw_dashed_polyline(draw, zarqa_points,   TRIB_WIDTH)
    draw_dashed_polyline(draw, yarkon_points,  TRIB_WIDTH)
    draw_dashed_polyline(draw, kishon_points,  TRIB_WIDTH)
    draw.flush()
    return img


def render_layer_frame():
    img, draw = _new_draw()
    pen = aggdraw.Pen(INK, width=FRAME_WIDTH_STROKE, opacity=255)
    draw.rectangle([FRAME_INSET_X, FRAME_INSET_Y, W - FRAME_INSET_X, H - FRAME_INSET_Y], pen)
    draw.flush()
    return img


def render_layer_scale():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _render_scale_bar(img)
    return img


def _render_scale_bar(img):
    px_per_km = (DH / (GEO_NORTH - GEO_SOUTH)) / 111.0
    km_px     = round(60 * px_per_km)
    mi_px     = round(60 * 1.60934 * px_per_km)
    bar_x     = int(FX0) + 200
    bar_y     = int(FY1) - 750
    draw      = ImageDraw.Draw(img)
    BLACK     = INK + (255,)
    lw = 30; tick_major = 90; tick_minor = 45; font_size = 120; label_gap = 15
    bar_y_km  = bar_y + tick_major + font_size + label_gap * 2
    try:
        font_num = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except Exception:
        font_num = ImageFont.load_default()
    spine_top = bar_y; spine_bottom = bar_y_km + tick_major
    draw.rectangle([bar_x - lw//2, spine_top, bar_x + lw//2, spine_bottom], fill=BLACK)
    draw.rectangle([bar_x, bar_y - lw//2, bar_x + mi_px, bar_y + lw//2], fill=BLACK)
    draw.text((bar_x + lw//2 + 5, bar_y - lw//2 - label_gap), "0", font=font_num, fill=BLACK, anchor="lb")
    for frac, lbl in [(0.5, "30"), (1.0, "60 mi")]:
        tx = bar_x + round(frac * mi_px)
        draw.rectangle([tx - lw//2, bar_y, tx + lw//2, bar_y + tick_major], fill=BLACK)
        draw.text((tx, bar_y - lw//2 - label_gap), lbl, font=font_num, fill=BLACK, anchor="mb")
    for frac in [0.25, 0.75]:
        tx = bar_x + round(frac * mi_px)
        draw.rectangle([tx - lw//2, bar_y, tx + lw//2, bar_y + tick_minor], fill=BLACK)
    draw.rectangle([bar_x, bar_y_km - lw//2, bar_x + km_px, bar_y_km + lw//2], fill=BLACK)
    draw.text((bar_x + lw//2 + 5, bar_y_km - lw//2 - label_gap), "0", font=font_num, fill=BLACK, anchor="lb")
    for frac, lbl in [(0.5, "30"), (1.0, "60 km")]:
        tx = bar_x + round(frac * km_px)
        draw.rectangle([tx - lw//2, bar_y_km, tx + lw//2, bar_y_km + tick_major], fill=BLACK)
        draw.text((tx, bar_y_km - lw//2 - label_gap), lbl, font=font_num, fill=BLACK, anchor="mb")
    for frac in [0.25, 0.75]:
        tx = bar_x + round(frac * km_px)
        draw.rectangle([tx - lw//2, bar_y_km, tx + lw//2, bar_y_km + tick_minor], fill=BLACK)


def render_layer_mediterranean():
    img, draw = _new_draw()
    fill  = aggdraw.Brush(INK, opacity=255)
    c_pen = aggdraw.Pen(INK, width=COAST_WIDTH, opacity=255)
    draw.path(build_med_sea_shape(),    fill)
    draw.path(build_coastline_stroke(), c_pen)
    draw.flush()
    return img


def render_layer_galilee():
    img, draw = _new_draw()
    fill  = aggdraw.Brush(INK, opacity=255)
    l_pen = aggdraw.Pen(INK, width=LAKE_WIDTH, opacity=255)
    gal_px = [geo(lon, lat) for lon, lat in galilee_points]
    gal_path = aggdraw.Path()
    gal_path.moveto(*gal_px[0])
    for pt in gal_px[1:]: gal_path.lineto(*pt)
    gal_path.close()
    draw.path(gal_path, fill, l_pen)
    draw.flush()
    return img


def render_layer_dead_sea():
    img, draw = _new_draw()
    fill  = aggdraw.Brush(INK, opacity=255)
    l_pen = aggdraw.Pen(INK, width=LAKE_WIDTH, opacity=255)
    for ds_pts in (dead_sea_points, dead_sea_middle_points, dead_sea_south_points):
        ds_px = [geo(lon, lat) for lon, lat in ds_pts]
        ds_path = aggdraw.Path()
        ds_path.moveto(*ds_px[0])
        for pt in ds_px[1:]: ds_path.lineto(*pt)
        ds_path.close()
        draw.path(ds_path, fill, l_pen)
    draw.flush()
    return img


def render_layer_gulf():
    img, draw = _new_draw()
    fill  = aggdraw.Brush(INK, opacity=255)
    l_pen = aggdraw.Pen(INK, width=LAKE_WIDTH, opacity=255)
    draw.path(build_gulf_shape(), fill, l_pen)
    draw.flush()
    return img


def render_layer_jordan():
    img, draw = _new_draw()
    j_pen = aggdraw.Pen(INK, width=JORDAN_WIDTH, opacity=255)
    draw.path(spline_pts([geo(*pt) for pt in jordan_river_points]), j_pen)
    draw.flush()
    return img


def render_layer_tributaries():
    img, draw = _new_draw()
    draw_dashed_polyline(draw, upper_jordan_points, TRIB_WIDTH)
    draw_dashed_polyline(draw, yarmouk_points, TRIB_WIDTH)
    draw_dashed_polyline(draw, zarqa_points,   TRIB_WIDTH)
    draw_dashed_polyline(draw, yarkon_points,  TRIB_WIDTH)
    draw_dashed_polyline(draw, kishon_points,  TRIB_WIDTH)
    draw.flush()
    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Rendering layers…")
    water          = render_layer_water()
    layer_frame    = render_layer_frame()
    layer_scale    = render_layer_scale()

    artwork = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    artwork.alpha_composite(water)
    artwork.alpha_composite(layer_frame)
    artwork.alpha_composite(layer_scale)

    png_path = os.path.join(PNG_DIR, "hydrographic.png")
    save_tiff(artwork, png_path, DPI)

    # Individual layers
    layers = [
        (render_layer_mediterranean(), "Layer_Mediterranean.png"),
        (render_layer_galilee(),       "Layer_Galilee.png"),
        (render_layer_dead_sea(),      "Layer_DeadSea.png"),
        (render_layer_gulf(),          "Layer_Gulf.png"),
        (render_layer_jordan(),        "Layer_Jordan.png"),
        (render_layer_tributaries(),   "Layer_Tributaries.png"),
        (water,                        "Layer_Water.png"),
        (layer_frame,                  "Layer_Frame.png"),
        (layer_scale,                  "Layer_Scale.png"),
    ]
    for img, name in layers:
        img.save(os.path.join(PNG_DIR, name), format="PNG")
        print(f"Saved: {name}")

    w_mm, h_mm = measure_motif(artwork, DPI)
    print(f"\nMotif: {w_mm:.0f} × {h_mm:.0f} mm at {DPI} DPI")

    make_preview(
        png_path,
        os.path.join(PREVIEWS_DIR, "preview_hydrographic.jpg"),
        shirt_name="white_tshirt_back.jpg",
        cx=0.5, cy=0.22,
        logo_frac=0.36,
    )
