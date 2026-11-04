# Aperture: Project Context

Working title: **Aperture**. Project folder: `D:\Work\ApertureAdventure`.
Built with Claude Code Game Studios (CCGS). This file is the hand-off from the chat where the concept was designed. Read it first, then `design/gdd/game-concept.md` (full concept; also as `design/gdd/aperture-game-concept.html`).

## Status

- Concept drafted (2026-11-03). **No engine configured, no GDDs, no code, no assets yet.**
- `project.yaml` and `CLAUDE.md` are still the studio template defaults. `/setup-engine` has not been run.
- The `asset-forge` skill is installed in `.claude/skills/asset-forge/`.

## What the user decided

- An RPG about photography that runs in a **web browser**, with **3D** possible (not only 2D).
- **Online**, with multiple users playing together.
- **Gear trading:** camera bodies and lenses with real-world style specs and mounts (focal length, maximum aperture f/, sensor and so on), "with the same real-world assets".
- **Photo evaluation:** each photo is rated and scored.
- **Leaderboard:** top 100 images by score, showing the image and its owner.
- **Start choice:** players begin with a phone or a camera, each with a cost. They capture photos and sell or trade them to upgrade gear.
- **Rarity tiers (for example C to SSS) for both gear and images.** A high-tier image needs high-tier gear (body and lens both SSS for an SSS image) plus subject, moment and light parameters. The chance to capture a high tier is a ratio. Images are unique, and gear has a limited supply based on its tier.
- Assets should be generated from scratch using only the Claude Code subscription, with no extra paid services.

## Decided later (2026-11-03)

- **Brands:** invented camera brands (e.g. Nokta, Kanro, Fujin) that copy real mount logic and specs. No real brand names.
- **Tone and setting:** cozy and reflective; forgotten memories and shy spirits that only appear through a lens, with no violence.
- **Engine:** Godot 4.7.2, GDScript, 3D, Web export with the Compatibility renderer (configured).

## Proposals from the chat that the user has NOT confirmed

- Selling photos to NPC clients first, with player-to-player trading later.
- Capture rule: image tier = the lowest of gear ceiling, subject, moment, light and skill limits, then a roll against the odds.
- Seasonal supply caps, gear wear and crafting, and first-claim on top-tier subjects with shared crew credit.

## Open questions

See "Open questions" in `design/gdd/game-concept.md` (brands, player-to-player selling, phone path, camera cost, tone, supply cap scope, broken gear, first-claim rule).

## Technical notes to remember

- The Godot reference in `docs/engine-reference/godot/modules/networking.md` uses ENet, which does **not** work in web exports. Use WebSocket or WebRTC with a server-authoritative design.
- A photo is stored as a recipe (camera position, settings, time of day, subject pose), not an image. The server recalculates scores and owns inventories, prices, rarity rolls and supply counters.
- Keep the art low-poly and light for the web build.

## Skills and tools

- `/asset-forge` (in `.claude/skills/asset-forge/`) makes low-poly `.glb` models, pixel sprites, SVG UI, seamless textures, sound effects and chiptune music from recipes, using only Python 3 (standard library). Run `/asset-spec` first so it has specs to work from. Audio can't be previewed by Claude, so it always needs a human listen.
- Optional extras: `ffmpeg` for OGG output, and `rsvg-convert`, Inkscape or ImageMagick for SVG to PNG.
- Out of scope for the skill: realistic or organic characters, rigged animation, painterly art, voice and orchestral music. Use CC0 packs (Kenney, Quaternius, Poly Haven) or an artist for those.

## Suggested next steps

1. Run `/start` and say you already have a concept in `design/gdd/game-concept.md`.
2. `/setup-engine`: Godot, 3D, Web target.
3. `/art-bible`, then `/map-systems` and `/design-system` for scoring, the economy, rarity and networking.
4. `/asset-spec`, then `/asset-forge`.
