# Systems Index: Aperture

> **Status**: Draft (unreviewed — see "Gate results" and "Assumptions to confirm")
> **Created**: 2026-11-03
> **Last Updated**: 2026-11-03
> **Source Concept**: design/gdd/game-concept.md (with design/project-context.md for decided vs unconfirmed items)
> **Produced by**: `/map-systems` workflow run by the systems-designer subagent without access to the user. Every point where the skill would have asked the user is resolved by a recorded assumption (see "Assumptions to confirm").
> **Config used**: `modes.rigor: full` (review mode `full`, `docs.density: thorough`, workflow `full`), `modes.automation: guided`, `project.stage: Concept`.

---

## Gate results

The skill calls for three director gates at `review_mode: full`. None of them ran in this session:

- `TD-SYSTEM-BOUNDARY: NOT ASSESSED — the authoring subagent had no Agent tool, so it could not spawn technical-director. Re-run with the dependency map below as input.`
- `PR-SCOPE: NOT ASSESSED — no Agent tool to spawn producer. Team size and project timeline are also missing from the concept and project.yaml, and the gate needs both.`
- `CD-SYSTEMS: NOT ASSESSED — no Agent tool to spawn creative-director. Re-run with this index, the three pillars and the priority tiers below.`

Until these run, this index is a **draft for user review**, not an approved system set. `production/session-state/active.md` was **not updated** (Step 5c), because this run was approved to write only this file.

---

## Overview

Aperture is a server-authoritative online photography RPG. Its mechanical scope has five parts:
1. **A capture simulation:** a 3D world with time, weather and light, shy subjects, and an in-game camera that models focal length, aperture, shutter and focus.
2. **An evaluation pipeline:** a photo is stored as a recipe, scored on the server in seven parts, then assigned a rarity tier by the "lowest limit wins, then roll" capture rule.
3. **A gear-and-money economy:** a phone or camera start, a gear catalog with real-world mount logic, NPC buyers, a gear shop, money sinks and, later, supply caps, wear and crafting.
4. **Persistence and social layers:** gallery, leaderboards, daily themes, found photos.
5. **Synchronous multiplayer, added later:** 2 to 4 player expedition rooms with crew roles.

The core loop (Explore, Capture, Develop, Sell, Upgrade) maps onto these systems. Explore uses Player Movement, World Time/Weather/Light and Zone Access. Capture uses Camera Model, Subject Behaviour and Capture Encounter. Develop uses Photo Recipe, Photo Scoring, Capture Tier Resolution and the Darkroom UI. Sell uses Photo Pricing & NPC Clients and Currency & Wallet. Upgrade uses Gear Shop, Inventory & Loadout and Gear Catalog. The concept's "first playable" asks us to prove that loop end to end, so the MVP tier is exactly the loop plus its foundations: 21 systems.

**Pillar mapping.**
- **Pillar 1 (Seeing is the skill)** depends most on Camera Model, Photo Scoring and Capture Tier Resolution. These three must make the player's framing and timing the main driver of results, with gear as a ceiling.
- **Pillar 2 (Every photo matters)** depends on Photo Recipe, Gallery, Photo Pricing and Leaderboards.
- **Pillar 3 (Play together without violence)** depends on Subject Behaviour, Capture Encounter (the non-violent "boss fight"), Expedition Rooms and Co-op Crew Roles.
- **The anti-pillar "not pay-to-win"** constrains every Economy system. No system in this index sells tier for money.

### Feedback loop analysis

- **Primary positive loop (intentional, needs damping):** better gear raises the tier ceiling, which gives higher-tier photos, more money, and better gear again. If left alone, this is the concept's own "rich get richer" risk.
- **Damping loops (negative):**
  - The skill limit in Capture Tier Resolution: the score must clear a minimum per tier.
  - Upkeep that grows with tier, in Gear Condition & Maintenance.
  - Diminishing returns on repeated subjects and rotating demand, in Photo Pricing.
  - Supply caps, in Supply Caps & Gear Serials.
  - Travel cost, in Zone Access & Travel.

  In MVP only the first and the diminishing returns exist. That is deliberate: the MVP has three upgrade items, so the loop cannot run away. The Alpha economy systems must land before the full ladder ships.
- **Secondary positive loop (social):** leaderboard visibility brings reputation, better commissions and more money. Damping comes from the separate boards (weekly, category and rarity, as the concept requires) and from seasons.
- **Risk loop:** first-claim on SS/SSS subjects concentrates top images in the most active players. Crew credit sharing and participation rewards damp this. The exact shape depends on the open first-claim question.

### Per-system rationale

**Foundation**
1. **Rarity Tier Ladder** — The single C–SSS ladder that gear, subjects, moments, light and images all share. It has no dependencies, and over a dozen systems read it, so it is the first bottleneck to lock. It defines tier IDs, their order, comparisons, and display rules.
2. **World Time, Weather & Light (inferred)** — The capture rule needs a "light tier" and a "moment tier", and top subjects "appear only in short windows (a particular weather, hour or place)". The recipe stores time of day, so this system must be deterministic and reproducible on the server.
3. **Network Transport & Server Authority** — WebSocket transport (ENet does not work in web exports), message versioning, field-range validation, and the rule that the server owns inventories, prices, scores, rolls and counters. Every economy and scoring system relies on this contract.
4. **Player Movement & Exploration (inferred)** — Moving a photographer through a low-poly area. It is small, but the camera and recipe rely on it, since camera position is part of the recipe.

**Core**
5. **Gear Catalog & Specs** — Bodies, lenses, phones and adapters as data: focal length, max aperture, focus speed, sensor size, low-light, burst, battery, mount, tier, condition fields, and vintage look tags. This is where the real-photography identity lives, and the brand question lands here.
6. **Accounts & Server Persistence** — Accounts, sessions and the database behind galleries, wallets, inventories and serials. Inferred detail, explicit need ("accounts and a database").
7. **Subject & Spirit Behaviour** — The photographable things: subject tier, spawn windows, shyness and approach rules, and poses (which the recipe stores). The setting itself is unconfirmed, so the system is named neutrally.
8. **Camera Model: Viewfinder & Exposure (inferred)** — The in-game camera. It simulates field of view from focal length, depth of field from aperture, exposure from shutter/aperture/ISO against scene light, autofocus behaviour, and phone auto-modes. Without it, "seeing is the skill" has nothing to act on.
9. **Photo Recipe & Re-render** — The canonical photo data (camera pose, settings, time, weather, subject ID and pose, gear IDs), its serialization and versioning, and the client-side re-render used by the gallery and leaderboard. It is the bottleneck between capture and everything downstream.
10. **Inventory & Loadout (inferred)** — Server-owned ownership of gear and the equipped body+lens pair, including mount-compatibility validation and adapter penalties.
11. **Currency & Wallet (inferred)** — One soft currency, server-owned balances, a transaction log, and the single place where all faucets and sinks are recorded.

**Feature**
12. **Photo Scoring** — The seven-part score (Subject, Focus, Exposure, Composition, Light, Moment, Rarity), each 0–100, combined into a final score with a visible breakdown. It is computed on the server from the recipe, so each part must be measurable from scene geometry and settings, not from pixels. This is the system with the most design risk.
13. **Capture Tier Resolution** — The concept's capture rule: gear ceiling = min(body, lens), then image tier = min(gear ceiling, subject, moment, light, skill limit), then a roll at the tier's odds. It owns the odds table and the near-miss rules (what you get when the roll fails).
14. **Starting Choice** — Phone vs entry camera, the cost of each, and the promise that "neither is a trap". It depends on two open questions (the phone path and how the camera is paid for).
15. **Gallery** — Persistent ownership of photos: limits, storage-sink hooks, edition state, and sold/unsold flags. Pillar 2 lives here.
16. **Photo Pricing & NPC Clients** — Base price from tier, score and demand. Also covers rotating demand, diminishing returns on repeats, editions ("sells once or in limited editions"), and NPC client requests. This is the main money faucet.
17. **Gear Shop (inferred)** — NPC gear vendor with prices and stock. In MVP it holds three upgrade items. Later, its stock is capped by Supply Caps.
18. **Capture Encounter** — The "capture encounter that works like a boss fight": a scripted subject with phases (approach, reveal, decisive moment, retreat), where the player must read light and timing. It is the MVP's set piece for Pillar 3.

**Presentation (MVP)**
19. **Viewfinder HUD (inferred)** — Framing guides, exposure meter, focus indicator, settings dials, battery and shot count.
20. **Darkroom & Gallery UI** — Post-shot development screen with the score breakdown (explicit MVP requirement), plus gallery browsing.
21. **Shop, Sell & Inventory UI (inferred)** — Selling photos to clients, buying gear, equipping a loadout, and wallet display.

**Vertical Slice**
22. **Zone Access & Travel (inferred)** — "New subjects and places unlock as you upgrade gear", plus travel as a money sink. A single MVP area needs no system; a slice with more than one area does.
23. **Daily Themes & Player Judging** — Themed contests judged by players. Concept marks it "if time allows". It needs anti-collusion and low-population fallbacks.
24. **Leaderboards** — Top-100 boards: all-time, weekly, by category, and rarity. The concept wants one board early, with the split boards to follow.
25. **Found Photos** — Asynchronous photos left in the world for others. A cheap social feature for low concurrency.
26. **Leaderboard & Social UI (inferred)** — Board browsing, entry re-render, contest voting screens.
27. **Audio: SFX & Ambience (inferred)** — The shutter, focus beeps, spirit cues and ambient light/weather beds. The shutter sound is core feedback, not polish.
28. **Onboarding & Tutorial (inferred)** — Teaches exposure and composition through the score breakdown. This is critical for phone-start casual players.

**Alpha**
29. **Expedition Rooms** — 2–4 player rooms: joining, state sync for positions, subjects and world time. It is the networking-heavy part of multiplayer, and is designed separately from the crew roles.
30. **Photographer Reputation (inferred)** — The concept mentions "money or reputation" as rewards. It is a non-money progression track that unlocks clients and commissions, and it also helps against rich-get-richer.
31. **Gear Condition & Maintenance** — Condition, wear, repairs and tier-scaled upkeep, which are the main money sinks. Breakage behaviour is an open question.
32. **Supply Caps & Gear Serials** — Server-owned per-tier counters and serial numbers ("SSS body #7 of 20"). Cap scope is an open question.
33. **Gear Crafting (Merge)** — Merging lower-tier items into a higher tier, so effort rather than luck leads to the top. The concept lists it as a fairness valve, so it is placed in Alpha next to the caps it relieves.
34. **First-Claim & Image Serials** — Claim-once for SS/SSS subject appearances, image serials ("SSS #12 of 100 this season"), and participation rewards. The claim rule is an open question.
35. **Seasons** — Cap resets, a hall of fame, and season-scoped serials.
36. **Co-op Crew Roles** — Wildlife, Portrait, Astro and Street roles, assists (reflector, flash), and credit split.
37. **Player-to-Player Trading & Market** — Two-sided confirmation, price floors and ceilings, and dupe prevention. Whether photos can be traded between players is an open question; gear trading was decided by the user.
38. **Subject Codex & Lore (inferred)** — A collection log of subjects, with lore if the spirit setting is confirmed.
39. **Moderation & Reporting (inferred)** — Player judging, commission text, gallery names and trading all create abuse surfaces that a public online game must handle.
40. **Settings & Accessibility (inferred)** — Input remapping, colour-blind-safe score UI, text size, and audio cue alternatives.
41. **Economy Telemetry (inferred)** — Faucet/sink and tier-distribution metrics. Without this, the "dead top end" and inflation risks cannot be tuned.

**Full Vision**
42. **Commission Board** — Player-posted requests fulfilled for money or reputation.
43. **Composite & Panorama Photos** — Merging crew shots into one higher-value image.
44. **Shared Hub** — A larger shared space where galleries are on display.
45. **Server-Wide Events & Timed Races** — Rare spirit for ten minutes, plus crew races.

---

## Systems Enumeration

Rows are numbered in recommended design order. "(inferred)" marks systems not named directly in the concept.

| # | System Name | Category | Priority | Status | Design Doc | Depends On |
|---|-------------|----------|----------|--------|------------|------------|
| 1 | Rarity Tier Ladder | Core | MVP | Not Started | — | — |
| 2 | World Time, Weather & Light (inferred) | Core | MVP | Not Started | — | — |
| 3 | Network Transport & Server Authority | Core | MVP | Not Started | — | — |
| 4 | Player Movement & Exploration (inferred) | Core | MVP | Not Started | — | — |
| 5 | Gear Catalog & Specs | Economy | MVP | Not Started | — | Rarity Tier Ladder |
| 6 | Accounts & Server Persistence | Persistence | MVP | Not Started | — | Network Transport & Server Authority |
| 7 | Subject & Spirit Behaviour | Gameplay | MVP | Not Started | — | Rarity Tier Ladder, World Time Weather & Light |
| 8 | Camera Model: Viewfinder & Exposure (inferred) | Gameplay | MVP | Not Started | — | Player Movement & Exploration, Gear Catalog & Specs, World Time Weather & Light |
| 9 | Photo Recipe & Re-render | Persistence | MVP | Not Started | — | Camera Model, Subject & Spirit Behaviour, World Time Weather & Light, Network Transport & Server Authority |
| 10 | Inventory & Loadout (inferred) | Economy | MVP | Not Started | — | Gear Catalog & Specs, Accounts & Server Persistence |
| 11 | Currency & Wallet (inferred) | Economy | MVP | Not Started | — | Accounts & Server Persistence |
| 12 | Photo Scoring | Gameplay | MVP | Not Started | — | Photo Recipe & Re-render, Gear Catalog & Specs, Subject & Spirit Behaviour, World Time Weather & Light |
| 13 | Capture Tier Resolution | Progression | MVP | Not Started | — | Rarity Tier Ladder, Gear Catalog & Specs, Inventory & Loadout, Subject & Spirit Behaviour, Photo Scoring |
| 14 | Starting Choice | Progression | MVP | Not Started | — | Gear Catalog & Specs, Inventory & Loadout, Currency & Wallet |
| 15 | Gallery | Persistence | MVP | Not Started | — | Photo Recipe & Re-render, Accounts & Server Persistence, Photo Scoring, Capture Tier Resolution |
| 16 | Photo Pricing & NPC Clients | Economy | MVP | Not Started | — | Photo Scoring, Capture Tier Resolution, Currency & Wallet, Gallery |
| 17 | Gear Shop (inferred) | Economy | MVP | Not Started | — | Gear Catalog & Specs, Inventory & Loadout, Currency & Wallet |
| 18 | Capture Encounter | Gameplay | MVP | Not Started | — | Subject & Spirit Behaviour, Camera Model, Photo Scoring, Capture Tier Resolution |
| 19 | Viewfinder HUD (inferred) | UI | MVP | Not Started | — | Camera Model, Gear Catalog & Specs |
| 20 | Darkroom & Gallery UI | UI | MVP | Not Started | — | Photo Scoring, Capture Tier Resolution, Gallery, Photo Recipe & Re-render |
| 21 | Shop, Sell & Inventory UI (inferred) | UI | MVP | Not Started | — | Gear Shop, Photo Pricing & NPC Clients, Inventory & Loadout, Currency & Wallet |
| 22 | Zone Access & Travel (inferred) | Progression | Vertical Slice | Not Started | — | Player Movement & Exploration, Gear Catalog & Specs, Inventory & Loadout, Currency & Wallet, Subject & Spirit Behaviour |
| 23 | Daily Themes & Player Judging | Gameplay | Vertical Slice | Not Started | — | Gallery, Photo Scoring, Accounts & Server Persistence, Currency & Wallet |
| 24 | Leaderboards | Meta | Vertical Slice | Not Started | — | Gallery, Photo Scoring, Capture Tier Resolution, Photo Recipe & Re-render, Accounts & Server Persistence |
| 25 | Found Photos | Gameplay | Vertical Slice | Not Started | — | Gallery, Photo Recipe & Re-render, Network Transport & Server Authority |
| 26 | Leaderboard & Social UI (inferred) | UI | Vertical Slice | Not Started | — | Leaderboards, Daily Themes & Player Judging, Found Photos, Photo Recipe & Re-render |
| 27 | Audio: SFX & Ambience (inferred) | Audio | Vertical Slice | Not Started | — | Camera Model, Subject & Spirit Behaviour, World Time Weather & Light, Capture Encounter |
| 28 | Onboarding & Tutorial (inferred) | Meta | Vertical Slice | Not Started | — | Starting Choice, Camera Model, Photo Scoring, Photo Pricing & NPC Clients, Viewfinder HUD, Darkroom & Gallery UI |
| 29 | Expedition Rooms | Core | Alpha | Not Started | — | Network Transport & Server Authority, Accounts & Server Persistence, Player Movement & Exploration, World Time Weather & Light |
| 30 | Photographer Reputation (inferred) | Progression | Alpha | Not Started | — | Photo Scoring, Photo Pricing & NPC Clients, Accounts & Server Persistence |
| 31 | Gear Condition & Maintenance | Economy | Alpha | Not Started | — | Gear Catalog & Specs, Inventory & Loadout, Currency & Wallet |
| 32 | Supply Caps & Gear Serials | Economy | Alpha | Not Started | — | Rarity Tier Ladder, Gear Catalog & Specs, Gear Shop, Network Transport & Server Authority |
| 33 | Gear Crafting (Merge) | Economy | Alpha | Not Started | — | Gear Catalog & Specs, Inventory & Loadout, Supply Caps & Gear Serials, Gear Condition & Maintenance |
| 34 | First-Claim & Image Serials | Gameplay | Alpha | Not Started | — | Subject & Spirit Behaviour, Capture Tier Resolution, Gallery, Network Transport & Server Authority |
| 35 | Seasons | Meta | Alpha | Not Started | — | Supply Caps & Gear Serials, First-Claim & Image Serials, Leaderboards |
| 36 | Co-op Crew Roles | Gameplay | Alpha | Not Started | — | Expedition Rooms, Subject & Spirit Behaviour, Camera Model, First-Claim & Image Serials |
| 37 | Player-to-Player Trading & Market | Economy | Alpha | Not Started | — | Inventory & Loadout, Currency & Wallet, Gallery, Photo Pricing & NPC Clients, Supply Caps & Gear Serials, Accounts & Server Persistence |
| 38 | Subject Codex & Lore (inferred) | Narrative | Alpha | Not Started | — | Subject & Spirit Behaviour, Gallery |
| 39 | Moderation & Reporting (inferred) | Meta | Alpha | Not Started | — | Accounts & Server Persistence, Daily Themes & Player Judging, Found Photos, Player-to-Player Trading & Market |
| 40 | Settings & Accessibility (inferred) | Meta | Alpha | Not Started | — | Viewfinder HUD, Darkroom & Gallery UI, Shop Sell & Inventory UI, Audio: SFX & Ambience |
| 41 | Economy Telemetry (inferred) | Meta | Alpha | Not Started | — | Currency & Wallet, Photo Pricing & NPC Clients, Gear Shop, Supply Caps & Gear Serials, Player-to-Player Trading & Market |
| 42 | Commission Board | Economy | Full Vision | Not Started | — | Photo Pricing & NPC Clients, Currency & Wallet, Photographer Reputation, Gallery, Moderation & Reporting |
| 43 | Composite & Panorama Photos | Gameplay | Full Vision | Not Started | — | Photo Recipe & Re-render, Photo Scoring, Co-op Crew Roles |
| 44 | Shared Hub | Gameplay | Full Vision | Not Started | — | Expedition Rooms, Gallery, Player Movement & Exploration, Leaderboards |
| 45 | Server-Wide Events & Timed Races | Meta | Full Vision | Not Started | — | World Time Weather & Light, Subject & Spirit Behaviour, First-Claim & Image Serials, Leaderboards, Expedition Rooms |

---

## Categories

| Category | Description | Systems in Aperture |
|----------|-------------|---------------------|
| **Core** | Foundation systems everything depends on | Rarity Tier Ladder, World Time/Weather/Light, Network Transport & Server Authority, Player Movement, Expedition Rooms (5) |
| **Gameplay** | The systems that make the game fun | Subject Behaviour, Camera Model, Photo Scoring, Capture Encounter, Daily Themes, Found Photos, First-Claim, Co-op Crew Roles, Composite Photos, Shared Hub (10) |
| **Progression** | How the player grows over time | Capture Tier Resolution, Starting Choice, Zone Access & Travel, Photographer Reputation (4) |
| **Economy** | Resource creation and consumption | Gear Catalog, Inventory & Loadout, Currency & Wallet, Photo Pricing, Gear Shop, Gear Condition, Supply Caps, Gear Crafting, P2P Trading, Commission Board (10) |
| **Persistence** | Save state and continuity | Accounts & Server Persistence, Photo Recipe & Re-render, Gallery (3) |
| **UI** | Player-facing information displays | Viewfinder HUD, Darkroom & Gallery UI, Shop/Sell/Inventory UI, Leaderboard & Social UI (4) |
| **Audio** | Sound and music systems | Audio: SFX & Ambience (1) |
| **Narrative** | Story and dialogue delivery | Subject Codex & Lore (1) |
| **Meta** | Systems outside the core game loop | Leaderboards, Onboarding, Seasons, Moderation, Settings & Accessibility, Economy Telemetry, Server-Wide Events (7) |

Total: 45 systems.

---

## Priority Tiers

| Tier | Definition | Target Milestone | Design Urgency |
|------|------------|------------------|----------------|
| **MVP** | Required for the core loop to function. Without these, you can't test "is this fun?" | First playable prototype | Design FIRST |
| **Vertical Slice** | Required for one complete, polished area. Demonstrates the full experience. | Vertical slice / demo | Design SECOND |
| **Alpha** | All features present in rough form. Complete mechanical scope, placeholder content OK. | Alpha milestone | Design THIRD |
| **Full Vision** | Polish, edge cases, nice-to-haves, and content-complete features. | Beta / Release | Design as needed |

| Tier | Count | Why these systems are here |
|------|-------|-----------------------------|
| MVP | 21 | The concept's "Must have" list (one area, about 5 subjects, phone + entry camera + 3 upgrades, score breakdown, NPC selling, gallery and darkroom, one capture encounter) plus every foundation those need. Capture Tier Resolution is MVP because "buy something that changes what you can capture" needs a gear ceiling. Without it, an upgrade changes only the score, and Pillar 1's "gear raises the ceiling" cannot be tested. |
| Vertical Slice | 7 | The concept's "If time allows" items (daily theme, single leaderboard, found photos), plus what a polished single area needs: travel/unlocks, audio feedback, onboarding. |
| Alpha | 13 | The concept's "Later" rarity and multiplayer items (supply caps, serials, first-claim, co-op, P2P trading), plus the economy damping systems the full ladder needs and the operational systems a public online game needs. |
| Full Vision | 4 | Commission board, composites, shared hub, server-wide events. These are explicitly "Later" and depend on Alpha multiplayer. |

> **Creative Director Note**: CD-SYSTEMS NOT ASSESSED — the authoring subagent could not spawn creative-director. Run the gate before GDD authoring begins.

---

## Dependency Map

**Layering convention used here:** a system's layer is set by its role. A system depends only on systems in its own layer or above. Within a layer, it depends only on systems listed **earlier** in that layer. A strict "Core depends only on Foundation" reading would produce 7+ layers for this graph (Camera Model needs Gear Catalog, Recipe needs Camera Model, and so on). See Assumption A1.

### Foundation Layer (no dependencies)

1. Rarity Tier Ladder — the shared C–SSS vocabulary. Gear, subjects, light, moment, images, caps, serials, pricing and boards all read it.
2. World Time, Weather & Light — the deterministic world state that "light tier", "moment tier" and spawn windows are computed from. It must be reproducible from a timestamp/seed so the server can re-score.
3. Network Transport & Server Authority — the authority contract every server-owned value (score, roll, price, inventory, counter) relies on.
4. Player Movement & Exploration — supplies the camera position that the recipe records.

### Core Layer (depends on foundation)

1. Gear Catalog & Specs — depends on: Rarity Tier Ladder
2. Accounts & Server Persistence — depends on: Network Transport & Server Authority
3. Subject & Spirit Behaviour — depends on: Rarity Tier Ladder, World Time/Weather/Light
4. Camera Model: Viewfinder & Exposure — depends on: Player Movement, Gear Catalog, World Time/Weather/Light
5. Photo Recipe & Re-render — depends on: Camera Model, Subject Behaviour, World Time/Weather/Light, Network
6. Inventory & Loadout — depends on: Gear Catalog, Accounts
7. Currency & Wallet — depends on: Accounts
8. Expedition Rooms (Alpha) — depends on: Network, Accounts, Player Movement, World Time/Weather/Light

### Feature Layer (depends on core)

1. Photo Scoring — depends on: Photo Recipe, Gear Catalog, Subject Behaviour, World Time/Weather/Light
2. Capture Tier Resolution — depends on: Rarity Tier Ladder, Gear Catalog, Inventory & Loadout, Subject Behaviour, Photo Scoring
3. Starting Choice — depends on: Gear Catalog, Inventory & Loadout, Currency & Wallet
4. Gallery — depends on: Photo Recipe, Accounts, Photo Scoring, Capture Tier Resolution
5. Photo Pricing & NPC Clients — depends on: Photo Scoring, Capture Tier Resolution, Currency & Wallet, Gallery
6. Gear Shop — depends on: Gear Catalog, Inventory & Loadout, Currency & Wallet
7. Capture Encounter — depends on: Subject Behaviour, Camera Model, Photo Scoring, Capture Tier Resolution
8. Zone Access & Travel — depends on: Player Movement, Gear Catalog, Inventory & Loadout, Currency & Wallet, Subject Behaviour
9. Daily Themes & Player Judging — depends on: Gallery, Photo Scoring, Accounts, Currency & Wallet
10. Leaderboards — depends on: Gallery, Photo Scoring, Capture Tier Resolution, Photo Recipe, Accounts
11. Found Photos — depends on: Gallery, Photo Recipe, Network
12. Photographer Reputation — depends on: Photo Scoring, Photo Pricing & NPC Clients, Accounts
13. Gear Condition & Maintenance — depends on: Gear Catalog, Inventory & Loadout, Currency & Wallet
14. Supply Caps & Gear Serials — depends on: Rarity Tier Ladder, Gear Catalog, Gear Shop, Network
15. Gear Crafting (Merge) — depends on: Gear Catalog, Inventory & Loadout, Supply Caps, Gear Condition
16. First-Claim & Image Serials — depends on: Subject Behaviour, Capture Tier Resolution, Gallery, Network
17. Seasons — depends on: Supply Caps, First-Claim, Leaderboards
18. Co-op Crew Roles — depends on: Expedition Rooms, Subject Behaviour, Camera Model, First-Claim
19. Player-to-Player Trading & Market — depends on: Inventory & Loadout, Currency & Wallet, Gallery, Photo Pricing, Supply Caps, Accounts
20. Commission Board — depends on: Photo Pricing, Currency & Wallet, Photographer Reputation, Gallery, Moderation & Reporting
21. Composite & Panorama Photos — depends on: Photo Recipe, Photo Scoring, Co-op Crew Roles
22. Shared Hub — depends on: Expedition Rooms, Gallery, Player Movement, Leaderboards
23. Server-Wide Events & Timed Races — depends on: World Time/Weather/Light, Subject Behaviour, First-Claim, Leaderboards, Expedition Rooms

### Presentation Layer (depends on features)

1. Viewfinder HUD — depends on: Camera Model, Gear Catalog
2. Darkroom & Gallery UI — depends on: Photo Scoring, Capture Tier Resolution, Gallery, Photo Recipe
3. Shop, Sell & Inventory UI — depends on: Gear Shop, Photo Pricing, Inventory & Loadout, Currency & Wallet
4. Leaderboard & Social UI — depends on: Leaderboards, Daily Themes, Found Photos, Photo Recipe
5. Audio: SFX & Ambience — depends on: Camera Model, Subject Behaviour, World Time/Weather/Light, Capture Encounter
6. Subject Codex & Lore — depends on: Subject Behaviour, Gallery

### Polish Layer (depends on everything)

1. Onboarding & Tutorial — depends on: Starting Choice, Camera Model, Photo Scoring, Photo Pricing, Viewfinder HUD, Darkroom & Gallery UI
2. Moderation & Reporting — depends on: Accounts, Daily Themes, Found Photos, P2P Trading
3. Settings & Accessibility — depends on: Viewfinder HUD, Darkroom & Gallery UI, Shop/Sell/Inventory UI, Audio
4. Economy Telemetry — depends on: Currency & Wallet, Photo Pricing, Gear Shop, Supply Caps, P2P Trading

(Commission Board is listed in Feature even though it depends on the Polish-layer Moderation system. It is Full Vision and is designed after Moderation in the design order, so the order still holds.)

### Bottleneck systems (high fan-in, so lock early)

| System | Direct dependents | Why it matters |
|--------|-------------------|----------------|
| Gear Catalog & Specs | 12 | Every economy system and the capture rule read its fields. A field rename (or a brand rename) ripples everywhere. |
| Photo Scoring | 10 | Pricing, tier, boards, contests, reputation and onboarding all consume the score. |
| Accounts & Server Persistence | 10 | Every server-owned record. |
| Subject & Spirit Behaviour | 10 | Every capture-side system. |
| Photo Recipe & Re-render | 8 | The format must be versioned from day one, because stored photos outlive code changes. |
| Network Transport & Server Authority | 7 directly, all server-owned values indirectly | The authority contract. |
| Rarity Tier Ladder | 5 directly, about 15 through tier fields | A shared vocabulary; cheap to design, expensive to change. |

### Leaf systems (no dependents, so lower risk and can be designed late)

Starting Choice, Capture Encounter, Shop/Sell/Inventory UI (except as an Accessibility input), Leaderboard & Social UI, Onboarding, Subject Codex & Lore, Settings & Accessibility, Economy Telemetry, Composite Photos, Shared Hub, Server-Wide Events, Commission Board.

---

## Recommended Design Order

| Order | System | Priority | Layer | Agent(s) | Est. Effort |
|-------|--------|----------|-------|----------|-------------|
| 1 | Rarity Tier Ladder | MVP | Foundation | systems-designer | S |
| 2 | World Time, Weather & Light | MVP | Foundation | game-designer, systems-designer, technical-artist | M |
| 3 | Network Transport & Server Authority | MVP | Foundation | network-programmer, technical-director, security-engineer | L |
| 4 | Player Movement & Exploration | MVP | Foundation | game-designer, gameplay-programmer | S |
| 5 | Gear Catalog & Specs | MVP | Core | systems-designer, economy-designer | L |
| 6 | Accounts & Server Persistence | MVP | Core | network-programmer, security-engineer | M |
| 7 | Subject & Spirit Behaviour | MVP | Core | game-designer, ai-programmer | L |
| 8 | Camera Model: Viewfinder & Exposure | MVP | Core | game-designer, systems-designer, godot-shader-specialist | L |
| 9 | Photo Recipe & Re-render | MVP | Core | technical-director, network-programmer, systems-designer | M |
| 10 | Inventory & Loadout | MVP | Core | systems-designer | M |
| 11 | Currency & Wallet | MVP | Core | economy-designer | S |
| 12 | Photo Scoring | MVP | Feature | systems-designer, game-designer | L |
| 13 | Capture Tier Resolution | MVP | Feature | systems-designer, economy-designer | M |
| 14 | Starting Choice | MVP | Feature | game-designer, economy-designer | S |
| 15 | Gallery | MVP | Feature | game-designer, systems-designer | S |
| 16 | Photo Pricing & NPC Clients | MVP | Feature | economy-designer | L |
| 17 | Gear Shop | MVP | Feature | economy-designer | S |
| 18 | Capture Encounter | MVP | Feature | game-designer, ai-programmer, level-designer | M |
| 19 | Viewfinder HUD | MVP | Presentation | ux-designer, ui-programmer | M |
| 20 | Darkroom & Gallery UI | MVP | Presentation | ux-designer, ui-programmer | M |
| 21 | Shop, Sell & Inventory UI | MVP | Presentation | ux-designer, ui-programmer | M |
| 22 | Zone Access & Travel | Vertical Slice | Feature | game-designer, level-designer, economy-designer | M |
| 23 | Daily Themes & Player Judging | Vertical Slice | Feature | game-designer, live-ops-designer | M |
| 24 | Leaderboards | Vertical Slice | Feature | systems-designer, network-programmer | M |
| 25 | Found Photos | Vertical Slice | Feature | game-designer | S |
| 26 | Leaderboard & Social UI | Vertical Slice | Presentation | ux-designer | S |
| 27 | Audio: SFX & Ambience | Vertical Slice | Presentation | audio-director, sound-designer | M |
| 28 | Onboarding & Tutorial | Vertical Slice | Polish | game-designer, ux-designer | M |
| 29 | Expedition Rooms | Alpha | Core | network-programmer, technical-director | L |
| 30 | Photographer Reputation | Alpha | Feature | game-designer, systems-designer | M |
| 31 | Gear Condition & Maintenance | Alpha | Feature | economy-designer | M |
| 32 | Supply Caps & Gear Serials | Alpha | Feature | economy-designer, network-programmer | M |
| 33 | Gear Crafting (Merge) | Alpha | Feature | economy-designer, systems-designer | M |
| 34 | First-Claim & Image Serials | Alpha | Feature | systems-designer, network-programmer | M |
| 35 | Seasons | Alpha | Feature | live-ops-designer, economy-designer | M |
| 36 | Co-op Crew Roles | Alpha | Feature | game-designer | L |
| 37 | Player-to-Player Trading & Market | Alpha | Feature | economy-designer, security-engineer | L |
| 38 | Subject Codex & Lore | Alpha | Presentation | narrative-director, writer | M |
| 39 | Moderation & Reporting | Alpha | Polish | community-manager, security-engineer | M |
| 40 | Settings & Accessibility | Alpha | Polish | accessibility-specialist, ux-designer | M |
| 41 | Economy Telemetry | Alpha | Polish | analytics-engineer, economy-designer | M |
| 42 | Commission Board | Full Vision | Feature | economy-designer | M |
| 43 | Composite & Panorama Photos | Full Vision | Feature | game-designer, systems-designer | M |
| 44 | Shared Hub | Full Vision | Feature | game-designer, network-programmer, level-designer | L |
| 45 | Server-Wide Events & Timed Races | Full Vision | Feature | live-ops-designer | M |

Effort: S = 1 session, M = 2–3 sessions, L = 4+ sessions. MVP total is about 7 S + 8 M + 6 L, which is roughly 50+ design sessions before the first playable is fully specified. This is the main input the missing PR-SCOPE gate needs.

**Parallel design opportunities.** Systems 1, 2, 3 and 4 have no dependencies on each other. Systems 6, 10 and 11 (accounts, inventory, wallet) can run in parallel with 7 and 8 (subject, camera). **Co-design pairs:** Photo Scoring (12) and Capture Tier Resolution (13). Photo Pricing (16) and Gear Shop (17) (see Circular Dependencies).

---

## Circular Dependencies

- **Photo Scoring <-> Capture Tier Resolution.** Scoring has a "Rarity" part, which looks as if it needs the image tier. Capture Tier Resolution needs the score as its skill limit. **Resolution:** Scoring's Rarity part reads the **subject** tier (from Subject Behaviour), never the image tier. Capture Tier Resolution reads the final score. The dependency then runs one way, Scoring to Tier. Record this as a contract in both GDDs.
- **Photo Pricing & NPC Clients <-> Photographer Reputation.** Reputation is earned from sales and commissions, and better clients unlock with reputation. **Resolution:** Reputation consumes sale events (one-way input). Pricing reads a read-only `reputation_level` through an interface that MVP Pricing stubs at 0. MVP Pricing is designed without Reputation; Alpha Reputation adds the client-unlock table.
- **Gear Condition & Maintenance <-> Supply Caps & Gear Serials** (only if broken gear returns to supply, an open question). **Resolution:** Supply Caps owns the counters and exposes a single `release_serial` operation. Gear Condition calls it on breakage and Supply Caps never reads condition. If broken gear simply disappears, the edge is removed.
- **Photo Pricing <-> Gear Shop (economic coupling, not structural).** Neither reads the other, but gear prices are only meaningful against photo income per hour. **Resolution:** design them consecutively (orders 16 and 17) against one shared faucet/sink budget table owned by economy-designer. It lives in the Currency & Wallet GDD so both cite the same numbers.

No other cycles were found in the declared graph.

---

## High-Risk Systems

| System | Risk Type | Risk Description | Mitigation |
|--------|-----------|-----------------|------------|
| Photo Recipe & Re-render | Technical | The server must re-score without a GPU (headless), and clients must re-render a stored recipe the same way across WebGL 2 devices and future code versions. Recipe format drift would silently change old photos' scores. | Score from scene geometry and settings (raycasts, frustum tests, light model), never from rendered pixels. Version the recipe from v1 and freeze the score at capture time with the version that produced it. Prototype before Production. |
| Photo Scoring | Design + Technical | Composition and Moment must be measurable, explainable in a breakdown, and feel fair. They also must not be gameable (the "one perfect spot" risk). This is the main test of Pillar 1. | Prototype with the 5 MVP subjects before locking weights. Define each part with a variable table. Pair with diminishing returns in Pricing. |
| Network Transport & Server Authority | Technical | ENet is not available in web exports. A WebSocket server on headless Godot 4.7 is not yet validated in this repo. There is also hosting cost for an always-on authority. | `/setup-engine` first, then a transport spike. Check `docs/engine-reference/godot/` for 4.5–4.7 networking changes, which are beyond the model's training data. |
| Capture Tier Resolution + Supply Caps | Design (economy) | The rich-get-richer loop, and a "dead top end" if SSS odds × caps × skill thresholds multiply to almost nothing. | Run a simulation spec (player cohorts × hours) before tuning. Economy Telemetry in Alpha. Concept: "make sure some SSS gear and images exist at all times". |
| Photo Pricing & NPC Clients | Design (economy) | Inflation, or a single grind spot. | Rotating demand, diminishing returns, sinks in Gear Condition and Zone Access. Shared budget table. |
| Gear Catalog & Specs | Legal + Design | Real brand names in a trading economy (trademark). A late rename touches assets, UI and marketing. | Decide the brand question before Gear Catalog GDD Section 3. Keep brand strings in data only. |
| Subject & Spirit Behaviour | Scope (art) | Characters and spirits are outside asset-forge's scope (no organic or rigged models). | Choose CC0 packs (Quaternius, Kenney) early, or design subjects as stylised non-rigged forms. |
| Daily Themes & Player Judging | Design (social) | Low concurrency means too few judges, and judges can collude. | Hybrid score: server score plus player votes, a minimum vote quorum, and vote weighting. |
| Expedition Rooms + Co-op Crew Roles | Scope + Technical | Synchronous 2–4 player play in a browser. The roles need four distinct mechanics. | Kept in Alpha. Async features ship first, as the concept advises. |
| Player-to-Player Trading & Market | Technical (security) | Duplication, scams, real-money trading. Loot-box regulation if anything random is ever sold. | Server-owned inventory, two-sided confirmation, price floors and ceilings, no paid random rewards. security-engineer reviews. |

---

## Progress Tracker

| Metric | Count |
|--------|-------|
| Total systems identified | 45 |
| Design docs started | 0 |
| Design docs reviewed | 0 |
| Design docs approved | 0 |
| MVP systems designed | 0/21 |
| Vertical Slice systems designed | 0/7 |

---

## Assumptions to confirm

### A. Choices made on the user's behalf (the skill would have asked)

| ID | Assumption | Where it applies | Alternative if rejected |
|----|------------|------------------|-------------------------|
| A1 | Layers are assigned by role. Same-layer dependencies are allowed if the dependency is earlier in the order. | Dependency Map | Strict layering (7+ layers). Same design order, different headings. |
| A2 | Network Transport & Server Authority and Accounts & Server Persistence are **MVP**, so the first playable is already server-authoritative and scores on the server. | Systems 3, 6, 9 | A local single-player first playable with authority added in VS. Faster to playable, but costs a rewrite of the scoring/economy boundary. |
| A3 | Capture Tier Resolution is **MVP**, with a reduced ladder (for example C–A only). The full C–SSS ladder, supply caps, serials and first-claim stay "Later", as the concept says. | Systems 1, 13 | Tier the MVP purely by gear unlocking subjects (no roll). |
| A4 | The "skill score" limit in the capture rule is **the photo's own final score** against a per-tier minimum, not a player level. Photographer Reputation is a separate, non-gating track. | Systems 12, 13, 30 | Skill is a player stat/level. That would add a Progression system and weaken Pillar 1. |
| A5 | Six tiers: C, B, A, S, SS, SSS (the concept says "for example"). | System 1 and everything that reads tiers | A different ladder length. Cheap to change only before Gear Catalog is designed. |
| A6 | Photo Recipe and its client re-render are **one system**. The concept's capture data (recipe) and display (re-render) share one versioned format. | System 9 | Split into "Photo Recipe" (data/server) and "Recipe Renderer" (client) if the GDD grows too large. |
| A7 | Scoring's Rarity part reads **subject** tier, which breaks the Scoring <-> Tier cycle. | Systems 12, 13 | Image-tier-based Rarity part would need a two-pass resolution. |
| A8 | Gallery browsing UI is merged with the Darkroom screen ("Darkroom & Gallery UI"). Shop, sell and inventory share one UI system. | Systems 20, 21 | Separate UI systems per screen. |
| A9 | Category choices: Network and Expedition Rooms = Core; Photo Recipe and Gallery = Persistence; Capture Tier Resolution = Progression; Leaderboards and Seasons = Meta. | Enumeration | Recategorise. Only `Category` is read by `/design-system`, so this changes Formulas hints, not structure. |
| A10 | Lens adapters, vintage looks and the phone are entries **inside Gear Catalog & Specs**, not separate systems. | System 5 | A separate "Phone Path" system if the phone becomes a full upgrade line (see B3). |
| A11 | Editions, demand rotation, diminishing returns and NPC client requests all live in **one** Photo Pricing system. | System 16 | Split "Demand Model" from "Client Requests". |
| A12 | Money sinks are spread out: travel in Zone Access, repairs/upkeep in Gear Condition, storage in Gallery (a storage limit with paid expansion). The concept names "storage" as a sink, but where it sits is my placement. | Systems 15, 22, 31 | One "Money Sinks" system. |
| A13 | One soft currency, no premium currency. Monetization/cosmetic store is **not** in this index (the concept only says paid items, if any, stay cosmetic). | System 11 | Add a "Cosmetics & Monetization" Meta system (Full Vision) once the business model is decided. |
| A14 | Gear Shop is an inferred NPC vendor with fixed MVP prices. Under supply caps its stock becomes cap-limited. | Systems 17, 32 | Gear only from contests and achievements ("earned, not bought" option). |
| A15 | Added inferred systems not in the concept: Moderation & Reporting, Economy Telemetry, Settings & Accessibility, Onboarding, Audio, Subject Codex & Lore, Photographer Reputation, Zone Access & Travel. | Systems 22, 27, 28, 30, 38–41 | Drop or merge any of them. |
| A16 | Gear Crafting and Seasons are **Alpha**, next to Supply Caps (they relieve the caps), even though the concept lists them only as options. | Systems 33, 35 | Full Vision, or cut, if the cap-scope answer makes them unnecessary. |
| A17 | Settings & Accessibility is Alpha. Accessibility could reasonably move earlier for a web game. | System 40 | Move to Vertical Slice. |
| A18 | System names are setting-neutral ("Subject & Spirit Behaviour", "Subject Codex & Lore"), because the spirits setting is unconfirmed. | Systems 7, 38 | Rename once the setting is decided. |
| A19 | Depth applied is `thorough` (from `rigor: full`). Rationale is in Overview, not in extra table columns, per the template contract. | Whole doc | — |
| A20 | Director gates and the session-state update did not run (see Gate results). | Whole doc | Re-run the three gates; update `production/session-state/active.md`. |

### B. Systems whose shape depends on an open question in the concept

| ID | Open question | Systems affected | What changes |
|----|---------------|------------------|--------------|
| B1 | **Brands:** invented makers or real names (with legal review)? | Gear Catalog & Specs (5), Shop/Sell/Inventory UI (21), Leaderboards (24, entries show gear used), Leaderboard & Social UI (26), Subject Codex & Lore (38) | Naming data, mount family names, the asset pipeline (logos/body designs), legal sign-off. Decide before Gear Catalog Section 3. |
| B2 | **Player-to-player photo selling:** allowed, or only NPCs and the market at first? (Gear trading itself was decided.) | Player-to-Player Trading & Market (37), Photo Pricing (16, editions and resale rules), Gallery (15, ownership transfer), Currency & Wallet (11), Moderation (39), Economy Telemetry (41), Commission Board (42) | Whether photos are tradable assets. That affects edition rules ("a sold photo cannot be resold by the seller") and dupe prevention. |
| B3 | **Phone path:** starting tool only, or a permanent path with its own upgrades? | Starting Choice (14), Gear Catalog (5), Camera Model (8, auto modes), Capture Tier Resolution (13, phone tier ceiling), Leaderboards (24, possible phone category), Onboarding (28) | A permanent path needs a phone upgrade line and a tier ceiling above C/B. That might justify a separate "Phone Path" system (A10). |
| B4 | **Starting camera cost:** in-game debt, or paid up front? | Starting Choice (14), Currency & Wallet (11, debt state and repayment) | Debt adds a negative-balance state, repayment rules and failure edge cases to Wallet. |
| B5 | **Supply cap scope:** global, per season, or per player? | Supply Caps & Gear Serials (32), Seasons (35), Gear Shop (17), Gear Crafting (33), P2P Trading (37), Economy Telemetry (41) | Global or per-season caps need server counters and seasons. Per-player caps make Supply Caps a simple ownership limit and weaken Seasons. |
| B6 | **Broken gear:** disappears, or returns to supply? | Gear Condition & Maintenance (31), Supply Caps & Gear Serials (32), Gear Crafting (33) | "Returns to supply" creates the Condition -> Supply `release_serial` edge (see Circular Dependencies). "Disappears" removes it and makes breakage a permanent sink. |
| B7 | **First claim:** winner-takes-all, or a smaller reward for everyone nearby? | First-Claim & Image Serials (34), Co-op Crew Roles (36, credit split), Server-Wide Events & Timed Races (45), Leaderboards (24, rarity board), Expedition Rooms (29, who counts as "nearby") | Reward table, presence detection, and how sharp the competitive loop is. |
| B8 | **Tone:** cozy and reflective, mystery/ghost story, or competitive rival? (Also the unconfirmed spirits setting.) | Subject & Spirit Behaviour (7), Capture Encounter (18), Audio (27), Onboarding (28), Subject Codex & Lore (38), Server-Wide Events (45) | Subject behaviour vocabulary, encounter pacing, and whether a Narrative system beyond the Codex is needed. |

---

## Next Steps

- [ ] User reviews the enumeration, dependencies, priorities and every row of "Assumptions to confirm"
- [ ] Run the three NOT ASSESSED gates: TD-SYSTEM-BOUNDARY, PR-SCOPE (supply team size and timeline), CD-SYSTEMS
- [ ] Resolve B1 (brands) before designing Gear Catalog & Specs
- [ ] Run `/setup-engine` (Godot 4.7, Web) before Network Transport & Server Authority is designed
- [ ] Design MVP-tier systems first (use `/design-system [system-name]`), starting with Rarity Tier Ladder
- [ ] Run `/design-review` on each completed GDD
- [ ] Run `/gate-check technical-setup` when MVP systems are designed
- [ ] Validate the highest-risk systems (Photo Recipe, Photo Scoring, Network) with `/vertical-slice` or a prototype before committing to Production
