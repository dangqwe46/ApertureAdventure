# Rarity Tier Ladder

> **Status**: In Design
> **Author**: user + agents (creative-director, systems-designer, gameplay-programmer, qa-lead)
> **Last Updated**: 2026-11-03
> **Last Verified**: 2026-11-03
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-03 — CONCERNS (5 small items) fixed: near-miss messaging rule, setting-independent anchor, gear-as-ceiling rule, cap-lowering sign-off, Pillar 3 note. NOT ASSESSED: MDA aesthetics target (no ranking exists in the concept); tone fit (tone unconfirmed).
> **Implements Pillar**: Pillar 2 "Every photo matters" (tiers give photos and gear their standing); supports Pillar 1 "Seeing is the skill" (gear sets a ceiling, never the result)

## Summary

The Rarity Tier Ladder is Aperture's one shared scale, C < B < A < S < SS < SSS, used for gear, subjects, light, moment and finished photos. It gives every tier a stable ID, an order, comparison operations (most importantly "lowest of a set" for the capture rule) and badge tokens (letter, lit blades, colour), while leaving odds, prices and supply caps to the systems that own them. It exists so that "the lowest limit wins" has one common vocabulary, and so the badge a player reads means the same thing on a lens, a spirit and a photo; the MVP produces only C to A.

> **Quick reference** — Layer: `Foundation` · Priority: `MVP` · Key deps: `None` (read by ~15 systems; see Dependencies) · Engine: no `core`/`scripting` module in `docs/engine-reference/godot/modules/`, so feasibility was not checked against the pinned engine (no engine API is used)

## Overview

The Rarity Tier Ladder is the single, shared six-step scale — **C, B, A, S, SS, SSS** — that every rarity-bearing thing in Aperture is measured on: camera bodies, lenses, photo subjects, the light and moment of a shot, and the finished image. It is a data and rules layer, not a mechanic the player operates: it defines each tier's stable identity, the order between tiers, the comparison operations other systems call (lowest-of-a-set, at-least, step, gap), and the display tokens (letter, lit aperture blades, colour token) the UI uses to show a tier. It deliberately owns **no numbers about value or chance** — capture odds, prices and supply caps live in Capture Tier Resolution, Photo Pricing and Supply Caps, which key their own tables on the ladder's tier IDs.

The player meets the ladder everywhere and uses it nowhere: it is the badge on a lens in the shop, the blades lit on a spirit in the viewfinder, the letter on a developed photo. Without it, each system would invent its own scale, and the core capture rule — "the lowest limit wins" across gear, subject, moment, light and skill — would have nothing common to compare. For the MVP the game produces only C to A (`enabled_cap = A`); the higher tiers exist as valid IDs from day one so that no stored record ever has to change when they open.

Implementation approach (data format, client/server sharing) is not decided here → becomes an ADR.

## Player Fantasy

**Framing: both** — the ladder is infrastructure, but its badges are read directly and constantly.

**"The ladder is how far I can see."** A tier tells the player what their eye and kit can currently *hold*, not what they own or what they have been allowed. The anchor moment: holding a B lens, the player spots a subject showing four violet blades lit (in the proposed setting, a lens-only spirit; the moment works the same for a rare animal or a rare light). They can see it, frame it and photograph it — the shot comes out at their gear's tier, not the spirit's — and they leave knowing the hour, the weather and the place to come back to with better glass. The ladder turns "I can't have that" into "I know what I'm aiming for." This serves Pillar 1, *"Seeing is the skill. Success comes from the player's eye and timing. Gear raises the ceiling but never replaces skill,"* and the core fantasy, *"I see what others miss, and I choose what's worth keeping."*

**The reveal rule.** The top of the ladder gets one moment of ceremony: an SSS image is the only animated rarity treatment in the whole UI (art bible §4.4). That shimmer always plays **after** the score breakdown has shown why the shot earned it (light, moment, skill). The badge confirms skill; it never replaces the explanation. This is the guard against the ladder reading as a gacha pull, and it protects the anti-pillar "not pay-to-win."

**Language.** Calm and observational, never loot-speak: "Your lens is ready for more," not "Locked"; blades *open*, they are not *earned*; "a rare light tonight," not "Legendary drop!" Higher-tier subjects are always visible and photographable, so the ladder never reads as a wall.

> Tone and setting are **unconfirmed** (concept Open Questions: tone; the spirits setting is a proposal). The anchor moment and wording assume a cozy, reflective tone with lens-only spirits; revisit this section when tone is decided.

For Pillar 3 (*play together*), the shared badge vocabulary is what lets crewmates compare, discuss and trade photos at a glance: an A on your print means the same as an A on theirs.

Odds, price and scarcity *feelings* are owned by Capture Tier Resolution, Photo Pricing and Supply Caps; this section covers only what a badge means when the player reads it.

## Detailed Design

### Core Rules

1. **Identity is a stable string ID.** The six IDs are `"C"`, `"B"`, `"A"`, `"S"`, `"SS"`, `"SSS"`. They are what is stored, transmitted, logged, and used as keys in other systems' tier-keyed tables. IDs are exact-match and case-sensitive (`"sss"` is not a tier).
2. **Rank is derived, never stored.** Each tier's rank is an integer 1–6 (C = 1 … SSS = 6) taken from its position in the ladder data table at load time. Rank is never persisted or sent over the network; only IDs are. Rationale: if a tier is ever added, ranks shift, and a stored rank would silently change meaning.
3. **Permanence.** After launch an ID's string and its meaning never change, and no tier is ever removed. The only allowed change to the ladder is appending a new ID (preferably above SSS); see States and Transitions.
4. **Total order.** C < B < A < S < SS < SSS, defined only by the order of the ladder data table.
5. **Two data sets, one owner.** This system owns:
   - the **identity table** — the ordered list of IDs plus a `ladder_version`. Client, headless server and backend all load it; it is the one that is version-checked between client and server.
   - the **display table**, keyed by ID — `letter`, `blades` (lit aperture blades, 1–6) and `colour_token` (`stone`, `fern`, `lens`, `violet`, `amber`, `pearl`). Only clients need it. Hex values, frame ornaments and the SSS shimmer are defined by the art bible (§4.4) against these token names. Display names for localisation are separate keys, never the IDs.

   Splitting the two means a colour or blade tweak never forces a client/server version mismatch.
6. **Operations.** The ladder exposes pure functions with no state (defined in Formulas):
   - `parse(raw)` → tier ID, or `ERR_UNKNOWN` / `ERR_UNSET`
   - `compare(a, b)` → −1 / 0 / +1; `at_least(a, b)` → bool
   - `tier_min(set)`, `tier_max(set)` → tier ID, or `ERR_EMPTY`
   - `tier_step(t, delta)` → tier ID, clamped to C..SSS
   - `tier_gap(a, b)` → signed int
   - `blades_lit(t)`, `letter(t)`, `colour_token(t)` → display tokens
   - `is_enabled(t)`, `clamp_to_enabled(t)` → respect the enabled cap
7. **Enabled cap.** One configuration value, `enabled_cap`, limits the highest tier the game may **newly produce or unlock**. MVP: `enabled_cap = "A"`. Every ID above the cap stays valid for parsing, storage, display and comparison. Any system that *creates* a tier value (Capture Tier Resolution, content authoring, shop stock) applies `clamp_to_enabled` to its output; existing records above the cap are never altered. Exception: authored content that has a fixed tier (gear models, subject variants) is **gated, not clamped**: an item above the cap keeps its true tier and simply is not released, stocked or scheduled until `is_enabled` allows it. Clamping would relabel it.
8. **Gear is a ceiling, never the result.** Because the capture rule takes the lowest limit, top-tier gear only *allows* a high tier: skill, light and moment are limits too, so SSS gear with an average eye, flat light or a missed moment still yields an average tier. No system may use the ladder to let gear alone raise an outcome (Pillar 1; anti-pillar "not pay-to-win").
9. **No null tier.** The ladder defines no "zero" or "below C" tier. A missing tier is an error to the caller, or the caller's own explicit unset state. `tier_min` can therefore never return a phantom tier.
10. **Server authority.** The server holds the authoritative identity table. Clients receive it for display and local prediction only. Every tier ID arriving from the network is re-parsed; gameplay-relevant tiers (an image's tier, a capture's limits) are always recomputed by the server from its own data and the photo recipe, never taken from the client.

**What this system does not own:** skill-score-to-tier thresholds (Photo Scoring / Capture Tier Resolution); capture odds and the capture rule itself (Capture Tier Resolution — the ladder only supplies `tier_min`); subject, moment and light tier assignment (Subject & Spirit Behaviour, World Time Weather & Light); supply caps and serials (Supply Caps & Gear Serials); prices (Photo Pricing); first-claim scope (First-Claim & Image Serials); the tier assigned to each item (Gear Catalog & Specs); and colours, ornaments and animation (art bible).

### States and Transitions

The ladder has **no runtime states**. It is static data plus one configuration value. Changes happen only between releases or by an operator config change:

| Change | Who decides | Effect | Migration |
|---|---|---|---|
| `enabled_cap` raised (e.g. A → S) | producer, with content ready | New tiers become producible by creating systems | None — all IDs already valid |
| `enabled_cap` lowered | producer **and** creative-director sign-off | Production stops at the new cap; nothing existing is deleted or downgraded, and existing items keep their display and value | None; may strand priced content — review Pricing and Shop first |
| New tier appended (`ladder_version` + 1) | creative-director + producer | Ranks of existing tiers are unchanged when appended above SSS | Every tier-keyed table in other systems must add the new ID; loading fails fast if any table lacks it |

Seasonal or content-phase unlocks, if ever wanted, are expressed by another system changing `enabled_cap`; the ladder itself has no schedule.

### Interactions with Other Systems

The ladder reads nothing. Every other system reads it; each owns the tier *values* it assigns.

| System | Receives from the ladder | Sends to the ladder | Owner of the tier values |
|---|---|---|---|
| Gear Catalog & Specs | ID validation, display tokens | nothing | Gear Catalog (body and lens tier per item) |
| Subject & Spirit Behaviour | ID validation, display tokens | nothing | Subject system (tier per subject or appearance) |
| World Time, Weather & Light | ID validation | nothing | World system (light tier and moment tier outputs) |
| Photo Scoring | `tier_step`, `tier_gap` (if it bands scores into a skill tier) | nothing | Scoring (skill-limit tier) |
| Capture Tier Resolution | `tier_min`, `at_least`, `clamp_to_enabled` | nothing | Resolution (final image tier) |
| Supply Caps & Gear Serials | IDs as table keys, `compare` | nothing | Supply Caps (cap per tier) |
| Photo Pricing & NPC Clients | `compare`, `tier_gap` | nothing | Pricing (value per tier) |
| Gallery, Leaderboards | `compare`, display tokens | nothing | each owns its own sort and filter |
| Viewfinder HUD, Darkroom & Gallery UI, Shop UI | `letter`, `blades_lit`, `colour_token` | nothing | UI (rendering, art bible §4.4) |
| Network Transport & Server Authority | identity table and `ladder_version` for the handshake check | nothing | Network (version-mismatch handling) |

## Formulas

Every rule here is a lookup or integer arithmetic on ranks. None of them is a balance value; the tunable numbers that depend on tiers live in the systems that own them.

The rank formula is defined as:

`rank(t) = LADDER_INDEX[t]`  (C = 1, B = 2, A = 3, S = 4, SS = 5, SSS = 6)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t | string (tier ID) | {C, B, A, S, SS, SSS} | calculated (`parse` output) | Tier being ranked |
| LADDER_INDEX | map ID→int | 6 entries | data file (identity table order) | Position of each ID, 1-based |
| rank | int | 1–6 | calculated | Derived position; never stored |

**Output Range:** 1 to 6; an ID not in the table returns `ERR_UNKNOWN`, never a default.
**Example:** `rank("S") = 4`.

The tier_min formula is defined as:

`tier_min(T) = argmin over t in T of rank(t)`  (`tier_max` uses argmax)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| T | set of tier IDs | size 1..n | calculated (caller, e.g. Capture Tier Resolution) | Limits to combine, e.g. body, lens, subject, moment, light, skill |
| result | string (tier ID) | a member of T | calculated | Lowest (or highest) tier in T |

**Output Range:** always a member of T; an empty T returns `ERR_EMPTY`. Equal tiers need no tie-break because they are the same ID.
**Example:** T = {SSS, SS, S, A, SSS, SSS} → `tier_min(T) = A`.

The tier_step formula is defined as:

`tier_step(t, delta) = ID_AT[clamp(rank(t) + delta, 1, N)]`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t | string (tier ID) | valid ID | calculated (caller) | Starting tier |
| delta | int | any; −5..+5 is meaningful | calculated (caller) | Steps up (+) or down (−) |
| N | int | 6 | data file (identity table size) | Top rank |
| ID_AT | map int→ID | 1..N | data file (identity table order) | Inverse of LADDER_INDEX |

**Output Range:** C to SSS; never overflows. A caller detects a clamp by comparing input and output.
**Example:** `tier_step("S", +3)`: 4 + 3 = 7 → clamp to 6 → `SSS`. `tier_step("B", −2)`: 2 − 2 = 0 → clamp to 1 → `C`.

The tier_gap formula is defined as:

`tier_gap(a, b) = rank(a) − rank(b)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| a, b | string (tier ID) | valid IDs | calculated (caller) | Tiers to compare |
| gap | int | −5 to +5 | calculated | Positive when a is above b |

**Output Range:** −5 to +5 with six tiers.
**Example:** `tier_gap("SS", "B") = 5 − 2 = 3`.

The compare formula is defined as:

`compare(a, b) = sign(rank(a) − rank(b))`;  `at_least(a, b) = rank(a) ≥ rank(b)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| a, b | string (tier ID) | valid IDs | calculated (caller) | Tiers to compare |
| result | int / bool | {−1, 0, +1} / {true, false} | calculated | Ordering result |

**Output Range:** `compare` ∈ {−1, 0, +1}; `at_least` is a bool.
**Example:** `compare("A", "S") = −1`; `at_least("A", "S") = false`; `at_least("S", "S") = true`.

The blades_lit formula is defined as:

`blades_lit(t) = DISPLAY[t].blades`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t | string (tier ID) | valid ID | calculated (caller) | Tier to display |
| DISPLAY[t].blades | int | 1–6 | data file (display table) | Lit aperture blades on the badge |

**Output Range:** 1 to 6. It currently equals `rank(t)`, but it is a data column, not derived from rank, so the art bible can change it without touching identity.
**Example:** `blades_lit("A") = 3`.

The clamp_to_enabled formula is defined as:

`clamp_to_enabled(t) = ID_AT[min(rank(t), rank(enabled_cap))]`;  `is_enabled(t) = rank(t) ≤ rank(enabled_cap)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t | string (tier ID) | valid ID | calculated (a producing system) | Tier about to be produced |
| enabled_cap | string (tier ID) | valid ID; MVP = "A" | data file (config) | Highest tier the game may newly produce |

**Output Range:** C to `enabled_cap`.
**Example:** with `enabled_cap = "A"`: `clamp_to_enabled("SS") = A`; `is_enabled("S") = false`; `is_enabled("B") = true`.

## Edge Cases

- **If `tier_min` or `tier_max` receives an empty set**: return `ERR_EMPTY`, never a default of C. The caller treats the operation as invalid (for a capture: reject it and log it on the server).
- **If an ID not in the identity table arrives from a client** (wrong case such as `"sss"`, surrounding whitespace, a number, null, or an ID from a newer ladder version): `parse` returns `ERR_UNKNOWN`; the server rejects the message and never coerces it to a tier. Repeated invalid IDs count toward the network layer's anti-cheat and rate-limit path.
- **If a client sends a valid but inflated tier** (e.g. claims its capture is `"SSS"`): the server ignores client-sent tiers for anything gameplay-relevant, recomputes the tier from the photo recipe and its own inventory, logs the mismatch, and uses the server value.
- **If a producing system computes a tier above `enabled_cap`** (e.g. resolution yields SS while the cap is A): the result is clamped to the cap with `clamp_to_enabled`. Any message about this follows the Player Fantasy language rule (e.g. "your lens is ready for more") and **never names or shows the tier that was missed** — a "you would have got SS!" message is a near-miss slot-machine pattern and works against Pillar 1.
- **If stored data already holds a tier above `enabled_cap`** (e.g. after the cap was lowered): the record is kept and displayed unchanged; the cap limits only new production.
- **If `tier_step` would go below C or above SSS**: it clamps to C or SSS without error.
- **If client and server `ladder_version` differ**: the server's table wins and the client is told to update. Until it does, any ID the client cannot parse is shown as a neutral "?" badge with no colour, no blades and no comparison — rank is never trusted across versions.
- **If a seventh tier is appended later** (e.g. above SSS): existing records and the ranks of the six existing tiers are unaffected. If one were ever inserted mid-ladder, ranks would shift but nothing persisted breaks, because only IDs are stored. In both cases loading fails fast with a clear error when any other system's tier-keyed table lacks the new ID.
- **If legacy or migrated data has a null or empty tier**: `parse` returns `ERR_UNSET`; there is no runtime default. The migrating system assigns an explicit tier (usually C) in a logged migration step.
- **If a record stores both a rank integer and an ID and they disagree**: the ID wins and the rank field is ignored. A persisted rank field is a schema defect and must be removed.
- **If two equal tiers are compared**: `compare` returns 0 and `at_least` returns true. Any tie-break (leaderboard order, serial order) belongs to the consumer.
- **If an item (such as the phone) has no tier in Gear Catalog**: the capture rule's `tier_min` has nothing to compare and the capture is rejected. Gear Catalog must give every item, including the phone, an explicit tier (Open Question 1).
- **If the display table lacks an entry for a valid ID**: the client shows the letter only and logs a content error, and the build's data validation fails in CI. Display gaps never block gameplay on the server, which does not load the display table.

## Dependencies

**Upstream (this system depends on):** none. The ladder is Foundation-layer static data and reads no other system.

**Downstream (systems that depend on this one):**

| System | Hard / soft | Interface | GDD status |
|---|---|---|---|
| Gear Catalog & Specs | Hard | tier ID per body and lens; validation; display tokens | Not started |
| Subject & Spirit Behaviour | Hard | tier ID per subject or appearance | Not started |
| World Time, Weather & Light | Hard | light tier and moment tier outputs use ladder IDs | Not started |
| Photo Scoring | Soft | `tier_step` / `tier_gap` if scores band into a skill tier | Not started |
| Capture Tier Resolution | Hard | `tier_min`, `at_least`, `clamp_to_enabled` | Not started |
| Supply Caps & Gear Serials | Hard | caps keyed by tier ID | Not started |
| Photo Pricing & NPC Clients | Hard | value keyed by tier ID; `compare`, `tier_gap` | Not started |
| Gallery | Soft | tier ID on each photo; sort and filter by `compare` | Not started |
| Leaderboards | Soft | rarity board sorts by `compare` | Not started |
| Viewfinder HUD, Darkroom & Gallery UI, Shop/Sell/Inventory UI | Hard (display) | `letter`, `blades_lit`, `colour_token` | Not started |
| Network Transport & Server Authority | Hard | identity table and `ladder_version` in the handshake | Not started |

Bidirectional note: none of these GDDs exists yet. Each must list "depends on Rarity Tier Ladder" in its own Dependencies section when it is authored.

## Tuning Knobs

The ladder has almost nothing to tune, by design.

| Knob | Current value | Safe range | Affects | Too low / too high |
|---|---|---|---|---|
| `enabled_cap` | `"A"` (MVP) | any valid ID | Highest tier the game may newly produce | Too low: high-tier gear and subjects become pointless and players hit a ceiling early. Too high before content and balance exist: the top end is empty or trivially reachable, breaking the "SSS is rare" promise. |
| `DISPLAY[t].blades` | 1..6 (equal to rank) | 1..6, strictly increasing with rank | Badge readability | Duplicated or non-increasing counts make tiers unreadable for colour-blind players, since art bible §4.4 relies on blade count as a redundant cue. |
| `DISPLAY[t].colour_token` | stone, fern, lens, violet, amber, pearl | tokens defined in the art bible | Badge colour | A token the art bible does not define renders the fallback badge. |

**Not knobs:** the IDs, their order and the number of tiers are permanent identity. Tier-dependent numbers (odds, prices, caps, skill thresholds) are knobs in their owning systems' GDDs.

## Visual/Audio Requirements

This is a Core system; its visual needs are tokens, and the art bible owns their look.

- Each tier renders as the six-blade aperture badge with `blades_lit(t)` blades lit, the tier letter, and the colour for `colour_token(t)` (art bible §4.4 and the rarity badge notes).
- Colour is never the only cue: letter plus blade count (plus the art bible's frame ornament) must distinguish every pair of tiers.
- SSS is the only animated rarity treatment in the UI, and it plays only after the score breakdown (Player Fantasy, reveal rule).
- An unparseable ID renders a neutral "?" badge: no colour, no lit blades.
- Audio: none owned here. Any tier-reveal sound belongs to Capture Tier Resolution and the Darkroom UI.

## Game Feel

Not applicable: the ladder is data with no interaction, timing or feedback of its own. The feel of a tier reveal belongs to Capture Tier Resolution and the Darkroom & Gallery UI.

## UI Requirements

The ladder has no screen of its own. It supplies display tokens to every surface that shows a tier:

- Viewfinder HUD (a subject's tier when visible), Darkroom & Gallery UI (image tier, after the breakdown), Shop/Sell/Inventory UI (gear tiers), Leaderboard UI.
- Every tier display uses the same badge component and the same three tokens; no surface invents its own tier styling.
- Minimum size and contrast follow art bible §4.4 (tier letters at 16 px or larger; S Violet has the weakest contrast).

📌 **UX Flag — Rarity Tier Ladder**: the tier badge is a shared UI component. In Pre-Production, run `/ux-design` for the badge (and include it in the HUD and Darkroom specs) before writing UI epics.

## Cross-References

| Referenced document | What is used | Where |
|---|---|---|
| `design/gdd/game-concept.md`: Rarity system, Capture rule | Six tiers; "the lowest limit wins"; tier separate from score | Overview, Core Rules 6–7 |
| `design/gdd/game-concept.md`: Pillars | Pillar 1 and 2 quotes; anti-pillar "not pay-to-win" | Player Fantasy |
| `design/gdd/systems-index.md`: row 1, assumptions A3 and A5 | Six tiers (A5, now decided); MVP reduced ladder (A3, now decided as cap A) | Overview, Core Rule 7 |
| `design/art/art-bible.md` §4.4 and rarity badge notes | Colour per tier, blades lit, ornaments, SSS-only animation | Core Rule 5, Visual/Audio, UI Requirements |
| `docs/architecture/research-web-networking.md` | Server authority; one project, two export presets | Core Rule 10, Interactions |

No other GDD exists yet; every downstream GDD will cite this one.

## Acceptance Criteria

Tags: **[Logic]** automated gdUnit4 unit test (suggested name given) · **[Integration]** integration test or documented playtest · **[UI]** retained screenshot in `production/qa/evidence/`. Criteria marked *(provisional)* depend on a system that is not designed yet.

**A. Identity and parse (Core Rules 1, 9, 10)**

1. [Logic] **GIVEN** the identity table is loaded, **WHEN** `parse` is called on each of "C", "B", "A", "S", "SS", "SSS", **THEN** each returns that exact ID. `test_parse_valid_ids_returns_same_id`
2. [Logic] **GIVEN** the raw inputs "sss", " S", "S ", "4", the integer 4 and "SSSS", **WHEN** `parse` is called on each, **THEN** each returns `ERR_UNKNOWN` and none returns a tier. `test_parse_wrong_case_or_unknown_returns_err_unknown`
3. [Logic] **GIVEN** a raw value of null or "", **WHEN** it is parsed, **THEN** the result is `ERR_UNSET` (not C and not `ERR_UNKNOWN`). `test_parse_null_or_empty_returns_err_unset`
4. [Integration] *(provisional: Network Transport)* **GIVEN** a client message carrying tier "sss", **WHEN** the server receives it, **THEN** the message is rejected, no game state changes, and the network layer's invalid-ID counter increases (the size of the increment is owned by Network).
5. [Integration] *(provisional: Capture Tier Resolution, Network)* **GIVEN** a client claims "SSS" for a capture whose recipe and server inventory resolve to "B", **WHEN** the server processes it, **THEN** the stored image tier is "B" and the server log has one mismatch entry naming both values.

**B. Rank and order (Core Rules 2, 4; rank)**

6. [Logic] **GIVEN** the six-entry identity table, **WHEN** `rank` is called on each ID, **THEN** the ranks are C=1, B=2, A=3, S=4, SS=5, SSS=6. `test_rank_each_tier_matches_table_position`
7. [Logic] **GIVEN** a test-fixture table reordered to [B, C, A, S, SS, SSS], **WHEN** it is loaded, **THEN** `compare("B","C") = -1`, proving order comes only from the data. `test_order_follows_table_order_not_code`
8. [Integration] **GIVEN** a saved image record and a network tier message, **WHEN** their serialised payloads are inspected, **THEN** neither contains a rank field and both contain only the string ID.
9. [Logic] **GIVEN** a legacy record `{tier: "S", rank: 2}`, **WHEN** it is loaded, **THEN** the effective tier is "S" and a schema-defect warning is logged. `test_record_rank_id_disagree_id_wins`

**C. Operations (Core Rule 6; Formulas)**

10. [Logic] **WHEN** `compare` and `at_least` are evaluated, **THEN** `compare("A","S") = -1`, `compare("S","A") = +1`, `compare("S","S") = 0`, `at_least("A","S") = false`, `at_least("S","S") = true`. `test_compare_and_at_least_ordering_results`
11. [Logic] **GIVEN** T = {SSS, SS, S, A, SSS, SSS}, **WHEN** `tier_min` and `tier_max` run, **THEN** they return A and SSS; for the one-element set {B} both return B. `test_tier_min_max_returns_member_of_set`
12. [Logic] **GIVEN** an empty set, **WHEN** `tier_min` or `tier_max` is called, **THEN** each returns `ERR_EMPTY` (not C). `test_tier_min_empty_set_returns_err_empty`
13. [Logic] **WHEN** `tier_step` runs, **THEN** ("S", +3) = SSS, ("B", -2) = C, ("A", +1) = S, ("A", 0) = A, ("C", -99) = C, ("SSS", +99) = SSS, with no error raised. `test_tier_step_out_of_range_clamps_to_ends`
14. [Logic] **WHEN** `tier_gap` runs, **THEN** ("SS","B") = 3, ("B","SS") = -3, ("SSS","C") = 5, ("A","A") = 0. `test_tier_gap_returns_signed_rank_difference`

**D. Enabled cap (Core Rule 7; clamp_to_enabled, is_enabled)**

15. [Logic] **GIVEN** `enabled_cap = "A"`, **WHEN** the cap functions run, **THEN** `clamp_to_enabled("SS") = A`, `clamp_to_enabled("B") = B`, `is_enabled("S") = false`, `is_enabled("A") = true`, `is_enabled("B") = true`. `test_clamp_to_enabled_above_cap_returns_cap`
16. [Logic] **GIVEN** `enabled_cap = "A"`, **WHEN** "SS" is parsed, compared and looked up for display, **THEN** all three succeed; the cap never invalidates an ID. `test_ids_above_cap_remain_parseable`
17. [Integration] *(provisional: Capture Tier Resolution)* **GIVEN** `enabled_cap = "A"` and a capture with limits {S, A, SS}, **WHEN** resolution runs on the server, **THEN** the image tier ceiling is A.
18. [Integration] **GIVEN** a stored image of tier "S", **WHEN** `enabled_cap` is lowered from S to A and the server restarts, **THEN** the record still reads "S" and still shows the S badge.

**E. Data split, versioning and permanence (Core Rules 3, 5; States and Transitions)**

19. [Integration] **GIVEN** a build in which only the display table changes (e.g. the `colour_token` for S), **WHEN** that client connects to an unchanged server, **THEN** `ladder_version` matches and no version mismatch is raised.
20. [UI] *(provisional: UX spec for the update prompt)* **GIVEN** a client on `ladder_version` 1 and a server on version 2 that adds "SSSS", **WHEN** the client displays an SSSS item, **THEN** a neutral "?" badge appears with no colour and no lit blades, the item is excluded from tier sorting and comparison, and an update prompt is shown. Evidence: screenshot.
21. [Logic] **GIVEN** a fixture table with "SSSS" appended, **WHEN** it is loaded, **THEN** the ranks of C to SSS are unchanged (1–6) and SSSS = 7. `test_append_tier_keeps_existing_ranks`
22. [Integration] **GIVEN** the appended table and a tier-keyed table (e.g. supply caps) with no SSSS key, **WHEN** the server boots, **THEN** loading stops with an error naming that table and the missing ID.
23. [Integration] **GIVEN** the identity table of the last released build, **WHEN** CI compares the current identity table against it, **THEN** the check fails if any released ID was removed, renamed or reordered, and passes when IDs were only appended at the end.

**F. Display (Core Rule 5; blades_lit)**

24. [Logic] **WHEN** the display functions run for each tier, **THEN** `blades_lit` returns 1–6, `letter` returns the matching letter, and `colour_token` returns stone, fern, lens, violet, amber, pearl in tier order; `blades_lit("A") = 3`. `test_display_tokens_match_display_table`
25. [UI] **GIVEN** one item of each tier in the Gallery, **WHEN** it is rendered, **THEN** each badge shows the correct letter and number of lit blades. Evidence: one screenshot showing all six tiers.
26. [Integration] **GIVEN** a display table missing "SS", **WHEN** CI data validation runs, **THEN** it fails; **WHEN** the client runs anyway, **THEN** an SS item shows only its letter and a content error is logged; **WHEN** the headless server boots, **THEN** it boots normally.

**G. Performance**

27. [Logic] **GIVEN** the ladder is loaded, **WHEN** 10,000 mixed `compare` / `tier_min` / `parse` calls run, **THEN** they allocate no new objects (engine object counter) and complete in under 5 ms headless. `test_ladder_ops_no_allocation_after_load`. The 5 ms budget is a proposal for the technical-director to confirm.

Coverage notes: the phone's tier is out of scope here (Open Question 1, Gear Catalog). A mid-ladder insert is not given a criterion because Core Rule 3 forbids it; criterion 23 enforces that rule in CI.

## Open Questions

| # | Question | Owner | Resolve by |
|---|---|---|---|
| 1 | What tier is the phone (and any otherwise tier-less item)? The capture rule needs a value for body and lens. Proposal: the phone is tier C, with its own ceiling rules in Gear Catalog. | game-designer (Gear Catalog GDD) | Before Gear Catalog & Specs is designed |
| 2 | The concept's odds table merges C/B and A/S into bands. Do capture odds apply per tier or per band? | systems-designer (Capture Tier Resolution GDD) | Before Capture Tier Resolution is designed |
| 3 | Which system converts the skill score into a skill-limit tier: Photo Scoring or Capture Tier Resolution? | systems-designer | Before Photo Scoring is designed |
| 4 | Is "claimable once" for SS and SSS subjects, or SSS only? (The concept says both; its capture table implies SS is merely "rare".) Owned by First-Claim, not the ladder. | game-designer (First-Claim GDD) | Alpha |
| 5 | Tone and setting are unconfirmed; the Player Fantasy wording assumes cozy and reflective with lens-only spirits. | creative-director + user | Before Vertical Slice |
| 6 | Data format and client/server sharing of the identity and display tables (JSON vs Resource; version hash in the handshake). | technical-director → ADR | Architecture phase |
