#!/usr/bin/env python3
"""Turn a text pixel-art recipe into a PNG sprite (sheet) + frame metadata JSON.

Pure Python standard library.

Usage:
    python3 pixel_sprite.py recipe.json -o assets/art/sprites/char_slime_idle.png
    python3 pixel_sprite.py recipe.json -o out.png --preview out_preview.png

Recipe:
{
  "name": "char_slime_idle",
  "palette": { ".": "transparent", "k": "#1a1c2c", "g": "#38b764", "w": "#f4f4f4" },
  "symmetric": "odd",            # optional: rows give the LEFT half (incl. centre col); mirrored to the right
  "outline": "#1a1c2c",          # optional: auto 1px outline around opaque pixels (needs a transparent border)
  "scale": 1,                    # integer nearest-neighbour upscale of the final sheet
  "columns": 4,                  # frames per row in the sheet (default: all in one row)
  "frames": [
    { "duration_ms": 120, "rows": ["..kkk..", ".kgggk.", ...] },
    ...
  ]
}
Every frame must have the same width and height. A frame may also be given
as a plain list of rows. "copy": N reuses frame N, "shift": [dx, dy] offsets it.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _png import write_png, hex_to_rgb  # noqa: E402

TRANSPARENT = (0, 0, 0, 0)


def parse_palette(pal):
    out = {}
    for k, v in pal.items():
        if len(k) != 1:
            sys.exit("palette key '%s' must be a single character" % k)
        if v in ("transparent", "none", None):
            out[k] = TRANSPARENT
        else:
            c = hex_to_rgb(v)
            out[k] = c if len(c) == 4 else c + (255,)
    return out


def expand_rows(rows, symmetric):
    if not symmetric:
        return rows
    out = []
    for r in rows:
        mirror = r[::-1] if symmetric == "even" else r[:-1][::-1]
        out.append(r + mirror)
    return out


def frame_pixels(rows, pal, name):
    h, w = len(rows), len(rows[0])
    px = []
    for y, r in enumerate(rows):
        if len(r) != w:
            sys.exit("%s: row %d is %d wide, expected %d" % (name, y, len(r), w))
        for x, ch in enumerate(r):
            if ch not in pal:
                sys.exit("%s: row %d col %d uses '%s', which is not in the palette" % (name, y, x, ch))
            px.append(pal[ch])
    return w, h, px


def add_outline(w, h, px, colour):
    out = list(px)
    for y in range(h):
        for x in range(w):
            if px[y * w + x][3] != 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[ny * w + nx][3] != 0:
                    out[y * w + x] = colour
                    break
    return out


def shift(w, h, px, dx, dy):
    out = [TRANSPARENT] * (w * h)
    for y in range(h):
        for x in range(w):
            sx, sy = x - dx, y - dy
            if 0 <= sx < w and 0 <= sy < h:
                out[y * w + x] = px[sy * w + sx]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipe")
    ap.add_argument("-o", "--out", required=True, help="output sprite sheet .png")
    ap.add_argument("--preview", help="also write an 8x enlarged preview on a checkerboard")
    a = ap.parse_args()
    with open(a.recipe, encoding="utf-8") as f:
        r = json.load(f)
    pal = parse_palette(r["palette"])
    sym = r.get("symmetric")
    outline = r.get("outline")
    oc = None
    if outline:
        oc = hex_to_rgb(outline)
        oc = oc if len(oc) == 4 else oc + (255,)
    frames, durations = [], []
    for i, fr in enumerate(r["frames"]):
        if isinstance(fr, list):
            fr = {"rows": fr}
        if "copy" in fr:
            src = fr["copy"]
            if not 0 <= src < len(frames):
                sys.exit("frame %d copies frame %s, which does not exist yet" % (i, src))
            w, h, px = frames[src]
        else:
            w, h, px = frame_pixels(expand_rows(fr["rows"], sym), pal, "frame %d" % i)
            if oc:
                px = add_outline(w, h, px, oc)
        if "shift" in fr:
            px = shift(w, h, px, fr["shift"][0], fr["shift"][1])
        frames.append((w, h, px))
        durations.append(fr.get("duration_ms", r.get("duration_ms", 100)))
    fw, fh = frames[0][0], frames[0][1]
    for i, (w, h, _) in enumerate(frames):
        if (w, h) != (fw, fh):
            sys.exit("frame %d is %dx%d but frame 0 is %dx%d" % (i, w, h, fw, fh))
    cols = int(r.get("columns", len(frames)))
    rows_n = (len(frames) + cols - 1) // cols
    s = int(r.get("scale", 1))
    W, H = fw * cols * s, fh * rows_n * s
    img = bytearray(W * H * 4)
    for i, (_, _, px) in enumerate(frames):
        ox, oy = (i % cols) * fw * s, (i // cols) * fh * s
        for y in range(fh):
            for x in range(fw):
                c = bytes(px[y * fw + x])
                for yy in range(s):
                    o = ((oy + y * s + yy) * W + ox + x * s) * 4
                    img[o:o + 4 * s] = c * s
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    write_png(a.out, W, H, img, alpha=True)
    meta = {"name": r.get("name", os.path.splitext(os.path.basename(a.out))[0]),
            "image": os.path.basename(a.out), "frame_width": fw * s, "frame_height": fh * s,
            "columns": cols, "rows": rows_n, "frame_count": len(frames),
            "durations_ms": durations, "loop": r.get("loop", True),
            "fps_hint": round(1000.0 / (sum(durations) / len(durations)), 2)}
    meta_path = os.path.splitext(a.out)[0] + ".json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("wrote %s  (%dx%d, %d frames of %dx%d)" % (a.out, W, H, len(frames), fw * s, fh * s))
    print("wrote %s" % meta_path)
    if a.preview:
        z = max(1, 8 // s)
        PW, PH = W * z, H * z
        pv = bytearray(PW * PH * 3)
        for y in range(PH):
            for x in range(PW):
                bg = 220 if ((x // 8) + (y // 8)) % 2 else 200
                o = ((y // z) * W + (x // z)) * 4
                al = img[o + 3] / 255.0
                p = (y * PW + x) * 3
                pv[p:p + 3] = bytes(int(img[o + i] * al + bg * (1 - al)) for i in range(3))
        write_png(a.preview, PW, PH, pv)
        print("preview: %s" % a.preview)


if __name__ == "__main__":
    main()
