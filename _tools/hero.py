#!/usr/bin/env python3
"""Home hero photo: grade and export from the 2752x1536 source (_src/hero-trader-2752.png).

The grade is done here, in the asset, never in CSS (no gradients/overlays in the stylesheet):
  * the left ~40% of the frame (street, danfo, passers-by) is darkened to 34% brightness with a
    smooth fall-off that ends at the shop doorway (~63% of the width), so the white headline sits
    on a quiet dark field while the trader stays untouched;
  * the far-left street is softened a touch so it does not compete with the headline;
  * a slight warmth (R +2%, G -1%, B -5%) and a small contrast lift over the whole frame.
Exports (assets/img): hero-trader-{1376,1920,2752}.{webp,jpg} for >=1024px viewports, and the
ungraded trader crop for phones, hero-trader-m-{640,956,1280}.{webp,jpg} (crop x 840..2752 of the
source, i.e. the same framing as the earlier 420..1376 crop of the 1376px master).

    python3 _tools/hero.py
"""
import os, subprocess
from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_src", "hero-trader-2752.png")
OUT = os.path.join(ROOT, "assets", "img")

DARK = 0.34          # brightness of the darkened field
RAMP = (0.40, 0.63)  # fall-off from full dark to untouched, as fractions of the width
SOFT = (0.30, 0.45)  # soften fully up to 30% of the width, fading out by 45%
WARM = (1.02, 0.99, 0.95)
CONTRAST = 1.04


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def hmask(w, h, a, b, invert=False):
    """L mask: 255 left of a, 0 right of b, smooth in between (or the reverse)."""
    row = []
    for x in range(w):
        v = 1 - smoothstep(a * w, b * w, x)
        row.append(int(round((1 - v if invert else v) * 255)))
    m = Image.new("L", (w, 1))
    m.putdata(row)
    return m.resize((w, h))


def grade(im):
    w, h = im.size
    # 1. soften the far-left street
    soft = im.filter(ImageFilter.GaussianBlur(radius=w / 1376 * 1.6))
    im = Image.composite(soft, im, hmask(w, h, *SOFT))
    # 2. darken the left field with a smooth fall-off ending at the doorway
    dark = ImageEnhance.Brightness(im).enhance(DARK)
    im = Image.composite(dark, im, hmask(w, h, *RAMP))
    # 3. warmth + a small contrast lift
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * WARM[0] + 0.5)))
    g = g.point(lambda v: min(255, int(v * WARM[1] + 0.5)))
    b = b.point(lambda v: min(255, int(v * WARM[2] + 0.5)))
    im = Image.merge("RGB", (r, g, b))
    return ImageEnhance.Contrast(im).enhance(CONTRAST)


def export(im, name, widths, q_jpg=82, q_webp=80):
    for w in widths:
        h = round(im.height * w / im.width)
        out = im if w == im.width else im.resize((w, h), Image.LANCZOS)
        jpg = os.path.join(OUT, f"{name}-{w}.jpg")
        out.save(jpg, "JPEG", quality=q_jpg, optimize=True, progressive=True, subsampling="4:2:0")
        webp = os.path.join(OUT, f"{name}-{w}.webp")
        out.save(webp, "WEBP", quality=q_webp, method=6)
        print(f"{name}-{w}: {w}x{h}  jpg {os.path.getsize(jpg)//1024} KB  webp {os.path.getsize(webp)//1024} KB")


def main():
    src = Image.open(SRC).convert("RGB")
    assert src.size == (2752, 1536), src.size
    graded = grade(src)
    export(graded, "hero-trader", [2752, 1920, 1376])
    # phones: ungraded trader crop, same framing as before (x 840..2752 = 1912x1536)
    crop = src.crop((840, 0, 2752, 1536))
    export(crop, "hero-trader-m", [1280, 956, 640])
    # sharpness check: edge energy of the 1920 export vs a 1920 downscale of the raw source
    a = graded.resize((1920, 1072), Image.LANCZOS).convert("L").filter(ImageFilter.FIND_EDGES)
    from PIL import ImageStat
    print("1920 export edge energy (higher = sharper):", round(ImageStat.Stat(a).mean[0], 2))


if __name__ == "__main__":
    main()
