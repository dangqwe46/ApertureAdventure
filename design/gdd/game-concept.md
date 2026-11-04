# Aperture: Game Concept

> Status: first draft, 2026-11-03. Includes the rarity system. All numbers are placeholders to tune.
> This is the working concept for Aperture; see `design/project-context.md` for decisions and open questions.

## Pitch

Aperture is an online, browser-based photography RPG where you build a career with a camera: start with a phone or an entry camera, photograph subjects, sell the photos, and spend the money on lenses and bodies that reach harder subjects.

**Core fantasy:** “I see what others miss, and I choose what’s worth keeping.”

**Unique hook:** photography is the RPG system itself. Gear is your equipment and your economy, the scoring system is the skill check, the rarity tiers decide what you can capture, and the top-100 leaderboard is the social payoff.

**Proposed setting (open to change):** a world where forgotten memories and shy spirits only appear through a lens, so subjects are gentle and the tension comes from light and timing.

## Pillars

1.  **Seeing is the skill.** Success comes from the player’s eye and timing. Gear raises the ceiling but never replaces skill.
2.  **Every photo matters.** Photos persist in a gallery, earn money, and can reach the leaderboard.
3.  **Play together without violence.** Co-op and contests, with tension from fleeting light and shy subjects, never killing.

**Anti-pillars:** not pay-to-win, not a combat game, not a photo-upload or social-media app (players photograph only the game world), and not photoreal.

## Core loop
```text

Start (phone or camera)
   |
   v
Explore --> Capture --> Develop (darkroom and score)
   ^                          |
   |                          v
Upgrade gear <--- money --- Sell (NPC clients first)

(new subjects and places unlock as you upgrade gear)
```

Players choose a free phone or a paid camera, then repeat the loop: explore, capture, develop and score the photo, sell it, and spend the money on gear that opens subjects the old gear could not reach.

## Gear and economy

Gear is the progression system: players start with a phone or a camera, sell photos for money, and buy gear that unlocks subjects the old gear could not reach.

### Starting choice

|            | Phone                                                    | Entry camera                                                   |
|------------|----------------------------------------------------------|----------------------------------------------------------------|
| Cost       | Free or nearly free                                      | Costs starting money                                           |
| Strengths  | Always on you, auto-focus and auto-exposure, easy to use | Interchangeable lenses, manual control, higher quality ceiling |
| Weaknesses | Fixed lens, small sensor, weak in low light              | Fewer helpers, steeper learning curve                          |
| Fits       | New or casual players                                    | Players who want depth                                         |

Neither is a trap: a skilled phone player should beat a careless camera owner early on, and the phone stays a valid “street” style later.

### Gear specs (real photography logic)

- **Lenses:** focal length (for example 24, 50, 85 and 200 mm) sets the field of view, the maximum aperture (f/1.4 to f/2.8) sets background blur and light gathered, and focus speed matters for moving subjects.
- **Bodies:** sensor size, low-light performance, burst rate and battery.
- **Mounts:** a lens only fits a body with the same mount. Adapters are tradable items that cost some quality.
- **Tier and condition:** every body and lens has a rarity tier (see Rarity system) and a condition. Vintage lenses have a distinct look, and worn gear has small flaws.

### Brands (assumption: invented makers)

Real specs and mount logic are free to use, but real brand names, logos and product designs belong to their owners, which is a risk for a game with a trading economy. The design uses invented makers that copy the real-world logic, for example a “Nokta” Z-mount and F-mount family, a “Kanro” R-mount and E-mount family, and a “Fujin” X-mount. This needs a decision, and a lawyer’s check if real names are kept.

### Selling photos

- The server sets a base price from the photo’s tier, its score, and current demand.
- A photo sells once or in limited editions. A sold photo cannot be resold by the seller.
- Buyers are NPC clients, commissions and contests first. Player-to-player selling comes later.

### Balance

- Diminishing returns on repeated subjects, with rotating demand, so there is no single grind spot.
- Money sinks: maintenance, travel, storage and repairs, so the economy does not inflate.
- Anti rich-get-richer: skill thresholds for each tier, upkeep that grows with tier, cheaper side-grade gear, and decent early commissions for newcomers.
- Gear raises the ceiling but never replaces skill, so it is never pay-to-win.

## Rarity system

Gear and images share one tier ladder, for example C, B, A, S, SS and SSS, and the high tiers are rare by design. All numbers in this section are placeholders to tune.

### Tiers

Quality and rarity are two separate things:

- **Tier** is what you captured and what gear could capture it. It sets the base value.
- **Score** is how well you shot it. It adjusts value within the tier.

A technically perfect shot of a common subject stays a low tier, and a messy shot of a rare spirit is still a rare image.

### Capture rule
```text

Body tier  --+
             +--> Gear ceiling (lower of the two) --+
Lens tier  --+                                       |
Subject tier (subject rarity) -----------------------+
Moment tier (timing of the shot) --------------------+--> IMAGE TIER
Light tier (light quality) --------------------------+    (the lowest limit wins,
Skill score (minimum per tier) ----------------------+     then odds decide the capture)
```

Gear sets the ceiling as the lower of the body and lens tiers (and of any adapter fitted), so an SSS image needs both to be SSS. The scene and your skill each add a limit, the lowest limit wins, and a roll against the odds below decides whether you get it.

| Image tier | Gear needed         | Scene needed                               | Example chance if all met |
|------------|---------------------|--------------------------------------------|---------------------------|
| C / B      | Any                 | Common                                     | Near guaranteed           |
| A / S      | A / S body and lens | Uncommon subject, decent moment and light  | 60–80%                    |
| SS         | SS body and lens    | Rare subject, strong moment and light      | 25–40%                    |
| SSS        | SSS body and lens   | SSS subject, perfect moment, perfect light | 5–10%                     |

Top-tier subjects appear only in short windows (a particular weather, hour or place), so players plan around them instead of waiting at one spot.

### Unique images

Every photo is already unique, because its recipe holds the camera position, settings, time of day and subject pose. The top tiers add real scarcity on top of that:

- Each SSS and SS subject appearance can be **claimed once**. The first valid capture owns it, and other players who were there get a lesser result, such as a participation reward.
- Each high-tier image gets a **serial number**, for example “SSS \#12 of 100 this season”.
- Co-op crews can share a claim, with the credit split by role.

### Limited gear

Gear has a supply cap per tier, with serial numbers (for example “SSS body \#7 of 20”). The server owns the counters, so the cap cannot be exceeded by exploits or duplicate trades.

A fixed cap locks out late players, so the design needs at least some of these:

| Option             | How it keeps the economy fair                                                                         |
|--------------------|-------------------------------------------------------------------------------------------------------|
| Seasons            | Caps reset each season, and old gear retires into a hall of fame or a collection                      |
| Wear               | Gear degrades and eventually breaks, freeing supply slowly                                            |
| Crafting           | Merge several lower-tier items into one higher-tier item, so effort rather than luck leads to the top |
| Earned, not bought | Top gear unlocks through achievements and contests rather than random chests                          |

## Photo evaluation

Every shot is scored from separate parts by clear rules, so players see exactly why a photo scored well and can learn from it.

| Part        | What it measures                       |
|-------------|----------------------------------------|
| Subject     | In frame and recognisable              |
| Focus       | Sharp where it matters                 |
| Exposure    | Not too dark or too bright             |
| Composition | Rule of thirds, leading lines, framing |
| Light       | Direction and quality                  |
| Moment      | Caught at the decisive instant         |
| Rarity      | Difficulty or rarity of the subject    |

Each part gets a rating (for example 0 to 100) and the parts combine into a final score. The score adjusts the image’s value within its tier, and a breakdown is shown after every shot.

Gear sets the tier ceiling (see Rarity system) and helps individual parts, since a fast lens helps blur and low light, but it cannot make a poorly framed shot score well. The server recalculates every score from the stored photo recipe, so the client cannot report its own result.

## Online play

Players share one world and one economy, with small groups for expeditions and cheap asynchronous features so the game is fun even when few players are online together.

### Co-op crews (2 to 4 players)

Each role does something the others cannot.

| Role     | Contribution                                                         |
|----------|----------------------------------------------------------------------|
| Wildlife | Tracks and lures the subject                                         |
| Portrait | Coaxes shy spirits into the open                                     |
| Astro    | Takes long exposures, but needs protecting while the shutter is open |
| Street   | Scouts ahead and spots rare moments                                  |

Players can also assist (holding a reflector or flash) and combine their shots into one panorama or composite photo for a bigger reward.

### Competition and social play

- Daily and weekly themes (“golden hour”, “reflections”), judged by other players.
- Timed races where a crew chases the same rare spirit.
- A shared hub where each player’s gallery is on display.
- Found photos: players leave photos at spots in the world for others to discover.
- A commission board where players post requests (“the lighthouse at dusk”) and others fulfil them for money or reputation.
- Server-wide events, such as a rare spirit at golden hour for ten minutes.

### Leaderboard (top 100)

Each entry shows the image, its tier and score, the owner and the gear used. There are separate boards for all-time, weekly and by category (wildlife, portrait, astro), plus a rarity board, because one global board gets dominated by a few players and high scores on common subjects get buried. Each entry is re-rendered from its recipe, so the board is cheap to store.

## Technical considerations

The plan is Godot in 3D, exported to the web with the Compatibility renderer (WebGL 2), with a server that decides everything that matters.

- **Networking:** ENet, which the studio’s Godot reference uses, is not available in web exports. Use WebSocket (simplest, server-authoritative) or WebRTC.
- **Server authority:** the server owns inventories, trades, prices, scores, rarity rolls and the supply and claim counters. Messages are versioned and field ranges are validated, as the studio’s network rules require.
- **Photo as a recipe:** a photo is stored as the camera position, settings, time of day and subject pose, then re-rendered when viewed. Photos stay tiny, the server can verify the score, and players cannot upload arbitrary images.
- **Backend:** a headless Godot server plus accounts and a database for galleries, ratings, commissions, the market and serial numbers.
- **Room size:** small expedition rooms of 2 to 4 players, and a larger shared hub added later.
- **Look and assets:** stylised low-poly keeps the web build light. The asset-forge skill can make props, sprites, textures and sounds, while characters and spirits are better sourced from free packs.

## Risks and open questions

| Risk                                                                                | Mitigation                                                                                                         |
|-------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| Real brand names and designs                                                        | Use invented makers with real specs, and decide this early because renaming later touches assets, UI and marketing |
| Score cheating                                                                      | Store photos as recipes and let the server recalculate every score                                                 |
| Score gaming (one perfect spot)                                                     | Rotate subjects and daily themes, with diminishing returns on repeats                                              |
| Trading abuse (scams, duplication)                                                  | Server-owned inventory, two-sided confirmation, price floors and ceilings                                          |
| Rich get richer: SSS gear earns SSS images, which buy more SSS gear                 | Skill thresholds for each tier, plus upkeep costs that grow with tier                                              |
| Loot-box rules: many regions regulate paid random rewards                           | Avoid paid random rewards, and keep any paid items cosmetic                                                        |
| Pay-to-win: limited gear sold for money turns the leaderboard into a wallet contest | Never sell tier. Any paid items stay cosmetic or side-grades                                                       |
| Dead top end: if SSS is too rare, nobody sees it                                    | Test the odds, and make sure some SSS gear and images exist at all times                                           |
| Scope (RPG plus camera plus online)                                                 | Start with asynchronous features and small co-op rooms                                                             |
| Web performance                                                                     | Low-poly art, few materials, small textures                                                                        |

### Open questions

- [x] Invented camera brands, or real names (with legal review)? **Decided 2026-11-03: invented brands with real-world specs and mount logic.**
- [ ] Can players sell photos to each other, or only to NPCs and the market at first?
- [ ] Is the phone only a starting tool, or a permanent path with its own upgrades?
- [ ] Does the starting camera cost in-game debt, or a price paid up front?
- [x] Which tone: cozy and reflective, mystery and ghost story, or a competitive rival? **Decided 2026-11-03: cozy and reflective, with shy spirits and forgotten memories visible only through a lens.**
- [ ] Is the gear supply cap global, per season, or per player?
- [ ] When gear breaks, does it disappear or return to supply?
- [ ] Is the first claim on a top-tier subject winner-takes-all, or does everyone nearby get a smaller reward?

Recommendation for the rarity questions: seasonal caps, wear plus crafting, and first-claim with shared credit for crews.

## First playable version

The first version proves one loop end to end: capture a subject, get a fair score, sell it, and buy something that changes what you can capture.

### Must have

- One small area with about 5 photographable subjects
- A phone and one entry camera, plus 3 pieces of upgrade gear
- A score breakdown after each shot
- Selling photos to NPC clients
- A gallery and a basic darkroom screen
- One capture encounter that works like a boss fight

### If time allows

- Daily theme contest
- A single leaderboard
- Found photos

### Later

- The full rarity ladder with supply caps, serial numbers and first-claim subjects
- 2 to 4 player co-op expeditions
- Player-to-player trading
- Shared hub and server-wide events
- Commission board

## Next steps in the studio

1.  `/start`, then `/brainstorm` to refine this into the studio’s game concept document.
2.  `/setup-engine`, choosing Godot, 3D and the Web target.
3.  `/art-bible` for the palette, shape language and polycount budgets.
4.  `/map-systems`, then `/design-system` for scoring, the economy, rarity and networking, using the economy-designer and network-programmer agents.
5.  `/asset-spec`, then `/asset-forge` to produce models, sprites, textures and sounds.
