# Asset Specs — Character: Spirits, Memories, Player and People

> **Source**: design/gdd/subject-spirit-behaviour.md (Rule 4 roster, Visual/Audio Requirements); design/gdd/player-movement-exploration.md (R2, Visual/Audio Requirements)
> **Art Bible**: design/art/art-bible.md (draft; not reviewed, Section 8 values are starting values per A14)
> **Generated**: 2026-11-05. **Updated**: 2026-11-07 for the 3D stylized Quaternius direction (art bible Revision 2026-11-05, 5.1 to 5.4, 8.3, 8.10 to 8.12)
> **Status**: 23 assets specced / 0 approved / 5 restyle proposals / 1 superseded / 17 needed

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

## Restyling the subjects for the textured world (proposal)

ASSET-013 to 017 were built for the old flat direction. They stay as proposals. Art bible 5.3
says spirits must not imitate the kit, so restyling means contrast, not added texture:

| Change | Rule (art bible 5.3) | State of the current models |
|---|---|---|
| Keep them untextured | Spirits read as "not of this world" against painted surfaces | Already so; asset-forge has no UVs |
| Smooth shading | `smooth_angle` 30 to 60 | Already 50 to 60 |
| Brighter than anything around them | Highest value in the scene | Not tested. Any colour change is for art-director |
| Soft rim on busy texture | Edge stays clear | Needs ASSET-087 |
| Answer the scene's light | Warmer on the sun side at golden hour | Needs ASSET-087 |
| Greyscale test (6.5) | Pass against the busiest kit surfaces, not plain ground | Not run |

The work is mainly shader and material, and geometry may not need to change. The materials in
the table above are unchanged until art-director decides. Recipes are in
`design/assets/recipes/`; the `.glb` files exist only on the `dev` branch, not on `document`.

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

**Superseded by ASSET-002.** Kept for the record only: the old budget of 3,000 tris and the
flat-colour materials below no longer apply. Do not use it.

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

**Status:** Superseded

---

## Character source (ASSET-002, 006 to 009)

All files are in `D:/Tools/downloads-quaternius/`. Third-party files stay out of git (art bible
8.11, 8.12). Characters keep their textures, at 512 px base colour, no normal map (8.6).

| Part | Source | Notes |
|---|---|---|
| Head | `Superhero_Male_FullBody.gltf`, `Superhero_Female_FullBody.gltf` | **The pack has no head-only mesh**, and the outfit readme says to use only the head. The body mesh must be trimmed, which is a new pipeline step |
| Hair | `Hairstyles/Rigged to Head Bone/glTF (Godot -Unreal)/` | 8 pieces: Hair_SimpleParted 1,301, Hair_Buzzed 830, Hair_BuzzedFemale 830, Hair_Long 2,906, Hair_Buns 3,284, Hair_Beard 1,034, Eyebrows_Regular 984, Eyebrows_Female 1,480 |
| Outfit | `Exports/glTF (Godot-Unreal)/Outfits/` or `Modular Parts/` | Peasant and Ranger, male and female |
| Colour variants | `Textures/Peasant/T_Peasant_2_BaseColor.png`, `Textures/Ranger/T_Ranger_3_BaseColor.png` | One extra colour map each |
| Clips | `Unreal-Godot/UAL1_Standard.glb` | No root motion, as Movement requires. `_RM` is the root-motion copy |

**Rig match (read from the files):** bases, all four outfits and `UAL1_Standard.glb` share the
same 65 joint names in the same order. That is not proof of fit: nothing has been tested
together in Godot, which art bible 5.1 asks for.

**Size:** the male base is 1.81 m and the female 1.77 m, against the 1.75 m and 1.60 m eye height
in Movement R2 and R10. Either scale the bodies or accept the difference. Eye height on the
pack heads has not been measured.

**Skin:** outfit hands use `T_Regular_*_Dark` maps only, while the bases also have Light maps,
so a Light head would not match its hands until a Light hand map exists.

### Triangle budget (measured)

Budget: **15,000 near, 5,000 at LOD1** (art bible 8.3). Head counts are estimates: triangles
whose vertices are mainly weighted to `Head` or `neck_01`. Each total adds head, eyes (768),
eyebrows and one hair piece.

| Build | Outfit | Head | Brows | Hair | Total | Over by |
|---|---|---|---|---|---|---|
| Male Peasant, parted hair | 12,894 | 2,852 | 984 | 1,301 | **18,799** | 3,799 |
| Female Peasant, buzzed hair | 13,568 | 3,070 | 1,480 | 830 | **19,716** | 4,716 |
| Female Peasant, long hair | 13,568 | 3,070 | 1,480 | 2,906 | **21,792** | 6,792 |
| Male Ranger, modular body, arms, legs, Peasant feet, parted hair | 13,250 | 2,852 | 984 | 1,301 | **19,155** | 4,155 |
| Male Ranger, full outfit with hood, no hair | 26,982 | 2,852 | 984 | 0 | **31,586** | 16,586 |

Heaviest parts: Ranger boots 9,172, Ranger bracers 3,636 (full outfit only), Female Peasant arms
6,848, male hands and forearms 3,930. **No build fits.** Options, both needing a decision:

1. Reduce the meshes. Blender was not found on this machine, so this needs a tool or an artist.
2. Raise the budget. The cost lands on the character share of the scene total: 4 near characters
   at 15,000 is already 60,000, against 20,000 in the 8.3 split.

**Draw calls:** a Peasant build is 9 surfaces as supplied (5 outfit, then head, eyes, brows, hair).
4 players plus 8 subjects at 4 parts is 68, over the group budget of 60 (8.4). Merging outfit
surfaces by material gives 6 each, or 56, which leaves 4 for NPCs and held gear. NPCs at LOD1
need the same merge. The shadow pass adds more.

---

## ASSET-002 — Player photographer, final

| Field | Value |
|-------|-------|
| Route | Quaternius pack |
| Naming | `char_player_base_01.gltf` (8.1, 8.2), male and female bases |
| Priority | First playable: ASSET-001 no longer covers that tier |

**Outfit is for art-director to pick.** The closest pack match to "practical jacket" (5.1) looks
like the Ranger body and arms without pauldron or hood, with Peasant feet to avoid the 9,172 tri
boots. That mix uses two texture sets and needs a fit test. Peasant alone is the fallback, and
is the lightest build. Nothing medieval should show (6.1), so leave out pauldrons.

**Held gear:** attach the owned `gear_` model to the `hand_r` bone or a chest point, at about 1.2x
scale (3.3), so the camera stays the hero shape. `camera_ring` stays the brightest detail.

**Customisation (5.1):** jacket colour from the variant maps or a tint, hat and bag from ASSET-011,
strap colour on the held gear. All cosmetic, never tier.

**Status:** Needed

---

## ASSET-003 to ASSET-005, ASSET-173 — Player clips

| ID | Need | Source | State |
|---|---|---|---|
| ASSET-003 | Idle | UAL1 `Idle_Loop` | Available |
| ASSET-003 | Walk | UAL1 `Walk_Loop` | Available |
| ASSET-003 | Hurry | UAL1 `Jog_Fwd_Loop` | Available |
| ASSET-003 | Sneak idle | UAL1 `Crouch_Idle_Loop` | Available |
| ASSET-003 | Sneak walk | UAL1 `Crouch_Fwd_Loop` | Available |
| ASSET-003 | Stand and sneak transition (0.25 s) | Blend between clips in Godot | No clip needed |
| ASSET-003 | Soft landing | UAL1 `Jump_Land` | Available |
| ASSET-003 | Wade walk | UAL1 `Walk_Loop`, slowed | Stand-in |
| ASSET-004 | Raise to eye, hold phone up (0.22 s) | none | **No free source** |
| ASSET-004 | Viewfinder idle, breathing on the body, never on the eye anchor | none | **No free source** |
| ASSET-004 | Lower and glance at back screen (0.18 s) | none | **No free source** |
| ASSET-005 | Scramble or vault (0.8 s) | UAL2 Standard `CLIMBUP 1M` | Pack needed; clip length unknown |
| ASSET-173 | Ladder climb loop | none | **No free source** |

No foot skating above 0.3 m/s mismatch, which needs checking at Movement's speeds. Clips with no
free source stay `Needs an artist`.

**Fallback to test for ASSET-004 and ASSET-173:** IK on the arms over an idle or crouch clip,
with hand targets on the held gear or ladder rungs. `docs/engine-reference/godot/modules/animation.md`
lists `TwoBoneIK` under `SkeletonModifier3D` as new in 4.6; the reference gives no exact API, so
verify it against the 4.7.2 docs before use. UAL1 `Pistol_Aim_Neutral` may do as a test pose;
it has not been viewed. UAL2 `IDLE_TALKING PHONE` is named as a phone call, so it is unlikely to
fit holding a phone up.

Readability targets (Movement GDD): sneak silhouette visibly lower at 20 m; raised-viewfinder
pose reads at 30 m. Keep the eye height at 1.60 m and 1.05 m so the third-person body matches
the first-person camera. Asset-forge cannot make any of these: it has no skinning.

**Status:** Needed

---

## ASSET-006 to ASSET-010, ASSET-174 — NPC clients

| ID | Asset | Proposed base | Role prop (art bible 3.3) |
|---|---|---|---|
| ASSET-006 | `char_npc_client_fisher.gltf` | Male Peasant | Hat |
| ASSET-007 | `char_npc_client_shopkeeper.gltf` | Female Peasant | Apron |
| ASSET-008 | `char_npc_client_courier.gltf` | Male Peasant, `T_Peasant_2` | Satchel |
| ASSET-009 | `char_npc_client_archivist.gltf` | Female Peasant, `T_Peasant_2` | Clipboard |
| ASSET-010 | NPC idle clips | UAL1 `Idle_Loop`, `Idle_Talking_Loop`, `Sitting_Idle_Loop` | n/a |
| ASSET-174 | `prop_role_*_01.glb` | asset-forge, rigid parts on bones | All four |

Same bases and outfits as the player, with a muted palette (Clay, Slate, Sage) so they never
outshine players or subjects (art bible 5.2). The budget above applies. UAL2 `IDLE_FOLD ARMS` and
`IDLE_RAIL` would add variety if that pack is downloaded.

**Role props are a weak spot.** No hat, apron or clipboard is in the installed packs. asset-forge
parts are rigid and untextured, which may look stiff, and an apron is the worst case because it
must follow the legs (bible 5.1 raised this risk). Fantasy Props shows a satchel in its preview.

**Provisional:** the Photo Pricing and Gear Shop GDDs are not written, so the roster is a guess
from the art bible's four example props.

**Status:** Needed

---

## ASSET-011, ASSET-012 — Cosmetics and wildlife

Later. Cosmetics are hats and bags from a fixed palette list, tier-free (art bible 5.1), made as
asset-forge rigid parts. Wildlife candidates are in the Ultimate Animated Animal Pack (12 animals,
glTF, not downloaded). Budget up to 5,000 tris, and the same pose vocabulary (8.3, 5.4). The site
flags that pack as not textured, so bible 5.4's check against the textured world applies. No
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

**Status:** Restyle proposal

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

**Status:** Restyle proposal

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

**Status:** Restyle proposal

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

**Status:** Restyle proposal

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

**Status:** Restyle proposal

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
