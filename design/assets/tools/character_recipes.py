#!/usr/bin/env python3
"""Emit and build the Aperture character recipes (subjects + placeholder player).

Curved and elliptical shapes cannot be typed by hand into model_glb.py recipes,
and every extra part costs a draw call, so this helper bakes them into `mesh`
parts. The JSON it writes is what model_glb.py consumes; change shapes HERE and
re-run, or a re-run will overwrite hand edits to the JSON.

    python design/assets/tools/character_recipes.py            # all recipes + .glb + previews
    python design/assets/tools/character_recipes.py subj_mossmote_base_01
    python design/assets/tools/character_recipes.py --thumbs OUT.png   # 64 px read test

Each recipe also carries a `poses` table (ignored by model_glb.py): per-node
overrides for the engine to move towards. They are rendered to
design/assets/previews/<name>_<pose>.png.

Standard library only. Requires .claude/skills/asset-forge/scripts/model_glb.py.
"""
import argparse
import copy
import json
import math
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FORGE = os.path.join(ROOT, ".claude", "skills", "asset-forge", "scripts")
MODELS = os.path.join(ROOT, "assets", "art", "models")
RECIPES = os.path.join(ROOT, "design", "assets", "recipes")
PREVIEWS = os.path.join(ROOT, "design", "assets", "previews")
sys.path.insert(0, FORGE)
import model_glb  # noqa: E402

# Art bible 4.2. subj_body is the 50/50 mix of Lumen and Paper White ("pale tint
# of Lumen or Paper White", 5.3). Emissive values are Lumen at 50 % and 75 %; the
# engine scales them from glow_permille.
SUBJECT_MATERIALS = {
    "subj_body": {"color": "#B9E8DE", "emissive": "#3F716C", "roughness": 0.6},
    "subj_glow": {"color": "#7FE3D8", "emissive": "#5FAAA2", "roughness": 0.5},
    "subj_face": {"color": "#1E2230", "roughness": 0.8},
}


# ------------------------------------------------------------------ vector
def v_add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def v_sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def v_mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def v_cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def v_dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_norm(a):
    l = math.sqrt(v_dot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)


# ------------------------------------------------------------------ mesh builders
class Mesh:
    """Vertex and face accumulator. Each add_* call is one closed shell."""

    def __init__(self):
        self.v, self.f = [], []

    def _shell(self, verts, faces):
        """Append a closed shell, flipping it if it winds inside out."""
        c = tuple(sum(p[i] for p in verts) / len(verts) for i in range(3))
        vol = 0.0
        for f in faces:
            for i in range(1, len(f) - 1):
                vol += v_dot(v_sub(verts[f[0]], c), v_cross(v_sub(verts[f[i]], c), v_sub(verts[f[i + 1]], c)))
        if vol < 0:
            faces = [list(reversed(f)) for f in faces]
        o = len(self.v)
        self.v += verts
        self.f += [[i + o for i in f] for f in faces]
        return self

    def add_rings(self, rings, closed=False):
        """Skin equal-length rings of points; open ends get a centre fan."""
        n, m = len(rings[0]), len(rings)
        verts = [p for r in rings for p in r]
        faces = []
        for j in range(m if closed else m - 1):
            a, b = j * n, ((j + 1) % m) * n
            for i in range(n):
                k = (i + 1) % n
                faces.append([a + k, a + i, b + i, b + k])
        if not closed:
            for ring_i, flip in ((0, False), (m - 1, True)):
                c = tuple(sum(p[x] for p in rings[ring_i]) / n for x in range(3))
                ci = len(verts)
                verts.append(c)
                for i in range(n):
                    k = (i + 1) % n
                    a, b = ring_i * n + i, ring_i * n + k
                    faces.append([ci, a, b] if flip else [ci, b, a])
        return self._shell(verts, faces)

    def add_tube(self, path, radii, sides=8, ref=(1, 0, 0), closed=False):
        """Sweep an ellipse along path. radii[i] = r, or (r along ref, r across)."""
        rings, n = [], len(path)
        for i, p in enumerate(path):
            a = path[(i - 1) % n] if (closed or i > 0) else p
            b = path[(i + 1) % n] if (closed or i < n - 1) else p
            t = v_norm(v_sub(b, a))
            u = v_norm(v_sub(ref, v_mul(t, v_dot(ref, t))))
            w = v_cross(t, u)
            r = radii[i] if isinstance(radii[i], (tuple, list)) else (radii[i], radii[i])
            rings.append([v_add(p, v_add(v_mul(u, math.cos(s) * r[0]), v_mul(w, math.sin(s) * r[1])))
                          for s in (2 * math.pi * k / sides for k in range(sides))])
        return self.add_rings(rings, closed)

    def add_loft(self, stations, sides=8):
        """Stack of ellipses on Y: stations = (y, rx, rz[, cx, cz])."""
        rings = []
        for st in stations:
            y, rx, rz = st[:3]
            cx, cz = (st[3], st[4]) if len(st) > 3 else (0.0, 0.0)
            rings.append([(cx + rx * math.cos(s), y, cz + rz * math.sin(s))
                          for s in (2 * math.pi * k / sides + math.pi / sides for k in range(sides))])
        return self.add_rings(rings)

    def add_ball(self, c, r, seg=8, rings=5):
        st = []
        for i in range(rings):
            a = math.pi * (i + 0.5) / rings
            st.append((c[1] - r * math.cos(a), r * math.sin(a), r * math.sin(a), c[0], c[2]))
        return self.add_loft(st, seg)

    def add_prism(self, outline, z=0.0, depth=0.02):
        """Convex 2D outline in XY, extruded along Z."""
        n = len(outline)
        h = depth / 2
        verts = [(x, y, z + h) for x, y in outline] + [(x, y, z - h) for x, y in outline]
        faces = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
        for i in range(n):
            k = (i + 1) % n
            faces.append([k, i, i + n, k + n])
        return self._shell(verts, faces)

    def add_dot(self, c, normal, r=0.016, h=0.006, sides=8):
        """Small dome whose rim sinks into the surface it sits on."""
        n = v_norm(normal)
        u = v_norm(v_cross(n, (0, 1, 0)) if abs(n[1]) < 0.9 else v_cross(n, (1, 0, 0)))
        w = v_cross(n, u)
        rim = [v_add(v_sub(c, v_mul(n, h)), v_add(v_mul(u, math.cos(a) * r), v_mul(w, math.sin(a) * r)))
               for a in (2 * math.pi * k / sides for k in range(sides))]
        tip = v_add(c, v_mul(n, h))
        faces = [[sides, i, (i + 1) % sides] for i in range(sides)]
        if v_dot(v_cross(v_sub(rim[0], tip), v_sub(rim[1], tip)), n) < 0:
            faces = [list(reversed(f)) for f in faces]
        o = len(self.v)
        self.v += rim + [tip]
        self.f += [[i + o for i in f] for f in faces]
        return self

    def part(self, name, material, smooth=50, **kw):
        d = {"name": name, "shape": "mesh", "material": material, "smooth_angle": smooth,
             "vertices": [[round(c, 4) for c in p] for p in self.v], "faces": self.f}
        d.update(kw)
        return d


def ellipse_profile(r, half_h, n=10, bottom=1.0):
    """Lathe profile of an ellipsoid; bottom < 1 flattens the underside."""
    pts = []
    for i in range(n + 1):
        a = -math.pi / 2 + math.pi * i / n
        y = math.sin(a) * half_h
        pts.append([round(r * math.cos(a), 4), round(y * (bottom if y < 0 else 1.0), 4)])
    pts[0][0] = pts[-1][0] = 0
    return pts


def radius_at(profile, y):
    for (r0, y0), (r1, y1) in zip(profile, profile[1:]):
        if y0 <= y <= y1:
            return r0 + (r1 - r0) * (y - y0) / ((y1 - y0) or 1)
    return 0.0


def eyes_on_lathe(profile, x, y, r=0.016):
    """Two dots on the front of a lathe body, sitting on its surface."""
    z = math.sqrt(max(radius_at(profile, y) ** 2 - x * x, 0.0))
    m = Mesh()
    for sx in (1, -1):
        m.add_dot((sx * x, y, z), (sx * x, y * 0.4, z), r)
    return m


# ------------------------------------------------------------------ subjects
def subject(name, comment, parts, poses):
    return {"name": name, "comment": comment, "merge": False,
            "materials": SUBJECT_MATERIALS, "poses": poses, "parts": parts}


def puffwisp():
    prof = ellipse_profile(0.17, 0.15, 10, bottom=0.92)
    root = Mesh().add_tube(
        [(0, -0.02, 0.03), (0, 0.0, -0.05), (0, 0.03, -0.12), (0, 0.07, -0.17), (0, 0.11, -0.2)],
        [0.085, 0.08, 0.066, 0.052, 0.042], sides=8)
    tip = Mesh().add_tube(
        [(0, -0.02, 0.01), (0, 0.03, -0.015), (0, 0.07, -0.012), (0, 0.1, 0.012), (0, 0.112, 0.05), (0, 0.112, 0.066)],
        [0.04, 0.038, 0.031, 0.024, 0.016, 0.008], sides=8)
    parts = [
        {"name": "body", "shape": "lathe", "profile": prof, "segments": 16, "smooth_angle": 60,
         "material": "subj_body"},
        eyes_on_lathe(prof, 0.055, -0.03, 0.02).part("face", "subj_face", parent="body"),
        root.part("wisp_root", "subj_glow", parent="body", pos=[0, 0.05, -0.10]),
        tip.part("wisp_tip", "subj_glow", parent="wisp_root", pos=[0, 0.11, -0.2]),
    ]
    poses = {"decisive": {"wisp_root": {"rot": [-38, 0, 0]}, "wisp_tip": {"rot": [-65, 0, 0]}}}
    return subject("subj_puffwisp_base_01",
                   "Puffwisp (species_key 1, tier C). Trait: short trailing wisp. Rest pose = IDLE.",
                   parts, poses)


def mossmote():
    prof = ellipse_profile(0.16, 0.105, 10, bottom=0.82)
    fin = Mesh().add_tube(
        [(-0.03, -0.012, 0), (0.03, 0.012, 0), (0.09, 0.03, 0), (0.15, 0.036, 0), (0.205, 0.025, 0), (0.235, 0.008, 0)],
        [(0.014, 0.03), (0.018, 0.058), (0.018, 0.074), (0.016, 0.066), (0.012, 0.042), (0.008, 0.02)],
        sides=8, ref=(0, 0, 1))
    parts = [
        {"name": "body", "shape": "lathe", "profile": prof, "segments": 16, "smooth_angle": 60,
         "material": "subj_body"},
        eyes_on_lathe(prof, 0.05, -0.012, 0.02).part("face", "subj_face", parent="body"),
        fin.part("fin", "subj_glow", parent="body", pos=[0.10, 0.07, 0.0], rot=[0, 0, 22],
                 mirror_x=True, mirror_name="fin_mirror"),
    ]
    poses = {"decisive": {"fin": {"rot": [0, 0, 68]}, "fin_mirror": {"rot": [0, 0, -68]}}}
    return subject("subj_mossmote_base_01",
                   "Mossmote (species_key 2, tier C). Trait: two ear-like fins. Rest pose = IDLE.",
                   parts, poses)


def driftfin():
    zs = [0.27, 0.25, 0.19, 0.10, 0.0, -0.10, -0.19, -0.25]
    hs = [0.006, 0.05, 0.088, 0.112, 0.112, 0.094, 0.07, 0.054]
    ws = [0.006, 0.042, 0.074, 0.092, 0.09, 0.072, 0.052, 0.038]
    body = Mesh().add_tube([(0, -0.02, z) for z in zs], list(zip(hs, ws)), sides=16, ref=(0, 1, 0))
    root = Mesh().add_tube(
        [(0, 0, 0.05), (0, 0.0, -0.05), (0, -0.015, -0.15), (0, -0.03, -0.26), (0, -0.035, -0.36)],
        [(0.05, 0.03), (0.056, 0.024), (0.07, 0.018), (0.084, 0.014), (0.092, 0.012)],
        sides=10, ref=(0, 1, 0))
    tip = Mesh().add_tube(
        [(0, -0.003, 0.05), (0, 0.0, -0.01), (0, 0.015, -0.1), (0, 0.05, -0.2), (0, 0.1, -0.28), (0, 0.15, -0.33),
         (0, 0.175, -0.345)],
        [(0.07, 0.008), (0.09, 0.01), (0.1, 0.012), (0.098, 0.011), (0.085, 0.01), (0.055, 0.008), (0.015, 0.005)],
        sides=10, ref=(0, 1, 0))
    face = Mesh()
    for sx in (1, -1):
        face.add_dot((sx * 0.054, -0.05, 0.215), (sx * 0.8, -0.3, 0.5), 0.018)
    parts = [
        body.part("body", "subj_body", smooth=60),
        face.part("face", "subj_face", parent="body"),
        root.part("tail_root", "subj_glow", parent="body", pos=[0, -0.02, -0.25]),
        tip.part("tail_tip", "subj_glow", parent="tail_root", pos=[0, -0.035, -0.36]),
    ]
    poses = {"decisive": {"tail_root": {"rot": [20, 0, 0]}, "tail_tip": {"rot": [26, 0, 0]},
                          "body": {"rot": [-8, 0, 0]}}}
    return subject("subj_driftfin_base_01",
                   "Driftfin (species_key 3, tier B). Trait: long tail fin. Rest pose = IDLE.",
                   parts, poses)


def rounded_rect_path(w, h, r, steps=4):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                       (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), 0.0))
    return pts


def blob(cx, cy, rx, ry, n=10):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def hearth_echo():
    path = rounded_rect_path(1.2, 0.9, 0.08)
    frame = Mesh().add_tube(path, [(0.03, 0.038)] * len(path), sides=6, ref=(0, 0, 1), closed=True)
    scene = Mesh()
    # Doorway arch, floor line and two seated figures; the right third dissolves.
    arch = [(-0.42 + 0.17 * math.cos(math.pi * i / 8), -0.05 + 0.2 * math.sin(math.pi * i / 8), 0.0)
            for i in range(9)]
    arch = [(-0.25, -0.3, 0)] + arch + [(-0.59, -0.3, 0)]
    scene.add_tube(arch, [0.016] * len(arch), sides=6, ref=(0, 0, 1))
    scene.add_tube([(-0.5, -0.31, 0), (-0.25, -0.31, 0), (0.0, -0.31, 0), (0.17, -0.31, 0)],
                   [0.012, 0.016, 0.014, 0.004], sides=6, ref=(0, 0, 1))
    scene.add_prism(blob(-0.12, 0.09, 0.075, 0.08), depth=0.03)
    scene.add_prism([(-0.25, -0.3), (-0.0, -0.3), (0.015, -0.2), (-0.02, -0.07), (-0.07, -0.01),
                     (-0.17, -0.01), (-0.22, -0.07), (-0.255, -0.2)], depth=0.03)
    scene.add_prism(blob(0.11, -0.04, 0.05, 0.054), depth=0.03)
    scene.add_prism([(0.04, -0.3), (0.19, -0.3), (0.2, -0.22), (0.17, -0.13), (0.14, -0.1),
                     (0.08, -0.1), (0.05, -0.13), (0.03, -0.22)], depth=0.03)
    motes = Mesh()
    for c, r in (((0.27, -0.14, 0.03), 0.026), ((0.34, 0.03, -0.02), 0.02), ((0.3, 0.17, 0.02), 0.016),
                 ((0.42, -0.2, 0.0), 0.018), ((0.45, 0.12, 0.03), 0.012)):
        motes.add_ball(c, r)
    parts = [
        frame.part("frame", "subj_glow", smooth=50),
        scene.part("scene", "subj_body", smooth=35, parent="frame"),
        motes.part("motes", "subj_glow", smooth=60, parent="frame"),
    ]
    poses = {"decisive": {"scene": {"pos": [0, 0, 0.05]}, "motes": {"pos": [-0.08, 0, 0.05]}},
             "fading": {"frame": {"scale": [1.0, 0.12, 1.0]}}}
    return subject("subj_hearth_echo_base_01",
                   "Hearth Echo (species_key 4, tier B, MEMORY). Trait: empty frame of faded light "
                   "around a half-seen scene. Still; no face (memories are not creatures).",
                   parts, poses)


def halo_keeper():
    prof = [[0, -0.30], [0.07, -0.295], [0.135, -0.265], [0.18, -0.21], [0.2, -0.13], [0.196, -0.05],
            [0.172, 0.03], [0.15, 0.09], [0.145, 0.15], [0.14, 0.21], [0.112, 0.265], [0.065, 0.3], [0, 0.31]]
    parts = [
        {"name": "body", "shape": "lathe", "profile": prof, "segments": 18, "smooth_angle": 60,
         "material": "subj_body"},
        eyes_on_lathe(prof, 0.052, 0.13, 0.021).part("face", "subj_face", parent="body"),
        {"name": "ring", "shape": "torus", "radius": 0.34, "tube": 0.022, "segments": 32, "sides": 8,
         "smooth_angle": 60, "pos": [0, -0.04, 0], "rot": [14, 0, 9], "parent": "body", "material": "subj_glow"},
    ]
    poses = {"decisive": {"ring": {"pos": [0, 0.06, 0], "rot": [4, 0, 3], "scale": [1.3, 1.3, 1.3]}}}
    return subject("subj_halo_keeper_base_01",
                   "Halo Keeper (species_key 5, tier A). Trait: a slow ring orbiting the body. "
                   "Spin the ring node about its local Y. Rest pose = IDLE.",
                   parts, poses)


# ------------------------------------------------------------------ player placeholder
def player():
    mats = {
        "jacket": {"color": "#7D9A78", "roughness": 0.9},
        "trousers": {"color": "#4A5568", "roughness": 0.9},
        "skin": {"color": "#B9805C", "roughness": 0.8},
        "ink": {"color": "#2E3446", "roughness": 0.7},
        "strap": {"color": "#7FB2DC", "roughness": 0.7},
        "camera_ring": {"color": "#F2EDE4", "emissive": "#2A2826", "roughness": 0.4},
    }
    torso = Mesh().add_loft([(-0.13, 0.165, 0.125), (-0.04, 0.178, 0.13), (0.16, 0.185, 0.128),
                             (0.40, 0.205, 0.125), (0.49, 0.17, 0.105), (0.545, 0.075, 0.07)], 10)
    head = Mesh().add_loft([(-0.14, 0.05, 0.05, 0, 0), (-0.09, 0.052, 0.052, 0, 0.005),
                            (-0.06, 0.085, 0.095, 0, 0.012), (0.0, 0.112, 0.118, 0, 0.012),
                            (0.07, 0.112, 0.118, 0, 0.008), (0.115, 0.08, 0.088, 0, 0.004),
                            (0.138, 0.02, 0.022, 0, 0)], 10)
    hair = Mesh().add_loft([(-0.045, 0.086, 0.07, 0, -0.078), (0.01, 0.118, 0.098, 0, -0.038),
                            (0.05, 0.123, 0.128, 0, -0.008), (0.1, 0.104, 0.112, 0, -0.004),
                            (0.137, 0.062, 0.066, 0, -0.002), (0.153, 0.012, 0.012, 0, 0)], 10)
    upper = Mesh().add_loft([(0.055, 0.03, 0.03), (0.03, 0.056, 0.06), (-0.02, 0.066, 0.068), (-0.14, 0.058, 0.06),
                             (-0.285, 0.05, 0.052), (-0.3, 0.03, 0.03)], 7)
    fore = Mesh().add_loft([(0.02, 0.03, 0.03), (0.0, 0.05, 0.052), (-0.13, 0.046, 0.048),
                            (-0.245, 0.04, 0.042), (-0.25, 0.012, 0.012)], 7)
    hand = Mesh().add_loft([(0.01, 0.022, 0.03), (-0.03, 0.03, 0.044), (-0.08, 0.026, 0.04),
                            (-0.105, 0.01, 0.018)], 6)
    thigh = Mesh().add_loft([(0.05, 0.06, 0.06), (-0.04, 0.094, 0.098), (-0.22, 0.08, 0.086),
                             (-0.41, 0.064, 0.07), (-0.43, 0.03, 0.03)], 7)
    shin = Mesh().add_loft([(0.02, 0.03, 0.03), (0.0, 0.064, 0.07), (-0.16, 0.062, 0.07),
                            (-0.34, 0.05, 0.054), (-0.36, 0.03, 0.03)], 7)
    boot = Mesh().add_loft([(0.05, 0.052, 0.058, 0, 0.0), (-0.015, 0.058, 0.09, 0, 0.03),
                            (-0.08, 0.06, 0.135, 0, 0.055), (-0.1, 0.054, 0.128, 0, 0.055)], 8)
    bag = Mesh().add_loft([(-0.1, 0.08, 0.05), (-0.085, 0.115, 0.06), (0.06, 0.115, 0.058),
                           (0.095, 0.09, 0.046), (0.105, 0.05, 0.02)], 6)
    strap_path = [(0.0, 0.08, 0.14), (0.075, 0.2, 0.135), (0.1, 0.38, 0.115), (0.11, 0.5, 0.05),
                  (0.09, 0.545, -0.03), (0.0, 0.565, -0.075), (-0.09, 0.545, -0.03), (-0.11, 0.5, 0.05),
                  (-0.1, 0.38, 0.115), (-0.075, 0.2, 0.135)]
    strap = Mesh().add_tube(strap_path, [(0.009, 0.022)] * len(strap_path), sides=4, ref=(0, 0, 1), closed=True)
    # Placeholder camera at 1.2x real size (art bible 3.3). The engine swaps this for
    # the owned gear_ model at the gear_socket node, so it carries no tier colour or brand.
    cam = Mesh().add_loft([(-0.05, 0.11, 0.034), (0.05, 0.11, 0.034)], 4)
    cam.add_tube([(0, 0, 0.03), (0, 0, 0.12)], [0.046, 0.05], sides=10, ref=(0, 1, 0))
    ring = Mesh().add_tube([(0, 0, 0.113), (0, 0, 0.14)], [0.057, 0.06], sides=10, ref=(0, 1, 0))
    ring.add_loft([(0.049, 0.112, 0.036), (0.062, 0.112, 0.036)], 4)

    parts = [
        torso.part("torso", "jacket", smooth=0, pos=[0, 0.92, 0]),
        head.part("head", "skin", smooth=0, parent="torso", pos=[0, 0.68, 0.01]),
        hair.part("hair", "ink", smooth=0, parent="head"),
        upper.part("upper_arm", "jacket", smooth=0, parent="torso", pos=[0.218, 0.425, 0], rot=[0, 0, 4],
                   mirror_x=True, mirror_name="upper_arm_mirror"),
        fore.part("forearm", "jacket", smooth=0, parent="upper_arm", pos=[0, -0.3, 0], rot=[-10, 0, 0],
                  mirror_x=True, mirror_name="forearm_mirror", mirror_parent="upper_arm_mirror"),
        hand.part("hand", "skin", smooth=0, parent="forearm", pos=[0, -0.245, 0],
                  mirror_x=True, mirror_name="hand_mirror", mirror_parent="forearm_mirror"),
        thigh.part("thigh", "trousers", smooth=0, parent="torso", pos=[0.098, -0.03, 0],
                   mirror_x=True, mirror_name="thigh_mirror"),
        shin.part("shin", "trousers", smooth=0, parent="thigh", pos=[0, -0.43, 0],
                  mirror_x=True, mirror_name="shin_mirror", mirror_parent="thigh_mirror"),
        boot.part("boot", "ink", smooth=0, parent="shin", pos=[0, -0.36, 0],
                  mirror_x=True, mirror_name="boot_mirror", mirror_parent="shin_mirror"),
        bag.part("bag", "trousers", smooth=0, parent="torso", pos=[0.215, 0.0, -0.05], rot=[0, 18, 0]),
        strap.part("strap", "strap", smooth=0, parent="torso"),
        cam.part("gear_socket", "ink", smooth=0, parent="torso", pos=[0, 0.1, 0.172]),
        ring.part("camera_ring", "camera_ring", smooth=0, parent="gear_socket"),
    ]
    poses = {
        "raise_camera": {
            "upper_arm": {"rot": [-65, 0, 15]}, "upper_arm_mirror": {"rot": [-65, 0, -15]},
            "forearm": {"rot": [-117, 0, 25]}, "forearm_mirror": {"rot": [-117, 0, -25]},
            "gear_socket": {"pos": [0, 0.68, 0.2]},
        },
        "sneak": {
            "torso": {"pos": [0, 0.5, -0.2], "rot": [38, 0, 0]},
            "upper_arm": {"rot": [-38, 0, 4]}, "upper_arm_mirror": {"rot": [-38, 0, -4]},
            "thigh": {"rot": [-128, 0, 0]}, "thigh_mirror": {"rot": [-128, 0, 0]},
            "shin": {"rot": [90, 0, 0]}, "shin_mirror": {"rot": [90, 0, 0]},
            "head": {"rot": [-34, 0, 0]},
        },
    }
    return {"name": "char_player_base_01_placeholder",
            "comment": "PLACEHOLDER. Stiff jointed figure, no skeleton, no animation. Replace with a CC0 rigged human "
                       "(art bible A5). Feet on y = 0, faces +Z, height 1.75 m, eye height 1.60 m (Player Movement R2).",
            "merge": False, "materials": mats, "poses": poses, "parts": parts}


BUILDERS = {
    "subj_puffwisp_base_01": (puffwisp, 1200),
    "subj_mossmote_base_01": (mossmote, 1200),
    "subj_driftfin_base_01": (driftfin, 1200),
    "subj_hearth_echo_base_01": (hearth_echo, 1200),
    "subj_halo_keeper_base_01": (halo_keeper, 1200),
    "char_player_base_01_placeholder": (player, 3000),
}


# ------------------------------------------------------------------ output
def write_recipe(recipe, path):
    """One line per part, so the JSON stays diffable."""
    head = {k: v for k, v in recipe.items() if k != "parts"}
    text = json.dumps(head, indent=2)[:-2]
    lines = ",\n".join("    " + json.dumps(p, separators=(",", ":")) for p in recipe["parts"])
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + ',\n  "parts": [\n' + lines + "\n  ]\n}\n")


def posed(recipe, pose):
    """Copy of a recipe with a pose table applied, for preview rendering."""
    r = copy.deepcopy(recipe)
    table = r["poses"][pose]
    out = []
    for p in r["parts"]:
        if not p.get("mirror_x"):
            out.append(p)
            continue
        a, b = dict(p), dict(p)
        a.pop("mirror_x")
        b.pop("mirror_x")
        b["name"] = p["mirror_name"]
        b["pos"] = [-p["pos"][0]] + list(p["pos"][1:])
        pr = p.get("rot", [0, 0, 0])
        b["rot"] = [pr[0], -pr[1], -pr[2]]
        b["vertices"] = [[-x, y, z] for x, y, z in p["vertices"]]
        b["faces"] = [list(reversed(f)) for f in p["faces"]]
        if p.get("mirror_parent"):
            b["parent"] = p["mirror_parent"]
        out += [a, b]
    for p in out:
        p.update(table.get(p["name"], {}))
    r["parts"] = out
    return r


def build(name):
    fn, budget = BUILDERS[name]
    recipe = fn()
    os.makedirs(MODELS, exist_ok=True)
    os.makedirs(RECIPES, exist_ok=True)
    path = os.path.join(RECIPES, name + ".json")
    write_recipe(recipe, path)
    res = subprocess.run([sys.executable, os.path.join(FORGE, "model_glb.py"), path,
                          "-o", os.path.join(MODELS, name + ".glb"),
                          "--preview", os.path.join(PREVIEWS, name + ".png"),
                          "--max-tris", str(budget)], capture_output=True, text=True)
    print(res.stdout.strip())
    if res.returncode:
        print(res.stderr.strip())
    print("draw calls (one per part): %d   materials: %d"
          % (len(model_glb.build_parts(recipe)), len(recipe["materials"])))
    for pose in recipe.get("poses", {}):
        pr = posed(recipe, pose)
        model_glb.render_preview(pr, model_glb.build_parts(pr), os.path.join(PREVIEWS, "%s_%s.png" % (name, pose)))


def thumbs(path):
    """64 px read test: each model and pose, lit on Darkroom Ink and as a flat silhouette."""
    grabbed = {}
    real = model_glb.write_png

    def grab(_p, w, h, img):
        grabbed["img"], grabbed["w"] = img, w

    model_glb.write_png = grab
    tiles = []
    for name, (fn, _b) in BUILDERS.items():
        rec = fn()
        for r in [rec] + [posed(rec, k) for k in rec.get("poses", {})]:
            model_glb.render_preview(r, model_glb.build_parts(r), "unused.png", size=64)
            tiles.append((bytes(grabbed["img"]), grabbed["w"]))
    model_glb.write_png = real
    cols, cell, zoom = 7, 64, 2
    rows = (len(tiles) + cols - 1) // cols
    W, H = cols * cell * zoom, rows * cell * 2 * zoom
    out = bytearray(b"\x1e\x22\x30" * (W * H))
    bg = {(226, 226, 226), (236, 236, 236), (160, 160, 160)}
    for t, (img, w) in enumerate(tiles):
        tx, ty = (t % cols) * cell * zoom, (t // cols) * cell * 2 * zoom
        for y in range(cell):
            for x in range(cell):
                o = (y * w + x) * 3          # top-left pane = 3/4 view
                px = (img[o], img[o + 1], img[o + 2])
                if px in bg:
                    continue
                for dy in range(zoom):
                    for dx in range(zoom):
                        a = ((ty + y * zoom + dy) * W + tx + x * zoom + dx) * 3
                        out[a:a + 3] = bytes(px)
                        b = ((ty + (cell + y) * zoom + dy) * W + tx + x * zoom + dx) * 3
                        out[b:b + 3] = b"\xf2\xed\xe4"
    real(path, W, H, out)
    print("thumbs:", path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="recipe names; default all")
    ap.add_argument("--thumbs", help="write a 64 px read-test contact sheet here instead of building")
    a = ap.parse_args()
    if a.thumbs:
        thumbs(a.thumbs)
        return
    for name in a.names or BUILDERS:
        build(name)


if __name__ == "__main__":
    main()
