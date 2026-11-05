# Asset Specs — Character: Spirits, Memories, Player and People

> **Source**: design/gdd/subject-spirit-behaviour.md (Rule 4 roster, Visual/Audio Requirements); design/gdd/player-movement-exploration.md (R2, Visual/Audio Requirements)
> **Art Bible**: design/art/art-bible.md (draft; not reviewed, Section 8 values are starting values per A14)
> **Generated**: 2026-11-05
> **Status**: 21 assets specced / 0 approved / 6 done / 15 needed

**art-director not consulted.** `modes.rigor: full` asks for both `art-director` and
`technical-artist`. This spec was written by technical-artist alone, and the asset list was
not confirmed with the user. Visual descriptions are anchored to the art bible, and nobody
has signed off the look. Subject GDD Open Question 8 assigns species names, lore and look to
narrative-director and art-director "before art production". These models were built ahead
of that answer, so treat their look as a proposal.

## Rules shared by every subject

| Rule | Value | Why |
|---|---|---|
| Origin | Visual centre of the body, **not** y = 0 | **Deviation from the skill's base-at-zero default.** Art bible 8.8 only names props, characters, gear and doors. Subjects float: `scale_permille` and turning must pivot on the body, and the anchor sets height. |
| Facing | +Z | Art bible 8.8. |
| Rest pose | `IDLE` (tucked) | GDD pose vocabulary. Other poses are per-node targets, listed in each recipe's `poses` table. |
| Materials | `subj_body`, `subj_glow`, `subj_face`, identical across all five | Art bible 8.4: shared palette materials. |
| `subj_body` | `#B9E8DE`, emissive `#3F716C` | 50/50 mix of Lumen and Paper White ("pale tint", 5.3). Emissive is Lumen at 50 %. |
| `subj_glow` | `#7FE3D8`, emissive `#5FAAA2` | Lumen; emissive is Lumen at 75 %. |
| `subj_face` | `#1E2230` | Darkroom Ink. Two dots at most, no mouth. |
| Glow | Engine scales emission from `glow_permille` | Opaque, no alpha (art bible 8.5). No real light. |
| Shading | `smooth_angle` 50 to 60 | Art bible 3.2. The preview PNG draws flat facets whatever the setting, so preview facets are not the final look. |
| Secondary motion | Seed from `appearance_id` and `capture_ms` | Subject GDD: no free-running timers (P4). |

**Draw-call budget.** Each part is one mesh node, so one draw call. The art bible gives the
whole characters, subjects and held-gear group **60**, and the GDD allows up to 8 subjects.
Subjects are held to **4 parts or fewer**: both eyes share one mesh, and curves are single
meshes rather than chains. Worst case 8 x 4 = 32 of 60.

## Proposed `BOUNDS_MM`

The Subject GDD names `BOUNDS_MM` per species but gives no values. These are the furthest
extents from origin in the rest pose, measured from the built models, for systems-designer
to confirm. Size follows the species, never tier (art bible 5.3).

| Species | Proposed `BOUNDS_MM` | Note |
|---|---|---|
| Puffwisp | 350 | Body radius 170; the rest is the wisp |
| Mossmote | 320 | Set by fin span |
| Driftfin | 980 | Set by tail; body alone is about 270. Scoring may want a body-only value |
| Hearth Echo | 630 | Half width of the frame |
| Halo Keeper | 360 | Set by ring; about 470 in the decisive pose |

---

## ASSET-001 — Player photographer, placeholder

| Field | Value |
|-------|-------|
| Category | 3D |
| Format | `.glb` |
| Naming | `char_player_base_01_placeholder.glb` |
| Polycount | up to 3,000 tris (art bible 8.3). Built: **1,444** |
| Texture Res | none, flat colour |
| Draw calls | **19** (see below) |
| Size | 1.75 m tall, eye at 1.60 m (Movement R2, R10), feet on y = 0 |

**Visual Description:**
A clean, stiff-jointed, flat-shaded figure in a practical jacket with a sling bag and a
camera on a neck strap. Faceless, with a simple hair cap, and approachable rather than heroic.

**This is a placeholder.** It has no skeleton and no animation. Limbs are rigid nodes with
pivots at the shoulder, elbow, wrist, hip, knee and ankle, so it can stand in for development
and can be posed in code, but it will look stiff. It must not ship; the `_placeholder` name
lets `/launch-checklist` catch it.

**Nodes:** `torso` (hip pivot), `head`, `hair`, `upper_arm`, `forearm`, `hand`, `thigh`,
`shin`, `boot` (limbs with `_mirror` copies), `bag`, `strap`, `gear_socket`, `camera_ring`.

**Held gear:** `gear_socket` is a neutral placeholder camera at 1.2x real size. The engine
hides it and attaches the owned `gear_` model there, so it carries no tier colour or brand.
`camera_ring` is the brightest detail on the figure (art bible 3.3).

**Materials (6):** `jacket` Sage, `trousers` Dusk Slate, `skin` Driftwood Clay, `ink` Ink Soft,
`strap` Sky Blue, `camera_ring` Paper White.

**Colours needing art-director input:** the palette has no skin or hair stop, so Driftwood
Clay and Ink Soft are stand-ins. Sky Blue is only a default for the player-chosen strap colour.

**Poses in the recipe:** `raise_camera` (camera at 1.60 m) and `sneak` (eye at 1.03 m, inside
the 1.05 m ± 0.15 m band; feet about 16 mm above ground).

**Budget note:** 19 draw calls x 4 players = 76, over the 60 group budget on its own. Fine for
one local player during development. It is one more reason to move to a skinned CC0 mesh
before multiplayer tests.

**Art Bible Anchors:**
- 3.3: the camera is the hero shape, about 1.2x scale.
- 5.1: everyday outdoors photographer; relaxed and grounded.
- 8.2: `_placeholder` naming. A5: this is the listed alternative, used here only as a stand-in.

**Generation Prompt:** not applicable; recipe route.

**Status:** Done (as a placeholder)

---

## ASSET-002 to ASSET-005 — Player final and clips

| ID | Asset | Route | Requirement |
|---|---|---|---|
| ASSET-002 | Final player, `char_player_base_01.glb` | CC0 pack | Rigged human, up to 3,000 tris, recoloured, flat-shaded override, realistic textures removed (art bible 5.1). Must expose a hand or chest attachment for `gear_socket`. |
| ASSET-003 | Locomotion clips | CC0 pack | Idle, walk, hurry, sneak idle, sneak walk, stand and sneak transition (0.25 s), soft landing, wade walk. No root motion; no foot skating above 0.3 m/s mismatch. |
| ASSET-004 | Camera clips | Needs an artist | Raise to eye and hold phone up (0.22 s), viewfinder idle with breathing on the body and never on the eye anchor, lower and glance at back screen (0.18 s). Specific to this game, so unlikely to be in a pack. |
| ASSET-005 | Traversal clips | CC0 pack | Ladder climb loop, scramble or vault (0.8 s). |

Readability targets (Movement GDD): sneak silhouette visibly lower at 20 m; raised-viewfinder
pose reads at 30 m. Keep the eye height at 1.60 m and 1.05 m so the third-person body matches
the first-person camera. Asset-forge cannot make any of these: it has no skinning.

**Status:** Needed

---

## ASSET-006 to ASSET-010 — NPC clients

| ID | Asset | Role prop (art bible 3.3) |
|---|---|---|
| ASSET-006 | `char_npc_client_fisher.glb` | Hat |
| ASSET-007 | `char_npc_client_shopkeeper.glb` | Apron |
| ASSET-008 | `char_npc_client_courier.glb` | Satchel |
| ASSET-009 | `char_npc_client_archivist.glb` | Clipboard |
| ASSET-010 | NPC idle clips | Idle and one small gesture |

Same CC0 base bodies as the player, up to 3,000 tris, muted Clay, Slate and Sage so they never
outshine players or subjects (art bible 5.2). **Provisional:** the Photo Pricing and Gear Shop
GDDs are not written, so the roster is a guess from the art bible's four example props.

**Status:** Needed

---

## ASSET-011, ASSET-012 — Cosmetics and wildlife

Later. Cosmetics are hats and bags from a fixed palette list, tier-free (art bible 5.1).
Wildlife uses CC0 rigged animals up to 2,500 tris and the same pose vocabulary (5.4). No
animal species is in the MVP roster.

**Status:** Needed

---

## ASSET-013 — Puffwisp

| Field | Value |
|-------|-------|
| Category | 3D |
| Format | `.glb` |
| Naming | `subj_puffwisp_base_01.glb` |
| Polycount | 400-1,200 tris. Built: **480** |
| Draw calls | 4 |
| Size | 0.34 x 0.43 x 0.52 m |

**Visual Description:**
A small round puff, heavier at the bottom, with two low-set dots for a face. A short wisp
leaves the back of the body and lifts into a soft curl, giving a comma silhouette.

**Trait:** short trailing wisp. **Nodes:** `body`, `face`, `wisp_root`, `wisp_tip`.
**Decisive pose:** `wisp_root` X -38, `wisp_tip` X -65, so the wisp opens out behind the body.

**Known weakness:** in this pose the wisp is hidden behind the body from straight in front, so the
trait does not read from that angle. It is a pose-table change, not a mesh change. The wisp tip also
stays slightly narrow for a "no hard points" shape.

**Art Bible Anchors:**
- 3.2: round, small, face low on the body, one trait.
- 5.3: pale Lumen, at most a two-dot face.

**Generation Prompt:** not applicable; recipe route.

**Status:** Done

---

## ASSET-014 — Mossmote

| Field | Value |
|-------|-------|
| Category | 3D |
| Format | `.glb` |
| Naming | `subj_mossmote_base_01.glb` |
| Polycount | 400-1,200 tris. Built: **496** |
| Draw calls | 4 |
| Size | 0.64 x 0.31 x 0.32 m |

**Visual Description:**
A low, wide bun with a flattened underside that hovers just above moss. Two broad ear-like
fins droop sideways at rest and stand tall in the decisive pose.

**Trait:** two ear-like fins. **Nodes:** `body`, `face`, `fin`, `fin_mirror`.
**Decisive pose:** `fin` Z +68, `fin_mirror` Z -68 (rest is ±22).

**Art Bible Anchors:**
- 3.2: "a pair of ear-like fins"; tucked at rest, spreading is the decisive moment.

**Generation Prompt:** not applicable; recipe route.

**Status:** Done

---

## ASSET-015 — Driftfin

| Field | Value |
|-------|-------|
| Category | 3D |
| Format | `.glb` |
| Naming | `subj_driftfin_base_01.glb` |
| Polycount | 400-1,200 tris. Built: **512** |
| Draw calls | 4 |
| Size | 0.18 x 0.28 x 1.25 m |

**Visual Description:**
A slender teardrop body with a soft nose, running into a long, flat ribbon tail that is more
than half the length. Reads as a gentle fish-like shape without any sharp fin points.

**Trait:** long tail fin. **Nodes:** `body`, `face`, `tail_root`, `tail_tip`.
**Decisive pose:** `body` X -8, `tail_root` X +20, `tail_tip` X +26, lifting the tail.

**Art Bible Anchors:**
- 3.2: "a long tail"; teardrop form; no hard points.

**Generation Prompt:** not applicable; recipe route.

**Status:** Done

---

## ASSET-016 — Hearth Echo (memory)

| Field | Value |
|-------|-------|
| Category | 3D |
| Format | `.glb` |
| Naming | `subj_hearth_echo_base_01.glb` |
| Polycount | 400-1,200 tris. Built: **948** |
| Draw calls | 3 |
| Size | 1.27 x 0.97 x 0.09 m |

**Visual Description:**
A 4:3 frame of faded light with soft corners, empty except for a half-seen scene hanging
inside it: a doorway arch, a floor line and two seated figures. The right third has already
dissolved into motes. No face, because a memory is not a creature, and it stays still.

**Trait:** empty frame around a half-seen scene. **Nodes:** `frame`, `scene`, `motes`.
**Poses:** `decisive` moves `scene` and `motes` forward. `fading` scales `frame` to Y 0.12 as
the "scale fold" the GDD allows; `scene` and `motes` inherit it. Hearth Echo uses two of the
three shared materials (`subj_face` is unused).

**Risk:** the frame is thin edge-on (about 0.09 m), so a shot from the side loses the subject.
Level design should give each anchor a clear front view, and the Photo Scoring GDD may need
to treat facing as part of "recognisable".

**Art Bible Anchors:**
- 6.4: spirit traces, empty frames with a Lumen shimmer.
- 8.5: opaque with emissive; the scene floats in the opening with no alpha panel behind it.

**Generation Prompt:** not applicable; recipe route.

**Status:** Done

---

## ASSET-017 — Halo Keeper

| Field | Value |
|-------|-------|
| Category | 3D |
| Format | `.glb` |
| Naming | `subj_halo_keeper_base_01.glb` |
| Polycount | 400-1,200 tris. Built: **924** |
| Draw calls | 3 |
| Size | 0.72 x 0.61 x 0.70 m |

**Visual Description:**
A soft, upright bell with a gently narrowed head, like a small lantern-keeper. A slim Lumen
ring tilts around its middle and turns slowly.

**Trait:** a slow ring orbiting the body. **Nodes:** `body`, `face`, `ring`.
**Motion:** spin `ring` about its own local Y. **Decisive pose:** ring rises, levels and spreads
to scale 1.3 (`pos` Y +0.06, `rot` [4, 0, 3]).

**Art Bible Anchors:**
- 3.2: "a ring around the body".
- 5.3: tier A stays one body and one trait; second orbiting parts start at S.

**Generation Prompt:** not applicable; recipe route.

**Status:** Done

---

## ASSET-018 — Capture Encounter set-piece subject

Not specced. The Subject GDD defers this subject to the Capture Encounter GDD, which is not
started. Route is asset-forge if it follows the rigid-part rules.

**Status:** Needed

---

## ASSET-019 to ASSET-021 — Disabled high-tier subjects

| ID | Asset | Tier | Build notes |
|---|---|---|---|
| ASSET-019 | `subj_driftfin_gilded_01.glb` | S | Driftfin plus a second orbiting part |
| ASSET-020 | `subj_vesper_halo_base_01.glb` | SS | Ring, orbiting part, trailing wisp; up to 2,000 tris |
| ASSET-021 | `subj_aurora_drifter_base_01.glb` | SSS | Large and slow, two orbiting parts, long wisp; up to 2,000 tris |

These cannot spawn while `enabled_cap = "A"`, so they are Later. Each added part costs one
draw call; the 4-part rule above does not hold at these tiers and needs its own allowance.

**Status:** Needed

---

## How to rebuild

Recipes sit beside the models in `assets/art/models/`, as requested. Shape data comes from
`design/assets/tools/character_recipes.py`, so edit that file and re-run it; a re-run
overwrites hand edits to the JSON.

**Recipe location conflict:** art bible 8.1 and the asset-forge skill put recipes in
`design/assets/recipes/`, which `export_presets.cfg` keeps out of the build. Under `assets/`
they fall under `all_resources`, so the `.json` files may ship in the Web export (about 65 KB;
not tested). Decided 2026-11-05: recipes moved to `design/assets/recipes/`.
