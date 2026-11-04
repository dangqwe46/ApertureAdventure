# World Time, Weather & Light

> **Status**: Designed 2026-11-03 (pending `/design-review` in a fresh session)
> **Author**: user + agents (systems-designer)
> **Last Updated**: 2026-11-03
> **Last Verified**: 2026-11-03
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-03 — CONCERNS fixed: D11 marked superseded; SSS-reachability criterion (48) added; neutral event IDs; D8 subject-camping risk handed to Subject & Spirit Behaviour. NOT ASSESSED: MDA aesthetics target (none stated); tone fit (tone unconfirmed).
> **Implements Pillar**: Pillar 1 "Seeing is the skill" (reading light and timing is the skill check); supports Pillar 3 "Play together without violence" (tension comes from fleeting light, shared by everyone in the world)

## Summary

World Time, Weather & Light is the deterministic world clock of Aperture. From one server timestamp it derives the time-of-day band, the weather, any rare light event, the light condition (one of the art bible's seven presets), a **light tier** and a **world-moment tier** (both rarity-ladder IDs), and the key-light direction and scene brightness. Everything is a pure integer function of `(capture time, zone, rules version)`, so the headless server can recompute any photo's world state exactly without rendering. Clients never hold the seed; they get a resolved feed plus a short forecast.

> **Quick reference** — Layer: `Foundation` · Priority: `MVP` · Key deps: `Rarity Tier Ladder` (tier IDs, `clamp_to_enabled`); consumed by Subject & Spirit Behaviour, Camera Model, Photo Recipe, Photo Scoring, Capture Tier Resolution, Network Transport · Engine: Godot 4.7.2, Web/Compatibility; rendering claims not covered by `docs/engine-reference/godot/modules/rendering.md` are marked UNVERIFIED

## Overview

This system answers one question for the rest of the game: *"At server time T, in zone Z, what is the world like?"* The answer is a **WorldState**: the world day and phase, the time-of-day band (blue hour, dawn, day, golden hour, blue hour, night), the weather (clear, overcast, fog, rain) and its transition blend, any active rare light event, the resulting light condition, a 0–100 light-quality value, the **light tier**, the **world-moment** inputs and tier, the key-light angles, the scene exposure value and the wind. It owns the clock, the weather schedule, the light-event schedule and the formulas that turn them into tiers. It does not own subjects, exposure math, the scoring of light direction, or how the world looks (the art bible and technical-artist own the presets).

The design is built around the server re-scoring photos without a GPU (`docs/architecture/research-web-networking.md` §4.1). Every output that can affect a score is computed with 64-bit integers, a specified hash and explicit floor division, with no engine RNG and no floats, so two server processes, or one server a year later, produce the same WorldState for the same inputs. The clock is **global and accelerated**: a world day lasts 63 real minutes, so one week of real time holds exactly 160 world days, and a player who can only play at 8 pm still sees every hour over the course of a week. Weather is a **seeded schedule**, not live randomness: players can learn it, plan around it and see a forecast, but only the server knows the seed. The top tiers of light (SS, SSS) come only from rare, short, seeded light events, which is how the concept's rule *"Top-tier subjects appear only in short windows (a particular weather, hour or place)"* becomes data.

Implementation choices (data format, hash algorithm, how the feed is delivered) are not fixed here; they become ADRs (see Open Questions).

## Player Fantasy

**Framing: direct.** The player reads this system with their eyes every second they play.

**"I know this light."** The fantasy is the photographer who has learned the sky: who knows the harbour turns gold in ten minutes, that a grey evening can break into rays, that the cyan dusk only comes after a clear day. The anchor moment: the forecast says the evening slot is overcast. Most players write off golden hour. One player remembers that sunbeams only come through cloud at golden hour, walks to the cliff, waits, and the sky opens for two minutes. They got the shot because they read the world, not because of their gear. That is Pillar 1, *"Success comes from the player's eye and timing. Gear raises the ceiling but never replaces skill,"* and the core fantasy, *"I see what others miss, and I choose what's worth keeping."*

**The world is shared.** Everyone is under the same sky. When the aurora comes, every player in that zone sees it at the same moment, and crewmates can say "tonight, the lighthouse" and mean the same thing. This supports Pillar 3: the tension is the light closing, never a threat (art bible P3, *"make the light rarer and shorter rather than making anything bigger, faster or sharper"*).

**Fairness by learnability.** Nothing in the light is a hidden dice roll at the moment of the shot. The light tier is fully set by where and when you stand, and you can see the light before the score names it (art bible §2.2: *"Light quality must be legible to the naked eye"*). Luck decides which days bring rare events; skill decides whether you are there and ready.

> Tone and setting are unconfirmed (concept Open Questions). Event names (Lumen Dusk, Aurora) assume the proposed spirit setting, but the mechanics work for any setting.

## Detailed Design

### Core Rules

1. **One authoritative clock.** World time is a pure function of the server's UTC time in integer milliseconds: `t_w = t_ms − WORLD_EPOCH_MS`. It has no runtime state, never pauses, and is the same for every zone, room, process and player. Menus, disconnects and server restarts do not stop it. Time zones and daylight saving play no part, because only UTC is used.
2. **Accelerated day, made of bands.** A world day lasts `DAY_MS` = 3,780,000 ms (63 real minutes) and is an ordered list of **bands**, each with a real duration in ms. Phase 0 is the start of `BLUE_AM`. Default band table:

   | Band | Real duration | Phase range (s) | Display clock | Share of day |
   |---|---|---|---|---|
   | `BLUE_AM` | 120 s | 0 – 120 | 05:00 – 05:30 | 3.2% |
   | `DAWN` | 300 s | 120 – 420 | 05:30 – 07:00 | 7.9% |
   | `DAY` | 1,620 s | 420 – 2,040 | 07:00 – 17:30 | 42.9% |
   | `GOLDEN` | 420 s | 2,040 – 2,460 | 17:30 – 19:00 | 11.1% |
   | `BLUE_PM` | 240 s | 2,460 – 2,700 | 19:00 – 19:45 | 6.3% |
   | `NIGHT` | 1,080 s | 2,700 – 3,780 | 19:45 – 05:00 | 28.6% |

   Band ranges are half-open `[start, end)`. The displayed clock is non-linear (it runs faster through the long bands). It is flavour for the HUD only and never a scoring input. The morning is the pastel `DAWN` and the evening is the warm `GOLDEN`, so the two ends of the day look different on purpose.
3. **Zones.** Every outdoor place belongs to a **zone** (`zone_id`, int). A zone has its own weather weights, light modifiers, event eligibility and a `zone_phase_offset_ms` (MVP: 0 for the single area). The offset is reserved so that later, travelling between zones can mean travelling to a different hour (Zone Access & Travel, Vertical Slice). A zone with `world_light = false` (an interior) ignores the clock and uses a fixed light condition from zone data (rule 15).
4. **Weather is a seeded slot schedule.** Time is cut into weather **slots** of `SLOT_MS` = 630,000 ms (10.5 real minutes, 6 per world day, aligned to the day). Each slot has one weather from {`CLEAR`, `OVERCAST`, `FOG`, `RAIN`}, drawn from the zone's weights with a server-secret seed (Formula 3). A "stay" roll makes some slots copy the previous slot's draw, so weather has some continuity while every slot can still be computed in O(1) from its index alone. At the start of each slot, the weather blends from the previous slot's weather over `TRANSITION_MS` = 60,000 ms. For every gameplay output, the **effective weather** is the new weather once the blend reaches 500‰ and the previous weather before that.
5. **Light condition.** The band and the effective weather select one of the art bible's seven light conditions (§2.2): `DAWN`, `MIDDAY`, `GOLDEN_HOUR`, `BLUE_HOUR`, `NIGHT`, `OVERCAST_FOG`, `RAIN` (Formula 5). Visual crossfades between presets are client-side presentation only. For gameplay, the condition is always one discrete value at the capture time.
6. **Light tier.** The condition, how close the shot is to the centre of its band (**band peak**), the zone modifier and any active light event give an integer **light quality** `LQ` from 0 to 100. Thresholds turn `LQ` into a ladder tier, and the result is passed through `clamp_to_enabled` (Formulas 6, 7). Outputs are ladder **IDs** only; no rank is stored or sent (Rarity Tier Ladder, Core Rule 2). Without an event, the best light is S (golden hour at its peak). SS and SSS light exist only during light events.
7. **Light events.** Rare, short, seeded light phenomena. Defaults: `SUNBEAM` (rays through cloud at golden hour under overcast), `LUMEN_DUSK` (a cyan dusk at evening blue hour under a clear sky) and `AURORA` (violet bands at night under a clear sky). The art bible requires that *"a rare window must look different from ordinary golden hour"*. For each zone and world day, each event type gets one deterministic roll (Formula 8). An event fits entirely inside its band and has a lifecycle `BUILDING → ACTIVE → FADING`. Only `ACTIVE` affects tiers. An event is scheduled only if the required weather holds across its whole lifecycle, so the weather can never cut it short. At most one event can happen per band per zone per day; if two would share a band, the higher-priority one wins. Operator-scheduled events (Server-Wide Events, Full Vision) are rows in the versioned schedule data and override seeded events in the same band.
8. **World moment, and who owns "moment".** This system owns the **world** part of the decisive moment: how rare and brief the current world window is, and how close the shot is to its peak (Formula 10). It outputs `world_moment_points`, `world_moment_tier` (a ladder ID, clamped) and the list of active windows with their phases and the time left in each. **Subject & Spirit Behaviour** owns the subject's part (decisive pose timing) and the rule that combines the two into the capture rule's "Moment tier". The recommended combination is `tier_max(world_moment_tier, subject_moment_tier)`, so catching either the world's instant or the subject's instant counts (see Decisions to confirm, D7 and D8). This is consistent with the Rarity Tier Ladder's interaction table, which lists this system as the owner of a moment-tier output. The dependency still runs one way, because this system never reads subject state.
9. **Key light and brightness.** The system outputs the key-light elevation and azimuth in integer decidegrees (the sun by day, the moon at night, one shadow-casting light as the art bible requires), and `scene_ev_deci`, the scene exposure value at ISO 100 ×10 (Formulas 11, 12). Camera Model owns the exposure maths. Photo Scoring owns how light direction is scored. Both read these integers.
10. **Determinism contract.** Every output in rules 1–9 that a score or tier can depend on is computed with 64-bit integer arithmetic, explicit floor division (`floordiv`), a specified 32-bit hash with published test vectors (`hash32`), and data tables. Engine RNG (`randi`, `RandomNumberGenerator`), `hash()` on Variants, floats and trigonometry are forbidden in that path. Float trig is allowed only downstream (for example Photo Scoring turning angles into a vector), and that system owns its own tolerance. The same function library runs on the server and the client. Clients use it only to interpolate visuals between feed updates.
11. **Seed secrecy, world feed and forecast.** `world_seed` exists only on the server. Clients receive a **world feed**: the current WorldState, the public band table, the effective weather for the next `FORECAST_SLOTS` = 6 slots (one world day), and **event notices**. An event notice names the zone and band, never the exact minute, and appears `EVENT_NOTICE_MS` = 600,000 ms (10 real minutes) before the event's build-up starts. Players can plan without being able to datamine the schedule.
12. **The server owns the capture time, through Network.** The capture instant is the lag-compensated tick that Network Transport & Server Authority resolves (its Formula F8: ±60 ms tolerance, at most 400 ms rewind), converted to server UTC ms (Formula 13). This system has no acceptance window of its own and never reads a client-sent time. The server then computes the WorldState from the accepted `capture_ms`; it never trusts a client-sent tier, weather or condition.
13. **Versioned rules, never retroactive.** All world data (epoch, band table, slot length, weights, thresholds, events, operator events, seed) belongs to a `world_rules_version` with an `effective_from_ms`. The version used is the latest one with `effective_from_ms ≤ capture_ms`. A new version is only accepted if `effective_from_ms ≥ now + FORECAST_HORIZON_MS`, so a forecast or notice already shown stays true. Every version stays loadable on the server for re-scoring and disputes.
14. **Snapshot for re-render.** At capture, the server writes a compact **WorldSnapshot** into the photo record: `world_rules_version`, `capture_ms`, `zone_id`, `phase_ms`, band, previous and effective weather, `blend_permille`, condition, `event_id` and `event_phase_permille`, key-light angles, `scene_ev_deci`, `wind_dir_deg`, `light_tier` and `world_moment_tier`. The gallery and leaderboard re-render from the snapshot plus the public band and preset tables, never from the seed. Animated shaders (wind, water, shimmer) take their time from `capture_ms` (art bible P4 and §8.5: *"must take time from the world clock, not a free-running timer"*). Photo Recipe owns the schema; this system defines the content.
15. **Interiors.** In a zone with `world_light = false`, the condition, `LQ`, key light and EV come from zone data. The light tier is computed from that fixed `LQ`, the world moment uses only the `DAY` band window (world moment C), and no events occur. MVP interiors (darkroom, shop) are not photographable; the rule exists so the first photographable interior has defined behaviour.

**What this system does not own:** subject spawning and poses (it answers the window queries Subject & Spirit Behaviour asks); exposure maths (Camera Model); the Light and Moment parts of the score (Photo Scoring); the capture rule and odds (Capture Tier Resolution); the recipe schema (Photo Recipe); clock sync and message transport (Network Transport); the look of each preset (art bible, technical-artist); audio beds (Audio).

### States and Transitions

The system is stateless: every state below is *derived* from `t_w`, not stored. The tables describe what the derived values do as time passes.

**Band cycle (per zone, repeats every world day)**

| From | To | Trigger | Notes |
|---|---|---|---|
| `BLUE_AM` | `DAWN` | phase reaches 120,000 ms | key light rises above the horizon |
| `DAWN` | `DAY` | 420,000 ms | the flat "midday" look begins |
| `DAY` | `GOLDEN` | 2,040,000 ms | the signature light |
| `GOLDEN` | `BLUE_PM` | 2,460,000 ms | the sun sets |
| `BLUE_PM` | `NIGHT` | 2,700,000 ms | the key light switches from sun to moon |
| `NIGHT` | `BLUE_AM` | 3,780,000 ms (wraps to 0) | `day_index` + 1 |

The client may crossfade presets across a boundary over `BAND_XFADE_MS` (default 20,000 ms, centred on the boundary). This is visual only; the scoring band changes exactly at the boundary.

**Weather slot**

| State | Entered when | Exits when | Effective weather |
|---|---|---|---|
| `SETTLED` | blend reaches 1000‰ | next slot starts | `weather(n)` |
| `TRANSITION` (blend < 500‰) | slot `n` starts | blend reaches 500‰ | `weather(n−1)` |
| `TRANSITION` (blend ≥ 500‰) | blend reaches 500‰ | blend reaches 1000‰ | `weather(n)` |

If `weather(n) = weather(n−1)`, the transition is invisible and the effective weather does not change. A **clearing** window opens when the effective weather changes from `OVERCAST`, `FOG` or `RAIN` to `CLEAR`, and lasts `CLEARING_MS` (default 90,000 ms) from the slot start.

**Light event lifecycle (per scheduled event)**

| State | Duration (default) | Effect on outputs |
|---|---|---|
| `NOTICE` | 600,000 ms before `BUILDING` | feed carries the zone and band hint; no visual or tier effect |
| `BUILDING` | `build_ms` | visual build-up (the readable cue); no tier effect |
| `ACTIVE` | `active_ms` | event light and moment points apply (Formulas 7, 10) |
| `FADING` | `fade_ms` | visual fade; no tier effect |
| `NONE` | — | — |

**Rules version**

| From | To | Trigger |
|---|---|---|
| version *k* active | version *k*+1 active | `capture_ms` (or now) ≥ `effective_from_ms(k+1)`; must be at least `FORECAST_HORIZON_MS` in the future when published |

### Interactions with Other Systems

| System | Reads from this system | Sends to this system | Notes |
|---|---|---|---|
| Rarity Tier Ladder | — | tier IDs, `clamp_to_enabled`, `tier_max`, `tier_min`, `tier_step` | this system produces ladder IDs |
| Subject & Spirit Behaviour | `world_state(z, t)`, active windows with phase and `ms_to_end`, `world_moment_tier`, `find_next_window(z, from_t, predicate, horizon)`, `can_occur(z, predicate)` | nothing | spawn windows ("subject X appears in GOLDEN under OVERCAST") are predicates on WorldState; owns the final moment tier |
| Camera Model | `scene_ev_deci`, condition, key-light angles | nothing | exposure maths lives there |
| Photo Recipe & Re-render | WorldSnapshot content (rule 14); `world_rules_version` | `capture_ms`, `zone_id` | the recipe stores the snapshot; re-render reads it |
| Photo Scoring | `LQ`, condition, key-light angles, event id | nothing | the Light part ("direction and quality") may reuse `LQ` for quality |
| Capture Tier Resolution | `light_tier`; the moment tier through Subject & Spirit Behaviour | nothing | `tier_min` over all limits |
| Network Transport & Server Authority | world feed content, capture-time acceptance rule | clock sync offset (client side), receipt time `r` | Network owns transport and sync; this system owns the content and the rule |
| Player Movement & Exploration | — | `zone_id` at the player's position (server side) | the server validates the recipe's zone against its own position data |
| Expedition Rooms (Alpha) | the same global clock | nothing | rooms do not own a clock |
| Audio: SFX & Ambience | condition, effective weather, blend, event state | nothing | ambience beds and the event cue |
| Viewfinder HUD | display clock, band, weather, forecast, event notices | nothing | see UI Requirements |
| Daily Themes, Commission Board | condition and band from the photo's snapshot | nothing | "golden hour" themes, "the lighthouse at dusk" requests |
| Server-Wide Events (Full Vision) | — | operator event rows (through the versioned schedule) | |
| Zone Access & Travel (VS) | — | per-zone `zone_phase_offset_ms`, weights | |
| Economy Telemetry (Alpha) | time share per light tier, event counts | nothing | tuning the dead-top-end risk |

## Formulas

Notation: all values are 64-bit integers. `floordiv(a, b)` rounds toward negative infinity. `mod(a, b)` is the matching non-negative remainder. `‰` is per mille (0–1000). `bp` is basis points (0–10,000). `hash32(...)` is the specified hash (rule 10), returning 0 to 2^32−1.

### F1. World clock

The world_clock formula is defined as:

`t_w = t_ms − WORLD_EPOCH_MS;  t_z = t_w + zone_phase_offset_ms[z];  day_index = floordiv(t_z, DAY_MS);  phase_ms = mod(t_z, DAY_MS);  band = the B with BAND_START[B] ≤ phase_ms < BAND_END[B];  band_offset_ms = phase_ms − BAND_START[band];  slot_index = floordiv(t_z, SLOT_MS);  slot_offset_ms = mod(t_z, SLOT_MS)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t_ms | int (ms) | ≥ WORLD_EPOCH_MS | calculated (server UTC, or an accepted `capture_ms`) | Unix time in ms |
| WORLD_EPOCH_MS | int (ms) | fixed per rules version; default 1,798,761,600,000 (2027-01-01T00:00Z, placeholder) | data file | Start of world time |
| zone_phase_offset_ms | int (ms) | 0 to DAY_MS−1; MVP 0 | data file (zone table) | Per-zone shift of the clock |
| DAY_MS | int (ms) | default 3,780,000 | data file | Length of a world day; must equal the sum of band durations |
| BAND_START, BAND_END | int (ms) per band | 0 to DAY_MS | data file (band table) | Half-open band ranges |
| SLOT_MS | int (ms) | default 630,000; must divide DAY_MS | data file | Weather slot length |
| day_index | int | ≥ 0 | calculated | World day number |
| phase_ms | int (ms) | 0 to DAY_MS−1 | calculated | Time into the world day |
| band | enum | {BLUE_AM, DAWN, DAY, GOLDEN, BLUE_PM, NIGHT} | calculated | Current band |
| band_offset_ms | int (ms) | 0 to band length−1 | calculated | Time into the band |
| slot_index, slot_offset_ms | int | ≥ 0; 0 to SLOT_MS−1 | calculated | Weather slot and time into it |

**Output Range:** `phase_ms` is always in [0, DAY_MS). `t_ms < WORLD_EPOCH_MS` returns `ERR_BEFORE_EPOCH`, never a negative day. int64 ms does not overflow for about 292 million years.
**Example:** `t_w` = 100,580,000, offset 0. `day_index` = floordiv(100,580,000, 3,780,000) = 26 (26 × 3,780,000 = 98,280,000). `phase_ms` = 2,300,000, which falls in GOLDEN [2,040,000, 2,460,000). `band_offset_ms` = 260,000. `slot_index` = floordiv(100,580,000, 630,000) = 159 (slot 3 of day 26). `slot_offset_ms` = 410,000.

### F2. Band peak

The band_peak formula is defined as:

`peak_permille(o, L) = 1000 − floordiv(1000 × |2·o − L|, L)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| o | int (ms) | 0 to L−1 | calculated (F1 `band_offset_ms`, or the offset into an event's ACTIVE phase or a clearing window) | Offset into the window |
| L | int (ms) | > 0 | data file (band, event or clearing length) | Window length |
| peak_permille | int (‰) | 0 to 1000 | calculated | 1000 at the window centre, 0 at its edges, linear between (a triangle) |

**Output Range:** 0 to 1000, never negative because |2o − L| ≤ L. The time spent at or above any value x is (1000−x)/1000 of the window, so peak is uniformly distributed over time.
**Example:** GOLDEN, o = 260,000, L = 420,000: |520,000 − 420,000| = 100,000; floordiv(100,000,000, 420,000) = 238; peak = **762**. At o = 210,000 (the centre) peak = 1000; at o = 0 peak = 0.

### F3. Weather slot draw

The weather_slot formula is defined as:

`raw(n, z) = PICK(WEIGHTS[z], mod(hash32(world_seed, z, n, SALT_WEATHER), 10000));  stays(n, z) = mod(hash32(world_seed, z, n, SALT_STAY), 10000) < P_STAY_BP[z];  weather(n, z) = stays(n, z) ? raw(n−1, z) : raw(n, z)`

`PICK(W, x)` returns the first weather in the fixed order CLEAR, OVERCAST, FOG, RAIN whose cumulative weight is greater than x.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| n | int | any (slot 0 reads n = −1, which is well defined) | calculated (F1 `slot_index`) | Weather slot |
| z | int | valid zone ID | calculated (caller) | Zone |
| world_seed | int (32-bit) | any; server-secret | data file (server-only secret, per rules version) | Schedule seed |
| SALT_WEATHER, SALT_STAY | int constants | distinct | data file | Separates independent draws |
| WEIGHTS[z] | 4 × int (bp) | each 0–10,000, sum = 10,000; default CLEAR 5000, OVERCAST 2500, FOG 1000, RAIN 1500 | data file (zone table) | Chance of each weather |
| P_STAY_BP[z] | int (bp) | 0 to 9000; default 3500 | data file | Chance that a slot repeats the previous draw |
| weather(n, z) | enum | {CLEAR, OVERCAST, FOG, RAIN} | calculated | Slot weather |

**Output Range:** one of the four weathers. Because `raw` values are independent draws with the same weights, the long-run share of each weather equals `WEIGHTS` exactly, whatever `P_STAY_BP` is. `P_STAY_BP` only changes how often the weather repeats from one slot to the next. A weight of 0 means that weather never occurs in that zone.
**Example:** slot 159, zone 0. Suppose `hash32(seed, 0, 159, SALT_WEATHER) mod 10000 = 3172`; the cumulative weights are CLEAR < 5000, so `raw` = CLEAR. The stay roll is 6120 ≥ 3500, so the slot does not stay, and `weather(159, 0)` = **CLEAR**. (Real hash values come from the reference vectors; these are illustrative.)

### F4. Transition blend and effective weather

The weather_effective formula is defined as:

`blend_permille = min(1000, floordiv(slot_offset_ms × 1000, TRANSITION_MS));  weather_eff = (blend_permille ≥ 500) ? weather(n) : weather(n−1)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| slot_offset_ms | int (ms) | 0 to SLOT_MS−1 | calculated (F1) | Time into the slot |
| TRANSITION_MS | int (ms) | 10,000 to 180,000; default 60,000 | data file | Blend duration |
| blend_permille | int (‰) | 0 to 1000 | calculated | Visual blend from the previous weather to the new one |
| weather_eff | enum | four weathers | calculated | Weather used by every gameplay output |

**Output Range:** `blend_permille` is clamped to 1000. The gameplay switch happens at exactly 500‰ (30 s into the slot by default).
**Example:** `slot_offset_ms` = 410,000 → blend = min(1000, 6,833) = 1000 → effective = `weather(159)` = CLEAR. At `slot_offset_ms` = 29,999 the blend is 499 (the previous weather counts); at 30,000 it is 500 (the new weather counts).

### F5. Light condition

The light_condition formula is defined as:

`condition = CONDITION_MATRIX[band][weather_eff]` (outdoor zones);  `condition = ZONE_FIXED_CONDITION[z]` (interiors)

| band \ weather | CLEAR | OVERCAST | FOG | RAIN |
|---|---|---|---|---|
| BLUE_AM | BLUE_HOUR | BLUE_HOUR | BLUE_HOUR | RAIN |
| DAWN | DAWN | OVERCAST_FOG | DAWN | RAIN |
| DAY | MIDDAY | OVERCAST_FOG | OVERCAST_FOG | RAIN |
| GOLDEN | GOLDEN_HOUR | OVERCAST_FOG | OVERCAST_FOG | RAIN |
| BLUE_PM | BLUE_HOUR | BLUE_HOUR | BLUE_HOUR | RAIN |
| NIGHT | NIGHT | NIGHT | NIGHT | NIGHT |

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| band | enum | 6 bands | calculated (F1) | Time-of-day band |
| weather_eff | enum | 4 weathers | calculated (F4) | Effective weather |
| CONDITION_MATRIX | 6 × 4 table | values from the 7 conditions | data file | Mapping, matching art bible §2.2 |
| condition | enum | {DAWN, MIDDAY, GOLDEN_HOUR, BLUE_HOUR, NIGHT, OVERCAST_FOG, RAIN} | calculated | Light preset and scoring condition |

**Output Range:** exactly one of the seven art-bible conditions. Fog at dawn stays `DAWN`, because the art bible describes dawn as *"gentle, pastel, misty"*. Rain or cloud at night stays `NIGHT`; the client may show wet surfaces there as a visual variant.
**Example:** band GOLDEN, weather CLEAR → **GOLDEN_HOUR**. If the slot had been OVERCAST, the result would be OVERCAST_FOG: golden hour is lost, which is the stake the weather adds.

### F6. Points to tier

The points_to_tier formula is defined as:

`points_to_tier(x, T) = the highest-ranked tier t with T[t] ≤ x`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| x | int | 0 to 100 | calculated (F7 `LQ` or F10 `WMP`) | Points to band |
| T | map tier ID → int | T[C] = 0; strictly increasing with rank; light default C 0, B 30, A 55, S 75, SS 88, SSS 96; moment default C 0, B 30, A 55, S 75, SS 88, SSS 96 | data file (`LIGHT_T`, `MOMENT_T`) | Minimum points per tier |
| result | tier ID | C to SSS | calculated | Ladder ID (never a rank) |

**Output Range:** always a valid ladder ID, and never below C because T[C] = 0. A table that is not strictly increasing, or has no C key, fails at load.
**Example:** x = 75 with the light table → S (75 ≥ 75; 75 < 88). x = 74 → A.

### F7. Light quality and light tier

The light_tier formula is defined as:

`LQ_base = BASE[condition] + floordiv(SPAN[condition] × peak_permille, 1000);  LQ_event = event_active ? EBASE[e] + floordiv(ESPAN[e] × event_peak_permille, 1000) : 0;  LQ = clamp(max(LQ_base, LQ_event) + ZONE_MOD[z][condition], 0, 100);  light_tier = clamp_to_enabled(points_to_tier(LQ, LIGHT_T))`

| condition | BASE | SPAN | LQ range (no event) | Tier range (no event, uncapped) |
|---|---|---|---|---|
| MIDDAY | 30 | 0 | 30 | B |
| NIGHT | 25 | 10 | 25–35 | C–B |
| OVERCAST_FOG | 40 | 5 | 40–45 | B |
| RAIN | 35 | 10 | 35–45 | B |
| BLUE_HOUR | 50 | 15 | 50–65 | B–A |
| DAWN | 50 | 15 | 50–65 | B–A |
| GOLDEN_HOUR | 60 | 20 | 60–80 | A–S |

| event | EBASE | ESPAN | LQ_event range | Tier range |
|---|---|---|---|---|
| SUNBEAM | 72 | 20 | 72–92 | A–SS |
| LUMEN_DUSK | 78 | 20 | 78–98 | S–SSS |
| AURORA | 80 | 20 | 80–100 | S–SSS |

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| condition | enum | 7 conditions | calculated (F5) | Light condition |
| peak_permille | int (‰) | 0–1000 | calculated (F2 over the band) | Closeness to the band centre |
| BASE, SPAN | int per condition | 0–100 | data file | Base light quality and the bonus at the peak |
| event_active, e | bool, event ID | — | calculated (F8, F9) | Whether an event is ACTIVE, and which |
| event_peak_permille | int (‰) | 0–1000 | calculated (F9) | Closeness to the event's centre |
| EBASE, ESPAN | int per event | 0–100 | data file | Event light quality |
| ZONE_MOD[z][c] | int | −20 to +10; MVP all 0 | data file (zone table) | Place modifier (for example a canopy that softens noon) |
| LIGHT_T | threshold table | see F6 | data file | Light thresholds |
| enabled_cap | tier ID | MVP "A" | data file (Rarity Tier Ladder config) | Producible cap |
| LQ | int | 0–100 | calculated | Light quality; Photo Scoring may read it |
| light_tier | tier ID | C to `enabled_cap` | calculated | The capture rule's "Light tier" |

**Output Range:** `LQ` is clamped to [0, 100]. `light_tier` lies in C..`enabled_cap`. SS needs `LQ` ≥ 88 and SSS needs ≥ 96, and both are reachable only during an ACTIVE event. With the defaults and no cap, the share of world time per tier is approximately: C 14.3%, B 71.6%, A 12.7%, S 1.4%, plus event time (SS and SSS amount to a few tens of seconds per real day; see Tuning Knobs). The A share works out as follows: golden 11.1% × 50% clear × 75% of the band, + dawn 7.9% × 60% × 66.7%, + blue AM 3.2% × 85% × 66.7%, + blue PM 6.3% × 85% × 66.7%.
**Example (capped, MVP):** GOLDEN_HOUR, peak 762, no event, zone 0: `LQ_base` = 60 + floordiv(20 × 762, 1000) = 60 + 15 = 75 → points_to_tier = **S** → `clamp_to_enabled` with cap A → **A**. Per the Rarity Tier Ladder edge case, no message ever mentions the S that was clamped away.
**Example (event):** LUMEN_DUSK ACTIVE with event peak 607, during BLUE_HOUR band peak 834: `LQ_base` = 50 + floordiv(15 × 834, 1000) = 62; `LQ_event` = 78 + floordiv(20 × 607, 1000) = 90; `LQ` = max(62, 90) = 90 → **SS** (cap A → A).

### F8. Light event schedule

The event_schedule formula is defined as:

`rolled(e, z, d) = mod(hash32(world_seed, z, d, SALT_EVENT[e]), 10000) < CHANCE_BP[e][z];  free_ms = L_band(e) − build_ms[e] − active_ms[e] − fade_ms[e];  build_start(e, z, d) = d × DAY_MS + BAND_START[band(e)] + mod(hash32(world_seed, z, d, SALT_EVENT_T[e]), free_ms + 1);  scheduled(e, z, d) = rolled ∧ weather_eff ∈ ALLOWED_WEATHER[e] at every slot overlapping [build_start, build_start + build_ms + active_ms + fade_ms) ∧ no higher-priority event or operator event is scheduled in band(e)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| e | event ID | {SUNBEAM, LUMEN_DUSK, AURORA} (+ operator) | data file (event table, in priority order) | Event type |
| d | int | ≥ 0 | calculated (F1 `day_index`) | World day |
| CHANCE_BP[e][z] | int (bp) | 0–5000; default SUNBEAM 1500, LUMEN_DUSK 800, AURORA 500 | data file | Roll chance per zone per day |
| band(e) | enum | default SUNBEAM GOLDEN, LUMEN_DUSK BLUE_PM, AURORA NIGHT | data file | Band the event lives in |
| ALLOWED_WEATHER[e] | set | default SUNBEAM {OVERCAST}, LUMEN_DUSK {CLEAR}, AURORA {CLEAR} | data file | Weather required throughout |
| build_ms, active_ms, fade_ms | int (ms) | SUNBEAM 30,000/120,000/30,000; LUMEN_DUSK 20,000/90,000/20,000; AURORA 60,000/180,000/60,000 | data file | Lifecycle durations |
| L_band(e) | int (ms) | from the band table | data file | Length of the event's band |
| free_ms | int (ms) | must be ≥ 0, otherwise the event table fails at load | calculated | Room to place the event in its band |
| build_start | int (ms, world time in the zone's frame) | inside band(e) of day d | calculated | When BUILDING begins |
| scheduled | bool | — | calculated | Whether the event happens |

**Output Range:** zero or one occurrence per event type per zone per day, always fully inside its band, never overlapping another event in the same zone. The expected number per real day (22.86 world days) is `22.86 × CHANCE × P(weather holds)`. Defaults: SUNBEAM ≈ 22.86 × 0.15 × 0.25 ≈ 0.86, LUMEN_DUSK ≈ 0.91 at most (it needs two consecutive clear slots, so the true value is a little lower), AURORA ≈ 0.57 at most.
**Example:** day 26, zone 0, LUMEN_DUSK. The roll value 412 < 800, so it is rolled. `free_ms` = 240,000 − 130,000 = 110,000. The offset roll gives 57,300, so `build_start` = 98,280,000 + 2,460,000 + 57,300 = 100,797,300 (phase 2,517,300). The lifecycle runs to phase 2,647,300 and overlaps slots 3 and 4 (the boundary is at phase 2,520,000). Both are CLEAR, so the event is **scheduled**: ACTIVE from phase 2,537,300 to 2,627,300.

### F9. Event phase

The event_phase formula is defined as:

`event_active = active_start ≤ t_z < active_start + active_ms;  event_peak_permille = peak_permille(t_z − active_start, active_ms)`, where `active_start = build_start + build_ms`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t_z | int (ms) | ≥ 0 | calculated (F1) | Zone world time |
| active_start | int (ms) | — | calculated (F8) | Start of ACTIVE |
| active_ms | int (ms) | > 0 | data file | ACTIVE length |
| event_peak_permille | int (‰) | 0–1000 | calculated (F2) | Closeness to the event centre |

**Output Range:** 0–1000 while ACTIVE; undefined (the event is not active) outside it.
**Example:** capture at phase 2,600,000: offset = 2,600,000 − 2,537,300 = 62,700; |125,400 − 90,000| = 35,400; floordiv(35,400,000, 90,000) = 393; event peak = **607**.

### F10. World moment

The world_moment formula is defined as:

`WMP = clamp(max over active windows w of (RARITY[w] + floordiv(SHARP[w] × peak(w), 1000)), 0, 100);  world_moment_tier = clamp_to_enabled(points_to_tier(WMP, MOMENT_T))`

Active windows at any instant: the band window (always), the weather window for `weather_eff`, the **clearing** window (if open, F4 / States), and the ACTIVE event (if any).

| window | RARITY | SHARP | peak(w) from |
|---|---|---|---|
| band DAY / NIGHT | 10 / 15 | 0 / 0 | band (F2) |
| band DAWN / GOLDEN | 40 / 40 | 20 / 20 | band (F2) |
| band BLUE_AM / BLUE_PM | 45 / 45 | 20 / 20 | band (F2) |
| weather CLEAR / OVERCAST | 0 / 10 | 0 / 0 | slot (F2 over SLOT_MS) |
| weather FOG / RAIN | 30 / 30 | 10 / 10 | slot (F2 over SLOT_MS) |
| CLEARING | 55 | 25 | F2 over CLEARING_MS |
| event SUNBEAM / LUMEN_DUSK / AURORA | 70 / 75 / 75 | 25 / 25 / 25 | F9 |

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| w | window | active windows (1–4 at once) | calculated | A transient world window |
| RARITY[w], SHARP[w] | int | 0–100 | data file | How rare or brief the window is; the bonus at its peak |
| peak(w) | int (‰) | 0–1000 | calculated (F2, F9) | Closeness to the window centre |
| MOMENT_T | threshold table | see F6 | data file | Moment thresholds |
| WMP | int | 0–100 | calculated | World-moment points |
| world_moment_tier | tier ID | C to `enabled_cap` | calculated | The world part of the capture rule's "Moment tier" |

**Output Range:** `WMP` lies in [0, 100] (clamped, and `max` over windows never errors because the band window is always present). Without events the best world moment is S (a clearing at its peak, 80). SS and SSS need an event near its peak.
**Example:** the golden capture from F1/F7: the band window gives 40 + floordiv(20 × 762, 1000) = 55; the CLEAR weather window gives 0; no clearing (410 s into the slot is past 90 s); no event. WMP = 55 → **A** (cap A → A). In the LUMEN_DUSK example: 75 + floordiv(25 × 607, 1000) = 90 → **SS** (cap A → A).

### F11. Key light

The key_light formula is defined as:

`v(x) = v0 + floordiv((v1 − v0) × (x − x0), x1 − x0)` for consecutive keyframes (x0, v0), (x1, v1) with x0 ≤ x < x1, applied separately to elevation and azimuth; `key_source = SUN` for phase < 2,700,000, otherwise `MOON`

Default keyframes (phase s → elevation decideg, azimuth decideg): sun (0, −80, 700), (120, −20, 800), (420, 120, 950), (1230, 650, 1800), (2040, 150, 2650), (2460, −20, 2850), (2700, −80, 2950); moon (2700, 100, 1100), (3240, 350, 1800), (3780, 100, 2500). Below the horizon (elevation < 0), the light renders as the weak ambient the art bible specifies for blue hour.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| x | int (ms) | 0 to DAY_MS−1 | calculated (F1 `phase_ms`) | Day phase |
| (x0, v0), (x1, v1) | int pairs | keyframes sorted by x, covering [0, DAY_MS) | data file (key-light table) | Bracketing keyframes |
| elev_deci | int (0.1°) | −900 to 900 | calculated | Key-light elevation |
| azim_deci | int (0.1°) | 0 to 3599 (wrapped with `mod`) | calculated | Key-light azimuth, clockwise from north |
| key_source | enum | {SUN, MOON} | calculated | Which body the single shadow light represents |

**Output Range:** elevation stays between the bracketing keyframe values (linear interpolation never overshoots). The azimuth is wrapped to [0, 3600).
**Example:** phase 2,300 s lies between (2040, 150, 2650) and (2460, −20, 2850). Elevation = 150 + floordiv(−170 × 260, 420) = 150 + floordiv(−44,200, 420) = 150 − 106 = **44** (4.4°). Floor matters here: truncation would give −105 and 45. Azimuth = 2650 + floordiv(200 × 260, 420) = 2650 + 123 = **2773** (277.3°).

### F12. Scene exposure value

The scene_ev formula is defined as:

`scene_ev_deci = clamp(EV_KEY(phase_ms) + EV_WEATHER[weather_eff] + (event_active ? EV_EVENT[e] : 0) + EV_ZONE[z], EV_MIN, EV_MAX)`

`EV_KEY` uses F11 interpolation over the default keyframes (phase s → EV100 ×10): (0, 40), (120, 80), (420, 120), (1230, 150), (2040, 130), (2460, 90), (2700, 40), (2760, 10), (3720, 10), (3780, 40).

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| EV_KEY | int (0.1 EV) | −40 to 160 | data file (EV keyframes) + F11 interpolation | Clear-sky brightness over the day |
| EV_WEATHER | int (0.1 EV) | default CLEAR 0, OVERCAST −30, FOG −20, RAIN −40 | data file | Weather darkening |
| EV_EVENT | int (0.1 EV) | default SUNBEAM +10, LUMEN_DUSK 0, AURORA +5 | data file | Event brightening |
| EV_ZONE | int (0.1 EV) | −30 to +10; MVP 0 | data file | Place modifier |
| EV_MIN, EV_MAX | int | default −40, 160 | data file | Clamp |
| scene_ev_deci | int (0.1 EV at ISO 100) | −40 to 160 | calculated | Brightness that Camera Model exposes against |

**Output Range:** clamped to [EV_MIN, EV_MAX] = [−4.0, 16.0] EV. With the defaults, clear midday is about EV 15 ("sunny 16") and night is EV 1, so night needs long exposures, which is the Astro role's niche.
**Example:** phase 2,300 s between (2040, 130) and (2460, 90): 130 + floordiv(−40 × 260, 420) = 130 + floordiv(−10,400, 420) = 130 − 25 = **105** (EV 10.5), CLEAR, no event → 105.

### F13. Capture time (from Network)

The capture_time formula is defined as:

`capture_ms = tick_to_ms(capture_tick)`, where `capture_tick` is resolved by Network Transport & Server Authority, Formula F8 (lag-compensated moment: the client's `view_tick` is used only within ±`VIEW_TOLERANCE_MS` of the server's estimate, and rewind never exceeds `MAX_REWIND_MS`).

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| capture_tick | int (session tick) | `[recv_tick − MAX_REWIND_MS × TICK_HZ / 1000, recv_tick]` | calculated (Network F8, server) | Lag-compensated tick of the shot |
| tick_to_ms | function | — | calculated (Network session clock) | Converts a session tick to server UTC ms |
| capture_ms | int (ms) | ≥ `WORLD_EPOCH_MS` | calculated (server) | The time this system evaluates the WorldState at |

**Output Range:** server UTC ms, at most `MAX_REWIND_MS` (default 400 ms, about 7 world seconds) before receipt. This system has **no acceptance window of its own** and never reads a client-sent time directly (decided 2026-11-03: Network owns capture-time authority).
**Example:** recv at server ms 100,580,900; Network F8 resolves a 300 ms rewind → `capture_ms = 100,580,600`; the WorldState is computed at that instant.

## Edge Cases

- **If a timestamp falls exactly on a band, slot or event boundary**: the half-open rule applies: the instant belongs to the *later* band, slot or state (phase 2,040,000 is GOLDEN, and 2,039,999 is DAY).
- **If `t_ms` is before `WORLD_EPOCH_MS`**: F1 returns `ERR_BEFORE_EPOCH`; a capture with that time is rejected and logged; the feed never shows a pre-epoch state (the server refuses to start if its clock is before the epoch of the active version).
- **If the client's claimed view tick is outside Network's tolerance**: Network clamps it to its own estimate (Network F8) and logs it; this system evaluates the WorldState at the resulting time. There is no separate world-side rejection.
- **If the connection drops between shutter and receipt**: the capture reaches the server late (or never) and is outside Network's rewind window; Network discards the shot (see Network Edge Cases). Offline capture is not supported in MVP (Open Question 3).
- **If a capture lands during a weather transition**: gameplay uses `weather_eff` (F4). At blend 499‰ it is the previous weather, and at 500‰ the new one. The snapshot stores both weathers and the blend, so the re-render shows the exact mix the player saw.
- **If a capture lands in the visual band crossfade**: the score uses the discrete band at `capture_ms`. The re-render recomputes the same crossfade from `phase_ms` and the public band table, so the image matches.
- **If an event's required weather would not hold for its whole lifecycle**: the event is not scheduled that day (F8). It is not rerolled or moved, so an event can never be cut off mid-way by a slot change.
- **If two seeded events (or a seeded and an operator event) want the same band in the same zone and day**: the operator event wins, then the higher-priority seeded event; the loser does not happen that day.
- **If an event's `build + active + fade` is longer than its band**: the event table fails validation at load and the server does not start with that rules version.
- **If the band durations do not add up to `DAY_MS`, `SLOT_MS` does not divide `DAY_MS`, or a zone's weather weights do not add up to 10,000**: the rules version fails at load with an error naming the table; it is never auto-corrected.
- **If a zone gives a weather weight 0 and a subject window requires that weather**: Subject & Spirit Behaviour's content validation calls `can_occur(z, predicate)`, gets false and fails the build.
- **If a light or moment tier would exceed `enabled_cap`**: it is clamped with `clamp_to_enabled`; no UI, log shown to players or audio cue reveals the unclamped tier (Rarity Tier Ladder edge case on near-miss messaging). The internal `LQ` and `WMP` points are server-side values and are not shown as tier names.
- **If `LQ` or `WMP` would leave 0–100** (for example a −20 zone modifier on NIGHT gives 5 − 20 = −15): it is clamped to the range, so −15 becomes 0 → C.
- **If the server's clock steps backwards (NTP correction) or two server processes disagree slightly**: scoring uses the `capture_ms` resolved from Network F8, so stored results do not change. Hosts must keep clock skew below 100 ms (Network ADR). If a process detects a backward step larger than 250 ms, it logs a clock alarm.
- **If a new rules version is published with `effective_from_ms` less than `FORECAST_HORIZON_MS` in the future**: it is rejected at publish time, so forecasts and event notices already sent never become false.
- **If an old photo is re-scored or disputed after a rules change**: the server loads the version that was active at `capture_ms` and recomputes with it. If the result differs from the stored snapshot, it raises a determinism alarm and keeps the stored snapshot (the scoring freeze is recorded in Photo Recipe).
- **If the world seed leaks**: anyone could compute every future event. Response: publish a new rules version with a new seed (effective after the forecast horizon). Past photos are unaffected because they keep their version.
- **If the server is down for hours**: world time keeps flowing because it is a function of UTC. Events scheduled during the downtime are missed, with no make-up; on restart the feed resumes at the current state.
- **If a player sits in a menu or in the darkroom**: the world clock does not pause. A forecast shown before the menu stays valid because it is deterministic.
- **If a capture's `zone_id` disagrees with the server's own record of the player's position**: the server uses its own zone (Player Movement), logs the mismatch, and computes the WorldState for that zone.
- **If a zone is an interior (`world_light = false`)**: rule 15 applies; no events occur; band and weather are still reported for flavour UI but do not affect light outputs.
- **If slot 0 needs `raw(−1)`**: `hash32` accepts the signed index −1 and returns a defined value, so `weather(0)` never needs a special case.
- **If the Capture Encounter wants "clouds parting" or "the sun sinking"**: the encounter cannot change world light locally, because that would break the shared world and re-render. Subject & Spirit Behaviour schedules the encounter to start inside a matching world window (for example 60 s before a GOLDEN slot changes from OVERCAST to CLEAR, found with `find_next_window`).
- **If two players in the same zone shoot at the same millisecond**: they get identical WorldStates; their light tiers are the same and differ only through their own subject, skill and gear.

## Dependencies

**Upstream (this system depends on):**

| System | Hard / soft | Interface | Status |
|---|---|---|---|
| Rarity Tier Ladder | Hard | tier IDs; `clamp_to_enabled`; `tier_max`, `tier_min`, `tier_step` (for Subject's bounded moment combination) | In Design (`rarity-tier-ladder.md` already lists this system as a downstream dependent) |

Runtime inputs (`zone_id`, receipt time `r`, the clock-sync offset) are passed in as parameters by their owners. They are not structural dependencies, so the Foundation layering in the systems index still holds. Note: row 2 of `systems-index.md` currently lists "Depends On: —". It should list Rarity Tier Ladder (not edited here; see Decisions to confirm, D17).

**Downstream (systems that depend on this one):**

| System | Hard / soft | Interface | GDD status |
|---|---|---|---|
| Subject & Spirit Behaviour | Hard | WorldState, windows, `find_next_window`, `can_occur`, `world_moment_tier` | Not started |
| Camera Model | Hard | `scene_ev_deci`, condition, key light | Not started |
| Photo Recipe & Re-render | Hard | WorldSnapshot content, `world_rules_version` | Not started |
| Photo Scoring | Hard | `LQ`, condition, key light, event | Not started |
| Capture Tier Resolution | Hard | `light_tier` (and the moment tier through Subject) | Not started |
| Network Transport & Server Authority | Hard | world feed content; F13 acceptance rule | Not started |
| Expedition Rooms | Soft | the shared clock | Not started |
| Audio: SFX & Ambience | Soft | condition, weather, blend, event state | Not started |
| Viewfinder HUD | Soft | clock, weather, forecast, notices | Not started |
| Daily Themes, Commission Board | Soft | condition and band in the snapshot | Not started |
| Server-Wide Events & Timed Races | Soft | operator event rows | Not started |
| Zone Access & Travel | Soft | zone offset and weights | Not started |
| Economy Telemetry | Soft | tier time share, event counts | Not started |

Bidirectional note: each downstream GDD must list "depends on World Time, Weather & Light" when authored.

## Tuning Knobs

| Knob | Default | Safe range | Affects | Too low / too high |
|---|---|---|---|---|
| `DAY_MS` | 3,780,000 (63 min) | 1,800,000 – 7,200,000; prefer values where 7 × 86,400,000 / DAY_MS is an integer (so the pattern repeats weekly) and 86,400,000 / DAY_MS is not | Pace; how often each band recurs | Too short: golden hour flashes by and the world feels frantic. Too long: players who play at fixed hours rarely see some bands. A value dividing 24 h evenly gives a fixed-hour player the same band every day. |
| Band durations | see Core Rule 2 | GOLDEN 240–600 s; BLUE 90–300 s; NIGHT ≤ 35% of the day | Window length, A-light share | Short windows make planning stressful; long ones make good light common and devalue it. |
| `SLOT_MS` | 630,000 | must divide `DAY_MS`; 315,000 – 1,260,000 | Weather volatility; whether a band spans two slots | Too short: the sky flickers. Too long: a bad slot kills a whole evening. |
| `WEIGHTS[z]` | 5000/2500/1000/1500 | each 0–8000 | Weather mix; the golden-hour clear chance; event eligibility | Too little CLEAR: golden hour and A light become rare. Too little OVERCAST: SUNBEAM vanishes. |
| `P_STAY_BP` | 3500 | 0 – 7000 | Continuity of weather | 0 means independent slots (jumpy); high values produce long streaks, and players stuck in a streak of rain get frustrated. |
| `TRANSITION_MS` | 60,000 | 10,000 – 180,000 | Weather blend speed | Too fast looks like a pop; too slow muddies what weather it "is". |
| `CLEARING_MS`, clearing RARITY/SHARP | 90,000; 55/25 | 30,000–180,000; RARITY 40–65 | How valuable a clearing is | High values make "wait for the rain to stop" the dominant strategy. |
| `BASE`, `SPAN` per condition | F7 table | 0–80 each; GOLDEN_HOUR BASE + SPAN must stay below `LIGHT_T[SS]` | Light tier per condition | Raising MIDDAY to A or more removes the "noon is plain" lesson (art bible). |
| `LIGHT_T`, `MOMENT_T` | 0/30/55/75/88/96 | strictly increasing; SS ≥ 85 | Tier bands | Lower SS/SSS thresholds let ordinary golden hour reach SS, which breaks "SS/SSS only in short windows". |
| `EBASE`, `ESPAN` per event | F7 table | EBASE 65–85; EBASE + ESPAN ≤ 100 | Top-tier light availability | If EBASE + ESPAN < 96, SSS light can never occur (dead top end). |
| `CHANCE_BP[e]` | 1500 / 800 / 500 | 100 – 5000 | Events per real day | Too low: the dead top end. Too high: events stop feeling rare. Target (proposal): 0.5–1.5 of each per zone per real day, to confirm with an Economy Telemetry simulation. |
| Event `build/active/fade` | F8 table | ACTIVE 45–300 s | How long the top window is open | SSS light time per occurrence = ACTIVE × (EBASE + ESPAN − 96)/ESPAN. With the defaults: LUMEN 9 s, AURORA 36 s. That is very tight; tune together with the Capture odds. |
| `EVENT_NOTICE_MS` | 600,000 | 0 – 1,800,000 | Planning time | 0 makes events pure luck of presence (anti-Pillar 1); too long lets everyone camp, so the event becomes crowded and first-claim races get harsh. |
| `FORECAST_SLOTS` | 6 | 2 – 12 | Planning horizon | Fewer means less planning; more reveals too much and makes surprise rare. |
| `ZONE_MOD`, `EV_ZONE`, `zone_phase_offset_ms` | 0 | see F7 / F12 / F1 | Place identity | Large modifiers make one zone strictly better (a grind spot). |
| `BAND_XFADE_MS` | 20,000 | 0 – 60,000 | Visual smoothness only | Not a gameplay knob; any value is safe for scoring. |

**Not knobs:** the condition names (art bible identity), the hash algorithm and salts once released (changing them is a new rules version), and integer-only arithmetic.

## Visual/Audio Requirements

- **Presets.** One preset per condition from art bible §2.2 (sun colour, angle and intensity, ambient tint, sky band, contrast), applied to the single shadow-casting key light and the environment. The key light's angles come from F11 and its intensity and colour from the preset. *UNVERIFIED: `DirectionalLight3D` shadow quality and cost on the Compatibility renderer, and whether a sky gradient can be driven per frame through `WorldEnvironment` on Web; neither is covered by `docs/engine-reference/godot/modules/rendering.md`.*
- **Smooth time.** Visuals interpolate continuously (key light, sky band, EV-driven exposure in the viewfinder). Rotating the shadow light every frame may cause visible shadow swimming (*UNVERIFIED*); if it does, the technical-artist may step the rotation in small increments. This is a visual-only choice, and the snapshot angles stay exact.
- **Weather visuals.** OVERCAST: flat sky, low contrast. FOG: depth fog in the sky colour (art bible §2.2 says to assume no volumetric fog; Compatibility fog modes are *UNVERIFIED*; the prototype observed that a custom spatial shader can read `hint_depth_texture` on Compatibility/Web, so a shader fog fallback exists). RAIN: lower surface roughness, cheap streak particles at most one alpha layer (art bible §8.5), and particles seeded from `capture_ms` and the slot so re-renders match (P4).
- **Events must look unlike any ordinary condition.** SUNBEAM: visible rays with motes; LUMEN_DUSK: a cyan (Lumen) dusk; AURORA: violet bands (art bible §2.1 rare-window rule). BUILDING shows a readable precursor (rays thinning through cloud, a cyan tint creeping into the horizon), and FADING reverses it. The world desaturates slightly except the event light (art bible §2.1).
- **Wind.** Direction per slot is `mod(hash32(seed, z, n, SALT_WIND), 360)`; strength comes from a per-weather table. Grass and water shaders take their time from world time, never a free-running timer (art bible §8.5).
- **Audio** (owned by Audio: SFX & Ambience): ambience beds per condition, crossfaded with `blend_permille`; a rain layer; one distinct, gentle cue when an event enters BUILDING, never an alarm (Pillar 3). Rain and event audio need captions or visual equivalents for players who cannot hear them (Settings & Accessibility).
- **Accessibility.** Event light must not flash. Any brightness pulse must stay within flash-safety limits, and the reduce-flashing option (art bible §2.1) also softens event shimmer.

## Game Feel

- **Time is felt, not watched.** At the default pace the sun's azimuth moves about 0.3° per real second at midday. Shadows visibly creep over a minute, but nothing jumps. Golden hour (7 min) is long enough to compose, short enough to feel precious.
- **Readable peaks.** Light quality rises and falls linearly with the band peak, so "the best moment is the middle of golden hour" is learnable. The art bible requires the difference between C and S light to be visible before the score says so.
- **Build-up before reward.** Every event has a BUILDING phase (20–60 s) with a visual and audio precursor, so the player's reaction ("it's starting!") comes before the tier-relevant ACTIVE phase. That gap is the window in which skill works.
- **No dice at the shutter.** For a given place and time the world gives the same light to everyone. The only roll in the capture rule belongs to Capture Tier Resolution.
- **Forecast anticipation.** Seeing "evening slot: overcast" should prompt a decision (stay for a possible sunbeam, or go elsewhere), not resignation. Playtests should check that players make that choice (Open Question 7).

## UI Requirements

- **Viewfinder HUD / world HUD:** the display clock (non-linear, from the band table), a band glyph, the current weather icon, and a subtle indicator of how far through the current band you are (no numbers, no tier letter, so the naked eye stays primary; art bible §2.2).
- **Forecast panel:** the next 6 slots (one world day) for the current zone, with weather icons and band markers. Accessible from the HUD or map, not the viewfinder.
- **Event notice:** a calm toast plus a map marker naming the zone and band ("the sky feels strange over the harbour this evening"), shown `EVENT_NOTICE_MS` before build-up. The wording follows the Rarity Tier Ladder's language rule (no loot-speak, no tier names).
- **Darkroom breakdown:** shows the condition name and, after the score, the light tier and world-moment contribution as ladder badges (owned by Darkroom & Gallery UI). It never shows a tier above `enabled_cap` and never says what a clamp removed.
- **Rejection message** for F13: a gentle, non-blaming message that the shot did not reach the darkroom in time (wording owned by UI and Network).
- **Colour is never the only cue:** weather icons and band glyphs need distinct shapes (art bible §4.7).

> 📌 **UX Flag — World Time, Weather & Light**: the HUD clock, forecast panel and event notice need `/ux-design` specs (HUD and map) before UI epics are written.

## Cross-References

| Referenced document | What is used | Where |
|---|---|---|
| `design/gdd/game-concept.md`: Pillars, Capture rule, Photo evaluation, Online play, Technical considerations | "Moment tier" and "Light tier" in the capture rule; "Top-tier subjects appear only in short windows (a particular weather, hour or place)"; Light = "direction and quality", Moment = "decisive instant"; server-wide events; the recipe stores time of day; the server recalculates | Overview, Core Rules 6–8, 12–14 |
| `design/gdd/systems-index.md`: row 2, Foundation layer, Expedition Rooms, Server-Wide Events, High-Risk (Photo Recipe) | "must be deterministic and reproducible on the server"; freeze the score per version | Overview, Core Rules 10, 13; Dependencies |
| `design/gdd/rarity-tier-ladder.md`: Core Rules 2, 7, 10; Formulas `clamp_to_enabled`, `tier_max`; edge case on near-miss messaging; interactions table | IDs only, never rank; `enabled_cap = "A"`; producers clamp; this system owns light and moment tier outputs | Core Rules 6, 8; F6, F7, F10; Edge Cases |
| `design/art/art-bible.md`: P3, P4, §2.1 (rare window, encounter), §2.2 (seven conditions, one sun, fog VERIFY), §4.7, §8.5 | Condition list and looks; re-render rule; world-clock-driven shaders; event look rule | Core Rules 5, 9, 14; Visual/Audio |
| `docs/architecture/research-web-networking.md` §4.1, §5.1, §5.4, §8 risk 1 | Analytic, render-free scoring; WASM vs native float risk; recipe < 512 bytes | Core Rules 10, 12, 14 |
| `prototypes/aperture-concept/README.md` Findings | Native DoF unsupported on Compatibility; a custom depth-reading shader works on Web (observed); geometry-only scoring built but not yet playtested | Visual/Audio (fog fallback); Open Questions |
| `docs/engine-reference/godot/modules/rendering.md` | Compatibility = OpenGL 3.3 / WebGL 2; no lighting or fog specifics, so those claims are UNVERIFIED | Visual/Audio |

## Acceptance Criteria

Tags: **[Logic]** automated gdUnit4 unit test (suggested name) · **[Integration]** integration test or documented playtest · **[UI]** retained screenshot in `production/qa/evidence/`. All Logic tests use a fixture rules version with a fixed test seed and the default tables unless stated. *(provisional)* marks criteria that depend on a system not yet designed.

**A. Clock and bands (Core Rules 1–3; F1)**

1. [Logic] **GIVEN** `t_w` = 100,580,000 and zone offset 0, **WHEN** the world clock runs, **THEN** `day_index` = 26, `phase_ms` = 2,300,000, band = GOLDEN, `band_offset_ms` = 260,000, `slot_index` = 159, `slot_offset_ms` = 410,000. `test_world_clock_known_timestamp_returns_expected_fields`
2. [Logic] **GIVEN** phases 2,039,999 and 2,040,000, **WHEN** the band is resolved, **THEN** they return DAY and GOLDEN respectively; phase 3,779,999 is NIGHT and 3,780,000 is BLUE_AM of the next day. `test_band_boundary_half_open_assigns_later_band`
3. [Logic] **GIVEN** `t_ms` = `WORLD_EPOCH_MS` − 1, **WHEN** the world clock runs, **THEN** it returns `ERR_BEFORE_EPOCH`. `test_world_clock_before_epoch_returns_error`
4. [Logic] **GIVEN** a band table summing to 3,779,000, or `SLOT_MS` = 640,000, **WHEN** the rules version loads, **THEN** loading fails with an error naming the table. `test_rules_version_invalid_band_or_slot_fails_load`
5. [Logic] **GIVEN** zone A offset 0 and zone B offset 420,000, **WHEN** both are queried at phase 2,000,000, **THEN** A is DAY and B is GOLDEN. `test_zone_phase_offset_shifts_band`
6. [Integration] **GIVEN** two server processes with synced clocks, **WHEN** each computes the WorldState for the same zone at the same `t_ms`, **THEN** the serialised states are byte-identical; **AND** pausing the client menu for 60 s advances `phase_ms` by 60,000.
7. [Logic] **GIVEN** GOLDEN `band_offset_ms` = 260,000, **WHEN** the display clock is computed, **THEN** it returns 18:25 (1050 + floordiv(260,000 × 90, 420,000) = 1105 minutes). `test_display_clock_golden_offset_returns_1825`

**B. Band peak (F2)**

8. [Logic] **GIVEN** L = 420,000, **WHEN** peak is computed at o = 0, 210,000, 260,000 and 419,999, **THEN** it returns 0, 1000, 762 and 0 respectively, and never a value outside 0–1000 for any o in [0, L). `test_band_peak_edges_centre_and_example`

**C. Weather (Core Rule 4; F3, F4)**

9. [Logic] **GIVEN** the fixture seed, **WHEN** `weather(n, 0)` is computed for n = −1..9,999 twice in separate runs, **THEN** both sequences are identical. `test_weather_same_inputs_same_sequence`
10. [Logic] **GIVEN** the fixture seed and default weights, **WHEN** `weather(n, 0)` is computed for n = 0..99,999, **THEN** each weather's share is within ±1.0 percentage point of its weight, and with `P_STAY_BP` = 9000 the shares still stay within ±1.5 points. `test_weather_marginal_share_matches_weights`
11. [Logic] **GIVEN** a slot whose stay roll is below `P_STAY_BP`, **WHEN** its weather is computed, **THEN** it equals `raw(n−1)`, not `raw(n)`. `test_weather_stay_copies_previous_raw_draw`
12. [Logic] **GIVEN** `weather(n−1)` = RAIN and `weather(n)` = CLEAR, **WHEN** `slot_offset_ms` = 29,999 and 30,000, **THEN** blend is 499 and 500 and the effective weather is RAIN and CLEAR respectively. `test_weather_blend_switches_at_500_permille`
13. [Logic] **GIVEN** zone weights summing to 9,999, **WHEN** the rules version loads, **THEN** loading fails naming the zone. `test_weather_weights_not_10000_fails_load`
14. [Logic] **GIVEN** the published `hash32` reference vectors, **WHEN** `hash32` runs on each input, including negative indices, **THEN** every output matches bit for bit. `test_hash32_matches_reference_vectors`

**D. Light condition (Core Rule 5; F5)**

15. [Logic] **WHEN** all 24 band × weather combinations are resolved, **THEN** each matches the F5 matrix, and every result is one of the seven art-bible conditions. `test_light_condition_matrix_all_cells`

**E. Points to tier and light tier (Core Rule 6; F6, F7)**

16. [Logic] **GIVEN** the default light thresholds, **WHEN** `points_to_tier` runs on 0, 29, 30, 74, 75, 87, 88, 95, 96, 100, **THEN** it returns C, C, B, A, S, S, SS, SS, SSS, SSS as ladder ID strings. `test_points_to_tier_threshold_boundaries`
17. [Logic] **GIVEN** a threshold table that is not strictly increasing or lacks C, **WHEN** it loads, **THEN** loading fails. `test_threshold_table_invalid_fails_load`
18. [Logic] **GIVEN** GOLDEN_HOUR, peak 762, no event, zone mod 0 and `enabled_cap` = "A", **WHEN** the light tier is computed, **THEN** `LQ` = 75 and `light_tier` = "A"; with a fixture cap of "SSS" it is "S". `test_light_tier_golden_example_clamped_to_cap`
19. [Logic] **GIVEN** NIGHT at peak 0 and a zone modifier of −20, **WHEN** `LQ` is computed, **THEN** it is 0 (clamped, not −15) and the tier is C. `test_light_quality_clamped_to_zero`
20. [Logic] **GIVEN** a fixture cap of "SSS" and no events, **WHEN** the light tier is sampled every 1,000 ms over one world day for every weather, **THEN** no sample is SS or SSS. `test_light_tier_without_event_never_exceeds_s`
21. [Logic] **GIVEN** the default tables, fixture seed and a cap of "SSS", **WHEN** light tiers are sampled every 1,000 ms over 7 real days in zone 0 with events disabled, **THEN** time shares are C 14.3%, B 71.6%, A 12.7%, S 1.4%, each within ±2.0 points. `test_light_tier_time_share_matches_spec`

**F. Light events (Core Rule 7; F8, F9)**

22. [Logic] **GIVEN** the fixture seed, **WHEN** the event schedule for zone 0, days 0..999 is computed twice, **THEN** the results are identical, every event lies fully inside its band, and no two events in the zone overlap. `test_event_schedule_deterministic_and_within_band`
23. [Logic] **GIVEN** an event whose roll passes but whose lifecycle overlaps a slot with disallowed weather, **WHEN** it is scheduled, **THEN** `scheduled` = false and no other start time is tried. `test_event_ineligible_weather_not_scheduled`
24. [Logic] **GIVEN** an event with build + active + fade larger than its band, **WHEN** the event table loads, **THEN** loading fails. `test_event_longer_than_band_fails_load`
25. [Logic] **GIVEN** two events assigned to the same band that both roll, **WHEN** the schedule is computed, **THEN** only the higher-priority event is scheduled; an operator event in that band overrides both. `test_event_same_band_priority_wins`
26. [Logic] **GIVEN** LUMEN_DUSK ACTIVE from phase 2,537,300 for 90,000 ms, **WHEN** queried at phase 2,600,000, **THEN** event peak = 607, `LQ` = 90, and the uncapped light tier = SS; during BUILDING or FADING it adds nothing to `LQ`. `test_event_phase_and_light_example`

**G. World moment (Core Rule 8; F10)**

27. [Logic] **GIVEN** the golden example (peak 762, CLEAR, no clearing, no event), **WHEN** the world moment is computed, **THEN** WMP = 55 and `world_moment_tier` = "A". `test_world_moment_golden_example`
28. [Logic] **GIVEN** the previous slot was RAIN and the current slot CLEAR, at 45,000 ms into the slot, **WHEN** the world moment is computed, **THEN** the CLEARING window is active with peak 1000 and WMP = max(band, 80) = 80 → S (uncapped). `test_world_moment_clearing_window_peak`
29. [Logic] **GIVEN** several active windows, **WHEN** WMP is computed, **THEN** it equals the maximum of the windows' values (not their sum). `test_world_moment_takes_max_of_windows`
30. [Integration] *(provisional: Subject & Spirit Behaviour)* **GIVEN** `world_moment_tier` = A and a subject moment tier of B, **WHEN** the capture's moment tier is resolved, **THEN** the value Capture Tier Resolution receives follows Subject & Spirit Behaviour F14 (A in an ANTICIPATION or DECISIVE pose; B otherwise).

**H. Key light and EV (Core Rule 9; F11, F12)**

31. [Logic] **GIVEN** phase 2,300 s, **WHEN** the key light is computed, **THEN** elevation = 44 and azimuth = 2773 (floor division; truncation would give 45). `test_key_light_interpolation_uses_floor_division`
32. [Logic] **GIVEN** phase 2,300 s, CLEAR, no event, **WHEN** scene EV is computed, **THEN** it is 105; with RAIN it is 65; at night under RAIN it is clamped to no lower than −40. `test_scene_ev_example_and_weather_offset`
33. [Logic] **GIVEN** phases 2,699,999 and 2,700,000, **WHEN** `key_source` is resolved, **THEN** it is SUN and MOON respectively. `test_key_source_switches_at_night_start`

**I. Determinism, feed, capture time, versions (Core Rules 10–14; F13)**

34. [Integration] **GIVEN** 1,000 golden capture times spread over the fixture schedule, **WHEN** WorldSnapshots are computed by the Web build and the Linux server build in CI, **THEN** all are byte-identical.
35. [Integration] **GIVEN** the scoring-path source files, **WHEN** CI static checks run, **THEN** they contain no `randi`, `randf`, `RandomNumberGenerator`, Variant `hash()` or float literal in the world-state functions.
36. [Integration] *(provisional: Network Transport)* **GIVEN** a connected client, **WHEN** its world feed messages are captured over 2 real hours, **THEN** none contains `world_seed`; the 6-slot forecast matches the server's later actual weather for every slot; each event notice arrives 600,000 ms (± 1 feed tick) before BUILDING and names the zone and band, never a minute.
37. [Logic] **GIVEN** a `capture_tick` resolved by Network F8, **WHEN** the WorldState is computed, **THEN** it is evaluated at exactly `tick_to_ms(capture_tick)` and never at a client-sent time. `test_world_state_uses_network_capture_tick`
38. [Integration] *(provisional: Network Transport)* **GIVEN** a client `view_tick` outside Network's ±60 ms tolerance, **WHEN** the server processes the shot, **THEN** the WorldState is evaluated at Network's clamped estimate and the clamp is logged.
39. [Logic] **GIVEN** versions 1 (from epoch) and 2 (`effective_from` = E), **WHEN** a capture at E − 1 and one at E are resolved, **THEN** they use version 1 and version 2 respectively; publishing a version 3 with `effective_from` < now + `FORECAST_HORIZON_MS` is rejected. `test_rules_version_selected_by_capture_time`
40. [Integration] *(provisional: Photo Recipe)* **GIVEN** a stored photo captured under version 1, **WHEN** version 2 is active and the photo is re-scored, **THEN** its WorldSnapshot equals the stored one.
41. [Logic] **WHEN** a WorldSnapshot is serialised, **THEN** it is 64 bytes or less and contains tier IDs as strings and no rank field. `test_world_snapshot_size_and_id_only_fields`
42. [UI] **GIVEN** a photo taken during a FOG→CLEAR transition at blend 700‰, **WHEN** it is opened in the Gallery, **THEN** the re-render matches the viewfinder capture (same sky, fog amount, shadow angle, wind phase). Evidence: side-by-side screenshot.

**J. Interiors and performance (Core Rule 15)**

43. [Logic] **GIVEN** a zone with `world_light = false` and fixed condition OVERCAST_FOG with `LQ` 40, **WHEN** queried at any time, including during a scheduled outdoor event, **THEN** the condition is OVERCAST_FOG, `light_tier` = B, `world_moment_tier` = C, and no event is active. `test_interior_zone_uses_fixed_light`
44. [Logic] **WHEN** 10,000 full WorldState queries run headless after load, **THEN** they complete in under 50 ms total and allocate no new objects. `test_world_state_query_performance_budget` (budget is a proposal for technical-director).

**K. UI**

45. [UI] *(provisional: Viewfinder HUD spec)* **GIVEN** a client in GOLDEN under CLEAR, **WHEN** the HUD is shown, **THEN** the display clock, band glyph and weather icon appear, and no tier letter or number is visible. Evidence: screenshot.
46. [UI] *(provisional: HUD/map spec)* **GIVEN** an event notice in the feed, **WHEN** it arrives, **THEN** the toast and map marker show the zone and band in calm wording with no tier name. Evidence: screenshot.
47. [UI] **GIVEN** `enabled_cap` = A and a capture with uncapped light S, **WHEN** the Darkroom breakdown shows, **THEN** the light badge reads A, and no text or badge mentions S. Evidence: screenshot.

Coverage notes: every Core Rule (1–15) and every formula (F1–F13) has at least one criterion. Formula F5 → 15; F6 → 16–17; F7 → 18–21; F8/F9 → 22–26; F10 → 27–29; F11/F12 → 31–33; F13 → 37.

48. [Integration] *(provisional: target to be set before `enabled_cap` rises above A)* **GIVEN** the default event chances and a player who plays one fixed real hour per day, **WHEN** a 4-week schedule simulation runs, **THEN** that player has at least the target number of reachable SSS-eligible light windows per real week (each announced by the 10-minute event notice). The target value is owned by Open Question 10.

## Open Questions

| # | Question | Owner | Resolve by |
|---|---|---|---|
| 1 | Which hash function (`hash32`) and integer conventions (floor division helpers, signed index handling) are used, and the published reference vectors. GDScript `int` is assumed to be 64-bit and `/` on ints to truncate toward zero (UNVERIFIED, not in the engine reference), so `floordiv` must be explicit. | technical-director → ADR "Deterministic world-state functions" | Before implementation |
| 2 | How the world feed is delivered (push on change versus periodic snapshot), its tick rate, and how clients sync clocks (offset estimation). | network-programmer → Network Transport GDD / ADR | Network Transport design |
| 3 | Offline or late capture: should captures made during a short disconnect be queued with a signed client timestamp, or is rejection acceptable? | game-designer + network-programmer | Before Vertical Slice |
| 4 | Moon phases for night/astro (would change NIGHT light and AURORA odds over a multi-day cycle). | game-designer | Alpha (Astro role) |
| 5 | Seasonal day length (longer golden hours in one season)? It interacts with Seasons (Alpha). | game-designer + live-ops-designer | Alpha |
| 6 | Event names and looks depend on the unconfirmed setting and tone (B8). Event IDs in data stay neutral and mechanical; SUNBEAM / LUMEN_DUSK / AURORA are display names only and change with the setting. Hard blocker before Vertical Slice. | creative-director + art-director | Before Vertical Slice |
| 7 | Playtest: do players read the forecast and change plans, and is a 63-minute day the right pace? | game-designer (playtest) | First playable |
| 8 | Compatibility/Web rendering of fog, glow, dynamic sky and per-frame shadow-light rotation (UNVERIFIED; art bible VERIFY items). | technical-artist | Before art production |
| 9 | Should Photo Scoring's Light part reuse `LQ` directly for "quality", or compute its own? | systems-designer (Photo Scoring GDD) | Photo Scoring design |
| 10 | The SSS light time per real day with the defaults is very small (about 30 s across both events). Is that the intended scarcity when combined with the capture odds? | systems-designer + economy-designer (simulation) | Before `enabled_cap` rises above A |

## Decisions to confirm

> **DECIDED 2026-11-03 (user):** D1 = (b) 63-minute day; D11 = Network owns capture time (the −1.5 s / +0.25 s window was replaced by Network F8, see F13); all other decisions = the recommended option.

Each item is a choice this draft made on the user's behalf. The recommended option is what the document currently uses.

- **D1. World clock speed.** (a) Real time: one world day is 24 real hours, which is realistic, but players who play at fixed hours never see some light. (b) **Accelerated, 63-minute day (≈ 22.86 : 1)**, chosen so a week holds exactly 160 world days and a fixed-hour player sees every band within a week. (c) Faster, a 24-minute day (60 : 1): more golden hours, but each lasts about 2.5 minutes and feels frantic. **Recommendation: (b).**
- **D2. Shared global clock vs per-room.** (a) **One global clock for every player, room and process, with a per-zone phase-offset field reserved (0 in MVP).** This enables shared events, commissions ("the lighthouse at dusk"), forecasts and crew planning. (b) A per-room clock, which allows private timelines but breaks shared events and the leaderboard's sense of "the same sky". (c) A per-player clock, which suits solo play but makes multiplayer and found photos incoherent. **Recommendation: (a).**
- **D3. Day structure.** (a) **An ordered band list with real durations and a non-linear display clock; asymmetric day (pastel DAWN in the morning, GOLDEN only in the evening).** (b) A symmetric day with golden hour both morning and evening (more A light, less identity per end of day). (c) A physically based sun (elevation from trigonometry), which is more realistic but needs floats in the scoring path. **Recommendation: (a).**
- **D4. Weather model.** (a) **A seeded slot schedule, stateless O(1), with a "stay" roll for continuity; the long-run mix equals the weights exactly.** (b) A seeded Markov chain with daily checkpoints, for more realistic fronts but with state and checkpoint upkeep. (c) A hand-authored weekly calendar: fully designed but predictable and costly to author. (d) Live random weather: simplest, but cannot be reproduced and breaks re-scoring. **Recommendation: (a).**
- **D5. Weather set and slot length.** (a) **Four weathers (clear, overcast, fog, rain), 10.5-minute slots, 60-second blend.** (b) Add storm and snow now (more art and audio scope). (c) Two weathers (clear, overcast) for MVP only. **Recommendation: (a).**
- **D6. How the light tier is derived.** (a) **Integer light quality points: condition base + band-peak bonus, max with event light, + zone modifier, then thresholds and `clamp_to_enabled`.** (b) A pure lookup from condition to tier (simple, but no timing within the band, so the peak does not matter). (c) A continuous physical model (sun elevation, cloud cover, scattering): richer, but float-heavy and harder to explain in the breakdown. **Recommendation: (a).**
- **D7. Which part of "moment" this system owns.** (a) **This system owns the world part (`world_moment_tier` from band, weather, clearing and event windows); Subject & Spirit Behaviour owns the subject part and the combination rule.** This keeps World a dependency-free Foundation system and matches the ladder's interactions table. (b) Subject & Spirit Behaviour owns the whole moment tier, and this system exports only raw window data (no tier). (c) This system owns the full moment tier, reading the subject's pose timing, which creates a World → Subject dependency and breaks the layering. **Recommendation: (a).**
- **D8. Recommended combination of world and subject moment (decided finally in the Subject GDD).** **SUPERSEDED 2026-11-04:** Subject & Spirit Behaviour D7 uses a bounded max, `tier_max(subject, tier_min(world, subject + 1 step))`, applied only in ANTICIPATION or DECISIVE poses; plain `tier_max` below is history only. (a) **`tier_max(world, subject)`: catching either the world's instant or the subject's decisive pose counts.** (b) `tier_min(world, subject)`: both must align, which is very harsh (noon would cap every moment at C). (c) Subject-primary, stepped up one tier when the world moment is higher. **Recommendation: (a).** Risk owned by Subject & Spirit Behaviour: with `tier_max`, players could camp a world event and ignore the subject, so that GDD must keep the subject part meaningful.
- **D9. Rare light events.** (a) **Three seeded events (SUNBEAM, LUMEN_DUSK, AURORA) are the only source of SS/SSS light; operator events can override.** (b) Operator-scheduled events only (fully curated, but needs live-ops staffing). (c) No events: SS/SSS from ordinary golden-hour peaks, which contradicts "short windows" and the art bible's rare-window rule. **Recommendation: (a).**
- **D10. Forecast and seed secrecy.** (a) **Secret seed on the server; the client gets a 6-slot weather forecast and a 10-minute event notice (zone and band only).** (b) No forecast at all, which makes the light pure luck of presence (against Pillar 1 planning). (c) The full schedule is public, so players can plan perfectly but camp and datamine everything and nothing surprises. **Recommendation: (a).**
- **D11. Capture-time authority.** **SUPERSEDED 2026-11-03:** the user chose Network-owned capture time (Network F8; see F13 and Core Rule 12). The options below are kept for history only. ~~(a) The client's synced timestamp is accepted within −1.5 s / +0.25 s of server receipt, and rejected otherwise.~~ (b) Always use the server receipt time, which is simple and cheat-proof but punishes latency (the shot is scored later than it was taken). (c) Clamp out-of-window times to the receipt time instead of rejecting, which keeps the shot but can desync it from the subject pose. **Recommendation: (a).**
- **D12. Rules versioning and old photos.** (a) **Every world-rules version stays loadable; new versions take effect only beyond the forecast horizon; a WorldSnapshot is stored with each photo for re-render and audit.** (b) Store only the timestamp and recompute with current rules, which saves space but lets tuning silently change old photos. (c) Store only the snapshot and never recompute, which is cheapest but loses the ability to verify disputes. **Recommendation: (a).**
- **D13. Baseline value of plain light.** (a) **Midday is B (plain but usable); C light happens only in the darker half of the night.** (b) Midday is C, a strong push towards good light, but 43% of the day would cap every image at C. (c) Midday is A, which removes the "noon is plain" lesson the art bible asks for. **Recommendation: (a).**
- **D14. Night length.** (a) **Night is 28.6% of the day (18 real minutes).** (b) A shorter night (about 15%), with more daylight play but a weaker Astro niche. (c) A realistic night (about 40%). **Recommendation: (a).**
- **D15. Interiors.** (a) **Interior zones use fixed light from zone data, have no events, and give world moment C; no MVP interior is photographable.** (b) Interiors take window light from the world clock (richer, needs per-zone light mapping). (c) Interiors cannot be photographed, ever. **Recommendation: (a).**
- **D16. Determinism approach.** (a) **The scoring path uses only 64-bit integers with a specified hash and floor division; floats only downstream; the algorithm is fixed in an ADR with reference vectors.** (b) Floats with a tolerance window (simpler to write; tier boundaries can flip between platforms). (c) Fixed-point decimals via a library or GDExtension (more precision, extra dependency). **Recommendation: (a).**
- **D17. Systems index row 2 dependency.** (a) **Record "Depends On: Rarity Tier Ladder" on row 2 of `systems-index.md` (that edit was not made, as instructed).** (b) Leave it as "—" and treat the ladder as a shared vocabulary, not a dependency. **Recommendation: (a).**
