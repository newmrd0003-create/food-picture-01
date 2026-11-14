#!/usr/bin/env python3
"""Draw a steaming bowl of ramen, v4 — top-1 push vs v3 (72.8%).

v2 scored only 72.8% (v1 72.2%): polishing the same flat top-down bowl
is dead. v3 rethinks the image against the judge's own criteria
(RULES.txt): (1) makes you hungry, (2) food looks FRESH and REAL with
texture you can taste — steam, gloss, melt — not plastic or muddy,
(3) styling/light/composition lead the eye to the food,
(5) reads small at ~300px, main dish clear.

Changes vs v3 (fixes found by looking at v3 @300px):
- Bowl BIGGER and cropped at the frame bottom (~87% width): the dark
  red body no longer eats a third of the frame; broth is the hero.
- Egg BIGGER (rx 104->118, yolk r 52->60, brighter yolk heart).
- Chashu "smiley face" fixed: green onions / sesame / chili now drawn
  BEFORE egg+chashu, so nothing lands on their faces.
- Nori rebuilt as a curved sheet leaning on the rim, not a flat card.
- Steam stronger/brighter; broth warmer + stronger specular; noodles
  thicker with more gloss; chopsticks thicker.
- fBm wood-grain table in the bottom corners (grounds the shot).
- Final unsharp mask for 300px crispness.
- Noodle NEST: thick strands in a deliberate chef's swirl (tangential
  flow around the nest center) instead of 78 random spaghetti worms;
  each strand 4 passes: shadow, wheat body, bright top highlight,
  wet gloss streak. Broth-coated look.
- ONE big jammy egg, front-center, huge at 300px: radial-gradient yolk
  (bright orange heart -> deep amber), glossy specular, soft white.
- Chashu: 2 LARGE slices front-right with seared char streaks, pink
  gradient, fat marbling, gloss.
- Broth: rich amber radial gradient + key-light specular arc + oil
  pools with bright specular dots + per-pixel grain (numpy) so it
  reads as liquid, not a flat disc.
- Background: dark warm bokeh (out-of-focus amber lights) for depth
  of field; bowl sharp, background soft.
- Steam: 6 strong columns, brighter, rising into the top third.
- Final grade: warm saturation lift + fine film grain for a
  photographic feel.

PIL + numpy + scipy renderer (build-time only; the grader runs
main.ts, which just copies entry.png). Fully deterministic: fixed
seeds, no time, no network, no external assets. Rendered at 2x and
downscaled. Writes entry.png (1024x1024) next to this script.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

SS = 2                      # supersample factor
W = H = 1024 * SS
OUT = 1024
SEED = 20261115

rng = random.Random(SEED)
npr = np.random.RandomState(SEED)


def S(v):
    return v * SS


def rgba(rgb, a=255):
    return (rgb[0], rgb[1], rgb[2], a)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(size, top, bot):
    w, h = size
    t = np.linspace(0, 1, h, dtype=np.float64)[:, None, None]
    top = np.array(top, dtype=np.float64)
    bot = np.array(bot, dtype=np.float64)
    arr = top[None, None, :] * (1 - t) + bot[None, None, :] * t
    arr = np.repeat(arr, w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def soft_ellipse(layer, box, fill, blur):
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=fill)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def ellipse_ring(draw, cx, cy, rx, ry, width, color, alpha=255):
    n = max(220, int(2.0 * (rx + ry)))
    for i in range(n):
        t = 2.0 * math.pi * i / n
        x = cx + rx * math.cos(t)
        y = cy + ry * math.sin(t)
        r = width / 2.0
        draw.ellipse([x - r, y - r, x + r, y + r], fill=rgba(color, alpha))


# ------------------------------------------------------------------ canvas --
# Dark warm background, slightly lighter toward the top (steam glow zone).
img = vgrad((W, H), (34, 20, 10), (16, 9, 5)).convert("RGB")

# Warm bokeh: out-of-focus amber lights, heavily blurred -> depth of field.
bok = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(bok)
for _ in range(26):
    x = rng.uniform(0, 1024) * SS
    y = rng.uniform(0, 420) * SS
    r = rng.uniform(14, 55) * SS
    c = rng.choice([(255, 170, 70), (255, 200, 110), (220, 130, 40),
                    (255, 140, 60)])
    a = rng.randint(28, 85)
    bd.ellipse([x - r, y - r, x + r, y + r], fill=rgba(c, a))
bok = bok.filter(ImageFilter.GaussianBlur(S(34)))
img.paste(bok, (0, 0), bok)
# A few larger, dimmer bokeh at the bottom corners.
bok2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd2 = ImageDraw.Draw(bok2)
for (x, y, r, a) in [(90, 950, 70, 40), (940, 930, 80, 34), (60, 700, 46, 30)]:
    bd2.ellipse([S(x) - S(r), S(y) - S(r), S(x) + S(r), S(y) + S(r)],
                fill=rgba((255, 170, 80), a))
bok2 = bok2.filter(ImageFilter.GaussianBlur(S(40)))
img.paste(bok2, (0, 0), bok2)

# Warm glow rising above the bowl: soft radial wash, no hard edge.
gw, gh = W, H
gyy, gxx = np.mgrid[0:gh, 0:gw].astype(np.float64)
gd = np.clip(np.sqrt(((gxx - S(512)) / S(420)) ** 2 +
                     ((gyy - S(240)) / S(300)) ** 2), 0, 1)
gglow = (1 - gd) ** 2.2 * 26.0
arr0 = np.asarray(img).astype(np.float64)
arr0[..., 0] = np.clip(arr0[..., 0] + gglow * 1.0, 0, 255)
arr0[..., 1] = np.clip(arr0[..., 1] + gglow * 0.55, 0, 255)
arr0[..., 2] = np.clip(arr0[..., 2] + gglow * 0.18, 0, 255)
img = Image.fromarray(arr0.astype(np.uint8), "RGB")

draw = ImageDraw.Draw(img, "RGBA")


# fBm wood-grain table in the bottom band (grounds the shot; bowl covers
# most of it, corners show). Deterministic value noise via seeded rng.
_wy0, _wy1 = int(H * 0.84), H
_wnoise = gaussian_filter(npr.random((_wy1 - _wy0, W)), sigma=6)
_yy = np.arange(_wy0, _wy1)[:, None].astype(np.float64)
_wood = np.sin(_yy * 0.055 + _wnoise * 9.0)
_wt = (_wood - _wood.min()) / (_wood.max() - _wood.min())
_wcol = np.zeros((_wy1 - _wy0, W, 3), dtype=np.float64)
for _ci, (_lo, _hi) in enumerate([(52, 118), (32, 76), (14, 38)]):
    _wcol[..., _ci] = _lo + (_hi - _lo) * _wt
_fade = np.clip((np.arange(_wy0, _wy1) - _wy0) / 60.0, 0, 1)[:, None, None]
_arr = np.asarray(img).astype(np.float64)
_arr[_wy0:_wy1] = _arr[_wy0:_wy1] * (1 - 0.55 * _fade) + _wcol * (0.55 * _fade)
img = Image.fromarray(np.clip(_arr, 0, 255).astype(np.uint8), "RGB")

# -------------------------------------------------------------------- bowl --
# 3/4 angle: bowl big in frame, center slightly below middle.
BCX, BCY = S(512), S(700)
BRX, BRY = S(432), S(286)
body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
for i in range(BRY * 2):
    y = BCY - BRY + i
    t = i / (BRY * 2)
    # richer lacquer: bright red shoulder -> deep oxblood base
    c = lerp((178, 52, 34), (58, 16, 11), t)
    bd.line([(BCX - BRX, y), (BCX + BRX, y)], fill=rgba(c, 255))
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.ellipse([BCX - BRX, BCY - BRY, BCX + BRX, BCY + BRY], fill=255)
body.putalpha(Image.composite(body.split()[3], Image.new("L", (W, H), 0), mask))
img.paste(body, (0, 0), body)

# Key-light rim: bright warm edge on the bowl's upper-left shoulder.
hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
soft_ellipse(hl, [S(150), S(470), S(330), S(820)], rgba((255, 170, 110), 85),
             S(30))
soft_ellipse(hl, [S(700), S(760), S(900), S(900)], rgba((255, 140, 80), 50),
             S(34))
img.paste(hl, (0, 0), hl)

# Decorative cream stripe + gold line low on the body.
draw = ImageDraw.Draw(img, "RGBA")
ellipse_ring(draw, BCX, S(758), S(418), S(248), S(10), (240, 222, 184), 235)
ellipse_ring(draw, BCX, S(780), S(420), S(252), S(4), (216, 168, 86), 230)
# Bowl foot.
draw.ellipse([S(438), S(940), S(586), S(982)], fill=rgba((42, 11, 8), 255))
draw.ellipse([S(446), S(940), S(578), S(974)], fill=rgba((76, 24, 15), 255))

# Rim: thick cream ring with a gold line.
ellipse_ring(draw, BCX, S(585), S(402), S(230), S(18), (248, 234, 202), 255)
ellipse_ring(draw, BCX, S(585), S(390), S(218), S(4), (208, 160, 78), 255)
# Inner rim shadow (broth sits inside this).
ellipse_ring(draw, BCX, S(585), S(378), S(206), S(7), (96, 44, 18), 170)

# ------------------------------------------------------------------- broth --
PCX, PCY = S(512), S(585)
PRX, PRY = S(378), S(212)
# Radial broth gradient via numpy: bright golden heart (key light
# upper-left) -> deep amber edge, with per-pixel grain for liquid texture.
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
nx = (xx - PCX) / PRX
ny = (yy - PCY) / PRY
d = np.clip(np.sqrt(nx * nx + ny * ny), 0, 1)
# key light offset: brightness peaks upper-left of center
lx = (xx - (PCX - S(90))) / (PRX * 1.5)
ly = (yy - (PCY - S(70))) / (PRY * 1.5)
dl = np.clip(np.sqrt(lx * lx + ly * ly), 0, 1)
base = np.zeros((H, W, 3), dtype=np.float64)
heart = np.array([247, 180, 68], dtype=np.float64)    # bright golden heart
mid = np.array([210, 130, 34], dtype=np.float64)      # amber
edge = np.array([134, 68, 16], dtype=np.float64)      # deep edge
t = d[..., None]
broth_arr = heart * (1 - t) ** 1.6 + mid * (1 - (1 - t) ** 1.6) * (1 - t) + edge * t
light = (1 - dl)[..., None] * 38.0
broth_arr = broth_arr + light
# fine grain so the surface reads as liquid, not plastic
grain = npr.normal(0, 1.5, (H, W, 1))
broth_arr = broth_arr + grain
broth_arr = np.clip(broth_arr, 0, 255).astype(np.uint8)
broth_img = Image.fromarray(broth_arr, "RGB")
bmask = Image.new("L", (W, H), 0)
bmd = ImageDraw.Draw(bmask)
bmd.ellipse([PCX - PRX, PCY - PRY, PCX + PRX, PCY + PRY], fill=255)
img.paste(broth_img, (0, 0), bmask)

# Oil sheen: glossy pools with bright specular dots.
sheen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(sheen)
for (sx, sy, sr, a) in [(400, 525, 105, 85), (650, 625, 125, 75),
                        (520, 665, 95, 65), (325, 625, 70, 60),
                        (710, 525, 65, 55)]:
    sd.ellipse([S(sx) - S(sr), S(sy) - S(sr) // 2, S(sx) + S(sr),
                S(sy) + S(sr) // 2], fill=rgba((252, 200, 96), a))
sheen = sheen.filter(ImageFilter.GaussianBlur(S(18)))
sheen = Image.composite(sheen, Image.new("RGBA", (W, H), (0, 0, 0, 0)), bmask)
img.paste(sheen, (0, 0), sheen)
# Key-light specular arc on the broth (upper-left crescent).
spec = Image.new("RGBA", (W, H), (0, 0, 0, 0))
spd = ImageDraw.Draw(spec)
spd.arc([S(225), S(420), S(570), S(585)], start=195, end=330,
        fill=rgba((255, 228, 165), 195), width=int(S(18)))
spd.arc([S(610), S(645), S(850), S(750)], start=10, end=80,
        fill=rgba((255, 212, 135), 110), width=int(S(12)))
spec = spec.filter(ImageFilter.GaussianBlur(S(10)))
spec = Image.composite(spec, Image.new("RGBA", (W, H), (0, 0, 0, 0)), bmask)
img.paste(spec, (0, 0), spec)

# ----------------------------------------------------------------- noodles --
# The nest: thick strands flowing TANGENTIALLY around the nest center,
# like a chef's folded portion — organized swirl, not random spaghetti.
# Each strand 4 passes: shadow, wheat body, bright top highlight,
# wet gloss streak (broth-coated look).
NCX, NCY = S(468), S(585)          # nest center (left of bowl center)
NRX, NRY = S(232), S(140)          # nest radii
nood = Image.new("RGBA", (W, H), (0, 0, 0, 0))
nd = ImageDraw.Draw(nood)

wheat = [(236, 198, 110), (226, 182, 88), (244, 212, 132), (218, 168, 74)]


def nest_strand(cx, cy, rx, ry, a0, sweep, waves, amp, phase):
    """A strand arcing around (cx,cy): angle a0 -> a0+sweep, with waves."""
    pts = []
    steps = 30
    for i in range(steps + 1):
        t = i / steps
        a = a0 + sweep * t
        # radius wobbles so strands cross and nest
        r = 1.0 + 0.10 * math.sin(2 * math.pi * waves * t + phase)
        x = cx + rx * r * math.cos(a)
        y = cy + ry * r * math.sin(a)
        # small perpendicular wiggle for a hand-folded feel
        x += amp * math.sin(2 * math.pi * (waves + 1) * t + phase * 1.3) * math.sin(a)
        y += amp * 0.7 * math.sin(2 * math.pi * waves * t + phase) * math.cos(a)
        pts.append((x, y))
    return pts


def draw_strand(pts, wdt, col):
    nd.line(pts, fill=rgba((146, 100, 34), 210), width=int(wdt + 4 * SS),
            joint="curve")
    nd.line(pts, fill=rgba(col, 255), width=int(wdt), joint="curve")
    hi = [(x - 2 * SS, y - 3 * SS) for (x, y) in pts]
    nd.line(hi, fill=rgba((252, 230, 166), 230), width=max(2, int(wdt * 0.38)),
            joint="curve")
    gl = [(x - 1 * SS, y - 4 * SS) for (x, y) in pts]
    nd.line(gl, fill=rgba((255, 246, 210), 150), width=max(1, int(wdt * 0.16)),
            joint="curve")


# Outer swirl ring: long smooth curves, gentle wiggle only.
for _ in range(48):
    a0 = rng.uniform(0, 2 * math.pi)
    sweep = rng.uniform(1.2, 3.4) * rng.choice([1, 1, -1])
    waves = rng.uniform(0.6, 1.4)
    amp = rng.uniform(3, 7) * SS
    ph = rng.uniform(0, 6.28)
    wdt = rng.uniform(13, 18) * SS
    draw_strand(nest_strand(NCX, NCY, NRX, NRY, a0, sweep, waves, amp, ph),
                wdt, rng.choice(wheat))
# Inner swirl: smaller radii so the nest has a full center, not a hole.
for _ in range(30):
    a0 = rng.uniform(0, 2 * math.pi)
    sweep = rng.uniform(1.4, 3.6) * rng.choice([1, 1, -1])
    waves = rng.uniform(0.6, 1.4)
    amp = rng.uniform(3, 6) * SS
    ph = rng.uniform(0, 6.28)
    wdt = rng.uniform(12, 17) * SS
    rr = rng.uniform(0.35, 0.7)
    draw_strand(nest_strand(NCX, NCY, NRX * rr, NRY * rr, a0, sweep, waves,
                            amp, ph), wdt, rng.choice(wheat))
# Crossing strands through the middle so no bare broth shows.
for _ in range(14):
    x0 = NCX + rng.uniform(-NRX, NRX) * 0.7
    y0 = NCY + rng.uniform(-NRY, NRY) * 0.7
    leng = rng.uniform(120, 220) * SS
    dang = rng.uniform(0, 2 * math.pi)
    dx, dy = leng * math.cos(dang), leng * math.sin(dang) * 0.6
    pts = []
    for i in range(21):
        t = i / 20
        x = x0 + dx * t + S(4) * math.sin(t * 6 + i)
        y = y0 + dy * t + S(2) * math.sin(t * 5)
        pts.append((x, y))
    draw_strand(pts, rng.uniform(12, 16) * SS, rng.choice(wheat))
# A few loose strands spilling over the nest edge toward the egg/chashu.
for _ in range(10):
    x0 = NCX + rng.uniform(-NRX, NRX) * 0.9
    y0 = NCY + rng.uniform(-NRY, NRY) * 0.9
    leng = rng.uniform(90, 170) * SS
    dang = rng.uniform(0, 2 * math.pi)
    dx, dy = leng * math.cos(dang), leng * math.sin(dang) * 0.6
    pts = []
    for i in range(21):
        t = i / 20
        x = x0 + dx * t + S(4) * math.sin(t * 6 + i)
        y = y0 + dy * t + S(2) * math.sin(t * 5)
        pts.append((x, y))
    draw_strand(pts, rng.uniform(12, 16) * SS, rng.choice(wheat))
nood = Image.composite(nood, Image.new("RGBA", (W, H), (0, 0, 0, 0)), bmask)
img.paste(nood, (0, 0), nood)

# ------------------------------------------------------------ toppings ------
def drop_shadow(cx, cy, rx, ry, alpha=95, blur=10):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    soft_ellipse(sh, [cx - rx, cy - ry + S(7), cx + rx, cy + ry + S(7)],
                 rgba((28, 11, 4), alpha), S(blur))
    img.paste(sh, (0, 0), sh)


draw = ImageDraw.Draw(img, "RGBA")

# --- green onion rings: FEWER, BIGGER, crisp ---
draw = ImageDraw.Draw(img, "RGBA")
for _ in range(14):
    ang = rng.uniform(0, 2 * math.pi)
    rr = rng.uniform(0.15, 0.92)
    x = PCX + PRX * rr * math.cos(ang)
    y = PCY + PRY * rr * math.sin(ang)
    r = rng.uniform(10, 15) * SS
    draw.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85],
                 fill=rgba((40, 132, 52), 255))
    draw.ellipse([x - r * 0.55, y - r * 0.45, x + r * 0.55, y + r * 0.45],
                 fill=rgba((132, 212, 126), 255))
    draw.ellipse([x - r * 0.22, y - r * 0.2, x + r * 0.22, y + r * 0.2],
                 fill=rgba((26, 84, 34), 255))

# --- sesame seeds: fewer, bigger ---
for _ in range(16):
    ang = rng.uniform(0, 2 * math.pi)
    rr = rng.uniform(0.1, 0.9)
    x = PCX + PRX * rr * math.cos(ang)
    y = PCY + PRY * rr * math.sin(ang)
    c = rng.choice([(246, 240, 222), (42, 30, 20)])
    draw.ellipse([x - S(6), y - S(3), x + S(6), y + S(3)], fill=rgba(c, 235))

# --- chili oil: glossy red pools with specular dots ---
for (cx, cy, r) in [(S(470), S(520), S(13)), (S(590), S(690), S(15)),
                    (S(300), S(600), S(11)), (S(690), S(600), S(12))]:
    draw.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8],
                 fill=rgba((198, 48, 18), 240))
    draw.ellipse([cx - r * 0.5, cy - r * 0.55, cx + r * 0.05, cy - r * 0.1],
                 fill=rgba((255, 156, 116), 230))

# --- THE hero egg: one BIG jammy half, front-center-left ---
def egg_big(cx, cy, rx, ry):
    drop_shadow(cx, cy, rx, ry, alpha=110, blur=12)
    d = ImageDraw.Draw(img, "RGBA")
    # white: soft radial gradient, slightly translucent rim
    for r in range(12, -1, -1):
        t = r / 12.0
        c = lerp((254, 240, 214), (232, 206, 164), t)
        d.ellipse([cx - rx * t, cy - ry * t, cx + rx * t, cy + ry * t],
                  fill=rgba(c, 255))
    # yolk: big, radial — bright orange heart -> deep amber rim
    yx, yy, yr = cx + S(4), cy - S(2), S(60)
    for r in range(14, -1, -1):
        t = r / 14.0
        c = lerp((255, 176, 56), (212, 96, 12), t)
        d.ellipse([yx - yr * t, yy - yr * t * 0.94, yx + yr * t, yy + yr * t * 0.94],
                  fill=rgba(c, 255))
    # molten center glow
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    soft_ellipse(g, [yx - S(22), yy - S(20), yx + S(22), yy + S(20)],
                 rgba((255, 190, 90), 170), S(10))
    img.paste(g, (0, 0), g)
    # glossy specular on the yolk
    g2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    soft_ellipse(g2, [yx - S(26), yy - S(30), yx - S(2), yy - S(10)],
                 rgba((255, 228, 160), 230), S(7))
    img.paste(g2, (0, 0), g2)


egg_big(S(385), S(672), S(118), S(90))

# --- chashu: 2 LARGE slices, front-right, seared char streaks ---
def chashu(cx, cy, r):
    drop_shadow(cx, cy, r, r * 0.92, alpha=110, blur=12)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([cx - r, cy - r * 0.92, cx + r, cy + r * 0.92],
              fill=rgba((118, 54, 28), 255))
    d.ellipse([cx - r * 0.84, cy - r * 0.78, cx + r * 0.84, cy + r * 0.78],
              fill=rgba((238, 176, 150), 255))
    d.ellipse([cx - r * 0.56, cy - r * 0.52, cx + r * 0.56, cy + r * 0.52],
              fill=rgba((248, 208, 184), 255))
    # white fat marbling arcs
    d.arc([cx - r * 0.64, cy - r * 0.59, cx + r * 0.64, cy + r * 0.59],
          start=185, end=355, fill=rgba((252, 232, 212), 240), width=int(S(10)))
    d.arc([cx - r * 0.40, cy - r * 0.37, cx + r * 0.40, cy + r * 0.37],
          start=15, end=165, fill=rgba((252, 232, 212), 215), width=int(S(7)))
    # subtle seared edge: dark crescents hugging the rim only
    d.arc([cx - r * 0.97, cy - r * 0.9, cx + r * 0.97, cy + r * 0.9],
          start=200, end=320, fill=rgba((88, 38, 16), 170), width=int(S(7)))
    d.arc([cx - r * 0.97, cy - r * 0.9, cx + r * 0.97, cy + r * 0.9],
          start=20, end=110, fill=rgba((88, 38, 16), 140), width=int(S(6)))
    # gloss
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    soft_ellipse(g, [cx - S(34), cy - S(36), cx + S(12), cy - S(8)],
                 rgba((255, 214, 184), 150), S(9))
    img.paste(g, (0, 0), g)


chashu(S(748), S(692), S(98))
chashu(S(798), S(590), S(80))

# --- narutomaki (two, pink spiral, smaller so they don't clutter) ---
def naruto(cx, cy, r):
    drop_shadow(cx, cy, r, r, alpha=80, blur=8)
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


naruto(S(565), S(748), S(32))
naruto(S(478), S(738), S(27))

# (menma removed in v3: the two bars floated on the nest and read as
# stray sticks; egg + chashu + narutomaki carry the toppings.)

# --- nori: ONE large sheet standing at the back-left, glossy sheen ---
def nori(cx, cy, w, h, ang):
    # Curved sheet leaning on the rim, bottom edge dipped in broth:
    # top edge bows outward, sides taper — reads as nori, not a card.
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    top, bot = [], []
    for i in range(25):
        t = i / 24
        x = cx - w + 2 * w * t
        top.append((x, cy - h + S(10) * math.sin(t * math.pi) - S(4) * t))
        bot.append((x, cy + h - S(6) * math.sin(t * math.pi)))
    d.polygon(top + bot[::-1], fill=rgba((16, 38, 26), 255))
    # vertical fiber lines following the curve
    for gx in range(-2, 3):
        x0 = cx + gx * w // 2
        d.line([(x0, cy - h + S(8)), (x0 + S(3), cy + h - S(8))],
               fill=rgba((44, 84, 58), 170), width=int(S(2)))
    # glossy sheen stripe on the left third
    d.polygon([(cx - w + S(6), cy - h + S(10)), (cx - w + S(20), cy - h + S(6)),
               (cx - w + S(24), cy + h - S(8)), (cx - w + S(10), cy + h - S(6))],
              fill=rgba((110, 152, 112), 110))
    layer = layer.rotate(ang, center=(cx, cy), resample=Image.BICUBIC)
    img.paste(layer, (0, 0), layer)


nori(S(318), S(478), S(42), S(58), 14)

# --- LIFTED NOODLE BUNDLE: the hero — big, glossy, draping from the
#     chopsticks at top-right down into the broth, with broth drip ---
lift = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(lift)
tip = (S(712), S(300))
base = (S(730), S(610))
for k in range(16):
    off = (k - 7.5) * S(9)
    mid = (S(766) + off, S(445))
    pts = []
    for i in range(25):
        t = i / 24
        x = (1 - t) ** 2 * (base[0] + off) + 2 * (1 - t) * t * mid[0] + t ** 2 * tip[0]
        y = (1 - t) ** 2 * base[1] + 2 * (1 - t) * t * mid[1] + t ** 2 * tip[1]
        x += S(14) * math.sin(t * 8 + k * 0.9)
        pts.append((x, y))
    wdt = rng.uniform(12, 16) * SS
    col = rng.choice(wheat)
    ld.line(pts, fill=rgba((146, 100, 34), 210), width=int(wdt + 4 * SS),
            joint="curve")
    ld.line(pts, fill=rgba(col, 255), width=int(wdt), joint="curve")
    ld.line([(x - 2 * SS, y - 3 * SS) for (x, y) in pts],
            fill=rgba((252, 230, 166), 235), width=max(2, int(wdt * 0.4)),
            joint="curve")
    ld.line([(x - 1 * SS, y - 4 * SS) for (x, y) in pts],
            fill=rgba((255, 246, 210), 160), width=max(1, int(wdt * 0.18)),
            joint="curve")
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
    sh = [(x + S(5), y + S(7)) for (x, y) in pts]
    d.polygon(sh, fill=rgba((20, 8, 4), 110))
    for t in [1.0, 0.7, 0.4]:
        c = lerp((190, 144, 82), (126, 84, 40), 1 - t)
        inset = (1 - t) * 0.28
        p = [(pts[0][0] + (pts[3][0] - pts[0][0]) * inset,
              pts[0][1] + (pts[3][1] - pts[0][1]) * inset),
             (pts[1][0] + (pts[2][0] - pts[1][0]) * inset,
              pts[1][1] + (pts[2][1] - pts[1][1]) * inset),
             pts[2], pts[3]]
        d.polygon(p, fill=rgba(c, 255))
    d.line([pts[0], pts[1]], fill=rgba((236, 194, 134), 200), width=int(S(3)))


chopstick(S(760), S(120), S(712), S(300), S(22), S(12))
chopstick(S(804), S(140), S(738), S(314), S(22), S(12))

# ------------------------------------------------------------------- steam --
# 6 strong columns, brighter, rising into the top third.
steam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(steam)
for (sx, amp, ph, a) in [(360, 32, 0.0, 150), (440, 38, 1.1, 140),
                         (520, 30, 2.2, 145), (600, 36, 3.3, 130),
                         (680, 28, 4.4, 125), (300, 26, 5.2, 115)]:
    pts = []
    for i in range(45):
        t = i / 44
        x = S(sx) + S(amp) * math.sin(t * 7.0 + ph)
        y = S(520) - t * S(440)
        pts.append((x, y))
    sd.line(pts, fill=rgba((255, 250, 240), a), width=int(S(30)), joint="curve")
steam = steam.filter(ImageFilter.GaussianBlur(S(15)))
img.paste(steam, (0, 0), steam)
steam2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd2 = ImageDraw.Draw(steam2)
for (sx, amp, ph, a) in [(410, 22, 0.7, 105), (570, 24, 2.9, 100),
                         (650, 20, 4.8, 95)]:
    pts = []
    for i in range(45):
        t = i / 44
        x = S(sx) + S(amp) * math.sin(t * 9 + ph)
        y = S(510) - t * S(410)
        pts.append((x, y))
    sd2.line(pts, fill=rgba((255, 252, 244), a), width=int(S(16)), joint="curve")
steam2 = steam2.filter(ImageFilter.GaussianBlur(S(9)))
img.paste(steam2, (0, 0), steam2)

# ------------------------------------------- table garnish + final grade -----
draw = ImageDraw.Draw(img, "RGBA")
for _ in range(7):
    x = rng.uniform(90, 934) * SS
    y = rng.uniform(950, 990) * SS
    r = rng.uniform(6, 9) * SS
    draw.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85],
                 fill=rgba((46, 139, 58), 200))
    draw.ellipse([x - r * 0.5, y - r * 0.4, x + r * 0.5, y + r * 0.4],
                 fill=rgba((126, 208, 122), 200))

# Vignette: darken edges, keep the bowl bright.
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W * 0.22, -H * 0.22, W * 1.22, H * 1.22], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(S(150)))
dark = Image.new("RGB", (W, H), (10, 5, 2))
img = Image.composite(img, dark, vig)

# Warm grade + fine film grain (photographic feel) via numpy.
arr = np.asarray(img).astype(np.float64)
arr[..., 0] = np.clip(arr[..., 0] * 1.08 + 5, 0, 255)   # warm red lift
arr[..., 1] = np.clip(arr[..., 1] * 1.02, 0, 255)
arr[..., 2] = np.clip(arr[..., 2] * 0.96, 0, 255)       # cool blue down
arr += npr.normal(0, 0.0, arr.shape)                    # film grain (off: PNG size)
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

# Downscale, light unsharp for 300px crispness, and save.
img = img.resize((OUT, OUT), Image.LANCZOS)
img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
img.save("entry.png", optimize=True, compress_level=9)
print("wrote entry.png")
