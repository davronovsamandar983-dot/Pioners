#!/usr/bin/env python3
"""Draw the SAT DAVLAT emblem: a double outer ring, three broken orbital
arcs carrying nodes, an interlocking trefoil knot at the centre, SAT set
along the top arc and the instructor name along the bottom arc.

Emits book/assets/logo.png (stroke alpha 255) and logo-watermark.png
(the same art baked at alpha 51/255), both 1250x1260 RGBA.

Both files must keep a real alpha channel: the emblem sits over navy on
the cover and over body text on every page, so an opaque white square
would show in both places.
"""
import math, pathlib, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1250, 1260
SS = 4                      # supersample, then downsample for clean edges
CX, CY = W / 2, H / 2 + 6
SOLID = (0, 24, 86, 255)
FAINT_RGB = (0, 30, 87)
FAINT_A = 51

SERIF = ("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf")

HERE = pathlib.Path(__file__).resolve().parent.parent
OUT = HERE / "book/assets"


def font(size):
    for p in SERIF:
        if pathlib.Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def arc_text(img, text, radius, centre_deg, size, flip=False):
    """Set text along a circular arc, one rotated glyph at a time."""
    f = font(size)
    probe = ImageDraw.Draw(img)
    if flip:                      # the bottom arc sweeps the other way
        text = text[::-1]
    gap = size * 0.16
    widths = [probe.textlength(ch, font=f) for ch in text]
    total = sum(widths) + gap * (len(text) - 1)
    ang = centre_deg - math.degrees(total / radius) / 2
    box = size * 2
    for ch, w in zip(text, widths):
        step = math.degrees((w + gap) / radius)
        a = math.radians(ang + step / 2)
        x, y = CX + radius * math.cos(a), CY + radius * math.sin(a)
        rot = -(ang + step / 2) + (90 if flip else -90)
        glyph = Image.new("RGBA", (box, box), (0, 0, 0, 0))
        ImageDraw.Draw(glyph).text((box / 2, box / 2), ch, font=f,
                                   fill=SOLID, anchor="mm")
        glyph = glyph.rotate(rot, resample=Image.BICUBIC, center=(box / 2, box / 2))
        img.alpha_composite(glyph, (int(x - box / 2), int(y - box / 2)))
        ang += step


def draw(name):
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def circle(r, width):
        d.ellipse([(CX - r) * SS, (CY - r) * SS, (CX + r) * SS, (CY + r) * SS],
                  outline=SOLID, width=int(width * SS))

    def arc(r, start, end, width):
        d.arc([(CX - r) * SS, (CY - r) * SS, (CX + r) * SS, (CY + r) * SS],
              start, end, fill=SOLID, width=int(width * SS))

    def dot(r, deg, rr):
        a = math.radians(deg)
        x, y = CX + r * math.cos(a), CY + r * math.sin(a)
        d.ellipse([(x - rr) * SS, (y - rr) * SS, (x + rr) * SS, (y + rr) * SS], fill=SOLID)

    # double outer border
    circle(604, 17)
    circle(556, 7)

    # three orbital arcs, broken where the two texts run
    arc(474, 200, 340, 7)
    arc(474, 20, 160, 7)
    arc(408, 194, 346, 6)
    arc(408, 14, 166, 6)
    arc(344, 188, 352, 5)
    arc(344, 8, 172, 5)

    # Nodes riding the orbits. There is deliberately none at top centre:
    # that is where SAT sits, and a node there prints through the A.
    for deg, r, rr in ((0, 474, 26), (180, 474, 26), (90, 408, 28),
                       (-38, 408, 22), (-142, 408, 22), (38, 344, 20), (142, 344, 20)):
        dot(r, deg, rr)

    # the knot: three thick interlocking crescents, 120 degrees apart
    for k in range(3):
        base = k * 120
        off = math.radians(base)
        ox, oy = CX + 62 * math.cos(off), CY + 62 * math.sin(off)
        r = 196
        o = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        ImageDraw.Draw(o).arc([(ox - r) * SS, (oy - r) * SS, (ox + r) * SS, (oy + r) * SS],
                              base + 28, base + 320, fill=SOLID, width=int(17 * SS))
        img.alpha_composite(o)

    img = img.resize((W, H), Image.LANCZOS)
    arc_text(img, "SAT", 500, -90, 108)
    arc_text(img, name.upper(), 505, 90, 66, flip=True)

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / "logo.png")

    # The faint variant is a second file baked at ~20% alpha, not a
    # draw-time opacity. Over white it resolves to roughly #CDD3DE.
    alpha = img.split()[3].point(lambda v: int(v * FAINT_A / 255))
    faint = Image.new("RGBA", (W, H), FAINT_RGB + (0,))
    faint.putalpha(alpha)
    faint.save(OUT / "logo-watermark.png")

    for f in ("logo.png", "logo-watermark.png"):
        im = Image.open(OUT / f)
        print(f"{f}: {im.size} {im.mode} max-alpha={im.getextrema()[3][1]}")


if __name__ == "__main__":
    draw(sys.argv[1] if len(sys.argv) > 1 else "DAVLAT KAMOLIDDINOV")
