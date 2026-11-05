# Photo Recipe & Re-render

> **Status**: Designed 2026-11-05 (pending `/design-review` in a fresh session)
> **Author**: user + agents (systems-designer)
> **Last Updated**: 2026-11-05
> **Last Verified**: 2026-11-05
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-05 — CONCERNS fixed: promise reworded to same moment and facts with a mood guard; stale text. Requirement: Open Question 3 (archive packs on Web) must be resolved, with player wording for a long-term failure, before the first layout change ships. NOT ASSESSED: MDA target.
> **Implements Pillar**: Pillar 2 "Every photo matters" (a photo is one small, permanent, exact record of what the camera did, and its score never drifts); supports Pillar 1 "Seeing is the skill" (what the player framed is what comes back) and the anti-pillar "not a photo-upload or social-media app" (no player image ever reaches the server)

## Summary

Photo Recipe & Re-render defines what a photo is: a small, versioned, integer-only binary record built by the server at the shutter, and the client-side pipeline that turns that record back into a picture in the Darkroom, Gallery, Leaderboards and Found Photos. A recipe has a client-readable render block and a server-only audit block, 118 bytes plus 47 per subject, with a hard cap of 512 bytes. No image is stored on the server. Scores are frozen at capture; a re-score writes a separate audit row and changes nothing. Every version that a recipe names stays loadable forever, so an old photo keeps the place, gear and rules it was shot with.

> **Quick reference** — Layer: `Core` · Priority: `MVP` · Key deps: `Camera Model` (`ShotSettings`, `evaluate_shot`), `Subject & Spirit Behaviour` (SubjectSnapshot), `World Time, Weather & Light` (WorldSnapshot), `Network Transport & Server Authority` (assembly split, commit before reveal), `Accounts & Server Persistence` (opaque immutable storage), `Player Movement & Exploration` (capture pose), `Gear Catalog & Specs` (`spec_rev`) · Engine: Godot 4.7.2, Web/Compatibility; rendering and storage claims absent from `docs/engine-reference/godot/` are marked UNVERIFIED

## Overview

This system answers five questions for the rest of the game.

1. **What is a photo, as data?** A recipe: camera pose, resolved settings, gear, world state, subject state and the few render results that cannot be recomputed. It holds no pixels and no account data.
2. **Who builds it, and when?** The session server, after validation and before scoring. The client proposes only pose, settings and the viewed tick (Network Rule 7). Scoring reads the bytes as they will be stored, so what was scored is exactly what was saved.
3. **How does it stay true for years?** Records are immutable and every field is an integer. A recipe names the versions it depends on: `recipe_version`, `world_rules_version`, `subject_rules_version` per subject, `spec_rev` per gear item and `scene_rev` for the place. Each version stays loadable. Migrations never touch recipes (Accounts Rule 43).
4. **How is a score protected?** The score is frozen at capture with its `scoring_version` (Accounts Rule 23). A later re-score proves the record, or raises an alarm. It never rewrites anything.
5. **How does a player see it?** The client's **render studio** rebuilds the moment offscreen from the render block and draws one frame. Thumbnails are rendered on demand on the client and cached on the client.

The photo-as-recipe idea is the concept's: *"a photo is stored as the camera position, settings, time of day and subject pose, then re-rendered when viewed. Photos stay tiny, the server can verify the score, and players cannot upload arbitrary images."*

**Not owned here:** what a photo is worth (Photo Scoring); its tier and the roll (Capture Tier Resolution); who owns it and which photos a player may keep (Gallery); screens and layout (Darkroom & Gallery UI, Leaderboard & Social UI); board rules (Leaderboards); the meaning of camera, world and subject fields (their own GDDs, which own content while this GDD owns the schema).

**MVP scope.** MVP uses the format, the server build, frozen scores, the Darkroom and Gallery renders, and the thumbnail cache. Leaderboards and Found Photos arrive in Vertical Slice and reuse the same pipeline, so the rules for them are set now. `scene_rev` 1 is the only scene revision at launch, so archive packs (Rule 30) need no MVP implementation, only the field and the CI check.

## Player Fantasy

**Framing: indirect.** Players never see a recipe. They feel it whenever a photo comes back as the same moment with the same facts. Guard: a cosmetic or pipeline change may never perceptibly alter a print's mood, colour or light; such a change needs a `scene_rev` or art sign-off.

**"That's the moment I kept."** The anchor moment: a player opens their gallery a year after launch and finds the Halo Keeper shot from the lighthouse rail, on their first good lens, long since sold. The ring is at the same angle, the same blue dusk sits behind it, the same soft edge falls where their focus fell short. The harbour has been rebuilt since then, and in the photo it still looks the way it did that evening. The score has not moved by a point. Nothing in the game can quietly take that moment back.

**"Every print on the wall is real."** On a leaderboard, each print was rebuilt from what the server witnessed. It cannot be pasted in, edited or faked. A photo at the top of the wall got there through something a player actually did.

**"Prints develop, they don't load."** A list of photos appears at once as data and soft colour, and each print then comes up like paper in a tray. Waiting has the feel of the darkroom, never of a spinner.

**MDA aesthetics served** (primary first): *Expression* (a kept record of the player's own eye), *Sensation* (a print developing), *Fellowship* (a wall of shots that can be trusted). **SDT:** *Competence* because the photo shows honestly what the player did; *Relatedness* through other players' real moments.

**Language.** Prints, developing, the old harbour. Never "rendering", "cache", "asset missing" or "version mismatch". A photo that cannot be shown yet "is still drying", never "failed to load".

**What the player must never feel:** that an old photo's moment, mood or light changed; that a score shifted after an update; that a screen is slow because of their own collection; that the game stole a shot in the viewfinder to draw prints.

## Detailed Design

### Core Rules

**A. What a recipe is**

1. **A photo is a recipe.** A recipe is the complete record needed to rebuild and audit one shot. It holds no pixels. It has two blocks with different audiences (Rule 3).
2. **Recipes hold no personal data.** No account ID, display name, `rid`, `item_id` or client timestamp appears in either block. Network Rule 7 says the server fills in the player ID: that value goes in the `photo` row (`author_ref`, `owner_account_id`, Accounts Rule 24), not in the recipe. Gear is stored as model and revision, never as an owned item, so a sold lens leaves old photos intact (Inventory Interactions). Author, owner and server commit time stay in the row, which is why a change of owner never touches a recipe.
3. **Two blocks (Decision D3).**
   - The **render block** is everything a client needs to draw the photo. It is the only part any client ever receives. Column: `photo.recipe`.
   - The **audit block** is what only the server may read: world and subject tiers, moment points, journal digests, off-frame subjects and audit flags. Column: `photo.recipe_audit`.

   Separate columns make the safe behaviour the default: a query that forgets to filter cannot leak. It also keeps server-side values such as moment points away from clients (World Edge Cases: internal points are server-side values).
4. **Immutable.** Both blocks are written once in the capture commit and never change, even for an operator. Corrections to a photo are new audited rows (Accounts Rule 29).
5. **Teammates and other players are never in a recipe** (Movement R20). Neither is anything the HUD draws (art bible §7.1: *"Nothing UI is ever in a stored photo"*). NPCs are also excluded (Rule 41, Decision D11).

**B. The binary format (Decisions D1, D2)**

6. **Encoding.** Fixed-width little-endian integers, two's complement for signed fields, fields in the order listed, with no padding, no varints and no floats. Godot's Variant serialisation is not used, because its byte format is outside this project's control. Blocks are self-delimiting through `n_view` and `n_total`, so a byte count that disagrees with those counts makes the record unreadable (Edge Cases).
7. **Tier values are IDs, never ranks.** Tiers are stored as a 3-byte ASCII field, NUL padded (`"A\0\0"`, `"SSS"`). A numeric tier code would be a rank in disguise, which Rarity Tier Ladder Core Rule 2 and Accounts Rule 20 forbid. On decode every value goes through the ladder's `parse`.
8. **Enums are stable codes.** `band`, `condition`, weather, `event_id`, `surface_id`, `program`, `phone_mode`, `focus_mode`, `pose`, `lifecycle` and `awareness` use published integer codes. Code 0 means none or default wherever that exists. The tables are append-only: a code is never reused or reordered. CI compares them with the last released table.
9. **Render block, fixed part: 106 bytes.**

   | Group | Field | Encoding | Bytes | Range and meaning | Source |
   |---|---|---|---|---|---|
   | Header | `recipe_version` | u16 | 2 | ≥ 1 | this system |
   | | `flags` | u16 | 2 | bit 0 stance (0 stand, 1 sneak); bit 1 `is_phone`; bit 2 `night_applied`; bit 3 `portrait_applied`; bit 4 `key_source` (0 sun, 1 moon); others 0 | Movement, Camera, World |
   | | `zone_id` | u16 | 2 | zone | server position (World Edge Cases) |
   | | `world_rules_version` | u16 | 2 | version active at `capture_ms` | World Rule 13 |
   | | `scene_rev` | u16 | 2 | zone layout revision (Rule 28) | zone data |
   | | `render_rev` | u16 | 2 | render pipeline revision at capture (Rule 32) | build constant |
   | | `capture_ms` | i64 | 8 | server UTC ms | World F13 |
   | | `n_view` | u8 | 1 | 0–8; subjects in the render block | F2 |
   | Pose | `eye_x_mm`, `eye_y_mm`, `eye_z_mm` | i32 ×3 | 12 | zone space, mm | Movement R15, quantised (Rule 15) |
   | | `yaw_mdeg` | u32 | 4 | 0–359,999, normalised | Movement R15 |
   | | `pitch_mdeg` | i32 | 4 | −85,000 to 85,000 | Movement R15 |
   | | `speed_mm_s` | u16 | 2 | horizontal body speed | Movement R15 |
   | | `surface_id` | u8 | 1 | surface under the feet | Movement R15 |
   | Settings | `mode` | u8 | 1 | bits 0–1 `program`, 2–3 `phone_mode`, 4–5 `focus_mode` | Camera Rule 30 |
   | | `module_id` | u8 | 1 | 0 on bodies | Camera Rule 30 |
   | | `f_deci` | u16 | 2 | 19–3000 | Camera Rule 30 |
   | | `zoom_milli` | u16 | 2 | 1000 on bodies | Camera Rule 30 |
   | | `n_deci` | u16 | 2 | 10–320, **resolved** | Camera Rule 31 |
   | | `t_us` | u32 | 4 | resolved | Camera Rule 31 |
   | | `iso` | u32 | 4 | resolved | Camera Rule 31 |
   | | `comp_t` | i8 | 1 | −9 to +9; 0 in `MANUAL` | Camera Rule 30 |
   | | `focus_mm` | u32 | 4 | up to `FOCUS_INF_MM` (1,000,000) | Camera Rule 30 |
   | | `burst_id` | u16 | 2 | 0 = single | Camera Rule 30 |
   | | `burst_index` | u8 | 1 | frame in burst | Camera Rule 30 |
   | Gear | `body_key`, `body_rev` | u16 ×2 | 4 | body or phone `model_key` (Rule 12), `spec_rev` | server loadout |
   | | `lens_key`, `lens_rev` | u16 ×2 | 4 | 0, 0 on a phone | server loadout |
   | | `adapter_key`, `adapter_rev` | u16 ×2 | 4 | 0, 0 if none | server loadout |
   | World | `phase_ms` | u32 | 4 | 0 to `DAY_MS` − 1 | World F1 |
   | | `band` | u8 | 1 | band code | World Rule 2 |
   | | `weather` | u8 | 1 | bits 0–1 previous, 2–3 next, 4–5 effective | World Rule 4 |
   | | `blend_permille` | u16 | 2 | 0–1000 | World F4 |
   | | `condition` | u8 | 1 | one of seven conditions | World F5 |
   | | `event_id` | u8 | 1 | 0 = none | World Rule 7 |
   | | `event_phase_permille` | u16 | 2 | 0–1000 | World F9 |
   | | `key_elev_deci` | i16 | 2 | −900 to 900 | World F11 |
   | | `key_azim_deci` | u16 | 2 | 0–3599 | World F11 |
   | | `scene_ev_deci` | i16 | 2 | −40 to 160 | World F12 |
   | | `wind_dir_deg` | u16 | 2 | 0–359 | World Visual/Audio |
   | Results | `exposure_err_deci` | i16 | 2 | −100 to 100 | Camera F4 |
   | | `noise_permille` | u16 | 2 | 0–1000 | Camera F6 |
   | | `shake_bp` | u16 | 2 | 0 to about 3,000 | Camera F13 |

   The `weather` byte adds the **next** weather to World Rule 14's list. During the first half of a blend the effective weather equals the previous weather, so those two alone cannot give the mix the player saw, although World's Edge Cases promise it (Cross-References request 4).
10. **Render block, per subject in view: 36 bytes.**

    | Field | Encoding | Bytes | Meaning |
    |---|---|---|---|
    | `species_key` | u16 | 2 | Subject Rule 1 |
    | `variant_key` | u8 | 1 | Subject Rule 1 |
    | `anchor_key` | u16 | 2 | Subject Rule 2 |
    | `schedule_index` | u32 | 4 | With `zone_id` and the three keys above, rebuilds `appearance_id` (Subject Rule 3) |
    | `subject_rules_version` | u16 | 2 | **Per subject**: an appearance runs to its end under the version active at its start (Subject Rule 12), so two subjects in one photo can differ |
    | `pose` | u8 | 1 | Subject Rule 28 |
    | `state` | u8 | 1 | bits 0–3 `lifecycle`, 4–7 `awareness` |
    | `pose_phase_permille` | u16 | 2 | 0–1000 |
    | `pos_x_mm`, `pos_y_mm`, `pos_z_mm` | i32 ×3 | 12 | zone space |
    | `yaw_deci` | u16 | 2 | 0–3599 |
    | `scale_permille` | u16 | 2 | |
    | `glow_permille` | u16 | 2 | 0–1000 |
    | `motion_bp` | u16 | 2 | 0–5,000 (Camera F14) |
    | `motion_dir` | u8 | 1 | On-frame smear direction, 256ths of a circle (Cross-References request 3) |

11. **Audit block: 12 bytes fixed, then 11 per subject in view, then 47 per subject out of view.**

    | Part | Field | Encoding | Bytes | Meaning |
    |---|---|---|---|---|
    | Fixed | `render_hash` | u32 | 4 | `hash32` of the render block; binds the two blocks |
    | | `audit_flags` | u8 | 1 | bit 0 `trail_anomaly` (Movement R19); bit 1 `view_tick_clamped` (Network Rule 24) |
    | | `n_total` | u8 | 1 | All photographable subjects in the zone, 0–8 |
    | | `light_tier` | char[3] | 3 | World F7 |
    | | `world_moment_tier` | char[3] | 3 | World F10 |
    | Per subject in view (11) | `subject_tier` | char[3] | 3 | Subject F12 |
    | | `subject_moment_tier` | char[3] | 3 | Subject F13 |
    | | `subject_moment_points` | u8 | 1 | 0–100 |
    | | `journal_digest` | u32 | 4 | Subject Rule 32 |
    | Per subject out of view (47) | 36-byte subject record, then the 11-byte tail | | 47 | Same fields as above |

    Subjects in view come first in `n_view` order, in the same order as in the render block. The order is ascending by `appearance_id` text within each group. Every subject Rule 32 of the Subject GDD requires is present, and its content is unchanged (Decision D13).
12. **Gear needs an integer key (Decision D9).** `model_id` is a string of 20 or more characters, so three of them would cost over 60 bytes. Gear Catalog adds a permanent integer `model_key` per model, as Subject already does with `species_key`, with the same never-reused rule. 0 means none. Decoding turns it back into `model_id`.

**C. Building a recipe on the server**

13. **Build order.** Only after Network's seven checks have passed (Network Rule 21) and `capture_tick` is resolved:

    1. Compute `capture_ms` (World F13).
    2. Quantise the proposed pose (Rule 15).
    3. Validate the pose and settings on the quantised values (Movement R18, Network Rule 25, Camera `validate_settings`).
    4. Read the server loadout (Inventory Rule 30), the WorldSnapshot and the SubjectSnapshots at `capture_ms`.
    5. Run `evaluate_shot` (Camera Rule 32).
    6. Assemble and encode both blocks (`recipe_encode`).
    7. Decode them again and hand the decoded form to Photo Scoring and Capture Tier Resolution (Rule 16).
    8. Commit the blocks with the score, tier, roll and frame spend in one transaction (Accounts Rule 26).
    9. Send `SHUTTER_RESULT` with `saved: true` and the render block (Rule 18).
14. **Field authority.** Only these values come from the client: pose (eye, yaw, pitch, stance, speed, surface) and the settings Camera Rule 30 lists as sent. Everything else comes from server state (Network Rule 7, acceptance criterion 30). Resolved values replace sent ones (Camera Rule 31).
15. **Quantise first.** Movement records metres and degrees. `recipe_quantise` converts them to mm and millidegrees, rounding half up, **before** validation and evaluation. Non-finite input is rejected there. Scoring and the render therefore use the same numbers, so no rounding gap can open between the score and the print. Applying the function to an already quantised value changes nothing, so the client may send quantised integers (protocol ADR).
16. **Scoring reads what is stored.** Step 7's round trip means a defect in the encoder shows up as a wrong result in test, instead of as a score that cannot be reproduced later. `recipe_decode(recipe_encode(r)) = r` for every valid record.
17. **Client time is never stored.** Movement R15 lists a client timestamp in the capture pose. The server may use it for trail checks, but it does not enter the recipe, because Accounts Rule 25 forbids storing client-supplied time and `capture_ms` already holds the authoritative instant.
18. **Reveal only after commit (Network Rule 29).** The render block contains exposure, shake and motion results, which are part of the result (Camera Rule 32). `SHUTTER_RESULT` with `saved: false` therefore carries **no** recipe data at all. `saved: true` carries the render block, at most 394 bytes, inside its 1,024-byte budget. `RESULT_QUERY` returns the same response after a reconnect.

**D. Freezing and re-score (Decision D10)**

19. **Frozen at capture.** The score, its parts, `scoring_version` and the tier are stored at capture and are never recomputed in place (Accounts Rule 23). No code path in this system writes those columns after the capture commit.
20. **Re-render never scores.** A client render reads no score and computes none. A difference between prints on two devices can never affect a score.
21. **What re-score reads.** Re-scoring runs in the server's scoring-only mode (research §4). It reads the stored snapshots and never re-simulates (Subject Rule 32). The inputs split into two kinds:

    | Kind | Fields | Re-score behaviour |
    |---|---|---|
    | **Frozen inputs**: need history that is gone after capture | `motion_bp`, `motion_dir` (past subject positions), `night_applied` (past stillness, `still_since_ms`), `portrait_applied`, subject snapshots | Read as stored |
    | **Recomputable**: pure functions of the recipe | `exposure_err_deci`, `noise_permille`, `shake_bp`, `in_dof`, `defocus_bp`, `x_bp`, `y_bp`, resolved auto settings | Recomputed with the catalog at `spec_rev` and compared with the stored value |

22. **Audit row.** Every re-score writes a new `rescore_audit` row: `photo_id`, `scoring_version` used, the resulting score and parts, `matched` (bool), the reason, and the operator or job. It never touches the `photo` row (Accounts Rule 23).
23. **Two kinds of re-score.**
    - **Replay** uses the photo's own `scoring_version`, and it must reproduce the frozen score exactly. A mismatch raises a determinism alarm. The stored record wins, as World's and Subject's Edge Cases require.
    - **What-if** uses a newer `scoring_version` for tuning and telemetry. It never produces a player-visible value.
24. **Three audit checks, all read-only.** (a) `render_hash` matches the render block. (b) World: recompute `world_state` under `world_rules_version` and compare it with the stored fields (World Edge Cases). (c) Subject: where a journal is still retained, re-derive each snapshot and compare its `journal_digest` (Subject Rule 32). Journals are found through `photo.session_ref`, a row field, because they are stored per session. After `JOURNAL_RETENTION_DAYS` check (c) is reported as `not_available`, which is not a failure. A nightly job replays `AUDIT_SAMPLE_PER_NIGHT` random photos.

**E. Versions and compatibility**

25. **What each version pins.**

    | Field | Pins | Kept loadable by |
    |---|---|---|
    | `recipe_version` | The byte layout | Decoders in the client and server build, forever |
    | `world_rules_version` | Bands, presets, rules (World Rule 13) | Server for audit; client keeps the public band and preset tables only |
    | `subject_rules_version` | Species data, including the art asset (Subject Rules 1, 12) | Server for audit; client keeps art and pose tables |
    | `spec_rev` | Gear specs and `look_tags` (Gear Rule 7) | Server; client keeps render fields of every revision |
    | `scene_rev` | Zone layout and occluders (Rule 28) | Server collision archive; client archive pack (Rule 30) |
    | `render_rev` | Which pipeline drew it first (Rule 32) | Recorded only |
    | `scoring_version` | Score rules (row, not recipe) | Photo Scoring |

26. **Any layout change is a new `recipe_version`.** A new field, a changed width or a changed meaning all need one. Every released version gets a golden test vector that is never deleted.
27. **Decoders chain, records don't change.** Each version has a pure in-memory function `upgrade_vN_to_vN1`. Reading an old recipe runs the chain and gives the current in-memory form, with a defined default for any field that did not exist. The result is never written back (Accounts Rule 43). Client and server ship in lockstep (Network D4), so a current build reads every older version. Only a stale tab can meet a newer one (F6).
28. **`scene_rev` is the layout revision of a zone (Decision D4).** Each zone has an integer `scene_rev` that increases when, and only when, a **layout change** ships. A layout change alters anything inside `layout_hash`: collision, the baked eye volume, or the position, silhouette or visibility of a static object that can be seen from the eye volume. `content_version` (Network Rule 12) is a different value: it changes with any content change, and it exists to keep live clients in step. `scene_rev` exists so old photos keep their place.
29. **Cosmetic changes need no revision.** Materials, palette, textures, LODs and shader fixes keep the silhouette and the layout, so `scene_rev` stays the same and old photos pick them up, under the "same facts, not same pixels" rule (Rule 37). Art changes that alter what a place *is* are layout changes, even if the mesh count is unchanged. CI compares `layout_hash` with the last released one and fails the build if it changed while `scene_rev` did not.
30. **Archive packs.** When a layout change ships, the outgoing layout is kept in two forms. The server keeps its collision and eye volume, so a re-score can use the geometry the photo was scored against. The client gets a **delta archive pack** on the static asset host, holding only the meshes and transforms that differ from the current zone (F13). A client fetches a pack when it first needs it and may keep it in the asset cache. Runtime pack loading on Web is UNVERIFIED (Open Question 3).
31. **Never the wrong picture.** A photo is drawn with exactly its `scene_rev`, or it is not drawn. Drawing it in today's zone could put the camera inside a new wall or remove what the photo was of. While a pack is unavailable the print shows its light swatch and "still drying" (Rule 46). The score, title and metadata stay visible.
32. **Old photos use the current pipeline (Decision D12).** Only one render pipeline ships. Pipeline improvements change how old photos look, within the fact list in Rule 37. `RENDER_REV` increases with any visible pipeline change, which invalidates cached thumbnails (Rule 48). `render_rev` in the recipe records the pipeline at capture, so a future pipeline can keep a legacy look if that is ever wanted. A pipeline change must keep the meaning of every recorded integer.
33. **Retired content.** Retired gear keeps resolving (Gear States). A subject species removed from spawning stays in the data for its old versions, with its art. No content a recipe can name is ever deleted from the data. CI fails if a released `model_key`, `species_key`, `scene_rev` or enum code disappears.

**F. The client re-render**

34. **Render studio.** One offscreen 3D viewport, isolated from the live world, with its own light and environment, draws one frame on request. It uses its own world so a historic time of day cannot touch the live scene. An offscreen `SubViewport` with its own `World3D`, single-frame update and pixel read-back on Web are all UNVERIFIED in the engine reference (Open Question 1).
35. **Inputs.** The render reads the render block, the public band and preset tables, zone assets at `scene_rev`, catalog data at each `spec_rev`, and subject art under each `subject_rules_version`. It never reads the seed (World Rule 14), a score or live world state. Automatic values, exposure and motion are read from the recipe and are not re-solved, because rules and tables can change after capture.
36. **Scene set-up.** From the block: the camera uses the eye position, yaw, pitch and roll 0; `vfov_deg` uses Gear F3 with `f_deci`, `crop_eff_milli` and `zoom_milli`; the frame is always 3:2 (Camera Rule 3). The light condition, weather mix and band crossfade come from `phase_ms`, `blend_permille` and the tables (World Edge Cases). The key light uses the stored angles. Each subject is placed at its stored position, yaw, scale, pose, phase and glow; secondary motion is seeded from `appearance_id` and `capture_ms` (Subject Rule 28). The lens layer is always on (Camera Rule 2); the third-person shimmer is never drawn.
37. **Same facts, not same pixels (Camera Decision D7).** Across devices, sizes and future builds, these are the facts that must hold: camera pose and FOV; subject position, pose and glow (F10); exposure within one third stop; what is sharp and what is not; condition, weather mix and event; the seeded grain pattern's presence and strength; shake and smear direction and length. Antialiasing, filtering and small shader differences may vary.
38. **Post order (proposal; technical-artist owns the shader).** Depth blur, subject smear, shake blur, exposure gain (Camera F21, same formula and clamp as the preview), phone tone, grade and vignette, look tags, then grain. The stored `exposure_err_deci` drives F21.
39. **Blur is a custom shader on Web.** Native depth of field does not work on Compatibility (prototype finding, observed in a Web export). A custom full-screen spatial shader reading `hint_depth_texture` and `hint_screen_texture` does work there, with multi-tap sampling; `textureLod` on the screen texture showed no blur. That finding covers the main viewport only: the same shader inside an offscreen viewport is UNVERIFIED. `docs/engine-reference/godot/modules/rendering.md` recommends `Compositor` for post effects, but it does not say whether that works on Compatibility, so this design does not rely on it (UNVERIFIED).
40. **Everything animated reads recorded time.** Shader time comes from F7, grain from F8, shake direction from `mod(capture_ms, 16)` (Camera F13). A free-running timer in anything that can appear in a photo is a defect (art bible P4, §8.5).
41. **Nothing unrecorded may appear in a photo (Decision D11).** The art bible's test applies: *"would the gallery copy of this photo differ from what the player saw?"* The recipe stores no NPC state, so NPCs are drawn ghosted in the viewfinder as teammates are (Movement R20) and are absent from the photo. Any moving world object (a boat, a door) must be a pure function of `phase_ms` and public data, or it is treated the same way.
42. **The queue yields to play.** A render runs only when the live game can spare it. While the device state is `Live`, `Firing` or `Exposing`, the queue is paused, so a print can never cost a player a frame in the viewfinder. Renders are spaced at least `RENDER_MIN_GAP_MS` apart.
43. **Quality does not drop facts (Decision D14).** Camera's preview quality setting never reaches this system (Camera Rule 48, criterion 48). A low-end device may take longer or use fewer blur taps at thumbnail size, but it never removes blur, smear or grain from a print.

**G. Prints, thumbnails and lists (Decisions D5, D6)**

44. **Three sizes, all 3:2.** The art bible gives no photo size, only that a subject must read in a 64 px thumbnail, so these are proposals. `THUMB` 288×192 is used for lists, walls and Found Photos frames, and it must still read at 64 px when scaled down. `PRINT` 960×640 is the Darkroom and detail view. `FULL` 1920×1280 is full screen and export. Only `THUMB` is cached on disk.
45. **Thumbnails are rendered on demand and cached on the client.** There is no server copy (Rule 51). The cache has two levels: decoded textures in RAM, least recently used first (`THUMB_RAM_SLOTS`), and encoded images in persistent browser storage through `user://` (`THUMB_CACHE_MB`, F12). Persistence across sessions and inside an iframe is UNVERIFIED (Accounts Open Question 10), and it is optional: if storage fails, thumbnails are simply re-rendered. Encoding a thumbnail to a compressed buffer on Web is UNVERIFIED.
46. **Light swatch first.** Every print appears at once as a card with a soft gradient made from its `condition`, `band` and `event_id`, using no 3D work. The rendered print then fades in. The swatch is also what is shown for `PACK_NEEDED` and `UPDATE_NEEDED`.
47. **Render order.** Visible prints come first, top to bottom, then the next `PREFETCH_ROWS` rows. Jobs are grouped by (`zone_id`, `scene_rev`), so each zone loads once per pass. A job for a print that scrolls away is dropped unless it has started. Own photos are rendered once at the Darkroom, so they are already cached in the Gallery on that device.
48. **Cache key.** `(photo_id, size, RENDER_REV)`. Recipes are immutable, so an entry can go stale only when `RENDER_REV` changes. Old entries are replaced lazily, and until then the old thumbnail is shown rather than a swatch.
49. **A board in one request.** A list endpoint returns each entry's render block and display metadata together (F4), so a top-100 board is one small response with no request per photo. The list decides what is shown, so a cached thumbnail of a photo that has been hidden or removed is simply never asked for.
50. **Darkroom.** On `saved: true` the client renders the `PRINT` size, then derives the `THUMB` from it. The develop animation covers this: Network recommends a minimum develop time of at least 600 ms. The frozen frame (Camera Rule 49) is never used as the print or the thumbnail, because it has no smear, shake or final grain.

**H. Stored images and sharing (Decisions D7, D8)**

51. **No photo image is stored on the server.** Three reasons, in order of weight:

    - **Trust.** The concept promises that *"players cannot upload arbitrary images"*, so a client-rendered image can't be accepted.
    - **No renderer.** The server is headless and has no GPU (systems index, High-Risk Systems).
    - **Cost.** F5 shows images cost about 580 times the storage of recipes, on a project limited to free services.

    If measurement shows boards are too slow (F11), the fallback in Decision D5 option C is a disposable atlas baked by a trusted renderer. It would be a cache, never a source of truth, and it needs a new decision.
52. **Save a print (Vertical Slice).** A player can save any photo they can view as an image file. The client renders `FULL` with a print border and a small caption (photographer, tier, serial if any, game name), then hands the file to the browser. The border belongs to the export only: the photo area has no UI (art bible §7.1), and this is not a stored photo. Browser download through `JavaScriptBridge` is UNVERIFIED.
53. **Share link (Vertical Slice).** A link holds only the opaque `photo_id`. Opening it starts the game, which shows that print from the public render block. There is no image preview in link cards, because no image exists on a server. A hidden, removed or purged photo gives "This print is no longer available". The link is a view of the game's record, so it can't be used to prove a saved image is real, and the in-game print remains the authority.
54. **Data export (Alpha, Accounts Rule 50).** The JSON export carries the render block as base64 with `recipe_version`, and a decoded field list. The audit block is excluded: it holds no personal data, and it does hold server-side values.

**What this system does not own:** the worth of a photo (Photo Scoring); tier and roll (Capture Tier Resolution); ownership, limits and discarding (Gallery); board rules and queries (Leaderboards); placement rules (Found Photos); screens (UI systems); the meaning of camera, world, subject, movement and gear fields (their GDDs); the shader code and final look (technical-artist, art bible).

### States and Transitions

**Recipe on the server**

| State | Entered when | Leaves to | Notes |
|---|---|---|---|
| `Assembling` | `SHUTTER` passes Network's checks | `Encoded`; `Rejected` on pose or settings failure | Session memory only |
| `Encoded` | Both blocks encoded and decoded back | `Committed`; `Lost` on a session crash | Scoring and the roll happen here. An outbox retry keeps the same bytes and `rid` |
| `Committed` | Meta commit | row states in Accounts (`Saved`, `Hidden`, `Transferred`, `Removed`) | Immutable from here |
| `Rejected` | Validation failed | terminal | No recipe exists; no frame is spent (Camera Rule 38) |
| `Lost` | Session crash before commit | terminal | Nothing was revealed (Accounts States) |

**Render job on the client**

| State | Entered when | Leaves to | Shown |
|---|---|---|---|
| `Requested` | UI asks for a print | `Cached` on a cache hit; else `Checking` | Light swatch |
| `Checking` | Cache miss | F6 verdict: `Queued`, `WaitingPack`, `UpdateNeeded`, `Unreadable` | Light swatch |
| `WaitingPack` | Verdict `PACK_NEEDED` | `Queued` once fetched; retries with back-off | Swatch, "still drying" |
| `Queued` | Verdict `EXACT` | `Rendering`; `Dropped` if scrolled away | Swatch |
| `Paused` | Device `Live`, `Firing` or `Exposing`, or the tab is hidden | back to `Queued` | Swatch |
| `Rendering` | Queue slot free and zone ready | `Cached`; `Queued` on context loss | Swatch |
| `Cached` | Render done | — | Print fades in |
| `UpdateNeeded` | Verdict `UPDATE_NEEDED` | cleared by a reload | Swatch, update prompt |
| `Unreadable` | Verdict `UNREADABLE` | terminal on this client | Swatch, "This print can't be shown"; logged |
| `Dropped` | Print left the view before starting | — | — |

### Interactions with Other Systems

| System | Direction | What flows | Owner of the rule |
|---|---|---|---|
| Camera Model | Camera → this | `ShotSettings`, resolved `n_deci`, `t_us`, `iso`, `exposure_err_deci`, `noise_permille`, `shake_bp`, per-subject `motion_bp` and direction, flags, F20/F21 | Camera owns meaning; this system owns the schema |
| Player Movement & Exploration | Movement → this | Capture pose (R15), R18 validation | Movement owns meaning and ranges; this system owns quantisation |
| World Time, Weather & Light | World → this | WorldSnapshot, public tables, `hash32` | World owns content |
| Subject & Spirit Behaviour | Subject → this | SubjectSnapshots, `journal_digest`, per-subject version | Subject owns content |
| Gear Catalog & Specs | Gear → this | `model_key`, `model_id`, `spec_rev`, render fields, `look_tags` | Gear |
| Inventory & Loadout | Loadout → this | Mounted `model_id`, `spec_rev` at capture (Rule 30) | Loadout |
| Network Transport & Server Authority | both | Assembly split, `capture_tick`, `SHUTTER_RESULT`, `RESULT_QUERY`, commit before reveal | Network owns transport; this system owns recipe bytes |
| Accounts & Server Persistence | both | Opaque blocks, `recipe_version`, `session_ref`, `rescore_audit` rows, purge | Accounts owns storage; never decodes recipes |
| Rarity Tier Ladder | Ladder → this | `parse` for tier IDs | Ladder |
| Photo Scoring | this → Scoring | Decoded recipe at capture; scoring-only mode for replay | Scoring owns score and `scoring_version` |
| Capture Tier Resolution | this → Resolution | Decoded recipe | Resolution owns tier and roll |
| Gallery | Gallery ↔ this | Photo rows, render blocks; `request_print` | Gallery owns ownership and limits |
| Darkroom & Gallery UI | UI → this | `request_print(photo_id, size, priority)`; states in UI Requirements | UI owns layout |
| Leaderboards, Leaderboard & Social UI (VS) | both | Render blocks in one list; gear display from keys | Leaderboards owns queries |
| Found Photos (VS) | Found → this | Print requests at `THUMB`, lowest priority | Found Photos owns placement |
| First-Claim & Image Serials (Alpha) | this → First-Claim | `appearance_id`, `capture_ms`, audit | First-Claim |
| Composite & Panorama Photos (Full Vision) | that → this | A future record referencing several recipes, needing a new version | That GDD |
| Zone Access & Travel (VS) | Zone → this | `scene_rev`, zone assets, `layout_hash` | Zone data; this system owns the revision rule |
| Moderation & Reporting (Alpha) | Moderation → this | Audit requests | Moderation |

## Formulas

All byte, time and size values marked estimate are placeholders until the first spike measures them. Only the server's values in F1 and F2 affect stored data; F7–F13 are client or planning values.

### F1. Recipe size

The recipe_bytes formula is defined as:

`recipe_bytes = RENDER_FIXED_B + AUDIT_FIXED_B + n_total × SUBJECT_B`, with `SUBJECT_B = SUBJECT_RENDER_B + SUBJECT_AUDIT_B`; `render_bytes = RENDER_FIXED_B + n_view × SUBJECT_RENDER_B`; load check: `RENDER_FIXED_B + AUDIT_FIXED_B + MAX_ACTIVE_PER_ZONE × SUBJECT_B ≤ RECIPE_MAX_B`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| RENDER_FIXED_B | int (bytes) | 106 in v1 | Rule 9 | Fixed render block |
| AUDIT_FIXED_B | int (bytes) | 12 in v1 | Rule 11 | Fixed audit block |
| SUBJECT_RENDER_B | int (bytes) | 36 in v1 | Rule 10 | Subject record |
| SUBJECT_AUDIT_B | int (bytes) | 11 in v1 | Rule 11 | Subject audit tail |
| SUBJECT_B | int (bytes) | 47 in v1 | calculated | Full cost of one subject |
| n_total | int | 0–`MAX_ACTIVE_PER_ZONE` (8) | Subject Rule 32 | Photographable subjects in the zone |
| n_view | int | 0–`n_total` | F2 | Subjects in the render block |
| RECIPE_MAX_B | int (bytes) | 512 | research §5.4 budget; config | Hard cap on both blocks together |
| recipe_bytes | int (bytes) | 118–494 | calculated | Stored size |
| render_bytes | int (bytes) | 106–394 | calculated | Client payload |

**Output Range:** bounded: minimum 118 B (landscape, no subjects), maximum 494 B (8 subjects), leaving 18 B of headroom. The largest `MAX_ACTIVE_PER_ZONE` the cap allows is floor((512 − 118) / 47) = **8**, so raising that knob to 9 (541 B) fails the load check until the format or the cap changes. Adding 3 bytes per subject would also reach the limit (8 × 50 + 118 = 518 B).
**Example:** three subjects in the zone, one in view: render 106 + 36 = **142 B**; audit 12 + 11 + 2 × 47 = **117 B**; total 118 + 3 × 47 = **259 B**. This fits Accounts' `PHOTO_ROW_B` estimate of 600–1200 B at the 8-subject maximum (494 + about 200 = 694 B).

### F2. View set

The in_view formula is defined as (float; server only, and the result is stored as record order):

`in_view = (zc + R > 0) AND (abs(x_bp) ≤ 5,000 + r_x + VIEW_MARGIN_BP) AND (abs(y_bp) ≤ 5,000 + r_y + VIEW_MARGIN_BP)`, where `r_x = 10,000 × R × f_eq_real / (max(zc, 1) × 36)` and `r_y = 10,000 × R × f_eq_real / (max(zc, 1) × 24)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| zc | float (mm) | any | Camera F15 | Depth along the look |
| x_bp, y_bp | int (bp) | any | Camera F15 | Position from frame centre |
| R | int (mm) | per species | Subject `BOUNDS_MM` | Subject bounds radius |
| f_eq_real | float (mm) | 12–450 | Gear F3 | Equivalent focal length |
| VIEW_MARGIN_BP | int (bp) | 0–1,000; default 100 | data file | Extra margin for smear and glow |
| r_x, r_y | float (bp) | ≥ 0 | calculated | Bounds radius on the frame |
| in_view | bool | — | calculated | Goes in the render block |

**Output Range:** true or false. This test is deliberately wider than Camera's `in_frame`, so a subject whose edge or smear enters the frame is drawn. It ignores occlusion: depth decides that in the render. At zc ≤ 0, `max(zc, 1)` prevents a division by zero. A subject around the eye gives very large `r_x` and passes, which only costs bytes.
**Example:** 75 mm equivalent, 8 m ahead, 1 m right, placeholder R 300 mm: `x_bp` 2,604; `r_x` = 10,000 × 300 × 75 / (8,000 × 36) = 781; limit 5,881, so **true**. At 3 m right: `x_bp` 7,813 > 5,881, so **false**.

### F3. Angle quantisation error

The pose_err_px formula is defined as:

`pose_err_px = (ANGLE_Q_MDEG / 2,000) × frame_w_px / hfov_deg`, with `hfov_deg = 2 × atan(18 / f_eq_real)` in degrees

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| ANGLE_Q_MDEG | int (0.001°) | 1 in v1 | format constant | Angle step |
| frame_w_px | int (px) | 288–1920 | Rule 44 | Render width |
| f_eq_real | float (mm) | 12–450 | Gear F3 | Equivalent focal length |
| hfov_deg | float (°) | 4.58–112.6 | calculated | Horizontal field of view |
| pose_err_px | float (px) | 0.0013–0.21 | calculated | Largest shift between the live view and the stored pose |

**Output Range:** bounded: at most 0.21 px (1920 px wide, 450 mm equivalent), at least 0.0013 px (288 px wide, 12 mm equivalent). The error exists only between the live view and the photo: score and print share the quantised value (Rule 15). Position rounding of 0.5 mm is similar at normal distances and reaches about 8 px only on a subject 1.5 m away at 450 mm equivalent, which is under 0.5% of frame width.
**Example:** 450 mm equivalent, 1,920 px: 0.0005 × 1,920 / 4.58 = **0.21 px**. Hundredth-of-a-degree steps would give 2.1 px, a visible shift in a long-lens shot, which is why the format spends 4 bytes per angle.

### F4. Board payload

The board_bytes formula is defined as:

`board_bytes = n × ((RENDER_FIXED_B + v × SUBJECT_RENDER_B) × ENC_FACTOR + ENTRY_META_B)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| n | int | 1–100 | Leaderboards | Entries in one response |
| v | float | 0–8 | measured; estimate 1.2 | Average subjects in view |
| ENC_FACTOR | float | 1.0 binary, 1.334 base64 | meta API format | Transport overhead |
| ENTRY_META_B | int (bytes) | 60–250; estimate 120 | estimate | Rank, name, score, tier, ID |
| board_bytes | float (bytes) | up to 64,600 at defaults | calculated | One response, before compression |

**Output Range:** bounded by the top-100 limit. At base64 and the worst case (`v` = 8) it is about 64.6 KB. There is no failure value.
**Example:** 100 entries, `v` 1.2, base64: (106 + 43.2) × 1.334 = 199 B; + 120 = 319 B; × 100 = **31.9 KB**. Sending thumbnails instead would be 100 × 12 KB = 1.2 MB, about 38 times more per board view, against the egress concern in Network F14.

### F5. Stored image cost

The image_cost_ratio formula is defined as:

`image_cost_ratio = PRINT_B / recipe_bytes_avg`;  `image_store_b = accounts × photos_per_account × PRINT_B`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| PRINT_B | int (bytes) | 80,000–300,000; estimate 150,000 | estimate: 1280-class JPEG | One stored image |
| recipe_bytes_avg | int (bytes) | 118–494; estimate 259 | F1 | Average recipe |
| photos_per_account | int | 0–`MAX_PHOTO_RECORDS` | Accounts F1 example: 600 | Photos held |
| accounts | int | ≥ 0 | forecast | Accounts |
| image_cost_ratio | float | about 160–2,500 | calculated | Image size as a multiple of recipe size |
| image_store_b | int (bytes) | unbounded | calculated | Added server storage if images were kept |

**Output Range:** unbounded with accounts, which is the point of the formula. It is a design justification and is not run in the game.
**Example:** 150,000 / 259 = **579×**. 1,000 accounts × 600 photos: recipes 155 MB; images **90 GB**, against Accounts F2's 1.67 GB for the entire database, before backups copy it off the host.

### F6. Render verdict

The render_verdict formula is defined as:

`render_verdict = UNREADABLE if block_invalid; else UPDATE_NEEDED if (recipe_version > RECIPE_CURRENT) or unknown_reference; else PACK_NEEDED if scene_rev is not available locally; else EXACT`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| block_invalid | bool | — | decoder | Length disagrees with `n_view`, or a field is outside its range |
| recipe_version | int | ≥ 1 | render block | Layout of this record |
| RECIPE_CURRENT | int | ≥ 1 | build constant | Newest layout this client decodes |
| unknown_reference | bool | — | calculated | A `model_key`, `spec_rev`, `subject_rules_version`, `world_rules_version` or `scene_rev` newer than this client knows |
| scene_rev | int | ≥ 1 | render block | Layout needed |
| render_verdict | enum | `EXACT`, `PACK_NEEDED`, `UPDATE_NEEDED`, `UNREADABLE` | calculated | Decides the job state |

**Output Range:** one of four values, tested in the order above. `recipe_version` is read first and an unknown version makes the rest of the block uninterpretable, so a version above `RECIPE_CURRENT` gives `UPDATE_NEEDED` without a block check.
**Example:** a stale tab with `RECIPE_CURRENT` 1 meets a version 2 recipe: **`UPDATE_NEEDED`**. A current client meets a photo with `scene_rev` 1 in a zone now at 3: **`PACK_NEEDED`**, then `EXACT` once the pack is in.

### F7. Shader time

The shader_time_s formula is defined as:

`shader_time_s = phase_ms / 1000.0`; load check: every animated shader period divides `DAY_MS`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| phase_ms | int (ms) | 0 to `DAY_MS` − 1 | render block; live World F1 | Day phase |
| DAY_MS | int (ms) | 3,780,000 | World Rule 2 | World day |
| shader_time_s | float (s) | 0–3,779.999 | calculated | The time uniform for wind, water and shimmer |

**Output Range:** bounded by the day. Raw epoch time cannot be used: a 32-bit shader float near 10⁸ seconds has steps of about 8 s, so animation would stop. At 3,780 s the step is about 0.00024 s. The wrap at phase 0 is invisible only if periods divide `DAY_MS`, which has many divisors (2⁵ × 3³ × 5⁴ × 7). The live world must use this same value, or the photo won't match what the player saw. Shader float precision on WebGL 2 is UNVERIFIED on low-end devices.
**Example:** `phase_ms` 2,300,600 → **2,300.6 s**, in the live view and in every later render.

### F8. Grain seed

The grain_seed formula is defined as:

`grain_seed = hash32(capture_ms, SALT_GRAIN)`;  `grain_u = mod(grain_seed, 65,536) / 65,536.0`;  `grain_v = floordiv(grain_seed, 65,536) / 65,536.0`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| capture_ms | int (ms) | ≥ `WORLD_EPOCH_MS` | render block | Capture time |
| SALT_GRAIN | int | constant | data file | Public salt; never `world_seed` (World Rule 14) |
| grain_seed | int | 0 to 2³²−1 | calculated, World `hash32` | Stable seed |
| grain_u, grain_v | float | 0 to 0.99998 | calculated | Offsets for the grain pattern, split so a shader float keeps them exact |

**Output Range:** bounded. The grain pattern is fixed per photo. Strength comes from `noise_permille`; at 0 no grain is drawn.
**Example (illustrative hash):** `grain_seed` 2,882,400,018 = 0xABCDEF12: `grain_u` = 0xEF12 / 65,536 = 61,202 / 65,536 = **0.934**; `grain_v` = 0xABCD / 65,536 = 43,981 / 65,536 = **0.671**.

### F9. Render blur radius

The render_blur_px formula is defined as (float; client only):

`render_blur_px = min(defocus_bp, RENDER_BLUR_CAP_BP) × render_w_px / 20,000`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| defocus_bp | float (bp) | 0 to about 3,000 | Camera F8 per pixel | Blur disc diameter |
| RENDER_BLUR_CAP_BP | int (bp) | 400–3,000; default 800 | data file; UNVERIFIED cost | Largest diameter drawn |
| render_w_px | int (px) | 288, 960, 1920 | Rule 44 | Render width |
| render_blur_px | float (px) | 0–76.8 at defaults | calculated | Blur radius |

**Output Range:** 0 to 76.8 px at `FULL`, 11.5 px at `THUMB`. The cap is set in basis points of frame width, so a thumbnail and a print of one photo show the same blur in proportion. This defines Camera F20's `RENDER_BLUR_MAX_PX` as `RENDER_BLUR_CAP_BP × render_w_px / 20,000`. Large radii may need more taps or a lower-resolution blur pass (Open Question 2).
**Example:** KR 85 at f/1.4 background, about 749 bp: at `THUMB` 749 × 288 / 20,000 = **10.8 px**; at `FULL` **71.9 px**. Camera's preview draws this at 14 px on a 1,280 px frame.

### F10. Render fidelity

The frame_err_bp formula is defined as:

`frame_err_bp = max(abs(x_render − x_bp), abs(y_render − y_bp))`; pass when `frame_err_bp ≤ RENDER_FRAME_TOL_BP`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| x_render, y_render | float (bp) | any | Test: subject centre projected through the render studio camera | Position in the render |
| x_bp, y_bp | int (bp) | any | Camera F15, recomputed from the recipe | Position the server scored |
| RENDER_FRAME_TOL_BP | int (bp) | 5–30; default 10 | data file | Tolerance |
| frame_err_bp | float (bp) | ≥ 0 | calculated | Mismatch |

**Output Range:** unbounded above; it is a test measure and is not run in the game. The default of 10 bp is 0.1% of frame width: 1.9 px at `FULL`.
**Example:** `x_bp` 2,604, `x_render` 2,601.5, `y_bp` 0, `y_render` 1.2: max(2.5, 1.2) = **2.5 bp**, a pass.

### F11. Board fill time

The board_fill_ms formula is defined as:

`board_fill_ms = (zone_cold ? t_zone_ms : 0) × n_zones + n_miss × max(t_render_ms, RENDER_MIN_GAP_MS)`, with `n_miss = ceil(n_prints × (1 − hit_rate))`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| n_prints | int | 1–100 | UI | Prints wanted |
| hit_rate | float | 0–1 | measured | Share already cached |
| t_render_ms | float (ms) | 10–200; estimate 40 | NOT MEASURED, spike | One `THUMB` render and read-back |
| RENDER_MIN_GAP_MS | int (ms) | 16–200; default 50 | data file | Minimum spacing (Rule 42) |
| t_zone_ms | float (ms) | 500–10,000; estimate 3,000 | NOT MEASURED, spike | Loading a zone into the studio |
| zone_cold | bool | — | calculated | The zone is not yet loaded |
| n_zones | int | 1–zones on the board | calculated | Zones to load |
| board_fill_ms | float (ms) | 0 to unbounded by zones | calculated | Time until all wanted prints are drawn |

**Output Range:** 0 with a full cache. Grows with zones, so job grouping (Rule 47) matters from Vertical Slice. Targets: first visible page `BOARD_PAGE_TARGET_MS` (2,000 ms) warm and 6,000 ms cold on reference hardware, which is not yet defined. The list itself shows at once, so this is time to full prints and never time to usable.
**Example (all estimates):** 24 visible, empty cache, zone loaded: 24 × 50 = **1,200 ms**. Cold: 3,000 + 1,200 = **4,200 ms**. All 100, warm: **5,000 ms**. Returning player, hit rate 0.9: ceil(2.4) = 3 × 50 = **150 ms**. Boards change slowly, so most views after the first are close to this last case.

### F12. Thumbnail cache

The thumb_cache_entries formula is defined as:

`thumb_cache_entries = floor(THUMB_CACHE_MB × 1,048,576 / THUMB_B)`;  `thumb_ram_b = THUMB_RAM_SLOTS × THUMB_W × THUMB_H × 4`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| THUMB_CACHE_MB | int (MB) | 8–128; default 48 | data file | Persistent cache limit |
| THUMB_B | int (bytes) | 6,000–25,000; estimate 12,000 | NOT MEASURED | One encoded thumbnail |
| THUMB_RAM_SLOTS | int | 40–240; default 120 | data file | Decoded textures kept |
| THUMB_W, THUMB_H | int (px) | 288, 192 | Rule 44 | Thumbnail size |
| thumb_cache_entries | int | calculated | calculated | Thumbnails on disk |
| thumb_ram_b | int (bytes) | 8.8–53 MB | calculated | RAM used, uncompressed RGBA8 |

**Output Range:** bounded by the two knobs. At defaults, 26.5 MB of RAM is inside the 512 MB project budget, but it sits on top of the 64 MB texture budget per loaded scene (art bible §8.6). Least recently used entries go first.
**Example:** floor(48 × 1,048,576 / 12,000) = **4,194** thumbnails; 120 × 288 × 192 × 4 = **26,542,080 B**.

### F13. Scene archive

The archive_bytes formula is defined as:

`archive_bytes = Σ over superseded scene_rev r of delta_b(r)`;  `archive_egress_month_b = Σ fetches(r) × delta_b(r)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| delta_b(r) | int (bytes) | 100 KB–20 MB | measured at build | Assets that differ between revision `r` and the current zone |
| fetches(r) | int | ≥ 0 | measured | Pack downloads per month |
| archive_bytes | int (bytes) | ≥ 0 | calculated | Static storage |
| archive_egress_month_b | int (bytes) | ≥ 0 | calculated | Static host egress |

**Output Range:** 0 until the first layout change, then it grows with each one. Browser-side caching keeps `fetches` low. A pack is a static file and takes no session or database load.
**Example (placeholder):** two layout changes at 3 MB each: **6 MB** stored. 500 fetches a month of one pack: **1.5 GB/month**, small next to Network F14's 17.9 GB/month for 3 average players.

## Edge Cases

**Building a recipe**

- **If the zone has more subjects than the format allows**: this cannot happen in a valid build, because F1's load check fails the server at start. If it still occurs at runtime, the record keeps all subjects in view, drops out-of-view subjects farthest from the eye first, sets a log entry, and the shot still commits: a player never loses a shot to a size check.
- **If a photo has no subject in the zone**: `n_view` and `n_total` are 0, and the recipe is 118 B. Capture Tier Resolution decides what such a photo is (Subject Edge Cases).
- **If a subject's bounds are in view but its centre is not**: it is in the render block (F2), even when Camera's `in_frame` is false. Photo Scoring decides whether it counts.
- **If a subject is in `HIDDEN` or `GONE` at `capture_ms`**: it is not in the recipe (Subject Rule 15).
- **If the pose has a non-finite value**: `recipe_quantise` rejects it with `ERR_OUT_OF_RANGE`; no frame is spent.
- **If yaw is outside 0–360°**: it is wrapped to 0–359,999 before validation (Movement R11 allows unbounded yaw).
- **If rounding moves a pose across a validity limit** (eye band or reach): the quantised value is the one judged. Client `can_shoot` uses the same quantised check, so an honest client is not surprised.
- **If two appearances in one photo have different `subject_rules_version` values**: each record keeps its own (Rule 10).
- **If a shot lands during a weather blend**: previous, next and effective weather and the blend are all stored; the effective weather decides gameplay and the mix decides the look.
- **If the same `rid` is retried from the outbox**: the same bytes are sent, and the permanent key makes the second insert a no-op (Accounts Rule 30). The recipe is never rebuilt, because a rebuild could differ.
- **If a late retry arrives for a removed photo**: "removed", per Accounts States. No recipe returns.
- **If encoding fails, or decode of the fresh bytes differs from the input**: the shot is refused with `ERR_SERVICE_DEGRADED` before any roll, no frame is spent, and an alarm is logged. A stored record must never be one the decoder can't read back.

**Stored records**

- **If a stored block fails its length or `render_hash` check**: the print shows the swatch and "This print can't be shown", the frozen score stays visible and stays valid, an operator alarm is raised, and the row is never altered. A backup can be compared (Accounts Rule 37).
- **If a server cannot load a stored `spec_rev`**: re-score returns `not_available`, the frozen score stands, and an alarm is raised. Gear's "needs re-render" edge case maps to this state.
- **If `enabled_cap` falls after a photo was taken**: its stored tiers are unchanged (Subject Edge Cases).
- **If a replay gives a different score**: the frozen score stays, the audit row has `matched = false`, and a determinism alarm is raised. Nothing is paid out or clawed back automatically.
- **If a stored WorldSnapshot differs from a recomputed one**: the stored one stays and an alarm is raised (World Edge Cases).
- **If a journal has been deleted by retention**: check (c) reports `not_available`, not a failure.
- **If a photo changes owner** (Alpha): recipe bytes do not change.
- **If the account is purged**: the row and both blocks are deleted (Accounts Rule 44). No account data existed in the blocks, so backups hold nothing extra. Share links return "no longer available", and the `roll` row keeps de-duplication.
- **If a Hidden photo is requested directly by ID**: the service returns not found to anyone but its owner, so a share link can't reach it.

**Versions and content**

- **If a zone asset changes after a photo was taken**: a cosmetic change is picked up, and the photo keeps its layout (Rule 29). A layout change raises `scene_rev`, and the old layout stays available as an archive pack (Rule 30), so the print still shows the old place.
- **If a build changes `layout_hash` without raising `scene_rev`**: CI fails it.
- **If the archive pack can't be fetched** (offline, host down): the print stays in `WaitingPack` with the swatch and "still drying", and it retries with back-off. It is never drawn in today's zone (Rule 31).
- **If a pack is permanently lost**: the print shows the swatch and metadata and an operator alarm is raised. Score and record stay valid. The pack can be rebuilt from version control, which is why every `scene_rev` is tagged at release.
- **If a photo's camera is inside new geometry**: this can't arise, since the old layout is what is drawn.
- **If a subject's art is revised under a new `subject_rules_version`**: old photos keep the art of their own version. A pure bug fix that keeps the silhouette may be applied to old versions as a cosmetic change.
- **If an old `look_tags` value is removed from the shader**: this is forbidden by Rule 33. A tag that no longer has an effect must still be accepted and drawn neutrally.
- **If the client's catalog doesn't know a `model_key`**: `UPDATE_NEEDED`; the gear shows a neutral silhouette and "?" (Gear Edge Cases).
- **If a stale tab meets a newer `recipe_version`**: `UPDATE_NEEDED`. It does not guess at the layout.
- **If `RENDER_REV` changes**: thumbnails are kept until replaced lazily; a player's whole gallery doesn't re-render at once.

**Rendering on the client**

- **If the player raises the viewfinder during a render**: new jobs pause (Rule 42). A job already in its frame finishes, because a single frame can't be split.
- **If the WebGL context is lost**: jobs return to `Queued`, cached images are untouched, and the studio is rebuilt (engine behaviour UNVERIFIED).
- **If the tab is hidden**: the queue pauses, and jobs resume on return.
- **If persistent storage is full, blocked or evicted**: thumbnails live in RAM only. Nothing else changes.
- **If a device can't compile the blur shader**: a print is still drawn without blur, and a small "simple print" note is shown. This breaks the fact list and is logged, so the rate can be measured. Scores are not affected.
- **If two tabs share the cache**: same key, same content. The last writer wins harmlessly.
- **If a player tampers with their local cache or render**: only their own screen changes. Boards and scores read server data.
- **If a player signs out**: the persistent thumbnail cache is cleared, so the next person on a shared device doesn't see private photos.
- **If a list contains a photo removed after the response**: the print still draws from the render block already held, and the next refresh drops it.
- **If 100 prints span many zones** (VS and later): jobs group by zone, and at most one extra zone is in memory at a time, inside the 512 MB budget. A zone is unloaded when its group ends.
- **If a Found Photo print is in view while the player is in the world**: it is the lowest priority and follows Rule 42. The frame shows the swatch until it is drawn.

**Degenerate strategies**

- **Editing a saved image and posting it as real**: possible and harmless. The link and the in-game print are the authority (Rule 53).
- **Scripted scraping of render blocks to map spirits**: blocks are historic, and off-frame subjects are never sent. Seed and schedule stay secret (World Rule 11).
- **Filling a gallery to slow the game**: lists render only what is visible, and the cost per list doesn't grow with collection size.

## Dependencies

| System | Type | Interface | Status |
|---|---|---|---|
| Camera Model: Viewfinder & Exposure | Hard | `ShotSettings`, `evaluate_shot` outputs, F20, F21 | Designed |
| Subject & Spirit Behaviour | Hard | SubjectSnapshot, `journal_digest`, secondary-motion seed | Designed |
| World Time, Weather & Light | Hard | WorldSnapshot, public tables, `hash32` | Designed |
| Network Transport & Server Authority | Hard | Rule 7 split, `capture_tick`, Rule 29, `SHUTTER_RESULT` | Designed |
| Accounts & Server Persistence | Hard | Opaque immutable storage, audit rows | Designed |
| Player Movement & Exploration | Hard | Capture pose R15, R18 | Designed |
| Gear Catalog & Specs | Hard | `model_key` (new), `spec_rev`, render fields, `look_tags` | Designed; needs `model_key` |
| Inventory & Loadout | Hard | Server loadout at capture | Designed |
| Rarity Tier Ladder | Hard | `parse`, tier IDs | Designed |
| Photo Scoring | Dependent (hard) | Decoded recipe, scoring-only replay, `scoring_version` | Not started |
| Capture Tier Resolution | Dependent (hard) | Decoded recipe | Not started |
| Gallery | Dependent (hard) | Rows, render blocks, `request_print` | Not started |
| Darkroom & Gallery UI | Dependent (hard) | `request_print`, job states | Not started |
| Leaderboards; Leaderboard & Social UI | Dependent (VS) | Render blocks in list responses | Not started |
| Found Photos | Dependent (VS) | `THUMB` prints | Not started |
| Zone Access & Travel | Dependent (VS) | `scene_rev`, `layout_hash` | Not started |
| First-Claim & Image Serials | Dependent (Alpha) | `appearance_id`, audit | Not started |
| Composite & Panorama Photos | Dependent (Full Vision) | New version | Not started |

**Bidirectional follow-ups (not edited here; this run may write only this file):** see Cross-References for the requests each GDD needs. Systems-index row 9 lists Camera, Subject, World, Network and Movement, but not Gear Catalog, Inventory, Accounts or Rarity Tier Ladder. Row 9's category is Persistence while this GDD's layer is Core, as briefed.

## Tuning Knobs

| Knob | Default | Safe range | Category | Affects | Notes and risk |
|---|---|---|---|---|---|
| `RECIPE_MAX_B` | 512 | 494–1024 | Gate | Storage, F1 load check | Too low: valid zones fail load. Raising it changes Accounts F1 |
| `VIEW_MARGIN_BP` | 100 | 0–1,000 | Feel | Which subjects are drawn | Too low: a smear edge is cut. Too high: larger payloads |
| `THUMB_W` × `THUMB_H` | 288×192 | 192×128–432×288 | Curve | Render cost, list clarity | Must read at 64 px. Changing it needs a `RENDER_REV` bump |
| `PRINT_W` × `PRINT_H` | 960×640 | 720×480–1200×800 | Curve | Darkroom cost | Must finish inside the develop time |
| `FULL_W` × `FULL_H` | 1920×1280 | 960×640–3840×2560 | Curve | Export, memory | Higher sizes cost RAM and blur taps |
| `RENDER_MIN_GAP_MS` | 50 | 16–200 | Feel | F11 fill time and hitching | Too low: scrolling hitches. Too high: slow boards |
| `RENDER_BLUR_CAP_BP` | 800 | 400–3,000 | Curve | Largest background blur | Cost UNVERIFIED |
| `RENDER_FRAME_TOL_BP` | 10 | 5–30 | Gate | Fidelity test | Too low: false failures across GPUs |
| `PREFETCH_ROWS` | 2 | 0–6 | Feel | Scroll smoothness | Too high: work on prints never seen |
| `THUMB_CACHE_MB` | 48 | 8–128 | Gate | Repeat views, browser storage | Browser quotas UNVERIFIED |
| `THUMB_RAM_SLOTS` | 120 | 40–240 | Gate | RAM, F12 | Must exceed the largest visible list plus prefetch |
| `BOARD_PAGE_TARGET_MS` | 2,000 | 1,000–5,000 | Gate | Decision D5 trigger | Breach on reference hardware reopens D5 option C |
| `AUDIT_SAMPLE_PER_NIGHT` | 100 | 0–10,000 | Gate | Early determinism alarms | Bound by scoring queue budget (Network F12) |
| `SWATCH_FADE_MS` | 200 | 0–500 | Feel | Print reveal | 0 under reduced motion |

Fixed by format and not tunable without a new `recipe_version`: all field widths, `ANGLE_Q_MDEG`, millimetre position units. Owned elsewhere: `MAX_ACTIVE_PER_ZONE` (Subject; bounded by F1), `PHONE_TONE_PERMILLE`, `PREVIEW_EV_CLAMP` (Camera), `DAY_MS` (World).

## Visual/Audio Requirements

The art bible owns the look; these are this system's needs.

- **Clean frame.** No HUD, grid, peaking, focus marks, ghosted people, floating icons or third-person shimmer in any render.
- **Lens world on.** Every render shows the lens-world grade: phone tone for phone shots, true exposure for cameras (Camera Visual/Audio).
- **Photo effects.** Grain from `noise_permille` (F8), shake as a directional blur of `shake_bp`, smear of `motion_bp` along `motion_dir` masked to the subject, look tags modifying the blur (Gear Visual/Audio; must be visible at thumbnail size). Whether smear ships in MVP is Camera Open Question 4; the data is stored either way, so it can be added later with no format change.
- **Portrait blur.** `PORTRAIT_SYNTH_BLUR_BP` is applied beyond the in-frame subject nearest the frame centre, the same choice as Camera F16. This is a proposal (Cross-References request 3).
- **Light swatch.** A soft gradient from condition, band and event, using the art bible's preset colours. Tier colours never appear on it (art bible §7.4).
- **Print reveal.** The print rises out of the swatch like developing paper. No flash and no shimmer of its own.
- **Shader standard.** Multi-tap blur conflicts with `.claude/rules/shader-code.md` (no texture reads in loops; two-pass blur). This needs the same technical-artist decision Camera Visual/Audio flags.
- **UNVERIFIED engine claims** (not in `docs/engine-reference/godot/`): `SubViewport` single-frame render and read-back on Web; `hint_depth_texture` and `hint_screen_texture` inside an offscreen viewport on Compatibility; an isolated `World3D` sharing loaded resources; `Compositor` on Compatibility; glow on Compatibility (art bible's fallback is halo cards); encoding images to a buffer on Web; byte-level `PackedByteArray` or `StreamPeerBuffer` APIs in 4.7; `user://` persistence on Web; runtime resource packs on Web; `JavaScriptBridge` downloads; WebGL context-loss behaviour.
- **Audio.** This system makes no sound. Any print or darkroom cue belongs to Audio: SFX & Ambience.

## Game Feel

| Moment | Target | Why |
|---|---|---|
| List opens | Metadata and swatches within 100 ms of the response | The list is usable before any render |
| Print appears | Fade over `SWATCH_FADE_MS` | Reads as developing |
| Darkroom print | Ready inside the develop animation (≥ 600 ms, Network Game Feel) | A normal result never waits on rendering |
| Board fill | `BOARD_PAGE_TARGET_MS` warm, 6,000 ms cold (F11) | Estimates until the spike |
| Scrolling | No hitch above one dropped frame from a render, on reference hardware | `RENDER_MIN_GAP_MS` paces the work |
| In the viewfinder | Zero render work starts | The player must never lose a frame to a print |
| Returning to a known list | Prints show at once from cache | Boards change slowly |

There is never a spinner. A print that can't be shown yet is a calm blank print, not an error.

## UI Requirements

This system provides data and states. Layout belongs to Darkroom & Gallery UI and Leaderboard & Social UI.

- **`request_print(photo_id, size, priority)`** and **`cancel_print(photo_id)`**, returning the job state and, when ready, a texture. Priority is `VISIBLE`, `PREFETCH` or `AMBIENT` (Found Photos).
- **`light_swatch(render_block)`**: gradient data available without rendering.
- **`recipe_facts(render_block)`**: display values for the photo's detail view: gear from keys, focal length, aperture, shutter speed, ISO, time band, weather, place and capture date.
- **`recipe_alt_text(render_block)`**: a short text description for screen readers and for players who can't see the print ("A Halo Keeper at blue hour, at the lighthouse"). Exact wording: narrative-director and ux-designer.
- **Job-state wording** (cozy; final text from ux-designer):

  | State | Text |
  |---|---|
  | `WaitingPack` | "Still drying" |
  | `UpdateNeeded` | "A newer print. Reload to see it." |
  | `Unreadable` | "This print can't be shown" |
  | Removed or hidden (via link) | "This print is no longer available" |

- **Save a print and Copy link** (Vertical Slice) are UI actions on the detail view.
- **Reduced motion.** `SWATCH_FADE_MS` is treated as 0; the SSS shimmer on boards is owned by the UI.
- **Score is never tied to a print's state.** A swatch-only card still shows score, tier and owner.

## Cross-References

**Sources**

| Document | Section | Used for |
|---|---|---|
| `design/gdd/camera-model-viewfinder-exposure.md` | Rules 2, 3, 30–32, 44, 48, 49; F4, F6, F8, F13–F16, F20, F21; D7 | Content, re-render inputs, fact rule |
| `design/gdd/subject-spirit-behaviour.md` | Rules 1–3, 12, 15, 28, 29, 31, 32 | Snapshot content, re-score reads the snapshot |
| `design/gdd/world-time-weather-light.md` | Rules 10, 13, 14; F1, F4, F11, F12, F13; Edge Cases | Snapshot, rules versions, re-render rule |
| `design/gdd/gear-catalog-specs.md` | Rules 2, 7; Edge Cases; D10 | `spec_rev` kept by photos |
| `design/gdd/network-transport-server-authority.md` | Rules 6, 7, 12, 21, 24, 25, 28, 29; F3, F14; D4, D5 | Server assembly, reveal after commit |
| `design/gdd/accounts-server-persistence.md` | Rules 18–30, 43, 44, 50; F1, F2; States | `photo` record, frozen scores, no migration |
| `design/gdd/player-movement-exploration.md` | R10, R11, R15, R18–R20 | Capture pose |
| `design/gdd/inventory-loadout.md` | Rule 30; Interactions | Model IDs, never `item_id` |
| `design/gdd/rarity-tier-ladder.md` | Core Rules 1, 2 | Tier IDs, never ranks |
| `design/art/art-bible.md` | P4; §3.2 (64 px), §7.1, §7.4, §8.5, §8.6 | Re-render rule, no UI in photos |
| `design/gdd/systems-index.md` | Row 9; High-Risk Systems; A6 | Scope and risk |
| `design/gdd/game-concept.md` | Unique images; Leaderboard; Technical considerations | Source intent |
| `docs/architecture/research-web-networking.md` | §4, §5.4 | 512 B budget, scoring-only mode |
| `prototypes/aperture-concept/README.md` | Findings | Blur on Web; no-pixel scoring (gameplay NOT ASSESSED) |

**Requests to other GDDs** (not edited here)

| # | GDD | Request |
|---|---|---|
| 1 | Accounts | Rule 22 cites Network F3 as the recipe cap, but F3 caps the `SHUTTER` message, not a stored recipe; cite `RECIPE_MAX_B` here. Add `recipe_audit`, `session_ref` and the `rescore_audit` record. Rule 25 says every timestamp comes from the meta clock, but `capture_ms` comes from the session server inside an opaque block; add that exception. |
| 2 | Network | Rule 7's player ID lives in the row, not the recipe. `SHUTTER_RESULT` carries the render block with `saved: true` only. The `SHUTTER` cap note ("recipe budget") should refer to the client-proposed fields only. |
| 3 | Camera Model | Add `motion_dir` to `evaluate_shot`. Mark `exposure_err_deci` as read by re-render (F21 already needs it). Name `RENDER_BLUR_CAP_BP` in F20. Confirm which subject `PORTRAIT` uses. NPCs ghosted in the viewfinder (Decision D11). |
| 4 | World | Rule 14 must also store the slot's **next** weather: previous and effective alone can't give the blend during its first half. Live shaders must take time from `phase_ms` (F7). |
| 5 | Subject | Rule 32 stands. Note that out-of-view subjects are stored in the audit block only, and that `MAX_ACTIVE_PER_ZONE` is capped at 8 by F1. |
| 6 | Gear Catalog | Add permanent `model_key`. The client catalog must keep render fields of every `spec_rev`. |
| 7 | Player Movement | R15's client timestamp is not stored (Rule 17). Metres and degrees become mm and millidegrees on the server (Rule 15). Client `can_shoot` should check the quantised pose. Yaw convention: still Camera Open Question 11(b). |
| 8 | Art bible | State photo sizes once D6 is decided. Record that NPCs are not in photos (D11). |
| 9 | Systems index | Row 9 dependencies (see Dependencies). |

## Acceptance Criteria

**A. Format**

1. [Logic] **GIVEN** every valid recipe in the fixture set, **WHEN** it is encoded and decoded, **THEN** the result equals the input field by field. `test_recipe_round_trip_preserves_every_field`
2. [Logic] **GIVEN** a recipe with 0 subjects, **WHEN** encoded, **THEN** render plus audit is 118 bytes. `test_recipe_size_no_subjects_is_118_bytes`
3. [Logic] **GIVEN** a recipe with 8 subjects, **WHEN** encoded, **THEN** the total is 494 bytes and no more than `RECIPE_MAX_B`. `test_recipe_size_eight_subjects_is_494_bytes`
4. [Logic] **GIVEN** a recipe with 3 subjects and 1 in view, **WHEN** encoded, **THEN** the render block is 142 bytes and the audit block 117. `test_recipe_blocks_split_142_and_117_bytes`
5. [Logic] **GIVEN** `MAX_ACTIVE_PER_ZONE` of 9, **WHEN** the F1 load check runs, **THEN** it fails naming both values. `test_size_load_check_nine_subjects_fails`
6. [Logic] **GIVEN** the golden bytes of every released `recipe_version`, **WHEN** the current decoder reads them, **THEN** the decoded values equal the stored expected values. `test_golden_vectors_decode_all_versions`
7. [Logic] **GIVEN** an encoded recipe, **WHEN** its bytes are inspected against a field map, **THEN** every multi-byte field is little-endian and no float is present. `test_encoding_is_little_endian_integers_only`
8. [Logic] **GIVEN** tier `"SSS"` and tier `"A"`, **WHEN** encoded, **THEN** the fields are ASCII `SSS` and `A\0\0`, and decoding passes them through `parse`. `test_tier_fields_store_ids_not_ranks`
9. [Logic] **GIVEN** a tier field holding an unknown ID, **WHEN** decoded, **THEN** the record is unreadable and no tier is coerced. `test_unknown_tier_field_is_rejected`
10. [Logic] **GIVEN** a render block whose length disagrees with `n_view`, **WHEN** decoded, **THEN** the verdict is `UNREADABLE`. `test_truncated_block_is_unreadable`
11. [Logic] **GIVEN** an encoded recipe, **WHEN** scanned, **THEN** neither block contains the account ID, `rid`, `item_id` or client timestamp of the fixture. `test_recipe_contains_no_personal_or_client_fields`
12. [Logic] **GIVEN** a blend of 300‰ moving from OVERCAST to CLEAR, **WHEN** the WorldSnapshot is encoded, **THEN** decoded previous is OVERCAST, next is CLEAR, effective is OVERCAST. `test_weather_byte_keeps_both_sides_of_blend`
13. [Logic] **GIVEN** two subjects with different `subject_rules_version`, **WHEN** encoded and decoded, **THEN** each keeps its own. `test_subject_rules_version_is_per_subject`

**B. Server build**

14. [Logic] **GIVEN** pose yaw 372.0004° and pitch 10.0005°, **WHEN** quantised, **THEN** yaw is 12,000 and pitch 10,001, and quantising again changes nothing. `test_quantise_wraps_rounds_and_is_idempotent`
15. [Logic] **GIVEN** a NaN pose field, **WHEN** quantised, **THEN** the shot is rejected with `ERR_OUT_OF_RANGE`, and no recipe exists. `test_quantise_rejects_non_finite_pose`
16. [Logic] **GIVEN** a `SHUTTER` claiming gear, a world time and a subject pose, **WHEN** the recipe is built, **THEN** those fields come from server state. `test_recipe_build_ignores_client_authoritative_claims`
17. [Logic] **GIVEN** a shot in `AUTO`, **WHEN** the recipe is built, **THEN** `n_deci`, `t_us` and `iso` are the F5 solver's values at `capture_ms`. `test_recipe_stores_resolved_auto_settings`
18. [Logic] **GIVEN** a spy on Photo Scoring, **WHEN** a recipe is built, **THEN** Scoring receives the decoded bytes and not the pre-encoding record. `test_scoring_reads_decoded_stored_form`
19. [Logic] **GIVEN** the F2 examples, **WHEN** evaluated, **THEN** 1 m right is in view and 3 m right is not. `test_in_view_uses_bounds_and_margin`
20. [Logic] **GIVEN** a subject out of view, **WHEN** encoded, **THEN** it is absent from the render block and present in the audit block. `test_out_of_view_subject_only_in_audit_block`
21. [Integration] **GIVEN** a delayed commit, **WHEN** `SHUTTER_RESULT` is sent with `saved: false`, **THEN** it contains no recipe data, and the `saved: true` message contains the render block but no audit bytes.
22. [Integration] **GIVEN** an outbox retry of a shot, **WHEN** it commits, **THEN** exactly one photo row exists and its bytes equal the first encoding.
23. [Integration] **GIVEN** a Web client, **WHEN** any meta or session response carrying a photo is captured, **THEN** it has no `recipe_audit` bytes and no `subject_moment_points`.

**C. Freezing and re-score**

24. [Integration] **GIVEN** a stored photo, **WHEN** a replay runs with its own `scoring_version`, **THEN** the score matches, `matched` is true and the `photo` row is byte-identical before and after.
25. [Integration] **GIVEN** a photo shot with `lens_std50_f18_b_01` rev 1 after rev 2 ships, **WHEN** re-scored, **THEN** rev 1 specs are used and the stored score is unchanged (Gear criterion 7).
26. [Integration] **GIVEN** a deliberately altered scoring rule under the same version, **WHEN** replayed, **THEN** a `matched = false` row and one determinism alarm exist and the frozen score is unchanged.
27. [Logic] **GIVEN** stored `motion_bp` and `night_applied` and no retained history, **WHEN** a re-score reads them, **THEN** they are used as stored and no position history is requested. `test_rescore_reads_frozen_history_inputs`
28. [Logic] **GIVEN** a stored `shake_bp`, **WHEN** recomputed from the recipe, **THEN** it equals the stored value. `test_recomputable_results_match_stored_values`
29. [Logic] **GIVEN** a changed render block, **WHEN** audit check (a) runs, **THEN** it reports a `render_hash` mismatch. `test_render_hash_detects_changed_block`
30. [Integration] **GIVEN** a photo whose journal has expired, **WHEN** audited, **THEN** check (c) reports `not_available` and the audit does not fail.

**D. Versions and compatibility**

31. [Logic] **GIVEN** a version 1 fixture and a test version 2 decoder, **WHEN** read, **THEN** the upgrade chain fills defined defaults and the source bytes are unchanged. `test_upgrade_chain_runs_in_memory_only`
32. [Logic] **GIVEN** each input combination in F6, **WHEN** evaluated, **THEN** the verdict and its priority order match the formula. `test_render_verdict_order`
33. [Integration] **GIVEN** a schema migration, **WHEN** it runs, **THEN** `recipe`, `recipe_audit` and `recipe_version` are byte-identical for all fixture photos.
34. [Integration] **GIVEN** a zone build with a moved static mesh and the same `scene_rev`, **WHEN** CI runs, **THEN** it fails on `layout_hash`, and passes when `scene_rev` is raised and an archive pack exists.
35. [Integration] **GIVEN** a material-only change, **WHEN** CI runs, **THEN** `layout_hash` and `scene_rev` are unchanged and the build passes.
36. [Integration] **GIVEN** a build that removes a released `model_key`, `species_key`, enum code or `scene_rev`, **WHEN** CI runs, **THEN** it fails.
37. [Integration] **GIVEN** a photo at `scene_rev` 1 and a client at 2 with the pack blocked, **WHEN** the print is requested, **THEN** it stays on the swatch and never draws in revision 2; when the pack is available it draws in revision 1.

**E. Re-render**

38. [Logic] **GIVEN** `phase_ms` 2,300,600, **WHEN** F7 runs, **THEN** the result is 2,300.6. `test_shader_time_uses_phase`
39. [Logic] **GIVEN** the same `capture_ms` twice, **WHEN** F8 runs, **THEN** seed and offsets match, and `world_seed` is not an input. `test_grain_seed_is_stable_and_seedless`
40. [Logic] **GIVEN** 749 bp, **WHEN** F9 runs, **THEN** the radius is 10.8 px at 288 and 71.9 px at 1920; 3,000 bp is capped at 11.5 and 76.8. `test_render_blur_scales_with_width_and_cap`
41. [Integration] **GIVEN** a fixture recipe with a subject in frame, **WHEN** rendered, **THEN** `frame_err_bp` is within `RENDER_FRAME_TOL_BP` at all three sizes.
42. [Integration] **GIVEN** a fixture recipe, **WHEN** rendered twice on one machine, **THEN** the two images are identical. Retained screenshots in `production/qa/evidence/` record the result.
43. [Integration] **GIVEN** a recipe from a shot in the Web export, **WHEN** re-rendered, **THEN** FOV and pose are identical, brightness matches within one third stop and sharp regions match (Camera criterion 46); evidence is a retained side-by-side screenshot.
44. [Integration] **GIVEN** a shot with a teammate and an NPC in the viewfinder, **WHEN** rendered, **THEN** neither appears, and no UI appears (retained screenshot).
45. [Integration] **GIVEN** the blur shader in the studio on Web, **WHEN** a shallow-depth recipe is rendered, **THEN** background blur is visible (retained screenshot). This is the first spike's pass condition.
46. [Integration] **GIVEN** preview blur quality off, **WHEN** a print is rendered, **THEN** it has full depth blur (Camera criterion 48).
47. [Integration] **GIVEN** a device in `Live`, **WHEN** jobs are queued, **THEN** none starts until the viewfinder lowers.

**F. Thumbnails and lists**

48. [Logic] **GIVEN** a cached thumbnail and an unchanged `RENDER_REV`, **WHEN** requested, **THEN** no render is queued. `test_thumbnail_cache_hit_skips_render`
49. [Logic] **GIVEN** a higher `RENDER_REV`, **WHEN** requested, **THEN** the old thumbnail is returned and one render is queued. `test_render_rev_change_replaces_lazily`
50. [Logic] **GIVEN** jobs for two zones interleaved, **WHEN** queued, **THEN** they run grouped by (`zone_id`, `scene_rev`), visible first. `test_queue_groups_by_zone_visible_first`
51. [Logic] **GIVEN** a queued job that scrolls away, **WHEN** cancelled, **THEN** it is dropped. `test_cancelled_job_is_dropped_before_start`
52. [Logic] **GIVEN** the F12 defaults, **WHEN** evaluated, **THEN** entries are 4,194 and RAM is 26,542,080 B. `test_thumb_cache_budget_values`
53. [Integration] **GIVEN** a 100-entry board, **WHEN** the list loads, **THEN** one request returns all render blocks and the response is no larger than F4's worst case.
54. [UI] **GIVEN** a 100-entry board and an empty cache, **WHEN** opened, **THEN** all entries show metadata and swatches first and prints fade in without a spinner (retained screenshots of each state).
55. [Integration] **GIVEN** persistent storage blocked, **WHEN** a gallery opens, **THEN** thumbnails still appear from RAM and no error is shown.
56. [Integration] **GIVEN** a signed-in player with cached thumbnails, **WHEN** they sign out, **THEN** the persistent cache is empty.
57. [Integration] (measurement) **GIVEN** reference hardware once defined, **WHEN** a 24-print page opens warm, **THEN** it fills within `BOARD_PAGE_TARGET_MS`. A failure reopens Decision D5.

**G. Stored images and sharing**

58. [Integration] **GIVEN** the meta API, **WHEN** its photo endpoints are listed, **THEN** none accepts image data from a client, and no image column exists.
59. [UI] **GIVEN** the Darkroom, **WHEN** a print develops, **THEN** the print is from the recipe, not the frozen frame, and it is ready within the develop animation on reference hardware (retained screenshot).
60. [UI] (VS) **GIVEN** a detail view, **WHEN** Save a print is used, **THEN** an image file at `FULL` with border and caption reaches the browser, and the photo area contains no UI (retained screenshot).
61. [Integration] (VS) **GIVEN** a share link to a removed or hidden photo, **WHEN** opened, **THEN** "This print is no longer available" shows and no render block is returned.

## Open Questions

| # | Question | Owner | Resolve by |
|---|---|---|---|
| 1 | **Spike: render studio on Web.** Does an offscreen viewport render one frame with read-back on Compatibility/WebGL 2, with its own world, and what do `t_render_ms` and `t_zone_ms` measure? | godot-specialist + technical-artist | Before Production; research §8 |
| 2 | Does the custom blur shader work inside an offscreen viewport, and what tap count or lower-resolution pass serves `RENDER_BLUR_CAP_BP` at `FULL`? Shared with Camera Open Question 1. | godot-shader-specialist + technical-artist | First spike |
| 3 | Can resource packs load at runtime on Web? If not, how does an archive load? Only needed at the first layout change after launch. | godot-specialist | Before the first post-launch layout change |
| 4 | Does `user://` persist on the chosen host, and what are the storage quotas? (Accounts Open Question 10.) | devops-engineer | First Web host test |
| 5 | Which device is the reference hardware? (Camera Open Question 1, Movement Open Question 7.) Every timing target waits for it. | technical-director + producer | First spike |
| 6 | Cross-device differences: how far do GPUs and drivers vary on the same recipe? Does `RENDER_FRAME_TOL_BP` hold? | qa-lead + technical-artist | After spike |
| 7 | Is 18 bytes of headroom enough? Likely v2 candidates: gear condition (Gear Condition) and roll angle. An out-of-view subject trim (D13 option B) is the first way to find room. | systems-designer | Before `enabled_cap` or Alpha features add fields |
| 8 | What is the exact definition of `layout_hash`: what makes a static object "visible from the eye volume"? | technical-artist + level-designer | Before the first zone is released |
| 9 | Photo Scoring isn't designed yet: must every `scoring_version` stay loadable forever for replay? Does Scoring need any field not stored here? Any addition must fit F1. | systems-designer (Photo Scoring GDD) | Photo Scoring design |
| 10 | Which subject does `PORTRAIT` key its background blur to? (Camera request 3.) | game-designer | Before Camera implementation |
| 11 | First-Claim ordering: is `capture_ms` precise enough, or must `capture_tick` be stored? (Network D11; Subject Open Question 4.) | First-Claim GDD | Alpha |
| 12 | Does the free static host allow unlimited-duration storage, and what are its egress limits (F13)? | devops-engineer | Before the first pack |
| 13 | Public read rules: can an unsigned visitor open a share link, and what rate limit applies? | security-engineer + network-programmer | Vertical Slice |
| 14 | The prototype's hypothesis that a geometry-only score feels fair is still NOT ASSESSED; this format assumes it. | game-designer | First human playtest |
| 15 | Registry: recipe sizes, `scene_rev`, `model_key` and the block split are cross-system facts and should be added to `design/registry/entities.yaml` (not edited here). | systems-designer, with user approval | After this GDD is approved |

**ADR candidates:** Photo recipe schema and versioning (research §7, item 5: Rules 6–12, 25–27); render studio and print cache (Rules 34–50); scene archive and `layout_hash` (Rules 28–31); deterministic shared library (extends the World and Subject ADR with `recipe_encode`, `recipe_decode`, golden vectors).

## Decisions to confirm

> **DECIDED 2026-11-05 (user):** every item = the recommended option.



- **D1. Recipe size target.** (a) **Hard cap 512 B; 494 B worst case; about 260 B typical.** Matches research §5.4 and Accounts' row estimate, with 18 B of headroom at 8 subjects. (b) Raise the cap to 1,024 B: more room for future fields, but it means changing the budget in Accounts F1 and the research note, and the extra storage buys nothing today. (c) Tighten to 256 B: only possible by dropping subjects from the record, which breaks Subject Rule 32. **Recommendation: (a).**
- **D2. Binary or JSON.** (a) **Fixed-width little-endian binary, with golden vectors.** Meets the cap with exact integers, and it is what makes D1 possible. It is harder to read by hand, so a debug decoder is needed. (b) JSON: easy to inspect, but about 2–3 KB for three subjects (estimate), which is over the cap, and number and field-order handling invite drift. (c) Compressed JSON: smaller, but size varies and per-record compression gains little on short records. **Recommendation: (a).**
- **D3. One record or two blocks.** (a) **Render block and audit block in two columns.** Clients can't receive server-only values by accident; costs one Accounts column. (b) One column with a stored length, sliced on read: simpler schema, but one careless query leaks the audit data. (c) One record, all client-visible: simplest, but it exposes moment points and off-frame subjects. **Recommendation: (a).**
- **D4. What happens when a zone asset changes after a photo was taken.** (a) **Cosmetic changes apply to old photos; layout changes raise `scene_rev`, and the old layout is kept in a server collision archive and a client delta pack; a print is exact or stays a swatch.** Keeps Pillar 2's promise, with the cost arriving only at the first layout change. (b) Always draw in the current zone with a "the place has changed" note: no archive cost, but old photos change, and a camera may end up inside a wall. (c) Freeze released layouts forever: no new mechanism, but zones can never be rebuilt. **Recommendation: (a).**
- **D5. How a leaderboard shows 100 photos fast on the Web.** (a) **One list response with render blocks; metadata and light swatches at once; client renders visible prints first, paced, grouped by zone, then cached.** No image egress, about 32 KB per board. The first cold view may take seconds (F11, unmeasured). (b) Render all 100 before showing the board: simple, but a long blank wait. (c) Add a trusted bake: a developer-run renderer publishes a disposable atlas of the top 100 to a static host, about 1.2 MB; instant, but it adds an operations job and stored images. Keep this as the fallback if `BOARD_PAGE_TARGET_MS` fails. **Recommendation: (a), with (c) reserved.**
- **D6. Thumbnail strategy.** (a) **On demand on the client, one 288×192 size, in a RAM cache and a persistent browser cache, keyed by photo, size and `RENDER_REV`.** Nothing on the server; repeat views are instant; a lost cache only costs re-rendering. (b) Render on demand with no persistent cache: simpler, but every session re-renders. (c) Server-stored thumbnails: fast everywhere, but needs a trusted renderer and breaks the no-upload rule. **Recommendation: (a).**
- **D7. Stored images on the server.** (a) **None.** Keeps the no-upload promise, needs no GPU, and saves about 580 times the storage (F5). Link cards can't show a picture. (b) Store images for top-tier or top-100 photos only, from a trusted renderer: helps sharing, but adds a render service and a second source of truth. **Recommendation: (a).**
- **D8. Sharing a photo outside the game.** (a) **Vertical Slice: Save a print (a local file with a print border and caption) and a share link that opens the game.** No server image and no cost; the link has no picture preview, so the player posts the saved file. (b) Save a print only: smallest scope, but other people can't open the photo in the game. (c) Public web page with a server image: the best link previews, but it needs D7 (b). **Recommendation: (a).**
- **D9. Gear reference in the recipe.** (a) **Gear Catalog adds a permanent integer `model_key`.** 2 bytes per item, same pattern as `species_key`; one Gear edit. (b) A recipe-owned lookup table of `model_id` strings: no Gear change, but a second table to keep permanent. (c) Inline strings: no table, but more than 60 extra bytes, which breaks the cap at 8 subjects. **Recommendation: (a).**
- **D10. Freezing and re-score.** (a) **Score frozen at capture; replay and what-if write audit rows only; history-dependent results are stored and read as frozen inputs; nightly sample replay.** Matches Accounts Rule 23. Each `scoring_version` must stay loadable, which is a cost for Photo Scoring. (b) The same with no nightly sample: less load, but drift is found only in a dispute. (c) Re-score all photos on each rules change: scores would stay comparable, but it breaks "my photo never changes". **Recommendation: (a).**
- **D11. NPCs and other unrecorded movers.** (a) **Ghosted in the viewfinder and absent from photos, like teammates.** Simple and honest; a photo of the town has no townsfolk. (b) Record NPC poses in the recipe: town scenes with people, but each costs bytes the cap can't hold. (c) Make NPC motion a pure function of `phase_ms`: people appear in photos at no byte cost, but it limits NPC behaviour. **Recommendation: (a) for MVP; (c) is a possible later upgrade.**
- **D12. Old photos under new render code.** (a) **One current pipeline for all photos, inside the fact list; `render_rev` is recorded.** Old photos improve with the game, and only one pipeline is maintained, but their exact pixels change. (b) Keep every pipeline: exact look forever, at a growing cost and with a larger build. **Recommendation: (a).**
- **D13. Which subjects are stored.** (a) **All photographable subjects in the zone, as Subject Rule 32 says; only those in view reach clients.** Complete for audit and First-Claim, but it uses most of the byte budget. (b) In-view subjects in full, out-of-view subjects as a short digest: frees about 30 B each, but needs a Subject change and weakens audit. **Recommendation: (a) now; (b) is the first way to make room later.**
- **D14. Low-end devices.** (a) **Same facts on every device; a slow device is slower, never simpler** (except a shader that can't compile, which is logged). Keeps Pillar 2 and a fair wall, at the cost of slower boards on weak hardware. (b) A lower-quality print mode that drops smear and grain: faster, but different devices then show different facts. **Recommendation: (a).**
- **D15. Pose precision.** (a) **Millimetre position and millidegree angles, at most 0.21 px of error (F3).** Costs 4 bytes per angle. (b) Hundredth-of-a-degree angles in smaller fields: saves about 3 bytes, but up to 2.1 px of shift on long lenses, in a game about framing. **Recommendation: (a).**
