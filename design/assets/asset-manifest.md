# Asset Manifest

> Last updated: 2026-11-05
> Inventory: design/assets/entity-inventory.md
> **Status meaning:** `Done` = generated, preview read, triangle budget met, and loaded in Godot 4.7.2 headless. It does not mean approved: no art director or user has signed these off, and no model has been seen lit in the engine.

## Progress Summary

| Total | Needed | Done |
|---|---|---|
| 171 | 165 | 6 |

| Priority | Assets | Done |
|---|---|---|
| First playable | 49 | 6 |
| MVP | 103 | 0 |
| Later | 19 | 0 |

| Route | Assets |
|---|---|
| asset-forge recipe | 136 |
| CC0 pack | 11 |
| Needs an artist | 3 |
| Engine-built | 19 |
| OFL font | 2 |

## Key

**Priority.** `First playable` = the smallest set that lets one player walk the area, raise the lens, photograph a subject and see the darkroom result. `MVP` = the rest of the concept's "First playable version" list and the MVP rows of the systems index. `Later` = Vertical Slice onward, or disabled data. The concept calls its whole MVP scope "first playable"; this manifest splits it, which is an assumption (see the inventory).

**Rows.** A row can be a small set that is produced together (badge set, footsteps, clip sets). Split it when work starts; new IDs continue from the highest in use.

**Route.** `asset-forge recipe` = generated locally (`Needed` audio always needs a human listen). `CC0 pack` = Quaternius or Kenney first, not downloaded yet. `Needs an artist` = out of scope for code and unlikely in a free pack. Two routes were added to the three requested because they fit no other: `Engine-built` = shaders and particles made in Godot by technical-artist or godot-shader-specialist; `OFL font` = free font under the SIL Open Font License, not CC0.

**CC0 licence log.** Nothing has been downloaded. Record the source URL and licence here on import (art bible 8.2).

## Assets by Context

### Characters and animation

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-001 | Player photographer, placeholder | `char_player_base_01_placeholder.glb` | Character | First playable | asset-forge recipe | Done | design/assets/specs/characters-assets.md |
| ASSET-002 | Player photographer, final | `char_player_base_01.glb` | Character | MVP | CC0 pack | Needed | design/assets/specs/characters-assets.md |
| ASSET-003 | Player locomotion clips | `char_player_base_01.glb (clips)` | Animation | MVP | CC0 pack | Needed | design/assets/specs/characters-assets.md |
| ASSET-004 | Player camera clips | `char_player_base_01.glb (clips)` | Animation | MVP | Needs an artist | Needed | design/assets/specs/characters-assets.md |
| ASSET-005 | Player traversal clips | `char_player_base_01.glb (clips)` | Animation | MVP | CC0 pack | Needed | design/assets/specs/characters-assets.md |
| ASSET-006 | NPC client, fisher | `char_npc_client_fisher.glb` | Character | MVP | CC0 pack | Needed | design/assets/specs/characters-assets.md |
| ASSET-007 | NPC client, shopkeeper | `char_npc_client_shopkeeper.glb` | Character | MVP | CC0 pack | Needed | design/assets/specs/characters-assets.md |
| ASSET-008 | NPC client, courier | `char_npc_client_courier.glb` | Character | MVP | CC0 pack | Needed | design/assets/specs/characters-assets.md |
| ASSET-009 | NPC client, archivist | `char_npc_client_archivist.glb` | Character | MVP | CC0 pack | Needed | design/assets/specs/characters-assets.md |
| ASSET-010 | NPC idle clips | `char_npc_client_*.glb (clips)` | Animation | MVP | CC0 pack | Needed | design/assets/specs/characters-assets.md |
| ASSET-011 | Player cosmetics | `char_player_hat_*.glb, char_player_bag_*.glb` | Character | Later | asset-forge recipe | Needed | design/assets/specs/characters-assets.md |
| ASSET-012 | Wildlife subjects | `char_animal_*.glb` | Character | Later | CC0 pack | Needed | design/assets/specs/characters-assets.md |

### Subjects (spirits and memories)

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-013 | Puffwisp | `subj_puffwisp_base_01.glb` | Creature | First playable | asset-forge recipe | Done | design/assets/specs/characters-assets.md |
| ASSET-014 | Mossmote | `subj_mossmote_base_01.glb` | Creature | First playable | asset-forge recipe | Done | design/assets/specs/characters-assets.md |
| ASSET-015 | Driftfin | `subj_driftfin_base_01.glb` | Creature | First playable | asset-forge recipe | Done | design/assets/specs/characters-assets.md |
| ASSET-016 | Hearth Echo | `subj_hearth_echo_base_01.glb` | Creature | First playable | asset-forge recipe | Done | design/assets/specs/characters-assets.md |
| ASSET-017 | Halo Keeper | `subj_halo_keeper_base_01.glb` | Creature | First playable | asset-forge recipe | Done | design/assets/specs/characters-assets.md |
| ASSET-018 | Capture Encounter set-piece subject | `subj_encounter_base_01.glb` | Creature | MVP | asset-forge recipe | Needed | design/assets/specs/characters-assets.md |
| ASSET-019 | Driftfin (gilded) | `subj_driftfin_gilded_01.glb` | Creature | Later | asset-forge recipe | Needed | design/assets/specs/characters-assets.md |
| ASSET-020 | Vesper Halo | `subj_vesper_halo_base_01.glb` | Creature | Later | asset-forge recipe | Needed | design/assets/specs/characters-assets.md |
| ASSET-021 | Aurora Drifter | `subj_aurora_drifter_base_01.glb` | Creature | Later | asset-forge recipe | Needed | design/assets/specs/characters-assets.md |

### Gear models

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-022 | Lumo Pebble phone | `gear_phone_basic_c_01.glb` | Item | First playable | asset-forge recipe | Needed | not specced |
| ASSET-023 | Kanro Hearth body | `gear_body_aps_entry_b_01.glb` | Item | First playable | asset-forge recipe | Needed | not specced |
| ASSET-024 | Kanro Lantern body | `gear_body_ff_a_01.glb` | Item | First playable | asset-forge recipe | Needed | not specced |
| ASSET-025 | Kanro KR-S 18-45mm lens | `gear_lens_zoom18_45_c_01.glb` | Item | First playable | asset-forge recipe | Needed | not specced |
| ASSET-026 | Kanro KR 50mm f/1.8 lens | `gear_lens_std50_f18_b_01.glb` | Item | First playable | asset-forge recipe | Needed | not specced |
| ASSET-027 | Kanro KR 85mm f/1.4 lens | `gear_lens_tele85_f14_a_01.glb` | Item | First playable | asset-forge recipe | Needed | not specced |
| ASSET-028 | Fujin Drift body | `gear_body_aps_retro_b_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-029 | Nokta Kestrel body | `gear_body_ff_wild_a_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-030 | Kanro KR 100-300mm lens | `gear_lens_zoom100_300_b_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-031 | Kanro KR 40mm Pancake lens | `gear_lens_pan40_f28_a_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-032 | Fujin FX 27mm lens | `gear_lens_std27_f28_c_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-033 | Fujin FX 33mm lens | `gear_lens_std33_f14_b_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-034 | Nokta NZ 24-70mm lens | `gear_lens_zoom24_70_f4_b_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-035 | Hollin 58mm "Harbour" lens | `gear_lens_std58_f20_b_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-036 | Hollin 28mm lens | `gear_lens_wide28_f28_c_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-037 | Hollin H42 to KR ring | `gear_adp_t455_m20_b_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-038 | Hollin H42 to FX ring | `gear_adp_t455_m17_b_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-039 | Nokta KR to NZ Smart Adapter | `gear_adp_m20_m16_a_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-040 | Nokta NZ 200mm f/2.8 lens | `gear_lens_tele200_f28_s_01.glb` | Item | Later | asset-forge recipe | Needed | not specced |
| ASSET-041 | Kanro Beacon body | `gear_body_ff_s_01.glb` | Item | Later | asset-forge recipe | Needed | not specced |
| ASSET-042 | Kanro KR 50mm f/1.2 lens | `gear_lens_std50_f12_ss_01.glb` | Item | Later | asset-forge recipe | Needed | not specced |
| ASSET-043 | Nokta Zenith body | `gear_body_mf_sss_01.glb` | Item | Later | asset-forge recipe | Needed | not specced |
| ASSET-044 | Nokta NM 80mm f/1.8 lens | `gear_lens_std80_f18_sss_01.glb` | Item | Later | asset-forge recipe | Needed | not specced |
| ASSET-045 | Mount index dot and brand decal slot | `gear_* (material slot)` | Item | MVP | Engine-built | Needed | not specced |

### Environment

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-046 | Lighthouse | `env_lighthouse_main_large.glb` | Environment | First playable | asset-forge recipe | Needed | not specced |
| ASSET-047 | Cliff chunks | `env_cliff_chunk_01..03.glb` | Environment | First playable | asset-forge recipe | Needed | not specced |
| ASSET-048 | Terrain base | `env_terrain_village_01.glb` | Environment | First playable | asset-forge recipe | Needed | not specced |
| ASSET-049 | Gabled house, lived-in | `env_house_gabled_01.glb` | Environment | First playable | asset-forge recipe | Needed | not specced |
| ASSET-050 | Gabled house, shut | `env_house_shut_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-051 | Gabled house, small | `env_house_small_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-052 | Gear shop exterior | `env_shop_gear_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-053 | Pier on posts | `env_pier_main_large.glb` | Environment | First playable | asset-forge recipe | Needed | not specced |
| ASSET-054 | Harbour wall | `env_wall_harbour_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-055 | Round tree | `env_tree_round_01.glb` | Environment | First playable | asset-forge recipe | Needed | not specced |
| ASSET-056 | Pine tree | `env_tree_pine_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-057 | Rock set | `env_rock_chunky_01..03.glb` | Environment | First playable | asset-forge recipe | Needed | not specced |
| ASSET-058 | Moss patch | `env_moss_patch_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-059 | Grass clump | `env_grass_clump_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-060 | Ladder traversal piece | `env_ladder_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-061 | Rock scramble and low wall | `env_scramble_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-062 | Darkroom interior | `env_room_darkroom_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-063 | Gallery interior | `env_room_gallery_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-064 | Gear shop interior | `env_room_shop_01.glb` | Environment | MVP | asset-forge recipe | Needed | not specced |

### Props

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-065 | Fence section | `prop_fence_weathered_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-066 | Signpost, icon only | `prop_sign_icon_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-067 | Crate | `prop_crate_weathered_small.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-068 | Bench | `prop_bench_weathered_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-069 | Rowing boat | `prop_boat_row_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-070 | Mooring post | `prop_post_mooring_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-071 | Empty picture frame | `prop_frame_empty_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-072 | Small cairn | `prop_cairn_small_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-073 | Forgotten lens cap | `prop_lenscap_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-074 | Darkroom table set | `prop_darkroom_table_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-075 | Gallery print frame | `prop_print_frame_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-076 | Shop shelf and counter | `prop_shop_shelf_01.glb` | Item | MVP | asset-forge recipe | Needed | not specced |
| ASSET-077 | Found photo marker | `prop_print_found_01.glb` | Item | Later | asset-forge recipe | Needed | not specced |

### Textures

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-078 | Grass ground | `tex_grass_meadow_256.png` | Environment | First playable | asset-forge recipe | Needed | not specced |
| ASSET-079 | Sand shore | `tex_sand_shore_256.png` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-080 | Cobble street | `tex_cobble_street_256.png (+ _n)` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-081 | Pier planks | `tex_planks_pier_256.png (+ _n)` | Environment | First playable | asset-forge recipe | Needed | not specced |
| ASSET-082 | Darkroom table surface | `tex_darkroom_table_512.png` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-083 | Gallery wall | `tex_gallery_wall_512.png` | Environment | MVP | asset-forge recipe | Needed | not specced |
| ASSET-084 | Shop surface | `tex_shop_surface_512.png` | Environment | MVP | asset-forge recipe | Needed | not specced |

### VFX and shaders

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-085 | Lens-world post pass | `shader: lens_post` | VFX | First playable | Engine-built | Needed | not specced |
| ASSET-086 | Lens-only subject layer | `shader or cull layer` | VFX | First playable | Engine-built | Needed | not specced |
| ASSET-087 | Subject rim and glow | `shader: subj_rim` | VFX | First playable | Engine-built | Needed | not specced |
| ASSET-088 | Glow halo card | `vfx_halo_card_small.png` | VFX | First playable | Engine-built | Needed | not specced |
| ASSET-089 | Naked-eye shimmer motes | `vfx_motes_shimmer_loop_small.png` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-090 | Memory fade | `shader: memory_fade` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-091 | Sky gradient by band | `shader: sky_band` | VFX | First playable | Engine-built | Needed | not specced |
| ASSET-092 | Water surface | `shader: water` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-093 | Wind on grass | `shader: wind_grass` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-094 | Fog | `shader: depth_fog` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-095 | Rain streaks | `vfx_rain_streaks_loop_small.png` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-096 | Capture iris and flash | `shader: capture_iris` | VFX | First playable | Engine-built | Needed | not specced |
| ASSET-097 | Look tag shader parameters | `shader: lens_post params` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-098 | Sunbeam event | `vfx_motes_beam_loop_small.png` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-099 | Lumen Dusk event | `shader: event_lumen_dusk` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-100 | Aurora event | `shader: event_aurora` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-101 | Darkroom light swatch | `shader: light_swatch` | VFX | MVP | Engine-built | Needed | not specced |
| ASSET-102 | Print reveal | `shader: print_reveal` | VFX | First playable | Engine-built | Needed | not specced |

### UI screens

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-103 | Title and sign-in | `ui_screen (.tscn + SVG parts)` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-104 | Account panel | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-105 | Restore notice | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-106 | Pending deletion | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-107 | Starting choice | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-108 | Darkroom breakdown card | `ui_screen (.tscn + SVG parts)` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-109 | Gallery | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-110 | Gear shop and detail | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-111 | Sell to clients | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-112 | Gear screen (loadout, Bag, Shelf) | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-113 | Wallet history | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-114 | Forecast panel | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-115 | Field swap list and iris wipe | `ui_screen (.tscn + SVG parts)` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-116 | Leaderboard | `ui_screen (.tscn + SVG parts)` | UI | Later | asset-forge recipe | Needed | not specced |

### HUD and icons

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-117 | Camera viewfinder skin | `ui_vf_camera_*.svg` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-118 | Phone viewfinder skin | `ui_vf_phone_*.svg` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-119 | Red live dot and battery | `ui_icon_live_24.svg, ui_icon_battery_24.svg` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-120 | Exploration device icon | `ui_icon_device_24.svg` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-121 | Compass strip | `ui_compass_strip.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-122 | Context prompts | `ui_prompt_*.svg` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-123 | Clock and band glyphs | `ui_icon_band_*_24.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-124 | Weather icons | `ui_icon_weather_*_24.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-125 | Event toast and map marker | `ui_icon_event_24.svg` | UI | Later | asset-forge recipe | Needed | not specced |
| ASSET-126 | Presence glyph, 3 states | `ui_icon_presence_*_24.svg` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-127 | Curious cue | `ui_icon_curious_24.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-128 | Tier badge set | `ui_badge_tier_c..sss.svg, ui_badge_tier_unknown.svg` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-129 | Tier frame ornaments | `ui_frame_tier_*.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-130 | Connection indicator | `ui_icon_conn_*_24.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-131 | Developing and saving marks | `ui_mark_developing.svg, ui_mark_saving.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-132 | Guest badge and keep-progress banner | `ui_chip_guest.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-133 | Envelope and lock icons | `ui_icon_mail_24.svg, ui_icon_lock_24.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-134 | Glint currency icon and wallet chip | `ui_icon_glint_24.svg` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-135 | Gear side silhouettes | `ui_icon_gear_*_48.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-136 | Bound phone mark | `ui_icon_bound_24.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-137 | Bag and Shelf art | `ui_bag_canvas.svg, ui_shelf_wood.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-138 | Client print icon | `ui_icon_print_24.svg` | UI | MVP | asset-forge recipe | Needed | not specced |
| ASSET-139 | Logo, spinner, iris transition | `ui_logo_aperture.svg, ui_spinner_aperture.svg` | UI | First playable | asset-forge recipe | Needed | not specced |
| ASSET-140 | Co-op role icons | `ui_icon_role_*_24.svg` | UI | Later | asset-forge recipe | Needed | not specced |

### Fonts

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-141 | Inter | `assets/ui/fonts/` | UI | First playable | OFL font | Needed | not specced |
| ASSET-142 | IBM Plex Mono | `assets/ui/fonts/` | UI | First playable | OFL font | Needed | not specced |

### Audio

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-143 | Shutter ML_SOFT | `sfx_shutter_ml_soft_01.ogg` | SFX | First playable | asset-forge recipe | Needed | not specced |
| ASSET-144 | Shutter PHONE_SYNTH | `sfx_shutter_phone_synth_01.ogg` | SFX | First playable | asset-forge recipe | Needed | not specced |
| ASSET-145 | Shutter ML_LEAF | `sfx_shutter_ml_leaf_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-146 | Subject anticipation tone | `sfx_subject_anticipation_01.ogg` | SFX | First playable | asset-forge recipe | Needed | not specced |
| ASSET-147 | Subject decisive bell | `sfx_subject_decisive_01.ogg` | SFX | First playable | asset-forge recipe | Needed | not specced |
| ASSET-148 | Subject emergence chime | `sfx_subject_emerge_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-149 | Subject tuck hush | `sfx_subject_tuck_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-150 | Subject flight swirl | `sfx_subject_flee_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-151 | Subject return chime | `sfx_subject_return_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-152 | Footsteps by surface | `sfx_step_{grass,sand,stone,plank,water}_01..03.ogg` | SFX | First playable | asset-forge recipe | Needed | not specced |
| ASSET-153 | Landing thump | `sfx_land_soft_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-154 | Ladder rungs | `sfx_ladder_rung_01..03.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-155 | Wading splashes | `sfx_wade_01..03.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-156 | Viewfinder raise rustle | `sfx_raise_rustle_01.ogg` | SFX | First playable | asset-forge recipe | Needed | not specced |
| ASSET-157 | Aperture dial click | `sfx_dial_click_01.ogg` | SFX | First playable | asset-forge recipe | Needed | not specced |
| ASSET-158 | Focus confirmation | `sfx_focus_confirm_01.ogg` | SFX | First playable | asset-forge recipe | Needed | not specced |
| ASSET-159 | Zoom ring | `sfx_zoom_ring_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-160 | Bayonet mount twist-click | `sfx_mount_bayonet_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-161 | Thread mount screw | `sfx_mount_thread_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-162 | Pocket rustle and Bag pack | `sfx_pocket_rustle_01.ogg, sfx_bag_pack_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-163 | Refusal tap | `sfx_ui_refuse_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-164 | Sale tick and purchase cue | `sfx_ui_sale_01.ogg, sfx_ui_buy_01.ogg` | SFX | MVP | asset-forge recipe | Needed | not specced |
| ASSET-165 | Account saved chime | `sfx_ui_saved_01.ogg` | SFX | Later | asset-forge recipe | Needed | not specced |
| ASSET-166 | Reconnected cue | `sfx_ui_reconnect_01.ogg` | SFX | Later | asset-forge recipe | Needed | not specced |
| ASSET-167 | Ambience beds by condition | `amb_{clear,overcast,fog,night}_loop.ogg` | Ambient | MVP | CC0 pack | Needed | not specced |
| ASSET-168 | Rain layer | `amb_rain_loop.ogg` | Ambient | MVP | CC0 pack | Needed | not specced |
| ASSET-169 | Event build-up cue | `sfx_event_build_01.ogg` | Ambient | Later | asset-forge recipe | Needed | not specced |
| ASSET-170 | Music | `music_*_loop.ogg` | Music | Later | Needs an artist | Needed | not specced |

### Marketing

| Asset ID | Name | File | Type | Priority | Route | Status | Spec File |
|---|---|---|---|---|---|---|---|
| ASSET-171 | Title key art | `ui_keyart_title.png` | Other | Later | Needs an artist | Needed | not specced |
