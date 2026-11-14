#!/usr/bin/env python3
"""Draw a steaming bowl of ramen, programmatically, standard library only.

Writes entry.png (1024x1024) next to this script. Fully deterministic:
fixed seed, no time, no network, no external assets.

Scene: dark background, warm glow, ceramic bowl with golden broth,
tangled noodles, soft egg with jammy yolk, narutomaki, spring onions,
nori, chopsticks lifting noodles, gentle steam rising.
"""
import math
import struct
import zlib

W = H = 1024
buf = bytearray(W * H * 3)

# ---------------------------------------------------------------- canvas ----
def _row_fill(y, r, g, b):
    i = y * W * 3
    buf[i:i + W * 3] = bytes((r, g, b)) * W


def blend(x, y, r, g, b, a):
    """Blend color (r,g,b) with alpha a (0..1) onto pixel (x,y)."""
    if a <= 0.0 or x < 0 or x >= W or y < 0 or y >= H:
        return
    if a >= 1.0:
        i = (y * W + x) * 3
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b
        return
    i = (y * W + x) * 3
    ia = 1.0 - a
    buf[i] = int(buf[i] * ia + r * a + 0.5)
    buf[i + 1] = int(buf[i + 1] * ia + g * a + 0.5)
    buf[i + 2] = int(buf[i + 2] * ia + b * a + 0.5)


def lerp(a, b, t):
    return a + (b - a) * t


def fill_ellipse(cx, cy, rx, ry, c_top, c_bot, alpha=1.0):
    """Vertical-gradient ellipse."""
    y0 = max(0, int(cy - ry))
    y1 = min(H - 1, int(cy + ry))
    for y in range(y0, y1 + 1):
        dy = (y - cy) / ry
        s = 1.0 - dy * dy
        if s <= 0:
            continue
        dx = rx * math.sqrt(s)
        t = (y - (cy - ry)) / (2.0 * ry)
        r = int(lerp(c_top[0], c_bot[0], t))
        g = int(lerp(c_top[1], c_bot[1], t))
        b = int(lerp(c_top[2], c_bot[2], t))
        x0 = max(0, int(cx - dx))
        x1 = min(W - 1, int(cx + dx))
        for x in range(x0, x1 + 1):
            blend(x, y, r, g, b, alpha)


def radial_ellipse(cx, cy, rx, ry, c_in, c_out, alpha=1.0):
    """Radial-gradient ellipse (center color -> edge color)."""
    y0 = max(0, int(cy - ry))
    y1 = min(H - 1, int(cy + ry))
    x0 = max(0, int(cx - rx))
    x1 = min(W - 1, int(cx + rx))
    for y in range(y0, y1 + 1):
        dy = (y - cy) / ry
        for x in range(x0, x1 + 1):
            dx = (x - cx) / rx
            d = dx * dx + dy * dy
            if d <= 1.0:
                t = math.sqrt(d)
                r = int(lerp(c_in[0], c_out[0], t))
                g = int(lerp(c_in[1], c_out[1], t))
                b = int(lerp(c_in[2], c_out[2], t))
                blend(x, y, r, g, b, alpha)


def soft_ellipse(cx, cy, rx, ry, color, max_a):
    """Ellipse whose alpha fades linearly to 0 at the edge."""
    y0 = max(0, int(cy - ry))
    y1 = min(H - 1, int(cy + ry))
    x0 = max(0, int(cx - rx))
    x1 = min(W - 1, int(cx + rx))
    for y in range(y0, y1 + 1):
        dy = (y - cy) / ry
        for x in range(x0, x1 + 1):
            dx = (x - cx) / rx
            d = dx * dx + dy * dy
            if d <= 1.0:
                blend(x, y, color[0], color[1], color[2], max_a * (1.0 - d))


def disc(cx, cy, r, color, alpha=1.0):
    """Solid disc."""
    r = int(r)
    y0 = max(0, cy - r)
    y1 = min(H - 1, cy + r)
    x0 = max(0, cx - r)
    x1 = min(W - 1, cx + r)
    rr = r * r
    for y in range(y0, y1 + 1):
        dy = y - cy
        for x in range(x0, x1 + 1):
            dx = x - cx
            if dx * dx + dy * dy <= rr:
                blend(x, y, color[0], color[1], color[2], alpha)


def soft_disc(cx, cy, r, color, max_a):
    """Disc with radial alpha falloff."""
    y0 = max(0, int(cy - r))
    y1 = min(H - 1, int(cy + r))
    x0 = max(0, int(cx - r))
    x1 = min(W - 1, int(cx + r))
    for y in range(y0, y1 + 1):
        dy = y - cy
        for x in range(x0, x1 + 1):
            dx = x - cx
            d2 = dx * dx + dy * dy
            if d2 <= r * r:
                d = math.sqrt(d2) / r
                blend(x, y, color[0], color[1], color[2], max_a * (1.0 - d))


def stroke(points, width, color, alpha=1.0):
    """Thick polyline: stamp discs along the path."""
    rad = max(1, width // 2)
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 3) + 1)
        for s in range(steps + 1):
            t = s / steps
            x = int(x0 + (x1 - x0) * t)
            y = int(y0 + (y1 - y0) * t)
            disc(x, y, rad, color, alpha)


def ellipse_ring(cx, cy, rx, ry, width, color, alpha=1.0):
    """Decorative ring stamped along an ellipse perimeter. Stamps are
    spaced to overlap so the ring is solid, not dotted."""
    n = max(220, int(2.0 * (rx + ry)))
    for i in range(n):
        a = 2.0 * math.pi * i / n
        x = int(cx + rx * math.cos(a))
        y = int(cy + ry * math.sin(a))
        disc(x, y, max(1, width // 2), color, alpha)


def poly_fill(pts, c_top, c_bot, alpha=1.0):
    """Scanline fill of a convex-ish polygon with a vertical gradient."""
    ys = [p[1] for p in pts]
    y0, y1 = max(0, min(ys)), min(H - 1, max(ys))
    n = len(pts)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x0, yy0 = pts[i]
            x1, yy1 = pts[(i + 1) % n]
            if (yy0 <= y < yy1) or (yy1 <= y < yy0):
                t = (y - yy0) / (yy1 - yy0)
                xs.append(x0 + (x1 - x0) * t)
        if len(xs) >= 2:
            xs.sort()
            t = (y - y0) / max(1, y1 - y0)
            r = int(lerp(c_top[0], c_bot[0], t))
            g = int(lerp(c_top[1], c_bot[1], t))
            b = int(lerp(c_top[2], c_bot[2], t))
            for x in range(max(0, int(xs[0])), min(W - 1, int(xs[-1])) + 1):
                blend(x, y, r, g, b, alpha)


# ------------------------------------------------------------- random -------
_seed = [987654321]


def rnd():
    _seed[0] = (_seed[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return _seed[0] / 0x7FFFFFFF


# ---------------------------------------------------------------- scene -----
def draw():
    # 1. Background: warm dark vertical gradient.
    for y in range(H):
        t = y / (H - 1)
        r = int(lerp(26, 10, t))
        g = int(lerp(17, 8, t))
        b = int(lerp(12, 6, t))
        _row_fill(y, r, g, b)

    # 2. Warm glow behind the bowl.
    soft_ellipse(512, 500, 430, 400, (96, 58, 26), 0.55)
    soft_ellipse(512, 520, 300, 270, (140, 88, 36), 0.35)

    # 3. Soft shadow under the bowl.
    soft_ellipse(512, 862, 350, 42, (0, 0, 0), 0.55)

    # 4. Bowl body: deep red ceramic, vertical gradient.
    fill_ellipse(512, 648, 336, 212, (150, 48, 34), (66, 16, 10))
    # Decorative cream stripe + thin gold line on the body (thin, low on
    # the body so it reads as a stripe, not a second rim).
    ellipse_ring(512, 626, 332, 200, 8, (232, 214, 176), 0.9)
    ellipse_ring(512, 646, 334, 204, 4, (212, 164, 82), 0.85)
    # Soft warm sheen on the left of the body.
    soft_ellipse(400, 700, 90, 120, (200, 90, 60), 0.12)
    # Bowl foot.
    fill_ellipse(512, 848, 118, 20, (52, 14, 9), (30, 8, 5))

    # 5. Rim: cream ceramic ring, then broth.
    fill_ellipse(512, 560, 336, 108, (243, 233, 210), (214, 196, 164))
    # Dark rim edge for definition.
    ellipse_ring(512, 560, 334, 106, 5, (92, 23, 16), 0.85)
    # Broth: golden radial gradient, bright heart, deeper edge.
    radial_ellipse(512, 560, 298, 92, (249, 195, 77), (176, 106, 20))
    # Broth gloss, upper left.
    soft_ellipse(428, 522, 96, 22, (255, 240, 190), 0.20)
    soft_ellipse(610, 600, 70, 16, (255, 220, 140), 0.10)

    # 6. Noodles: tangled wavy strokes across the broth, clipped to it.
    def in_broth(x, y):
        return ((x - 512) / 292.0) ** 2 + ((y - 560) / 88.0) ** 2 <= 1.0

    noodle_cols = [(242, 212, 146), (232, 196, 120), (250, 226, 168)]
    for i in range(46):
        # A wavy chord across the broth.
        y_base = 500 + rnd() * 120
        x0 = 240 + rnd() * 60
        x1 = 700 + rnd() * 80
        amp = 6 + rnd() * 12
        ph = rnd() * 6.28
        col = noodle_cols[i % 3]
        # shadow pass slightly below, then the strand itself.
        for dy, cc, al in ((3, (150, 105, 40), 0.5), (0, col, 0.95)):
            pts = []
            steps = 26
            for s in range(steps + 1):
                t = s / steps
                x = int(x0 + (x1 - x0) * t)
                y = int(y_base + math.sin(t * 9.0 + ph) * amp + dy)
                if in_broth(x, y):
                    pts.append((x, y))
            if len(pts) > 2:
                stroke(pts, 5, cc, al)

    # 7. Soft egg, left of centre: white + jammy yolk.
    soft_ellipse(400, 548, 70, 48, (60, 30, 8), 0.30)
    fill_ellipse(400, 544, 64, 44, (255, 250, 240), (233, 220, 196))
    radial_ellipse(400, 544, 27, 27, (255, 122, 26), (255, 179, 71))
    soft_ellipse(388, 530, 11, 7, (255, 255, 255), 0.55)

    # 8. Narutomaki (fish-cake swirl), right of centre.
    disc(628, 592, 24, (255, 250, 244), 0.95)
    disc(628, 592, 15, (245, 180, 190), 0.9)
    disc(628, 592, 7, (255, 250, 244), 0.95)
    disc(628, 592, 3, (232, 120, 140), 0.9)

    # 9. Spring onions: little green rings scattered on the broth.
    onion_spots = [(470, 505), (540, 498), (660, 520), (700, 560), (560, 610),
                   (330, 560), (360, 600), (500, 620), (740, 540)]
    for (ox, oy) in onion_spots:
        if not in_broth(ox, oy):
            continue
        disc(ox, oy, 9, (86, 158, 66), 0.95)
        disc(ox, oy, 5, (38, 96, 34), 0.95)
        disc(ox - 2, oy - 2, 2, (150, 210, 120), 0.8)

    # 10. Chili threads: thin red curves on the broth.
    for (cx0, cy0, cx1, cy1) in [(470, 580, 560, 600), (600, 520, 690, 540),
                                 (350, 520, 420, 500)]:
        pts = []
        for s in range(13):
            t = s / 12.0
            pts.append((int(cx0 + (cx1 - cx0) * t),
                        int(cy0 + (cy1 - cy0) * t + math.sin(t * 6.0) * 4)))
        stroke(pts, 3, (193, 39, 45), 0.9)

    # 11. Sesame seeds: tiny cream dots.
    for _ in range(16):
        sx = int(260 + rnd() * 500)
        sy = int(490 + rnd() * 140)
        if in_broth(sx, sy):
            disc(sx, sy, 2, (245, 230, 200), 0.85)

    # 12. Nori sheet standing at the back-right of the bowl.
    poly_fill([(706, 428), (792, 448), (776, 566), (694, 548)],
              (34, 52, 26), (14, 24, 12), 0.97)
    stroke([(716, 440), (700, 540)], 3, (120, 150, 100), 0.25)
    stroke([(740, 446), (726, 546)], 3, (120, 150, 100), 0.20)

    # 13. Chopsticks from the top-right, holding a lifted noodle tangle.
    #    Tips near (640, 470); handles up-right.
    for (tx, ty, hx, hy, wdt) in ((640, 470, 788, 148, 13),
                                  (668, 478, 818, 192, 13)):
        # shadow then wood, then a light edge line.
        stroke([(tx + 4, ty + 5), (hx + 4, hy + 5)], wdt, (40, 20, 8), 0.5)
        stroke([(tx, ty), (hx, hy)], wdt, (150, 96, 44), 0.95)
        stroke([(tx - 3, ty - 2), (hx - 3, hy - 2)], 4, (205, 150, 84), 0.7)
    # Lifted tangle: strands hanging from the tips down to the broth.
    for i in range(14):
        x_top = 640 + int(rnd() * 34)
        x_bot = 610 + int(rnd() * 70)
        amp = 8 + rnd() * 10
        ph = rnd() * 6.28
        col = noodle_cols[i % 3]
        pts = []
        for s in range(15):
            t = s / 14.0
            x = int(x_top + (x_bot - x_top) * t + math.sin(t * 7.0 + ph) * amp * t)
            y = int(468 + (556 - 468) * t)
            pts.append((x, y))
        stroke(pts, 5, col, 0.95)
        stroke([(pts[0][0] + 2, pts[0][1] + 2),
                (pts[-1][0] + 2, pts[-1][1] + 2)], 5, (150, 105, 40), 0.35)

    # 14. Steam: soft white columns rising above the bowl.
    for (bx, ph) in ((390, 0.0), (480, 1.4), (575, 2.6), (665, 3.9)):
        for step in range(56):
            t = step / 55.0
            y = int(478 - t * 360)
            x = int(bx + 26 * math.sin(t * 5.2 + ph)
                    + 9 * math.sin(t * 11.0 + ph * 2.0))
            r = 13 + int(20 * t)
            a = 0.10 * (1.0 - t * 0.75)
            soft_disc(x, y, r, (255, 250, 240), a)

    # 15. Vignette: darken the corners.
    for (vx, vy) in ((0, 0), (1024, 0), (0, 1024), (1024, 1024)):
        soft_ellipse(vx, vy, 560, 560, (0, 0, 0), 0.30)


# ------------------------------------------------------------------ png ------
def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: None
        raw += buf[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


if __name__ == "__main__":
    import os
    draw()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    size = write_png(out)
    print("wrote %s (%d bytes, %dx%d)" % (out, size, W, H))
