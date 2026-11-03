# asset-forge - a Claude Code skill

Generates game assets using only Claude Code: Claude writes recipes, bundled
Python scripts turn them into files, and Claude checks rendered previews.
No image/3D/audio APIs, no extra keys.

Makes: low-poly 3D models (.glb), pixel-art sprite sheets, SVG UI and icons,
seamless textures with normal maps, sound effects, and chiptune music loops.
Designed to follow `/asset-spec` from Claude Code Game Studios, but works with a
plain description too.

## Install
Copy this folder into your game project:

```
<your-project>/.claude/skills/asset-forge/
```

Requirements: Python 3.8+ (standard library only).
Optional: `ffmpeg` (OGG output), `rsvg-convert` / Inkscape / ImageMagick (SVG to PNG).

## Use
```
/asset-forge                      # pick from Needed assets in the manifest
/asset-forge ASSET-007            # one asset from /asset-spec
/asset-forge spec:forest-level    # every Needed asset in that spec file
/asset-forge "a wooden treasure chest with gold trim, low-poly"
```

Recipes are saved to `design/assets/recipes/` so any asset can be tweaked and
regenerated later. Previews go to `design/assets/previews/`.

## Limits
Low-poly / stylised only. No textured UV-mapped models, skeletal rigs, painterly
art, voice, or orchestral music; the skill reports those as out of scope and
suggests CC0 sources or an artist instead.
