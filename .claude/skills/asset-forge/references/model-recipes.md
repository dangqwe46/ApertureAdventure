# 3D model recipes (`model_glb.py`)

A recipe is a JSON file describing a model as named parts built from primitives.
Units are metres, +Y is up, the model's **front faces +Z**, and the origin should
sit where the engine expects it (feet / base on y = 0 for characters and props,
the grip for held items, the hinge for doors).

```json
{
  "name": "prop_lantern",
  "merge": false,
  "materials": {
    "iron":  { "color": "#3a3a40", "metallic": 0.7, "roughness": 0.5 },
    "glass": { "color": "#ffd27a", "emissive": "#c07a10", "opacity": 0.8 }
  },
  "parts": [
    { "name": "body", "shape": "cylinder", "radius": 0.12, "height": 0.25, "segments": 8,
      "pos": [0, 0.15, 0], "material": "glass" }
  ]
}
```

## Top-level keys
| key | meaning |
|---|---|
| `name` | root node name in the engine; use the asset file name |
| `merge` | `true` bakes all parts into one mesh (one draw call per material). Use for static scenery and anything repeated. `false` (default) keeps one node per part so parts can be animated |
| `materials` | name -> `color` (#rrggbb sRGB), `metallic` 0-1, `roughness` 0-1, `emissive` (#rrggbb), `opacity` 0-1 (switches to alpha blend), `double_sided` |
| `parts` | list of parts, below |

## Part keys
| key | meaning |
|---|---|
| `name` | unique; becomes the node name (animate by name in the engine) |
| `shape` | `box`, `cylinder`, `cone`, `sphere`, `lathe`, `torus`, `plane`, `wedge`, `extrude`, `mesh` |
| `pos` | [x, y, z] relative to parent |
| `rot` | Euler degrees [x, y, z], applied X then Y then Z |
| `scale` | [x, y, z], applied to the part's own geometry before rotation |
| `parent` | another part's name: this part moves with it (pivots, lids, arms, wheels) |
| `material` | key in `materials` |
| `smooth_angle` | 0 = flat low-poly facets (default); 30-60 = smooth curved surfaces, crisp hard edges. Spheres and tori default to 40 |
| `mirror_x` | also create a copy mirrored across X (ears, arms, wheels). Copy is named `<name>_mirror`, or `mirror_name`; `mirror_parent` re-parents the copy |

## Shapes
| shape | parameters (defaults) | notes |
|---|---|---|
| `box` | `size` [1,1,1] | centred on its origin |
| `cylinder` | `radius` 0.5 (or `radius_bottom` / `radius_top` for tapers), `height` 1, `segments` 12 | along local Y, centred |
| `cone` | `radius` 0.5, `height` 1, `segments` 12 | apex at +Y |
| `sphere` | `radius` 0.5, `segments` 10, `rings` 6 | low values = gem / rock look |
| `lathe` | `profile` [[radius, y], ...] bottom -> top along the outside, `segments` 12, `cap_bottom`, `cap_top` | vases, bottles, mushrooms, tree trunks, potions, helmets, chess pieces. radius 0 makes a pole |
| `torus` | `radius` 0.5, `tube` 0.15, `segments` 16, `sides` 8 | in the XZ plane; `rot` [90,0,0] stands it up |
| `plane` | `size` [w, d] | one-sided, faces +Y; set `double_sided` on its material if seen from below |
| `wedge` | `size` [1,1,1] | ramp: tall at the back (-Z), slopes down to the front |
| `extrude` | `points` [[x, y], ...] outline seen from the front, `depth` 0.1 | blades, shields, signs, leaves, stars, letters. Outline must not self-intersect |
| `mesh` | `vertices` [[x,y,z], ...], `faces` [[i, j, k, ...], ...] counter-clockwise seen from outside | anything else; keep faces convex |

## Working method
1. Block out the silhouette first with 3-6 large parts and render `--preview-only`.
   Read the PNG; fix proportions before adding detail.
2. Add secondary shapes (trim, handles, eyes), then small detail.
3. Keep segment counts low: 6-8 for small round things, 10-16 for large ones.
   The art bible's polycount budget wins; pass it as `--max-tris`.
4. Use 3-6 materials with a deliberate palette from the art bible; low-poly
   reads through colour blocks, not texture detail.
5. Anything the game animates gets its own part with the pivot at its origin:
   make an invisible-ish tiny `box` pivot part (or a real part) at the hinge and
   parent the moving part to it with an offset `pos`.

## Pattern library
- **Round character body**: `sphere` (smooth) scaled [1, 0.85, 1]; eyes are small spheres, mirror_x.
- **Humanoid (blocky)**: box torso, box head, cylinder limbs parented to small pivot boxes at shoulders / hips so arms swing from the shoulder. Feet on y = 0.
- **Rock / boulder**: `sphere` with `segments` 6, `rings` 4, `smooth_angle` 0, non-uniform `scale`, random-looking `rot`.
- **Tree**: cylinder trunk + 2-3 stacked cones (pine) or 2-3 low-poly spheres (round tree); `merge: true`.
- **Building**: boxes for walls, `wedge` or rotated boxes for roof, thin boxes for door / window frames.
- **Crystal / gem**: `lathe` profile `[[0,0],[0.15,0.25],[0.1,0.7],[0,0.85]]`, `segments` 5-6, emissive material.
- **Coin / token**: `cylinder` radius 0.15 height 0.03 segments 12, `rot` [90,0,0], metallic gold.
- **Potion**: `lathe` bottle profile + small cylinder cork + emissive liquid lathe slightly inside.

## Limits (be honest in the report)
No UV textures, no skinned skeletons, no baked animation. Rigid-part animation
(doors, lids, wheels, turrets, swinging limbs) is done in the engine by rotating
named nodes. Organic characters, faces, cloth and anything needing sculpting are
out of scope: say so and suggest the free asset sources or an artist.
