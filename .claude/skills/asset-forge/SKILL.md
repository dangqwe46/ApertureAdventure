---
name: asset-forge
description: "Generate game assets with code only - low-poly 3D models (.glb), pixel sprites, SVG UI, seamless textures, sound effects and chiptune music - from /asset-spec specs or a plain description. No external APIs or keys. Use after /asset-spec, or when the user asks to make, generate or create art, models, sprites, icons, textures, SFX or music."
argument-hint: "[ASSET-NNN | spec:<target> | \"free-text description\"]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(python3 *), Bash(python *), Bash(py *)
---

# Asset Forge

Claude cannot paint pixels or sculpt meshes directly, but it can write code and
data that produce them. This skill turns an asset spec into a **recipe** (JSON or
SVG), runs a bundled generator, **looks at a rendered preview**, and iterates until
the result matches the spec. Everything runs locally with Python 3 standard
library; nothing calls an external service, so it costs nothing beyond the
Claude Code subscription.

Generators (in `${CLAUDE_SKILL_DIR}/scripts/`):

| Script | Makes | Reference |
|---|---|---|
| `model_glb.py` | low-poly 3D `.glb` + 4-view PNG preview | `references/model-recipes.md` |
| `pixel_sprite.py` | pixel-art sprite / sheet `.png` + frame `.json` + preview | `references/2d-recipes.md` |
| *(none - write SVG directly)* | vector UI, icons, HUD; `svg_raster.py` for PNG | `references/2d-recipes.md` |
| `texture_gen.py` | seamless textures `.png` (+ normal map) | `references/2d-recipes.md` |
| `sfx_synth.py` | sound effects `.wav` / `.ogg`, with variants | `references/audio-recipes.md` |
| `music_synth.py` | seamless music loops `.wav` / `.ogg` | `references/audio-recipes.md` |

Working examples are in `${CLAUDE_SKILL_DIR}/examples/`. Read the reference file
for a route before writing its first recipe in a session.

---

## Phase 0: Resolve what to make

- `ASSET-NNN` -> find that ID: `Grep pattern="ASSET-NNN" path="design/assets"`, read its block in the spec file.
- `spec:<target>` -> read `design/assets/specs/<target>-assets.md`; take every asset whose **Status** is `Needed`.
- Free text -> treat it as a one-off spec. Ask for anything essential that is missing (size / style / format) in one `AskUserQuestion`; otherwise choose sensible defaults and state them.
- No argument -> read `design/assets/asset-manifest.md`, list the `Needed` rows, and ask which to make (offer the first 3 plus "all of one spec file").
- No manifest and no spec -> say `/asset-spec` produces the specs this skill works best from, and offer to proceed from a description instead.

## Phase 1: Gather constraints

Read, if they exist (do not fail if they don't - note what was missing):

1. `design/art/art-bible.md` - palette (hex values), shape language, polycount and texture-resolution tiers, naming rule.
2. The asset's spec block - Category, Dimensions, Format, Naming, Polycount, Texture Res, Visual Description, Art Bible Anchors. The **Generation Prompt** is useful as a description of intent; ignore its image-model keywords.
3. `project.yaml` - which engine (Godot / Unity / other) and whether the target includes web. Web or mobile targets mean tighter budgets: prefer `merge: true` models, 256 px textures, few materials.

Check Python once: `python3 --version` (on Windows try `python --version` or `py --version`, and use that command for every script below).

## Phase 2: Route each asset

| Spec says | Route |
|---|---|
| 3D, model, prop, environment piece, low-poly character, weapon, vehicle | `model_glb.py` |
| Sprite, pixel art, tileset, 2D character / item / effect frames | `pixel_sprite.py` |
| UI, icon, HUD, button, logo, vector / flat art | SVG written directly |
| Texture, material, ground / wall / floor surface, seamless background | `texture_gen.py` |
| SFX, sound | `sfx_synth.py` |
| Music, ambient loop, stinger | `music_synth.py` |

**Out of scope** (do not pretend): realistic or organic sculpted characters,
skinned rigs and baked skeletal animation, painterly / photo-real images, voice,
orchestral or vocal music. Mark these `NOT GENERATED - out of scope` and offer
the options in `references/free-sources.md` (including a clearly named
placeholder so work can continue).

Output paths and names follow `references/engine-import.md` and the spec's
**Naming** field; if neither gives one, use CCGS's pattern
`[category]_[name]_[variant]_[size].[ext]` (art) or
`[category]_[context]_[name]_[variant].[ext]` (audio), lowercase with underscores.

## Phase 3: Confirm the plan

Show a short table - asset ID, name, route, output path, budget - and ask with
`AskUserQuestion`: "May I generate these and write them to `assets/` (recipes to
`design/assets/recipes/`)?" Options: `[A] Yes, all` / `[B] Only some` / `[C] Change something`.
Writing into `assets/` and `design/` always needs this yes, whatever the
automation mode.

## Phase 4: Make each asset

For each asset:

1. **Write the recipe** to `design/assets/recipes/<asset_name>.json` (SVG goes
   straight to its asset path). The recipe is the source of truth: small edits +
   re-run beat starting over, and the user can tweak it later.
2. **Generate** with the script (`--help` on any script shows its options):
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/model_glb.py" design/assets/recipes/prop_chest.json \
     -o assets/art/models/prop_chest.glb --preview design/assets/previews/prop_chest.png --max-tris 800
   python3 "${CLAUDE_SKILL_DIR}/scripts/pixel_sprite.py" design/assets/recipes/char_slime_idle.json \
     -o assets/art/sprites/char_slime_idle.png --preview design/assets/previews/char_slime_idle.png
   python3 "${CLAUDE_SKILL_DIR}/scripts/texture_gen.py" --recipe design/assets/recipes/tex_wall.json --size 256 \
     -o assets/art/textures/tex_wall_256.png --normal assets/art/textures/tex_wall_256_n.png
   python3 "${CLAUDE_SKILL_DIR}/scripts/sfx_synth.py" --recipe design/assets/recipes/sfx_player_jump.json \
     --variants 3 --ogg -o assets/audio/sfx/sfx_player_jump.wav
   python3 "${CLAUDE_SKILL_DIR}/scripts/music_synth.py" design/assets/recipes/music_menu_loop.json \
     --ogg -o assets/audio/music/music_menu_theme_loop.wav
   ```
   For 3D, iterate on the shape with `--preview-only` first (fast), then build the .glb.
3. **Look at it.** Read the preview PNG (for SVG, rasterise to a preview with
   `svg_raster.py` and read that). Compare against the spec's description,
   silhouette and palette. Name what is wrong and fix the recipe. Up to **3
   rounds**; if it still misses, stop and report what is off rather than looping.
4. **Audio cannot be previewed by Claude.** Check the script output (duration,
   no errors), sanity-check parameters against the description, and mark audio
   `NEEDS LISTEN` - the user must play it.

Preview PNGs live in `design/assets/previews/` so they are not shipped as game assets.

## Phase 5: Verify and report

For each asset, check what can be checked and say plainly what could not:

- File exists at the planned path, name follows the naming rule.
- 3D: triangle count within the polycount budget (`--max-tris`), origin / base sits at y = 0 unless the spec says otherwise (script prints `min y`).
- Textures / sprites: power-of-two where the art bible requires it, size matches the spec.
- Audio: format matches the spec (OGG if requested - if ffmpeg was missing, say OGG conversion **did not run**).

Report as a table with one verdict per asset:

| Verdict | Meaning |
|---|---|
| `DONE` | generated, previewed, checks passed |
| `NEEDS LISTEN` / `NEEDS REVIEW` | generated, but a human must judge it (all audio; anything Claude was unsure about) |
| `NOT ASSESSED - <reason>` | generated, but a check could not run (e.g. no budget in spec or art bible) |
| `NOT GENERATED - <reason>` | out of scope or failed after 3 rounds; give the alternative |

Never report `DONE` for something whose preview you did not read.

## Phase 6: Update the manifest and hand off

If `design/assets/asset-manifest.md` exists, ask "May I update the manifest?"
then set generated assets to `In Progress` (or `Done` if the user has looked
and agreed). Never set `Approved` - that belongs to the art director / user.
Update the spec file's **Status** lines and its summary counts the same way.

Close with next steps: open the assets in the engine (see
`references/engine-import.md`), play the audio, then run `/asset-audit` to check
naming, sizes and formats across the project.

## Rules

- Recipes over one-off scripts: never hand-edit generated binaries; change the recipe and regenerate.
- Stay on the art bible's palette and shape language; consistency across a set matters more than detail in one asset.
- Keep budgets small for web targets.
- Never download, call an image / audio / 3D generation API, or install packages as part of this skill. Scripts need only Python 3; ffmpeg and an SVG rasteriser are optional extras that the skill reports on when absent.
