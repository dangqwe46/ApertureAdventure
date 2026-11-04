# Subject & Spirit Behaviour

> Authoring guidance: .claude/docs/templates/guidance/game-design-document-guide.md (load per-section as you author — do not read entirely).

> **Status**: Designed 2026-11-04 (pending `/design-review` in a fresh session)
> **Author**: game-designer agent (draft for the user; every choice made on the user's behalf is listed in "Decisions to confirm")
> **Last Updated**: 2026-11-03
> **Last Verified**: 2026-11-03
> **Implements Pillar**: Pillar 1 "Seeing is the skill" (finding, approaching and timing a shy subject is the eye-and-timing check); Pillar 3 "Play together without violence" (the tension comes from shy subjects and fleeting windows; subjects never attack, chase or harm). Supports Pillar 2 "Every photo matters" (every subject pose in a photo is exact and re-renderable).
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-04 — CONCERNS fixed: world lift limited to ANTICIPATION/DECISIVE, F14 authoritative, memory fantasy added, Movement and World contracts aligned. Open: curiosity is nearly inert at cap A (Open Question below; Photo Scoring must carry that reward). NOT ASSESSED: MDA aesthetics target (none stated). TD feasibility and `/design-review` not run.

## Summary

Subject & Spirit Behaviour decides which photographable subjects exist in the world, where and when they appear, how they react to a photographer's presence, and what pose they hold at any instant. In the confirmed cozy, reflective setting the subjects are **shy spirits** and **forgotten memories** that can be seen only through a lens. Every subject has a fixed rarity tier, a seeded appearance schedule tied to World Time, Weather & Light windows, an awareness model (unaware, curious, wary, fleeing or fading) driven by the presence radius that Player Movement publishes, and a repeating **decisive pose** whose timing produces the subject part of the capture rule's Moment tier. This system also owns the rule that combines the world moment and the subject moment. Everything runs on the server as integer maths from a seed, the world clock and a tick-stamped journal, so a subject's pose at a photo's `capture_tick` is exact and reproducible.

> **Quick reference** — Layer: `Core` · Priority: `MVP` · Key deps: `Rarity Tier Ladder`, `World Time, Weather & Light`, `Player Movement & Exploration` (presence), `Network Transport & Server Authority` (server tick, snapshots, rewind) · Read by 10 systems (see Dependencies)

## Overview

This system answers four questions for the rest of the game:

1. **What is here, and when?** A seeded **appearance schedule** places subject **species** at authored **anchors** in a zone during the world windows each species needs (a band, a weather, a light event). The schedule is a pure function of `(world_seed, zone, world time, subject rules version)`, global for every session, so "the Halo Keeper comes to the lighthouse at blue hour" is a shared, learnable fact of the world.
2. **How does it react to me?** While an appearance is present, the server compares each player's **presence radius** (published by Player Movement) with their distance to the subject. Too much presence too close raises an **alarm** meter: the subject turns wary, tucks in, drifts back and, if pushed, **flees** (spirits) or **fades** (memories). A quiet, patient photographer close by raises **curiosity** instead: the subject turns to face them and drifts a little nearer. Subjects never attack, chase, block or harm anyone.
3. **What pose is it in right now?** Each species runs a repeating pose cycle: idle, a readable **anticipation**, a short **decisive pose** (opens fully, glow peaks), and settle. Being startled pauses the cycle. The pose, position, facing and glow at any millisecond are pure functions of the schedule plus the appearance's journal of reactions.
4. **What do they contribute to a photo's tier?** A **subject tier** (fixed per species and variant, never rolled) and a **subject moment tier** (from the pose at the capture instant), which this system combines with World's `world_moment_tier` into the capture rule's **Moment tier** using a bounded rule that stops players from camping a world event and ignoring the subject.

The system does not own photo scoring, the capture rule's roll, first-claim, prices, the look of subjects (art bible), or transport (Network). It owns the subject rules, data and the deterministic simulation contract.

Implementation approach (data format, journal storage, hash algorithm shared with World) is not decided here → becomes ADRs (see Open Questions).

## Player Fantasy

**Framing: direct.** The player reads this system with their eyes in every encounter.

**Memories** carry a different note: a forgotten memory cannot notice you, so the feeling is not trust but tenderness, arriving quietly and catching it before it fades.

**"It trusted me for a moment."** The fantasy is the patient nature photographer crossed with a quiet ghost story: you raise the camera and the lens shows what the naked eye cannot, a small glowing spirit drifting by the pier. You lower your stance, step onto the grass instead of the planks, and wait. It notices you, hesitates, and then turns toward you and rises. Its glow builds (the anticipation) and it opens fully for a second and a half. You press the shutter at the peak. That is Pillar 1, *"Success comes from the player's eye and timing. Gear raises the ceiling but never replaces skill,"* and the core fantasy, *"I see what others miss, and I choose what's worth keeping."*

**Anchor moment.** Blue hour at the lighthouse. The forecast was clear, the Halo Keeper is known to visit, and the player has been waiting on the cliff with a long lens. A faint shimmer on the gallery rail: it has arrived. Through the viewfinder its ring turns slowly. The player knows from last time that walking up the stairs startled it, so they stay where they are, frame, and wait for the pulse. The ring flares; the shutter clicks inside the window. Even if the photo comes out at the player's gear tier rather than the spirit's, they know exactly what they did right and what glass to come back with (Rarity Tier Ladder, Player Fantasy: higher-tier subjects are always visible and photographable).

**MDA aesthetics served** (primary first): *Discovery* (learning where and when each subject appears, and its habits), *Challenge* (approach and timing, never reflexes under threat), *Fantasy* (a hidden world revealed by the lens), *Sensation* (glow, motion and sound of the decisive pose). **SDT:** *Competence* through readable reactions and a readable anticipation before every decisive pose; *Autonomy* through many valid approaches (long lens from afar, slow sneak up close, waiting for curiosity); *Relatedness* through the subjects themselves, whose curiosity is a small bond, and through a shared schedule crewmates can plan around.

**What the player must never feel:** hunted or threatened (subjects never move toward a player aggressively, never make threatening sounds, never block paths); cheated by randomness at the shutter (the subject tier is fixed and readable; poses are telegraphed); punished harshly for a mistake (a startled spirit gets one chance to return, and failure costs minutes, not progress); told what they "almost" got (no near-miss messaging, per Rarity Tier Ladder Edge Cases).

**Language.** Calm and observational: "It's watching you," "It slipped away," "It came back," never "Target lost," "Escaped!" or "Missed an S moment!".

## Detailed Design

### Core Rules

**A. Content model**

1. **Species and variants.** A **species** is a data row describing one subject archetype: a permanent integer `species_key` (never reused or reordered, used in hashes), a string `species_id`, `kind` (`SPIRIT` or `MEMORY`), schedule rules, awareness parameters, pose cycle and moment parameters, and its art asset. A **variant** is a data row that refines a species for a specific window (for example a sunbeam-lit Driftfin) with its own `variant_key`, tier and window; the base form is variant 0. Every variant has exactly one authored **tier** (a ladder ID). Variants are content, not random outcomes.
2. **Anchors.** An **anchor** is an authored point in a zone (`zone_id`, `anchor_key`, position in integer millimetres, `drift_radius_mm`, and the list of species and variants it may host). Anchors are placed by the level-designer. Content validation (Rule 34) requires each anchor to be photographable: within `ANCHOR_MAX_SHOT_M` (default 40 m) of a cell of the zone's baked eye volume (Player Movement R18).
3. **Appearance.** An **appearance** is one scheduled visit of one variant to one anchor: `(zone_id, anchor_key, species_key, variant_key, schedule_index)`, a start and end time in world ms, and its subject tier. Its stable ID is the readable composite key `appearance_id = "z{zone}-a{anchor}-s{species}-v{variant}-k{index}"`, the same in every session and process. First-Claim & Image Serials (Alpha) keys claims on this ID; this system never decides claims.
4. **MVP roster.** Five species ship in MVP, spanning C to A; three higher-tier variants exist as data but cannot spawn while `enabled_cap = "A"` (Rule 13). Display names are placeholders pending narrative-director and art-director; IDs are neutral.

   | key | `species_id` (variant) | Kind | Tier | Trait (art bible §3.2: one per archetype) | Schedule mode | Bands | Weathers | Anchors (MVP area) | Exit style |
   |---|---|---|---|---|---|---|---|---|---|
   | 1 | `puffwisp` | Spirit | C | short trailing wisp | PERIODIC | DAWN, DAY, GOLDEN | CLEAR, OVERCAST, FOG | 6 (meadow, woodland edge) | Flee |
   | 2 | `mossmote` | Spirit | C | two ear-like fins; hovers just above moss | PERIODIC | BLUE_AM, BLUE_PM, NIGHT | all | 4 (rocks, woodland floor) | Flee |
   | 3 | `driftfin` | Spirit | B | long tail fin | PERIODIC | BLUE_AM, DAWN, GOLDEN, BLUE_PM | CLEAR, OVERCAST | 3 (pier, harbour wall) | Flee |
   | 4 | `hearth_echo` | Memory | B | an empty frame of faded light around a half-seen scene | PERIODIC | all | FOG, RAIN | 4 (house doorsteps, lighthouse door) | Fade |
   | 5 | `halo_keeper` | Spirit | A | a slow ring orbiting the body | BAND | BLUE_AM, BLUE_PM | CLEAR, OVERCAST, FOG | 1 (lighthouse gallery rail) | Flee |
   | 3/v1 | `driftfin` (gilded) | Spirit | S | as Driftfin + a second orbiting part | EVENT `SUNBEAM` | GOLDEN | OVERCAST | pier | Flee |
   | 6 | `vesper_halo` | Spirit | SS | ring + orbiting part + trailing wisp; own event light | EVENT `LUMEN_DUSK` | BLUE_PM | CLEAR | lighthouse | Flee |
   | 7 | `aurora_drifter` | Spirit | SSS | large, slow, two orbiting parts + long wisp | EVENT `AURORA` | NIGHT | CLEAR | cliff | Flee |

   Coverage check: every band and weather of the MVP day has at least one MVP species (clear days: Puffwisp and Driftfin; blue hours: Driftfin, Mossmote, Halo Keeper; night: Mossmote; fog and rain: Hearth Echo, Mossmote, Puffwisp in fog). The Capture Encounter's set-piece subject is defined in the Capture Encounter GDD and runs on this system's rules (Rule 30).
5. **Tier is fixed per variant, never rolled.** `subject_tier = clamp_to_enabled(TIER[variant])` (Formula F12). Two photos of the same variant always carry the same subject tier. The scarcity of high tiers comes from when and where they appear (short world windows, per the concept: *"Top-tier subjects appear only in short windows (a particular weather, hour or place)"*), not from a hidden roll on the subject.
6. **Gear never gates subjects.** Spawning, visibility through the lens, awareness and poses never read the player's gear, tier or wallet. A phone sees and can photograph a Halo Keeper. Gear acts only as the capture rule's ceiling (Rarity Tier Ladder Core Rule 8). Lens reach still matters in play, because a long lens lets a player frame a shy subject from outside its notice range.

**B. Schedule**

7. **Three schedule modes.**
   - `PERIODIC`: time is cut into cycles of `CYCLE_MS[s]`; each (anchor, cycle) gets one seeded spawn roll and one seeded start offset (F1).
   - `BAND`: one roll per anchor per occurrence of each allowed band (F1, band form).
   - `EVENT`: one appearance per scheduled World light event of the named type, at the variant's anchor, from the event's `BUILDING` start to its `FADING` end, if a seeded roll at `EVENT_SPAWN_BP` passes (F1, event form).
8. **Window predicates.** A species or variant declares a **window predicate**: allowed bands, allowed effective weathers, and optionally a required light event. An appearance is scheduled only if the predicate holds for its **whole** span (F2), using World's `world_state(z, t)` at the start, the last millisecond and every band boundary and effective-weather switch inside the span. A subject never vanishes because the weather turned mid-visit (mirrors World Core Rule 7 for events).
9. **One appearance per anchor at a time; a zone cap.** If two candidate appearances overlap on one anchor, the higher tier wins, then the lower `species_key`. At most `MAX_ACTIVE_PER_ZONE` (default 8, matching Network's bandwidth example of 8 subjects) appearances may overlap in a zone; candidates are admitted in ascending order of start time (ties: higher tier, then lower `species_key`, then lower `anchor_key`) and a candidate that would exceed the cap is dropped (F3). This depends only on the schedule, never on players, so it is identical in every session.
10. **The schedule is global; reactions are per session.** All sessions (solo sessions of capacity 1 in MVP, crews in Alpha) see the same appearances at the same times, because the schedule depends only on the server-secret `world_seed`, the zone and world time. Each session simulates its own **reactions** (awareness, flee, curiosity) for the players in it. Two solo players can each meet the same `appearance_id`; one may startle it in their session while it stays calm in the other's. First-Claim & Image Serials (Alpha) must account for this (Open Question 4).
11. **Seed secrecy.** Clients never receive the seed or a future schedule. The server announces an appearance to clients with an `EVENT subject_spawn` when its `EMERGING` begins (Network message list), and `subject_despawn` when it reaches `GONE`. Players learn habits (bands, weather, places) from play, NPC hints and the Codex (Alpha); exact times are never published ahead.
12. **Versioned, never retroactive.** All subject data (roster, anchors, schedule parameters, awareness and pose parameters, salts) belong to a `subject_rules_version` with an `effective_from_ms`, following World Core Rule 13: a new version is accepted only if `effective_from_ms ≥ now + FORECAST_HORIZON_MS`, and every version stays loadable on the server for audit. An appearance always runs to its end under the version active at its start.
13. **Higher tiers do not spawn above the cap.** A variant whose authored tier is above `enabled_cap` is **not scheduled** (`is_enabled(TIER[variant])` is false), so no S, SS or SSS subject appears in MVP. When `enabled_cap` rises, those variants begin spawning under a new `subject_rules_version`. `clamp_to_enabled` is still applied to every produced subject tier as a safety net (Rarity Tier Ladder Core Rule 7).

**C. Visibility**

14. **Lens-only.** Spirits and memories are rendered **only in the lens world** (the viewfinder view state, art bible A1 and §2.1). In the naked-eye (third-person) view they are not drawn, with one exception: a faint Lumen **shimmer** (a few motes, no silhouette) at the subject's position while it is `EMERGING` or in its `DECISIVE` pose, and while it is within `SHIMMER_RANGE_M` (default 35 m) of the camera (F16). The shimmer is presentation only; it never affects scoring, awareness or the schedule. The server does not know or care which view a player is in for any rule in this system.
15. **Photographable states.** A subject is photographable (present in the capture's subject set and the recipe) in `EMERGING`, `PRESENT` (any awareness), `FLEEING` / `FADING` and `DEPARTING`. It is not photographable in `SCHEDULED`, `HIDDEN` or `GONE`.

**D. Awareness (reactions to presence)**

16. **Presence comes from Movement, reactions live here.** Player Movement computes and publishes each player's presence radius (its F4/F5); this system owns every reaction (Movement D5). On the server, presence is evaluated from the server-accepted player state each tick and converted once, at this system's boundary, to integer centimetres (`presence_cm = floor(presence_m × 100)`). No client-sent presence or awareness is ever read (Network Core Rule 6).
17. **Simulation tick.** Awareness updates run once per server tick (Network `TICK_HZ`, default 30). Each tick has an integer `tick_ms` (Network's `tick_to_ms`, floored). Player positions are taken as the server's accepted positions, converted to integer millimetres.
18. **Intrusion.** For each player, `intrusion_cm = reach_cm − distance_cm`, where `reach_cm` is presence scaled by the species' sensitivity `SENSE_PCT` (F4). A positive value means the player is noticeably close. The subject reacts to the **largest** intrusion among the players in its session (co-op aggregation, D10).
19. **No line of sight.** In MVP, spirits and memories *sense* presence; walls and terrain do not block it, and they do not watch the camera. (Rationale: deterministic, cheap, fits the lore. A line-of-sight test is an Open Question for Alpha.)
20. **Alarm.** Positive intrusion raises an integer alarm meter `A` (0–1000‰) each tick, with an extra **startle** jump the first tick a player's intrusion crosses `STARTLE_CM` (for example arriving at a hurry); no intrusion lowers it by `ALARM_DECAY` per tick (F5).
21. **Curiosity.** If no player intrudes, the alarm is below `CALM_T`, and a player is within `CURIOUS_R_CM`, the curiosity meter `Cu` (0–1000‰) rises; otherwise it falls (F6). Memories (`kind = MEMORY`) have no curiosity.
22. **Awareness states.** `UNAWARE`, `CURIOUS`, `WARY` and the flight transition are derived from the meters with hysteresis (F7). Entering `WARY` resets curiosity to 0. Reaching `A = 1000` starts `FLEEING` (spirits) or `FADING` (memories).
23. **Behaviour per awareness state** (all motion bounded, slow and away-or-toward only, never at speed toward a player):
    - `UNAWARE`: follows its seeded drift path around the anchor (F9); pose cycle runs.
    - `CURIOUS`: turns to face the curious player (16-direction facing, F10) and drifts toward them by up to `CURIOUS_APPROACH_MM`, never closer than `CURIOUS_MIN_GAP_MM` to that player; pose cycle runs; its decisive pose earns `CURIOUS_BONUS` moment points (F13).
    - `WARY`: tucks in (the `TUCKED` pose: shrinks to 85% scale, glow dims to 300‰) and drifts away from the intruding player by up to `WARY_RETREAT_MM`; the pose cycle is **paused**.
    - `FLEEING` (spirit): drifts away and upward along a 16-direction heading away from the intruder for `FLEE_MS`, glow fading to 0 (F8), then `HIDDEN`.
    - `FADING` (memory): stays in place, its glow and scale fold away over `FADE_MS`, then `HIDDEN`.
24. **One return.** A subject that fled or faded returns once: after `RETURN_MS` in `HIDDEN` it re-emerges at its anchor (a new `EMERGING`, alarm and curiosity at 0) if it has a return left (`MAX_RETURNS`, default 1) and at least `MIN_RETURN_LEFT_MS` of its appearance remains; otherwise it goes `GONE`. A second flight always ends the appearance. The schedule of later appearances is never changed by a flight.
25. **Never violent.** No subject state moves a subject toward a player faster than `CURIOUS_SHIFT_MM_PER_S` (default 600 mm/s), no subject collides with players or blocks movement (subjects have no physics collision with players), and no reaction affects a player's position, camera, gear, wallet or inputs.

**E. Poses and the decisive moment**

26. **Pose cycle.** Each species has a cycle `IDLE → ANTICIPATION → DECISIVE → SETTLE → IDLE…` with per-species durations (F11). The anticipation is a readable cue (glow pulse and a small rise, plus an audio cue) of at least `MIN_ANTICIPATION_MS` (default 1000 ms) before every decisive pose, so a skilled player can time it (art bible §5.3). The first cycle after an appearance emerges starts at a seeded offset; after a `WARY` episode ends, the cycle restarts `RECOVER_IDLE_MS` before the next anticipation.
27. **Decisive pose.** During `DECISIVE` the subject "opens fully": fins and ring spread, it rises to its full height, glow goes from 700‰ to 1000‰ at the centre of the window and back. Its closeness to the window centre is `peak_permille` (World F2), which drives the subject moment points (F13).
28. **Pose outputs.** At any millisecond `t` this system can produce a **SubjectSnapshot** for an appearance: `appearance_id`, `species_id`, `variant_key`, `subject_tier`, `lifecycle` state, `awareness`, `pose` (one of `EMERGING`, `IDLE`, `ANTICIPATION`, `DECISIVE`, `SETTLE`, `TUCKED`, `FLEEING`, `FADING`, `DEPARTING`), `pose_phase_permille`, position (integer mm, zone space), `yaw_deci` (0–3599), `scale_permille`, `glow_permille`, `subject_moment_points` and `subject_moment_tier`, and `subject_rules_version`. Secondary motion (fin flutter, wisp sway) is seeded from `appearance_id` and `t` so the re-render matches (art bible P4).

**F. Determinism and the capture**

29. **Determinism contract.** Every output in Rule 28 that a score or tier can depend on is a pure function of:
    - the subject rules version and world rules version (data),
    - the schedule (F1–F3; seed, zone, world time),
    - the appearance's **journal**: the ordered list of tick-stamped reaction transitions the server recorded for it in this session (`AWARE` with new state, target direction and shift magnitude; `RETARGET`; `FLEE`; `HIDE`; `RETURN`; `GONE`; Capture Encounter `ENC_PHASE`), and
    - the query time `t_ms`.
    
    It is computed with 64-bit integers, explicit `floordiv`, World's specified `hash32`, the published 64-entry integer sine table, the 16-direction vector table and `isqrt` (integer floor square root). Engine RNG, Variant `hash()`, floats and trigonometry are forbidden in this path (same rule as World Core Rule 10). The journal itself is produced by the tick loop from integer inputs only (Rules 16–17), so replaying the same per-tick inputs reproduces the same journal bit for bit.
30. **Capture Encounter override.** The Capture Encounter may drive one appearance through scripted phases by writing `ENC_PHASE` journal entries (for example force `CURIOUS`, hold a decisive pose, or end with a calm departure). It uses the same pose and moment formulas, so encounter photos are scored like any other. It can never make a subject threaten or block a player.
31. **Capture time and pose at capture.** The capture instant is Network's lag-compensated tick (Network F8), converted to integer ms exactly as World does (`capture_ms = tick_to_ms(capture_tick)`, World F13). The server evaluates every photographable subject's SubjectSnapshot at `capture_ms` (Rule 28); awareness and lifecycle state are those after the last tick with `tick_ms ≤ capture_ms`; position, facing, glow and pose phase are evaluated at `capture_ms` itself, so a fractional capture tick gives the exactly interpolated pose (Network acceptance criterion 37). Network's history buffer only needs the journal entries and appearance records back to its rewind floor.
32. **What the recipe stores.** At capture, the server writes into the recipe the SubjectSnapshot of every photographable subject in the session's zone (at most `MAX_ACTIVE_PER_ZONE`), plus a `journal_digest` (hash of each appearance's journal up to `capture_ms`). Photo Recipe owns the schema; this system defines the content. Re-scoring and re-rendering read the stored snapshots and never re-simulate. Audit (disputes, First-Claim) may re-derive the snapshots from the retained journal (`JOURNAL_RETENTION_DAYS`) and compare; a mismatch raises a determinism alarm and the stored snapshot is kept (as World's Edge Cases do).

**G. Moment combination**

33. **Bounded moment rule.** The capture rule's **Moment tier** is (F14):
    - with a subject: `moment_tier = tier_max(subject_moment_tier, tier_min(world_moment_tier, tier_step(subject_moment_tier, +WORLD_LIFT_STEPS)))`, default `WORLD_LIFT_STEPS = 1`: catching either instant counts, but the world's instant can lift the moment **at most one step** above the subject's own moment. An idle subject photographed during an aurora is a good moment, not a perfect one; a perfect (SSS) moment needs the decisive pose and the world's peak together, matching the concept's *"SSS subject, perfect moment, perfect light"*. This is the anti-camping guard the World CD review asked for (World D8). **Decided 2026-11-04: the lift applies only in ANTICIPATION or DECISIVE poses.** Without this, at `enabled_cap` A an idle subject under world A would equal a decisive shot and timing would add nothing. An idle subject during an aurora therefore keeps its own moment tier. F14 is authoritative: a subject's own SSS moment needs no world lift.
    - with no subject in the photo: `moment_tier = tier_min(world_moment_tier, NO_SUBJECT_MOMENT_CAP)` (default `"B"`). Whether a subject-less photo can produce an image at all, and at what tier, belongs to Capture Tier Resolution (the subject limit is then `ERR_UNSET` from this system).
    - Which subject is "the" subject of a photo (in frame and recognisable) is chosen by Photo Scoring's Subject part; this system supplies tier and moment for every photographable subject.

**H. Content validation**

34. **Fail fast at load.** A `subject_rules_version` fails to load (and the server does not start with it) if: a variant has no tier or an unknown tier ID; a `species_key` or `variant_key` is reused; a PERIODIC species has `DUR_MS > CYCLE_MS`; a BAND or EVENT appearance cannot fit its band (`DUR_MS > L_band`); any pose duration is ≤ 0 or `ANTICIPATION_MS < MIN_ANTICIPATION_MS`; an anchor lies outside its zone or more than `ANCHOR_MAX_SHOT_M` from the eye volume; a window predicate is impossible in its zone (World `can_occur(z, predicate)` returns false); or the decisive moment points of a variant cannot reach its own tier at peak with curiosity (`DBASE + DSHARP + CURIOUS_BONUS < MOMENT_T[TIER]`), which would make a subject's own top moment unreachable.

**What this system does not own:** the presence radius (Movement); world windows, light tier and world moment (World); the capture rule, odds and near-miss handling (Capture Tier Resolution); the seven-part score, including how Moment and Subject parts are scored (Photo Scoring); the recipe schema (Photo Recipe); transport, ticks, rewind and snapshots (Network); claims and serials (First-Claim); the look, rig and animation of subjects (art bible, technical-artist); sounds (Audio); lore (narrative-director, Subject Codex & Lore).

### States and Transitions

An appearance has a **lifecycle** state; while present it also has an **awareness** state and a **pose** layer. All of them are derived from the schedule and the journal (Rule 29); none is stored outside the journal.

**Lifecycle (per appearance)**

| State | Entered when | Exits when | Photographable |
|---|---|---|---|
| `SCHEDULED` | schedule says the appearance exists (F1–F3) | world time reaches `start` | no |
| `EMERGING` | `t ≥ start` (or a return, Rule 24) | `EMERGE_MS` (default 3,000 ms) elapsed → `PRESENT` | yes |
| `PRESENT` | emergence complete | `t ≥ end − DEPART_MS` → `DEPARTING`; `A = 1000` → `FLEEING` / `FADING` | yes |
| `DEPARTING` | `DEPART_MS` (default 4,000 ms) before `end` | `t ≥ end` → `GONE` | yes |
| `FLEEING` (spirit) / `FADING` (memory) | alarm reaches 1000 while `EMERGING` or `PRESENT` | `FLEE_MS` / `FADE_MS` elapsed → `HIDDEN` | yes |
| `HIDDEN` | flight finished | after `RETURN_MS`: return allowed (Rule 24) → `EMERGING`; else → `GONE` | no |
| `GONE` | end reached, or no return left | — (despawn event sent) | no |

A flight that would still be running at `end` is cut short: the appearance goes `GONE` at `end`. During `DEPARTING` the alarm is not updated and no flight can start (it is already leaving calmly).

**Awareness (while `EMERGING` or `PRESENT`)**

| From | To | Condition (evaluated each tick, in this order) |
|---|---|---|
| any | flight | `A = 1000` |
| `UNAWARE` / `CURIOUS` | `WARY` | `A ≥ WARY_T` (default 400); `Cu` reset to 0 |
| `WARY` | `UNAWARE` | `A < CALM_T` (default 200) |
| `UNAWARE` | `CURIOUS` | species can be curious, `A < CALM_T`, `Cu ≥ CURIOUS_ON` (default 700) |
| `CURIOUS` | `UNAWARE` | `Cu < CURIOUS_OFF` (default 300) |

Each change writes an `AWARE` journal entry with the tick, the new state, the 16-direction heading toward (curious) or away from (wary) the relevant player, and the shift magnitude (F9). While `CURIOUS`, a `RETARGET` entry is written when the curious player's 16-direction heading changes, at most once per `RETARGET_MIN_MS` (default 500 ms), so facing follows a moving player without depending on continuous input.

**Pose layer**

| Pose | When | Glow (‰) | Notes |
|---|---|---|---|
| `EMERGING` | lifecycle `EMERGING` | 0 → 400 linearly | naked-eye shimmer visible |
| `IDLE` | cycle position in idle | 400 | tucked shape, slow drift |
| `ANTICIPATION` | cycle position in anticipation | 400 → 700, one visible pulse | rise of 100 mm, audio cue |
| `DECISIVE` | cycle position in decisive | 700 + 300 × peak / 1000 | opens fully; naked-eye shimmer visible |
| `SETTLE` | cycle position in settle | 700 → 400 | folds back |
| `TUCKED` | awareness `WARY` | 300 | scale 850‰; cycle paused |
| `FLEEING` / `FADING` | lifecycle flight | 1000 × (1 − elapsed / duration) | F8 |
| `DEPARTING` | lifecycle `DEPARTING` | 400 → 0 | rises 1 m, calm |

### Interactions with Other Systems

| System | Direction | What flows | Owner of the rule |
|---|---|---|---|
| Rarity Tier Ladder | Ladder → this | tier IDs, `parse`, `clamp_to_enabled`, `is_enabled`, `tier_min`, `tier_max`, `tier_step`, display tokens for the badge | Ladder owns operations; this system owns subject tier values |
| World Time, Weather & Light | World → this | `world_state(z, t)` (band, effective weather, event phase), `world_moment_tier`, `find_next_window`, `can_occur`, `hash32`, `peak_permille`, `points_to_tier`, `MOMENT_T`; the event schedule (for EVENT species) | World owns windows and the world moment; this system owns the subject moment and the combination (World Core Rule 8, D7) |
| Player Movement & Exploration | Movement → this | presence radius and presence events (server-evaluated from accepted state), player position | Movement computes presence; this system owns all reactions (Movement R9, D5) |
| Network Transport & Server Authority | both | this → Network: subject state for `SNAPSHOT`, `EVENT subject_spawn/despawn`, journal for the history buffer; Network → this: server tick, `tick_to_ms`, `capture_tick`, accepted player positions | Network owns transport, ticks and rewind; subjects simulated on the server only (Network Interactions table) |
| Photo Recipe & Re-render | this → Recipe | SubjectSnapshots and `journal_digest` at `capture_ms`; `subject_rules_version` | Recipe owns schema; this system owns content and meanings |
| Photo Scoring | this → Scoring | subject position, facing, scale, pose, bounds radius (`BOUNDS_MM` per species), `subject_moment_points`, subject tier (for the Rarity part, per the systems index circular-dependency resolution) | Scoring owns every score part and picks the primary subject |
| Capture Tier Resolution | this → Resolution | `subject_tier` and the combined `moment_tier` (Rule 33) for the primary subject | Resolution owns the capture rule, odds and near-miss handling |
| Capture Encounter | Encounter → this | `ENC_PHASE` journal commands for its scripted appearance | Encounter owns its script; this system owns the rules it runs on |
| Camera Model | Camera → Movement → this | shutter presence event (through Movement's presence channel) | Camera owns its magnitude; this system only reacts to presence |
| Viewfinder HUD | this → HUD | subject tier badge data for framed subjects; nearest subject's awareness band for Movement's presence glyph | HUD owns layout |
| Zone Access & Travel (VS) | Zone → this | zones and their anchors; which zone a session simulates | Zone |
| Audio: SFX & Ambience (VS) | this → Audio | emergence, anticipation, decisive, wary, flee/fade, return, departure events with position | Audio owns sounds |
| First-Claim & Image Serials (Alpha) | this → First-Claim | `appearance_id`, subject tier, lifecycle; captures ordered by Network F8 | First-Claim owns claims |
| Co-op Crew Roles (Alpha) | Roles → this | hooks: per-player `SENSE_PCT` and `CURIOUS_GAIN` multipliers (e.g. Portrait coaxes, Wildlife lures) | Roles own the role rules; multipliers are data here |
| Subject Codex & Lore (Alpha) | this → Codex | species data (habits, windows, tier) | Codex owns presentation and lore |
| Server-Wide Events & Timed Races (Full Vision) | Events → this | operator-scheduled EVENT appearances (rows in a subject rules version) | Events |
| Economy Telemetry (Alpha) | this → Telemetry | appearances per species, flights, returns, decisive-pose capture rate | Telemetry |

## Formulas

Notation follows World Time, Weather & Light: 64-bit integers, `floordiv` rounds toward negative infinity, `mod` is non-negative, ‰ is per mille, bp is basis points (0–10,000), `hash32` is World's specified hash. Positions are in integer millimetres in zone space (x, z horizontal, y up). Tables of default values per species are in Tuning Knobs.

### F1. Appearance schedule

The appearance_schedule formula is defined as:

`k = floordiv(t_z, CYCLE_MS[s]);  rolled(s, a, k) = mod(hash32(world_seed, z, a, s, k, SALT_SPAWN), 10000) < SPAWN_BP[s];  start(s, a, k) = k × CYCLE_MS[s] + mod(hash32(world_seed, z, a, s, k, SALT_SPAWN_T), CYCLE_MS[s] − DUR_MS[s] + 1);  end = start + DUR_MS[s];  scheduled = rolled ∧ window_holds(s, z, start, end) (F2) ∧ admitted(F3) ∧ is_enabled(TIER[s])`

Band form (`BAND` mode): `k` is the band-occurrence index `day_index × 6 + band_ordinal` for each allowed band; `start = BAND_START_ABS(k) + mod(hash32(…, SALT_SPAWN_T), L_band − DUR_MS[s] + 1)`. Event form (`EVENT` mode): for each World event of the required type scheduled in zone `z` on day `d`, `rolled = mod(hash32(world_seed, z, a, s, d, SALT_SPAWN), 10000) < EVENT_SPAWN_BP[s]`, `start = build_start`, `end = build_start + build_ms + active_ms + fade_ms` (World F8).

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t_z | int (ms) | ≥ 0 | calculated (World F1, zone world time) | World time in the zone's frame |
| s | int | permanent `species_key` × 16 + `variant_key` | data file (roster) | Variant being scheduled |
| a | int | valid `anchor_key` hosting s | data file (zone anchors) | Anchor |
| z | int | valid zone ID | data file | Zone |
| world_seed | int (32-bit) | server-secret | data file (World, per rules version) | Shared schedule seed; distinct salts keep subject draws independent of weather |
| SALT_SPAWN, SALT_SPAWN_T | int constants | distinct from every World salt | data file | Draw separators |
| CYCLE_MS[s] | int (ms) | 60,000–1,260,000 | data file | PERIODIC cycle length |
| DUR_MS[s] | int (ms) | 30,000 to CYCLE_MS (or band length) | data file | Appearance length |
| SPAWN_BP[s], EVENT_SPAWN_BP[s] | int (bp) | 0–10,000 | data file | Chance per anchor per cycle / band occurrence / event |
| TIER[s] | tier ID | C–SSS | data file | Authored tier of the variant |
| k | int | ≥ 0 | calculated | Schedule index (part of `appearance_id`) |
| start, end | int (ms, zone world time) | inside cycle k (or the band / event) | calculated | Appearance span, half-open `[start, end)` |
| scheduled | bool | — | calculated | Whether the appearance exists |

**Output Range:** at most one candidate per (variant, anchor, cycle); `start + DUR_MS ≤ (k + 1) × CYCLE_MS`, so a PERIODIC appearance never spills into the next cycle. A variant above `enabled_cap` is never scheduled.
**Example:** Puffwisp (`s` = 16, base variant), zone 0, anchor 3, `CYCLE_MS` 180,000, `DUR_MS` 120,000, `SPAWN_BP` 7,000. At `t_z` = 100,580,000: `k` = floordiv(100,580,000, 180,000) = 558 (558 × 180,000 = 100,440,000). Suppose the roll is 4,120 < 7,000 → rolled. The offset is `mod(h, 60,001)` = 23,456 (illustrative), so `start` = 100,463,456 and `end` = 100,583,456. In day 26 (starts at 98,280,000) these are phases 2,183,456 and 2,303,456, both in GOLDEN, inside weather slot 3, which is CLEAR (World F3 example) → the window holds (F2) and the appearance `z0-a3-s1-v0-k558` exists until 100,583,456.

### F2. Window holds

The window_holds formula is defined as:

`window_holds(s, z, start, end) = ∀ t ∈ CHECK(start, end): band(z, t) ∈ BANDS[s] ∧ weather_eff(z, t) ∈ WEATHERS[s] ∧ (EVENT_REQ[s] = NONE ∨ event(z, t) = EVENT_REQ[s])`, where `CHECK = {start, end − 1} ∪ {each band start in (start, end)} ∪ {each slot_start + TRANSITION_MS / 2 in (start, end)}`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| BANDS[s] | set of bands | non-empty subset of the 6 bands | data file | Allowed time-of-day bands |
| WEATHERS[s] | set of weathers | non-empty subset of the 4 weathers | data file | Allowed effective weathers |
| EVENT_REQ[s] | event ID or NONE | World event IDs | data file | Required light event (EVENT species) |
| band, weather_eff, event | enums | World values | calculated (World `world_state`, F1, F4, F9) | World state at time t |
| TRANSITION_MS | int (ms) | World default 60,000 | data file (World) | The effective weather switches at its midpoint (World F4) |
| CHECK | set of times | 2 to about 10 points | calculated | The only instants at which band or effective weather can change |

**Output Range:** boolean. Because band and effective weather change only at the instants in `CHECK`, checking those points is exact, not sampled.
**Example:** a Driftfin candidate spans phases 2,480,000–2,600,000 (BLUE_PM). The slot boundary at phase 2,520,000 puts an effective-weather switch at 2,550,000. If slot 4 is RAIN, `weather_eff` at 2,550,000 is RAIN ∉ {CLEAR, OVERCAST}, so `window_holds` = false and the Driftfin does not come that cycle.

### F3. Anchor and zone admission

The admitted formula is defined as:

`admitted(c) = (no admitted candidate on anchor(c) overlaps c with higher priority) ∧ (|{admitted d : d overlaps start(c)}| < MAX_ACTIVE_PER_ZONE)`, evaluating candidates in ascending `(start, −rank(TIER), species_key, anchor_key)` order over the lookback `[start(c) − MAX_DUR_MS, start(c)]`; `priority = (rank(TIER), −species_key)`, higher first

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| c, d | appearance candidates | rolled and window-valid (F1, F2) | calculated | Candidates in the zone |
| MAX_ACTIVE_PER_ZONE | int | 4–12 | data file (default 8) | Simultaneous appearances in a zone |
| MAX_DUR_MS | int (ms) | max of `DUR_MS` over the roster | calculated at load | Lookback that bounds the evaluation |
| rank | int | 1–6 | Rarity Tier Ladder (`rank`, derived) | Used for ordering only, never stored |

**Output Range:** boolean; the result depends only on the schedule, so every session agrees. Evaluation cost is bounded by the candidates in one `MAX_DUR_MS` lookback.
**Example:** the pier anchor hosts Driftfin (B) and Puffwisp (C). Both roll candidates overlapping 100,500,000–100,560,000. Driftfin has the higher rank, so it is admitted; the Puffwisp candidate on that anchor is dropped. Elsewhere, 8 appearances are already active when a ninth Mossmote candidate starts; it is dropped.

### F4. Distance and intrusion

The intrusion formula is defined as:

`d_cm = floordiv(isqrt(dx² + dy² + dz²), 10);  reach_cm = floordiv(presence_cm × SENSE_PCT[s] × ROLE_SENSE_PCT[p], 10000);  intrusion_cm(p) = reach_cm − d_cm;  I = max over players p in the session of intrusion_cm(p)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| dx, dy, dz | int (mm) | zone extent | calculated (server-accepted player position − subject position at the tick) | Offset from subject to player body centre |
| isqrt | function | — | calculated (integer floor square root) | Deterministic square root |
| presence_cm | int (cm) | 0–2,500 | Player Movement F5 evaluated on the server, floored to cm (Rule 16) | Player's presence radius |
| SENSE_PCT[s] | int (%) | 50–250 | data file | How sensitive the species is |
| ROLE_SENSE_PCT[p] | int (%) | 50–150; MVP 100 | data file (Co-op Crew Roles hook) | Per-player multiplier |
| d_cm | int (cm) | ≥ 0 | calculated | 3D distance |
| intrusion_cm, I | int (cm) | negative to 6,250 | calculated | How far inside the notice range a player is |

**Output Range:** `I` > 0 means at least one player is inside the subject's notice range. With no players in the session, `I` is defined as −1 (no intrusion).
**Example:** Halo Keeper (`SENSE_PCT` 180), a player walking on cobble (presence 6.5 m → 650 cm) at offset (8,000, 3,000, 4,000) mm: `isqrt(89,000,000)` = 9,433 → `d_cm` = 943; `reach_cm` = floordiv(650 × 180 × 100, 10,000) = 1,170; intrusion = **227 cm**. Sneaking on grass (presence 1.96 m → 196 cm): reach 352, intrusion −591, unnoticed.

### F5. Alarm meter

The alarm formula is defined as:

`A' = min(1000, A + floordiv(I × ALARM_GAIN[s], 100) + (startle ? STARTLE_JUMP : 0))` if `I > 0`;  `A' = max(0, A − ALARM_DECAY[s])` otherwise;  `startle` = true on the first tick where some player's `intrusion_cm ≥ STARTLE_CM[s]` after a tick where it was below

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| A, A' | int (‰) | 0–1000 | calculated (previous tick) | Alarm before and after this tick |
| I | int (cm) | see F4 | calculated (F4) | Largest intrusion |
| ALARM_GAIN[s] | int (‰ per metre per tick) | 1–10 | data file | How fast intrusion alarms the subject |
| ALARM_DECAY[s] | int (‰ per tick) | 2–30 | data file | How fast it calms down |
| STARTLE_CM[s] | int (cm) | 200–1,000 | data file | Intrusion that counts as a sudden arrival |
| STARTLE_JUMP | int (‰) | 0–600 | data file (default 400) | Extra alarm on a startle |

**Output Range:** 0–1000; reaching 1000 starts a flight (F7). Alarm is not updated during `DEPARTING`, `FLEEING`, `FADING` or `HIDDEN`.
**Example:** the walking player above (`I` = 227) and Halo Keeper (`ALARM_GAIN` 5): +floordiv(227 × 5, 100) = +11 per tick. From 0 it reaches `WARY_T` 400 after 37 ticks (1.23 s at 30 Hz) and 1000 after 91 ticks (3.03 s): the player has over a second of visible warning (the subject tucks in) to stop or back off. A player hurrying on the pier (12.35 m → `reach` 2,223, `I` = 1,280 ≥ 600): startle +400 plus +64 → `A` = 464, wary at once; flight after 9 more ticks.

### F6. Curiosity meter

The curiosity formula is defined as:

`Cu' = min(1000, Cu + floordiv(CURIOUS_GAIN[s] × ROLE_CURIOUS_PCT[c], 100))` if `CURIOUS_OK[s] ∧ I ≤ 0 ∧ A < CALM_T ∧ ∃ c: d_cm(c) ≤ CURIOUS_R_CM[s]`;  `Cu' = max(0, Cu − CURIOUS_DECAY)` otherwise;  `Cu' = 0` on entering `WARY`. The curious target `c` is the nearest qualifying player (ties: lowest session slot).

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| Cu, Cu' | int (‰) | 0–1000 | calculated | Curiosity before and after the tick |
| CURIOUS_OK[s] | bool | — | data file (false for memories) | Species can become curious |
| CURIOUS_GAIN[s] | int (‰ per tick) | 0–40 | data file | Curiosity growth while a quiet player is near |
| ROLE_CURIOUS_PCT[c] | int (%) | 50–200; MVP 100 | data file (Co-op Crew Roles hook) | Per-player multiplier (Portrait "coaxes") |
| CURIOUS_DECAY | int (‰ per tick) | 5–50 | data file (default 20) | Loss when no quiet player is near |
| CURIOUS_R_CM[s] | int (cm) | 200–1,500 | data file | How close a quiet player must be |
| CALM_T | int (‰) | 100–300 | data file (default 200) | Alarm below which the subject is calm |

**Output Range:** 0–1000.
**Example:** a player sneaks to 3 m from a Puffwisp on grass and stops (presence 0.4 m → reach 40 cm, `I` = −260). `d` = 300 ≤ 500, so `Cu` rises by 12 per tick and passes `CURIOUS_ON` 700 after 59 ticks (1.97 s): the Puffwisp turns to face the player.

### F7. Awareness state

The awareness_state formula is defined as:

`awareness' = FLIGHT if A' = 1000;  WARY if A' ≥ WARY_T ∨ (awareness = WARY ∧ A' ≥ CALM_T);  CURIOUS if CURIOUS_OK ∧ A' < CALM_T ∧ (Cu' ≥ CURIOUS_ON ∨ (awareness = CURIOUS ∧ Cu' ≥ CURIOUS_OFF));  UNAWARE otherwise` (an `UNAWARE` or `CURIOUS` subject whose alarm is between `CALM_T` and `WARY_T` keeps its state, except that `CURIOUS` drops to `UNAWARE` when `A' ≥ CALM_T`)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| A', Cu' | int (‰) | 0–1000 | calculated (F5, F6) | Meters after this tick |
| awareness | enum | UNAWARE, CURIOUS, WARY | calculated (previous tick) | Current state |
| WARY_T | int (‰) | 250–700 | data file (default 400) | Alarm that makes the subject wary |
| CURIOUS_ON, CURIOUS_OFF | int (‰) | 500–900 / 100–500 | data file (default 700 / 300) | Curiosity hysteresis |
| FLIGHT | — | — | — | Lifecycle → `FLEEING` (spirit) or `FADING` (memory) |

**Output Range:** one state per tick; hysteresis gaps (`WARY_T − CALM_T` = 200‰; `CURIOUS_ON − CURIOUS_OFF` = 400‰) prevent flicker. A load check requires `CALM_T < WARY_T < 1000` and `CURIOUS_OFF < CURIOUS_ON`.
**Example:** the Halo Keeper reaches `A` = 407 → `WARY`. The player stops; decay 6 per tick brings it below 200 after 35 ticks (1.17 s) → `UNAWARE`, and the pose cycle restarts (F11).

### F8. Flight (flee or fade) and return

The flight formula is defined as:

`e = t − flee_start;  offset_mm = DIR16[h] × floordiv(FLEE_SPEED_MM_S × e, 1000) / 1000 (horizontal) + (0, floordiv(FLEE_RISE_MM_S × e, 1000), 0);  glow_permille = 1000 − floordiv(1000 × e, FLEE_MS)` for spirits (for memories: no offset, `glow_permille` and `scale_permille` both `1000 − floordiv(1000 × e, FADE_MS)`);  `returns = returns_used < MAX_RETURNS ∧ end − (flee_start + FLEE_MS + RETURN_MS) ≥ MIN_RETURN_LEFT_MS`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| flee_start | int (ms) | — | journal (`FLEE` entry tick_ms) | When the flight began |
| h | int | 0–15 | journal (`FLEE` entry; F10 `dir16` of subject − intruder) | Heading away from the player with the largest intrusion |
| DIR16 | table of 16 (x, z) pairs ×1000 | — | data file | Unit vectors at 22.5° steps |
| FLEE_SPEED_MM_S, FLEE_RISE_MM_S | int (mm/s) | 1,000–4,000 / 200–1,200 | data file (default 2,500 / 600) | Drift-away speed |
| FLEE_MS, FADE_MS | int (ms) | 1,000–5,000 | data file (default 2,500 / 3,000) | Flight duration |
| RETURN_MS | int (ms) | 5,000–60,000 | data file (default 20,000) | Time hidden before a return |
| MAX_RETURNS | int | 0–2 | data file (default 1) | Returns per appearance |
| MIN_RETURN_LEFT_MS | int (ms) | 10,000–60,000 | data file (default 30,000) | Appearance time that must remain to return |

**Output Range:** `glow_permille` 1000 → 0 over the flight; the spirit ends at most 6.25 m away and 1.5 m higher with defaults; the subject is `HIDDEN` afterwards.
**Example:** a Halo Keeper appearance runs `start` to `start + 100,000`. It flees at `start + 40,000` with heading 9. At `e` = 1,000 ms it is 2,500 mm along heading 9 and 600 mm higher, glow 600‰. Hidden from `start + 42,500`; return check: 100,000 − (40,000 + 2,500 + 20,000) = 37,500 ≥ 30,000 → it re-emerges at `start + 62,500` with `returns_used` = 1. If startled again, it goes `GONE`.

### F9. Drift path and reaction shift (position)

The subject_position formula is defined as:

`u = mod(t − start + DRIFT_OFF, DRIFT_LOOP_MS);  j = floordiv(u × K, DRIFT_LOOP_MS);  r = u × K − j × DRIFT_LOOP_MS;  base = ANCHOR + W[j] + floordiv((W[j+1 mod K] − W[j]) × r, DRIFT_LOOP_MS);  bob_y = floordiv(BOB_AMP_MM × SIN64[floordiv(mod(t − start, BOB_MS) × 64, BOB_MS)], 1000);  shift = DIR16[h] × floordiv(M × min(t − t_shift, SHIFT_MS), SHIFT_MS) / 1000;  pos = base + (0, bob_y, 0) + shift (+ F8 offset while fleeing)`, with `W[i] = (mod(hash32(world_seed, appearance, i, SALT_DRIFT_X), 2R + 1) − R, mod(hash32(…, SALT_DRIFT_Y), R_Y + 1), mod(hash32(…, SALT_DRIFT_Z), 2R + 1) − R)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| ANCHOR | int (mm) ×3 | zone space | data file (anchor) | Anchor position |
| R, R_Y | int (mm) | 0–3,000 / 0–1,000 | data file (`drift_radius_mm`, species height range) | Drift box half-size |
| K | int | 4 | data file | Waypoints in the seeded loop |
| DRIFT_LOOP_MS | int (ms) | 8,000–40,000 | data file | Time for one loop |
| DRIFT_OFF | int (ms) | 0 to DRIFT_LOOP_MS − 1 | calculated (seeded per appearance) | Start point on the loop |
| BOB_AMP_MM, BOB_MS | int | 0–300 mm / 1,500–6,000 ms | data file | Gentle float bob |
| SIN64 | table of 64 ints | −1000 to 1000 | data file (published values of round(1000·sin(2πi/64))) | Integer sine table; no runtime trig |
| h, M, t_shift | int | 0–15; 0–`CURIOUS_APPROACH_MM` or `WARY_RETREAT_MM`; ms | journal (latest `AWARE` / `RETARGET` entry) | Shift direction, size and start; when the state returns to `UNAWARE`, a new entry shifts back to 0 over `SHIFT_MS` |
| SHIFT_MS | int (ms) | 500–3,000 | data file (default 1,000) | How long a reaction shift takes |
| pos | int (mm) ×3 | anchor ± drift box ± shift | calculated | Subject position at t |

**Output Range:** the subject stays within `R` + max shift of its anchor horizontally until a flight. A curious approach magnitude is set at the transition to `min(CURIOUS_APPROACH_MM, max(0, d_mm − CURIOUS_MIN_GAP_MM))`, so the subject never comes closer than `CURIOUS_MIN_GAP_MM` (default 1,500 mm) to the curious player at that moment, and it moves at most `CURIOUS_APPROACH_MM / SHIFT_MS` (600 mm/s with defaults; Rule 25).
**Example:** `u` = 6,500, `K` = 4, loop 16,000: `j` = floordiv(26,000, 16,000) = 1; `r` = 10,000; with `W[1].x` = 400 and `W[2].x` = −800: x = 400 + floordiv(−1,200 × 10,000, 16,000) = 400 − 750 = **−350 mm** from the anchor. Bob: `BOB_MS` 3,000, `mod(6,500, 3,000)` = 500 → index floordiv(32,000, 3,000) = 10 → `SIN64[10]` = 831 → `bob_y` = floordiv(120 × 831, 1,000) = **99 mm**.

### F10. Sixteen-direction heading and facing

The dir16 formula is defined as:

`dir16(dx, dz) = argmax over i ∈ 0..15 of (dx × DIR16[i].x + dz × DIR16[i].z)` (ties: lowest i; `dx = dz = 0` returns the subject's current heading);  `yaw_deci(t) = yaw0 + floordiv(delta × min(t − t_turn, TURN_MS), TURN_MS)`, where `delta` is the shortest signed turn from `yaw0` to `h × 225` decidegrees, wrapped with `mod(·, 3600)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| dx, dz | int (mm) | zone extent | calculated (target − subject, horizontal) | Direction to face or move along |
| DIR16[i] | (int, int) ×1000 | i × 22.5° | data file | Direction table (index 0 = +x, counter-clockwise) |
| h | int | 0–15 | calculated | Heading index |
| yaw0, t_turn | int (decideg), int (ms) | 0–3599 | journal (facing at the last `AWARE` / `RETARGET`) | Turn start |
| TURN_MS | int (ms) | 300–2,000 | data file (default 800) | Turn duration |
| yaw_deci | int (0.1°) | 0–3599 | calculated | Facing at t |

**Output Range:** heading 0–15; yaw always wrapped to [0, 3600). Uncurious subjects face along their drift direction (`dir16` of `W[j+1] − W[j]`).
**Example:** the away vector from an intruder is (−8,000, −4,000). Dot products: i = 8 (−1000, 0) → 8,000,000; i = 9 (−924, −383) → 8,924,000; i = 10 (−707, −707) → 8,484,000. Result **9** (202.5°), the nearest of the 16 directions to the true 206.6°.

### F11. Pose cycle timing

The pose_cycle formula is defined as:

`P = IDLE_MS + ANT_MS + DEC_MS + SET_MS;  c = mod(t − calm_start + c0, P);  pose = IDLE if c < IDLE_MS; ANTICIPATION if c < IDLE_MS + ANT_MS; DECISIVE if c < IDLE_MS + ANT_MS + DEC_MS; SETTLE otherwise;  o = c − IDLE_MS − ANT_MS;  dec_peak = peak_permille(o, DEC_MS)` (World F2), where `calm_start` is the end of the latest `EMERGING` or the latest `WARY → UNAWARE` transition, and `c0 = mod(hash32(world_seed, appearance, SALT_POSE), P)` for the first calm period of an appearance, else `c0 = IDLE_MS − RECOVER_IDLE_MS`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| IDLE_MS, ANT_MS, DEC_MS, SET_MS | int (ms) | 2,000–20,000 / ≥ 1,000 / 800–3,000 / 500–3,000 | data file (per species) | Pose durations |
| calm_start | int (ms) | — | journal / lifecycle | Start of the current calm period |
| c0 | int (ms) | 0 to P − 1 | calculated | Cycle start offset |
| RECOVER_IDLE_MS | int (ms) | 1,000 to IDLE_MS | data file (default 4,000) | After a wary episode, time until the next anticipation |
| c | int (ms) | 0 to P − 1 | calculated | Position in the cycle |
| dec_peak | int (‰) | 0–1000 | calculated | Closeness to the decisive centre |

**Output Range:** the cycle only runs while `UNAWARE` or `CURIOUS` (and in `PRESENT` / `EMERGING`); `WARY` overrides the pose with `TUCKED`. The decisive pose occupies `DEC_MS / P` of calm time (Puffwisp 18%, Halo Keeper 6.7%).
**Example:** Halo Keeper, `P` = 14,000 + 1,000 + 1,200 + 1,800 = 18,000. Emergence ends at `start + 3,000`; seeded `c0` = 11,000. At `t = start + 6,600`: `c` = mod(3,600 + 11,000, 18,000) = 14,600 → **ANTICIPATION**. At `t = start + 7,400`: `c` = 15,400 → **DECISIVE**, `o` = 400, `dec_peak` = 1000 − floordiv(1000 × |800 − 1,200|, 1,200) = 1000 − 333 = **667**.

### F12. Subject tier

The subject_tier formula is defined as:

`spawnable(v) = is_enabled(TIER[v]);  subject_tier(appearance) = clamp_to_enabled(TIER[variant(appearance)])`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| TIER[v] | tier ID | C–SSS | data file (roster) | Authored tier of the variant |
| enabled_cap | tier ID | MVP "A" | data file (Rarity Tier Ladder config) | Highest producible tier |
| subject_tier | tier ID | C to `enabled_cap` | calculated | The capture rule's Subject tier |

**Output Range:** C to `enabled_cap`. Fixed for the whole appearance; never rolled; unaffected by awareness, pose or gear.
**Example:** Halo Keeper: `TIER` = A, cap A → `spawnable` true, `subject_tier` = **A**. Aurora Drifter: `TIER` = SSS → `spawnable` false, so it never appears in MVP. If a test or an encounter forced one, `clamp_to_enabled("SSS")` = **A**, and no message mentions SSS (Rarity Tier Ladder Edge Cases).

### F13. Subject moment points and tier

The subject_moment formula is defined as:

`SMP = DBASE[s] + floordiv(DSHARP[s] × dec_peak, 1000) + (awareness = CURIOUS ? CURIOUS_BONUS : 0)` when `pose = DECISIVE`;  `SMP = ANTIC_PTS` (ANTICIPATION);  `SMP = IDLE_PTS` (IDLE, SETTLE, EMERGING, DEPARTING);  `SMP = WARY_PTS` (TUCKED);  `SMP = FLIGHT_PTS` (FLEEING, FADING);  `SMP = clamp(SMP, 0, 100);  subject_moment_tier = clamp_to_enabled(points_to_tier(SMP, MOMENT_T))`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| DBASE[s], DSHARP[s] | int | 30–70 / 10–35 | data file (per variant) | Decisive points at the window edge, and the bonus at its centre |
| dec_peak | int (‰) | 0–1000 | calculated (F11) | Closeness to the decisive centre |
| CURIOUS_BONUS | int | 0–20 | data file (default 10) | Reward for earning the subject's trust |
| ANTIC_PTS, IDLE_PTS, WARY_PTS, FLIGHT_PTS | int | 0–50 | data file (default 40 / 30 / 15 / 0) | Points outside the decisive pose |
| MOMENT_T | threshold table | C 0, B 30, A 55, S 75, SS 88, SSS 96 | data file (World F6, shared) | Moment thresholds (same table as the world moment, so the two are comparable) |
| SMP | int | 0–100 | calculated | Subject moment points (Photo Scoring may read them) |
| subject_moment_tier | tier ID | C to `enabled_cap` | calculated | The subject part of Moment |

**Output Range:** 0–100 points; tier C to `enabled_cap`. Defaults: a calm subject is B (30), its anticipation B (40), a wary one C (15), a fleeing one C (0). The decisive pose of every MVP species reaches A; the load check (Rule 34) guarantees every variant can reach its own tier at peak with curiosity.
**Example:** Halo Keeper (`DBASE` 55, `DSHARP` 30) at `dec_peak` 667, curious: 55 + floordiv(30 × 667, 1000) + 10 = 55 + 20 + 10 = **85** → S → cap A → **A**. The same instant, uncurious: 75 → S → A. A Puffwisp (45 / 20) idle: 30 → **B**; decisive at `dec_peak` 400, unaware: 45 + 8 = 53 → **B** (the edge of the window is not yet the moment); at `dec_peak` 500: 55 → **A**.

### F14. Moment combination (world + subject)

The moment_combination formula is defined as:

`moment_tier = tier_max(subject_moment_tier, tier_min(world_moment_tier, tier_step(subject_moment_tier, +WORLD_LIFT_STEPS)))` when a subject is in the photo **and its pose is ANTICIPATION or DECISIVE**; `moment_tier = subject_moment_tier` when a subject is in the photo in any other pose;  `moment_tier = tier_min(world_moment_tier, NO_SUBJECT_MOMENT_CAP)` otherwise

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| subject_moment_tier | tier ID | C to cap | calculated (F13, primary subject chosen by Photo Scoring) | Subject's instant |
| world_moment_tier | tier ID | C to cap | World F10 | World's instant (band, weather, clearing, event) |
| WORLD_LIFT_STEPS | int | 0–2 | data file (default 1) | How many steps the world may lift the moment above the subject's own |
| NO_SUBJECT_MOMENT_CAP | tier ID | C–A | data file (default "B") | Moment ceiling for a photo with no subject |
| moment_tier | tier ID | C to cap | calculated | The capture rule's Moment tier |

**Output Range:** always between `subject_moment_tier` and `tier_step(subject_moment_tier, +WORLD_LIFT_STEPS)` when a subject is present, and never above `world_moment_tier` unless the subject's own moment is higher. All inputs are already clamped, so the output is ≤ `enabled_cap`. Setting `WORLD_LIFT_STEPS = 5` reproduces plain `tier_max` (World D8 option a); `0` makes the moment subject-only.
**Example (uncapped tiers, to show the shape):**
- Camping an aurora with an idle subject: subject B, world SS → `tier_step(B, +1)` = A; `tier_min(SS, A)` = A; `tier_max(B, A)` = **A** (plain `tier_max` would have given SS).
- Decisive pose at its peak during the aurora: subject S, world SSS → step = SS; min = SS; max(S, SS) = **SS**. A perfect **SSS** moment needs subject ≥ SS with world SSS, or a subject SSS.
- Decisive at noon: subject A, world C → min(C, S) = C; max(A, C) = **A** (the subject alone carries the moment).
- MVP (cap A): the same rule; nothing above A is produced.

### F15. Expected appearances (balance model)

The expected_appearances formula is defined as:

`E_hour(s) = (3,600,000 / CYCLE_MS[s]) × N_ANCHORS[s] × SPAWN_BP[s] / 10,000 × P_fit(s)` (PERIODIC);  `E_hour(s) = (N_BANDS[s] × N_ANCHORS[s] × SPAWN_BP[s] / 10,000 × P_fit(s)) × 3,600,000 / DAY_MS` (BAND);  `concurrency(s) ≈ E_hour(s) × DUR_MS[s] / 3,600,000`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| N_ANCHORS[s] | int | 1–12 | data file | Anchors hosting s in the zone |
| N_BANDS[s] | int | 1–6 | data file | Allowed bands (BAND mode) |
| P_fit(s) | fraction | 0–1 | estimated (simulation; F2 rejects spans crossing a band edge or a weather switch) | Share of rolled candidates whose window holds |
| DAY_MS | int (ms) | 3,780,000 | data file (World) | World day |
| E_hour, concurrency | float (analysis only, never in the game path) | ≥ 0 | calculated | Appearances per real hour; average number present at once |

**Output Range:** analysis values for tuning, not runtime values. Estimates with defaults (P_fit approximate, to be confirmed by the simulation criterion 31):

| Species | P_fit (approx.) | E_hour | Concurrency | Reading |
|---|---|---|---|---|
| Puffwisp | 0.45 | 20 × 6 × 0.70 × 0.45 ≈ 37.8 | ≈ 1.3 | almost always one nearby in daylight |
| Mossmote | 0.33 | 15 × 4 × 0.60 × 0.33 ≈ 11.9 | ≈ 0.5 (≈ 1.3 during its bands) | night and blue-hour staple |
| Driftfin | 0.17 | 12 × 3 × 0.50 × 0.17 ≈ 3.1 | ≈ 0.1 | a few visits per real hour, at the edges of the day |
| Hearth Echo | 0.20 | 8.57 × 4 × 0.60 × 0.20 ≈ 4.1 | ≈ 0.2 | only on grey, wet days |
| Halo Keeper | 0.85 | (2 × 1 × 0.60 × 0.85) × 0.952 ≈ 0.97 | — | about once per real hour, at blue hour |

**Example:** Halo Keeper: 2 bands × 1 anchor × 0.6 × 0.85 = 1.02 per world day; × 3,600,000 / 3,780,000 = **0.97 per real hour**. A player who learns "blue hour, lighthouse, not in rain" meets it about once an hour.

### F16. Naked-eye shimmer (presentation only)

The shimmer formula is defined as:

`shimmer_permille = (view = THIRD_PERSON ∧ pose ∈ {EMERGING, DECISIVE} ∧ dist_m ≤ SHIMMER_RANGE_M) ? max(SHIMMER_MIN_PERMILLE, 1000 − floordiv(1000 × dist_mm, SHIMMER_RANGE_M × 1000)) : 0`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| view | enum | THIRD_PERSON, VIEWFINDER | Player Movement (view state, client) | Current view |
| dist_mm | int (mm) | ≥ 0 | calculated (client, camera to subject) | Distance |
| SHIMMER_RANGE_M | int (m) | 10–60 | data file (default 35) | Shimmer visibility range |
| SHIMMER_MIN_PERMILLE | int (‰) | 0–500 | data file (default 250) | Minimum intensity inside range |
| shimmer_permille | int (‰) | 0–1000 | calculated (client) | Mote intensity |

**Output Range:** 0–1000; client-side only, never stored in a recipe and never read by the server.
**Example:** a Driftfin in its decisive pose 14 m away: 1000 − floordiv(1000 × 14,000, 35,000) = **600‰**; at 34 m it is 29 → raised to 250‰; at 36 m, 0.

## Edge Cases

- **If a capture lands exactly on a pose or state boundary**: half-open ranges apply as in World: `c = IDLE_MS + ANT_MS` is `DECISIVE` (with `dec_peak` 0), and a lifecycle change at tick `T` applies from `tick_ms(T)` inclusive.
- **If `capture_tick` is fractional**: lifecycle and awareness are those after the last tick with `tick_ms ≤ capture_ms`; position, facing, glow and pose phase are evaluated at `capture_ms` itself (Rule 31), so the result equals the interpolated pose the client was shown.
- **If Network clamps the client's `view_tick`**: this system evaluates the snapshot at the clamped `capture_ms`; it has no acceptance window of its own and never reads a client-sent pose.
- **If a player shoots a subject during the first ticks after it entered `WARY`**: the photo records `TUCKED` and `WARY_PTS`; there is no grace period, because the tuck is the visible feedback that the approach failed.
- **If the alarm reaches 1000 during `EMERGING`**: the flight starts immediately; a subject can be startled by someone standing on its anchor when it arrives. Its one return still applies.
- **If a flight would extend past the appearance `end`**: the appearance goes `GONE` at `end`; no return is possible.
- **If a player stands on an anchor before the appearance starts**: the subject still emerges there (the schedule never reads players). With walking presence at 0 m, intrusion is large, the first tick startles (`STARTLE_JUMP`), and the subject turns wary and usually flees. The emergence shimmer in third person is the learnable cue to step back.
- **If a player camps an anchor sneaking and still** (presence 0.4 m): no intrusion except at very close range, so the subject stays calm or becomes curious. This is intended play, not a degenerate case: patience is the skill. Diminishing returns on repeated subjects are owned by Photo Pricing.
- **Degenerate: camping a world event and ignoring the subject.** Bounded combination (F14): the world can lift the moment at most one step above the subject's own; and only in ANTICIPATION or DECISIVE poses, so an idle subject at an aurora keeps its own moment; SS/SSS moments need the decisive pose.
- **Degenerate: deliberately startling a subject for a "dramatic" flight photo.** `FLIGHT_PTS` = 0 → moment C, so the photo is capped at C by the capture rule. Startling is never rewarded.
- **Degenerate: sprint up, then sneak at the last second.** Movement's presence decay (its F5) keeps presence high for about 1.8 s, and the startle jump fires on the first tick inside `STARTLE_CM`; the subject tucks in.
- **Degenerate: one crewmate stands far away "on watch" while another approaches.** Co-op uses the largest intrusion (F4), so a distant teammate adds nothing; only the noisiest nearby player matters. (Alpha roles may add multipliers; never a way to block or herd a subject.)
- **Degenerate: herding a spirit into a better background by approaching from one side.** Allowed within bounds: wary retreat is at most `WARY_RETREAT_MM` (default 800 mm) and flight ends the encounter, so herding is small and costly. This is mild expressive play, not an exploit.
- **Degenerate: repeated close passes to farm decisive poses while curious.** Curiosity only rises while no one intrudes; each wary episode resets curiosity and restarts the cycle `RECOVER_IDLE_MS` before anticipation. There is no reward beyond the normal pose cycle.
- **If two players in one session are equally the nearest curious candidate**: the lower session slot is the target (F6); the subject faces that player.
- **If the curious target leaves `CURIOUS_R_CM` while another quiet player is inside**: curiosity keeps rising (any qualifying player suffices), and a `RETARGET` entry turns the subject to the new nearest player within `RETARGET_MIN_MS`.
- **If a player is at exactly the subject's position** (`d_cm` = 0, dx = dz = 0): intrusion equals reach; `dir16` returns the subject's current heading, so the flee direction is defined.
- **If no players are in the session's zone** (all in menus or the darkroom, or the session is empty): `I` = −1, alarm decays, and the schedule and pose cycle continue. In a solo session where the only player is `Released`, the session closes and its journals are retained for `JOURNAL_RETENTION_DAYS`.
- **If a player joins or reconnects mid-appearance**: they receive current snapshots; an appearance already present shows its current pose. Without journal entries, the pose is the default timeline (F9, F11), which is a pure function of the schedule.
- **If a session starts during an appearance** (late join): the appearance is instantiated in its default timeline at the current time; `calm_start` is the end of its emergence even if that was before the session began.
- **If a subject's drift or shift would take it inside solid geometry**: anchors are authored with `drift_radius_mm` that clears geometry (level-designer); subjects have no collision and may visually overlap thin props. Content validation warns (not fails) when the drift box intersects collision.
- **If a subject is beyond the camera's far clip or too small to recognise**: it is still in the recipe's subject set; Photo Scoring's Subject part decides whether it counts as "in frame and recognisable".
- **If two subjects are in frame**: this system supplies both snapshots; Photo Scoring picks the primary subject, and the moment combination uses that subject's moment (F14).
- **If no subject is in frame** (a landscape): this system returns no subject tier (`ERR_UNSET`) and the moment is `tier_min(world_moment_tier, "B")`. Capture Tier Resolution decides whether and how such a photo gets a tier.
- **If a variant's tier is above `enabled_cap`**: it is not scheduled (Rule 13). If `enabled_cap` is lowered later, already-stored photos keep their subject tier (Rarity Tier Ladder); appearances in progress finish; new ones stop with the next rules version.
- **If `enabled_cap` rises mid-day**: higher variants start spawning only from the next `subject_rules_version`, published at least `FORECAST_HORIZON_MS` ahead, so no appearance changes tier mid-visit.
- **If a World light event an EVENT species depends on is not scheduled** (weather failed, operator override): no appearance; there is no make-up visit.
- **If an event species' anchor already hosts another appearance**: higher tier wins (F3), so the event subject takes the anchor and the other candidate is dropped from the schedule.
- **If the zone cap is reached when a higher-tier candidate starts**: it is dropped like any other (F3 uses start order). Rationale: admission must stay pure and stable; rare species are protected by giving them dedicated anchors instead (level-designer).
- **If the server restarts or a session crashes**: schedules continue (pure functions of time); in-progress reactions are lost and appearances resume in their default timeline in the new session. Photos already captured keep their stored snapshots.
- **If an audit re-derives a snapshot from the journal and it differs from the stored one**: the stored snapshot is kept, a determinism alarm is raised, and the case is logged for the ai-programmer (Rule 32).
- **If a client sends a subject pose, tier, awareness or presence**: it is ignored, logged as a mismatch and counted per Network's violation rules; the server uses its own state (Network Core Rule 6).
- **If the Capture Encounter script asks for a state the rules forbid** (moving toward a player faster than Rule 25 allows, or blocking a path): the command is rejected at content validation; at runtime an invalid `ENC_PHASE` is ignored and logged.
- **If a hash or table input is negative** (schedule index before the epoch): World F1 returns `ERR_BEFORE_EPOCH` and no appearance is produced.
- **If the presence value from Movement is non-finite**: it is treated as `presence_max` (15 m) for that tick and logged; the subject reacts as to a loud player rather than ignoring the error.

## Dependencies

**Upstream (this system depends on):**

| System | Hard / soft | Interface | Status |
|---|---|---|---|
| Rarity Tier Ladder | Hard | tier IDs; `parse`, `is_enabled`, `clamp_to_enabled`, `tier_min`, `tier_max`, `tier_step`, `rank` (ordering only) | In Design; already lists this system as a dependent |
| World Time, Weather & Light | Hard | `world_state`, event schedule, `world_moment_tier`, `can_occur`, `find_next_window`, `hash32`, `peak_permille`, `points_to_tier`, `MOMENT_T`, versioning rules | Designed; lists this system as a dependent and hands it the moment combination (D7, D8) |
| Player Movement & Exploration | Hard | presence radius (F4/F5, server-evaluated), presence events, player position | Designed; lists this system as a dependent (presence contract, D5) |
| Network Transport & Server Authority | Hard | server tick and `tick_to_ms`, `capture_tick` (F8), history buffer (F9b), `SNAPSHOT` and `EVENT` transport, accepted positions | Designed; lists this system in its Interactions table ("Subjects are simulated on the server only") |

Note: `systems-index.md` row 7 lists "Rarity Tier Ladder, World Time Weather & Light, Player Movement & Exploration (presence radius)" but not Network Transport & Server Authority. It should add Network (not edited here; this run may write only this file).

**Downstream (systems that depend on this one):**

| System | Hard / soft | Interface | GDD status |
|---|---|---|---|
| Photo Recipe & Re-render | Hard | SubjectSnapshot content, `journal_digest`, `subject_rules_version` | Not started |
| Photo Scoring | Hard | subject geometry and pose, `subject_moment_points`, subject tier (Rarity part) | Not started |
| Capture Tier Resolution | Hard | `subject_tier`, combined `moment_tier` | Not started |
| Capture Encounter | Hard | rules, pose/moment formulas, `ENC_PHASE` journal commands | Not started |
| Zone Access & Travel | Soft | anchors per zone; species habitats as a reason to travel | Not started |
| Audio: SFX & Ambience | Soft | subject events with positions | Not started |
| First-Claim & Image Serials | Hard | `appearance_id`, tier, lifecycle | Not started |
| Co-op Crew Roles | Soft | role multipliers (`ROLE_SENSE_PCT`, `ROLE_CURIOUS_PCT`) | Not started |
| Subject Codex & Lore | Soft | species data | Not started |
| Server-Wide Events & Timed Races | Soft | operator EVENT appearances | Not started |
| Viewfinder HUD (not in the index's 10) | Soft | badge data, awareness band for the presence glyph | Not started |

Bidirectional note: each downstream GDD must list "depends on Subject & Spirit Behaviour" when authored.

## Tuning Knobs

All values live in data (proposed `assets/data/subjects/species.json` for the roster and parameters, anchors in each zone's data; paths → gameplay-programmer). Categories: **Feel** (playtest), **Curve** (maths), **Gate** (pacing).

**Per-species defaults (MVP)**

| Species | Tier | CYCLE_MS / DUR_MS | SPAWN_BP | SENSE_PCT | ALARM_GAIN / DECAY | STARTLE_CM | CURIOUS_R_CM / GAIN | IDLE / ANT / DEC / SET (ms) | DBASE / DSHARP | drift R / loop |
|---|---|---|---|---|---|---|---|---|---|---|
| Puffwisp | C | 180,000 / 120,000 | 7,000 | 100 | 3 / 10 | 500 | 500 / 12 | 6,000 / 1,500 / 2,000 / 1,500 | 45 / 20 | 1,500 mm / 16 s |
| Mossmote | C | 240,000 / 150,000 | 6,000 | 80 | 3 / 10 | 400 | 400 / 15 | 7,000 / 1,500 / 2,000 / 1,500 | 45 / 20 | 600 mm / 20 s |
| Driftfin | B | 300,000 / 120,000 | 5,000 | 130 | 4 / 8 | 500 | 600 / 10 | 9,000 / 1,200 / 1,500 / 1,300 | 50 / 25 | 2,500 mm / 24 s |
| Hearth Echo | B | 420,000 / 150,000 | 6,000 | 120 | 4 / 6 | 400 | — (not curious) | 9,500 / 2,000 / 2,500 / 2,000 | 55 / 25 | 0 mm (still) |
| Halo Keeper | A | BAND / 100,000 | 6,000 | 180 | 5 / 6 | 600 | 800 / 8 | 14,000 / 1,000 / 1,200 / 1,800 | 55 / 30 | 800 mm / 30 s |
| Driftfin (gilded), disabled | S | EVENT SUNBEAM | 8,000 | 140 | 4 / 8 | 500 | 600 / 10 | 9,000 / 1,200 / 1,500 / 1,300 | 60 / 30 | 2,500 mm / 24 s |
| Vesper Halo, disabled | SS | EVENT LUMEN_DUSK | 8,000 | 200 | 6 / 6 | 600 | 800 / 7 | 12,000 / 1,000 / 1,000 / 2,000 | 65 / 30 | 800 mm / 30 s |
| Aurora Drifter, disabled | SSS | EVENT AURORA | 8,000 | 220 | 6 / 5 | 700 | 1,000 / 6 | 16,000 / 1,500 / 1,500 / 3,000 | 66 / 30 | 4,000 mm / 40 s |

**Global knobs**

| Knob | Default | Safe range | Category | Affects | Too low / too high |
|---|---|---|---|---|---|
| `MAX_ACTIVE_PER_ZONE` | 8 | 4–12 | Gate | Subjects at once; bandwidth (Network F13) | Low: empty world. High: crowded, cheapens rarity, snapshot cost |
| `EMERGE_MS` / `DEPART_MS` | 3,000 / 4,000 | 1,000–6,000 | Feel | Arrival and calm departure | Low: pop-in. High: long unphotographable-feeling transitions |
| `WARY_T` / `CALM_T` | 400 / 200 | 250–700 / 100–300 | Curve | Warning time before a subject tucks; hysteresis | Narrow gap: flicker. High `WARY_T`: little warning before flight |
| `STARTLE_JUMP` | 400 | 0–600 | Feel | Punishment for arriving fast | Low: sprint-stop works. High: instant flights feel unfair |
| `CURIOUS_ON` / `CURIOUS_OFF` / `CURIOUS_DECAY` | 700 / 300 / 20 | see F6/F7 | Feel | How easily trust is earned and lost | Low ON: curiosity is free. High: players never see it |
| `CURIOUS_APPROACH_MM` / `CURIOUS_MIN_GAP_MM` | 600 / 1,500 | 0–1,500 / 1,000–3,000 | Feel | How close a curious subject comes | High approach or low gap: intrusive, may fill the frame unexpectedly |
| `WARY_RETREAT_MM` | 800 | 0–2,000 | Feel | Visible retreat; herding potential | High: herding becomes a tactic |
| `SHIFT_MS` / `TURN_MS` / `RETARGET_MIN_MS` | 1,000 / 800 / 500 | see F9/F10 | Feel | Reaction smoothness | Low: twitchy. High: reactions read late |
| `FLEE_MS` / `FADE_MS` | 2,500 / 3,000 | 1,000–5,000 | Feel | Flight readability | Low: blink-out. High: lingering, photo-farmable (moment is C anyway) |
| `RETURN_MS` / `MAX_RETURNS` / `MIN_RETURN_LEFT_MS` | 20,000 / 1 / 30,000 | see F8 | Gate | Cost of a mistake | Low: no stakes. High or 0 returns: harsh for a cozy game |
| `MIN_ANTICIPATION_MS` | 1,000 | 600–2,000 | Feel (load check) | Telegraph before every decisive pose | Low: reflex test, against Pillar 1's "reading" |
| `RECOVER_IDLE_MS` | 4,000 | 1,000–IDLE | Feel | Wait after a wary episode | Low: no cost to startling. High: dead time |
| `CURIOUS_BONUS` | 10 | 0–20 | Curve | Reward for trust in the moment tier | 0: curiosity is cosmetic. High: required for every good shot |
| `IDLE_PTS` / `ANTIC_PTS` / `WARY_PTS` / `FLIGHT_PTS` | 30 / 40 / 15 / 0 | 0–50 | Curve | Moment tier outside the decisive pose | High `IDLE_PTS`: timing stops mattering. `FLIGHT_PTS` > 30: startling pays |
| `WORLD_LIFT_STEPS` | 1 | 0–2 (5 = plain `tier_max`) | Curve | Anti-camping strength | 0: world events stop mattering for moment. ≥ 2: camping returns |
| `NO_SUBJECT_MOMENT_CAP` | "B" | C–A | Curve | Landscapes | High: landscape-camping events beats subjects |
| `SHIMMER_RANGE_M` / `SHIMMER_MIN_PERMILLE` | 35 / 250 | 10–60 / 0–500 | Feel | Finding subjects without the lens | Low: tedious scanning. High: the lens loses its magic |
| `ANCHOR_MAX_SHOT_M` | 40 | 20–80 | Gate (content) | Anchors must be photographable | — |
| `JOURNAL_RETENTION_DAYS` | 30 | 7–365 | Gate (ops) | Audit window | Low: disputes cannot be verified. High: storage |
| `FLEE_SPEED_MM_S` / `FLEE_RISE_MM_S` | 2,500 / 600 | see F8 | Feel | How far a spirit drifts when it flees | — |

**Rationale for the defaults.** Alarm: at walking pace and halfway into the notice range a subject tucks in after about 1.2 s and flees after about 3 s (F5), long enough to read and react, short enough that carelessness has a cost. Pose: every MVP decisive window is 1.2–2.5 s with at least 1 s of anticipation, close to the prototype's subject (7 s visible every 14 s with a glow pulse used for Moment), but tighter, because the prototype's whole visible half counted. Spawn: densities target "a common subject is almost always within reach in its hours" and "the A subject about once per real hour" (F15).

## Visual/Audio Requirements

(Required for Gameplay systems.) The art bible owns the look; these are this system's needs.

- **Lens-only rendering** (art bible A1, §2.1): spirits and memories draw only in the viewfinder; in third person only the Lumen shimmer (F16) at emergence and decisive pose.
- **Design language** (art bible §3.2, §5.3, A17): soft, rounded, floating, emissive in pale Lumen (`#7FE3D8`) or Paper White; no mouth, at most a two-dot face; one distinguishing trait per species readable at 64 px; tier shown by complexity (S+ adds orbiting parts, a trailing wisp and its own event light), never by size or threat.
- **Pose vocabulary must read at telephoto and thumbnail size**: `IDLE` tucked; `ANTICIPATION` one clear glow pulse plus a 100 mm rise; `DECISIVE` fully open (fins and ring spread, highest point, glow peak); `SETTLE` folds back; `TUCKED` 85% scale, dim, drifting back; `FLEEING` drifts away and up while dimming; `FADING` (memories) folds into motes in place; `DEPARTING` rises calmly. Curious subjects visibly turn to face the camera.
- **Never threatening**: no fast approach, no sharp shapes, no red, no looming; flight always moves away from the player.
- **Memories** read differently from spirits: still, framed by a faded rectangle of light (art bible §6.4 "spirit traces": empty frames with a Lumen shimmer), opaque with emissive and a dither or scale fold for fading (alpha budget: at most one alpha layer per view, art bible §8.5).
- **Re-render exactness** (art bible P4): all motion that can appear in a photo (drift, bob, facing, pose, glow) comes from the SubjectSnapshot; secondary motion (fin flutter, wisp sway) is seeded from `appearance_id` and `capture_ms`. No free-running timers.
- **Budgets** (art bible §8.3–8.4): common subjects 400–1,200 triangles, SS/SSS up to 2,000; rigid-part models from asset-forge animated by rotating named nodes; at most 8 subjects in the characters/subjects draw-call group of 60; glow via emissive (halo cards as the Compatibility fallback).
- **Audio** (owned by Audio: SFX & Ambience; requirements from here): a soft emergence chime (positional); a rising anticipation tone that always precedes the decisive pose (the audio half of the telegraph, so timing never depends on sight alone); a gentle bell at the decisive centre; a hush or breath when a subject tucks in; a soft airy swirl for a flight; a quiet return chime. No stingers, growls or alarm sounds. All cues must have visual equivalents (accessibility).

## Game Feel

(Required.)

- **Reaction latency.** A change of awareness is visible within one server tick plus the client's interpolation delay (Network F7: about 200–300 ms). The first visible sign of rising alarm (a tiny flinch at `A ≥ 150`, client-side from snapshot `awareness` and an `alarm_band` field) arrives before the tuck, so the player can correct.
- **The held breath.** Approach should feel like slow, deliberate negotiation: the player hears their own footsteps soften (Movement), sees the subject's glow steady when they stop, and feels relief when it turns to face them. Curiosity is the reward moment: it should arrive 1.5–3 s after the player becomes still and quiet nearby (F6 defaults: 2 s for Puffwisp, about 3 s for Halo Keeper).
- **Timing, not reflexes.** Anticipation is at least 1 s and always both visual and audible. The decisive window (1.2–2.5 s) is wide enough that the challenge is reading and readiness, not twitch; peak timing (the centre third) is the mastery layer. Network's ±60 ms tolerance is small against these windows.
- **Failure is gentle.** A flight is a soft drift away, not a pop. The one return (after 20 s) lets the player try again in the same visit, so the cost of a mistake is short and proportional to its frequency (flow principle: frequent failures need fast recovery).
- **Shared readability.** In co-op, the subject reacts to the loudest nearby player, and its facing shows who it trusts; teammates can read why it tucked in.
- **Feel knobs to tune by playtest:** `STARTLE_JUMP`, `WARY_T`, `CURIOUS_GAIN`, `ANT_MS`, `DEC_MS`, `SHIFT_MS`, `TURN_MS`, `FLEE_MS`, `SHIMMER_RANGE_M`.

## UI Requirements

- **Tier badge on a framed subject** (Viewfinder HUD): when a photographable subject is inside the frame in the viewfinder, show its subject tier badge (letter, `blades_lit`, colour token; Rarity Tier Ladder display table) near it, in Lumen-framed style. Always shown regardless of gear (higher-tier subjects are always visible and photographable). Never shown in third person.
- **Presence glyph input** (Movement D10's three-state glyph near subjects): this system supplies, for the nearest present subject within `CURIOUS_R_CM × 2` or its notice range, an `alarm_band`: *quiet* (`I ≤ 0`), *noticed* (`I > 0` and `A < WARY_T`), *too close* (`WARY` or `A ≥ WARY_T`). HUD owns the glyph art; the three states map one-to-one.
- **Curious cue**: a small, optional "it's watching you" indicator (an eye-dot pair in Lumen) when a subject is curious toward this player. Proposal for ux-designer; the subject turning is the primary cue.
- **Darkroom breakdown wording** (Darkroom UI owns layout): the Moment line explains the subject part in plain words: "caught at the height of its glow," "it was resting," "it had tucked away," "it was slipping away," and, when the world lifted it, "under a rare sky." Never name a tier that was clamped away or missed (no near-miss messaging).
- **Spawn and despawn**: no pop-up notifications for ordinary appearances (discovery is the point). Rare appearances (A and above) may show a soft one-line toast only if the player is in the zone, *after* emergence starts ("Something is gathering at the lighthouse"); proposal for ux-designer, never with an exact countdown.
- **Accessibility**: anticipation and decisive cues are both visual and audio; reduced-motion settings must keep the glow pulse (value change) even if the rise is removed; the badge uses letter plus blades, never colour alone.

## Cross-References

| Document | Section | Why |
|---|---|---|
| `design/gdd/rarity-tier-ladder.md` | Core Rules 6–8, 10; Player Fantasy; Edge Cases (near-miss) | tier IDs, `clamp_to_enabled`, gear-as-ceiling, no near-miss messaging, subjects always photographable |
| `design/gdd/world-time-weather-light.md` | Core Rules 7, 8, 10, 13; F1, F2, F4, F6, F8–F10, F13; Edge Cases; D7, D8 | windows, world moment, determinism, versioning, capture time, the moment combination hand-off |
| `design/gdd/player-movement-exploration.md` | R9, F4, F5, D5, D10, Open Question 3 | presence contract; the glyph; this GDD answers OQ3 (server simulates subjects) |
| `design/gdd/network-transport-server-authority.md` | Core Rules 6, 7, 23, 24; F8, F9b; Interactions table; acceptance criterion 37 | server-only simulation, snapshots, rewind, capture tick |
| `design/gdd/game-concept.md` | Pitch, Pillars, Rarity system (Capture rule, short windows, claimed once), Photo evaluation (Subject, Moment) | source requirements |
| `design/gdd/systems-index.md` | row 7, per-system rationale 7, B7, B8, circular dependency note | scope and dependents |
| `design/art/art-bible.md` | A1, A17, P4, §2.1, §3.2, §5.3, §6.4, §8.3–8.5 | look, pose vocabulary, re-render rule, budgets |
| `prototypes/aperture-concept/README.md` and `main.gd` | subject visible 7 s every 14 s, glow pulse used for Moment | precedent for decisive-pose timing |

## Acceptance Criteria

Logic tests live in `tests/unit/subject_behaviour/` (gdUnit4). All Logic tests use fixed seeds, fixed data fixtures and injected world state; no engine RNG, no wall clock.

**Schedule and tier**

1. [Logic] **GIVEN** a fixed `world_seed`, rules versions and zone, **WHEN** the schedule is computed twice for the same time range in two separate processes, **THEN** the lists of `appearance_id`s with start and end times are identical. `test_schedule_is_pure_function_of_seed_and_time`
2. [Logic] **GIVEN** the F1 example inputs with an injected hash returning 4,120 and 23,456, **WHEN** the Puffwisp schedule is computed, **THEN** `start` = 100,463,456 and `end` = 100,583,456. `test_periodic_schedule_example`
3. [Logic] **GIVEN** any PERIODIC species and any cycle `k`, **WHEN** a start is computed, **THEN** `start ≥ k × CYCLE_MS` and `start + DUR_MS ≤ (k + 1) × CYCLE_MS`. `test_periodic_appearance_stays_in_cycle`
4. [Logic] **GIVEN** a candidate whose span contains an effective-weather switch to a disallowed weather, **WHEN** `window_holds` is evaluated, **THEN** it returns false; **AND** a span with only allowed values at every `CHECK` instant returns true. `test_window_holds_checks_every_change_instant`
5. [Logic] **GIVEN** two overlapping candidates on one anchor with tiers B and C, **WHEN** admission runs, **THEN** only the B candidate is admitted. `test_anchor_conflict_higher_tier_wins`
6. [Logic] **GIVEN** 8 active appearances in a zone, **WHEN** a ninth candidate starts, **THEN** it is not admitted, and the result is the same regardless of player positions. `test_zone_cap_is_independent_of_players`
7. [Logic] **GIVEN** `enabled_cap = "A"`, **WHEN** a full world day is scheduled, **THEN** no appearance of an S, SS or SSS variant exists; **AND** every produced `subject_tier` is in {C, B, A}. `test_variants_above_cap_never_spawn`
8. [Logic] **GIVEN** the same variant in two different appearances with different awareness histories, **WHEN** their `subject_tier` is read, **THEN** both equal `clamp_to_enabled(TIER[variant])`. `test_subject_tier_fixed_per_variant`
9. [Logic] **GIVEN** a player record with any gear (phone through A gear), **WHEN** schedule, awareness and pose are computed, **THEN** no output differs between gear loadouts. `test_gear_never_affects_subjects`

**Awareness**

10. [Logic] **GIVEN** the F4 inputs (presence 650 cm, `SENSE_PCT` 180, offset 8,000/3,000/4,000 mm), **WHEN** intrusion is computed, **THEN** it equals 227. `test_intrusion_example`
11. [Logic] **GIVEN** a constant intrusion of 227 cm on a Halo Keeper from `A` = 0, **WHEN** ticks are stepped, **THEN** awareness becomes `WARY` on tick 37 and the flight starts on tick 91. `test_alarm_rise_timing`
12. [Logic] **GIVEN** a player whose intrusion rises from below to above `STARTLE_CM`, **WHEN** the crossing tick is processed, **THEN** `STARTLE_JUMP` is added exactly once for that crossing. `test_startle_applies_once_per_crossing`
13. [Logic] **GIVEN** a `WARY` subject with `A` = 407 and no intrusion, **WHEN** ticks are stepped, **THEN** it becomes `UNAWARE` when `A` first drops below 200 and never toggles back without new intrusion. `test_wary_hysteresis`
14. [Logic] **GIVEN** a Puffwisp and a still sneaking player at 300 cm (presence 40 cm), **WHEN** ticks are stepped, **THEN** awareness becomes `CURIOUS` on tick 59. `test_curiosity_gain_example`
15. [Logic] **GIVEN** a Hearth Echo (memory) and any quiet nearby player, **WHEN** ticks are stepped, **THEN** it never becomes `CURIOUS`; **AND** when alarm reaches 1000 it enters `FADING`, not `FLEEING`. `test_memory_fades_and_is_never_curious`
16. [Logic] **GIVEN** two players, one at intrusion 50 and one at −400, **WHEN** the tick runs, **THEN** the alarm rises by the amount for intrusion 50 (largest intrusion), not the sum. `test_coop_uses_largest_intrusion`
17. [Logic] **GIVEN** a curious subject, **WHEN** its position is evaluated at any time, **THEN** its distance to the curious player at the transition is never below `CURIOUS_MIN_GAP_MM` because of the shift, and its speed toward any player never exceeds `CURIOUS_SHIFT_MM_PER_S`. `test_subjects_never_rush_players`
18. [Logic] **GIVEN** a flight at `start + 40,000` in a 100,000 ms appearance, **WHEN** the lifecycle is evaluated, **THEN** it is `HIDDEN` from `start + 42,500`, re-emerges at `start + 62,500`, and a second flight ends in `GONE`. `test_one_return_after_flight`
19. [Logic] **GIVEN** a flight that starts with less than `MIN_RETURN_LEFT_MS + RETURN_MS + FLEE_MS` remaining, **WHEN** the lifecycle is evaluated, **THEN** the subject goes `GONE` without returning. `test_no_return_near_end`

**Pose, moment and determinism**

20. [Logic] **GIVEN** the F11 Halo Keeper example (`c0` = 11,000), **WHEN** the pose is evaluated at `start + 6,600` and `start + 7,400`, **THEN** they are `ANTICIPATION` and `DECISIVE` with `dec_peak` 667. `test_pose_cycle_example`
21. [Logic] **GIVEN** every variant in the roster, **WHEN** the data loads, **THEN** each has `ANT_MS ≥ MIN_ANTICIPATION_MS` and `DBASE + DSHARP + CURIOUS_BONUS ≥ MOMENT_T[TIER]`; a fixture violating either fails the load. `test_roster_load_checks`
22. [Logic] **GIVEN** a subject that enters `WARY` during `DECISIVE`, **WHEN** the pose is evaluated, **THEN** it is `TUCKED` immediately, and after `WARY` ends the next anticipation starts exactly `RECOVER_IDLE_MS` after `calm_start`. `test_wary_pauses_and_recovers_cycle`
23. [Logic] **GIVEN** the F13 inputs, **WHEN** subject moment points are computed, **THEN** Halo Keeper curious at peak 667 → 85 → tier A under cap A; Puffwisp idle → 30 → B; fleeing → 0 → C. `test_subject_moment_points_examples`
24. [Logic] **GIVEN** the F14 cases (B/SS, S/SSS, A/C) with `enabled_cap = "SSS"` in a test fixture and `WORLD_LIFT_STEPS` = 1, **WHEN** the moment is combined, **THEN** the results are A, SS and A; **AND** with no subject and world SS the result is B. `test_bounded_moment_combination` (Cases assume a DECISIVE pose.) **AND GIVEN** an IDLE subject of moment B and world A, **THEN** the result is B. `test_idle_pose_gets_no_world_lift`
25. [Logic] **GIVEN** any pair of subject and world moment tiers, **WHEN** combined with `WORLD_LIFT_STEPS` = 1, **THEN** the result is ≥ the subject moment, ≤ `tier_step(subject, +1)`, and ≤ `enabled_cap`. `test_moment_combination_bounds_property`
26. [Logic] **GIVEN** a recorded per-tick input stream (positions in mm, presence in cm) for one appearance, **WHEN** the simulation is replayed twice, **THEN** the journals are byte-identical. `test_journal_replay_is_bit_identical`
27. [Logic] **GIVEN** an appearance and its journal, **WHEN** the SubjectSnapshot is evaluated at a fractional capture time between two ticks, **THEN** position and glow equal the integer interpolation of the two neighbouring tick values to within 1 mm and 1‰, and awareness equals that of the earlier tick. `test_snapshot_at_fractional_capture_time`
28. [Logic] **GIVEN** the drift and bob example inputs, **WHEN** position is computed, **THEN** x offset = −350 mm and `bob_y` = 99 mm; **AND** `dir16(−8,000, −4,000)` = 9. `test_drift_and_dir16_examples`
29. [Logic] **GIVEN** a client `SHUTTER` or `MOVE` carrying subject pose, tier, awareness or presence fields, **WHEN** the server processes it, **THEN** those fields are ignored and the recipe uses server snapshots. `test_client_subject_fields_ignored`

**Integration**

30. [Integration] **GIVEN** a solo session at 150 ms simulated RTT and a subject in its decisive pose, **WHEN** the shutter is pressed while the client renders a frame inside the window, **THEN** the stored recipe's SubjectSnapshot has `pose = DECISIVE` and the `dec_peak` of the clamped `capture_tick` (extends Network criterion 37).
31. [Integration] **GIVEN** the MVP roster and defaults, **WHEN** a 7-real-day schedule is simulated (no players), **THEN** every species appears, the Halo Keeper appears 0.6–1.4 times per real hour on average, concurrency never exceeds 8, and every band × weather combination that occurs has at least one species able to appear (F15 check).
32. [Integration] **GIVEN** a photo's stored recipe, **WHEN** the gallery re-renders it, **THEN** the subject's position, facing, pose and glow match the live frame (screenshot pair retained in `production/qa/evidence/`).
33. [Integration] **GIVEN** an audit request for a stored photo, **WHEN** the server re-derives its SubjectSnapshots from the retained journal, **THEN** they equal the stored snapshots and `journal_digest` matches.
34. [Integration] **GIVEN** a player sneaking (grass, viewfinder raised) at 3 m from a Puffwisp, **WHEN** Camera Model's shutter presence event fires once, **THEN** the Puffwisp does not enter `WARY`.

**UI**

35. [UI] **GIVEN** a B-tier subject inside the frame in the viewfinder and the player holding a phone, **WHEN** the HUD renders, **THEN** the B badge (letter and 2 blades) is shown near the subject, and in third person only the shimmer (if emerging or decisive) is visible. Screenshot retained.
36. [UI] **GIVEN** a photo of an A subject captured under `enabled_cap = "A"` whose uncapped subject moment would be S, **WHEN** the darkroom breakdown is shown, **THEN** no text, badge or sound mentions S or any tier above the result.
37. [UI] **GIVEN** a player approaching a subject, **WHEN** intrusion goes from ≤ 0 to positive to `WARY`, **THEN** the presence glyph shows quiet, noticed and too close in that order. Screenshot sequence retained.

**Experiential (playtest, game-designer)**

38. [Integration] *(playtest)* **GIVEN** 5 first-time players for 20 minutes in the MVP area, **WHEN** observed, **THEN** at least 4 of 5 photograph a subject in its decisive pose on purpose (they wait for the anticipation), and at least 3 of 5 make a subject curious without being told how.
39. [Integration] *(playtest)* **GIVEN** the same session, **WHEN** players are asked afterwards, **THEN** no player describes any subject as threatening or scary, and at least 4 of 5 can say why a subject fled when it did.
40. [Integration] *(playtest)* **GIVEN** a player who startles a subject, **WHEN** it returns, **THEN** the player tries again in the same visit in at least 70% of observed cases (failure recovery is fast enough to invite retry).

## Open Questions

| # | Question | Owner | Resolve by |
|---|---|---|---|
| 1 | Shared ADR with World: `hash32`, `isqrt`, `floordiv`, the published `SIN64` and `DIR16` tables and reference vectors for this system's formulas. | technical-director → ADR "Deterministic world-state functions" (extend) | Before implementation |
| 2 | Journal storage: where journals live, their size per appearance, retention (`JOURNAL_RETENTION_DAYS`), and whether audit needs them below tier A. | ai-programmer + technical-director → ADR | Before implementation |
| 3 | Presence quantisation: Movement's F4/F5 are floats; this GDD floors to cm at the boundary. Is server-side presence evaluated in a deterministic order so two processes agree on the floored value? | gameplay-programmer + ai-programmer | Before implementation |
| 4 | First-Claim across separate solo sessions: the same `appearance_id` can be met in several sessions with different reactions. Is the claim per appearance globally (first valid capture anywhere) or per session? | game-designer + First-Claim GDD (B7) | Alpha |
| 5 | Line of sight: should walls block presence for some species in Alpha (e.g. a spirit that hides behind the lighthouse)? Costs one server raycast per player per subject per tick. | game-designer + ai-programmer | Alpha |
| 6 | Capture Encounter contract: the exact `ENC_PHASE` command list and how an encounter appearance is scheduled (EVENT-like row or operator row). | Capture Encounter GDD | Capture Encounter design |
| 7 | Photo Scoring: does the Moment *part* (0–100 score) reuse the combined moment points, or score timing separately? Does the Subject part use `BOUNDS_MM` and facing for "recognisable"? | systems-designer (Photo Scoring GDD) | Photo Scoring design |
| 8 | Names, lore and the look of the five species and three disabled variants (placeholders here). | narrative-director + art-director | Before art production |
| 9 | Wildlife (animals, art bible §5.4) as subjects in Vertical Slice: same rules with `kind = ANIMAL` and line of sight? | game-designer | Vertical Slice |
| 10 | Should NPCs or the Codex give habit hints ("the lighthouse at blue hour") in MVP, and how precise? | game-designer + ux-designer | First playable |
| 11 | Playtest tuning of alarm and curiosity numbers, and whether `MAX_RETURNS = 1` is too gentle or too harsh. | game-designer (playtest) | First playable |
| 12 | Asset scope: can asset-forge's rigid-part pipeline produce readable decisive poses for all five species within budget (systems-index high-risk row)? | art-director + technical-artist | Before art production |

**Added 2026-11-04 (pillar check):** curiosity barely changes the tier at `enabled_cap` A, so a long lens can match a trusted approach. Photo Scoring must carry the reward for closeness, or these values must be re-tuned; owner game-designer, resolve in the Photo Scoring GDD. Memories have no curiosity or reward of their own yet; owner game-designer, resolve before Vertical Slice.

## Decisions to confirm

> **DECIDED 2026-11-04 (user):** every item = the recommended option. D7: bounded max (the world lifts the moment at most one step above the subject's own).

- **D1. MVP roster size.** (a) **Five species (2 × C, 2 × B including one memory, 1 × A) plus three disabled S/SS/SSS variants as data**, matching the concept's "about 5 photographable subjects" and covering every band and weather. (b) Three species (C, B, A): cheaper art, but nights or rainy hours would be empty. (c) Eight species: more discovery, but triples rigid-part art work for the first playable. **Recommendation: (a).**
- **D2. Lens-only visibility.** (a) **Spirits and memories render only in the viewfinder; in third person only a faint Lumen shimmer appears at emergence and during the decisive pose, within 35 m.** It keeps the lens magical and gives a learnable "something is there" cue. (b) Fully invisible without the lens, so players must scan constantly through the viewfinder (tedious, slow exploration). (c) Visible to the naked eye as a pale silhouette, which is easier to find but makes the lens no longer special. **Recommendation: (a).**
- **D3. How approach works.** (a) **Presence versus distance gives an intrusion value that drives an alarm meter with hysteresis, a startle jump for sudden arrivals, curiosity for quiet players nearby, and no line of sight in MVP.** Readable, deterministic, cheap. (b) A hard radius: step inside it and the subject flees at once (simple, but harsh and binary). (c) Sight cones with line-of-sight raycasts (richer stealth, more server cost, less cozy). **Recommendation: (a).**
- **D4. What happens when a subject is startled.** (a) **It flees (spirits) or fades (memories), returns once after 20 s if at least 30 s of the visit remain, and a second flight ends the visit; later appearances are unaffected.** Gentle failure that invites retry. (b) The visit ends on the first flight (higher stakes, harsher for a cozy game). (c) No flight at all, only wary tucking (removes the stakes from approach). **Recommendation: (a).**
- **D5. Subject tier per species or per appearance.** (a) **Fixed per species variant, authored, never rolled; rare variants come from rare world windows (e.g. a sunbeam Driftfin).** Learnable and fair. (b) Rolled per appearance (a gacha pull on every visit, and against "fairness by learnability"). (c) Fixed per anchor (place-based, but the same spirit would have different tiers in different places). **Recommendation: (a).**
- **D6. Variants above `enabled_cap`.** (a) **Not scheduled at all until the cap rises (new rules version); `clamp_to_enabled` stays as a safety net.** (b) Spawn them with their tier clamped to A: more spectacle in MVP, but an "SSS-looking" spirit worth A would confuse players and devalue it later. **Recommendation: (a).**
- **D7. World + subject moment combination.** (a) **Bounded max: `tier_max(subject, tier_min(world, subject + 1 step))`, so the world can lift the moment at most one step above the subject's own; the knob `WORLD_LIFT_STEPS` (5 = plain max).** It keeps World's "either instant counts" while stopping event camping. (b) Plain `tier_max(world, subject)` (World's original recommendation), with camping handled elsewhere (for example by Photo Scoring). (c) `tier_min(world, subject)`: both must align, which caps every noon photo at C. (d) Subject only: world events no longer matter for moment. **Recommendation: (a).** **2026-11-04: amended by the pillar check: the lift applies only in ANTICIPATION or DECISIVE poses (Core Rule 33, F14).**
- **D8. Moment value outside the decisive pose.** (a) **A calm subject is B (30 points), anticipation B (40), a tucked subject C (15), a fleeing or fading one C (0).** Ordinary shots are usable; startling is never rewarded. (b) Calm subjects are C, which makes every non-decisive photo C and timing extremely punishing. (c) Flight counts as a dramatic B moment, which rewards scaring subjects. **Recommendation: (a).**
- **D9. Curiosity.** (a) **Quiet, close players make a subject curious: it faces them, drifts a little nearer and its decisive pose earns +10 moment points.** It rewards patience and gives the subject a personality. (b) No curiosity, only alarm (simpler, but colder and less "trust"). (c) Curiosity required before any decisive pose (too strict; long-lens play becomes impossible). **Recommendation: (a).**
- **D10. Co-op aggregation.** (a) **The subject reacts to the largest intrusion among players; curiosity targets the nearest quiet player.** A crew is as quiet as its loudest nearby member, and a distant teammate costs nothing. (b) Sum of intrusions (crews are punished for being crews). (c) Nearest player only (a loud player just behind the nearest one is ignored). **Recommendation: (a).**
- **D11. Schedule scope.** (a) **One global schedule per zone, shared by every session; reactions simulated per session.** "The Halo Keeper at blue hour" is shared knowledge for crews, commissions and First-Claim. (b) A per-session seed (private worlds; breaks shared planning and first-claim). (c) Per player (no shared world). **Recommendation: (a).**
- **D12. Reproducibility method.** (a) **Pure schedule + tick-stamped reaction journal + stored SubjectSnapshot in the recipe; re-scoring reads the snapshot, audit re-derives from the journal.** (b) Full re-simulation from recorded raw inputs on every re-score (heavy, fragile). (c) Stored snapshot only, with no journal (cheapest, but disputes cannot be verified). **Recommendation: (a).**
- **D13. Moment for photos with no subject.** (a) **`tier_min(world_moment_tier, "B")`; whether such a photo gets an image tier is Capture Tier Resolution's decision.** (b) World moment unrestricted (landscape camping of events beats subjects). (c) Always C. **Recommendation: (a).**
- **D14. Decisive pose cadence.** (a) **A repeating, seeded pose cycle per species, decisive windows of 1.2–2.5 s, at least 1 s of audible and visible anticipation, paused while wary.** (b) Decisive poses only when curious (rarer, trust-gated). (c) Random decisive moments with no telegraph (reflex test, against "reading"). **Recommendation: (a).**
- **D15. Systems index row 7 dependency.** (a) **Add Network Transport & Server Authority to row 7's "Depends On" (not edited here, as instructed).** (b) Leave it as is and treat Network as transport, not a design dependency. **Recommendation: (a).**
