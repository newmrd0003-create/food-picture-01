#!/usr/bin/env python3
"""Draw a steaming bowl of ramen, v2 — rich, painterly, appetizing.

PIL + numpy renderer (build-time only; the grader runs main.ts, which
just copies entry.png). Fully deterministic: fixed seeds, no time, no
network, no external assets. Rendered at 2x and downscaled for smooth
anti-aliasing. Writes entry.png (1024x1024) next to this script.

Scene: warm wood table, lacquered red bowl, golden glossy broth, thick
wavy noodles piled high, jammy egg halves, chashu, narutomaki, nori,
green onions, menma, sesame, chili oil, chopsticks lifting noodles,
layered steam rising into a warm glow.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2                      # supersample factor
W = H = 1024 * SS
OUT = 1024
SEED = 20261115

rng = random.Random(SEED)
npr = np.random.RandomState(SEED)


def S(v):
    """Scale a 1024-space coordinate to render space."""
    return v * SS


def xy(x, y):
    return (S(x), S(y))


def rgba(rgb, a=255):
    return (rgb[0], rgb[1], rgb[2], a)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(size, top, bot):
    """Vertical gradient RGB image."""
    w, h = size
    t = np.linspace(0, 1, h, dtype=np.float64)[:, None, None]
    top = np.array(top, dtype=np.float64)
    bot = np.array(bot, dtype=np.float64)
    arr = top[None, None, :] * (1 - t) + bot[None, None, :] * t
    arr = np.repeat(arr, w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def rgrad(size, center, inner, outer):
    """Radial gradient RGB image, center -> corners."""
    w, h = size
    cx, cy = center
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2)
    d = np.clip(d, 0, 1)[..., None]
    inner = np.array(inner, dtype=np.float64)
    outer = np.array(outer, dtype=np.float64)
    arr = inner * (1 - d) + outer * d
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def soft_ellipse(layer, box, fill, blur):
    """Filled ellipse on an RGBA layer, then blurred in place."""
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=fill)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def ellipse_ring(draw, cx, cy, rx, ry, width, color, alpha=255):
    """Ring drawn as many overlapping dots so it is solid at any width."""
    n = max(220, int(2.0 * (rx + ry)))
    for i in range(n):
        t = 2.0 * math.pi * i / n
        x = cx + rx * math.cos(t)
        y = cy + ry * math.sin(t)
        r = width / 2.0
        draw.ellipse([x - r, y - r, x + r, y + r], fill=rgba(color, alpha))


# ------------------------------------------------------------------ canvas --
img = vgrad((W, H), (26, 15, 8), (58, 34, 16)).convert("RGB")

# Wood grain: long horizontal streaks, low contrast, seeded noise.
grain = np.zeros((H, W), dtype=np.float64)
for _ in range(90):
    y0 = npr.randint(0, H)
    amp = npr.uniform(4, 14)
    thick = npr.randint(2, 7)
    wav = npr.uniform(0.5, 2.0)
    ph = npr.uniform(0, 6.28)
    xs = np.arange(W)
    yc = y0 + amp * np.sin(xs / W * 6.28 * wav + ph)
    for yy in range(-thick, thick + 1):
        yi = np.clip((yc + yy).astype(int), 0, H - 1)
        grain[yi, xs] += npr.uniform(-9, 9)
arr = np.asarray(img).astype(np.int16)
arr += np.clip(grain[..., None] * 0.8, -12, 12).astype(np.int16)
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

# Warm radial glow behind the bowl.
glow = rgrad((W, H), (S(512), S(430)), (150, 88, 34), (0, 0, 0))
glow = glow.filter(ImageFilter.GaussianBlur(S(120)))
img = Image.blend(img, Image.composite(glow, img, glow.convert("L")), 0.55)

draw = ImageDraw.Draw(img, "RGBA")

# -------------------------------------------------------------------- bowl --
BCX, BCY = S(512), S(600)          # bowl center
BRX, BRY = S(352), S(238)          # bowl outer radii
# Body: vertical gradient red lacquer.
body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
for i in range(BRY * 2):
    y = BCY - BRY + i
    t = i / (BRY * 2)
    c = lerp((146, 38, 28), (52, 14, 10), t)
    bd.line([(BCX - BRX, y), (BCX + BRX, y)], fill=rgba(c, 255))
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.ellipse([BCX - BRX, BCY - BRY, BCX + BRX, BCY + BRY], fill=255)
body.putalpha(Image.composite(body.split()[3], Image.new("L", (W, H), 0), mask))
img.paste(body, (0, 0), body)

# Glossy highlight arc on the bowl's left shoulder.
hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
soft_ellipse(hl, [S(210), S(430), S(360), S(760)], rgba((255, 190, 130), 60), S(26))
soft_ellipse(hl, [S(640), S(700), S(820), S(830)], rgba((255, 150, 90), 40), S(30))
img.paste(hl, (0, 0), hl)

# Decorative cream stripe + gold line low on the body.
draw = ImageDraw.Draw(img, "RGBA")
ellipse_ring(draw, BCX, S(648), S(338), S(206), S(9), (238, 220, 182), 235)
ellipse_ring(draw, BCX, S(668), S(340), S(210), S(4), (214, 166, 84), 230)
# Bowl foot.
draw.ellipse([S(452), S(812), S(572), S(852)], fill=rgba((40, 10, 8), 255))
draw.ellipse([S(458), S(812), S(566), S(842)], fill=rgba((70, 22, 14), 255))

# Rim: thick cream ring with a gold line.
ellipse_ring(draw, BCX, S(516), S(330), S(196), S(17), (246, 232, 200), 255)
ellipse_ring(draw, BCX, S(516), S(318), S(188), S(4), (206, 158, 76), 255)
# Inner rim shadow (broth sits inside this).
ellipse_ring(draw, BCX, S(516), S(306), S(178), S(6), (90, 40, 16), 160)

# ------------------------------------------------------------------- broth --
PCX, PCY = S(512), S(516)          # broth center
PRX, PRY = S(302), S(176)          # broth radii
broth = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bdraw = ImageDraw.Draw(broth)
# Radial broth gradient: golden center -> deep edge.
for r in range(100, -1, -1):
    t = r / 100.0
    c = lerp((216, 138, 44), (122, 62, 14), t)
    bdraw.ellipse([PCX - PRX * t, PCY - PRY * t,
                   PCX + PRX * t, PCY + PRY * t], fill=rgba(c, 255))
# Oil sheen: soft golden arcs and pools on the surface.
sheen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sheen)
for (sx, sy, sr, a) in [(420, 470, 90, 70), (620, 560, 110, 60),
                        (520, 600, 80, 55), (350, 560, 60, 50),
                        (680, 470, 55, 45)]:
    sd.ellipse([S(sx) - S(sr), S(sy) - S(sr) // 2, S(sx) + S(sr),
                S(sy) + S(sr) // 2], fill=rgba((248, 196, 92), a))
sheen = sheen.filter(ImageFilter.GaussianBlur(S(16)))
bmask = Image.new("L", (W, H), 0)
bmd = ImageDraw.Draw(bmask)
bmd.ellipse([PCX - PRX, PCY - PRY, PCX + PRX, PCY + PRY], fill=255)
broth = Image.composite(Image.alpha_composite(broth, sheen), broth, bmask)
img.paste(broth, (0, 0), broth)

# ----------------------------------------------------------------- noodles --
# Noodle layer clipped to the broth ellipse; each strand drawn 3x:
# dark shadow offset, main wheat stroke, light top highlight.
nood = Image.new("RGBA", (W, H), (0, 0, 0, 0))
nd = ImageDraw.Draw(nood)


def strand_path(x0, y0, dx, dy, waves, amp, phase):
    pts = []
    steps = 26
    for i in range(steps + 1):
        t = i / steps
        x = x0 + dx * t + amp * math.sin(2 * math.pi * waves * t + phase)
        y = y0 + dy * t + amp * 0.45 * math.sin(2 * math.pi * (waves + 1) * t + phase * 1.7)
        pts.append((x, y))
    return pts


wheat = [(232, 194, 104), (222, 178, 84), (240, 208, 128), (214, 164, 70)]
for _ in range(78):
    # random start inside broth, random direction
    ang = rng.uniform(0, 2 * math.pi)
    rr = rng.uniform(0.1, 0.95)
    x0 = PCX + PRX * rr * math.cos(ang)
    y0 = PCY + PRY * rr * math.sin(ang)
    leng = rng.uniform(120, 260) * SS
    dang = rng.uniform(0, 2 * math.pi)
    dx, dy = leng * math.cos(dang), leng * math.sin(dang) * 0.55
    waves = rng.uniform(1.5, 3.5)
    amp = rng.uniform(10, 26) * SS
    ph = rng.uniform(0, 6.28)
    wdt = rng.uniform(7, 11) * SS
    col = rng.choice(wheat)
    pts = strand_path(x0, y0, dx, dy, waves, amp, ph)
    nd.line(pts, fill=rgba((140, 96, 32), 200), width=int(wdt + 3 * SS), joint="curve")
    nd.line(pts, fill=rgba(col, 255), width=int(wdt), joint="curve")
    hi = [(x - 2 * SS, y - 2 * SS) for (x, y) in pts]
    nd.line(hi, fill=rgba((250, 226, 160), 220), width=max(2, int(wdt * 0.35)), joint="curve")
nood = Image.composite(nood, Image.new("RGBA", (W, H), (0, 0, 0, 0)), bmask)
img.paste(nood, (0, 0), nood)

# Lifted noodle bundle is drawn later, after the nori, so the chopsticks
# visibly hold it (see below, just before the chopsticks).

# ------------------------------------------------------------ toppings ------
def drop_shadow(cx, cy, rx, ry, alpha=90, blur=10):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    soft_ellipse(sh, [cx - rx, cy - ry + S(6), cx + rx, cy + ry + S(6)],
                 rgba((30, 12, 4), alpha), S(blur))
    img.paste(sh, (0, 0), sh)


draw = ImageDraw.Draw(img, "RGBA")

# --- soft egg halves (two, glossy jammy yolks) ---
def egg(cx, cy, rx, ry):
    drop_shadow(cx, cy, rx, ry)
    d = ImageDraw.Draw(img, "RGBA")
    # white: radial-ish gradient via stacked ellipses
    for r in range(10, -1, -1):
        t = r / 10.0
        c = lerp((252, 244, 224), (232, 214, 178), t)
        d.ellipse([cx - rx * t, cy - ry * t, cx + rx * t, cy + ry * t],
                  fill=rgba(c, 255))
    # yolk
    yx, yy, yr = cx + S(6), cy - S(2), S(30)
    for r in range(10, -1, -1):
        t = r / 10.0
        c = lerp((246, 139, 31), (214, 96, 12), t)
        d.ellipse([yx - yr * t, yy - yr * t * 0.92, yx + yr * t, yy + yr * t * 0.92],
                  fill=rgba(c, 255))
    # yolk gloss
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    soft_ellipse(g, [yx - S(16), yy - S(18), yx + S(6), yy - S(2)],
                 rgba((255, 220, 150), 200), S(6))
    img.paste(g, (0, 0), g)


egg(S(392), S(478), S(66), S(50))
egg(S(636), S(566), S(60), S(46))

# --- chashu slices (two overlapping, seared rim + fat swirl) ---
def chashu(cx, cy, r):
    drop_shadow(cx, cy, r, r * 0.92)
    d = ImageDraw.Draw(img, "RGBA")
    # Seared dark rim, then pink meat, then lighter pink center.
    d.ellipse([cx - r, cy - r * 0.92, cx + r, cy + r * 0.92],
              fill=rgba((122, 58, 30), 255))
    d.ellipse([cx - r * 0.82, cy - r * 0.76, cx + r * 0.82, cy + r * 0.76],
              fill=rgba((236, 174, 148), 255))
    d.ellipse([cx - r * 0.55, cy - r * 0.51, cx + r * 0.55, cy + r * 0.51],
              fill=rgba((246, 205, 182), 255))
    # White fat marbling arcs.
    d.arc([cx - r * 0.62, cy - r * 0.57, cx + r * 0.62, cy + r * 0.57],
          start=190, end=350, fill=rgba((252, 230, 210), 235), width=int(S(9)))
    d.arc([cx - r * 0.38, cy - r * 0.35, cx + r * 0.38, cy + r * 0.35],
          start=20, end=160, fill=rgba((252, 230, 210), 210), width=int(S(6)))
    # Seared edge dots on the outer rim only.
    for _ in range(14):
        a = rng.uniform(0, 6.28)
        x = cx + r * 0.93 * math.cos(a)
        y = cy + r * 0.85 * math.sin(a)
        d.ellipse([x - S(3), y - S(3), x + S(3), y + S(3)],
                  fill=rgba((80, 36, 16), 200))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    soft_ellipse(g, [cx - S(28), cy - S(30), cx + S(10), cy - S(6)],
                 rgba((255, 210, 180), 130), S(8))
    img.paste(g, (0, 0), g)


chashu(S(712), S(452), S(56))
chashu(S(742), S(520), S(50))

# --- narutomaki (two, pink spiral) ---
def naruto(cx, cy, r):
    drop_shadow(cx, cy, r, r)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba((250, 246, 238), 255))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgba((232, 122, 154), 255),
              width=int(S(4)))
    pts = []
    for i in range(61):
        t = i / 60
        a = t * 4.6 * math.pi
        rr = r * 0.82 * t
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.95))
    d.line(pts, fill=rgba((232, 122, 154), 255), width=int(S(5)), joint="curve")
    d.ellipse([cx - S(5), cy - S(5), cx + S(5), cy + S(5)],
              fill=rgba((232, 122, 154), 255))


naruto(S(560), S(632), S(30))
naruto(S(470), S(610), S(26))

# --- menma (bamboo shoots) ---
def menma(cx, cy, w, h, ang):
    drop_shadow(cx, cy, w, h * 0.5, alpha=70)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=int(S(8)),
                        fill=rgba((198, 143, 61), 255))
    d.rounded_rectangle([cx - w, cy - h, cx + w, cy - h + S(10)], radius=int(S(8)),
                        fill=rgba((224, 178, 96), 255))
    layer = layer.rotate(ang, center=(cx, cy), resample=Image.BICUBIC)
    img.paste(layer, (0, 0), layer)


menma(S(520), S(430), S(52), S(13), -18)
menma(S(600), S(420), S(46), S(12), 12)
menma(S(430), S(560), S(44), S(12), 24)

# --- green onion rings (scattered) ---
draw = ImageDraw.Draw(img, "RGBA")
for _ in range(30):
    ang = rng.uniform(0, 2 * math.pi)
    rr = rng.uniform(0.15, 0.95)
    x = PCX + PRX * rr * math.cos(ang)
    y = PCY + PRY * rr * math.sin(ang)
    r = rng.uniform(6, 10) * SS
    draw.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85],
                 fill=rgba((46, 139, 58), 255))
    draw.ellipse([x - r * 0.55, y - r * 0.45, x + r * 0.55, y + r * 0.45],
                 fill=rgba((126, 208, 122), 255))
    draw.ellipse([x - r * 0.2, y - r * 0.18, x + r * 0.2, y + r * 0.18],
                 fill=rgba((30, 90, 38), 255))

# --- sesame seeds ---
for _ in range(26):
    ang = rng.uniform(0, 2 * math.pi)
    rr = rng.uniform(0.1, 0.9)
    x = PCX + PRX * rr * math.cos(ang)
    y = PCY + PRY * rr * math.sin(ang)
    c = rng.choice([(245, 238, 220), (40, 28, 18)])
    draw.ellipse([x - S(4), y - S(2), x + S(4), y + S(2)], fill=rgba(c, 230))

# --- chili oil droplets (glossy red) ---
for (cx, cy, r) in [(S(470), S(520), S(9)), (S(600), S(600), S(11)),
                    (S(380), S(600), S(8)), (S(690), S(590), S(9))]:
    draw.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8],
                 fill=rgba((194, 46, 18), 235))
    draw.ellipse([cx - r * 0.45, cy - r * 0.5, cx + r * 0.1, cy - r * 0.05],
                 fill=rgba((255, 150, 110), 220))

# --- nori sheets (standing at the back, slight sheen) ---
def nori(cx, cy, w, h, ang):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=int(S(6)),
                        fill=rgba((16, 38, 26), 255))
    for gx in range(-2, 3):
        x = cx + gx * w // 2
        d.line([(x, cy - h + S(6)), (x, cy + h - S(6))],
               fill=rgba((38, 74, 52), 160), width=int(S(2)))
    d.rectangle([cx - w + S(8), cy - h + S(10), cx - w + S(16), cy + h - S(10)],
                fill=rgba((90, 130, 95), 90))
    layer = layer.rotate(ang, center=(cx, cy), resample=Image.BICUBIC)
    img.paste(layer, (0, 0), layer)


nori(S(566), S(372), S(36), S(56), 8)
nori(S(672), S(380), S(32), S(50), -10)

# --- lifted noodle bundle (drawn after the nori, before the chopsticks) ---
lift = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(lift)
tip = (S(664), S(302))
base = (S(690), S(490))
for k in range(12):
    off = (k - 5.5) * S(7)
    mid = (S(716) + off, S(396))
    pts = []
    for i in range(21):
        t = i / 20
        # quadratic bezier base -> mid -> tip
        x = (1 - t) ** 2 * (base[0] + off) + 2 * (1 - t) * t * mid[0] + t ** 2 * tip[0]
        y = (1 - t) ** 2 * base[1] + 2 * (1 - t) * t * mid[1] + t ** 2 * tip[1]
        x += S(6) * math.sin(t * 9 + k)
        pts.append((x, y))
    wdt = rng.uniform(6, 9) * SS
    col = rng.choice(wheat)
    ld.line(pts, fill=rgba((140, 96, 32), 200), width=int(wdt + 3 * SS), joint="curve")
    ld.line(pts, fill=rgba(col, 255), width=int(wdt), joint="curve")
    ld.line([(x - 2 * SS, y - 2 * SS) for (x, y) in pts],
            fill=rgba((250, 226, 160), 220), width=max(2, int(wdt * 0.35)), joint="curve")
img.paste(lift, (0, 0), lift)

# -------------------------------------------------------------- chopsticks --
def chopstick(x0, y0, x1, y1, w0, w1):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    pts = [(x0 + nx * w0 / 2, y0 + ny * w0 / 2),
           (x1 + nx * w1 / 2, y1 + ny * w1 / 2),
           (x1 - nx * w1 / 2, y1 - ny * w1 / 2),
           (x0 - nx * w0 / 2, y0 - ny * w0 / 2)]
    d = ImageDraw.Draw(img, "RGBA")
    # shadow under the stick
    sh = [(x + S(5), y + S(7)) for (x, y) in pts]
    d.polygon(sh, fill=rgba((20, 8, 4), 110))
    for t in [1.0, 0.7, 0.4]:
        c = lerp((184, 138, 78), (122, 82, 38), 1 - t)
        inset = (1 - t) * 0.28
        p = [(pts[0][0] + (pts[3][0] - pts[0][0]) * inset,
              pts[0][1] + (pts[3][1] - pts[0][1]) * inset),
             (pts[1][0] + (pts[2][0] - pts[1][0]) * inset,
              pts[1][1] + (pts[2][1] - pts[1][1]) * inset),
             pts[2], pts[3]]
        d.polygon(p, fill=rgba(c, 255))
    # top highlight line
    d.line([pts[0], pts[1]], fill=rgba((232, 190, 130), 200), width=int(S(3)))


chopstick(S(706), S(140), S(664), S(302), S(16), S(9))
chopstick(S(748), S(158), S(688), S(314), S(16), S(9))

# ------------------------------------------------------------------- steam --
steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(steam)
for (sx, amp, ph, a) in [(400, 26, 0.0, 90), (470, 32, 1.3, 80),
                         (550, 24, 2.6, 85), (620, 30, 4.1, 75)]:
    pts = []
    for i in range(41):
        t = i / 40
        x = S(sx) + S(amp) * math.sin(t * 7.5 + ph)
        y = S(430) - t * S(360)
        pts.append((x, y))
    sd.line(pts, fill=rgba((255, 246, 232), a), width=int(S(22)), joint="curve")
steam = steam.filter(ImageFilter.GaussianBlur(S(14)))
img.paste(steam, (0, 0), steam)
steam2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd2 = ImageDraw.Draw(steam2)
for (sx, amp, ph, a) in [(430, 18, 0.6, 60), (580, 20, 3.2, 55)]:
    pts = []
    for i in range(41):
        t = i / 40
        x = S(sx) + S(amp) * math.sin(t * 9 + ph)
        y = S(420) - t * S(330)
        pts.append((x, y))
    sd2.line(pts, fill=rgba((255, 250, 240), a), width=int(S(12)), joint="curve")
steam2 = steam2.filter(ImageFilter.GaussianBlur(S(8)))
img.paste(steam2, (0, 0), steam2)

# ------------------------------------------- table garnish + final grade -----
draw = ImageDraw.Draw(img, "RGBA")
for _ in range(8):
    x = rng.uniform(90, 934) * SS
    y = rng.uniform(880, 960) * SS
    r = rng.uniform(5, 8) * SS
    draw.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85],
                 fill=rgba((46, 139, 58), 200))
    draw.ellipse([x - r * 0.5, y - r * 0.4, x + r * 0.5, y + r * 0.4],
                 fill=rgba((126, 208, 122), 200))
for _ in range(14):
    x = rng.uniform(80, 944) * SS
    y = rng.uniform(860, 980) * SS
    c = rng.choice([(245, 238, 220), (40, 28, 18)])
    draw.ellipse([x - S(3), y - S(2), x + S(3), y + S(2)], fill=rgba(c, 200))

# Vignette: darken edges.
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W * 0.25, -H * 0.25, W * 1.25, H * 1.25], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(S(160)))
dark = Image.new("RGB", (W, H), (12, 6, 3))
img = Image.composite(img, dark, vig)

# Downscale and save.
img = img.resize((OUT, OUT), Image.LANCZOS)
img.save("entry.png")
print("wrote entry.png")
