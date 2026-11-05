# Gear Catalog & Specs

> **Status**: Designed 2026-11-04 (pending `/design-review` in a fresh session)
> **Author**: user + agents (economy-designer)
> **Last Updated**: 2026-11-04
> **Last Verified**: 2026-11-03
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-04 — CONCERNS fixed: Pillar 1 wording, `model_id` tier token non-authoritative, gear models gated not clamped (ladder Rule 7 amended), phone fantasy softened, concept updated for adapters. Watch: add a higher-tier vintage line when the cap rises. NOT ASSESSED: MDA aesthetics target (none stated); Pillar 3 (no gear co-op role yet).
> **Implements Pillar**: Pillar 1 "Seeing is the skill" (gear raises the ceiling and widens options, never replaces the eye); supports Pillar 2 "Every photo matters" (a photo records the exact gear it was made with) and the anti-pillar "not pay-to-win" (the catalog sells nothing and has no premium flag)

## Summary

Gear Catalog & Specs is the data and rules for every camera body, lens, phone and mount adapter in Aperture. Each **model** has a permanent brand-neutral ID, one explicit rarity tier (the phone is tier C), and integer real-world specs (sensor crop factor, mount and flange distance, focal length or zoom range, maximum aperture, ISO and shutter ranges, burst rate, stabilisation, autofocus class, minimum focus distance). The catalog also defines the pure functions other systems call: does a lens fit, the gear ceiling, equivalent focal length and field of view, depth of field, blur, low-light reach and autofocus time. It owns no prices, supply counters, ownership or wear. MVP ships 18 enabled models from C to A and 5 dormant S to SSS examples held back by `enabled_cap = "A"`.

> **Quick reference** — Layer: `Core` · Priority: `MVP` · Key deps: `Rarity Tier Ladder` (tier IDs, `tier_min`, `is_enabled`); read by Camera Model, Inventory & Loadout, Photo Scoring, Capture Tier Resolution, Starting Choice, Gear Shop, Viewfinder HUD, Network Transport (setting ranges, burst rate) and the Alpha economy systems · Engine: no engine API is used (data and pure functions); data format → ADR

## Overview

The catalog answers two questions: *"What is this piece of gear?"* and *"What does it let a photographer do?"* It is a data layer with a small rules library, not a mechanic the player operates directly. The player meets it on every gear card in the shop, in the loadout screen, and in the viewfinder, where the zoom range, aperture dial and focus speed all come from the equipped body and lens.

Real photography logic is the identity of the system, as the user decided. A lens fits only a body with the same mount. An adapter can bridge two mounts only when the lens mount's flange distance is longer than the body's (the real reason mirrorless bodies adapt old SLR and screw-mount glass, but not the other way round). A small sensor crops the field of view and deepens depth of field. A fast aperture blurs backgrounds and gathers light. The specs and mount logic are real. The makers are invented (Kanro, Nokta, Fujin, plus the vintage maker Hollin and the phone maker Lumo), with no real brand names, logos or product designs, as the user decided on 2026-11-03.

The catalog separates the two things gear can give a player:

- **Tier is the ceiling.** Each model has exactly one tier, read as its optical and build grade. The capture rule takes the lowest of body and lens tier (and adapter tier, if used) as the gear ceiling. Tier never raises a result by itself (Rarity Tier Ladder, Core Rule 8).
- **Specs are the style.** Focal length, aperture, sensor and focus speed decide *which* photos are possible and how they look: a long lens reaches a shy subject on the far rocks, a fast fifty holds the blue hour, and a vintage lens swirls the background. A per-tier **spec budget** keeps a C or B model from carrying top-tier specs, and keeps the jump from tier to tier gentle, so cheap side-grades stay worth buying.

Prices, stock, supply caps, serial numbers, ownership, the equipped loadout, wear and repairs, crafting and scoring all belong to other systems. They key their own tables on the catalog's model IDs and tiers.

Implementation choices (data format, how client and server share the tables, how the catalog version is checked at the handshake) are not fixed here. They become an ADR.

## Player Fantasy

**Framing: direct.** The player handles this system every time they pick up a camera.

**"I know my glass."** The fantasy is the photographer who chooses a lens the way a painter chooses a brush: knowing what each one is for, and feeling the difference in the hands. The anchor moment: at dusk the player takes the kit zoom off and puts on the old Hollin 58 mm through a thread adapter. Autofocus is gone, so they slow down and turn the focus ring by hand. The background behind the lantern-lit spirit melts into a soft swirl that no other lens in their bag makes. The photo is still a B, because the adapter and lens are B, but it is unmistakably *theirs*. That is Pillar 1, *"Gear raises the ceiling but never replaces skill,"* and the core fantasy, *"I see what others miss, and I choose what's worth keeping."*

**Upgrades are new ways of seeing, not bigger numbers.** A 100–300 mm zoom does not make photos "better". It lets the player photograph the heron that will not let them come close. A fast fifty raises what is possible, never what you get: it can lift the gear ceiling, and it lets them keep shooting after the sun goes down, but the shot still has to be earned. Every model's card says what it is *for* in one calm line, so a purchase feels like a decision about the kind of photographer to be today.

**The phone is a real camera.** The phone is an honest way to start and to keep shooting (whether it becomes a permanent upgrade path is Open Question 1). The phone is always in the pocket, focuses and exposes itself, and has a night mode that holds still scenes the entry camera cannot. Its limits (a fixed lens, a tiny sensor with almost no natural blur, a C ceiling) are honest and visible, and a sharp eye with a phone still out-scores a careless eye with an expensive body (concept, Starting choice: *"Neither is a trap"*).

**Language.** Cozy and reflective, never stat-stick talk. "Holds the light until blue hour", not "Low-light +3". "Fits your Hearth with the H42 ring", not "Compatible: 1 adapter". "Your lens is ready for more" when the ceiling is the limit, never "Locked" (ladder language rule).

## Detailed Design

### Core Rules

**A. Identity**

1. **A model is the unit of the catalog.** A model is one kind of gear (for example "Kanro KR 50 mm f/1.8"). Every model has a permanent `model_id`, a `kind` (`BODY`, `LENS`, `PHONE`, `ADAPTER`), a `brand_id`, a display name key, one `tier`, a `spec_rev`, a `release_state` and its kind's spec fields (rules 9–12). Individual owned items (instances) are not catalog records. Inventory & Loadout owns instances; each instance stores only `item_id` and `model_id`, plus the fields other systems add (serial from Supply Caps, condition from Gear Condition).
2. **IDs are permanent and brand-neutral.** `model_id` follows `[kind]_[spec]_[tier]_[nn]`, lowercase, for example `lens_std50_f18_b_01`. It never contains a brand string, so a brand rename touches only display data (art bible A3). The asset base name is `gear_` + `model_id` (`gear_lens_std50_f18_b_01.glb`), matching the art bible naming rule (§8.2, A15). Once released, a `model_id` is never reused, renamed or deleted (retirement only; see States and Transitions). The `[tier]` token in a `model_id` is a **non-authoritative lowercase label for humans**: it is never parsed, and the `tier` field is the only source of a model's tier, so a signed-off tier migration (rule 7) leaves the ID unchanged.
3. **Tier is per model, never per instance.** All instances of a model share its tier. No instance rolls a tier, and no instance can hold a different tier from its model. Supply Caps, Pricing, Crafting and Condition may key their tables on tier, and never alter it.
4. **Every model has an explicit tier.** There is no null tier (Rarity Tier Ladder, Core Rule 9). The phone, each phone module and every adapter carries a tier. A model without a valid ladder ID fails catalog load and fails CI.
5. **Tier is the optical and build grade, and the capture ceiling.** It is not computed from specs. A model's specs must fit within its tier's spec budget (Formula F11), so tier and specs move together loosely, and a high-tier model may still have modest specs (for example the A-tier 40 mm pancake). Pricing and Shop should price tier first and specs second; that is their decision, not this system's.
6. **Specs are integers.** Every scoring-relevant spec is stored as an integer in a fixed unit (table below), so the server validates and replays gear without floats. Functions that need trigonometry or logarithms (FOV, depth of field) are computed downstream in the consuming system, which owns its own tolerance (World Time, Core Rule 10). Display-only derived stats are rounded to integers before they are shown or stored.

   | Quantity | Field unit | Example |
   |---|---|---|
   | Focal length | deci-mm (`_deci`) | 50 mm = 500 |
   | f-number | deci (`_deci`) | f/1.8 = 18 |
   | Crop factor | milli (`_milli`) | 1.5× = 1500 |
   | Flange distance | centi-mm (`_centi`) | 20.0 mm = 2000 |
   | Shutter speed | microseconds (`_us`) | 1/4000 s = 250 |
   | Burst rate | deci-frames/s (`_deci`) | 3.0 fps = 30 |
   | Magnification | milli (`_milli`) | 0.23× = 230 |
   | Distance | mm | 0.25 m = 250 |
   | EV | deci-EV (`_deci`) | EV 2.9 = 29 |

7. **Spec immutability and revisions.** The scoring-relevant fields of a released model are frozen for a given `spec_rev`. A correction or rebalance creates `spec_rev + 1` with patch notes. Owned instances always use the latest released revision (players own a model, not a revision). Photo recipes store `model_id` and `spec_rev`, so an old photo is always re-rendered and re-scored with the specs it was shot with. Every revision stays loadable on the server. A model's **tier** never changes after release, except by a logged operator migration signed off by creative-director and producer (it would ripple into prices and caps).
8. **Cosmetic variants never change tier or specs.** A model may declare `variant_of` (another `model_id`). A variant must match its base's tier and every spec field exactly, and differ only in colour or finish. CI rejects any variant that differs. This keeps any future cosmetic sale within the anti-pillar "never sell tier" (concept, Risks). Whether variants are ever sold is a monetization decision for creative-director, not this system.

**B. Kinds and fields**

9. **Body fields.** `mount_id`; `sensor_format` (`PHONE`, `ONE_INCH`, `M43`, `APSC`, `FF`, `MF`); `crop_milli`; `iso_min`, `iso_max`, `iso_clean` (highest ISO with no noise penalty; Photo Scoring decides what happens above it); `shutter_fast_us`, `shutter_slow_us`, `bulb` (bool, long exposures, Alpha Astro); `burst_deci`; `ibis_stops` (in-body stabilisation, 0–5); `af_class` (1–5); `battery_shots`; `sealed` (bool); `shutter_sound_id`.
10. **Lens fields.** `mount_id`; `coverage_crop_milli` (image circle: 1000 full frame, 1500 APS-C, 790 medium format); `f_min_deci`, `f_max_deci` (equal for a prime); `n_wide_deci` (maximum aperture at `f_min`), `n_tele_deci` (at `f_max`; equal to `n_wide_deci` for constant-aperture lenses), `n_min_deci` (smallest aperture); `mfd_mm` (minimum focus distance); `max_mag_milli`; `ois_stops` (0–5); `af_class` (0 = manual focus only, 1–5); `sealed`; `look_tags` (list); optional `length_override_mm` (art hint for pancakes).
11. **Phone fields.** A phone is one model that is both body and lens. It has body fields except `mount_id` (its mount is `INT`, integrated) and a list of 1–3 **modules**. Each module has `module_id`, `crop_milli` (its own sensor), `f_deci` (real focal length), `n_deci` (fixed aperture), `ois_stops`, `af_class`, `mfd_mm`, and inherits the phone's tier. A phone has `digital_zoom_max_milli` (MVP 2000, so 2×, on the main module only), `module_switch_ms`, and a set of **computational modes** (rule 18). Modules are never separate items: they cannot be removed, traded or adapted.
12. **Adapter fields.** `from_mount` (the lens side), `to_mount` (the body side), `adapter_kind` (`DUMB`: a plain ring with no contacts; `SMART`: with electronic contacts). Adapters have no optical specs and no spec budget; their tier is authored.
13. **Mounts are data.** Each mount has a neutral `mount_id`, a `display_code` and `brand_id` (display data, brand-renamable), `mount_type` (`BAYONET_ML` mirrorless, `BAYONET_SLR`, `THREAD`, `INTEGRATED`), `flange_centi`, `electronic` (bool), the `coverages` its lenses may have, and `swap_ms` (time to change a lens in the field, read by Inventory & Loadout and Camera Model).

**C. Fit and loadout rules (the catalog defines them; Inventory & Loadout enforces them at equip time)**

14. **A camera loadout is one body plus one lens, plus at most one adapter.** A phone loadout is the phone alone, with one active module. A body with no lens cannot shoot. Adapters never chain: two adapters in one loadout is invalid.
15. **Direct fit.** A lens fits a body directly when `lens.mount_id = body.mount_id` and the lens's `coverage_crop_milli` is in the mount's `coverages`. Coverage mismatches are allowed and real: a full-frame lens on an APS-C body is cropped by the body; an APS-C lens on a full-frame body makes the body switch to crop mode (Formula F1).
16. **Adapted fit.** A lens fits through an adapter when `adapter.from_mount = lens.mount_id`, `adapter.to_mount = body.mount_id`, and the adapter is valid by the flange rule (Formula F13). A `DUMB` adapter turns the lens's autofocus and lens stabilisation off. A `SMART` adapter keeps them, but lowers the lens's AF class by `SMART_AF_PENALTY`. Integrated (`INT`) mounts are never adaptable in either direction.
17. **Gear ceiling.** The gear ceiling of a loadout is `tier_min` of its body tier, lens tier and adapter tier (if any), or the phone's tier for a phone loadout (Formula F12). The catalog defines this function because only it knows which items a loadout contains. Capture Tier Resolution calls it and combines the result with the subject, moment, light and skill limits. The catalog never clamps the gear ceiling; producing systems apply `clamp_to_enabled` to what they produce.
18. **Phone computational modes.** The phone has three modes. Camera Model implements their behaviour and Photo Scoring applies their score effects; the catalog defines the parameters:
    - `AUTO` (always on): auto exposure and continuous subject-detect autofocus. The player can still set exposure compensation.
    - `NIGHT`: stacks frames for `NIGHT_MODE_STOPS` = 3 extra stops of low-light reach, but only if the camera is held still and the subject stays within `NIGHT_MODE_DRIFT_MM` for `NIGHT_MODE_HOLD_MS` = 2,000 ms. A moving subject ends the stack early and gives the normal exposure. `NIGHT_MODE_DRIFT_MM` = 150 and the phone's body `af_class` = 3 (2026-11-05, from Camera Model).
    - `PORTRAIT`: adds a synthetic background blur worth `PORTRAIT_SYNTH_BLUR_BP` = 250 bp of frame width (Formula F7), with edge artefacts. Photo Scoring decides how artefacts affect the Focus part; the recommendation is a small, visible penalty, so real glass keeps its value.
19. **Setting ranges.** For any valid loadout and current focal length, the catalog returns the legal camera settings: focal range (`f_min`..`f_max`, or modules plus digital zoom for a phone), aperture range (`n_max_at(f)` from Formula F4 to `n_min`), ISO range (`iso_min`..`iso_max`) and shutter range (`shutter_fast_us`..`shutter_slow_us`). Network Transport (rule 25) rejects any shot outside these ranges as the **server** knows the loadout, and Camera Model limits its dials to them.
20. **Producible models.** A model may be newly produced (shop stock, rewards, crafting output, starting kit) only when `release_state = RELEASED` and `is_enabled(tier)` is true. Models above `enabled_cap` are complete, valid data ("dormant") that is never minted. Owned instances of a model that later becomes non-producible stay fully usable.
21. **Catalog versioning.** The catalog has a `catalog_version`. Client, headless server and backend load the same catalog; the server's copy is authoritative. The version is checked at the handshake (as with `ladder_version`). Display data (names, brand labels, card blurbs) is split from rules data, so a text change never forces a version mismatch.
22. **Server authority.** The server holds the authoritative catalog. Every `model_id`, `spec_rev` and setting arriving from the network is checked against it. Gear-derived gameplay values (gear ceiling, legal ranges, burst rate) are always computed on the server from its own catalog and inventory, never taken from the client.

**D. MVP content**

23. **Brand roster (invented; working names, see Decision D3).** Brands exist only as display data (`brand_id`, name, label decal, one-line identity).

    | brand_id | Name | Identity (one line, for cards and art) | Mounts | MVP role |
    |---|---|---|---|---|
    | `br_kanro` | Kanro | Warm and approachable; the camera you grow up with. Rounded grips. Bodies are named for home lights (Hearth, Lantern, Beacon). | M20 "KR" (FF + APS-C) | Home mount of the first playable: entry kit and all three upgrades |
    | `br_nokta` | Nokta | Precise and patient; built for wildlife and long waits. Angular bodies. Bodies are named for birds (Kestrel) and sky words (Zenith). | M16 "NZ" (FF + APS-C), S465 "NF" (legacy SLR, reserved), M267 "NM" (medium format, dormant) | Alternative A body, mid zoom, smart adapter; top-end dormant examples |
    | `br_fujin` | Fujin | Small, quiet, street; dials on top, flat-top bodies, compact primes. | M17 "FX" (APS-C only) | Side-grade line that tops out at B in MVP |
    | `br_hollin` | Hollin | A workshop that closed long ago; chrome rings, manual focus, lenses with a memory of their own. | T455 "H42" (thread) | Vintage looks, the reason adapters exist in MVP |
    | `br_lumo` | Lumo | The phone in your pocket. | INT | The free starting phone |

24. **Mount families.** Flange distances follow real-world mount logic.

    | mount_id | display_code | Brand | mount_type | flange_centi | electronic | coverages | swap_ms | MVP |
    |---|---|---|---|---|---|---|---|---|
    | `M16` | NZ | Nokta | BAYONET_ML | 1600 | yes | 1000, 1500 | 1200 | yes |
    | `M17` | FX | Fujin | BAYONET_ML | 1770 | yes | 1500 | 1200 | yes |
    | `M20` | KR | Kanro | BAYONET_ML | 2000 | yes | 1000, 1500 | 1200 | yes |
    | `M267` | NM | Nokta | BAYONET_ML | 2670 | yes | 790 | 1500 | dormant (SSS example) |
    | `T455` | H42 | Hollin | THREAD | 4550 | no | 1000 | 2500 | yes |
    | `S465` | NF | Nokta | BAYONET_SLR | 4650 | yes | 1000, 1500 | 1200 | reserved, no models |
    | `INT` | — | Lumo | INTEGRATED | — | yes | phone | — (module switch 300 ms) | yes |

    What the flange rule allows (F13): H42 vintage lenses adapt to every mirrorless mount; KR lenses adapt to NZ and FX bodies; NZ lenses adapt to nothing (shortest flange); FX lenses adapt to NZ only. Nothing adapts onto H42 or onto the reserved SLR mount.

25. **Zooms exist in MVP.** The entry kit lens is a zoom (as real kits are), plus one tele zoom and one mid zoom. Variable-aperture zooms lose maximum aperture as they zoom in (Formula F4). Primes remain the fast, light-gathering choice, so "zoom versus walk" is a real trade.

26. **MVP catalog (enabled, tiers C to A).** Spec points (F11) are shown against the tier budget. "FP" marks the proposed first-playable set (phone, entry kit and three upgrades, per the concept's "a phone and one entry camera, plus 3 pieces of upgrade gear"); Gear Shop owns actual stock.

    **Phone**

    | model_id | Name | Tier | Modules (real f, crop → equivalent, aperture) | ISO min–max (clean) | Shutter | Burst | Other | Points / budget | FP |
    |---|---|---|---|---|---|---|---|---|---|
    | `phone_basic_c_01` | Lumo Pebble | C | main 4.6 mm, ×5.6 → 26 mm, f/1.8, OIS 2, AF 3, MFD 100 mm; ultrawide 1.9 mm, ×7.0 → 13 mm, f/2.2, OIS 0, AF 2, MFD 80 mm | 50–3200 (800) | 1/8000–1 s | 3.0 fps | digital zoom 2× (main); modes AUTO, NIGHT, PORTRAIT; battery 600 | body 1/2; main module 2/2; ultrawide 0/2 | ✓ start |

    **Bodies**

    | model_id | Name | Tier | Mount | Sensor (crop) | ISO min–max (clean) | Shutter | Burst | IBIS | AF | Sealed | Battery | Points / budget | FP |
    |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
    | `body_aps_entry_b_01` | Kanro Hearth | B | M20 | APS-C (1.5) | 100–12800 (3200) | 1/4000–30 s | 5.0 | 0 | 2 | no | 400 | 2/4 | ✓ start |
    | `body_ff_a_01` | Kanro Lantern | A | M20 | FF (1.0) | 100–51200 (6400) | 1/8000–30 s, bulb | 8.0 | 3 | 3 | no | 500 | 6/6 | ✓ U3 |
    | `body_aps_retro_b_01` | Fujin Drift | B | M17 | APS-C (1.5) | 160–12800 (3200) | 1/4000–30 s | 8.0 | 0 | 3 | no | 380 | 4/4 | |
    | `body_ff_wild_a_01` | Nokta Kestrel | A | M16 | FF (1.0) | 100–51200 (6400) | 1/8000–30 s | 10.0 | 0 | 3 | no | 520 | 6/6 | |

    **Lenses**

    | model_id | Name | Tier | Mount | Coverage | Focal (mm) | Max aperture | Min ap. | MFD / max mag | OIS | AF | Look tags | Points / budget | FP |
    |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
    | `lens_zoom18_45_c_01` | Kanro KR-S 18–45mm f/4.5–6.3 OS | C | M20 | APS-C | 18–45 | f/4.5–6.3 | f/22 | 250 mm / 0.23× | 3 | 2 | — | 2/2 | ✓ start (kit) |
    | `lens_std50_f18_b_01` | Kanro KR 50mm f/1.8 | B | M20 | FF | 50 | f/1.8 | f/16 | 300 mm / 0.19× | 0 | 2 | — | 2/3 | ✓ U1 |
    | `lens_tele85_f14_a_01` | Kanro KR 85mm f/1.4 | A | M20 | FF | 85 | f/1.4 | f/16 | 850 mm / 0.11× | 0 | 3 | — | 4/4 | ✓ U2 |
    | `lens_zoom100_300_b_01` | Kanro KR 100–300mm f/4.5–7.1 OS | B | M20 | FF | 100–300 | f/4.5–7.1 | f/32 | 1200 mm / 0.25× | 4 | 2 | — | 3/3 | |
    | `lens_pan40_f28_a_01` | Kanro KR 40mm f/2.8 Pancake | A | M20 | FF | 40 | f/2.8 | f/22 | 300 mm / 0.17× | 0 | 2 | — | 1/4 | |
    | `lens_std27_f28_c_01` | Fujin FX 27mm f/2.8 | C | M17 | APS-C | 27 | f/2.8 | f/16 | 340 mm / 0.10× | 0 | 2 | — | 0/2 | |
    | `lens_std33_f14_b_01` | Fujin FX 33mm f/1.4 | B | M17 | APS-C | 33 | f/1.4 | f/16 | 300 mm / 0.15× | 0 | 3 | — | 2/3 | |
    | `lens_zoom24_70_f4_b_01` | Nokta NZ 24–70mm f/4 | B | M16 | FF | 24–70 | f/4 | f/22 | 300 mm / 0.30× | 0 | 3 | — | 2/3 | |
    | `lens_std58_f20_b_01` | Hollin 58mm f/2 "Harbour" | B | T455 | FF | 58 | f/2 | f/16 | 600 mm / 0.11× | 0 | 0 (manual) | `SWIRL_BOKEH`, `WARM_FLARE` | 2/3 | |
    | `lens_wide28_f28_c_01` | Hollin 28mm f/2.8 | C | T455 | FF | 28 | f/2.8 | f/16 | 300 mm / 0.12× | 0 | 0 (manual) | `SOFT_CORNERS`, `WARM_FLARE` | 1/2 | |

    **Adapters**

    | model_id | Name | Tier | From → to | Kind | Flange depth | Effect |
    |---|---|---|---|---|---|---|
    | `adp_t455_m20_b_01` | Hollin H42 → KR ring | B | T455 → M20 | DUMB | 25.5 mm | manual focus, no lens OIS (Hollin lenses have neither anyway) |
    | `adp_t455_m17_b_01` | Hollin H42 → FX ring | B | T455 → M17 | DUMB | 27.8 mm | as above |
    | `adp_m20_m16_a_01` | Nokta KR → NZ Smart Adapter | A | M20 → M16 | SMART | 4.0 mm | AF class −1, OIS kept |

    Enabled tier counts: C 4, B 9, A 5 (18 models). Paths to an A ceiling in MVP: Lantern + KR 85; Lantern + KR 40 pancake; Kestrel + smart adapter + KR 85 (the Kestrel has no native A lens yet, which is what the smart adapter is for). The Fujin line and the Hollin line top out at B in MVP.

27. **Dormant examples (released data, above `enabled_cap`, never minted in MVP).** They exist so tier-keyed tables, UI and tests cover the whole ladder from day one.

    | model_id | Name | Tier | Kind | Key specs | Points / budget |
    |---|---|---|---|---|---|
    | `lens_tele200_f28_s_01` | Nokta NZ 200mm f/2.8 OS | S | lens, M16, FF | 200 mm f/2.8, OIS 4, AF 5 | 5/5 |
    | `body_ff_s_01` | Kanro Beacon | S | body, M20, FF | ISO clean 12800, burst 10, IBIS 3, AF 3 | 7/7 |
    | `lens_std50_f12_ss_01` | Kanro KR 50mm f/1.2 | SS | lens, M20, FF | 50 mm f/1.2, AF 4, sealed | 6/6 |
    | `body_mf_sss_01` | Nokta Zenith | SSS | body, M267, MF (0.79) | ISO clean 12800, burst 3, IBIS 5, AF 3, sealed | 9/9 |
    | `lens_std80_f18_sss_01` | Nokta NM 80mm f/1.8 | SSS | lens, M267, MF | 80 mm f/1.8 (≈ 63 mm f/1.4 equivalent), AF 3, sealed | 4/7 |

**What this system does not own:** prices and stock (Photo Pricing, Gear Shop); supply caps and serial numbers (Supply Caps & Gear Serials); ownership, instances and the equipped loadout (Inventory & Loadout, which enforces the fit rules defined here); wear, condition values, repairs and what `sealed` does in the rain (Gear Condition & Maintenance); merging (Gear Crafting); how specs change the score, including noise above `iso_clean`, portrait artefacts and digital-zoom loss (Photo Scoring); exposure, focusing behaviour, battery drain and the viewfinder (Camera Model); the final image tier and odds (Capture Tier Resolution); shapes, colours and decals (art bible).

### States and Transitions

The catalog has no per-player runtime state. Models move through a release lifecycle between builds, and loadouts have a derived validity state.

**Model release lifecycle**

| From | To | Who decides | Effect |
|---|---|---|---|
| — | `DRAFT` | designer | Authored in data; loaded only in dev builds; fails no validation it has not reached yet |
| `DRAFT` | `TESTING` | designer + QA | Passes CI validation (F11 budget, F13 adapters, variant rule, ID format, FOV bounds); loaded in test builds only |
| `TESTING` | `RELEASED` | producer | Part of the shipped catalog; producible if `is_enabled(tier)` (rule 20); `model_id` and tier become permanent |
| `RELEASED` | `RETIRED` | producer + economy-designer | No longer producible; existing instances stay fully usable, tradable and displayable; recipes still resolve |
| `RETIRED` | `RELEASED` | producer | Allowed (for example a seasonal return); the same `model_id` and tier |

"Dormant" is not a state. It is a `RELEASED` model whose tier is above `enabled_cap`, and it becomes producible the moment the cap is raised, with no data change.

**Spec revision**

| From | To | Trigger | Effect |
|---|---|---|---|
| `spec_rev` k | `spec_rev` k+1 | a balance or correction change to a released model | Instances use k+1 from the release that ships it; photos keep the revision they were shot with; revision k stays loadable on the server |

**Loadout validity (derived by the catalog's functions; Inventory & Loadout enforces it)**

| State | Condition | Can shoot |
|---|---|---|
| `VALID_DIRECT` | body + lens, same mount (rule 15) | yes |
| `VALID_ADAPTED` | body + lens + one valid adapter matching both mounts (rule 16) | yes, with adapter effects |
| `VALID_PHONE` | phone alone, one active module | yes |
| `INCOMPLETE` | body with no lens | no |
| `INVALID_MOUNT` | mounts differ and no matching adapter | no; equip is refused |
| `INVALID_ADAPTER` | adapter does not match, fails F13, or more than one adapter | no; equip is refused |

### Interactions with Other Systems

| System | Reads from the catalog | Sends to the catalog | Notes |
|---|---|---|---|
| Rarity Tier Ladder | — | tier IDs, `parse`, `tier_min`, `is_enabled`, display tokens | The catalog assigns a tier to every model; the ladder owns the vocabulary |
| Camera Model: Viewfinder & Exposure | specs, setting ranges (rule 19), F1–F6, F8, F10, phone modes, `swap_ms`, `module_switch_ms` | nothing | Owns exposure, focusing, zoom behaviour, battery drain; exposes against World F12 `scene_ev_deci` |
| Inventory & Loadout | fit rules (14–17), loadout validity, `model_id`, `kind`, adapter effects | nothing | Owns instances and the equipped set; enforces the fit rules at equip time, on the server |
| Capture Tier Resolution | `gear_ceiling(loadout)` (F12) | nothing | Combines it with subject, moment, light and skill limits through `tier_min` |
| Photo Scoring | specs per `model_id` + `spec_rev`; F5/F6 depth of field; `iso_clean`; `look_tags`; phone mode flags | nothing | Owns every score effect of gear; recommended: look tags have no score effect (D15) |
| Photo Recipe & Re-render | `model_id`, `spec_rev`, active phone module and mode | nothing | The recipe stores these; re-render reads `look_tags` for the lens look |
| Network Transport & Server Authority | setting ranges (rule 19), `burst_deci` (its F1b reads `burst_fps` = `burst_deci` / 10), `catalog_version` | nothing | Already lists Gear Catalog as a soft dependency (its rules 25–26) |
| Starting Choice | the starting phone and entry kit `model_id`s | nothing | Owns cost and the choice itself |
| Gear Shop | producible models (rule 20), tier, kind, spec points | nothing | Owns stock and price; the catalog owns no price |
| Photo Pricing & NPC Clients | (indirect) tier, `look_tags` for client requests such as "a vintage look" | nothing | Not a declared dependency in the systems index; optional |
| Viewfinder HUD | focal range, current FOV, aperture range, AF state source, battery capacity, phone modes | nothing | |
| Shop, Sell & Inventory UI | names, brand labels, tier, spec card fields, derived display stats (F7, F9, F10), fit status, gear ceiling preview | nothing | See UI Requirements |
| Zone Access & Travel (VS) | specs (for example "needs ≥ 300 mm equivalent" or "needs EV reach ≤ 1.0" as optional access hints) | nothing | Whether gear gates zones is that system's decision |
| Gear Condition & Maintenance (Alpha) | `sealed`, tier, kind | nothing | Owns condition values and their effects |
| Supply Caps & Gear Serials (Alpha) | `model_id`, tier | nothing | Whether caps are per model or per tier is its decision (B5) |
| Gear Crafting (Alpha) | `model_id`, tier, kind, `release_state` | nothing | Crafting outputs must be producible models (rule 20) |
| Leaderboards, Leaderboard & Social UI (VS) | display names and tier of the gear stored in the recipe | nothing | "Gear used" on each entry |
| Player-to-Player Trading (Alpha) | `model_id`, tier, `variant_of` | nothing | Trades instances; never edits catalog data |
| Economy Telemetry (Alpha) | model and tier lists | nothing | Ownership distribution per model and tier |

**Economy note (exhaustible sink).** The catalog is the menu of the main money sink in MVP. With 18 enabled models and no maintenance, travel or wear in MVP, a player who owns everything they want has nothing left to spend on. That is acceptable for the first playable (the concept caps it at three upgrades), but before the catalog grows or more players arrive, Currency & Wallet's shared budget table must state the time to buy out the enabled catalog, and the Alpha sinks (Gear Condition, Zone Access) must exist. The catalog's lever here is breadth: how many models each tier holds.

## Formulas

Notation: integers unless stated. `floordiv` rounds toward negative infinity. `round_half_up(x) = floor(x + 0.5)`. "Display only" means the value is shown in UI and never used by the server for a gameplay decision.

### F1. Effective crop factor

The effective_crop formula is defined as:

`crop_eff_milli = max(body.crop_milli, lens.coverage_crop_milli)` (camera loadout);  `crop_eff_milli = module.crop_milli` (phone)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| body.crop_milli | int | 790–7000 | data file (body) | Body sensor crop factor ×1000 (FF = 1000) |
| lens.coverage_crop_milli | int | 790, 1000, 1500 | data file (lens) | Crop factor of the lens's image circle |
| module.crop_milli | int | 2500–7000 | data file (phone module) | Phone module sensor crop |
| crop_eff_milli | int | 790–7000 | calculated | Crop that the frame actually uses |

**Output Range:** 790 to 7000. The larger crop wins: a full-frame lens on an APS-C body is cropped by the body, and an APS-C lens on a full-frame body makes the body crop to the lens's image circle.
**Example:** KR 50 mm (1000) on the Hearth (1500) → 1500. KR-S kit zoom (1500) on the Lantern (1000) → 1500 (the Lantern shoots in crop mode).

### F2. Equivalent focal length

The equivalent_focal formula is defined as:

`f_eq_mm = floordiv(f_deci × crop_eff_milli × zoom_milli + 5,000,000, 10,000,000)`  (`zoom_milli` = 1000 except phone digital zoom)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| f_deci | int | lens `f_min_deci`..`f_max_deci`, or module `f_deci` | calculated (Camera Model current zoom) / data file | Real focal length ×10 |
| crop_eff_milli | int | 790–7000 | calculated (F1) | Effective crop |
| zoom_milli | int | 1000..`digital_zoom_max_milli` (MVP 2000) | calculated (Camera Model, phone only) | Phone digital zoom factor ×1000 |
| f_eq_mm | int | `F_EQ_MIN`..`F_EQ_MAX` (12–450) | calculated | 35 mm-equivalent focal length, rounded half up |

**Output Range:** must lie within [`F_EQ_MIN`, `F_EQ_MAX`] = [12, 450] mm for every reachable loadout, which keeps the vertical FOV inside Player Movement's 3–90° range (CI checks every reachable pairing). The rounded value is for display and validation; F3 uses the unrounded value.
**Example:** 50 mm on APS-C: (500 × 1500 × 1000 + 5,000,000) / 10,000,000 = 755,000,000 / 10,000,000 → **75 mm**. Phone main: (46 × 5600 × 1000 + 5,000,000) / 10^7 = 262,600,000 / 10^7 → **26 mm**; at 2× digital zoom → 52 mm. KR 100–300 on the Hearth at 300 mm → **450 mm** (exactly at `F_EQ_MAX`).

### F3. Field of view

The field_of_view formula is defined as:

`vfov_deg = 2 × atan((SENSOR_H_FF / 2) / f_eq_real)`;  `hfov_deg = 2 × atan((SENSOR_W_FF / 2) / f_eq_real)`;  `f_eq_real = f_deci × crop_eff_milli × zoom_milli / 10^7` (float)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| SENSOR_H_FF | float (mm) | 24 | data file (constant) | Full-frame sensor height (3:2 frame) |
| SENSOR_W_FF | float (mm) | 36 | data file (constant) | Full-frame sensor width |
| f_eq_real | float (mm) | 12–450 | calculated (F2 without rounding) | Unrounded equivalent focal length |
| vfov_deg, hfov_deg | float (°) | vfov 3.06–90; hfov 4.6–112.6 | calculated (Camera Model) | Vertical and horizontal field of view |

**Output Range:** vertical FOV 3.06° (450 mm) to 90° (12 mm). Every frame is 3:2 in MVP, including the phone (Decision D11). Camera Model owns the camera; Photo Scoring owns any tolerance where FOV feeds a score (World Time, Core Rule 10).
**Example:** 200 mm full frame: 2 × atan(12/200) = **6.87°** (the same number Player Movement F6 uses). 50 mm on APS-C (75 mm): 2 × atan(0.16) = **18.18°** vertical, 2 × atan(0.24) = **26.99°** horizontal. Phone ultrawide (13.3 mm real equivalent): 2 × atan(12/13.3) = **84.1°**.

### F4. Maximum aperture at a focal length (variable-aperture zooms)

The n_max_at formula is defined as:

`n_max_at(f) = snap_up(n_wide + ceil_div((n_tele − n_wide) × (f − f_min), (f_max − f_min)))` for zooms; `n_max_at(f) = n_wide` for primes, constant-aperture zooms and phone modules

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| f | int (deci-mm) | `f_min_deci`..`f_max_deci` | calculated (Camera Model current zoom) | Current focal length |
| f_min, f_max | int (deci-mm) | 10–3000 | data file (lens) | Zoom range ends |
| n_wide, n_tele | int (deci f) | 10–110 | data file (lens) | Maximum aperture at each end |
| ceil_div | function | — | — | Integer division rounded up |
| snap_up | function | — | data file (`THIRD_STOPS`) | Smallest value in the third-stop list ≥ its input |
| THIRD_STOPS | list of int | 10, 11, 12, 14, 16, 18, 20, 22, 25, 28, 32, 35, 40, 45, 50, 56, 63, 71, 80, 90, 100, 110, 130, 140, 160, 180, 200, 220, 250, 290, 320 | data file | Standard third-stop f-numbers ×10 |
| result | int (deci f) | n_wide..n_tele | calculated | Widest legal aperture at f |

**Output Range:** `n_wide` to `n_tele`, always a value on the third-stop list, never wider than the lens allows (Network rule 25 checks the requested aperture against this, at the requested focal length).
**Example:** KR-S 18–45 f/4.5–6.3 at 30 mm: 45 + ceil_div(18 × 120, 270) = 45 + ceil_div(2160, 270) = 45 + 8 = 53 → snap_up → **56** (f/5.6). At 18 mm → 45 (f/4.5); at 45 mm → 63 (f/6.3).

### F5. Circle of confusion

The circle_of_confusion formula is defined as:

`coc_dum = floordiv(COC_FF_DUM × 1000 + floordiv(crop_eff_milli, 2), crop_eff_milli)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| COC_FF_DUM | int (0.1 µm) | 290–330; default 300 | data file (tuning) | Acceptable blur circle on full frame (30.0 µm) |
| crop_eff_milli | int | 790–7000 | calculated (F1) | Effective crop |
| coc_dum | int (0.1 µm) | 42–420 | calculated | Circle of confusion for this frame, rounded half up |

**Output Range:** about 4.3 µm (crop 7.0) to 38 µm (medium format).
**Example:** APS-C: (300,000 + 750) / 1500 → **200** (20.0 µm). Phone main (5.6): (300,000 + 2800) / 5600 → **54** (5.4 µm). Medium format (0.79): (300,000 + 395) / 790 → **380** (38.0 µm).

### F6. Depth of field

The depth_of_field formula is defined as:

`H = f² / (N × c) + f`;  `D_near = s × (H − f) / (H + s − 2f)`;  `D_far = s × (H − f) / (H − s)` if `s < H`, else infinity  (floats, mm)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| f | float (mm) | 1.9–300 | calculated (`f_deci` / 10) | Real focal length |
| N | float | 1.0–32 | calculated (Camera Model aperture setting / 10) | Set f-number |
| c | float (mm) | 0.0043–0.038 | calculated (F5 / 10,000) | Circle of confusion |
| s | float (mm) | `mfd_mm`..10^6 | calculated (Camera Model focus distance) | Focus distance |
| H | float (mm) | — | calculated | Hyperfocal distance |
| D_near, D_far | float (mm) | `mfd_mm`..infinity | calculated | Nearest and farthest acceptably sharp distances |

**Output Range:** D_near ≤ s ≤ D_far. Camera Model uses this for the depth-blur shader (the prototype's COC-based disc blur, which works on Compatibility/Web as a custom shader). Photo Scoring uses it for the Focus part and owns the tolerance.
**Example:** KR 50 mm f/1.8 on the Hearth, focused at 2 m: c = 0.020, H = 2500 / 0.036 + 50 = **69,494 mm**; D_near = 2000 × 69,444 / 71,394 = **1,945 mm**; D_far = 2000 × 69,444 / 67,494 = **2,058 mm**, so about 11 cm is sharp. The phone main module at 2 m, f/1.8: c = 0.0054, H ≈ **2,182 mm**, D_near ≈ **1,044 mm**, D_far ≈ **23,990 mm**: almost everything is sharp, which is why the phone has PORTRAIT mode.

### F7. Background blur index (display only)

The blur_index formula is defined as:

`blur_bp = round_half_up(10,000 × (f² / (N_tele × (S_REF − f))) / (SENSOR_W_FF / crop_eff))`  at the lens's longest focal length and its maximum aperture there; `blur_bp = PORTRAIT_SYNTH_BLUR_BP` for a phone in PORTRAIT mode

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| f | float (mm) | 1.9–300 | data file (`f_max_deci` / 10) | Longest real focal length |
| N_tele | float | 1.0–11 | data file (`n_tele_deci` / 10) | Maximum aperture at that focal length |
| S_REF | float (mm) | 1000–5000; default 2000 | data file (tuning) | Reference subject distance; background at infinity |
| SENSOR_W_FF / crop_eff | float (mm) | 5.1–45.6 | calculated (F1) | Sensor width of the frame |
| blur_bp | int (basis points of frame width) | 0–1500 | calculated | Size of a far background point's blur disc as a share of frame width |

**Output Range:** 0 to about 1,500 bp. It compares how much a loadout can separate a subject from its background. Display only: the real blur in a photo comes from F6 and Camera Model.
**Example:** KR 85 f/1.4 on the Lantern: 7225 / (1.4 × 1915) = 2.695 mm; ÷ 36 mm = 0.0749 → **749 bp** (7.5% of frame width). KR 50 f/1.8 on the Hearth: 0.712 mm ÷ 24 mm → **297 bp**. Kit zoom at 45 mm f/6.3 on the Hearth: 0.1644 ÷ 24 → **69 bp**. Phone main: 0.00589 mm ÷ 6.43 mm → **9 bp**; PORTRAIT mode → 250 bp.

### F8. Handheld shutter limit

The handheld_limit formula is defined as:

`stab = min(STAB_CAP, max(ois_eff, body.ibis_stops))`;  `t_hand_us = floordiv(1,000,000 × 2^stab, f_eq_mm)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| ois_eff | int (stops) | 0–5 | calculated (lens `ois_stops`, or 0 through a DUMB adapter; F13) | Lens stabilisation in use |
| body.ibis_stops | int (stops) | 0–5 | data file (body; phone uses module `ois_stops`) | In-body stabilisation |
| STAB_CAP | int (stops) | 3–7; default 6 | data file (tuning) | Maximum combined stabilisation |
| f_eq_mm | int (mm) | 12–450 | calculated (F2) | Equivalent focal length |
| t_hand_us | int (µs) | 2,222–5,333,333 | calculated | Slowest shutter that stays sharp handheld (reciprocal rule) |

**Output Range:** 1/450 s (450 mm, no stabilisation) to 5.3 s (12 mm, 6 stops). Stabilisation does not stack: the better of lens and body is used. Camera Model owns camera shake; this is its default threshold and the input to F9.
**Example:** KR-S kit at 18 mm on the Hearth: f_eq 27, OIS 3 → 8,000,000 / 27 = **296,296 µs** (about 0.3 s). KR 50 on the Hearth: f_eq 75, no stabilisation → **13,333 µs** (1/75 s).

### F9. Low-light reach (display only)

The low_light_reach formula is defined as:

`t_s_us = min(t_hand_us, T_SUBJECT_US)`;  `ev_reach_deci = round_half_up(10 × (log2(N² × 1,000,000 / t_s_us) − log2(iso_clean / 100)))` − (phone NIGHT mode ? `NIGHT_MODE_STOPS` × 10 : 0)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t_hand_us | int (µs) | from F8 | calculated (F8) | Handheld limit at the lens's widest focal length |
| T_SUBJECT_US | int (µs) | 8,000–33,333; default 16,667 (1/60 s) | data file (tuning) | Slowest shutter that freezes a gently moving subject |
| N | float | 1.0–11 | data file (`n_wide_deci` / 10) | Maximum aperture at the widest focal length |
| iso_clean | int | 400–25,600 | data file (body or phone) | Highest ISO without noise penalty |
| NIGHT_MODE_STOPS | int | 0–4; default 3 | data file (phone) | Night-mode stacking gain, still subjects only |
| ev_reach_deci | int (0.1 EV at ISO 100) | −40 to 120 | calculated | Darkest scene EV the loadout can expose correctly for a living subject |

**Output Range:** in the same unit as World Time F12 `scene_ev_deci` (−40 to 160), so the UI can say how far into the evening a loadout reaches. Lower is better. Display only: Camera Model computes real exposure.
**Example:** Kit zoom on the Hearth: t_s = min(296,296, 16,667) = 16,667; 20.25 × 10^6 / 16,667 = 1,215 → log2 = 10.247; minus log2(32) = 5 → **52** (EV 5.2, early blue hour). KR 50 on the Hearth: t_s = 13,333; 3.24 × 10^6 / 13,333 = 243 → 7.925 − 5 → **29**. KR 85 on the Lantern: t_s = 16,667; 1.96 × 10^6 / 16,667 = 117.6 → 6.877 − log2(64) = 6 → **9** (EV 0.9, below World's night EV 1.0). Phone main: 194.4 → 7.603 − 3 → **46**; NIGHT mode → **16**.

### F10. Autofocus acquire time

The af_time formula is defined as:

`af_ms = floordiv(AF_LENS_MS[lens_af_eff] × AF_BODY_PERMILLE[body.af_class], 1000)` if `lens_af_eff ≥ 1`; otherwise `MANUAL` (no autofocus)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| lens_af_eff | int | 0–5 | calculated (lens `af_class` after F13 adapter effects; phone module `af_class`) | Effective lens AF class |
| body.af_class | int | 1–5 | data file (body or phone) | Body AF system class |
| AF_LENS_MS | map int → int (ms) | defaults 1: 600, 2: 450, 3: 320, 4: 220, 5: 150 | data file (tuning) | Lens motor time to lock |
| AF_BODY_PERMILLE | map int → int (‰) | defaults 1: 1300, 2: 1150, 3: 1000, 4: 850, 5: 700 | data file (tuning) | Body AF speed multiplier |
| af_ms | int (ms) | 105–780, or `MANUAL` | calculated | Time from focus start to focus lock on a static subject |

**Output Range:** 105 ms (class 5 on class 5) to 780 ms (class 1 on class 1), or `MANUAL`. Camera Model owns tracking, hunting and moving-subject behaviour; this is the base value it starts from.
**Example:** Kit zoom (2) on the Hearth (2): 450 × 1150 / 1000 = **517 ms**. KR 85 (3) on the Lantern (3): **320 ms**. Nokta NZ 24–70 (3) on the Lantern via... not valid (NZ lenses cannot adapt to KR, F13). KR 85 (3) through the smart adapter (−1 → 2) on the Kestrel (3): 450 × 1000 / 1000 = **450 ms**. Hollin 58 on any body: **MANUAL**.

### F11. Spec points and tier budget (authoring validation)

The spec_budget formula is defined as:

`LSP = AP + ZP + SP + FP + MP + WS` (lens or phone module);  `BSP = SN + IC + BR + IB + AF + WS` (body or phone body);  `valid = LSP ≤ LENS_BUDGET[tier] and BSP ≤ BODY_BUDGET[tier]`

| Points | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| AP (equivalent max aperture `n_eq = floordiv(n_wide_deci × coverage_crop_milli, 1000)`; phone uses module crop) | > 28 | 21–28 | 15–20 | ≤ 14 |
| ZP (zoom ratio `f_max × 1000 / f_min`) | prime | ≤ 3000 | > 3000 | — |
| SP (lens `ois_stops`) | 0 | 1–3 | ≥ 4 | — |
| FP (lens `af_class`) | 0–2 | 3 | 4–5 | — |
| MP (`max_mag_milli` ≥ 500) | no | yes | — | — |
| SN (`crop_milli`) | ≥ 2500 | 1300–2499 | 900–1299 | < 900 |
| IC (`iso_clean`) | ≤ 1600 | 1601–6400 | > 6400 | — |
| BR (`burst_deci`) | ≤ 50 | 51–100 | > 100 | — |
| IB (`ibis_stops`) | 0 | 1–3 | ≥ 4 | — |
| AF (body `af_class`) | 1–2 | 3 | 4–5 | — |
| WS (`sealed`) | no | yes | — | — |

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| LSP | int | 0–11 | calculated | Lens spec points |
| BSP | int | 0–14 | calculated | Body spec points |
| LENS_BUDGET | map tier → int | defaults C 2, B 3, A 4, S 5, SS 6, SSS 7 | data file (tuning) | Maximum lens points per tier |
| BODY_BUDGET | map tier → int | defaults C 2, B 4, A 6, S 7, SS 8, SSS 9 | data file (tuning) | Maximum body points per tier |
| valid | bool | — | calculated (CI) | The model may leave `DRAFT` |

**Output Range:** a pass or fail per model. The budget is a ceiling only: a high-tier model with few points is allowed (it is a cheap route to that tier's ceiling, with weaker specs for the score). Aperture uses the full-frame-equivalent f-number, so a phone's f/1.8 or an APS-C f/1.4 is not counted as a full-frame f/1.4. Budgets rise by 1 per tier above A, so a top-tier model is at most a few points better than an A model; most of the top-end value is the ceiling, not raw power.
**Example:** KR 85 f/1.4 (A): AP 3 (n_eq 14) + ZP 0 + SP 0 + FP 1 (AF 3) + MP 0 + WS 0 = **4 ≤ 4**, valid. Kanro Lantern (A): SN 2 + IC 1 (6400) + BR 1 (8.0) + IB 1 (3) + AF 1 (3) + WS 0 = **6 ≤ 6**, valid; giving it 5 stops of IBIS would make IB 2 and BSP 7, which fails the A budget. Phone main module (C): AP 0 (n_eq = 18 × 5.6 = 100) + SP 1 + FP 1 = **2 ≤ 2**.

### F12. Gear ceiling

The gear_ceiling formula is defined as:

`gear_ceiling(L) = tier_min({phone.tier})` if L is a phone loadout; `tier_min({body.tier, lens.tier} ∪ ({adapter.tier} if L has an adapter))` if L is `VALID_DIRECT` or `VALID_ADAPTED`; `ERR_INCOMPLETE` or `ERR_INVALID_LOADOUT` otherwise

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| L | loadout | phone, or body + lens (+ adapter) | calculated (Inventory & Loadout, server) | The equipped set at the capture tick |
| body.tier, lens.tier, adapter.tier, phone.tier | tier ID | C–SSS | data file (catalog) | Model tiers |
| tier_min | function | — | Rarity Tier Ladder | Lowest tier of a non-empty set |
| gear_ceiling | tier ID or error | C–SSS | calculated | The gear limit passed to Capture Tier Resolution |

**Output Range:** a valid ladder ID, or an error that makes the capture invalid (it is never C by default; ladder Core Rule 9).
**Example:** Hearth (B) + kit zoom (C) → **C**. Hearth (B) + KR 50 (B) → **B**. Lantern (A) + KR 50 (B) → **B**. Lantern (A) + KR 85 (A) → **A**. Lantern (A) + H42 ring (B) + Hollin 58 (B) → **B**. Kestrel (A) + smart adapter (A) + KR 85 (A) → **A**. Lumo Pebble → **C**. Hearth with no lens → **ERR_INCOMPLETE**.

### F13. Adapter validity and adapted specs

The adapter_rule formula is defined as:

`adapter_valid = from ≠ INT and to ≠ INT and from ≠ to and (flange_centi[from] − flange_centi[to]) ≥ ADAPTER_MIN_DEPTH_CENTI and (kind = DUMB or (electronic[from] and electronic[to]))`;  `lens_af_eff = (kind = DUMB) ? 0 : max(1, lens.af_class − SMART_AF_PENALTY)` (0 stays 0);  `ois_eff = (kind = DUMB) ? 0 : lens.ois_stops`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| from, to | mount_id | mount table | data file (adapter) | Lens-side and body-side mounts |
| flange_centi | map mount → int | 1600–4650 | data file (mount table) | Flange focal distance ×100 |
| ADAPTER_MIN_DEPTH_CENTI | int | 50–300; default 100 (1.0 mm) | data file (tuning) | Thinnest buildable adapter |
| electronic | map mount → bool | — | data file (mount table) | The mount has electronic contacts |
| SMART_AF_PENALTY | int | 0–2; default 1 | data file (tuning) | AF classes lost through a smart adapter |
| lens_af_eff, ois_eff | int | 0–5 | calculated | Lens AF class and OIS after the adapter |

**Output Range:** `adapter_valid` is a bool checked in CI for every adapter model (an invalid adapter cannot leave `DRAFT`); `lens_af_eff` 0–5; `ois_eff` 0–5. A lens with AF class 0 stays manual through any adapter.
**Example:** H42 → KR: 4550 − 2000 = 2550 ≥ 100, DUMB → valid; Hollin 58 af 0 → 0, OIS 0. KR → NZ smart: 2000 − 1600 = 400 ≥ 100, both electronic → valid; KR 85 af 3 → **2**, OIS 0 → 0. NZ → KR: 1600 − 2000 = −400 → **invalid** (the lens would sit too close to the sensor to focus to infinity).

### F14. Silhouette hints (art input, display only)

The silhouette formula is defined as:

`front_dia_mm = max(DIA_MIN_MM, ceil(f_max_mm / N_tele × PUPIL_TO_FRONT_PERMILLE / 1000))`;  `length_mm = length_override_mm if set, else clamp(LEN_BASE_MM + floordiv(f_max_mm × LEN_PER_MM_PERMILLE, 1000), LEN_MIN_MM, LEN_MAX_MM)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| f_max_mm / N_tele | float (mm) | 0–110 | data file (lens) | Entrance pupil at the long end |
| PUPIL_TO_FRONT_PERMILLE | int | 1000–1400; default 1150 | data file (art tuning) | Front element to pupil ratio |
| DIA_MIN_MM | int | 40–60; default 46 | data file (art tuning) | Smallest front diameter |
| LEN_BASE_MM, LEN_PER_MM_PERMILLE | int | default 30, 600 | data file (art tuning) | Barrel length model |
| LEN_MIN_MM, LEN_MAX_MM | int | default 20, 240 | data file (art tuning) | Length clamp |
| front_dia_mm, length_mm | int (mm, model scale) | 20–240 | calculated | Proportions for asset-forge lens recipes and the side-silhouette icon |

**Output Range:** proportions only; the art bible owns shape and style. It makes the art bible rule (§3.4: *"Length and front diameter must express the specs"*) a formula.
**Example:** KR 85 f/1.4: 85 / 1.4 = 60.7 × 1.15 = 69.8 → **70 mm** front, length 30 + 51 = **81 mm**. KR 50 f/1.8: 27.8 × 1.15 = 32 → **46 mm** (minimum), length **60 mm**. So the fast 85 is visibly fatter and longer than the fifty.

## Edge Cases

- **If a model has no tier, an unparseable tier, or a tier key in the wrong case**: catalog load fails on that model with its `model_id` and the field name, and CI fails. The model never exists at runtime as "tier C by default" (ladder Core Rule 9).
- **If a phone module's tier differs from its phone's tier**: load fails. Modules always inherit the phone's tier.
- **If a released model's tier is edited in data without a logged migration**: CI fails by comparing against the last released catalog (as the ladder's identity check does). Only the migration path in Core Rule 7 can change it.
- **If a released `model_id` is removed, renamed or reused**: CI fails. Retire it instead.
- **If a lens's mount differs from the body's and no matching adapter is equipped**: the loadout is `INVALID_MOUNT`; Inventory & Loadout refuses the equip on the server; the previous loadout stays equipped.
- **If two adapters are equipped, or an adapter's mounts do not match the lens and body**: `INVALID_ADAPTER`; the equip is refused. Adapters never chain, even if each step would be valid.
- **If an adapter is equipped but the lens fits the body directly**: the adapter is unequipped automatically by the loadout and the loadout is `VALID_DIRECT` (an unnecessary adapter never lowers the gear ceiling).
- **If a body has no lens**: `INCOMPLETE`; the shutter is disabled in the HUD and the server rejects any `SHUTTER` for it; `gear_ceiling` returns `ERR_INCOMPLETE`, never the body's tier alone.
- **If a phone is equipped together with a lens or adapter**: impossible by data (integrated mounts accept nothing); the server refuses the equip with `INVALID_MOUNT`.
- **If an APS-C lens is mounted on a full-frame body**: allowed; `crop_eff` becomes 1500 (F1) and the body shoots in crop mode; the HUD shows "crop mode". Nothing is penalised beyond the real crop.
- **If a full-frame lens is mounted on a medium-format body (or any lens with a smaller image circle than the body)**: allowed; `crop_eff` takes the lens's coverage (F1).
- **If a reachable body and lens pairing gives an equivalent focal length outside 12–450 mm**: CI fails, naming the pair, because Player Movement's FOV range (3–90°) would be exceeded. Adding such gear requires Movement and Camera Model to widen their ranges first.
- **If the player zooms a variable-aperture lens in while set to its widest aperture**: the aperture follows `n_max_at(f)` (F4) and stops down automatically, as real lenses do; when they zoom back out, the aperture does not open again by itself (it stays at the value now set). The HUD shows the change.
- **If a `SHUTTER` requests an aperture wider than `n_max_at(f)` at its focal length, or a focal length outside the lens range**: Network rejects it with `ERR_OUT_OF_RANGE` (Network rule 25); the shot is not consumed.
- **If a requested aperture is between third stops**: Camera Model only offers third-stop values; the server rejects any value not on `THIRD_STOPS` as `ERR_OUT_OF_RANGE`.
- **If the lens is manual focus (AF class 0), natively or through a DUMB adapter**: `af_ms = MANUAL`; autofocus input does nothing, and focusing is by hand (Camera Model). Phone AUTO mode never applies to camera bodies.
- **If the phone's digital zoom is pushed past `digital_zoom_max_milli`, or used on the ultrawide**: it clamps to the maximum on the main module; the ultrawide has no digital zoom. Switching modules takes `module_switch_ms`.
- **If NIGHT mode is active and the subject or camera moves before `NIGHT_MODE_HOLD_MS`**: the stack ends early and the shot uses the normal exposure; nothing extra is rolled or charged.
- **If PORTRAIT mode is used with no detectable subject**: no synthetic blur is applied; the shot is a normal AUTO shot.
- **If a recipe names a `model_id` or `spec_rev` the server cannot load**: the server rejects the capture, or for a stored photo marks it "needs re-render" and keeps the stored score; it never substitutes another model. A client with an older `catalog_version` shows that gear with a neutral silhouette and "?" tier badge until it updates.
- **If a model is retired while a player owns it**: the instance keeps working, trading and displaying; it is simply no longer produced.
- **If a dormant (above-cap) model appears in a client message or a client inventory**: the server ignores the client copy; the server never minted it, so the server inventory cannot contain it, and the message counts as an invalid-item violation in Network.
- **If `enabled_cap` is raised (for example to S)**: dormant S models become producible with no data change; Gear Shop, Supply Caps and Pricing must already have rows for them (the ladder's fail-fast rule for tier-keyed tables).
- **If a cosmetic variant differs from its base in tier or any spec field**: CI fails. A variant can never be a stronger version of its base.
- **If a model exceeds its tier's spec budget (F11)**: it cannot leave `DRAFT`; CI names the model and which point category pushed it over.
- **If a spec revision changes a released lens (for example AF class 3 → 2)**: owned instances use the new revision from that release; photos keep their stored revision and score; the change appears in patch notes and on the gear card history.
- **If `battery_shots` is reached while battery depletion is disabled (MVP default, D12)**: nothing happens; the HUD shows no battery meter.
- **If gear is used in RAIN and is not `sealed`**: no effect in MVP; Gear Condition (Alpha) owns any effect.

## Dependencies

**Upstream (this system depends on):**

| System | Hard / soft | Interface | GDD status |
|---|---|---|---|
| Rarity Tier Ladder | Hard | tier IDs and `parse` for every model; `tier_min` (F12); `is_enabled` (rule 20); display tokens | Designed (In Design) |

The catalog reads no other system. It reads the art bible (§3.4, §7.3, §8.2, A3, A15) as a content standard, not a system.

**Downstream (systems that depend on this one):**

| System | Hard / soft | Interface | GDD status |
|---|---|---|---|
| Camera Model: Viewfinder & Exposure | Hard | specs, setting ranges, F1–F6, F8, F10, phone modes | Not started |
| Inventory & Loadout | Hard | fit rules, loadout validity, adapter effects, `model_id` | Not started |
| Photo Scoring | Hard | specs per `model_id` + `spec_rev`, F5/F6, `iso_clean`, mode flags | Not started |
| Capture Tier Resolution | Hard | `gear_ceiling` (F12) | Not started |
| Starting Choice | Hard | starting phone and entry kit model IDs | Not started |
| Gear Shop | Hard | producible models, tier, kind | Not started |
| Viewfinder HUD | Hard | focal range, FOV, aperture range, modes | Not started |
| Zone Access & Travel (VS) | Soft | specs as optional access hints | Not started |
| Gear Condition & Maintenance (Alpha) | Hard | `sealed`, tier, kind | Not started |
| Supply Caps & Gear Serials (Alpha) | Hard | `model_id`, tier | Not started |
| Gear Crafting (Alpha) | Hard | `model_id`, tier, `release_state` | Not started |
| Network Transport & Server Authority | Soft | setting ranges, `burst_deci`, `catalog_version` | Designed (lists Gear Catalog as soft, rules 25–26) |
| Photo Recipe & Re-render | Soft | `model_id`, `spec_rev`, module, mode, `look_tags` | Not started |
| Shop, Sell & Inventory UI; Leaderboards; Leaderboard & Social UI | Soft (display) | names, brand labels, tiers, card fields, F7/F9/F10 | Not started |

Bidirectional note: Network Transport already lists this system. Rarity Tier Ladder lists Gear Catalog as a hard dependent. Every other downstream GDD must list "depends on Gear Catalog & Specs" when it is authored. The systems index row 5 already records "Depends On: Rarity Tier Ladder"; its status column was not updated by this run (approved to write this one file only).

## Tuning Knobs

| Knob | Current value | Safe range | Affects | Too low / too high |
|---|---|---|---|---|
| `LENS_BUDGET[tier]` | C 2, B 3, A 4, S 5, SS 6, SSS 7 | each 1–10, strictly increasing | How strong a lens may be per tier (power curve) | Too low: no room for fast or zoom lenses at low tiers, so every upgrade is forced up the ladder. Too high: a cheap B lens carries top specs and higher tiers mean only the ceiling. |
| `BODY_BUDGET[tier]` | C 2, B 4, A 6, S 7, SS 8, SSS 9 | each 1–14, strictly increasing | How strong a body may be per tier | As above. Rising by only 1 above A keeps rich-get-richer damped (concept Balance). |
| Spec point thresholds (F11 table) | as listed | keep monotonic | What counts as a premium spec | Loose thresholds let premium specs slip into low tiers. |
| `COC_FF_DUM` | 300 (30 µm) | 290–330 | Depth of field everywhere | Lower: thinner focus, harsher Focus scores. Higher: everything looks sharp, blur matters less. |
| `S_REF` | 2000 mm | 1000–5000 | Blur index (display) | Only changes the displayed comparison number. |
| `T_SUBJECT_US` | 16,667 (1/60 s) | 8,000–33,333 | Low-light reach (display) | Shorter: fast lenses look much better than stabilised zooms. Longer: stabilisation dominates. |
| `STAB_CAP` | 6 stops | 3–7 | Handheld limit | Too high: tripods and Astro long exposures lose meaning. |
| `AF_LENS_MS`, `AF_BODY_PERMILLE` | see F10 | 100–1000 ms; 600–1500 ‰ | Focus speed on moving subjects | Too slow at low tiers: early subjects feel unfair. Too fast everywhere: AF class stops mattering. |
| `ADAPTER_MIN_DEPTH_CENTI` | 100 (1.0 mm) | 50–300 | Which adapters can exist | Above 230 the KR → FX adapter becomes impossible. |
| `SMART_AF_PENALTY` | 1 | 0–2 | Cost of adapting across brands | 0: adapting is free, so brands blur together. 2: the smart adapter is nearly useless. |
| `NIGHT_MODE_STOPS` | 3 | 0–4 | Phone low-light reach on still scenes | 4+: the phone out-reaches A gear at night and the camera path loses its niche. |
| `NIGHT_MODE_HOLD_MS` | 2000 | 1000–4000 | Phone night-mode difficulty | Too short: night mode becomes a free low-light button for moving subjects. |
| `PORTRAIT_SYNTH_BLUR_BP` | 250 | 100–400 | Phone fake blur strength | Above about 300 it beats the real KR 50 on APS-C (297 bp), devaluing real glass. |
| `digital_zoom_max_milli` (phone) | 2000 | 1000–3000 | Phone reach | Too high: the phone replaces the tele zoom side-grade. |
| `F_EQ_MIN`, `F_EQ_MAX` | 12, 450 mm | must match Player Movement / Camera Model FOV range | Which gear can be authored | Widening needs those systems to agree first. |
| `swap_ms` per mount | 1200 bayonet, 1500 MF, 2500 thread | 500–4000 | Cost of changing lens in the field | Too long: players never swap and miss the "which glass" choice. Too short: no reason to own a zoom. |
| Catalog breadth (models per tier) | C 4, B 9, A 5 enabled | content decision | Size of the exhaustible gear sink | Too few: money has nothing to buy soon. Too many: choice overload for new players. |

**Not knobs:** model IDs, mount IDs and released tiers are permanent identity. Prices, caps, wear and score effects are knobs in their owning GDDs.

## Visual/Audio Requirements

- **Silhouettes express specs.** Lens models and icons use F14 proportions so length shows focal length and front diameter shows speed (art bible §3.4, §7.3). Pancakes use `length_override_mm`.
- **No logos in geometry or textures.** Brand marks are a separate decal slot and UI label driven by `brand_id` (art bible A3, §8.2). Body shapes copy no real product: Kanro rounded grips, Nokta angular, Fujin flat-top with top dials, Hollin chrome-ringed barrels, Lumo a rounded slab with a camera bump (art bible §3.4 vocabulary).
- **Mount index dot.** Each mount has an index-dot colour token on the lens and body ring and in UI, plus its `display_code`; the art bible defines the token colours. Colour is never the only cue (the code is always shown).
- **Asset names.** `gear_` + `model_id`, brand-free (art bible §8.2, A15).
- **Look tags.** `SWIRL_BOKEH`, `WARM_FLARE`, `SOFT_CORNERS` map to re-render shader parameters (technical-artist), and must be visible in a thumbnail-sized photo. The custom depth blur used by the prototype on Compatibility/Web is the base the bokeh tags modify (UNVERIFIED for cost on low-end devices; prototype finding).
- **Audio.** Each body or phone has a `shutter_sound_id` (`ML_SOFT` mirrorless, `ML_LEAF` Fujin, `THREAD_CLICK` not used, `PHONE_SYNTH`), and each mount type a mount/unmount sound (bayonet twist-click; thread a slower screw). Audio owns the sounds; the catalog stores only IDs. Shutter sounds must be gentle and cozy, never mechanical-aggressive.

## Game Feel

The catalog's numbers set feel targets that Camera Model must deliver:

- **Speed differences are felt, not read.** The difference between 517 ms (kit) and 320 ms (KR 85 on Lantern) must be noticeable on a subject that turns away; Camera Model plays focus confirmation at the F10 time.
- **The aperture dial clicks in third stops** (`THIRD_STOPS`); a variable-aperture zoom audibly or visibly stops down as it zooms (F4).
- **Changing lenses takes a breath** (`swap_ms`), with the viewfinder unavailable for that time, so the choice of lens before a moment matters. Thread mounts are slower on purpose: the vintage lens is a commitment.
- **Manual focus is calm and precise:** a focus ring with focus peaking, never a minigame with a timer.
- **The phone feels effortless:** instant AUTO, one tap between modules, and NIGHT mode's hold shown as a gentle filling ring.

## UI Requirements

- **Gear card (shop, inventory, loadout).** Side silhouette icon; name (display name plus brand label); tier badge (ladder badge component); mount code with index dot; a one-line "what it's for"; key specs in photographer language (for example "50 mm · f/1.8 · KR mount · full-frame lens"); and, for the current body, the derived stats: equivalent focal range and FOV, blur index (F7) as a 5-step bar, low-light reach (F9) phrased against the day ("holds until blue hour", "reaches into the night" using World F12 band EVs), and AF speed (F10) as "quick / steady / slow / manual".
- **Fit status on every lens card**, against the equipped body: "Fits your Hearth", "Fits with the H42 → KR ring (manual focus)", or "Doesn't fit the KR mount". Never hide gear that does not fit.
- **Gear ceiling preview.** Before buying or equipping, the card shows the ceiling the new loadout would have ("Your gear ceiling would be B"). If the ceiling is the binding limit, the wording follows the ladder rule ("Your lens is ready for more"), never "Locked".
- **Compare view.** Two models side by side with the same derived stats.
- **Dormant models** are not shown in the shop in MVP. If they appear anywhere (for example a gallery photo from a test build), they use the normal badge.
- **Phone mode switch** (AUTO / NIGHT / PORTRAIT) and module switch (0.5× / 1× / 2×) belong to the Viewfinder HUD; the catalog supplies the list.
- **Accessibility.** Specs are text, not colour; FOV and blur bars carry numbers on hover or focus.

📌 **UX Flag — Gear Catalog & Specs**: the gear card, fit status and compare view are shared components. Run `/ux-design` for them (with the Shop, Sell & Inventory UI spec) before writing UI epics.

## Cross-References

| Referenced document | What is used | Where |
|---|---|---|
| `design/gdd/game-concept.md`: Gear and economy (Starting choice, Gear specs, Brands, Balance) | Phone vs camera, real spec logic, mounts and adapters "that cost some quality", invented makers, anti rich-get-richer, never pay-to-win | Overview, Player Fantasy, Core Rules 5, 8, 16–18, 23 |
| `design/gdd/game-concept.md`: Rarity system (Capture rule, Limited gear), Risks | Gear ceiling = lower of body and lens; supply caps are not owned here; "never sell tier" | Core Rules 3, 8, 17; F12 |
| `design/gdd/systems-index.md`: row 5, rationale 5, dependents, A10, B1, B3, B5, B6 | Field list; adapters, vintage looks and the phone inside this system (A10); brand question (B1, decided); phone path (B3, open); cap scope (B5) and breakage (B6) left to their owners | Core Rules 9–13, Decisions |
| `design/gdd/rarity-tier-ladder.md`: Core Rules 1, 7, 8, 9; Edge Cases; Open Question 1 | Tier IDs; enabled cap; gear is a ceiling; no null tier; the phone is tier C | Core Rules 3–5, 11, 20; F12 |
| `design/gdd/world-time-weather-light.md`: Summary, F12 | `scene_ev_deci` unit and night EV 1.0 | F9, UI Requirements |
| `design/gdd/network-transport-server-authority.md`: rules 20, 25–26, F1b | Server-known setting ranges; `burst_fps` 0.5–20; phone example burst 3 fps | Core Rules 19, 22; phone burst |
| `design/gdd/player-movement-exploration.md`: F6 | vfov = 2·atan(12 / f) for full frame; FOV range ~3–90° | F2, F3 |
| `design/art/art-bible.md`: §3.4, §7.3, §8.2, A3, A15 | Lens silhouettes show specs; no logos; brand-free `gear_` names | Core Rule 2, F14, Visual/Audio |
| `prototypes/aperture-concept/README.md` | Focal 24–200 mm, f/1.4–16, COC-based custom depth blur works on Compatibility/Web | F5, F6, Visual/Audio |

## Acceptance Criteria

Tags: **[Logic]** automated gdUnit4 unit test (suggested name given) · **[Integration]** integration test or documented playtest · **[UI]** retained screenshot in `production/qa/evidence/`. Criteria marked *(provisional)* depend on a system that is not designed yet.

**A. Identity and data validation (Core Rules 1–8)**

1. [Logic] **GIVEN** the MVP catalog, **WHEN** it loads, **THEN** every model has a tier that `parse` accepts, including `phone_basic_c_01` = "C" and both its modules = "C". `test_catalog_every_model_has_valid_tier_loads`
2. [Logic] **GIVEN** a fixture model with tier "" or "sss", **WHEN** the catalog loads, **THEN** loading fails with an error naming the `model_id` and the `tier` field, and no model defaults to C. `test_catalog_missing_tier_fails_load`
3. [Logic] **GIVEN** a phone fixture whose module tier differs from the phone tier, **WHEN** it loads, **THEN** loading fails. `test_phone_module_tier_mismatch_fails_load`
4. [Logic] **GIVEN** every `model_id` in the catalog, **WHEN** checked against the pattern `^(body|lens|phone|adp)_[a-z0-9]+(_[a-z0-9]+)*_(c|b|a|s|ss|sss)_[0-9]{2}$` and the brand name list, **THEN** all match the pattern, the tier segment equals the model's tier in lowercase, and none contains a brand name. `test_model_ids_brand_neutral_and_match_tier`
5. [Integration] **GIVEN** the catalog of the last released build, **WHEN** CI compares the current catalog, **THEN** it fails if a released `model_id` was removed, renamed or its tier changed without a migration record, and passes when models were only added, retired or given a new `spec_rev`.
6. [Logic] **GIVEN** a cosmetic variant fixture whose `af_class` differs from its base, **WHEN** validation runs, **THEN** it fails naming the field; a variant identical in all spec fields and tier passes. `test_cosmetic_variant_spec_mismatch_fails`
7. [Integration] *(provisional: Photo Recipe)* **GIVEN** a photo shot with `lens_std50_f18_b_01` rev 1, **WHEN** rev 2 changes its AF class and the server re-scores the photo, **THEN** it uses rev 1 specs and the stored score is unchanged, while a newly equipped instance uses rev 2.

**B. Spec budget (F11)**

8. [Logic] **GIVEN** each MVP and dormant model, **WHEN** F11 runs, **THEN** every model passes, and the computed points equal the "Points / budget" column of Core Rules 26–27 (for example KR 85 = 4, Lantern = 6, phone main module = 2). `test_spec_points_mvp_catalog_match_table`
9. [Logic] **GIVEN** the Lantern with `ibis_stops` changed to 5, **WHEN** F11 runs, **THEN** BSP = 7 and the model fails the A budget (6). `test_spec_budget_exceeded_fails_validation`
10. [Logic] **GIVEN** the phone main module (f/1.8, crop 5600), **WHEN** AP is computed, **THEN** `n_eq` = 100 and AP = 0. `test_aperture_points_use_equivalent_f_number`

**C. Optics (F1–F7)**

11. [Logic] **WHEN** F1 runs, **THEN** KR 50 on the Hearth gives 1500 and the KR-S kit on the Lantern gives 1500. `test_effective_crop_takes_larger_crop`
12. [Logic] **WHEN** F2 runs, **THEN** KR 50 on the Hearth = 75 mm, the phone main = 26 mm (52 mm at 2× digital zoom), the phone ultrawide = 13 mm, and KR 100–300 at 300 mm on the Hearth = 450 mm. `test_equivalent_focal_rounds_half_up`
13. [Logic] **GIVEN** 200 mm full frame, **WHEN** F3 runs, **THEN** vfov = 6.87° ± 0.01, matching Player Movement F6; and 75 mm equivalent gives vfov 18.18° ± 0.01 and hfov 26.99° ± 0.01. `test_fov_200mm_full_frame_returns_6_87deg`
14. [Logic] **GIVEN** every reachable direct and adapted pairing of enabled models, **WHEN** CI computes f_eq at both zoom ends, **THEN** all lie in 12–450 mm. `test_all_reachable_pairings_within_fov_bounds`
15. [Logic] **GIVEN** the KR-S 18–45 f/4.5–6.3, **WHEN** `n_max_at` runs at 18, 30 and 45 mm, **THEN** it returns 45, 56 and 63; a prime returns `n_wide_deci` at its only focal length. `test_n_max_at_zoom_snaps_up_to_third_stop`
16. [Logic] **WHEN** F5 runs, **THEN** crop 1500 → 200, 5600 → 54, 790 → 380. `test_coc_scales_with_crop_rounded`
17. [Logic] **GIVEN** 50 mm, f/1.8, c = 0.020 mm, s = 2000 mm, **WHEN** F6 runs, **THEN** H = 69,494 ± 1 mm, D_near = 1,945 ± 1 mm, D_far = 2,058 ± 1 mm; and when s ≥ H, D_far is infinity. `test_dof_50mm_f18_aps_c_matches_reference`
18. [Logic] **WHEN** F7 runs, **THEN** KR 85 on the Lantern = 749, KR 50 on the Hearth = 297, phone main = 9, phone in PORTRAIT = 250. `test_blur_index_reference_loadouts`

**D. Low light and autofocus (F8–F10)**

19. [Logic] **WHEN** F8 runs, **THEN** the kit at 18 mm on the Hearth = 296,296 µs and KR 50 on the Hearth = 13,333 µs; and a lens with OIS 3 on a body with IBIS 3 uses 3 stops, not 6. `test_handheld_limit_stabilisation_does_not_stack`
20. [Logic] **WHEN** F9 runs, **THEN** kit on Hearth = 52, KR 50 on Hearth = 29, KR 85 on Lantern = 9, phone = 46, phone NIGHT = 16. `test_low_light_reach_reference_loadouts`
21. [Logic] **WHEN** F10 runs, **THEN** kit on Hearth = 517 ms, KR 85 on Lantern = 320 ms, KR 85 via smart adapter on Kestrel = 450 ms, and Hollin 58 on any body = `MANUAL`. `test_af_time_lookup_and_manual`

**E. Fit, adapters and the gear ceiling (Core Rules 14–17; F12, F13)**

22. [Logic] **WHEN** F13 validates every adapter, **THEN** H42 → KR, H42 → FX and KR → NZ are valid; a fixture NZ → KR adapter (flange −4.0 mm) and a fixture INT → KR adapter are invalid. `test_adapter_flange_rule_valid_and_invalid`
23. [Logic] **GIVEN** a SMART adapter and KR 85 (AF 3, OIS 0), **WHEN** adapted specs are computed, **THEN** AF = 2 and OIS = 0; with a DUMB adapter and a fixture lens with AF 3 and OIS 3, **THEN** AF = 0 and OIS = 0. `test_adapter_effects_dumb_and_smart`
24. [Logic] **WHEN** loadout validity is evaluated, **THEN** Hearth + KR 50 = `VALID_DIRECT`; Hearth + H42 ring + Hollin 58 = `VALID_ADAPTED`; Hearth + Hollin 58 with no ring = `INVALID_MOUNT`; Hearth + two adapters = `INVALID_ADAPTER`; Hearth alone = `INCOMPLETE`; phone alone = `VALID_PHONE`. `test_loadout_validity_states`
25. [Logic] **WHEN** F12 runs, **THEN** Hearth + kit = C; Hearth + KR 50 = B; Lantern + KR 50 = B; Lantern + KR 85 = A; Lantern + H42 ring + Hollin 58 = B; Kestrel + smart adapter + KR 85 = A; phone = C; Hearth alone = `ERR_INCOMPLETE` (never B). `test_gear_ceiling_lowest_of_loadout`
26. [Logic] **GIVEN** a loadout with an adapter equipped where the lens fits the body directly, **WHEN** validity is evaluated, **THEN** the adapter is dropped and the gear ceiling is computed without it. `test_unneeded_adapter_never_lowers_ceiling`
27. [Integration] *(provisional: Inventory & Loadout, Network)* **GIVEN** a client that equips Hollin 58 on the Hearth without a ring, **WHEN** the server processes it, **THEN** the equip is refused with `INVALID_MOUNT` and the previous loadout stays equipped.

**F. Producibility, cap and ranges (Core Rules 19–22)**

28. [Logic] **GIVEN** `enabled_cap = "A"`, **WHEN** the producible list is built, **THEN** it contains the 18 enabled models and none of the 5 dormant ones; with the cap set to "S" in a fixture, `lens_tele200_f28_s_01` and `body_ff_s_01` are added with no data change. `test_producible_models_respect_enabled_cap`
29. [Logic] **GIVEN** the Hearth + KR-S kit at 45 mm, **WHEN** setting ranges are requested, **THEN** focal 18–45 mm, aperture f/6.3–f/22, ISO 100–12800 and shutter 250 µs–30 s are returned. `test_setting_ranges_follow_loadout_and_focal`
30. [Integration] *(provisional: Network)* **GIVEN** the kit zoom at 45 mm in the server loadout, **WHEN** a `SHUTTER` requests f/4.5, **THEN** it is rejected with `ERR_OUT_OF_RANGE` and the shot is not consumed.
31. [Integration] **GIVEN** a client with an older `catalog_version` that receives a photo using an unknown `model_id`, **WHEN** it displays the gear, **THEN** it shows a neutral silhouette and a "?" badge and prompts an update; the server's stored data is unchanged.
32. [Logic] **GIVEN** the phone, **WHEN** `burst_deci` is read for Network F1b, **THEN** `burst_fps` = 3.0, and every model's `burst_deci` / 10 is within 0.5–20. `test_burst_values_within_network_range`

**G. UI**

33. [UI] *(provisional: Shop, Sell & Inventory UI spec)* **GIVEN** the Hearth equipped, **WHEN** the shop shows KR 50, Hollin 58 and Nokta NZ 24–70, **THEN** their fit lines read "Fits your Hearth", "Fits with the H42 → KR ring (manual focus)" and "Doesn't fit the KR mount", and each card shows the gear ceiling preview. Evidence: screenshot.
34. [UI] **GIVEN** lens icons generated for KR 50, KR 85 and KR 100–300, **WHEN** shown side by side, **THEN** the 85 has the wider front and the 100–300 is the longest, following F14. Evidence: screenshot.
35. [Integration] **GIVEN** every display string for gear, **WHEN** CI greps the gear data, assets and UI strings for a list of real camera brand names, **THEN** none is found.

Coverage notes: score effects of specs (noise, portrait artefacts, look tags) are tested in Photo Scoring. Battery drain, focus behaviour and night-mode stacking behaviour are tested in Camera Model.

## Open Questions

> 2026-11-05: the Kestrel is 10 fps to match Network's `SHUTTER_RATE_CAP`; the dormant 80 mm is f/1.8 so it sits on `THIRD_STOPS`. CI must also check that `mfd_mm` exceeds the longest focal length. In F12, `L` is read when `SHUTTER` is validated, not at the capture tick.

| # | Question | Owner | Resolve by |
|---|---|---|---|
| 1 | Phone path (B3): is the phone only a starting tool, or a permanent path with B/A phone models? This GDD supports either: more phones are just more `PHONE` models. | game-designer + user | Before Starting Choice is designed |
| 2 | Trademark screen of the brand names. Working names have real-world near-collisions: "Nokta" (an existing metal-detector maker), "Kanro" (an existing Japanese confectionery company), "Fujin" (sounds close to a major camera maker). Display data only, so renaming is cheap until marketing starts. | producer + legal | Before any public build |
| 3 | Does battery drain exist (D12)? The field is authored; the cozy tone argues against running out mid-encounter. | game-designer (Camera Model GDD) | Camera Model design |
| 4 | Accessories: tripod (Astro long exposures need one), filters (ND, polariser), reflector and flash (the concept's co-op assists). Recommend a later `ACCESSORY` kind in this catalog. | game-designer | Alpha (Co-op Crew Roles) |
| 5 | Should the catalog ever include a third-party lens maker that makes lenses in several mounts (a cheaper side-grade line)? | economy-designer | Vertical Slice |
| 6 | Supply caps per model or per tier (B5), and does broken gear return to supply (B6)? Neither changes catalog data; both change how many models per tier we need. | economy-designer (Supply Caps GDD) | Alpha |
| 7 | Exhaustible sink: the time to buy out the enabled catalog against MVP photo income must be stated in the Currency & Wallet budget table. | economy-designer (Currency & Wallet, Pricing) | Before the shared budget table is locked |
| 8 | Photo resolution (megapixels) is deliberately absent. Is "detail" ever a score input (for example digital zoom loss)? | systems-designer (Photo Scoring) | Photo Scoring design |
| 9 | Data format and client/server sharing of the catalog, and the `catalog_version` handshake. | technical-director → ADR | Architecture phase |
| 10 | Registry: `gear_ceiling` (formula), `phone_basic_c_01` and the starting kit (items), `F_EQ_MIN`/`F_EQ_MAX` and `burst` ranges (constants) cross system boundaries and should be registered in `design/registry/entities.yaml` (not edited in this run). | economy-designer, with user approval | After this GDD is approved |

## Decisions to confirm

> **DECIDED 2026-11-04 (user):** every item = the recommended option. D3: keep the working brand names for now, trademark screen before any public build. D13: entry camera ceiling is C, same as the phone.

- **D1. Tier per model or per item.** (a) **Tier per model: every instance of a model has the same tier; instances add only serial and condition.** Simple to read ("the KR 85 is an A lens"), and supply caps, prices and crafting key cleanly on it. (b) Tier per instance, rolled when the item is made (the same lens can be B or S): more chase, but it is a loot roll, which raises gacha and loot-box concerns and breaks "a badge means the same thing everywhere". (c) Per model, with a small per-instance "grade" (for example a lucky copy) that never changes tier: flavour without randomness in tier, at extra scope. **Recommendation: (a).**
- **D2. What tier means for gear, and how it relates to specs.** (a) **Tier is the optical and build grade (the ceiling), authored per model; specs must fit a per-tier spec budget that rises gently (F11).** Cheap side-grades and "cheap route to a ceiling" models such as the A pancake stay possible. (b) Tier computed from spec points: transparent, but then a long lens is "higher tier" than a fast one and side-grades disappear. (c) No link between tier and specs: maximum freedom, but a C lens could carry SSS specs and the ladder stops meaning quality. **Recommendation: (a).**
- **D3. Brand roster and names.** (a) **Keep the working names Kanro, Nokta and Fujin from the concept, add Hollin (vintage) and Lumo (phone), and run a trademark screen before any public build;** names are display data only, so a rename stays cheap. (b) Rename now to names with no real-world near-collisions (all three working names have one, see Open Question 2). (c) Fewer brands for MVP (Kanro, Hollin, Lumo only), adding Nokta and Fujin later. **Recommendation: (a).**
- **D4. Mount families.** (a) **Seven mounts with real flange-distance logic and brand-neutral IDs (M16, M17, M20, M267, T455, S465 reserved, INT); adapters are possible only from a longer to a shorter flange.** (b) One mount per brand, with adapters defined by a hand-written table and no physical rule. (c) One universal mount (no compatibility rules), which is simpler but drops the "real mount logic" the user asked for. **Recommendation: (a).**
- **D5. First-playable mount scope.** (a) **The entry kit and all three upgrades are Kanro KR (M20), so a new player is never stuck with gear that does not fit; Fujin, Nokta and Hollin are in the MVP catalog for the shop to stock or not.** (b) Two brands in the first playable, to test adapters early. (c) Only Kanro in the MVP catalog. **Recommendation: (a).**
- **D6. Zooms in MVP.** (a) **Yes: a variable-aperture kit zoom, one tele zoom and one mid zoom, with primes kept as the fast choice.** (b) Primes only ("zoom with your feet"), which is purer, but the prototype already used 24–200 mm zoom and real kits are zooms. (c) Zooms, constant aperture only (simpler, loses the F4 trade-off). **Recommendation: (a).**
- **D7. The phone.** (a) **One tier-C phone (Lumo Pebble) with two fixed modules (26 mm and 13 mm equivalent), always-on AUTO assist, NIGHT and PORTRAIT computational modes, and 2× digital zoom; modules inherit the phone's tier and never separate.** This answers ladder Open Question 1. (b) One module and no computational modes: less scope, but the phone has no niche and becomes a trap. (c) A phone line with B and A models now (the permanent phone path, open question B3). **Recommendation: (a).**
- **D8. How an adapter affects the gear ceiling.** (a) **The adapter is a third member of the `tier_min` set (F12), plus an AF penalty; a cheap B ring caps a loadout at B.** (b) An adapter steps the ceiling down one tier (`tier_step −1`), whatever its own tier. (c) Adapters have no tier effect; the cost is specs only (AF and OIS). **Recommendation: (a).** It makes the concept's "adapters cost some quality" readable on one badge, and Capture Tier Resolution must accept that the gear ceiling is a catalog function, not simply min(body, lens).
- **D9. Adapter rules.** (a) **At most one adapter; the flange rule with a 1.0 mm minimum; DUMB adapters (manual focus, no lens OIS) and SMART adapters (AF −1, OIS kept, both mounts electronic).** (b) Any adapter pair a designer lists, with no physical rule. (c) No adapters in MVP. **Recommendation: (a).**
- **D10. Spec changes after release.** (a) **Specs frozen per `spec_rev`; instances follow the latest revision; photos keep the revision they were shot with; tier changes only by signed-off migration.** (b) Live edits to specs (simple, but old photos change score silently). (c) Every change creates a new model ID (safe, but clutters the catalog and splits ownership). **Recommendation: (a).**
- **D11. Frame aspect ratio.** (a) **3:2 for every body and the phone in MVP** (one composition grid for Scoring and one FOV formula). (b) 4:3 for the phone, as real phones use, at the cost of a second composition grid. **Recommendation: (a).**
- **D12. Battery.** (a) **`battery_shots` is authored, but depletion is off in MVP** (cozy tone; no running out mid-encounter). (b) Depletion on, with charging in town as a light routine. (c) Remove the field. **Recommendation: (a).**
- **D13. Entry camera kit tiers.** (a) **Body B (Kanro Hearth) and kit lens C, so the starting ceiling is C, the same as the phone; the first B lens is the "buy something that changes what you can capture" moment.** (b) Body and kit lens both B, so the camera starts one tier above the phone (more reason to pay, but makes the phone look like a trap). (c) Both C. **Recommendation: (a).**
- **D14. Phone burst rate.** (a) **3.0 fps, matching Network F1b's phone example.** (b) 10 fps, closer to real phones, which makes the phone better than the entry body for action. **Recommendation: (a).**
- **D15. Do vintage look tags affect the score?** (a) **No: look tags change only the render, plus optional client requests and themes later; they are a style side-grade.** (b) A small score bonus in matching themes. **Recommendation: (a).**
- **D16. Low-light reach stat.** (a) **Use the slower of the handheld limit and 1/60 s, so the stat describes a living subject, where fast lenses matter.** (b) Use the pure handheld limit, which makes stabilised zooms look better than fast primes. **Recommendation: (a).**
- **D17. Model and mount IDs.** (a) **Brand-neutral IDs by kind, spec and tier (`lens_std50_f18_b_01`, `M20`), matching the art bible's asset rule.** (b) IDs that include the brand (`lens_kanro_50_f18`), easier to read but a brand rename would touch every stored record. **Recommendation: (a).**
- **D18. Weather sealing.** (a) **The `sealed` field is authored and counts in the spec budget, but has no effect in MVP; Gear Condition (Alpha) gives it meaning in RAIN.** (b) An MVP effect now (for example unsealed gear cannot shoot in rain), which is a harsh rule for a cozy game. (c) Remove the field. **Recommendation: (a).**
