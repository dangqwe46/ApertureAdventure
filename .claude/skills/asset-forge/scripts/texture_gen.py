#!/usr/bin/env python3
"""Generate seamless (tileable) procedural textures as PNG, with optional normal map.

Pure Python standard library. Sizes should be powers of two (64-1024).
Large sizes are slow in pure Python (512 px takes a few seconds per octave set).

Usage:
    python3 texture_gen.py --preset grass --size 256 -o assets/art/textures/tex_grass_256.png
    python3 texture_gen.py --preset bricks --size 512 -o tex_bricks_512.png --normal tex_bricks_512_n.png
    python3 texture_gen.py --recipe my_texture.json -o out.png
    python3 texture_gen.py --list

Recipe (JSON) - any preset key can be overridden:
{
  "type": "noise" | "bricks" | "planks" | "tiles" | "cells",
  "seed": 7,
  "scale": 4,                 # base noise frequency (cells per tile)
  "octaves": 4,
  "stops": [[0.0, "#2d5a27"], [0.6, "#4f8a3a"], [1.0, "#8fbf5a"]],   # height -> colour gradient
  "mortar": "#5b524a",        # bricks / tiles / cells: gap colour
  "rows": 8, "cols": 4,       # bricks / tiles / planks layout
  "gap": 0.06,                # gap width, fraction of a brick/tile/plank
  "variation": 0.15,          # per-brick/tile/plank brightness jitter
  "detail": 0.35              # how much fine noise is mixed over the pattern
}
"""
import argparse
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _png import write_png, hex_to_rgb  # noqa: E402

PRESETS = {
    "grass":  {"type": "noise", "scale": 6, "octaves": 5,
               "stops": [[0.0, "#2c5a24"], [0.45, "#3f7a32"], [0.75, "#5d9a42"], [1.0, "#8cc05a"]]},
    "dirt":   {"type": "noise", "scale": 5, "octaves": 5,
               "stops": [[0.0, "#4a3222"], [0.5, "#6b4a30"], [0.8, "#86603f"], [1.0, "#a07a52"]]},
    "sand":   {"type": "noise", "scale": 8, "octaves": 4,
               "stops": [[0.0, "#c9a86a"], [0.5, "#dcc085"], [1.0, "#efd9a4"]]},
    "stone":  {"type": "noise", "scale": 4, "octaves": 6,
               "stops": [[0.0, "#4b4d52"], [0.5, "#6d7077"], [0.8, "#8b8e94"], [1.0, "#a9abb0"]]},
    "snow":   {"type": "noise", "scale": 5, "octaves": 4,
               "stops": [[0.0, "#c9d6e6"], [0.6, "#e6eef7"], [1.0, "#ffffff"]]},
    "water":  {"type": "noise", "scale": 3, "octaves": 4,
               "stops": [[0.0, "#123d6b"], [0.55, "#1d5f98"], [0.85, "#3b8ccc"], [1.0, "#8cc8f0"]]},
    "lava":   {"type": "noise", "scale": 3, "octaves": 5,
               "stops": [[0.0, "#2a0a06"], [0.45, "#7a1a0a"], [0.7, "#e2531a"], [0.9, "#ffb43a"], [1.0, "#fff1a0"]]},
    "bricks": {"type": "bricks", "rows": 8, "cols": 4, "gap": 0.07, "variation": 0.18, "detail": 0.3,
               "mortar": "#6e665d", "stops": [[0.0, "#7a3424"], [0.6, "#9c4a33"], [1.0, "#b8634a"]]},
    "planks": {"type": "planks", "cols": 5, "gap": 0.04, "variation": 0.2, "detail": 0.5,
               "mortar": "#2b1b10", "stops": [[0.0, "#6a4326"], [0.5, "#8a5a34"], [1.0, "#a8744a"]]},
    "tiles":  {"type": "tiles", "rows": 4, "cols": 4, "gap": 0.05, "variation": 0.12, "detail": 0.3,
               "mortar": "#3c3a38", "stops": [[0.0, "#8f8a82"], [0.6, "#aaa49a"], [1.0, "#c4beb3"]]},
    "cobble": {"type": "cells", "scale": 6, "gap": 0.08, "variation": 0.2, "detail": 0.35,
               "mortar": "#3a3633", "stops": [[0.0, "#5f5b56"], [0.6, "#7d7872"], [1.0, "#9e988f"]]},
    "scales": {"type": "cells", "scale": 10, "gap": 0.06, "variation": 0.15, "detail": 0.2,
               "mortar": "#14331f", "stops": [[0.0, "#1f5a35"], [0.6, "#2e7d4a"], [1.0, "#58a86a"]]},
}


class Noise:
    """Tileable value noise / fBm over a unit square that wraps."""

    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.tables = {}

    def lattice(self, period):
        if period not in self.tables:
            self.tables[period] = [[self.rng.random() for _ in range(period)] for _ in range(period)]
        return self.tables[period]

    def value(self, u, v, period):
        t = self.lattice(period)
        x, y = u * period, v * period
        x0, y0 = int(math.floor(x)), int(math.floor(y))
        fx, fy = x - x0, y - y0
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        x0 %= period
        y0 %= period
        x1, y1 = (x0 + 1) % period, (y0 + 1) % period
        a = t[y0][x0] + (t[y0][x1] - t[y0][x0]) * sx
        b = t[y1][x0] + (t[y1][x1] - t[y1][x0]) * sx
        return a + (b - a) * sy

    def fbm(self, u, v, scale, octaves, sx=1, sy=1):
        total, amp, norm_ = 0.0, 1.0, 0.0
        p = max(1, int(scale))
        for _ in range(octaves):
            # anisotropy via separate periods keeps the result tileable
            total += amp * self.value_aniso(u, v, p * sx, p * sy)
            norm_ += amp
            amp *= 0.5
            p *= 2
        return total / norm_

    def value_aniso(self, u, v, px, py):
        if px == py:
            return self.value(u, v, px)
        key = (px, py)
        if key not in self.tables:
            self.tables[key] = [[self.rng.random() for _ in range(px)] for _ in range(py)]
        t = self.tables[key]
        x, y = u * px, v * py
        x0, y0 = int(math.floor(x)), int(math.floor(y))
        fx, fy = x - x0, y - y0
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        x0 %= px
        y0 %= py
        x1, y1 = (x0 + 1) % px, (y0 + 1) % py
        a = t[y0][x0] + (t[y0][x1] - t[y0][x0]) * sx
        b = t[y1][x0] + (t[y1][x1] - t[y1][x0]) * sx
        return a + (b - a) * sy


def gradient(stops, h):
    h = min(1.0, max(0.0, h))
    for i in range(len(stops) - 1):
        (t0, c0), (t1, c1) = stops[i], stops[i + 1]
        if h <= t1:
            k = 0 if t1 == t0 else (h - t0) / (t1 - t0)
            return tuple(c0[j] + (c1[j] - c0[j]) * k for j in range(3))
    return stops[-1][1]


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0))) if e1 != e0 else (1.0 if x >= e1 else 0.0)
    return t * t * (3 - 2 * t)


def generate(p, size):
    rng = random.Random(p.get("seed", 1) * 7919)
    nz = Noise(p.get("seed", 1))
    stops = [(t, hex_to_rgb(c)[:3]) for t, c in p["stops"]]
    mortar = hex_to_rgb(p.get("mortar", "#333333"))[:3]
    typ = p.get("type", "noise")
    detail = p.get("detail", 0.3)
    var = p.get("variation", 0.15)
    gap = p.get("gap", 0.06)
    octaves = int(p.get("octaves", 4))
    scale = p.get("scale", 4)
    rows, cols = int(p.get("rows", 8)), int(p.get("cols", 4))
    jitter = {}

    def cell_jit(key):
        if key not in jitter:
            jitter[key] = (rng.uniform(-var, var), rng.random())
        return jitter[key]

    # tileable Voronoi feature points for "cells"
    n_cells = max(2, int(scale))
    pts = {(i, j): (rng.random(), rng.random()) for i in range(n_cells) for j in range(n_cells)}

    color = bytearray(size * size * 3)
    height = [0.0] * (size * size)
    for y in range(size):
        v = (y + 0.5) / size
        for x in range(size):
            u = (x + 0.5) / size
            fine = nz.fbm(u, v, 16, 3)
            if typ == "noise":
                h = nz.fbm(u, v, scale, octaves)
                h = min(1.0, max(0.0, (h - 0.5) * 1.6 + 0.5))
                c = gradient(stops, h)
            elif typ in ("bricks", "tiles"):
                ry = v * rows
                r = int(ry)
                off = 0.5 if (typ == "bricks" and r % 2) else 0.0
                rx = (u * cols + off) % cols
                ci = int(rx)
                fx, fy = rx - ci, ry - r
                gx = gap * (rows / cols) if typ == "bricks" else gap
                edge = min(fx, 1 - fx) / max(gx, 1e-6), min(fy, 1 - fy) / max(gap, 1e-6)
                m = smoothstep(0.5, 1.0, min(edge))
                j, _ = cell_jit((r, ci))
                body = nz.fbm(u, v, scale, octaves) * (1 - detail) + fine * detail
                body = min(1.0, max(0.0, body + j))
                bc = gradient(stops, body)
                mc = tuple(mortar[k] * (0.85 + 0.3 * fine) for k in range(3))
                c = tuple(mc[k] + (bc[k] - mc[k]) * m for k in range(3))
                h = m * (0.7 + 0.3 * body)
            elif typ == "planks":
                rx = u * cols
                ci = int(rx)
                fx = rx - ci
                m = smoothstep(0.5, 1.0, min(fx, 1 - fx) / max(gap, 1e-6))
                j, ph = cell_jit(ci)
                grain = nz.fbm(u, (v + ph) % 1.0, 2, 4, sx=cols * 4, sy=1)
                rings = 0.5 + 0.5 * math.sin((grain * 12 + fx * 3) * math.pi)
                body = min(1.0, max(0.0, 0.25 + 0.5 * rings * (1 - detail) + grain * detail + j))
                bc = gradient(stops, body)
                c = tuple(mortar[k] + (bc[k] - mortar[k]) * m for k in range(3))
                h = m * (0.8 + 0.2 * body)
            elif typ == "cells":
                gu, gv = u * n_cells, v * n_cells
                cx, cy = int(gu), int(gv)
                d1 = d2 = 1e9
                best = None
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ix, iy = cx + dx, cy + dy
                        px_, py_ = pts[(ix % n_cells, iy % n_cells)]
                        d = math.hypot(ix + px_ - gu, iy + py_ - gv)
                        if d < d1:
                            d2, d1, best = d1, d, (ix % n_cells, iy % n_cells)
                        elif d < d2:
                            d2 = d
                m = smoothstep(gap, gap * 2.5, d2 - d1)
                j, _ = cell_jit(best)
                body = min(1.0, max(0.0, 0.55 - d1 * 0.5 + fine * detail + j))
                bc = gradient(stops, body)
                c = tuple(mortar[k] + (bc[k] - mortar[k]) * m for k in range(3))
                h = m * (0.6 + 0.4 * (1 - d1))
            else:
                sys.exit("unknown texture type '%s'" % typ)
            o = (y * size + x) * 3
            color[o:o + 3] = bytes(int(min(255, max(0, ch))) for ch in c)
            height[y * size + x] = h
    return color, height


def normal_map(height, size, strength):
    out = bytearray(size * size * 3)
    for y in range(size):
        for x in range(size):
            l = height[y * size + (x - 1) % size]
            r = height[y * size + (x + 1) % size]
            u = height[((y - 1) % size) * size + x]
            d = height[((y + 1) % size) * size + x]
            nx, ny, nz = (l - r) * strength, (d - u) * strength, 1.0   # OpenGL-style (Y+), as Godot expects
            ln = math.sqrt(nx * nx + ny * ny + nz * nz)
            o = (y * size + x) * 3
            out[o:o + 3] = bytes(int((c / ln * 0.5 + 0.5) * 255) for c in (nx, ny, nz))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preset", choices=sorted(PRESETS))
    ap.add_argument("--recipe", help="JSON recipe (may set 'preset' to start from one)")
    ap.add_argument("--size", type=int, default=256)
    ap.add_argument("--seed", type=int)
    ap.add_argument("-o", "--out")
    ap.add_argument("--normal", help="also write a tangent-space normal map (OpenGL / Y+ convention)")
    ap.add_argument("--normal-strength", type=float, default=4.0)
    ap.add_argument("--list", action="store_true", help="list presets")
    a = ap.parse_args()
    if a.list:
        for k in sorted(PRESETS):
            print("%-8s %s" % (k, PRESETS[k]["type"]))
        return
    if not a.out:
        sys.exit("give -o OUT.png")
    p = {}
    if a.recipe:
        with open(a.recipe, encoding="utf-8") as f:
            rec = json.load(f)
        if rec.get("preset"):
            p.update(PRESETS[rec["preset"]])
        p.update(rec)
    elif a.preset:
        p.update(PRESETS[a.preset])
    else:
        sys.exit("give --preset or --recipe (see --list)")
    if a.seed is not None:
        p["seed"] = a.seed
    if a.size & (a.size - 1):
        print("warning: %d is not a power of two; most engines prefer 64/128/256/512/1024" % a.size)
    color, height = generate(p, a.size)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    write_png(a.out, a.size, a.size, color)
    print("wrote %s  (%dx%d, seamless)" % (a.out, a.size, a.size))
    if a.normal:
        write_png(a.normal, a.size, a.size, normal_map(height, a.size, a.normal_strength))
        print("wrote %s  (normal map, OpenGL/Y+)" % a.normal)


if __name__ == "__main__":
    main()
