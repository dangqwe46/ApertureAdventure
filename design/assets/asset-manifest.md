# Asset Manifest

> Last updated: 2026-11-07, for the 3D stylized Quaternius direction (art bible Revision 2026-11-05, 8.10 to 8.12)
> Inventory: design/assets/entity-inventory.md
> **Every route here is a proposal.** Pack contents were read from the files on disk. Nothing has been imported or tested in Godot, and art-director has not reviewed this plan.

## Progress Summary

**Nothing is Done under the new direction.** All 174 IDs are kept: 169 active, 1 superseded, 4 retired. ASSET-172 to 174 are new splits.

| Total IDs | Active | Needed | Restyle proposal | Superseded | Retired |
|---|---|---|---|---|---|
| 174 | 169 | 164 | 5 | 1 | 4 |

| Priority | IDs | Needed | Restyle proposal | Superseded | Retired |
|---|---|---|---|---|---|
| First playable | 51 | 44 | 5 | 1 | 1 |
| MVP | 104 | 101 | 0 | 0 | 3 |
| Later | 19 | 19 | 0 | 0 | 0 |

Active rows by route:

| Route | Assets |
|---|---|
| Quaternius pack | 37 |
| asset-forge recipe | 104 |
| Engine-built | 20 |
| Needs an artist | 4 |
| OFL font | 2 |
| CC0 audio pack | 2 |

Active rows by availability:

| Available | Assets | Meaning |
|---|---|---|
| Now | 31 | Every source file is on disk in `D:/Tools/downloads-quaternius/` |
| Pack needed | 10 | Needs a free pack or font not downloaded yet |
| No free source | 4 | No free pack on disk or on the candidate list has it |
| Made here | 124 | Built in-house with asset-forge or Godot, so it needs no outside file |

## Key

**Priority.** `First playable` = the smallest set that lets one player walk the area, raise the lens, photograph a subject and see the darkroom result. `MVP` = the rest of the concept's "First playable version" list and the MVP rows of the systems index. `Later` = Vertical Slice onward, or disabled data. The concept calls its whole MVP scope "first playable"; this manifest splits it, which is an assumption (see the inventory). ASSET-002 and 003 moved to First playable, because the placeholder that covered that tier is superseded.

**Rows.** A row can be a small set that is produced together (badge set, footsteps, clip sets). Split it when work starts; new IDs continue from the highest in use. IDs are never reused or renumbered.

**Route.** `Quaternius pack` = a free Standard pack, used directly or kit-bashed from named pieces. `asset-forge recipe` = generated locally; models have no UVs, so they are untextured (`Needed` audio always needs a human listen). `Engine-built` = made in Godot by technical-artist or godot-shader-specialist. `Needs an artist` = no free source and out of scope for code. `OFL font` = SIL Open Font License. `CC0 audio pack` = free ambience, source not chosen.

**Status.** `Needed` = not made for this direction. `Restyle proposal` = a self-made model kept as a proposal, to restyle for the textured world (see the character spec). `Superseded` = kept for the record, not to be used. `Retired` = no longer a deliverable; the ID stays reserved.

**Source paths.** `Nature/` = `Stylized Nature MegaKit/`. `Village/` = `Medieval Village MegaKit/Medieval Village MegaKit[Standard]/`. `UBC/` = `Universal Base Characters/Universal Base Characters[Standard]/`. `UAL1/` = `Universal Animation Library/Universal Animation Library[Standard]/`. `Outfits/` = `Modular Character Outfits/Modular Character Outfits - Fantasy[Standard]/`. All sit under `D:/Tools/downloads-quaternius/`. Kit piece names omit `.gltf`.

**File names.** Art bible 8.1 changed world and character models from `.glb` to `.gltf` + `.bin` as supplied, renamed to 8.2 on import. Gear and spirits stay `.glb`. **`.tscn` is a proposal, not a bible rule:** rows assembled from kit pieces are Godot scenes merged per material (8.4), because no Blender install was found on this machine. Bible 8.2 still shows `env_lighthouse_main_large.glb` as an example.

## Pack Log

Art bible 8.2 and 8.11. Licence wording is from each pack's own file. Dates are the zip file dates. Page URLs checked 2026-11-07.

| Pack (Standard) | Page | Licence file | Downloaded | Real contents |
|---|---|---|---|---|
| Stylized Nature MegaKit | https://quaternius.com/packs/stylizednaturemegakit.html | `License_Standard.txt`: CC0 1.0 | 2026-11-05 | 68 glTF models (the file says 68 of 116) |
| Medieval Village MegaKit | https://quaternius.com/packs/medievalvillagemegakit.html | `License_Standard.txt`: CC0 1.0 | 2026-11-05 | 176 glTF models, 2k texture sets |
| Universal Base Characters | https://quaternius.com/packs/universalbasecharacters.html | `License_Standard.txt`: CC0 1.0 | 2026-11-05 | 2 full bodies, 8 head pieces (6 hair, 2 eyebrow). No head-only mesh |
| Universal Animation Library | https://quaternius.com/packs/universalanimationlibrary.html | `License.txt`: CC0 1.0 | 2026-11-05 | 43 clips, in `UAL1_Standard.glb` and root-motion `UAL1_Standard_RM.glb` |
| Modular Character Outfits - Fantasy | https://quaternius.com/packs/modularcharacteroutfitsfantasy.html | `License_Standard.txt`: CC0 1.0 | 2026-11-06 | Peasant and Ranger, male and female: 4 outfits, 20 parts |

The working rule in bible 8.11 covers the site's newer Quaternius Asset License as well: ship inside the game build only, never as a pack or mirror.

## Free Pack Candidates (not downloaded)

Read from the site on 2026-11-07. "Textured" is the site's own flag. Contents come from preview images, so exact file names are unknown until download.

| Pack | Free content | Textured | Serves | Verdict |
|---|---|---|---|---|
| Universal Animation Library 2 | 42 Standard clips | n/a | ASSET-005, 010 | **Download.** Not on the original list. Has `CLIMBUP 1M`; has no ladder or camera clip |
| Fantasy Props MegaKit | 94 of 211 models, 4 texture sets | Yes | ASSET-068, 074, 076, 174 | **Download.** Closest match to the kit. Check the texture budget (below) |
| Pirate Kit | 71 models, glTF | Yes | ASSET-069 | **Download to test the boat only.** The preview is brighter and more cartoon than the kit |
| Ultimate Animated Animal Pack | 12 animals, glTF | No | ASSET-012 | Hold until wildlife is scheduled (Later) |
| Ships | 6 models, no glTF | No | none | Skip: untextured, and no row depends on it |
| Ultimate Crops | 102 models, no glTF | No | none | Skip: no row needs crops |
| Ultimate House Interior | 123 models, no glTF | No | ASSET-074, 076 | Skip: Fantasy Props covers these and is textured |

## Import Rules

- **Third-party files stay out of git (8.11, 8.12).** `.gitignore` covers only the spike's assets today, so anything copied under `assets/` would be committed. **A rule is needed before the first import.** Proposed folder: `assets/third_party/quaternius/`. Merged scenes that embed pack geometry need the same protection, and a fresh public clone will need the packs fetched separately.
- **Renaming.** A `.gltf` points at its `.bin` and textures by relative path, so renaming to 8.2 must rewrite those paths or the import breaks.
- **Texture sizes (8.6).** Village maps are 2048 px and `T_TopWear.png`, `T_BottomWear.png` and `T_BrushedNoise.png` are 4096 px; all must come down to the 8.6 limits.
- **Grade at import (4.1, 6.2).** One shared material per texture set.

## Budget Risks Found in the Packs

| Finding | Budget (art bible) | Action |
|---|---|---|
| Every outfit plus head, eyes, brows and hair is about 18,800 to 31,600 tris | 15,000 near (8.3) | Reduce, or raise the budget. Figures in the character spec |
| 4 near characters at 15,000 is 60,000 tris | Characters 20,000 in the 150,000 split (8.3) | The bible conflicts with itself; needs a decision |
| 4 players as supplied (9 surfaces each) plus 8 subjects is 68 draw calls | 60 for the group (8.4) | Merge outfit surfaces by material: 6 each, 56 in total |
| `Corner_Exterior_Brick` 3,102; `Balcony_Simple_Straight` 1,120; `Balcony_Simple_Corner` 2,240 | Assembled building 15,000 | Use `Corner_Exterior_Wood` (12) and `Balcony_Cross_Straight` (132) |
| `TwistedTree_1` 9,564 | Tree 6,500 | Not used |
| `Rock_Medium_3` 522; `Grass_Wispy_Short` 494; `Prop_Wagon` 1,672 | Rock 400; grass 350; medium prop 1,500 | Reduce, or leave out |
| Trees ship with no LOD1 | 1,500 or fewer (8.3) | Must be generated; Godot LOD on the Compatibility renderer is unverified |
| Fantasy Props adds up to 4 texture sets | 64 MB per scene, already at the limit (8.6) | Load it in interior scenes only, and use texture compression if possible |

## Open Questions

- **Lighthouse shape (art-director).** Kit walls are flat 2 m pieces, so the tower is square, not round. `Roof_Tower_RoundTiles` also carries iron ornaments, which bible 3.1 keeps off main views.
- **Untextured self-made props (art-director).** Bible 5.3 calls spirits the only untextured surfaces, but asset-forge gear and props are untextured too.
- **Terrain route.** ASSET-048 is Engine-built; bible 8.10 does not list terrain under any source.
- **Sea and shore.** Bible 6.1 calls this the weakest part of the scene. It rests on ASSET-048, 079 and 092, and is unproven.

## Assets by Context

### Characters and animation

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-001 | Player photographer, placeholder | `char_player_base_01_placeholder.glb` | Character | First playable | asset-forge recipe | Recipe `design/assets/recipes/char_player_base_01_placeholder.json`; `.glb` on `dev` only | - | Superseded by ASSET-002 | design/assets/specs/characters-assets.md |
| ASSET-002 | Player photographer, final | `char_player_base_01.gltf` | Character | First playable | Quaternius pack | Head trimmed from `UBC/Base Characters/Godot - UE/Superhero_Male_FullBody.gltf` or `UBC/Base Characters/Godot - UE/Superhero_Female_FullBody.gltf`, hair from `UBC/Hairstyles/Rigged to Head Bone/glTF (Godot -Unreal)/`, outfit from `Outfits/` (Peasant or Ranger parts; see spec) | Now | Needed | design/assets/specs/characters-assets.md |
| ASSET-003 | Player locomotion clips | `char_anim_ual1.glb (shared library)` | Animation | First playable | Quaternius pack | `UAL1/Unreal-Godot/UAL1_Standard.glb`: `Idle_Loop`, `Walk_Loop`, `Jog_Fwd_Loop`, `Crouch_Idle_Loop`, `Crouch_Fwd_Loop`, `Jump_Land`. No wade clip: slowed `Walk_Loop` | Now | Needed | design/assets/specs/characters-assets.md |
| ASSET-004 | Player camera clips | `char_anim_camera_*.glb` | Animation | MVP | Needs an artist | None in UAL1 or the UAL2 Standard list. Fallback to test: hand IK in Godot (see spec) | No free source | Needed | design/assets/specs/characters-assets.md |
| ASSET-005 | Player traversal clips | `char_anim_ual2.glb (shared library)` | Animation | MVP | Quaternius pack | UAL2 Standard: `CLIMBUP 1M` for scramble and vault. Ladder moved to ASSET-173 | Pack needed | Needed | design/assets/specs/characters-assets.md |
| ASSET-006 | NPC client, fisher | `char_npc_client_fisher.gltf` | Character | MVP | Quaternius pack | Head from `UBC/Base Characters/Godot - UE/Superhero_Male_FullBody.gltf`, `Outfits/Exports/glTF (Godot-Unreal)/Outfits/Male_Peasant.gltf`. Role prop: ASSET-174 | Now | Needed | design/assets/specs/characters-assets.md |
| ASSET-007 | NPC client, shopkeeper | `char_npc_client_shopkeeper.gltf` | Character | MVP | Quaternius pack | Head from `UBC/Base Characters/Godot - UE/Superhero_Female_FullBody.gltf`, `Outfits/Exports/glTF (Godot-Unreal)/Outfits/Female_Peasant.gltf`. Role prop: ASSET-174 | Now | Needed | design/assets/specs/characters-assets.md |
| ASSET-008 | NPC client, courier | `char_npc_client_courier.gltf` | Character | MVP | Quaternius pack | Head from `UBC/Base Characters/Godot - UE/Superhero_Male_FullBody.gltf`, `Outfits/Exports/glTF (Godot-Unreal)/Outfits/Male_Peasant.gltf`, colour map `Outfits/Textures/Peasant/T_Peasant_2_BaseColor.png`. Role prop: ASSET-174 | Now | Needed | design/assets/specs/characters-assets.md |
| ASSET-009 | NPC client, archivist | `char_npc_client_archivist.gltf` | Character | MVP | Quaternius pack | Head from `UBC/Base Characters/Godot - UE/Superhero_Female_FullBody.gltf`, `Outfits/Exports/glTF (Godot-Unreal)/Outfits/Female_Peasant.gltf`, colour map `Outfits/Textures/Peasant/T_Peasant_2_BaseColor.png`. Role prop: ASSET-174 | Now | Needed | design/assets/specs/characters-assets.md |
| ASSET-010 | NPC idle clips | `char_anim_ual1.glb (shared library)` | Animation | MVP | Quaternius pack | `UAL1/Unreal-Godot/UAL1_Standard.glb`: `Idle_Loop`, `Idle_Talking_Loop`, `Sitting_Idle_Loop`. UAL2 `IDLE_FOLD ARMS`, `IDLE_RAIL` would add variety | Now | Needed | design/assets/specs/characters-assets.md |
| ASSET-011 | Player cosmetics | `char_player_hat_*.glb, char_player_bag_*.glb` | Character | Later | asset-forge recipe | Recipe for hats and bags, attached to bones. Jacket colours: `Outfits/Textures/Peasant/` and `Ranger/` colour maps, or a tint | Made here | Needed | design/assets/specs/characters-assets.md |
| ASSET-012 | Wildlife subjects | `char_animal_*.gltf` | Character | Later | Quaternius pack | Ultimate Animated Animal Pack, species not chosen. Site flags it not textured, so check against the world first (bible 5.4) | Pack needed | Needed | design/assets/specs/characters-assets.md |
| ASSET-173 | Player ladder climb loop | `char_anim_ladder_climb.glb` | Animation | MVP | Needs an artist | None in UAL1 or the UAL2 Standard list. Fallback to test: hand and foot IK on the ladder rungs | No free source | Needed | design/assets/specs/characters-assets.md |

### Subjects (spirits and memories)

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-013 | Puffwisp | `subj_puffwisp_base_01.glb` | Creature | First playable | asset-forge recipe | Recipe `design/assets/recipes/subj_puffwisp_base_01.json`; `.glb` on `dev` only | Made here | Restyle proposal | design/assets/specs/characters-assets.md |
| ASSET-014 | Mossmote | `subj_mossmote_base_01.glb` | Creature | First playable | asset-forge recipe | Recipe `design/assets/recipes/subj_mossmote_base_01.json`; `.glb` on `dev` only | Made here | Restyle proposal | design/assets/specs/characters-assets.md |
| ASSET-015 | Driftfin | `subj_driftfin_base_01.glb` | Creature | First playable | asset-forge recipe | Recipe `design/assets/recipes/subj_driftfin_base_01.json`; `.glb` on `dev` only | Made here | Restyle proposal | design/assets/specs/characters-assets.md |
| ASSET-016 | Hearth Echo | `subj_hearth_echo_base_01.glb` | Creature | First playable | asset-forge recipe | Recipe `design/assets/recipes/subj_hearth_echo_base_01.json`; `.glb` on `dev` only | Made here | Restyle proposal | design/assets/specs/characters-assets.md |
| ASSET-017 | Halo Keeper | `subj_halo_keeper_base_01.glb` | Creature | First playable | asset-forge recipe | Recipe `design/assets/recipes/subj_halo_keeper_base_01.json`; `.glb` on `dev` only | Made here | Restyle proposal | design/assets/specs/characters-assets.md |
| ASSET-018 | Capture Encounter set-piece subject | `subj_encounter_base_01.glb` | Creature | MVP | asset-forge recipe | Recipe, bible 5.3 rules | Made here | Needed | design/assets/specs/characters-assets.md |
| ASSET-019 | Driftfin (gilded) | `subj_driftfin_gilded_01.glb` | Creature | Later | asset-forge recipe | Recipe, bible 5.3 rules | Made here | Needed | design/assets/specs/characters-assets.md |
| ASSET-020 | Vesper Halo | `subj_vesper_halo_base_01.glb` | Creature | Later | asset-forge recipe | Recipe, bible 5.3 rules | Made here | Needed | design/assets/specs/characters-assets.md |
| ASSET-021 | Aurora Drifter | `subj_aurora_drifter_base_01.glb` | Creature | Later | asset-forge recipe | Recipe, bible 5.3 rules | Made here | Needed | design/assets/specs/characters-assets.md |

### Gear models

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-022 | Lumo Pebble phone | `gear_phone_basic_c_01.glb` | Item | First playable | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-023 | Kanro Hearth body | `gear_body_aps_entry_b_01.glb` | Item | First playable | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-024 | Kanro Lantern body | `gear_body_ff_a_01.glb` | Item | First playable | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-025 | Kanro KR-S 18-45mm lens | `gear_lens_zoom18_45_c_01.glb` | Item | First playable | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-026 | Kanro KR 50mm f/1.8 lens | `gear_lens_std50_f18_b_01.glb` | Item | First playable | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-027 | Kanro KR 85mm f/1.4 lens | `gear_lens_tele85_f14_a_01.glb` | Item | First playable | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-028 | Fujin Drift body | `gear_body_aps_retro_b_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-029 | Nokta Kestrel body | `gear_body_ff_wild_a_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-030 | Kanro KR 100-300mm lens | `gear_lens_zoom100_300_b_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-031 | Kanro KR 40mm Pancake lens | `gear_lens_pan40_f28_a_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-032 | Fujin FX 27mm lens | `gear_lens_std27_f28_c_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-033 | Fujin FX 33mm lens | `gear_lens_std33_f14_b_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-034 | Nokta NZ 24-70mm lens | `gear_lens_zoom24_70_f4_b_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-035 | Hollin 58mm "Harbour" lens | `gear_lens_std58_f20_b_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-036 | Hollin 28mm lens | `gear_lens_wide28_f28_c_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-037 | Hollin H42 to KR ring | `gear_adp_t455_m20_b_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-038 | Hollin H42 to FX ring | `gear_adp_t455_m17_b_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-039 | Nokta KR to NZ Smart Adapter | `gear_adp_m20_m16_a_01.glb` | Item | MVP | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-040 | Nokta NZ 200mm f/2.8 lens | `gear_lens_tele200_f28_s_01.glb` | Item | Later | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-041 | Kanro Beacon body | `gear_body_ff_s_01.glb` | Item | Later | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-042 | Kanro KR 50mm f/1.2 lens | `gear_lens_std50_f12_ss_01.glb` | Item | Later | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-043 | Nokta Zenith body | `gear_body_mf_sss_01.glb` | Item | Later | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-044 | Nokta NM 80mm f/1.8 lens | `gear_lens_std80_f18_sss_01.glb` | Item | Later | asset-forge recipe | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |
| ASSET-045 | Mount index dot and brand decal slot | `gear_* (material slot)` | Item | MVP | Engine-built | Recipe, bible 3.4 matching rules | Made here | Needed | not specced |

### Environment

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-046 | Lighthouse | `env_lighthouse_main_large.tscn` | Environment | First playable | Quaternius pack | Kit-bash: `Village/glTF/Wall_Plaster_Straight`, `Corner_Exterior_Wood`, `Window_Thin_Round1`, `Door_1_Round`, `Balcony_Cross_Straight`, `Roof_Tower_RoundTiles`. Lamp: `env_lighthouse_lamp_01.glb`, asset-forge, emissive only | Now | Needed | not specced |
| ASSET-047 | Cliff chunks | `env_cliff_chunk_01..03.tscn` | Environment | First playable | Quaternius pack | `Nature/glTF/Rock_Medium_1..3`, scaled up. No cliff piece in the free tier; check texture stretch | Now | Needed | not specced |
| ASSET-048 | Terrain base | `env_terrain_village_01.tscn` | Environment | First playable | Engine-built | Height mesh in Godot with a blend material from ASSET-078 to 080. asset-forge has no UVs, so it cannot carry this | Made here | Needed | not specced |
| ASSET-049 | Gabled house, lived-in | `env_house_gabled_01.tscn` | Environment | First playable | Quaternius pack | Kit-bash: `Village/glTF/Wall_Plaster_*`, `Wall_Plaster_WoodGrid`, `Door_*`, `Window_*`, `Balcony_Cross_*`, `Roof_RoundTiles_6x8`, `Prop_Chimney2` | Now | Needed | not specced |
| ASSET-050 | Gabled house, shut | `env_house_shut_01.tscn` | Environment | MVP | Quaternius pack | Kit-bash: `Village/glTF/Wall_UnevenBrick_*`, `WindowShutters_*_Closed`, `Prop_Vine*`, `Roof_RoundTiles_6x6`. Sag and boards by placement | Now | Needed | not specced |
| ASSET-051 | Gabled house, small | `env_house_small_01.tscn` | Environment | MVP | Quaternius pack | Kit-bash: `Village/glTF/Wall_Plaster_*`, `Roof_RoundTiles_4x4` | Now | Needed | not specced |
| ASSET-052 | Gear shop exterior | `env_shop_gear_01.tscn` | Environment | MVP | Quaternius pack | Kit-bash: `Village/glTF/Wall_Plaster_Window_Wide_*`, `Door_2_Round`, `Wall_Arch`, `Roof_RoundTiles_6x8` | Now | Needed | not specced |
| ASSET-053 | Pier on posts | `env_pier_main_large.tscn` | Environment | First playable | Quaternius pack | Kit-bash: `Village/glTF/Floor_WoodLight` deck, `Corner_ExteriorWide_Wood` posts, `Prop_Support` braces, `Prop_WoodenFence_Single` and `_Extension1` rail | Now | Needed | not specced |
| ASSET-054 | Harbour wall | `env_wall_harbour_01.tscn` | Environment | MVP | Quaternius pack | Kit-bash: `Village/glTF/Wall_UnevenBrick_Straight`, `Prop_ExteriorBorder_Straight1` and `_Corner` cap, `Prop_Brick1..4` | Now | Needed | not specced |
| ASSET-055 | Round tree | `env_tree_round_01..05.gltf` | Environment | First playable | Quaternius pack | `Nature/glTF/CommonTree_1..5` (3,182 to 6,265 tris). LOD1 must be made | Now | Needed | not specced |
| ASSET-056 | Pine tree | `env_tree_pine_01..05.gltf` | Environment | MVP | Quaternius pack | `Nature/glTF/Pine_1..5` (1,646 to 4,964 tris). LOD1 must be made | Now | Needed | not specced |
| ASSET-057 | Rock set | `env_rock_chunky_01..03.gltf` | Environment | First playable | Quaternius pack | `Nature/glTF/Rock_Medium_1..3`. `_3` is 522 tris, over the 400 budget | Now | Needed | not specced |
| ASSET-058 | Moss patch | `env_moss_patch_01.tscn` | Environment | MVP | Quaternius pack | `Nature/glTF/Clover_1`, `Clover_2`, `Plant_1`, flattened and tinted. No moss model in the free tier | Now | Needed | not specced |
| ASSET-059 | Grass clump | `env_grass_clump_01..03.gltf` | Environment | MVP | Quaternius pack | `Nature/glTF/Grass_Common_Short`, `Grass_Common_Tall`, `Grass_Wispy_Tall`. `Grass_Wispy_Short` is 494 tris, over the 350 budget | Now | Needed | not specced |
| ASSET-060 | Ladder traversal piece | `env_ladder_01.tscn` | Environment | MVP | Quaternius pack | Kit-bash: `Village/glTF/Corner_Exterior_Wood` as rails and rungs (12 tris each). No ladder in the kit | Now | Needed | not specced |
| ASSET-061 | Rock scramble and low wall | `env_scramble_01.tscn` | Environment | MVP | Quaternius pack | Kit-bash: `Nature/glTF/Rock_Medium_1..2`, `Village/glTF/Prop_Brick1..4`, `Prop_ExteriorBorder_Straight2` | Now | Needed | not specced |
| ASSET-062 | Darkroom interior | `env_room_darkroom_01.tscn` | Environment | MVP | Quaternius pack | Kit-bash shell: `Village/glTF/Wall_UnevenBrick_Straight`, `Floor_WoodDark`, `Door_1_Flat`, `Stair_Interior_Simple` | Now | Needed | not specced |
| ASSET-063 | Gallery interior | `env_room_gallery_01.tscn` | Environment | MVP | Quaternius pack | Kit-bash shell: `Village/glTF/Wall_Plaster_Straight`, `Floor_WoodLight`, `Wall_Arch` | Now | Needed | not specced |
| ASSET-064 | Gear shop interior | `env_room_shop_01.tscn` | Environment | MVP | Quaternius pack | Kit-bash shell: `Village/glTF/Wall_Plaster_Straight`, `Floor_WoodDark`, `Window_Wide_Round1` | Now | Needed | not specced |

### Props

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-065 | Fence section | `prop_fence_weathered_01..03.gltf` | Item | MVP | Quaternius pack | `Village/glTF/Prop_WoodenFence_Single`, `_Extension1`, `_Extension2` | Now | Needed | not specced |
| ASSET-066 | Signpost, icon only | `prop_sign_icon_01.tscn` | Item | MVP | Quaternius pack | Kit-bash: `Village/glTF/Corner_Exterior_Wood` post, `Prop_WoodenFence_Extension2` board. Icon is a decal from the UI set | Now | Needed | not specced |
| ASSET-067 | Crate | `prop_crate_weathered_small.gltf` | Item | MVP | Quaternius pack | `Village/glTF/Prop_Crate` (230 tris) | Now | Needed | not specced |
| ASSET-068 | Bench | `prop_bench_weathered_01.gltf` | Item | MVP | Quaternius pack | Fantasy Props MegaKit Standard, bench seen in its preview. File name unknown until downloaded | Pack needed | Needed | not specced |
| ASSET-069 | Rowing boat | `prop_boat_row_01.gltf` | Item | MVP | Quaternius pack | Pirate Kit, rowing boat seen in its preview. File name unknown; style check needed before use | Pack needed | Needed | not specced |
| ASSET-070 | Mooring post | `prop_post_mooring_01.tscn` | Item | MVP | Quaternius pack | `Village/glTF/Corner_ExteriorWide_Wood`, leaned (36 tris) | Now | Needed | not specced |
| ASSET-071 | Empty picture frame | `prop_frame_empty_01.glb` | Item | MVP | asset-forge recipe | No pack has it. Recipe under bible 3.4 matching rules; untextured (no UVs) | Made here | Needed | not specced |
| ASSET-072 | Small cairn | `prop_cairn_small_01.tscn` | Item | MVP | Quaternius pack | `Nature/glTF/Pebble_Round_1..5`, `Pebble_Square_1..6`, stacked | Now | Needed | not specced |
| ASSET-073 | Forgotten lens cap | `prop_lenscap_01.glb` | Item | MVP | asset-forge recipe | Gear family: recipe under bible 3.4 | Made here | Needed | not specced |
| ASSET-074 | Darkroom table set | `prop_darkroom_table_01.gltf` | Item | MVP | Quaternius pack | Fantasy Props MegaKit Standard, table and shelf seen in its preview. Enlarger and trays moved to ASSET-172 | Pack needed | Needed | not specced |
| ASSET-075 | Gallery print frame | `prop_print_frame_01.glb` | Item | MVP | asset-forge recipe | No pack has it. Shares its recipe with ASSET-071 | Made here | Needed | not specced |
| ASSET-076 | Shop shelf and counter | `prop_shop_shelf_01.gltf` | Item | MVP | Quaternius pack | Fantasy Props MegaKit Standard, shelves and table seen in its preview | Pack needed | Needed | not specced |
| ASSET-077 | Found photo marker | `prop_print_found_01.glb` | Item | Later | asset-forge recipe | Paper rectangle, no pack needed | Made here | Needed | not specced |
| ASSET-172 | Enlarger and developing trays | `prop_darkroom_enlarger_01.glb` | Item | MVP | asset-forge recipe | No pack has it. Recipe under bible 3.4 matching rules; untextured (no UVs) | Made here | Needed | not specced |
| ASSET-174 | NPC role props | `prop_role_*_01.glb` | Item | MVP | asset-forge recipe | Hat, apron, satchel, clipboard: rigid parts on bones, untextured. Fantasy Props shows a satchel in its preview, which could replace that one | Made here | Needed | design/assets/specs/characters-assets.md |

### Textures

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-078 | Grass ground | `tex_grass_meadow_256.png` | Environment | First playable | asset-forge recipe | `texture_gen.py` gap fill allowed by bible 6.2. No ground tile in the packs; `Grass.png` is a grass-model texture | Made here | Needed | not specced |
| ASSET-079 | Sand shore | `tex_sand_shore_256.png` | Environment | MVP | asset-forge recipe | `texture_gen.py` gap fill allowed by bible 6.2. No sand in the packs | Made here | Needed | not specced |
| ASSET-080 | Cobble street | `tex_cobble_street_512.png (+ _n 256)` | Environment | MVP | Quaternius pack | `Village/Textures/T_Brick_BaseColor.png`, `T_Brick_Normal.png`, downsized to the 8.6 ground row | Now | Needed | not specced |
| ASSET-081 | Pier planks | `tex_planks_pier_256.png (+ _n)` | Environment | First playable | None | Covered by the shared wood set on `Floor_WoodLight` in ASSET-053 | - | Retired | not specced |
| ASSET-082 | Darkroom table surface | `tex_darkroom_table_512.png` | Environment | MVP | None | Comes with the ASSET-074 table | - | Retired | not specced |
| ASSET-083 | Gallery wall | `tex_gallery_wall_512.png` | Environment | MVP | None | Covered by the shared plaster set on `Wall_Plaster_Straight` in ASSET-063 | - | Retired | not specced |
| ASSET-084 | Shop surface | `tex_shop_surface_512.png` | Environment | MVP | None | Covered by the shared wood set in ASSET-064 and the ASSET-076 shelves | - | Retired | not specced |

### VFX and shaders

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-085 | Lens-world post pass | `shader: lens_post` | VFX | First playable | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-086 | Lens-only subject layer | `shader or cull layer` | VFX | First playable | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-087 | Subject rim and glow | `shader: subj_rim` | VFX | First playable | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-088 | Glow halo card | `vfx_halo_card_small.png` | VFX | First playable | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-089 | Naked-eye shimmer motes | `vfx_motes_shimmer_loop_small.png` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-090 | Memory fade | `shader: memory_fade` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-091 | Sky gradient by band | `shader: sky_band` | VFX | First playable | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-092 | Water surface | `shader: water` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-093 | Wind on grass | `shader: wind_grass` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-094 | Fog | `shader: depth_fog` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-095 | Rain streaks | `vfx_rain_streaks_loop_small.png` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-096 | Capture iris and flash | `shader: capture_iris` | VFX | First playable | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-097 | Look tag shader parameters | `shader: lens_post params` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-098 | Sunbeam event | `vfx_motes_beam_loop_small.png` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-099 | Lumen Dusk event | `shader: event_lumen_dusk` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-100 | Aurora event | `shader: event_aurora` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-101 | Darkroom light swatch | `shader: light_swatch` | VFX | MVP | Engine-built | Godot shader or particles | Made here | Needed | not specced |
| ASSET-102 | Print reveal | `shader: print_reveal` | VFX | First playable | Engine-built | Godot shader or particles | Made here | Needed | not specced |

### UI screens

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-103 | Title and sign-in | `ui_screen (.tscn + SVG parts)` | UI | First playable | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-104 | Account panel | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-105 | Restore notice | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-106 | Pending deletion | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-107 | Starting choice | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-108 | Darkroom breakdown card | `ui_screen (.tscn + SVG parts)` | UI | First playable | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-109 | Gallery | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-110 | Gear shop and detail | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-111 | Sell to clients | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-112 | Gear screen (loadout, Bag, Shelf) | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-113 | Wallet history | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-114 | Forecast panel | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-115 | Field swap list and iris wipe | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |
| ASSET-116 | Leaderboard | `ui_screen (.tscn + SVG parts)` | UI | Later | asset-forge recipe | `.tscn` with hand-written SVG | Made here | Needed | not specced |

### HUD and icons

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-117 | Camera viewfinder skin | `ui_vf_camera_*.svg` | UI | First playable | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-118 | Phone viewfinder skin | `ui_vf_phone_*.svg` | UI | First playable | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-119 | Red live dot and battery | `ui_icon_live_24.svg, ui_icon_battery_24.svg` | UI | First playable | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-120 | Exploration device icon | `ui_icon_device_24.svg` | UI | First playable | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-121 | Compass strip | `ui_compass_strip.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-122 | Context prompts | `ui_prompt_*.svg` | UI | First playable | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-123 | Clock and band glyphs | `ui_icon_band_*_24.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-124 | Weather icons | `ui_icon_weather_*_24.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-125 | Event toast and map marker | `ui_icon_event_24.svg` | UI | Later | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-126 | Presence glyph, 3 states | `ui_icon_presence_*_24.svg` | UI | First playable | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-127 | Curious cue | `ui_icon_curious_24.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-128 | Tier badge set | `ui_badge_tier_c..sss.svg, ui_badge_tier_unknown.svg` | UI | First playable | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-129 | Tier frame ornaments | `ui_frame_tier_*.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-130 | Connection indicator | `ui_icon_conn_*_24.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-131 | Developing and saving marks | `ui_mark_developing.svg, ui_mark_saving.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-132 | Guest badge and keep-progress banner | `ui_chip_guest.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-133 | Envelope and lock icons | `ui_icon_mail_24.svg, ui_icon_lock_24.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-134 | Glint currency icon and wallet chip | `ui_icon_glint_24.svg` | UI | First playable | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-135 | Gear side silhouettes | `ui_icon_gear_*_48.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-136 | Bound phone mark | `ui_icon_bound_24.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-137 | Bag and Shelf art | `ui_bag_canvas.svg, ui_shelf_wood.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-138 | Client print icon | `ui_icon_print_24.svg` | UI | MVP | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-139 | Logo, spinner, iris transition | `ui_logo_aperture.svg, ui_spinner_aperture.svg` | UI | First playable | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |
| ASSET-140 | Co-op role icons | `ui_icon_role_*_24.svg` | UI | Later | asset-forge recipe | Hand-written SVG | Made here | Needed | not specced |

### Fonts

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-141 | Inter | `assets/ui/fonts/` | UI | First playable | OFL font | OFL download, not done. Confirm licence on download | Pack needed | Needed | not specced |
| ASSET-142 | IBM Plex Mono | `assets/ui/fonts/` | UI | First playable | OFL font | OFL download, not done. Confirm licence on download | Pack needed | Needed | not specced |

### Audio

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-143 | Shutter ML_SOFT | `sfx_shutter_ml_soft_01.ogg` | SFX | First playable | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-144 | Shutter PHONE_SYNTH | `sfx_shutter_phone_synth_01.ogg` | SFX | First playable | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-145 | Shutter ML_LEAF | `sfx_shutter_ml_leaf_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-146 | Subject anticipation tone | `sfx_subject_anticipation_01.ogg` | SFX | First playable | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-147 | Subject decisive bell | `sfx_subject_decisive_01.ogg` | SFX | First playable | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-148 | Subject emergence chime | `sfx_subject_emerge_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-149 | Subject tuck hush | `sfx_subject_tuck_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-150 | Subject flight swirl | `sfx_subject_flee_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-151 | Subject return chime | `sfx_subject_return_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-152 | Footsteps by surface | `sfx_step_{grass,sand,stone,plank,water}_01..03.ogg` | SFX | First playable | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-153 | Landing thump | `sfx_land_soft_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-154 | Ladder rungs | `sfx_ladder_rung_01..03.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-155 | Wading splashes | `sfx_wade_01..03.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-156 | Viewfinder raise rustle | `sfx_raise_rustle_01.ogg` | SFX | First playable | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-157 | Aperture dial click | `sfx_dial_click_01.ogg` | SFX | First playable | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-158 | Focus confirmation | `sfx_focus_confirm_01.ogg` | SFX | First playable | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-159 | Zoom ring | `sfx_zoom_ring_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-160 | Bayonet mount twist-click | `sfx_mount_bayonet_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-161 | Thread mount screw | `sfx_mount_thread_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-162 | Pocket rustle and Bag pack | `sfx_pocket_rustle_01.ogg, sfx_bag_pack_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-163 | Refusal tap | `sfx_ui_refuse_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-164 | Sale tick and purchase cue | `sfx_ui_sale_01.ogg, sfx_ui_buy_01.ogg` | SFX | MVP | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-165 | Account saved chime | `sfx_ui_saved_01.ogg` | SFX | Later | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-166 | Reconnected cue | `sfx_ui_reconnect_01.ogg` | SFX | Later | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-167 | Ambience beds by condition | `amb_{clear,overcast,fog,night}_loop.ogg` | Ambient | MVP | CC0 audio pack | No pack chosen; Quaternius has no audio and asset-forge makes no natural beds | Pack needed | Needed | not specced |
| ASSET-168 | Rain layer | `amb_rain_loop.ogg` | Ambient | MVP | CC0 audio pack | No pack chosen; Quaternius has no audio and asset-forge makes no natural beds | Pack needed | Needed | not specced |
| ASSET-169 | Event build-up cue | `sfx_event_build_01.ogg` | Ambient | Later | asset-forge recipe | Synth recipe | Made here | Needed | not specced |
| ASSET-170 | Music | `music_*_loop.ogg` | Music | Later | Needs an artist | No GDD asks for music; asset-forge is chiptune only | No free source | Needed | not specced |

### Marketing

| Asset ID | Name | File | Type | Priority | Route | Source | Available | Status | Spec File |
|---|---|---|---|---|---|---|---|---|---|
| ASSET-171 | Title key art | `ui_keyart_title.png` | Other | Later | Needs an artist | Painterly art is out of scope for code. Not requested by any GDD | No free source | Needed | not specced |
