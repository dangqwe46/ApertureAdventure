#!/usr/bin/env python3
"""Rasterise an SVG to PNG with whatever converter is installed.

Godot 4 imports .svg directly, so this is only needed when the engine or the
spec wants PNG (Unity, Three.js textures, itch.io page art, previews).

Tries, in order: rsvg-convert, inkscape, magick/convert (ImageMagick), cairosvg (Python).

Usage:
    python3 svg_raster.py icon.svg -o icon_64.png --size 64
    python3 svg_raster.py icon.svg -o icon.png --width 256 --height 128
"""
import argparse
import shutil
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--size", type=int, help="square output size in px")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    a = ap.parse_args()
    w = a.width or a.size
    h = a.height or a.size
    if shutil.which("rsvg-convert"):
        cmd = ["rsvg-convert", a.svg, "-o", a.out] + (["-w", str(w)] if w else []) + (["-h", str(h)] if h else [])
    elif shutil.which("inkscape"):
        cmd = ["inkscape", a.svg, "--export-type=png", "--export-filename=" + a.out]
        cmd += (["-w", str(w)] if w else []) + (["-h", str(h)] if h else [])
    elif shutil.which("magick") or shutil.which("convert"):
        tool = "magick" if shutil.which("magick") else "convert"
        cmd = [tool, "-background", "none", a.svg] + (["-resize", "%dx%d" % (w or h, h or w)] if (w or h) else []) + [a.out]
    else:
        try:
            import cairosvg
        except ImportError:
            sys.exit("NOT RASTERISED: no SVG converter found. Install one of: rsvg-convert (librsvg), "
                     "Inkscape, ImageMagick, or `pip install cairosvg`. Godot can import the .svg directly.")
        cairosvg.svg2png(url=a.svg, write_to=a.out, output_width=w, output_height=h)
        print("wrote %s (cairosvg)" % a.out)
        return
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("converter failed: %s\n%s" % (" ".join(cmd), r.stderr))
    print("wrote %s (%s)" % (a.out, cmd[0]))


if __name__ == "__main__":
    main()
