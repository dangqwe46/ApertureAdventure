# Visual Entity & Screen Inventory

> Generated: 2026-11-05. Updated: 2026-11-07 for the 3D stylized Quaternius direction (art bible Revision 2026-11-05, 8.10 to 8.12)
> Sources: design/art/art-bible.md; Visual/Audio and UI Requirements sections of the 10 designed GDDs in design/gdd/, plus design/gdd/photo-recipe-rerender.md (Visual/Audio only; it appeared untracked during this run); design/gdd/subject-spirit-behaviour.md (Rule 4 roster); design/gdd/gear-catalog-specs.md (Rules 26-27); design/gdd/game-concept.md; design/gdd/systems-index.md
> Asset IDs, priorities and routes live in design/assets/asset-manifest.md. Audio rows are descriptions only.

## How this inventory was produced (read first)

| Step `/asset-spec` normally runs | What happened |
|---|---|
| User reviews the proposed list (Phase 0b Step 3) | **Not done.** The user could not be asked in this run. Every row is a proposal. |
| `art-director` and `technical-artist` both consulted (`modes.rigor: full`) | **art-director not consulted.** Written by technical-artist alone, so descriptions are anchored to the art bible only. |
| Named entities from `design/registry/entities.yaml` | Registry header read; species and gear taken from their owning GDDs instead. |
| Systems without a GDD | **Not sourceable.** 11 of the 21 MVP systems are Not Started in the systems index (Photo Recipe, Photo Scoring, Capture Tier Resolution, Starting Choice, Gallery, Photo Pricing, Gear Shop, Capture Encounter, Viewfinder HUD, Darkroom & Gallery UI, Shop UI). Only Photo Recipe now has a GDD. The other rows come from the art bible or the systems index and are marked provisional. Expect additions. |

## Assumptions

| # | Assumption | Alternative |
|---|---|---|
| I1 | The concept's "first playable version" is split into a smaller `First playable` tier and `MVP`, because the request asked for both as separate priorities. | Treat them as one tier. |
| I2 | Audio: SFX & Ambience is a Vertical Slice system, but the shutter, the anticipation tone, the decisive bell, footsteps and viewfinder cues are pulled forward. The Subject GDD says timing must never depend on sight alone, and footsteps are the main feedback for presence. | Leave all audio to Vertical Slice and ship MVP silent. |
| I3 | Four NPC clients are assumed, using the art bible's four role props. | The Photo Pricing GDD sets the roster. |
| I4 | Interiors (darkroom, gallery, shop) are 3D rooms, per art bible 4.5 and 6.3. | Screen-only menus would remove several rows. |
| I5 | Display names are the GDD placeholders (Subject Open Question 8). IDs are neutral, so a rename touches no file name except where the species ID itself changes. | Wait for narrative-director. |

## Open items found while building this list

- **Mount index colours:** the Gear GDD says the art bible defines the mount token colours; it does not yet.
- **Skin and hair now come from the packs:** art bible 4.2 still has no skin stop, so the pack maps are graded to the palette (4.1). The outfit pack ships only the Dark skin map for hands, while the bases have Dark and Light.
- **Characters are over budget:** every outfit with a head is above the 15,000 limit in 8.3. Figures are in the character spec.
- **Art bible 5.1 is out of date:** it still calls outfits open. The user has since chosen Modular Character Outfits (Peasant, Ranger).
- **`BOUNDS_MM` has no values:** the Subject GDD names it per species but gives none. Proposed values are in the character spec.
- **Music:** nothing in the designed docs asks for it.

## Entities

| # | Asset ID | Name | Type | Description | Source | Status |
|---|---|---|---|---|---|---|
| 1 | ASSET-001 | Player photographer, placeholder | Character | Stiff jointed figure, no skeleton or animation. Superseded by ASSET-002; kept for the record only | Art bible 5.1, A5 | Superseded |
| 2 | ASSET-002 | Player photographer, final | Character | Rigged Universal Base Characters head and hair in a Modular Character Outfits outfit, keeping its textures, graded to palette | Art bible 5.1, 8.10 | Needed |
| 3 | ASSET-003 | Player locomotion clips | Animation | Idle, walk, hurry, sneak idle, sneak walk and soft landing from Universal Animation Library. Stand and sneak transition is a blend; wade is a slowed walk | Movement GDD Visual/Audio; Art bible 8.10 | Needed |
| 4 | ASSET-004 | Player camera clips | Animation | Raise to eye, hold phone up, viewfinder idle, lower and glance at back screen. In neither animation library | Movement GDD Visual/Audio; Art bible 5.1 | Needed |
| 5 | ASSET-005 | Player traversal clips | Animation | Scramble or vault at 0.8 s, from `CLIMBUP 1M` in Universal Animation Library 2. Ladder moved to ASSET-173 | Movement GDD Visual/Audio | Needed |
| 6 | ASSET-006 | NPC client, fisher | Character | Pack base and Peasant outfit, one role prop (hat), muted palette. Provisional: client roster not designed | Art bible 5.2; systems index 16 (GDD not started) | Needed |
| 7 | ASSET-007 | NPC client, shopkeeper | Character | Pack base and Peasant outfit, apron role prop. Provisional: Gear Shop GDD not started | Art bible 5.2; systems index 17 (GDD not started) | Needed |
| 8 | ASSET-008 | NPC client, courier | Character | Pack base and Peasant outfit, satchel role prop. Provisional | Art bible 5.2; systems index 16 (GDD not started) | Needed |
| 9 | ASSET-009 | NPC client, archivist | Character | Pack base and Peasant outfit, clipboard role prop. Provisional | Art bible 5.2; systems index 16 (GDD not started) | Needed |
| 10 | ASSET-010 | NPC idle clips | Animation | Idle and small gesture only, from Universal Animation Library | Art bible 5.2 | Needed |
| 11 | ASSET-011 | Player cosmetics | Character | Hat and bag options, jacket and strap colour lists | Art bible 5.1 | Needed |
| 12 | ASSET-012 | Wildlife subjects | Character | Rigged animals. Species not chosen; none are in the MVP roster. The free animal pack is not textured, so it needs checking against the world | Art bible 5.4 | Needed |
| 13 | ASSET-013 | Puffwisp | Creature | Tier C spirit, short trailing wisp. Proposal, to restyle for the textured world | Subject GDD Rule 4 | Restyle proposal |
| 14 | ASSET-014 | Mossmote | Creature | Tier C spirit, two ear-like fins, hovers above moss. Proposal, to restyle for the textured world | Subject GDD Rule 4 | Restyle proposal |
| 15 | ASSET-015 | Driftfin | Creature | Tier B spirit, long tail fin. Proposal, to restyle for the textured world | Subject GDD Rule 4 | Restyle proposal |
| 16 | ASSET-016 | Hearth Echo | Creature | Tier B memory, empty frame of faded light around a half-seen scene. Proposal, to restyle for the textured world | Subject GDD Rule 4 | Restyle proposal |
| 17 | ASSET-017 | Halo Keeper | Creature | Tier A spirit, slow ring orbiting the body. Proposal, to restyle for the textured world | Subject GDD Rule 4 | Restyle proposal |
| 18 | ASSET-018 | Capture Encounter set-piece subject | Creature | Concept's boss-like encounter. Not defined: Capture Encounter GDD not started | Concept; systems index 18 (GDD not started) | Needed |
| 19 | ASSET-019 | Driftfin (gilded) | Creature | Tier S variant, adds a second orbiting part. Disabled data in MVP | Subject GDD Rule 4 | Needed |
| 20 | ASSET-020 | Vesper Halo | Creature | Tier SS, ring, orbiting part, trailing wisp, own event light. Disabled data in MVP | Subject GDD Rule 4 | Needed |
| 21 | ASSET-021 | Aurora Drifter | Creature | Tier SSS, large, two orbiting parts, long wisp. Disabled data in MVP | Subject GDD Rule 4 | Needed |
| 22 | ASSET-022 | Lumo Pebble phone | Item | Rounded slab with camera bump; two modules | Gear GDD Rule 26 | Needed |
| 23 | ASSET-023 | Kanro Hearth body | Item | Entry kit body, rounded grip | Gear GDD Rule 26 | Needed |
| 24 | ASSET-024 | Kanro Lantern body | Item | Upgrade U3, rounded grip | Gear GDD Rule 26 | Needed |
| 25 | ASSET-025 | Kanro KR-S 18-45mm lens | Item | Entry kit zoom | Gear GDD Rule 26 | Needed |
| 26 | ASSET-026 | Kanro KR 50mm f/1.8 lens | Item | Upgrade U1 | Gear GDD Rule 26 | Needed |
| 27 | ASSET-027 | Kanro KR 85mm f/1.4 lens | Item | Upgrade U2; F14 gives 70 mm front, 81 mm length | Gear GDD Rule 26 | Needed |
| 28 | ASSET-028 | Fujin Drift body | Item | Flat top with top dials | Gear GDD Rule 26 | Needed |
| 29 | ASSET-029 | Nokta Kestrel body | Item | Angular body | Gear GDD Rule 26 | Needed |
| 30 | ASSET-030 | Kanro KR 100-300mm lens | Item | Tele zoom | Gear GDD Rule 26 | Needed |
| 31 | ASSET-031 | Kanro KR 40mm Pancake lens | Item | Uses length_override_mm | Gear GDD Rule 26 | Needed |
| 32 | ASSET-032 | Fujin FX 27mm lens | Item | Compact prime | Gear GDD Rule 26 | Needed |
| 33 | ASSET-033 | Fujin FX 33mm lens | Item | Compact fast prime | Gear GDD Rule 26 | Needed |
| 34 | ASSET-034 | Nokta NZ 24-70mm lens | Item | Mid zoom | Gear GDD Rule 26 | Needed |
| 35 | ASSET-035 | Hollin 58mm "Harbour" lens | Item | Chrome-ringed barrel, thread mount | Gear GDD Rule 26 | Needed |
| 36 | ASSET-036 | Hollin 28mm lens | Item | Chrome-ringed barrel, thread mount | Gear GDD Rule 26 | Needed |
| 37 | ASSET-037 | Hollin H42 to KR ring | Item | Adapter ring | Gear GDD Rule 26 | Needed |
| 38 | ASSET-038 | Hollin H42 to FX ring | Item | Adapter ring | Gear GDD Rule 26 | Needed |
| 39 | ASSET-039 | Nokta KR to NZ Smart Adapter | Item | Adapter ring with contacts | Gear GDD Rule 26 | Needed |
| 40 | ASSET-040 | Nokta NZ 200mm f/2.8 lens | Item | Dormant tier S | Gear GDD Rule 27 | Needed |
| 41 | ASSET-041 | Kanro Beacon body | Item | Dormant tier S | Gear GDD Rule 27 | Needed |
| 42 | ASSET-042 | Kanro KR 50mm f/1.2 lens | Item | Dormant tier SS | Gear GDD Rule 27 | Needed |
| 43 | ASSET-043 | Nokta Zenith body | Item | Dormant tier SSS | Gear GDD Rule 27 | Needed |
| 44 | ASSET-044 | Nokta NM 80mm f/1.8 lens | Item | Dormant tier SSS | Gear GDD Rule 27 | Needed |
| 45 | ASSET-045 | Mount index dot and brand decal slot | Item | Per-mount dot colour and swappable brand label. Bible owes the mount token colours | Gear GDD Visual/Audio; Art bible A3 | Needed |
| 46 | ASSET-046 | Lighthouse | Environment | Hero landmark built from kit walls and `Roof_Tower_RoundTiles`, white plaster, emissive lamp, gallery rail anchor for Halo Keeper | Art bible 3.1, 6.1, 8.10, 8.12 | Needed |
| 47 | ASSET-047 | Cliff chunks | Environment | Stylized Nature rocks at large scale for cliff and shore | Art bible 3.1, 6.1, 8.10 | Needed |
| 48 | ASSET-048 | Terrain base | Environment | Coastal village ground mesh built in Godot, with blended ground textures; one small area | Art bible 3.1, 6.1, 6.2 | Needed |
| 49 | ASSET-049 | Gabled house, lived-in | Environment | Half-timbered kit house, tiled gable, doorstep anchor for Hearth Echo | Art bible 3.1, 6.1, 8.10 | Needed |
| 50 | ASSET-050 | Gabled house, shut | Environment | Kit house, closed shutters, vines, uneven brick | Art bible 3.1, 6.1, 8.10 | Needed |
| 51 | ASSET-051 | Gabled house, small | Environment | Smaller kit house for street rhythm | Art bible 3.1, 6.1, 8.10 | Needed |
| 52 | ASSET-052 | Gear shop exterior | Environment | Kit building. Provisional; Gear Shop GDD not started | Art bible 3.1, 6.1, 8.10 | Needed |
| 53 | ASSET-053 | Pier on posts | Environment | Leading line built from kit planks, posts and fence rail. Driftfin anchors, plank footing | Art bible 3.1, 6.1, 8.10, 8.12 | Needed |
| 54 | ASSET-054 | Harbour wall | Environment | Kit brick wall with stone cap, Driftfin anchors | Art bible 3.1, 6.1, 8.10 | Needed |
| 55 | ASSET-055 | Round tree | Environment | Stylized Nature `CommonTree` set; needs a LOD1 | Art bible 3.1, 8.3, 8.10 | Needed |
| 56 | ASSET-056 | Pine tree | Environment | Stylized Nature `Pine` set for the woodland strip; needs a LOD1 | Art bible 3.1, 8.3, 8.10 | Needed |
| 57 | ASSET-057 | Rock set | Environment | Stylized Nature `Rock_Medium` set, Mossmote anchors | Art bible 3.1, 8.3, 8.10 | Needed |
| 58 | ASSET-058 | Moss patch | Environment | Low clover and plant cluster, tinted, for Mossmote anchors | Art bible 3.1, 8.10 | Needed |
| 59 | ASSET-059 | Grass clump | Environment | Stylized Nature grass, instanced in drifts | Art bible 6.3, 8.4, 8.10 | Needed |
| 60 | ASSET-060 | Ladder traversal piece | Environment | Authored traversal point, built from kit timber | Art bible 3.1, 8.10 | Needed |
| 61 | ASSET-061 | Rock scramble and low wall | Environment | Authored traversal points from Stylized Nature rocks and kit stone | Art bible 3.1, 8.10 | Needed |
| 62 | ASSET-062 | Darkroom interior | Environment | Red-lit hub room, kit shell. Provisional; Darkroom GDD not started | Art bible 3.1, 6.1, 8.10 | Needed |
| 63 | ASSET-063 | Gallery interior | Environment | Warm interior, print walls, kit shell. Provisional; Gallery GDD not started | Art bible 3.1, 6.1, 8.10 | Needed |
| 64 | ASSET-064 | Gear shop interior | Environment | Kit shell. Provisional; Gear Shop GDD not started | Art bible 3.1, 6.1, 8.10 | Needed |
| 65 | ASSET-065 | Fence section | Item | Repeated leading line, instanced | Art bible 6.3, 6.4, 8.3 | Needed |
| 66 | ASSET-066 | Signpost, icon only | Item | No text-heavy signage. Kit timber post and board, icon decal | Art bible 6.3, 6.4, 8.3 | Needed |
| 67 | ASSET-067 | Crate | Item | Repeated dressing | Art bible 6.3, 6.4, 8.3 | Needed |
| 68 | ASSET-068 | Bench | Item | Medium prop | Art bible 6.3, 6.4, 8.3 | Needed |
| 69 | ASSET-069 | Rowing boat | Item | Medium prop for the shore. Pirate Kit candidate, style check needed | Art bible 6.3, 6.4, 8.3 | Needed |
| 70 | ASSET-070 | Mooring post | Item | Leaning kit timber, weathering by shape | Art bible 6.3, 6.4, 8.3 | Needed |
| 71 | ASSET-071 | Empty picture frame | Item | Spirit trace; Lumen shimmer in lens view | Art bible 6.3, 6.4, 8.3 | Needed |
| 72 | ASSET-072 | Small cairn | Item | Spirit trace | Art bible 6.3, 6.4, 8.3 | Needed |
| 73 | ASSET-073 | Forgotten lens cap | Item | Photographer trace | Art bible 6.3, 6.4, 8.3 | Needed |
| 74 | ASSET-074 | Darkroom table set | Item | Table and shelves from Fantasy Props. Enlarger and trays moved to ASSET-172 | Art bible 6.3, 6.4, 8.3 | Needed |
| 75 | ASSET-075 | Gallery print frame | Item | Wall-mounted print holder | Art bible 6.3, 6.4, 8.3 | Needed |
| 76 | ASSET-076 | Shop shelf and counter | Item | Gear display from Fantasy Props | Art bible 6.3, 6.4, 8.3 | Needed |
| 77 | ASSET-077 | Found photo marker | Item | Small Paper White rectangle. Found Photos is Vertical Slice | Art bible 6.3, 6.4, 8.3 | Needed |
| 78 | ASSET-078 | Grass ground | Environment | Low-contrast seamless ground, gap fill per 6.2 | Art bible 6.2, 8.6 | Needed |
| 79 | ASSET-079 | Sand shore | Environment | Low-contrast seamless ground, gap fill per 6.2 | Art bible 6.2, 8.6 | Needed |
| 80 | ASSET-080 | Cobble street | Environment | Pack `T_Brick` set as a ground layer. Normal map allowed | Art bible 6.2, 8.6 | Needed |
| 81 | ASSET-081 | Pier planks | Environment | Retired: the pier uses the shared kit wood set | Art bible 6.2, 8.6 | Retired |
| 82 | ASSET-082 | Darkroom table surface | Environment | Retired: comes with the darkroom table | Art bible 6.2, 8.6 | Retired |
| 83 | ASSET-083 | Gallery wall | Environment | Retired: the gallery uses the shared kit plaster set | Art bible 6.2, 8.6 | Retired |
| 84 | ASSET-084 | Shop surface | Environment | Retired: the shop uses the shared kit wood set | Art bible 6.2, 8.6 | Retired |
| 85 | ASSET-085 | Lens-world post pass | VFX | Depth blur, exposure gain, grain, peaking, grade, vignette in one pass. Needs a decision on the shader-code rule conflict | Camera GDD Visual/Audio; Art bible 8.9 | Needed |
| 86 | ASSET-086 | Lens-only subject layer | VFX | Spirits draw only in the viewfinder. Cull-mask route is UNVERIFIED | Subject GDD Visual/Audio; Camera GDD | Needed |
| 87 | ASSET-087 | Subject rim and glow | VFX | Opaque, emissive and rim, driven by glow_permille | Art bible 5.3, 8.5 | Needed |
| 88 | ASSET-088 | Glow halo card | VFX | Fallback if glow is missing on Compatibility (VERIFY) | Art bible 8.5 | Needed |
| 89 | ASSET-089 | Naked-eye shimmer motes | VFX | F16; third person only, at emergence and decisive pose | Subject GDD F16 | Needed |
| 90 | ASSET-090 | Memory fade | VFX | Dither or scale fold into motes; at most one alpha layer | Subject GDD Visual/Audio | Needed |
| 91 | ASSET-091 | Sky gradient by band | VFX | Procedural, no HDRI | Art bible 8.6; World GDD | Needed |
| 92 | ASSET-092 | Water surface | VFX | Time from the world clock | Art bible 8.5 | Needed |
| 93 | ASSET-093 | Wind on grass | VFX | Time from the world clock | World GDD Visual/Audio | Needed |
| 94 | ASSET-094 | Fog | VFX | Depth fog in sky colour; shader fallback observed in prototype | World GDD Visual/Audio | Needed |
| 95 | ASSET-095 | Rain streaks | VFX | Seeded from capture_ms; one alpha layer at most | World GDD Visual/Audio | Needed |
| 96 | ASSET-096 | Capture iris and flash | VFX | Six-blade iris under 150 ms, flash removable | Camera GDD Visual/Audio | Needed |
| 97 | ASSET-097 | Look tag shader parameters | VFX | SWIRL_BOKEH, WARM_FLARE, SOFT_CORNERS | Gear GDD Visual/Audio | Needed |
| 98 | ASSET-098 | Sunbeam event | VFX | Visible rays with motes. No GDD line excludes light events from MVP, so listed as MVP; confirm | World GDD Visual/Audio | Needed |
| 99 | ASSET-099 | Lumen Dusk event | VFX | Cyan dusk grade | World GDD Visual/Audio | Needed |
| 100 | ASSET-100 | Aurora event | VFX | Violet bands | World GDD Visual/Audio | Needed |
| 101 | ASSET-101 | Darkroom light swatch | VFX | Soft gradient from condition, band and event; never tier colours | Photo Recipe GDD Visual/Audio | Needed |
| 102 | ASSET-102 | Print reveal | VFX | Print rises out of the swatch like developing paper; no flash | Photo Recipe GDD Visual/Audio | Needed |
| 103 | ASSET-171 | Title key art | Other | Painterly key art is out of scope for code generation. Not requested by any GDD | Asset-forge scope note | Needed |
| 104 | ASSET-172 | Enlarger and developing trays | Item | Self-made darkroom props, split from ASSET-074 because no pack has them | Art bible 6.3, 8.10 | Needed |
| 105 | ASSET-173 | Player ladder climb loop | Animation | Split from ASSET-005. In neither animation library | Movement GDD Visual/Audio | Needed |
| 106 | ASSET-174 | NPC role props | Item | Hat, apron, satchel, clipboard as rigid parts on bones, split from ASSET-006 to 009 | Art bible 3.3, 5.2 | Needed |

## UI Screens

| # | Asset ID | Screen Name | Description | Source | Status |
|---|---|---|---|---|---|
| 1 | ASSET-103 | Title and sign-in | Play, Play as guest, Sign in with email | Accounts GDD UI Requirements | Needed |
| 2 | ASSET-104 | Account panel | Standard menu panel; guest upgrade | Accounts GDD Visual/Audio | Needed |
| 3 | ASSET-105 | Restore notice | Calm one-off notice | Accounts GDD Visual/Audio | Needed |
| 4 | ASSET-106 | Pending deletion | Calm screen | Accounts GDD Visual/Audio | Needed |
| 5 | ASSET-107 | Starting choice | Phone or camera. Provisional; GDD not started | Systems index 14 | Needed |
| 6 | ASSET-108 | Darkroom breakdown card | Develop fade, seven bars, score, tier. Provisional; GDD not started | Art bible 7.4; systems index 20 | Needed |
| 7 | ASSET-109 | Gallery | Grid of white-bordered prints | Art bible 7.4; systems index 15 | Needed |
| 8 | ASSET-110 | Gear shop and detail | Turntable model, spec table, price | Art bible 7.4; systems index 21 | Needed |
| 9 | ASSET-111 | Sell to clients | Provisional; GDD not started | Systems index 16, 21 | Needed |
| 10 | ASSET-112 | Gear screen (loadout, Bag, Shelf) | Three areas with shared gear card | Inventory GDD UI Requirements | Needed |
| 11 | ASSET-113 | Wallet history | Plain ledger list | Currency GDD Game Feel | Needed |
| 12 | ASSET-114 | Forecast panel | Next 6 slots with icons | World GDD UI Requirements | Needed |
| 13 | ASSET-115 | Field swap list and iris wipe | Outgoing and incoming lens silhouettes | Inventory GDD Visual/Audio | Needed |
| 14 | ASSET-116 | Leaderboard | Wall of prints. Vertical Slice | Art bible 7.4 | Needed |

## HUD Elements

| # | Asset ID | Element | Description | Source | Status |
|---|---|---|---|---|---|
| 1 | ASSET-117 | Camera viewfinder skin | Corner brackets, thirds grid, focus points, exposure scale, data strip frame | Art bible 7.1 | Needed |
| 2 | ASSET-118 | Phone viewfinder skin | Rounded edge, shutter button, zoom pill, sun slider, NIGHT filling ring | Art bible 7.1; Gear GDD Game Feel | Needed |
| 3 | ASSET-119 | Red live dot and battery | Red is shutter-live only (A9) | Art bible 7.1 | Needed |
| 4 | ASSET-120 | Exploration device icon | Camera or phone, battery, shots left | Art bible 7.1 | Needed |
| 5 | ASSET-121 | Compass strip | UX check pending | Art bible 7.1 | Needed |
| 6 | ASSET-122 | Context prompts | Interact and traversal prompts | Movement GDD authored traversal points | Needed |
| 7 | ASSET-123 | Clock and band glyphs | Six bands, distinct shapes | World GDD UI Requirements | Needed |
| 8 | ASSET-124 | Weather icons | Clear, overcast, fog, rain, distinct shapes | World GDD UI Requirements | Needed |
| 9 | ASSET-125 | Event toast and map marker | Calm, no tier names | World GDD UI Requirements | Needed |
| 10 | ASSET-126 | Presence glyph, 3 states | Quiet, noticed, too close | Subject GDD UI Requirements | Needed |
| 11 | ASSET-127 | Curious cue | Lumen eye-dot pair. Proposal for ux-designer | Subject GDD UI Requirements | Needed |
| 12 | ASSET-128 | Tier badge set | Six-blade badge with letter, plus neutral ? badge | Rarity GDD Visual/Audio; Art bible 7.3 | Needed |
| 13 | ASSET-129 | Tier frame ornaments | Corner ticks and double borders | Art bible 4.4 | Needed |
| 14 | ASSET-130 | Connection indicator | Good, fair, poor, reconnecting; shape as well as colour | Network GDD Visual/Audio | Needed |
| 15 | ASSET-131 | Developing and saving marks | Reuse Darkroom visuals | Network GDD Visual/Audio | Needed |
| 16 | ASSET-132 | Guest badge and keep-progress banner | Colour is never the only cue | Accounts GDD Visual/Audio | Needed |
| 17 | ASSET-133 | Envelope and lock icons | Account icons | Accounts GDD Visual/Audio | Needed |
| 18 | ASSET-134 | Glint currency icon and wallet chip | Four-point amber sparkle; never in the viewfinder | Currency GDD Visual/Audio | Needed |
| 19 | ASSET-135 | Gear side silhouettes | 18 MVP models, F14 proportions | Gear GDD F14; Art bible 7.3 | Needed |
| 20 | ASSET-136 | Bound phone mark | Pocket icon, no rarity implication | Inventory GDD Visual/Audio | Needed |
| 21 | ASSET-137 | Bag and Shelf art | 4 pockets; filled and empty differ by shape | Inventory GDD Visual/Audio | Needed |
| 22 | ASSET-138 | Client print icon | Floats over a client; UI layer only | Art bible 5.2 | Needed |
| 23 | ASSET-139 | Logo, spinner, iris transition | Six-blade motif (A8) | Art bible 3.5, 7.5 | Needed |
| 24 | ASSET-140 | Co-op role icons | Alpha system | Art bible 7.3 | Needed |
| 25 | ASSET-141 | Inter | Interface text. Confirm licence on download | Art bible 7.2, A11 | Needed |
| 26 | ASSET-142 | IBM Plex Mono | Camera readouts and serial numbers. Confirm licence on download | Art bible 7.2, A11 | Needed |

## Audio

| # | Asset ID | Name | Type | Description | Source | Status |
|---|---|---|---|---|---|---|
| 1 | ASSET-143 | Shutter ML_SOFT | SFX | Gentle, plays at the press | Gear GDD Visual/Audio | Needed |
| 2 | ASSET-144 | Shutter PHONE_SYNTH | SFX | Soft synthetic | Gear GDD Visual/Audio | Needed |
| 3 | ASSET-145 | Shutter ML_LEAF | SFX | Fujin bodies | Gear GDD Visual/Audio | Needed |
| 4 | ASSET-146 | Subject anticipation tone | SFX | Rising tone; the audio half of the telegraph | Subject GDD Visual/Audio | Needed |
| 5 | ASSET-147 | Subject decisive bell | SFX | Gentle bell at the decisive centre | Subject GDD Visual/Audio | Needed |
| 6 | ASSET-148 | Subject emergence chime | SFX | Soft, positional | Subject GDD Visual/Audio | Needed |
| 7 | ASSET-149 | Subject tuck hush | SFX | Hush or breath | Subject GDD Visual/Audio | Needed |
| 8 | ASSET-150 | Subject flight swirl | SFX | Soft airy swirl | Subject GDD Visual/Audio | Needed |
| 9 | ASSET-151 | Subject return chime | SFX | Quiet | Subject GDD Visual/Audio | Needed |
| 10 | ASSET-152 | Footsteps by surface | SFX | Loudness tracks presence: plank louder than grass, hurry louder than sneak | Movement GDD Visual/Audio | Needed |
| 11 | ASSET-153 | Landing thump | SFX | Scaled to drop height | Movement GDD Visual/Audio | Needed |
| 12 | ASSET-154 | Ladder rungs | SFX | As named | Movement GDD Visual/Audio | Needed |
| 13 | ASSET-155 | Wading splashes | SFX | As named | Movement GDD Visual/Audio | Needed |
| 14 | ASSET-156 | Viewfinder raise rustle | SFX | Cloth or strap | Movement GDD Visual/Audio | Needed |
| 15 | ASSET-157 | Aperture dial click | SFX | One per third stop | Camera GDD Visual/Audio | Needed |
| 16 | ASSET-158 | Focus confirmation | SFX | Same frame as bracket close | Camera GDD Visual/Audio | Needed |
| 17 | ASSET-159 | Zoom ring | SFX | Faint | Camera GDD Visual/Audio | Needed |
| 18 | ASSET-160 | Bayonet mount twist-click | SFX | As named | Gear GDD Visual/Audio | Needed |
| 19 | ASSET-161 | Thread mount screw | SFX | Slower | Gear GDD Visual/Audio | Needed |
| 20 | ASSET-162 | Pocket rustle and Bag pack | SFX | As named | Inventory GDD Visual/Audio | Needed |
| 21 | ASSET-163 | Refusal tap | SFX | Soft low tap, no buzzer | Inventory GDD Visual/Audio | Needed |
| 22 | ASSET-164 | Sale tick and purchase cue | SFX | Warm tick, no casino sounds | Currency GDD Visual/Audio | Needed |
| 23 | ASSET-165 | Account saved chime | SFX | Optional | Accounts GDD Visual/Audio | Needed |
| 24 | ASSET-166 | Reconnected cue | SFX | Optional | Network GDD Visual/Audio | Needed |
| 25 | ASSET-167 | Ambience beds by condition | Ambient | Crossfaded with blend_permille. The generator makes SFX and chiptune, not natural beds | World GDD Visual/Audio | Needed |
| 26 | ASSET-168 | Rain layer | Ambient | Needs a caption or visual equivalent | World GDD Visual/Audio | Needed |
| 27 | ASSET-169 | Event build-up cue | Ambient | One distinct gentle cue, never an alarm | World GDD Visual/Audio | Needed |
| 28 | ASSET-170 | Music | Music | No GDD or bible section asks for music. asset-forge makes chiptune only, which may not suit the cozy tone | Systems index row Audio (no music system listed) | Needed |
