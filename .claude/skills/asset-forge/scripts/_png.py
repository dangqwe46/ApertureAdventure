"""Tiny dependency-free PNG writer and reader (8-bit RGB / RGBA).

Shared by the asset-forge scripts so none of them need Pillow.
"""
import struct
import zlib


def _chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path, width, height, pixels, alpha=False):
    """pixels: flat list/bytearray, row-major, 3 (RGB) or 4 (RGBA) bytes per pixel."""
    bpp = 4 if alpha else 3
    if len(pixels) != width * height * bpp:
        raise ValueError("pixel buffer is %d bytes, expected %d" % (len(pixels), width * height * bpp))
    buf = bytes(pixels)
    raw = bytearray()
    stride = width * bpp
    for y in range(height):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6 if alpha else 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_chunk(b"IHDR", ihdr))
        f.write(_chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(_chunk(b"IEND", b""))


def hex_to_rgb(h):
    """'#rrggbb' or '#rrggbbaa' -> tuple of ints."""
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) not in (6, 8):
        raise ValueError("bad colour '%s' (use #rrggbb)" % h)
    return tuple(int(h[i:i + 2], 16) for i in range(0, len(h), 2))
