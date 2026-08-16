#!/usr/bin/env python3
"""Draw the SAT DAVLAT emblem: concentric orbital rings with nodes, an
abstract knot at the centre, SAT along the top arc, the instructor name
along the bottom arc.

Emits book/assets/logo.png (stroke alpha 255) and logo-watermark.png
(the same art baked at alpha 51/255), both 1250x1260 RGBA.
"""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1250, 1260
SS = 4  # supersample factor
CX, CY = W / 2, H / 2 + 8
SOLID = (0, 24, 86, 255)
FAINT_RGB = (0, 30, 87)
FAINT_A = 51

HERE = pathlib.Path(__file__).resolve().parent.parent
OUT = HERE / "book/assets"


def font(size):
    for p in ("/usr/share/texmf/fonts/truetype/public/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if pathlib.Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def arc_text(d, text, radius, centre_deg, size, flip=False, spread=None):
    """Set text along a circular arc, letter by letter."""
    f = font(size)
    # the bottom arc is swept the other way round, so the glyphs have to
    # be laid down back to front to read left to right.
    if flip:
        text = text[::-1]
    widths = [d.textlength(ch, font=f) for ch in text]
    total = sum(widths) + (len(text) - 1) * size * 0.30
    span = spread if spread else math.degrees(total / radius)
    ang = centre_deg - span / 2
    for ch, w in zip(text, widths):
        step = math.degrees((w + size * 0.30) / radius)
        a = math.radians(ang + step / 2)
        x, y = CX + radius * math.cos(a), CY + radius * math.sin(a)
        rot = -(ang + step / 2) - 90 if not flip else -(ang + step / 2) + 90
        glyph = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
        ImageDraw.Draw(glyph).text((size, size), ch, font=f, fill=SOLID, anchor="mm")
        glyph = glyph.rotate(rot, resample=Image.BICUBIC, center=(size, size))
        d._image.alpha_composite(glyph, (int(x - size), int(y - size)))
        ang += step


def draw(name):
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d._image = img

    def ring(r, width):
        d.ellipse([(CX - r) * SS, (CY - r) * SS, (CX + r) * SS, (CY + r) * SS],
                  outline=SOLID, width=int(width * SS))

    # outer disc boundary and the orbital rings
    ring(600, 11)
    ring(560, 5)
    ring(430, 7)
    ring(360, 4)

    # orbital nodes on the 430 ring
    for k in range(12):
        a = math.radians(k * 30 - 90)
        x, y = CX + 430 * math.cos(a), CY + 430 * math.sin(a)
        rr = 26 if k % 3 == 0 else 15
        d.ellipse([(x - rr) * SS, (y - rr) * SS, (x + rr) * SS, (y + rr) * SS], fill=SOLID)

    # tilted orbits crossing the centre
    for tilt in (-32, 32, 90):
        box = [(CX - 300) * SS, (CY - 120) * SS, (CX + 300) * SS, (CY + 120) * SS]
        o = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        ImageDraw.Draw(o).ellipse(box, outline=SOLID, width=int(6 * SS))
        img.alpha_composite(o.rotate(tilt, resample=Image.BICUBIC, center=(CX * SS, CY * SS)))

    # the abstract knot at the centre: three interleaved loops
    for tilt in (0, 60, 120):
        box = [(CX - 130) * SS, (CY - 58) * SS, (CX + 130) * SS, (CY + 58) * SS]
        o = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        ImageDraw.Draw(o).ellipse(box, outline=SOLID, width=int(11 * SS))
        img.alpha_composite(o.rotate(tilt, resample=Image.BICUBIC, center=(CX * SS, CY * SS)))
    d.ellipse([(CX - 26) * SS, (CY - 26) * SS, (CX + 26) * SS, (CY + 26) * SS], fill=SOLID)

    img = img.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    d._image = img
    arc_text(d, "SAT", 497, -90, 96)
    arc_text(d, name.upper(), 497, 90, 62, flip=True)

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / "logo.png")

    # the faint variant is a second file baked at ~20% alpha, not a
    # draw-time opacity: it sits over navy on the cover and over body
    # text on every page.
    a = img.split()[3].point(lambda v: int(v * FAINT_A / 255))
    faint = Image.new("RGBA", (W, H), FAINT_RGB + (0,))
    faint.putalpha(a)
    faint.save(OUT / "logo-watermark.png")

    for f in ("logo.png", "logo-watermark.png"):
        im = Image.open(OUT / f)
        print(f"{f}: {im.size} {im.mode} max-alpha={max(im.split()[3].getdata())}")


if __name__ == "__main__":
    import sys
    draw(sys.argv[1] if len(sys.argv) > 1 else "DAVLAT")
