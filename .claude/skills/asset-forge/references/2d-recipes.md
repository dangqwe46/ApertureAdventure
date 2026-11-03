# 2D assets: pixel sprites, SVG, textures

## Choosing the route
| Spec says | Route |
|---|---|
| pixel art, retro, 8/16/32 px, sprite sheet, tiles | `pixel_sprite.py` |
| UI icons, buttons, HUD, logos, flat / vector style, cards, menus | hand-written **SVG** (+ `svg_raster.py` if PNG needed) |
| ground / wall / floor textures for 3D, seamless backgrounds | `texture_gen.py` |
| painterly, photo-real, detailed illustration | out of scope: report it, suggest free sources or an artist |

## Pixel sprites (`pixel_sprite.py`)
- Pick the palette from the art bible. Keep it small (4-16 colours), with one
  dark outline colour, a base, a shadow and a highlight per material.
- Draw at the native size in the spec (16x16, 32x32...). Keep a 1 px transparent
  border if you use `outline`.
- Use `symmetric` for front-facing characters and items: write the left half only.
  `even` mirrors every column (16 px wide from 8); `odd` shares the centre column.
- Animation frames: same size each. Idle = 2-4 frames with a 1 px squash or bob
  (`"shift": [0, 1]` on a `copy` frame is the cheapest bob). Walk = 4-6 frames.
- Light from the top-left: highlights on top/left edges, shadow bottom/right.
- Avoid "pillow shading" (shading every edge inward); avoid single stray pixels.
- Output also writes `<name>.json` with frame size, count, durations and an
  fps hint for Godot `SpriteFrames` / Unity sprite slicing.
- Always render `--preview` and look at it before reporting done.

Tilesets: make each tile a frame and set `columns` to the tileset width; the
sheet is then a regular grid ready for a Godot `TileSet` atlas.

## SVG (written directly by Claude)
- Set `viewBox` to the target size (e.g. `0 0 64 64`) and `width`/`height` to match.
- Use the art bible palette as hex fills; a consistent stroke width
  (e.g. 2-3 px at 64 px) gives a set of icons one family look.
- Build from simple shapes (`rect` with `rx`, `circle`, `path`) and keep it
  readable at the smallest display size; check by rasterising at that size.
- No embedded raster images, no external fonts (convert text to paths or avoid it).
- Godot 4 imports `.svg` directly (set the import scale for crisp UI). For PNG:
  `python3 svg_raster.py icon.svg -o icon_64.png --size 64`.

## Seamless textures (`texture_gen.py`)
Presets: grass, dirt, sand, stone, snow, water, lava, bricks, planks, tiles,
cobble, scales. Override `stops` with art-bible colours via a recipe:

```json
{ "preset": "bricks", "seed": 3, "rows": 6, "cols": 3,
  "stops": [[0, "#4a5a6a"], [0.6, "#5f7183"], [1, "#7a8ea2"]], "mortar": "#2c3036" }
```

- Sizes must be powers of two; 256 is plenty for low-poly / web, 512 for close-ups.
  Pure Python is slow above 512.
- `--normal file_n.png` adds a normal map (OpenGL / Y+, Godot's convention;
  Unity's import "normal map" type expects the same).
- Different `seed` = different variant with the same look.
