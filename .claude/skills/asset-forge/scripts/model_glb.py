#!/usr/bin/env python3
"""Build a low-poly 3D model (.glb) from a JSON recipe, plus a PNG preview.

Pure Python standard library. The .glb (glTF 2.0 binary) imports directly into
Godot 4, Unity (glTFast / UnityGLTF), Unreal, Blender and Three.js.

Usage:
    python3 model_glb.py recipe.json -o assets/art/models/prop_crate.glb
    python3 model_glb.py recipe.json -o out.glb --preview out_preview.png
    python3 model_glb.py recipe.json --preview-only out_preview.png

Recipe format: see references/model-recipes.md. Units are metres, +Y is up,
the model's front faces +Z (glTF convention).
"""
import argparse
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _png import write_png, hex_to_rgb  # noqa: E402


# ---------------------------------------------------------------- vector math
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def scale3(a, s): return (a[0] * s, a[1] * s, a[2] * s)


def norm(a):
    l = math.sqrt(dot(a, a))
    return (0.0, 1.0, 0.0) if l < 1e-12 else (a[0] / l, a[1] / l, a[2] / l)


def quat_from_euler(deg):
    """Euler degrees [x, y, z], applied X then Y then Z. Returns (x, y, z, w)."""
    def axis_q(axis, d):
        h = math.radians(d) / 2
        s = math.sin(h)
        v = [0.0, 0.0, 0.0]
        v[axis] = s
        return (v[0], v[1], v[2], math.cos(h))

    def qmul(a, b):
        ax, ay, az, aw = a
        bx, by, bz, bw = b
        return (aw * bx + ax * bw + ay * bz - az * by,
                aw * by - ax * bz + ay * bw + az * bx,
                aw * bz + ax * by - ay * bx + az * bw,
                aw * bw - ax * bx - ay * by - az * bz)

    qx, qy, qz = axis_q(0, deg[0]), axis_q(1, deg[1]), axis_q(2, deg[2])
    return qmul(qz, qmul(qy, qx))


def mat_from_trs(t, q, s):
    x, y, z, w = q
    r = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
         [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
         [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    m = [[r[i][j] * s[j] for j in range(3)] + [t[i]] for i in range(3)]
    m.append([0.0, 0.0, 0.0, 1.0])
    return m


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def mat_apply(m, p):
    return (m[0][0] * p[0] + m[0][1] * p[1] + m[0][2] * p[2] + m[0][3],
            m[1][0] * p[0] + m[1][1] * p[1] + m[1][2] * p[2] + m[1][3],
            m[2][0] * p[0] + m[2][1] * p[1] + m[2][2] * p[2] + m[2][3])


def mat_det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


# ---------------------------------------------------------------- primitives
# Each returns (verts, faces). Faces are lists of vertex indices, counter-
# clockwise seen from outside (outward normals). Faces may be convex polygons.

def lathe(profile, segments, cap_bottom=True, cap_top=True, angle=360.0):
    """Revolve [(radius, y), ...] (bottom to top, along the outside) around Y."""
    full = abs(angle - 360.0) < 1e-6
    n_ang = segments if full else segments + 1
    verts, faces, rings = [], [], []
    for r, y in profile:
        if r <= 1e-9:
            verts.append((0.0, float(y), 0.0))
            rings.append([len(verts) - 1] * n_ang)
        else:
            ring = []
            for i in range(n_ang):
                a = math.radians(angle) * i / segments
                verts.append((r * math.cos(a), float(y), r * math.sin(a)))
                ring.append(len(verts) - 1)
            rings.append(ring)
    for j in range(len(profile) - 1):
        lo, hi = rings[j], rings[j + 1]
        for i in range(segments):
            i2 = (i + 1) % n_ang if full else i + 1
            f = [lo[i], hi[i], hi[i2], lo[i2]]
            dedup = []
            for v in f:
                if v not in dedup:
                    dedup.append(v)
            if len(dedup) >= 3:
                faces.append(dedup)
    if full:
        if cap_bottom and profile[0][0] > 1e-9:
            faces.append(list(rings[0]))
        if cap_top and profile[-1][0] > 1e-9:
            faces.append(list(reversed(rings[-1])))
    return verts, faces


def prim_box(p):
    sx, sy, sz = [v / 2.0 for v in p.get("size", [1, 1, 1])]
    v = [(x, y, z) for z in (-sz, sz) for y in (-sy, sy) for x in (-sx, sx)]
    # index = xi + 2*yi + 4*zi
    faces = [[1, 3, 7, 5], [0, 4, 6, 2],   # +x, -x
             [2, 6, 7, 3], [0, 1, 5, 4],   # +y, -y
             [4, 5, 7, 6], [0, 2, 3, 1]]   # +z, -z
    return v, faces


def prim_cylinder(p):
    h = p.get("height", 1.0)
    rb = p.get("radius_bottom", p.get("radius", 0.5))
    rt = p.get("radius_top", p.get("radius", 0.5))
    return lathe([(rb, -h / 2), (rt, h / 2)], int(p.get("segments", 12)))


def prim_cone(p):
    h = p.get("height", 1.0)
    return lathe([(p.get("radius", 0.5), -h / 2), (0.0, h / 2)], int(p.get("segments", 12)))


def prim_sphere(p):
    r = p.get("radius", 0.5)
    rings = int(p.get("rings", 6))
    prof = []
    for j in range(rings + 1):
        a = -math.pi / 2 + math.pi * j / rings
        prof.append((r * math.cos(a) if 0 < j < rings else 0.0, r * math.sin(a)))
    return lathe(prof, int(p.get("segments", 10)))


def prim_lathe(p):
    prof = [tuple(pt) for pt in p["profile"]]
    return lathe(prof, int(p.get("segments", 12)), p.get("cap_bottom", True), p.get("cap_top", True))


def prim_torus(p):
    R, r = p.get("radius", 0.5), p.get("tube", 0.15)
    n, m = int(p.get("segments", 16)), int(p.get("sides", 8))
    verts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            verts.append(((R + r * math.cos(b)) * math.cos(a), r * math.sin(b), (R + r * math.cos(b)) * math.sin(a)))
    idx = lambda i, j: (i % n) * m + (j % m)
    faces = [[idx(i, j), idx(i, j + 1), idx(i + 1, j + 1), idx(i + 1, j)] for i in range(n) for j in range(m)]
    return verts, faces


def prim_plane(p):
    w, d = [v / 2.0 for v in p.get("size", [1, 1])]
    return [(-w, 0.0, -d), (-w, 0.0, d), (w, 0.0, d), (w, 0.0, -d)], [[0, 1, 2, 3]]


def prim_wedge(p):
    """Ramp: full height at the back (-Z), slopes down to the front (+Z)."""
    sx, sy, sz = [v / 2.0 for v in p.get("size", [1, 1, 1])]
    v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, -sy, sz), (-sx, -sy, sz), (-sx, sy, -sz), (sx, sy, -sz)]
    faces = [[0, 1, 2, 3], [0, 4, 5, 1], [1, 5, 2], [0, 3, 4], [3, 2, 5, 4]]
    return v, faces


def _area2d(pts):
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                     for i in range(len(pts)))


def _ear_clip(pts):
    """Triangulate a simple CCW polygon. Returns index triples."""
    idx = list(range(len(pts)))
    tris = []

    def inside(p, a, b, c):
        def s(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))

    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 1e-12:
                continue
            if any(inside(pts[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:
            raise ValueError("extrude outline is self-intersecting or degenerate")
    tris.append(tuple(idx))
    return tris


def prim_extrude(p):
    """Outline [[x, y], ...] in the XY plane (front view), thickness along Z."""
    pts = [tuple(map(float, q)) for q in p["points"]]
    if _area2d(pts) < 0:
        pts.reverse()
    t = p.get("depth", 0.1) / 2.0
    n = len(pts)
    verts = [(x, y, t) for x, y in pts] + [(x, y, -t) for x, y in pts]
    faces = []
    for a, b, c in _ear_clip(pts):
        faces.append([a, b, c])
        faces.append([c + n, b + n, a + n])
    for k in range(n):
        k2 = (k + 1) % n
        faces.append([k, k + n, k2 + n, k2])
    return verts, faces


def prim_mesh(p):
    return [tuple(map(float, v)) for v in p["vertices"]], [list(f) for f in p["faces"]]


PRIMS = {"box": prim_box, "cylinder": prim_cylinder, "cone": prim_cone, "sphere": prim_sphere,
         "lathe": prim_lathe, "torus": prim_torus, "plane": prim_plane, "wedge": prim_wedge,
         "extrude": prim_extrude, "mesh": prim_mesh}


# ---------------------------------------------------------------- shading
def newell(verts, f):
    n = [0.0, 0.0, 0.0]
    for i in range(len(f)):
        a, b = verts[f[i]], verts[f[(i + 1) % len(f)]]
        n[0] += (a[1] - b[1]) * (a[2] + b[2])
        n[1] += (a[2] - b[2]) * (a[0] + b[0])
        n[2] += (a[0] - b[0]) * (a[1] + b[1])
    return tuple(n)  # length = 2 * area


def shade(verts, faces, smooth_angle):
    """Return (positions, normals, triangle indices) with auto-smooth by angle."""
    fn_raw = [newell(verts, f) for f in faces]
    fn = [norm(n) for n in fn_raw]
    vert_faces = {}
    if smooth_angle > 0:
        # group by position so seams (duplicate verts) smooth too
        key = lambda v: (round(v[0], 5), round(v[1], 5), round(v[2], 5))
        for fi, f in enumerate(faces):
            for vi in f:
                vert_faces.setdefault(key(verts[vi]), []).append(fi)
    cos_lim = math.cos(math.radians(smooth_angle)) if smooth_angle > 0 else 2.0
    out_p, out_n, tris, cache = [], [], [], {}
    for fi, f in enumerate(faces):
        corner = []
        for vi in f:
            n = fn[fi]
            if smooth_angle > 0:
                acc = (0.0, 0.0, 0.0)
                for gi in vert_faces[(round(verts[vi][0], 5), round(verts[vi][1], 5), round(verts[vi][2], 5))]:
                    if dot(fn[gi], fn[fi]) >= cos_lim - 1e-9:
                        acc = add(acc, fn_raw[gi])
                n = norm(acc) if dot(acc, acc) > 1e-18 else fn[fi]
            k = (vi, round(n[0], 4), round(n[1], 4), round(n[2], 4))
            if k not in cache:
                cache[k] = len(out_p)
                out_p.append(verts[vi])
                out_n.append(n)
            corner.append(cache[k])
        for i in range(1, len(corner) - 1):
            tris.append((corner[0], corner[i], corner[i + 1]))
    return out_p, out_n, tris


# ---------------------------------------------------------------- recipe
def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def build_parts(recipe):
    """Expand the recipe into a list of part dicts with local geometry."""
    parts = []
    for raw in recipe["parts"]:
        copies = [(raw, False)]
        if raw.get("mirror_x"):
            copies.append((raw, True))
        for p, mirrored in copies:
            shape = p.get("shape", "box")
            if shape not in PRIMS:
                raise ValueError("part '%s': unknown shape '%s' (use one of %s)"
                                 % (p.get("name"), shape, ", ".join(sorted(PRIMS))))
            verts, faces = PRIMS[shape](p)
            pos = list(p.get("pos", [0, 0, 0]))
            rot = list(p.get("rot", [0, 0, 0]))
            name = p.get("name", "%s_%d" % (shape, len(parts)))
            parent = p.get("parent")
            if mirrored:
                verts = [(-x, y, z) for x, y, z in verts]
                faces = [list(reversed(f)) for f in faces]
                pos[0] = -pos[0]
                rot = [rot[0], -rot[1], -rot[2]]
                name = p.get("mirror_name", name + "_mirror")
                if parent and p.get("mirror_parent"):
                    parent = p["mirror_parent"]
            parts.append({
                "name": name, "parent": parent, "material": p.get("material", "default"),
                "verts": verts, "faces": faces, "pos": pos, "rot": rot,
                "scale": list(p.get("scale", [1, 1, 1])),
                "smooth": float(p.get("smooth_angle", 40 if shape in ("sphere", "torus") else 0)),
            })
    names = [p["name"] for p in parts]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise ValueError("duplicate part names: %s" % ", ".join(sorted(dupes)))
    for p in parts:
        if p["parent"] and p["parent"] not in names:
            raise ValueError("part '%s' has unknown parent '%s'" % (p["name"], p["parent"]))
    return parts


def world_matrices(parts):
    by = {p["name"]: p for p in parts}
    cache = {}

    def wm(name, depth=0):
        if depth > 64:
            raise ValueError("parent cycle involving '%s'" % name)
        if name in cache:
            return cache[name]
        p = by[name]
        local = mat_from_trs(p["pos"], quat_from_euler(p["rot"]), p["scale"])
        m = mat_mul(wm(p["parent"], depth + 1), local) if p["parent"] else local
        cache[name] = m
        return m

    return {p["name"]: wm(p["name"]) for p in parts}


def materials_table(recipe):
    mats = dict(recipe.get("materials", {}))
    mats.setdefault("default", {"color": "#b0b0b0"})
    return mats


# ---------------------------------------------------------------- glb writer
class Bin:
    def __init__(self):
        self.data = bytearray()
        self.views, self.accessors = [], []

    def add(self, raw, target, comp, count, typ, mn=None, mx=None):
        while len(self.data) % 4:
            self.data.append(0)
        self.views.append({"buffer": 0, "byteOffset": len(self.data), "byteLength": len(raw), "target": target})
        self.data += raw
        acc = {"bufferView": len(self.views) - 1, "componentType": comp, "count": count, "type": typ}
        if mn is not None:
            acc["min"], acc["max"] = mn, mx
        self.accessors.append(acc)
        return len(self.accessors) - 1


def make_primitive(b, pos, nrm, tris, mat_index):
    flat_p = [c for v in pos for c in v]
    flat_n = [c for v in nrm for c in v]
    mn = [min(v[i] for v in pos) for i in range(3)]
    mx = [max(v[i] for v in pos) for i in range(3)]
    pa = b.add(struct.pack("<%df" % len(flat_p), *flat_p), 34962, 5126, len(pos), "VEC3", mn, mx)
    na = b.add(struct.pack("<%df" % len(flat_n), *flat_n), 34962, 5126, len(nrm), "VEC3")
    flat_i = [i for t in tris for i in t]
    if len(pos) < 65536:
        ia = b.add(struct.pack("<%dH" % len(flat_i), *flat_i), 34963, 5123, len(flat_i), "SCALAR")
    else:
        ia = b.add(struct.pack("<%dI" % len(flat_i), *flat_i), 34963, 5125, len(flat_i), "SCALAR")
    return {"attributes": {"POSITION": pa, "NORMAL": na}, "indices": ia, "material": mat_index}


def write_glb(recipe, parts, path):
    mats = materials_table(recipe)
    used = []
    for p in parts:
        if p["material"] not in mats:
            raise ValueError("part '%s' uses undefined material '%s'" % (p["name"], p["material"]))
        if p["material"] not in used:
            used.append(p["material"])
    gl_mats = []
    for m in used:
        d = mats[m]
        rgb = hex_to_rgb(d.get("color", "#b0b0b0"))
        alpha = d.get("opacity", 1.0)
        gm = {"name": m, "pbrMetallicRoughness": {
            "baseColorFactor": [srgb_to_linear(rgb[0]), srgb_to_linear(rgb[1]), srgb_to_linear(rgb[2]), alpha],
            "metallicFactor": float(d.get("metallic", 0.0)), "roughnessFactor": float(d.get("roughness", 0.8))}}
        if d.get("emissive"):
            e = hex_to_rgb(d["emissive"])
            gm["emissiveFactor"] = [srgb_to_linear(c) for c in e[:3]]
        if alpha < 1.0:
            gm["alphaMode"] = "BLEND"
        if d.get("double_sided"):
            gm["doubleSided"] = True
        gl_mats.append(gm)
    mat_idx = {m: i for i, m in enumerate(used)}
    b = Bin()
    meshes, nodes = [], []
    tri_total = 0
    if recipe.get("merge", False):
        wms = world_matrices(parts)
        groups = {}
        for p in parts:
            m = wms[p["name"]]
            flip = mat_det3(m) < 0
            wv = [mat_apply(m, v) for v in p["verts"]]
            faces = [list(reversed(f)) for f in p["faces"]] if flip else p["faces"]
            g = groups.setdefault(p["material"], [])
            g.append((wv, faces, p["smooth"]))
        prims = []
        for mname, items in groups.items():
            P, N, T = [], [], []
            for wv, faces, sm in items:
                pp, nn, tt = shade(wv, faces, sm)
                off = len(P)
                P += pp
                N += nn
                T += [(a + off, b2 + off, c + off) for a, b2, c in tt]
            tri_total += len(T)
            prims.append(make_primitive(b, P, N, T, mat_idx[mname]))
        meshes.append({"name": recipe.get("name", "model"), "primitives": prims})
        nodes.append({"name": recipe.get("name", "model"), "mesh": 0})
        roots = [0]
    else:
        index = {p["name"]: i for i, p in enumerate(parts)}
        for p in parts:
            pp, nn, tt = shade(p["verts"], p["faces"], p["smooth"])
            tri_total += len(tt)
            meshes.append({"name": p["name"], "primitives": [make_primitive(b, pp, nn, tt, mat_idx[p["material"]])]})
            node = {"name": p["name"], "mesh": len(meshes) - 1}
            if any(abs(v) > 1e-9 for v in p["pos"]):
                node["translation"] = [float(v) for v in p["pos"]]
            if any(abs(v) > 1e-9 for v in p["rot"]):
                node["rotation"] = list(quat_from_euler(p["rot"]))
            if any(abs(v - 1) > 1e-9 for v in p["scale"]):
                node["scale"] = [float(v) for v in p["scale"]]
            nodes.append(node)
        for p in parts:
            if p["parent"]:
                nodes[index[p["parent"]]].setdefault("children", []).append(index[p["name"]])
        child_set = {c for n in nodes for c in n.get("children", [])}
        roots = [i for i in range(len(nodes)) if i not in child_set]
        # wrap in a named root so the engine sees one object
        nodes.append({"name": recipe.get("name", "model"), "children": roots})
        roots = [len(nodes) - 1]
    gltf = {
        "asset": {"version": "2.0", "generator": "asset-forge model_glb.py"},
        "scene": 0, "scenes": [{"name": recipe.get("name", "model"), "nodes": roots}],
        "nodes": nodes, "meshes": meshes, "materials": gl_mats,
        "accessors": b.accessors, "bufferViews": b.views,
        "buffers": [{"byteLength": len(b.data)}],
    }
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    bin_ = bytes(b.data) + b"\x00" * ((4 - len(b.data) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(bin_)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, total))
        f.write(struct.pack("<I4s", len(js), b"JSON") + js)
        f.write(struct.pack("<I4s", len(bin_), b"BIN\x00") + bin_)
    return tri_total


# ---------------------------------------------------------------- preview
def render_preview(recipe, parts, path, size=256):
    """2x2 grid: three-quarter, front (+Z), side (+X), top. Flat lambert shading."""
    mats = materials_table(recipe)
    wms = world_matrices(parts)
    tris = []
    for p in parts:
        m = wms[p["name"]]
        wv = [mat_apply(m, v) for v in p["verts"]]
        d = mats.get(p["material"], {})
        col = hex_to_rgb(d.get("color", "#b0b0b0"))[:3]
        emi = hex_to_rgb(d["emissive"])[:3] if d.get("emissive") else (0, 0, 0)
        for f in p["faces"]:
            for i in range(1, len(f) - 1):
                tris.append((wv[f[0]], wv[f[i]], wv[f[i + 1]], col, emi))
    views = [("3/4", 35.0, 25.0), ("front", 0.0, 0.0), ("side", 90.0, 0.0), ("top", 0.0, 90.0)]
    W = H = size * 2
    img = bytearray(W * H * 3)
    for y in range(H):
        for x in range(W):
            c = 236 if ((x // 16) + (y // 16)) % 2 else 226
            o = (y * W + x) * 3
            img[o:o + 3] = bytes((c, c, c))
    light = norm((0.45, 0.8, 0.55))
    for vi, (label, yaw, pitch) in enumerate(views):
        cy, sy = math.cos(math.radians(-yaw)), math.sin(math.radians(-yaw))
        cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

        def cam(v):
            x, y, z = v
            x, z = x * cy + z * sy, -x * sy + z * cy      # yaw around Y
            y, z = y * cp - z * sp, y * sp + z * cp       # pitch around X
            return (x, y, z)

        ct = [(cam(a), cam(b2), cam(c), col, emi, a, b2, c) for a, b2, c, col, emi in tris]
        if not ct:
            continue
        xs = [v[0] for t in ct for v in t[:3]]
        ys = [v[1] for t in ct for v in t[:3]]
        span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
        k = size * 0.84 / span
        ox = (size - (max(xs) - min(xs)) * k) / 2 - min(xs) * k
        oy = (size - (max(ys) - min(ys)) * k) / 2 + max(ys) * k
        x0, y0 = (vi % 2) * size, (vi // 2) * size
        zbuf = [-1e30] * (size * size)
        for a, b2, c, col, emi, wa, wb, wc in ct:
            n = norm(cross(sub(wb, wa), sub(wc, wa)))
            lit = 0.38 + 0.62 * abs(dot(n, light))
            rgb = [min(255, int(col[i] * lit + emi[i])) for i in range(3)]
            P = [(v[0] * k + ox, -v[1] * k + oy, v[2]) for v in (a, b2, c)]
            minx, maxx = max(0, int(min(q[0] for q in P))), min(size - 1, int(max(q[0] for q in P)) + 1)
            miny, maxy = max(0, int(min(q[1] for q in P))), min(size - 1, int(max(q[1] for q in P)) + 1)
            (ax, ay, az), (bx, by, bz), (qx, qy, qz) = P
            den = (by - qy) * (ax - qx) + (qx - bx) * (ay - qy)
            if abs(den) < 1e-12:
                continue
            for py in range(miny, maxy + 1):
                fy = py + 0.5
                for px in range(minx, maxx + 1):
                    fx = px + 0.5
                    w1 = ((by - qy) * (fx - qx) + (qx - bx) * (fy - qy)) / den
                    w2 = ((qy - ay) * (fx - qx) + (ax - qx) * (fy - qy)) / den
                    w3 = 1 - w1 - w2
                    if w1 < -1e-6 or w2 < -1e-6 or w3 < -1e-6:
                        continue
                    z = w1 * az + w2 * bz + w3 * qz
                    zi = py * size + px
                    if z > zbuf[zi]:
                        zbuf[zi] = z
                        o = ((y0 + py) * W + x0 + px) * 3
                        img[o:o + 3] = bytes(rgb)
        # thin border between views
        for i in range(size):
            for (xx, yy) in ((x0 + i, y0), (x0, y0 + i)):
                o = (yy * W + xx) * 3
                img[o:o + 3] = b"\xa0\xa0\xa0"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    write_png(path, W, H, img)


def bbox(parts):
    wms = world_matrices(parts)
    pts = [mat_apply(wms[p["name"]], v) for p in parts for v in p["verts"]]
    return [min(v[i] for v in pts) for i in range(3)], [max(v[i] for v in pts) for i in range(3)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipe")
    ap.add_argument("-o", "--out", help="output .glb path")
    ap.add_argument("--preview", help="also write a 4-view PNG preview here")
    ap.add_argument("--preview-only", help="write only the PNG preview (fast iteration)")
    ap.add_argument("--max-tris", type=int, help="fail if the model exceeds this triangle budget")
    a = ap.parse_args()
    with open(a.recipe, encoding="utf-8") as f:
        recipe = json.load(f)
    try:
        parts = build_parts(recipe)
    except (ValueError, KeyError) as e:
        sys.exit("recipe error: %s" % e)
    lo, hi = bbox(parts)
    if a.preview_only:
        render_preview(recipe, parts, a.preview_only)
        print("preview: %s" % a.preview_only)
        return
    if not a.out:
        sys.exit("give -o OUT.glb (or --preview-only PNG)")
    tris = write_glb(recipe, parts, a.out)
    print("wrote %s  (%d bytes)" % (a.out, os.path.getsize(a.out)))
    print("parts: %d  triangles: %d  merged: %s" % (len(parts), tris, bool(recipe.get("merge"))))
    print("size (m): %.3f x %.3f x %.3f   min y: %.3f" % (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], lo[1]))
    if a.preview:
        render_preview(recipe, parts, a.preview)
        print("preview: %s" % a.preview)
    if a.max_tris and tris > a.max_tris:
        sys.exit("OVER BUDGET: %d triangles > %d" % (tris, a.max_tris))


if __name__ == "__main__":
    main()
