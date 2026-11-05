# Art Bible: Aperture

> **Status**: Draft
> **Owned By**: art-director
> **Last Updated**: 2026-11-05 (art direction changed by the user; see "Revision 2026-11-05")
> **Art Director Sign-Off (AD-ART-BIBLE)**: [Not yet reviewed]

`/art-bible` writes these nine sections in this order and replaces each
section's placeholder line as that section is approved. A section still
holding its placeholder is incomplete; a later run fills only those.

---

## How this draft was produced (read first)

This draft was written by the art-director in a single pass, without the
user's section-by-section approval and without the other specialists the
`/art-bible` skill would normally consult. A reader must not take it as a
finished, reviewed bible.

| Step the skill normally runs | What happened in this draft |
|---|---|
| Phase 1 framing questions (scope, reference titles) | **Not asked.** Scope = full bible, because `modes.rigor: full` resolves to `workflow: full`, which requires all 9 sections. Depth = `thorough` (same reason). No reference titles came from the user; the art-director chose all of Section 9. |
| Per-section user approval | **Not done.** Every section is a proposal. See "Assumptions to confirm". |
| Section 7 `ux-designer` alignment check | **Did not run.** Section 7 is art-director only; readability and accessibility conflicts are flagged inline but not reviewed by UX. |
| Section 8 `technical-artist` hard-constraint check | **Did not run.** Every budget in Section 8 is an art-director starting value, not a validated limit. |
| Phase 5 AD-ART-BIBLE gate | **Did not run.** Header stays "[Not yet reviewed]". |
| Engine facts | Only facts present in `docs/engine-reference/godot/` or `.claude/skills/asset-forge/references/` are stated as fact. Other renderer behaviour is marked **VERIFY (not sourceable)** and routed to the technical-artist. |

Tags used in this document:

- **[DEPENDS: setting]**: only holds if the "forgotten memories and shy spirits seen through a lens" setting is confirmed.
- **[DEPENDS: brands]**: depends on the invented-brands versus real-brands decision.
- **[DEPENDS: tone]**: depends on the tone decision (cozy and reflective / mystery and ghost story / competitive rival).
- **VERIFY**: an engine or renderer claim that is not covered by the project's pinned engine reference.

### Revision 2026-11-05

The user changed the art direction: **3D stylized with textures, built from free
Quaternius assets**, replacing flat-shaded untextured low-poly. Also confirmed:
cozy and reflective tone, spirits and memories visible only through a lens, an
elevated three-quarter camera while exploring, and a first-person viewfinder when
shooting. The target stays Godot 4.7.2 Web, Compatibility renderer.

- **The direction itself is the user's decision.** The details below it (texture
  grading, budgets, how spirits and gear match) are art-director proposals. The
  ux-designer, technical-artist and AD-ART-BIBLE reviews have still not run.
- **`[DEPENDS: setting]` and `[DEPENDS: tone]` tags are resolved** by this decision.
  They stay in the text as markers of what the setting drives.
- **Unchanged:** "Light is the subject", the lighting presets (2.2), rarity colours
  and six-blade badge (4.4, 7.3), UI principles, the re-render rule (P4), section
  numbers and assumption numbers (GDDs cite them).
- **Evidence:** the Quaternius scene spike, the pack files and pack preview, and
  `design/art/demo.jpg`, which is a style reference only. Its content must not be
  copied. The spike was read from
  `.claude/worktrees/agent-afafb031d63f41d99/prototypes/quaternius-scene-spike/`;
  it is not yet in the main tree.
- **Stale until updated:** `design/assets/entity-inventory.md` (ASSET-002),
  `design/assets/specs/characters-assets.md` and `design/assets/asset-manifest.md`
  still describe the old direction.

---

## Assumptions to confirm

Every choice below was made on the user's behalf unless marked CONFIRMED or
SUPERSEDED. Each lists the alternative. The ones tagged with a DEPENDS tag also
hang on an open item in `design/gdd/game-concept.md`. Superseded rows keep their
number and old wording, because GDDs cite them.

| # | Choice made | Alternative | Depends on |
|---|---|---|---|
| A1 | **CONFIRMED 2026-11-05** (spirits and memories are lens-only). The world has two visual layers: the **naked-eye world** and the **lens world** (the view through the viewfinder), with different grading. Spirits exist only in the lens world. The two-layer system is built so it still works with no spirits (the lens layer becomes a pure "photographer's eye" grade). | One layer only: the viewfinder is a plain HUD over the same image, with no change of grade. | setting |
| A2 | **CONFIRMED 2026-11-05.** Tone is **cozy and reflective, with a quiet tint of mystery**: muted, warm-neutral world, light that does the emotional work, nothing frightening. | (a) Mystery and ghost story: darker values, colder palette, more fog and contrast. (b) Competitive rival: brighter, more saturated, louder UI. | tone |
| A3 | Gear art is **brand-agnostic**: no maker name or logo is baked into any mesh or texture. The brand mark is a separate, swappable label (a UI data field plus one decal slot). Examples in this document use the invented makers from the concept (Nokta, Kanro, Fujin). | Bake invented brand marks into the models; or use real brand names after legal review. Either way, no real product's industrial design or logo is copied. | brands |
| A4 | **Still proposed; revised 2026-11-05.** The first playable area is a **small coastal village**: cliff, lighthouse, pier, a few houses, a strip of woodland. Chosen because the concept's own example commission is "the lighthouse at dusk" and because a coast gives open sky for light and time-of-day play. The village is now the half-timbered Quaternius kit (6.1). The installed free packs hold no lighthouse, pier, water or shoreline pieces (8.10). | Forest valley or inland market village, which the kit covers with no gaps but which loses the lighthouse and open sea. | setting (partly) |
| A5 | **SUPERSEDED 2026-11-05.** New rule: human characters come from Quaternius Universal Base Characters plus Universal Animation Library, keep their textures, and still need outfits (5.1, open). World art comes from Quaternius kits. asset-forge makes gear, spirits and UI only (8.10). *Was:* Human characters and animals come from CC0 rigged packs (Quaternius first, Kenney second), recoloured to this palette and given flat-shaded material overrides. asset-forge makes spirits, gear, props and environment. | Code-made rigid-part "mannequin" humans from asset-forge (no skinning; limbs swing on pivots). Cheaper and fully in-house, but they would not match a textured world. | none |
| A6 | **SUPERSEDED 2026-11-05 (confirmed by the user).** New rule: an **elevated three-quarter camera** while exploring; taking a photo switches to a first-person viewfinder. *Was:* Exploration is third-person; taking a photo switches to a first-person viewfinder. | First-person throughout. (Camera perspective is a gameplay and UX decision; this bible only styles it.) | none |
| A7 | **Rarity colours follow the familiar game ladder** (grey, green, blue, violet, amber, prismatic) for C, B, A, S, SS, SSS, and are always backed by the tier letter and an aperture-blade count. | A metal ladder (iron, bronze, silver, gold, platinum, pearl), which reads as more "photographic equipment" but is harder to tell apart at small sizes. | none |
| A8 | **Six aperture blades are the game's core motif**: the logo, loading spinner, screen transitions and the rarity badge (C = 1 lit blade up to SSS = 6). Six matches the six tiers in the concept. | If the tier ladder changes length, keep six blades and light a fraction; or drop the blade badge and use pips. | none |
| A9 | **Red means "darkroom" and "shutter is live", never danger.** The game has no danger state (no violence). | Keep red only for errors, as most software does. | none |
| A10 | **SUPERSEDED 2026-11-05 (the user's decision).** New rule: world surfaces use the **stylized PBR textures from the Quaternius packs**, downsized for the Web and graded to the palette (A18). Only lens-world subjects and gear stay untextured, because asset-forge cannot UV-map (A20). *Was:* Default surface treatment is **flat-shaded, colour-blocked, untextured** geometry. Seamless textures are used only on terrain and large ground planes. | None; the direction is decided. | none |
| A11 | UI fonts are **Inter** (interface text) and **IBM Plex Mono** (camera readouts and serial numbers), both under the SIL Open Font License. Confirm each licence on its download page before shipping. | Other OFL fonts, e.g. Atkinson Hyperlegible (stronger on accessibility) or Space Grotesk / Space Mono (more personality). | none |
| A12 | UI is designed at a **1280x720 reference resolution** (the project's `run` command uses that size) and scales up. | 1920x1080 reference. | none |
| A13 | The phone and the camera get **different viewfinder skins** (phone: clean rounded touchscreen UI; camera: electronic-viewfinder data strip). | One shared viewfinder for both. | none |
| A14 | **Revised 2026-11-05.** All polycount, draw-call, texture and memory numbers in Section 8 are **provisional**: set by the art-director from one desktop spike and the pack files, and not yet measured in a browser. The technical-artist has not validated them. | Values set by technical-artist profiling on target hardware. | none |
| A15 | Asset name prefixes `subj_` (photographable subjects) and `gear_` (bodies, lenses, phones) are added to the CCGS categories. `subj_` is used instead of `spirit_` so names survive if the setting changes. | `spirit_` and `cam_` prefixes; or fold gear into `prop_`. Note: `/asset-audit` may not know the new prefixes yet. | setting |
| A16 | **Revised 2026-11-05.** Section 9 references 1 to 5 were chosen by the art-director. The user has since supplied two: the Medieval Village MegaKit preview and `design/art/demo.jpg` (style only). | Replace with the user's own references. | none |
| A17 | **CONFIRMED 2026-11-05** (setting); extended by A20. Spirit design language (soft, rounded, floating, emissive, no faces or a minimal two-dot face). | If spirits are dropped: the same rules apply to "rare moments" (rare animals, light phenomena, weather events). | setting |
| A18 | **New 2026-11-05.** Quaternius textures are **graded towards the palette** with material tints, so surfaces stay quieter than the light (4.1). The textures are not repainted. | Use the pack colours as they come. Cheaper and brighter, but the spike's orange roofs then compete with light and subjects. | none |
| A19 | **New 2026-11-05.** The game uses the **free Standard pack versions** only. They hold a portion of each kit's models, and the preview image may show pieces that are not in them. | Buy the PRO or SOURCE versions for more models and the stylized shaders. This conflicts with the "no extra paid services" decision, so it is the user's call. | none |
| A20 | **New 2026-11-05.** The figure-ground idea survives as **texture against no texture**: spirits are the only surfaces in the game with no texture at all, which marks them as lens-world (5.3). Gear is physical, so it follows separate matching rules (3.4). | Give spirits a texture of their own. This needs UV-mapped models, which asset-forge cannot make. | setting |

---

## 1. Visual Identity Statement

### The one-line rule

> **Light is the subject. The world is a warm, hand-crafted 3D storybook of
> textured forms, kept quiet enough that light, timing and framing are the things
> a player learns to see.**

When any visual decision is ambiguous, ask: *does this make the light, the
moment or the frame easier to read, or does it compete with them?* Choose the
option that makes them easier to read.

**Why this rule.** Aperture scores Light, Moment and Composition directly
(see Photo evaluation in the concept), and the first pillar says success comes
from the player's eye. A photography game fails visually if the world is so
busy that good and bad light look alike. Stylized textures make the world worth
photographing: tile, timber and cobble give light something to rake across, and
the spike's golden-hour street shows long shadows reading well on them. The risk
is the opposite of the old style's: texture adds noise and strong local colour,
so soft light and flat noon can blur together on a busy surface. The answer is
to keep the big forms simple, keep texture detail broad and painted rather than
fine, and grade surface colour down (A18), so light still does the most visible
work.

### Supporting principles

**P1. Light reads first.** *(Pillar 1: Seeing is the skill.)*
Forms are built so the light on them can be read: large simple masses, broad
painted texture, values kept in the middle range so that light pushes them up or
down. Saturation lives mostly in the light and the sky, not in the surfaces.

- *Design test:* when unsure between two kit pieces, pick the calmer one. When
  unsure about a material's tint, choose the one that shows the difference between
  golden hour and noon more clearly (mid-value, lower saturation). Compare the same
  view at both times of day; if they look alike, the surface is too strong.

**P2. Every view is frame-worthy, never filled.** *(Pillar 2: Every photo
matters.)*
Places are composed like photographs before a player ever lifts the camera:
there are leading lines, frames within frames (doorways, branches, arches),
horizons and negative space. Props are placed to make compositions, not to
fill floor.

- *Design test:* when unsure whether to add a prop, add it only if it creates
  a line, a frame, a foreground layer or a point of interest. If it only fills
  space, leave the space empty.

**P3. Gentle things, fleeting light.** *(Pillar 3: Play together without
violence.)*
Nothing in the art threatens. Subjects are soft and rounded; tension is drawn
with time (a light window closing, a subject about to leave), never with
weapons, blood, spikes or aggressive red. The excitement of a rare capture is
shown as light, glow and stillness, not as impact.

- *Design test:* when unsure how to make a moment feel high-stakes, make the
  light rarer and shorter (a ray, a glow, a colour shift) rather than making
  anything bigger, faster or sharper.

**P4 (production rule). What was seen must be re-renderable.**
A photo is stored as a recipe and re-rendered later (concept, Technical
considerations). So anything that can appear in a photo must look the same
when re-rendered from the recipe: time of day, weather, subject pose and any
animated foliage or water must be driven by recorded world state or seeded,
never by unseeded randomness or by per-client timing. Purely client-side
effects (screen-space UI, camera shake) must never be baked into the stored
photo.

- *Design test:* when unsure whether a visual effect may be random, ask "would
  the gallery copy of this photo differ from what the player saw?" If yes, it
  must be seeded or driven by the recipe.

---

## 2. Mood & Atmosphere

Aperture's states are defined by **what the player is doing with their eyes**:
looking around, looking through the lens, pressing the shutter, waiting for
the print, showing off. Each state has its own lighting character and its own
dominant colour, so a player knows at a glance which state they are in.

Time of day and weather are both a mood tool and a scoring input (Light tier),
so they get their own table after the states.

### 2.1 Game states

**Exploration (naked eye)**
- *Emotional target:* calm curiosity; the feeling of a slow walk with a camera
  over your shoulder, noticing things.
- *Lighting:* set by the time-of-day table below. Contrast medium. The sky is
  the brightest and most saturated area of the frame.
- *Descriptors:* open, quiet, airy, weathered, unhurried.
- *Energy:* contemplative.
- *Mood carrier:* long shadows and the colour of the sky; wind moving grass in
  slow, seeded waves.
- *Camera:* elevated three-quarter view (A6), looking down at the player and the
  street. Scenes must read from above as well as at eye level: roofs fill much of
  this view, so they are the largest colour area on screen (4.1).

**Viewfinder (lens world)** [DEPENDS: setting, for spirits; the grade applies either way]
- *Emotional target:* focus and quiet anticipation; the world narrows and
  something hidden might be there.
- *Lighting:* the same light as exploration, re-graded: contrast up one step,
  saturation up slightly at the centre, edges darkened by a soft vignette.
  Spirits and other lens-only subjects appear with a soft cyan-white glow
  (Lumen, see Section 4).
- *Descriptors:* hushed, focused, intimate, slightly uncanny.
- *Energy:* held breath.
- *Mood carrier:* the vignette and the frame edge; the sudden presence of a
  glowing subject that was not there to the naked eye.
- *Phone vs camera* (A13): the phone view is brighter and flatter (auto
  exposure, smaller vignette); the camera view keeps true exposure, so a dark
  scene stays dark. This makes the phone feel easy and the camera feel honest.

**Capture (shutter press)**
- *Emotional target:* a crisp, satisfying "got it".
- *Lighting:* a fast shutter blink, done as a six-blade iris closing and
  opening in under 150 ms (motif A8), plus one frame of a slight white flash.
  No screen shake.
- *Descriptors:* crisp, decisive, clean.
- *Energy:* an instant spike, then straight back to calm.
- *Mood carrier:* the iris blink and the small red "live" dot (A9) going out.
- *Accessibility:* the white flash must be under the flash-safety thresholds
  and must be removable by a reduce-flashing option (the iris can stay).

**Rare capture window (high-tier subject or light event)**
- *Emotional target:* wonder with urgency; "this will not last".
- *Lighting:* one special light per event: a ray through cloud, a strong
  golden rim, aurora-like bands at night. The world's saturation drops very
  slightly everywhere except the event light and the subject, pulling the eye
  to them.
- *Descriptors:* luminous, fleeting, charged, rare.
- *Energy:* rising, focused tension; never frantic.
- *Mood carrier:* the event light itself, plus slow-falling motes in the light
  beam (cheap particles).
- *Rule:* a rare window must look different from ordinary golden hour, or
  players will not learn to tell them apart. Use a hue that ordinary times of
  day never use (Lumen cyan at dusk, or a violet rim at night).

**Encounter (the "boss" capture from the first playable version)**
- *Emotional target:* patient skill under pressure, like stalking a shy
  animal; never fear.
- *Lighting:* the light changes during the encounter (clouds part, sun sinks)
  so the best moment has to be waited for. The subject's glow pulses when it
  is about to hold still (a readable "decisive moment" cue, supporting the
  Moment score).
- *Descriptors:* tense, quiet, shifting, alive.
- *Energy:* measured, with peaks.
- *Mood carrier:* the subject's anticipation pose and pulse before its
  decisive pose (see Section 5).

**Darkroom / Develop (score reveal)**
- *Emotional target:* warm suspense, then pride or a clear lesson.
- *Lighting:* a small room under red safelight (Safelight Red, Section 4);
  the print sits on a bright paper tray under its own neutral light so the
  photo's real colours are never tinted red.
- *Descriptors:* warm, enclosed, ritual, tactile, private.
- *Energy:* slow build, then release.
- *Mood carrier:* the photo appearing on blank paper (a develop fade from
  Paper White to the image), followed by the breakdown bars filling one by
  one.

**Gallery and hub** (A4; hub is "later" scope)
- *Emotional target:* pride and sharing; a cosy exhibition.
- *Lighting:* warm interior, gallery spot pools on each print, the rest of the
  room a step darker so prints are the brightest things.
- *Descriptors:* warm, proud, social, orderly.
- *Energy:* relaxed.
- *Mood carrier:* white-bordered prints on walls, each lit like a museum piece.

**Market and gear shop**
- *Emotional target:* desire and careful choice; a well-kept camera shop.
- *Lighting:* clean, neutral-warm, high key; gear turntables under a soft top
  light with a rim so metal edges and lens rings read.
- *Descriptors:* tidy, precise, inviting, tactile.
- *Energy:* measured.
- *Mood carrier:* the gear model rotating slowly with a rim light catching the
  tier ring (Section 5, gear).

**Leaderboard**
- *Emotional target:* aspiration and respect.
- *Lighting:* screen-space UI on Darkroom Ink; prints are the light sources.
- *Descriptors:* prestigious, calm, clear.
- *Energy:* still.
- *Mood carrier:* the top entries framed with their tier ornament; SSS entries
  carry the only animated shimmer on the screen.

**Title and menus**
- *Emotional target:* invitation; the moment before a walk at golden hour.
- *Lighting:* a slow, looping golden hour to blue hour over the lighthouse
  vista (A4) behind the menu.
- *Descriptors:* inviting, gentle, nostalgic.
- *Energy:* contemplative.
- *Mood carrier:* the aperture logo opening on the vista.

**Co-op expedition** (later scope)
- Same as exploration, plus soft teammate markers. Teammates must not add
  colour noise to a photograph: markers are UI-only and hidden in the stored
  photo (P4).

### 2.2 Time of day and weather (light vocabulary)

These are art targets for the technical-artist to turn into
`DirectionalLight3D` and `WorldEnvironment` presets. Hex values are starting
points to tune in-engine.

| Light condition | Sun colour | Sun angle and intensity | Ambient / shadow tint | Sky band (top to horizon) | Contrast | Intended light quality |
|---|---|---|---|---|---|---|
| Dawn | `#FFC9A8` | low, soft | `#8C9BC4` cool lilac | `#6E7FB8` to `#F4C8B8` | low-medium | gentle, pastel, misty |
| Midday | `#FFF6E8` | high, strong | `#A9BFD6` | `#5E9BD6` to `#CFE3F2` | high, short shadows | flat, plain; the "easy, low-value" light |
| Golden hour | `#FFB060` | low, warm, strong | `#6F7FA8` (complementary cool shadow) | `#7C8FC0` to `#FFC27A` | high, long shadows | the signature light: warm key, cool shadow |
| Blue hour | none or very weak | sun below horizon | `#4B5F9A` | `#2E3A6E` to `#8A8FC4` | low | still, cool; windows glow `#FFC56B` |
| Night (astro) | moon `#9DB4E8` | low | `#1E2648` | `#0E1430` to `#2A3466` | low, with point highlights | dark, starry; emissive lights carry the scene |
| Overcast / fog | `#DDE2E6` | diffuse | `#B4BCC4` | flat `#C9CFD4` | low | soft, even; good for portraits |
| Rain | `#C8D0D8` | diffuse | `#7C8894` | `#6C7884` to `#AAB4BE` | low-medium | moody; wet surfaces get lower roughness |

Rules:

- **Light quality must be legible to the naked eye.** The difference between a
  C-tier and an S-tier light should be visible before the score says so. Noon
  is deliberately the plainest look; golden hour and rare events are the
  richest.
- **Warm key, cool shadow** is the default relationship at golden hour and
  dawn (complementary colour contrast makes light direction obvious).
- **One sun, one shadow.** Exactly one directional light casts shadows.
  Local lights (lamps, lighthouse beam, spirit glow) use emissive materials
  first and real lights only where the light must fall on other objects
  (budget in Section 8).
- **Fog** is depth fog in the sky colour, used to separate foreground, middle
  ground and background layers (aerial perspective). VERIFY: which fog modes
  the Compatibility renderer supports in Godot 4.7.2 is not covered by
  `docs/engine-reference/godot/`; assume no volumetric fog until the
  technical-artist confirms.
- **The sky must keep its gradient.** In the spike, fog tinted the sky to one flat
  tan and the sun disappeared. Fog separates depth layers; it must not replace the
  sky bands in the table above.

---

## 3. Shape Language

The game uses **two opposed shape families**: the world is solid, textured and
hand-built; the things you photograph are smooth, round and untextured. This
figure-ground contrast is the main reason a subject pops out of a scene, and it
is cheap (it costs nothing in polygons or materials).

### 3.1 Environment geometry: chunky, hand-built, calm

- Built from the Quaternius modular kits. Their language is the standard: thick
  timber, chunky cobbles, overlapping tiles, slightly uneven lines, soft bevels.
  Anything else placed in the world must match that weight.
- Dominant forms: **steep gables and gentle wedges** (houses, roofs, stairs),
  **tall verticals used sparingly** as landmarks (lighthouse, a single tall tree,
  a mast), and **long horizontals** (horizon, path, fence, wall, shoreline) that
  make natural leading lines.
- Angles are calm. Sharp spiky forms are avoided (P3): the kit's iron roof
  ornaments stay off the main views. Rocks are chunky and broad, not jagged.
- Natural forms are stylized, not realistic: trees have big readable crown masses;
  grass and flowers are placed as drifts, not single scattered plants (6.3).
- Weathering uses **shape and kit dressing**: a leaning post, a missing plank,
  vines on a wall, an overgrown path. [DEPENDS: setting, for "forgotten" decay; a
  lighter version suits any tone]
- Kit pieces follow the kit's own grid (2-unit walls, 3 m storeys, roofs sized in
  metres of footprint, per the spike). Doors and shutters need exact placement; the
  spike only eyeballed them.

### 3.2 Subject geometry: smooth, round, small

- Spirits [DEPENDS: setting] and other living subjects use smooth, rounded
  forms (`smooth_angle` 30 to 60): spheres, teardrops, capsules, soft lathe
  profiles. No hard points, no teeth, no claws.
- **One distinguishing trait per subject archetype**, readable at thumbnail
  size (64 px): a long tail, a pair of ear-like fins, a ring around the body, a
  trailing wisp. Players must be able to name a subject from its silhouette
  alone in a 64 px leaderboard thumbnail.
- Shyness is drawn with shape: small bodies, tucked forms, heads lower than
  the body line; a subject "opening up" (spreading fins, rising) is its
  decisive moment.

### 3.3 Character geometry (players and NPCs)

- Quaternius Universal Base Characters (A5), dressed in simple stylized outfits
  (5.1, open). Proportions come from that base; they are not chibi.
- **The camera is the hero shape on a character.** It is slightly larger than
  real-world scale (about 1.2x) so it reads at distance, and it is the
  brightest detail on the figure (lens front ring, strap colour).
- NPC clients get one bold role prop silhouette each (a hat, an apron, a
  satchel, a clipboard) so they read as "people with a job" at a glance.

### 3.4 Gear geometry (bodies, lenses, phones)

Gear is the economy's main visual reward, so it gets the most precise shapes
in the game.

- **Lenses are concentric cylinders.** Rings (focus ring, aperture ring, tier
  ring) are separate cylinder parts. **Length and front diameter must express
  the specs:** a 24 mm wide lens is short and wide-fronted; a 200 mm is long; a
  fast f/1.4 has a visibly fat front element. A player should guess focal
  length roughly from the silhouette.
- **Bodies are boxes with a grip and a prism hump** (or flat-top for mirrorless
  types). Shapes copy no specific real product. [DEPENDS: brands]
- **Phones are rounded slabs** with a camera bump.
- Mount differences are shown by a coloured mount-ring index dot and the mount
  code in UI, not by complex geometry.
- **Matching the textured world.** Gear is a physical object but asset-forge cannot
  UV-map it, so it matches by other means:
  - Smooth shading on curves with crisp edges (`smooth_angle` 30 to 60), never flat
    facets, which would look like a different game beside the kit.
  - Real material values do the work: `metallic` and `roughness` per part, so rings
    and trim catch the same sun as the world.
  - Small chamfer rings and step details stand in for painted edge wear.
  - Optional shared surface grain from one small `texture_gen.py` tile, projected
    in the material so no UVs are needed. VERIFY: technical-artist to confirm
    triplanar mapping is usable on the Compatibility renderer.
  - Colours stay on the palette; the tier ring (4.4) stays the strongest accent.

### 3.5 UI shape grammar

The UI is its own language, borrowed from photography, not from the world:

- **Photo-print rectangles**: rounded corners (4 px radius at 720p), white
  print borders on any image.
- **The six-blade aperture polygon** (A8) is the hero UI shape: logo, loading,
  transitions, rarity badge.
- **Viewfinder geometry**: thin corner brackets, a rule-of-thirds grid,
  small square focus points, a horizontal exposure scale. Lines only, no
  filled panels inside the frame.
- **Panels are dark rounded cards**: Darkroom Ink at about 85 to 90 % opacity,
  about 10 px radius at 720p, a thin 1 px lighter edge (Ink Soft or a low-opacity
  Paper White), no bevels or skeuomorphic leather or metal. The textured world is
  busier than the old flat one, so UI text always sits on a panel, never directly
  on the scene (viewfinder readouts excepted, see above). Photo prints keep their
  sharper 4 px corners, so a photo never reads as a panel.

### 3.6 Hero versus supporting shapes

| Draws the eye (hero) | Recedes (supporting) |
|---|---|
| Subjects (smooth, untextured, glowing in lens view) | Ground, walls, roofs, rocks (textured, mid-value, graded down) |
| The rare event light | Ordinary sky gradient |
| Landmark verticals (lighthouse) | Repeated props (fences, crates, grass) |
| The camera on a character | Clothing detail |
| The print in any UI screen | Panels and chrome |

Rule: a scene has **one landmark** and **at most one active hero subject per
area** at a time, so the eye is never split.

---

## 4. Color System

### 4.1 Principle

**Surfaces are quiet; light and subjects carry colour.** World materials sit
in the middle of the value range at low to medium saturation, so the time of
day can visibly warm, cool, brighten and darken them. High saturation is
reserved for the sky, the event light, subjects and UI rarity cues.

**Grading the Quaternius textures (A18).** The pack colours are louder than this
principle: under golden light the spike's roofs go strong orange, and they fill
much of the three-quarter view. Each shared world material gets a tint or a
saturation pull at import, towards the palette below. The stylized look stays;
only its strength drops.

| Material | Pull towards | Check |
|---|---|---|
| Roof tiles | Driftwood Clay, with some Dusk Slate roofs for variety | no roof is the most saturated area of a frame at noon |
| Plaster | Weathered White | mid-to-light value, so light can still lift it |
| Timber | Driftwood Clay, darker | frames the wall without looking black at blue hour |
| Stone, cobble | Dusk Slate | broad value steps, low contrast between stones |
| Grass, foliage | Sage | golden hour can still turn it gold; bright red bushes and strong yellow flowers are accents only |

Exact tints are tuned in-engine against the 2.2 presets. Sky and light colours
stay as listed; nothing here changes a lighting preset.

### 4.2 Primary palette

| Name | Hex | Role and meaning |
|---|---|---|
| **Paper White** | `#F2EDE4` | Photographic paper. Print borders, UI light surfaces, the develop fade's starting colour. Means "a photo lives here". |
| **Darkroom Ink** | `#1E2230` | Deep shadow, UI dark panels, main text on paper. The darkest value in the game; never pure black. |
| **Dusk Slate** | `#4A5568` | Cool neutral for stone, roofs and distant layers; the main shadow-side tone. |
| **Sage** | `#7D9A78` | Vegetation base. Kept muted so golden hour can turn it gold and blue hour turn it teal. |
| **Driftwood Clay** | `#B9805C` | Warm earth, timber, brick. The warm counterweight to Slate. |
| **Golden Hour Amber** | `#F2B35E` | Warm key light, value, money, reward. The game's "good light" colour. |
| **Lumen** | `#7FE3D8` | The lens world: spirits, lens-only reveals, viewfinder focus confirmation. A hue the natural light presets never produce. [DEPENDS: setting; without spirits Lumen still marks "lens-only" information such as focus lock] |

Secondary and support colours:

| Name | Hex | Use |
|---|---|---|
| Sea Teal | `#3E7C86` | Water, coastal shadow |
| Sky Blue | `#7FB2DC` | Midday sky mid-tone |
| Weathered White | `#D9D2C5` | Painted walls, lighthouse body |
| Safelight Red | `#C8403A` | Darkroom lighting and the "shutter live / recording" dot only (A9) |
| Ink Soft | `#2E3446` | Second dark UI layer |
| Paper Shade | `#D8D1C4` | Second light UI layer, dividers |

### 4.3 Semantic colour vocabulary

| Colour | Means in Aperture | Never used for |
|---|---|---|
| Amber | Good light, reward, money, a sale | Errors |
| Lumen cyan | The lens sees something; focus locked; lens-only presence | Money, rarity |
| Paper White | A photograph, a finished thing | Warnings |
| Safelight Red | Darkroom; shutter is live | Danger, damage, enemies (there are none) |
| Violet (S tier) and prismatic (SSS) | Rarity only | Anything else |
| Muted Orange `#E08A3C` | Warning or "attention" in UI (low battery, card nearly full) | Rarity |

Errors (a failed trade, a lost connection) use Darkroom Ink text on Paper
White with an icon; they do not need a red, because red already means the
darkroom. This is assumption A9.

### 4.4 Rarity tier colours (gear and images)

| Tier | Colour | Hex | Blades lit (A8) | Frame ornament |
|---|---|---|---|---|
| C | Stone grey | `#9AA0A6` | 1 | plain border |
| B | Fern green | `#7FB27A` | 2 | plain border + corner tick |
| A | Lens blue | `#5B9BD5` | 3 | two corner ticks |
| S | Violet | `#9B7BD8` | 4 | four corner ticks |
| SS | Amber gold | `#F2B35E` | 5 | double border |
| SSS | Prismatic pearl | base `#FFF3D6`, shimmer from Lumen to Amber to Violet | 6 | double border + slow animated shimmer |

Rules:

- **The tier letter is always shown** next to the colour. Colour is never the
  only cue.
- SSS is the only animated rarity treatment anywhere in the UI, so it stays
  special. The shimmer respects a reduce-motion option (static gradient).
- On gear, the tier colour appears as **one ring** on lenses and one accent
  strip on bodies. Higher tiers also gain material quality: C and B matte
  plastic, A and S satin metal trim, SS brushed brass accent, SSS pearl ring
  with an emissive glint.
- SS shares its hue with Amber "reward". That is intended (SS and SSS are the
  valuable tiers), but SS must always carry its double border to stay distinct
  from a plain "sale" highlight.

### 4.5 Per-area colour temperature

| Area (A4) | Base temperature | Note |
|---|---|---|
| Village | warm (Clay, Weathered White) | warmest area; human life |
| Cliff and lighthouse | neutral-cool (Slate, Weathered White) | landmark against sky |
| Shore and pier | cool (Sea Teal, Slate) | water mirrors the sky, strongest time-of-day swing |
| Woodland strip | green-cool (Sage, Slate) | shade; dappled light is its "rare light" |
| Darkroom | red ambient, neutral print light | the only red-lit space |
| Gallery / hub | warm interior | prints are the brightest element |

### 4.6 UI palette and where it diverges from the world

The UI does **not** use the world's time-of-day colours, so it stays readable
over any sky. It uses two surfaces:

- **Darkroom mode** (dark): Darkroom Ink and Ink Soft panels, Paper White text,
  Amber and Lumen accents. Used in-game, in the viewfinder and on the
  leaderboard.
- **Print mode** (light): Paper White and Paper Shade panels, Darkroom Ink
  text. Used for the darkroom breakdown card, gallery labels and the shop.

Approximate contrast (to be measured with a contrast tool before sign-off):

| Pair | Approx. ratio | Use allowed |
|---|---|---|
| Darkroom Ink on Paper White | about 13:1 | all text |
| Paper White on Darkroom Ink | about 13:1 | all text |
| Amber on Darkroom Ink | about 8:1 | text and numbers |
| Lumen on Darkroom Ink | about 11:1 | text and numbers |
| Each rarity colour (C, B, A, S) on Darkroom Ink | about 4.5:1 to 6.5:1 | tier letters at 16 px+ only; S Violet is the weakest |
| Amber on Paper White | under 3:1 | **not for text**; icons with an Ink outline only |

### 4.7 Colourblind safety

| Risk pair | Who is affected | Backup cue required |
|---|---|---|
| C grey / B green / SS amber | deuteranopia, protanopia | tier letter + blade count + frame ornament |
| A blue / S violet | protanopia, tritanopia | tier letter + blade count (3 vs 4) + ornament (2 vs 4 ticks) |
| Lumen cyan / Sage green in the world | tritanopia | Lumen subjects also glow (value contrast) and have a soft rim; focus lock also shows a shape change (brackets close) |
| Safelight Red / Amber | protanopia | red is only ever an ambient and a "live" dot shape, never a state the player must read |
| Score breakdown good vs poor | all | bar length and number, never colour alone |
| Crew members (co-op) | all | role icon shape (Section 7) first, colour second |

---

## 5. Character Design Direction

### 5.1 Player photographer

- **Archetype:** an everyday outdoors photographer: practical jacket, bag or
  sling, camera or phone. Approachable and unheroic; the person is not the
  fantasy, the eye is.
- **Source:** Quaternius Universal Base Characters (male and female, with
  hairstyles) animated with the Universal Animation Library (A5). Characters keep
  their textures, since the world is now textured too. The bases are rigged for
  Godot, and their textures are graded to the palette like the world (4.1).
- **OPEN: outfits.** The Universal Base Characters are **underwear base bodies**.
  No clothing is in the installed packs, so they cannot ship as they are. The user
  must choose a route:
  1. A clothing or character pack from a free source, if one fits this rig.
  2. Outfits painted into the body texture. This is cheap and needs no new mesh, but
     it needs an artist or a texture tool, and the silhouette stays a bare body.
  3. Rigid add-ons from asset-forge (jacket shell, bag, hat) attached to bones. This
     stays in-house, but untextured shells may look stiff beside textured skin.
  4. Commissioning an artist, or buying a paid version.

  Until this is decided, the base bodies are placeholders only. Check the fit of the
  Universal Animation Library on the base rig in-engine as well; the installed files
  have not been tested together.
- **Customisation** (cosmetic, never tier, per the concept's anti pay-to-win
  rule): jacket colour from a fixed list drawn from the palette, hat, bag,
  camera strap colour. The strap is the player's personal identifier colour.
- **The camera is the hero** (Section 3.3). The held gear is the actual model
  the player owns, so a player carrying an SSS lens visibly carries its tier
  ring. This is the only place tier shows on a character.
- **Poses:** relaxed and grounded. Key poses: walk, crouch, raise camera to
  eye, check screen (camera) or hold phone up (phone), lower and look at the
  back screen after a shot. No aggressive or heroic stances.

### 5.2 NPC clients and townsfolk

- Same base bodies and the same open outfit question (5.1), with **one role
  silhouette prop** each (Section 3.3) and a muted palette (Clay, Slate, Sage) so
  they never outshine players or subjects.
- A client with a commission to offer carries a small floating Paper White
  "print" icon above the head (UI layer, never in photos).

### 5.3 Subjects (spirits) [DEPENDS: setting] (A17)

- **Made in asset-forge** as rigid-part models: floating bodies need no legs
  or skinning, so bob, drift, spin, scale pulse and part rotations (fins,
  tails, rings) are all animated in-engine by rotating named nodes, which
  asset-forge supports. No pack offers spirits, and they are the game's own
  identity, so this is the right place to make them ourselves.
- Design rules: soft rounded body, one distinguishing trait (Section 3.2),
  no mouth, at most a minimal two-dot face. Body in a pale tint of Lumen or
  Paper White; glow via an emissive material, not a real light.
- **Matching the textured world (A17, A20).** Spirits do not try to look like the
  kit. They are the opposite of it, and that is what makes them belong:
  - **Spirits are the only surfaces in the game with no texture.** Against painted
    tile and timber, a clean glowing form reads at once as "not of this world".
  - Smooth shading (`smooth_angle` 30 to 60), a brighter value than anything around
    them, and a soft rim so the edge stays clear on busy texture.
  - They still answer the scene's light: warmer on the sun side at golden hour, so
    they look present in the place rather than pasted over it.
  - Glow stays emissive first, with the halo-card fallback in 8.5 and 8.9.
  - The greyscale test in 6.5 is the pass or fail check, and textured backgrounds
    make it harder. Test spirits against the busiest kit surfaces, not plain ground.
- **Lens-only layer.** Spirits and memory traces live on their own render layer
  that only the viewfinder camera and the photo re-render can see. They must be
  absent from the exploration camera, so a spirit is never visible by accident in
  the three-quarter view. How the layer is built: technical-artist.
- **Tier is visible in design complexity,** not in size or threat: a common
  subject has one body and one trait; an SS or SSS subject adds a second
  orbiting part, a trailing wisp, and its own event light (Section 2.1).
- **Behaviour reads in pose** to support the Moment score: idle (tucked),
  wary (shrinks, drifts back), curious (rises, turns to camera),
  **decisive pose** (opens fully, holds for a short window, glow peaks). The
  decisive pose must be preceded by a readable anticipation (a pulse or a
  rise) so a skilled player can time it.
- **Naked eye vs lens:** a spirit's body is visible only through a lens (confirmed
  2026-11-05). In the naked-eye view the only sign is the faint shimmer defined in
  `design/gdd/subject-spirit-behaviour.md` F16, which is an effect in the air, not
  the spirit. On textured surfaces it must stay subtle but findable. [DEPENDS: setting]

### 5.4 Animals (wildlife role)

- CC0 rigged animals (Quaternius) graded to natural, muted palette tones. **No
  animal pack is installed yet**; any pack chosen must be checked against the
  textured world before use, because older low-poly packs may be flat-coloured.
  Animals are subjects too, so they follow the same pose vocabulary (idle, wary,
  curious, decisive).
- If the spirit setting is dropped, animals and light phenomena become the
  main rare subjects, and the "tier through complexity" rule applies to their
  markings and to the event light around them.

### 5.5 Telling them apart at a glance

| Type | Shape cue | Colour cue | Light cue |
|---|---|---|---|
| Player | human, camera hero shape | personal strap colour | none |
| Teammate (co-op) | as player | strap colour + role icon nameplate | none |
| NPC client | human + one role prop | muted palette | print icon if offering work |
| Animal | non-human, grounded | natural muted | none |
| Spirit [DEPENDS: setting] | smooth, floating, no legs | pale Lumen / Paper White | emissive glow in lens view |

### 5.6 Detail at camera distance (LOD philosophy)

- Detail is spent where the photo is taken: subjects are seen through a lens,
  often zoomed in at 85 to 200 mm, so **subjects get the most careful
  silhouettes and pose shapes** of any character.
- Players and NPCs are mostly seen at mid distance from the elevated three-quarter
  camera, but a telephoto can frame them closely; facial detail is minimal. Simplify, do not shrink: at distance, keep the camera
  and the role prop, drop small parts (straps, buttons, pockets).
- Telephoto lenses mean distant things can be framed large. Any subject that
  can be photographed from far away must still look good when filling the
  frame; LOD switching must respect the camera's zoom, not only distance
  (technical-artist to implement).

---

## 6. Environment Design Language

### 6.1 Architecture and culture (A4) [DEPENDS: setting, tone]

- **Storybook half-timbered village by the sea**: steep tiled gables, plaster and
  timber walls, stone footings, balconies and exterior stairs from the Medieval
  Village MegaKit, plus a pier on posts and a white lighthouse on a cliff.
  Familiar, slightly old-fashioned, not tied to one real country. Nothing medieval
  in theme is shown (no weapons, armour or castles): the kit supplies the building
  style only, and this is a place where people own cameras.
- **Known gap:** the lighthouse, pier, water and shoreline are not in the installed
  packs (8.10). In the spike the sea and sand are plain planes, which is the
  weakest part of the scene. A coast needs real work before this setting is proven.
- **Story of the place:** a village that was once busier. Some buildings are
  shut, some gardens overgrown, some posts and signs faded. People still live
  here, so it is quiet, not dead. [DEPENDS: setting; the "forgotten memories"
  angle makes abandoned rooms and empty frames the places memories cling to.
  Under a non-spirit setting the same decay reads as nostalgia.]
- **Built for photographs:** every area offers at least one strong vista with
  a landmark, at least one frame-within-a-frame (doorway, window, arch,
  branches), at least one leading line (pier, path, fence, wall) and open sky
  for light and time-of-day shots.

### 6.2 Texture philosophy

- **Default: the Quaternius stylized PBR sets** (A10 superseded). World surfaces
  use the packs' own base colour, normal and roughness or ORM maps. Painted,
  stylized and broad: this is the look. These are shared trim sheets, so many kit
  pieces use one material set, which helps both memory and draw calls.
- **Downsize everything for the Web.** The spike copied the textures at full size
  (2k and up) and its assets took about 77 MB. Size limits are in 8.6.
- **Grade at import, do not repaint** (4.1, A18). Keep one shared material per
  texture set, with tints set once, so the whole village stays consistent.
- **Ground and terrain.** Large ground planes need their own treatment, since the
  spike's flat green and sand show a visible repeating pattern. Blend at least two
  textures, or break the repeat with drifts of kit scatter. `texture_gen.py` tiles
  may fill a gap, recoloured to palette stops, if they sit well beside the kit.
- **Texture contrast stays low behind subjects.** Where a subject usually appears,
  prefer the calmer surfaces (plaster, grass) to the busier ones (cobble, tile).
- Wet stone after rain is lower roughness; glass is emissive at night instead of
  reflective. These rules are unchanged.
- **Never mix styles.** No photo-real textures from Poly Haven on gameplay geometry
  (anti-pillar: not photoreal). Poly Haven HDRIs are not used as visible skies
  either; skies are procedural gradients to match the time-of-day table.

### 6.3 Prop density

| Area type | Density | Why |
|---|---|---|
| Open vistas (cliff, shore) | sparse: 1 landmark, 2-3 supporting props, large negative space (sky 30-60 % of a typical frame) | light and horizon are the subject |
| Village streets | medium | frames within frames, human traces, mid-range compositions |
| Woodland strip | medium-dense at ground, open above | dappled light and depth layers |
| Interiors (darkroom, gallery, shop) | dense but ordered | tactile, handmade feeling; also no time-of-day light to carry the mood |
| Subject encounter spaces | sparse near the subject | the subject must read against a clean background |

Rule: **never place a prop where it would sit behind a subject's usual
position at the same value** as the subject (it would merge into it).

Rule: **scatter is composed, not sprinkled.** In the spike, evenly spread grass and
flowers read as random clumps. Plants gather in drifts along walls, fence lines and
path edges, with bare gaps between them, and one flower colour leads per drift.
Scatter placement is seeded or fixed, so it re-renders the same (P4).

### 6.4 Environmental storytelling

- **Found photos** (concept, Competition and social play): a print pinned to a
  post, propped in a window or tucked under a stone, marked by a small Paper
  White rectangle that catches light. Same marker everywhere so players learn
  it.
- **Traces of photographers:** tripod marks, a forgotten lens cap, a chalk
  mark on a wall where a good vista is. These quietly teach where to stand.
- **Light invitations:** gaps in walls, holes in roofs and windows placed so
  that at a specific time a beam of light falls somewhere worth shooting. The
  level should "promise" rare light windows before they happen.
- **Spirit traces** [DEPENDS: setting]: empty picture frames, faded
  silhouettes on walls, small cairns; places a memory lives. In lens view
  these show a faint Lumen shimmer.
- No text-heavy signage. Signs are icon or shape based.

### 6.5 Character versus environment legibility

- Environment: textured, mid-value, graded down (4.1), low texture contrast
  behind subject positions.
- Subjects: smooth, untextured, lighter or glowing, higher saturation, cleaner
  silhouettes.
- Players: mid-value with one bright strap and the camera as the brightest
  small detail.
- Check: a greyscale screenshot of any shooting spot must still show the
  subject as a clear, separate shape. This is a review test for every
  environment.

---

## 7. UI/HUD Visual Direction

> **Not reviewed by ux-designer.** This section is the art-director's
> direction only. Every item marked "UX check" needs the ux-designer's
> alignment pass before it is final.

### 7.1 Diegetic versus screen-space

- **Viewfinder HUD is diegetic**: it looks like the readout of the device the
  player is holding. It only appears while the player is looking through the
  lens.
  - *Camera skin* (A13): thin white corner brackets, rule-of-thirds grid
    (toggle), focus points as small squares that turn Lumen and close in when
    focus locks, a horizontal exposure scale (-3 to +3) at the bottom, a data
    strip showing focal length, f-number, shutter speed, ISO and shots left
    in IBM Plex Mono, the red "live" dot, and a battery icon.
  - *Phone skin*: rounded screen edge, a big circular shutter button, a
    simple zoom pill (1x, 2x), auto exposure shown as a small sun slider; no
    data strip. Friendlier and simpler, matching the phone's easier
    learning curve.
- **Everything else is screen-space**: darkroom breakdown, gallery, shop,
  market, leaderboard, menus. These use the darkroom and print modes from
  Section 4.6.
- **Exploration HUD is minimal**: a small device icon (phone or camera with
  battery and shots left), a compass strip (UX check), and context prompts.
  The world should be almost clear of UI, so a player is always composing.
- **Panel style in play**: any HUD element over the world uses the dark rounded
  cards from 3.5: compact chips at the screen edges, grouped so the centre stays
  clear. `design/art/demo.jpg` is a useful reference for this card style and for
  bright, legible text on dark over a detailed 3D scene. Take the styling, not its
  content, theme or density: that screen is much fuller than Aperture wants (7.6).
- **Nothing UI is ever in a stored photo** (P4).

### 7.2 Typography

| Role | Font (A11) | Weight | Size at 720p reference | Notes |
|---|---|---|---|---|
| Screen titles | Inter | SemiBold | 28 px | sentence case |
| Section headers | Inter | SemiBold | 20 px | |
| Body and labels | Inter | Regular / Medium | 16 px | default UI text |
| Camera readouts, scores, serial numbers ("SSS #12 of 100") | IBM Plex Mono | Medium | 16 px (data strip 14 px) | tabular figures so numbers do not jitter |
| Tier letters | Inter | Bold | 16 px minimum | always beside the tier colour |
| Minimum readable | | | **14 px** | nothing smaller at 720p; UX check |

- Personality: clean, calm, precise, a little technical, like a well-made
  camera menu. No decorative or handwritten fonts except optionally for a
  photo's caption that the player writes.
- Fonts are loaded as Godot font resources; asset-forge SVGs must not embed
  fonts (convert any text to paths, per its 2D reference).
- Text scaling option required (UX check).

### 7.3 Iconography

- **Outlined, single-weight icons** on a 24 px grid with a 2 px stroke and
  round caps and joins, made as SVG by asset-forge. One colour (Paper White or
  Darkroom Ink) plus at most one accent colour.
- **Gear icons are side silhouettes** that keep spec cues (lens length and
  front diameter, body grip shape) so they double as information.
- **Co-op role icons** (shape-first identification, Section 4.7): Wildlife =
  paw print, Portrait = oval face frame, Astro = four-point star, Street =
  compass arrow.
- **Rarity badge**: the six-blade aperture with N blades lit in the tier
  colour, plus the tier letter in the centre. Readable at 16 px; at 12 px or
  smaller show the letter only.

### 7.4 Key screens

- **Darkroom breakdown card** (print mode): the photo developing on Paper
  White, then seven horizontal bars (Subject, Focus, Exposure, Composition,
  Light, Moment, Rarity), each with its 0 to 100 number at the end, filling
  one by one. A one-line "why" under the weakest part to support learning.
  The final score and tier badge appear last. Bars are neutral Ink; only the
  final tier badge uses tier colour.
- **Gallery**: a grid of white-bordered prints with the tier ornament on the
  border, title and serial number below in Plex Mono.
- **Leaderboard**: a wall of prints on Darkroom Ink, rank number, owner name,
  gear used (icons), score and tier. SSS entries shimmer; nothing else moves.
- **Shop / gear detail**: turntable model, specs in a two-column table, tier
  ring visible on the model, price in Amber, serial number ("SSS body #7 of
  20") in Plex Mono.

### 7.5 UI motion

- **Iris transitions** (six-blade aperture closing and opening) between major
  screens, 250 to 350 ms, ease in-out.
- Panels slide 8 to 16 px and fade, 150 to 200 ms. Nothing bounces.
- Develop fade in the darkroom: 1.5 to 3 s, skippable after the first time.
- Score bars fill in sequence, 150 ms each, skippable.
- **Reduce-motion option** (UX check): iris becomes a cross-fade, SSS shimmer
  becomes static, develop fade becomes instant.

### 7.6 Art versus readability conflicts flagged (not decided)

These are the conflicts the art-director can see. They were not resolved and
need a ux-designer position before a decision by the user:

1. **Viewfinder minimalism versus information.** Art wants a clean frame for
   composing; players learning exposure may need more readouts. Proposed
   compromise: a toggle for an "assist" layer (histogram, exposure warnings).
2. **Darkroom red safelight versus legibility.** Resolved in direction by
   keeping all text on the print-mode card, never on red. UX to confirm.
3. **Data strip at 14 px** is below the 16 px body size. Art wants it small to
   feel like a real camera; UX may want it larger.
4. **Lumen focus lock versus colour vision.** Backed up by brackets closing
   (shape change); UX to confirm that is enough.
5. **Clear world versus online UI.** Art wants the exploration view almost free of
   UI; an online game may need chat, party and quest panels on screen. Proposed
   compromise: those panels collapse to small chips when not in use. UX to confirm.
6. **Thin viewfinder lines over textured scenes.** White 1 px brackets and grids sit
   directly on the image and may get lost on busy texture. A soft dark line behind
   them is the likely fix; test in-engine. UX to confirm.

---

## 8. Asset Standards

> **Not reviewed by technical-artist.** Every number below is an art-director
> value (A14). The project's performance targets given for this
> draft are: 60 fps, at most 500 draw calls, 512 MB memory, Godot 4.7.2,
> Compatibility renderer, Web export (WebGL 2). Note: `project.yaml` has no
> `performance` block yet, so these targets are not recorded in config.
>
> **All budgets in 8.3, 8.4 and 8.6 are PROVISIONAL until measured on the Web.**
> The only data so far is below. It is desktop only, and browser frame rate and
> load time have never been measured for this art.
>
> | Measured in the first scene (spike, 2026-11-05) | Value |
> |---|---|
> | Draw calls (includes shadow pass, desktop Compatibility, 1280x720) | about 640, over the 500 budget |
> | Triangles (same measure) | about 200,000 to 220,000 |
> | Objects per frame | about 660 |
> | Copied assets on disk | about 77 MB, mostly 2k+ PNG textures |
> | Web build, uncompressed | about 94 MB: `index.pck` 58 MB, `index.wasm` 39.5 MB |
>
> The spike had no optimisation at all, so these numbers are an upper starting
> point: separate nodes, full-size textures, no merging or instancing.

### 8.1 File formats

| Asset type | Format | Made by |
|---|---|---|
| 3D models, world and characters | `.gltf` + `.bin` or `.glb` as supplied | Quaternius packs (8.10) |
| 3D models, gear and spirits | `.glb` | asset-forge `model_glb.py` |
| World textures | `.png` from the packs, downsized (8.6) | Quaternius packs |
| Seamless textures | `.png`, power of two (+ `_n.png` normal map only where needed) | asset-forge `texture_gen.py`, gap-filling only (6.2) |
| UI, icons, HUD | `.svg` (Godot imports directly); `.png` only where needed via `svg_raster.py` | asset-forge (SVG written directly) |
| Pixel sprites | `.png` + frame `.json` | asset-forge `pixel_sprite.py` (limited use: e.g. stylised effect frames, small found-photo stickers) |
| Recipes (source of truth) | `.json` in `design/assets/recipes/` | asset-forge |
| Previews (not shipped) | `.png` in `design/assets/previews/` | asset-forge |

### 8.2 Naming convention

Pattern: `[category]_[name]_[variant]_[size].[ext]`, lowercase, underscores.

| Prefix | Use | Example |
|---|---|---|
| `env_` | environment pieces | `env_lighthouse_main_large.glb`, `env_cliff_chunk_02.glb` |
| `prop_` | props | `prop_crate_weathered_small.glb` |
| `char_` | humans and animals | `char_player_base_01.glb`, `char_npc_client_fisher.glb` |
| `subj_` (A15) | photographable subjects | `subj_wisp_common_01.glb` |
| `gear_` (A15) | bodies, lenses, phones | `gear_lens_std50_f18_a.glb`, `gear_body_mirrorless_s.glb`, `gear_phone_basic_c.glb` |
| `tex_` | textures | `tex_sand_shore_256.png` |
| `ui_` | UI | `ui_icon_lens_24.svg`, `ui_badge_tier_sss.svg` |
| `vfx_` | effects | `vfx_motes_beam_loop_small.png` |

Gear rules [DEPENDS: brands] (A3):

- Gear file names use **type, focal length / spec and tier**, never a brand
  name (`gear_lens_tele200_f28_ss.glb`, not `gear_lens_nokta_200.glb`), so a
  brand decision never forces a rename.
- No brand name or logo is modelled into geometry or textures. Brand marks
  are a separate decal or UI label driven by data.

Placeholders use `_placeholder` or `temp_` so `/launch-checklist` catches
them (per asset-forge's free-sources reference).

CC0 imports keep their licence and source URL recorded in
`design/assets/asset-manifest.md` (per asset-forge's free-sources reference),
and are renamed to this convention on import.

### 8.3 Polygon budgets (triangles, PROVISIONAL)

The old budgets were sized for hand-made low-poly. Quaternius assets are much
heavier, so the budgets below start from real pack counts (read from the glTF
files, 2026-11-05).

| Category | Measured in the pack | Budget (LOD0) | Notes |
|---|---|---|---|
| Small prop (crate, sign) | crate 230 | 50-300 | |
| Medium prop (wagon, bench, boat) | not measured | 300-1,500 | |
| Wall section | plaster wall 86 | up to 300 | |
| Roof piece | 6x8 round tiles 3,796 | up to 4,000 | the heaviest kit piece found; check every roof |
| Assembled house | not measured | up to 15,000 | merged by material |
| Hero landmark (lighthouse) | no pack piece | up to 15,000 | one per area |
| Rock | medium rock 342 | up to 400 | |
| Tree | pine 3,947; common tree 6,265 | up to 6,500, with LOD1 at 1,500 or fewer | at most 8 at LOD0 in any view |
| Grass or flower clump | tall grass 326 | up to 350 | instanced; about 100 near the camera |
| Subject, common | n/a | 400-1,200 | smooth parts, rigid animation |
| Subject, SS / SSS | n/a | up to 2,000 | extra orbiting parts |
| Player / NPC | base body with hair about 14,300 | up to 15,000 near; 5,000 at LOD1 | outfits add to this; at most 4 at LOD0 in view |
| Animal | no pack chosen | up to 5,000 | |
| Held camera body / lens | n/a | 300-600 / 150-400 | seen on the character and in shop |
| Gear shop close-up model | n/a | up to 1,500 | can be a separate LOD0 of the held model |
| **Scene total** | about 200,000-220,000 | **target 150,000; ceiling 200,000** | counted as the spike did, so the shadow pass is included |

Suggested split of the 150,000 target: buildings 60,000, trees 30,000, scatter
and rocks 25,000, characters 20,000, subjects and gear 5,000, everything else
10,000.

### 8.4 Draw calls (500 max)

The 500 limit stays as the **ceiling, now counted including the shadow pass**, the
way the spike measured it. The working target is **400**, to leave room for slower
browsers. The spike's 640 had no merging or instancing, so this should be reachable,
but that is unproven. If merging cannot reach 500, raise it; do not quietly raise
the budget.

Provisional allocation per view:

| Group | Budget |
|---|---|
| Environment, main pass (terrain, buildings, props, foliage) | 200 |
| Shadow pass | 100 |
| Characters, subjects and held gear (4 players + NPCs + subjects) | 60 |
| Effects (motes, water, glow cards) | 30 |
| UI | 60 |
| Headroom | 50 |

Target for objects per frame: **300 or fewer** (spike: about 660).

Rules:

- **Merge static kit pieces.** Each finished house becomes one mesh per shared
  material, not dozens of nodes. This is the largest saving available. asset-forge
  models use `merge: true` as before. How to merge at import or in the scene:
  technical-artist. Merged buildings still need their LODs and shadow settings.
- **Shared materials.** Every kit piece using a texture set shares one material
  from a library, rather than one copy per imported file, so assets can share
  state. Exact import settings: technical-artist.
- Repeated scatter (grass clumps, rocks, fence posts) uses instancing
  (`MultiMeshInstance3D`) rather than individual nodes.
- **Limit shadow casters.** Grass, flowers, pebbles and small props cast no shadows.
  Buildings, trees and characters do, because those shadows are what the player
  reads (P1).
- Materials per asset-forge model: **3-6** (asset-forge guidance), and props
  should aim for 3 or fewer.
- Any outline or second material pass doubles a mesh's draw calls (chibi toon
  spike), so none is planned for this direction.

### 8.5 Materials, lighting and effects

- **Emissive first, lights second.** Emissive works in the Compatibility
  renderer; transparency costs more (asset-forge engine-import reference).
  Spirits, windows, lamps and the lighthouse lamp glow through emissive
  materials.
- **Avoid alpha blending.** At most one alpha-blended layer in any view
  (e.g. one spirit wisp or the beam motes). Spirits are opaque with emissive
  and a rim effect, not see-through. Leaves, grass and vines use hard cut-out
  transparency (alpha scissor), not blending. VERIFY: how each pack material
  imports, and the cost of large areas of cut-out foliage on the Web.
- **PBR maps cost fragment time.** Every normal and roughness or ORM map is an
  extra texture read per pixel on a Web GPU. Keep them where they help the light
  read (8.6). VERIFY: real cost, measured in a browser on low-end hardware.
- **One shadow-casting directional light.** Real local lights only where light
  must fall on other surfaces. VERIFY: per-object light limits in the
  Compatibility renderer are not covered by `docs/engine-reference/godot/`.
- **Glow / bloom** on emissives is desired. VERIFY: glow availability and
  behaviour in the Compatibility renderer on 4.7.2. The pinned reference only
  states that glow now processes before tonemapping (4.6); it does not say
  whether Compatibility supports it. Fallback: small camera-facing halo cards.
- **Depth of field is a core risk.** Background blur from aperture (f/1.4 vs
  f/8) is part of the core fantasy and of the concept's lens specs. VERIFY:
  whether Godot's depth-of-field camera effect works in the Compatibility
  renderer is not covered by the pinned engine reference. If it does not, the
  technical-artist must find a cheap alternative for the viewfinder view and
  stored-photo renders only. **This is the biggest open visual-technical risk
  in this bible.**
- Shaders: none are specified here; the technical-artist owns them. Any
  animated shader (wind, water, shimmer) must take time from the world clock,
  not a free-running timer, so photos re-render the same (P4).

### 8.6 Textures and memory (512 MB total)

Pack textures are 2k and larger as supplied (spike). All are downsized on import.

| Use | Base colour | Normal | Roughness / ORM |
|---|---|---|---|
| Village trim sets (wall, roof, timber, stone) | 1024 px | 512 px | 512 px |
| Foliage, bark, flowers, grass | 512 px | none, or 256 px on bark | none |
| Characters (skin, hair, outfit) | 512 px | none | none |
| Ground and terrain | 512 px | 256 px on cobble | none |
| Close-up interiors (darkroom table, gallery wall, shop) | 512 px | none | none |
| asset-forge tiles | 256 px | only where needed | none |
| UI atlas or large UI | up to 1024 px | | only if SVGs are rasterised into an atlas |
| Not allowed | above 1024 px | | |

- Power-of-two sizes only (asset-forge requirement for textures).
- A scene loads only the texture sets it shows.
- Texture memory budget stays **64 MB per loaded scene**, leaving the rest of the
  512 MB for engine, audio, meshes, networking, the photo cache and browser overhead.
  The Photo Recipe GDD builds on this figure.
- **Worked estimate, uncompressed with mipmaps:** one village set is about 8 MB
  (5.3 + 1.3 + 1.3), six sets about 48 MB, eight 512 px foliage textures about
  11 MB, and characters about 5 MB. Total about 64 MB. That is **exactly at the
  limit with no spare room**, so GPU texture compression or fewer sets is needed.
  VERIFY: web texture compression formats and their Godot 4.7.2 web export
  settings are not covered by the pinned engine reference.
- **Download budget (provisional):** `index.pck` for the first area **24 MB or
  less** (spike: 58 MB), so about 64 MB uncompressed with `index.wasm`. Later areas
  load on demand. Measure the real transfer size with server compression on,
  because that, not the file size, is what a player waits for.
- Skies are procedural gradients (no HDRI files), saving memory and matching
  Section 2.2.

### 8.7 LOD levels

| Category | LOD0 | LOD1 | LOD2 |
|---|---|---|---|
| Buildings, landmarks | full | about 50 % | silhouette card or merged block |
| Trees, rocks | full | about 50 % | merged clump |
| Characters | full | simplified (drop straps, small parts) | none; cull |
| Subjects | full | about 60 %, silhouette kept | none |
| Small props | full | cull at distance | |

LOD choice for subjects and characters must consider the active focal
length (Section 5.6). Whether to use Godot's automatic mesh LOD or hand-made
LODs from asset-forge recipes: technical-artist.

Treat Quaternius assets as having no LODs until checked. Trees and characters are
heavy, so LOD1 is required for them, not optional (8.3). VERIFY: how well
generated LODs keep the look of cut-out foliage, and whether they work on the
Compatibility renderer.

### 8.8 Export and import settings

- Units in metres, +Y up, model front faces +Z, origin at the base (y = 0)
  for props and characters, the grip for held gear, the hinge for doors
  (asset-forge model reference).
- Parts that animate keep their own named nodes (`merge: false`); everything
  static is merged.
- asset-forge models in this game are gear and spirits, so both use `smooth_angle`
  30-60. Flat shading (`smooth_angle: 0`) is no longer used for shipped models.
- Recipes are the source of truth: edit the recipe and regenerate, never
  hand-edit a generated binary.
- Pack files are not edited in place. Downsizing, tints and merges happen at import
  or in the project copy, so a clean pack can always be re-imported.
- Folder layout as in asset-forge's engine-import reference
  (`assets/art/models/`, `assets/art/textures/`, `assets/art/ui/`, ...).

### 8.9 Art preference versus technical limit (recorded, not decided)

| Topic | Art ideal | Likely constraint | Proposed default until technical-artist reviews |
|---|---|---|---|
| Depth of field | true lens blur in viewfinder and photos | may be missing or costly in Compatibility (VERIFY) | must exist in some form; method left to technical-artist |
| Glow on spirits and lights | soft bloom | may be missing in Compatibility (VERIFY) | halo cards fallback |
| Spirits | slightly translucent | alpha cost on web | opaque + emissive + rim |
| Dynamic lights | many warm window lights at blue hour | light limits per object (VERIFY) | emissive windows, few real lights |
| Shadow quality | soft long shadows at golden hour | shadow cost on web | one directional shadow; quality setting by technical-artist |
| Texture detail | pack textures at high size with all PBR maps | download size, memory and fragment cost | 8.6 size limits; drop maps first on low-quality settings |
| Foliage | full pack trees everywhere | 4,000 to 6,300 triangles each; cut-out cost (VERIFY) | 8 at LOD0, LOD1 beyond |

### 8.10 Asset sourcing

| Source | What it supplies | Why |
|---|---|---|
| **Medieval Village MegaKit** (Standard) | walls, roofs, floors, stairs, balconies, doors, windows, village props | the world's style standard; modular, shared texture sets |
| **Stylized Nature MegaKit** (Standard) | trees, bushes, grass, flowers, rocks, pebbles, path pieces | same stylized PBR language as the village |
| **Universal Base Characters** (Standard) | human bases, hairstyles | rigged bases; outfits are open (5.1) |
| **Universal Animation Library** (Standard) | humanoid animation | walk, idle and similar; poses in 5.1 still need checking against what it holds |
| **asset-forge: gear** | bodies, lenses, phones | no pack has them; they need exact spec-driven shapes (3.4), many variants from recipes, and no copied real products |
| **asset-forge: spirits** | all subjects from 5.3 | they are the game's own identity, and rigid-part floating bodies suit the tool |
| **asset-forge: UI** | SVG icons, badges, panels, aperture motif | no pack holds this design language |
| **Engine-built** | water, sky, particles, lens effects | shaders and particles, by the technical-artist |

asset-forge **no longer makes environment or props**, so that the world keeps one
hand. Exceptions need a reason, such as the gaps below.

**Gaps in the installed packs (open):** lighthouse, pier, boats, shoreline, sea,
animals, clothing, and darkroom, gallery and shop props. Each needs a route: another
free pack, kit-bashing from existing pieces (for example, a lighthouse from stone
walls and `Roof_Tower_RoundTiles`), or a recipe that follows 3.4's matching rules.

### 8.12 Decisions recorded 2026-11-06 (user)

- Outfits: download free outfit packs and compare.
- Setting: keep the coastal village; build the lighthouse and pier from kit pieces, other packs or asset-forge.
- Packs: free Standard versions only.
- Repository: public, so third-party assets stay out of git.

### 8.11 Licence note

- The installed pack files (`License_Standard.txt`, `License.txt`) all state **CC0 1.0**.
- The site's newer **Quaternius Asset License (QAL) v1.0** (quaternius.com/license.html, read 2026-11-05) allows free personal and commercial use in games with no credit, and forbids redistributing the assets themselves as assets or packs, free or paid, even modified. Distributing a finished game that contains them is allowed.
- **Working rule, safe under either licence:**
  - Keep raw packs out of public repositories.
  - Ship only what the game uses, inside the game build.
  - Never publish the assets as a pack, a source mirror or a template.
- Check whether the prototype copy under `assets/` is in any repository that may go
  public. `.gitignore` and repository visibility are worth a look before the next push.
- Log each pack, its source URL, the licence file's wording and the download date in
  `design/assets/asset-manifest.md` (8.2).

---

## 9. Reference Direction

References 1 to 5 were chosen by the art-director (A16). They point in different
directions on purpose: camera UI, subject behaviour, colour of light,
composition, and spirit character. References 6 and 7 came from the user.

**1. Umurangi Generation (Origame Digital, 2020): camera feel and lens
swapping**
- *Take:* the tactile, readable viewfinder; swapping lenses that visibly
  change field of view; a camera HUD that feels like a device, not a menu.
- *Avoid:* its gritty, dystopian palette, graffiti textures and visual noise.
  Aperture is calm and clean.

**2. New Pokémon Snap (Bandai Namco / The Pokémon Company, 2021): subjects
and scoring presentation**
- *Take:* subjects with readable behaviour states and a clear "special pose"
  moment; a post-shot evaluation that explains why the photo scored well.
- *Avoid:* its saturated, toy-bright palette and on-rails staging. Our
  subjects are shy and muted, and the player chooses where to stand.

**3. Firewatch (Campo Santo, 2016): colour of light over time**
- *Take:* strong time-of-day palettes where each hour has its own sky and shadow
  colour, and aerial perspective in layered depth.
- *Avoid:* the near-monochrome orange grade. We let each time of day differ. The
  spike's single warm tint across the whole frame is exactly this mistake.

**4. Fan Ho and Saul Leiter (street photographers, 1950s-60s):
composition of light**
- *Take:* light shafts and pools as the subject, frames within frames
  (windows, doorways, reflections), layered foregrounds and large negative
  space. These are the compositions level designers should build for.
- *Avoid:* black-and-white grain filters or vintage overlays on the game
  image. We borrow their compositions, not their film look.

**5. Studio Ghibli's small forest spirits (e.g. the kodama in Princess
Mononoke, 1997): spirit character** [DEPENDS: setting]
- *Take:* how a very simple, small, slightly uncanny form with minimal
  features can feel alive and shy; spirits that are more curious than
  frightening.
- *Avoid:* copying any specific design, the hand-drawn look, or any face
  likely to read as eerie. Our spirits are geometric, glowing and built from
  rounded primitives.

**6. Quaternius Medieval Village MegaKit preview image (user-supplied): the target
world**
- *Take:* rich stylized surfaces, warm light on plaster and timber, a blue sky with
  painted clouds, a winding path as a leading line, overgrown edges. This is the
  quality bar for the village.
- *Avoid:* assuming it is reachable as shown. It is a high-end offline-quality
  render, probably using the paid kit and custom shaders, not the free kit on the
  Web Compatibility renderer. The spike is well below it. Its dense, strong colour
  is also louder than 4.1 allows.

**7. `design/art/demo.jpg` (user-supplied): style only**
- *Take:* the elevated three-quarter framing of a small, readable place, and dark
  rounded HUD cards with clear text over a detailed scene.
- *Avoid:* **all of its content**: its setting, theme, characters, text and
  game ideas must not be copied. Also avoid its screen density (7.1, 7.6).

Production baseline (not a style reference): the Quaternius packs set the
world's style. Imported assets are graded to this bible (4.1, A18), not repainted.
