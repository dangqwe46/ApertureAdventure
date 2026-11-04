# Player Movement & Exploration

> Authoring guidance: .claude/docs/templates/guidance/game-design-document-guide.md (load per-section as you author — do not read entirely).

> **Status**: Designed 2026-11-03 (pending `/design-review` in a fresh session)
> **Author**: game-designer agent (draft for the user; every choice made on the user's behalf is listed in "Decisions to confirm")
> **Last Updated**: 2026-11-03
> **Last Verified**: 2026-11-03
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-03 — CONCERNS fixed: client-side eye-band check in `can_shoot` plus no-false-reject criterion (37); Pillar 3 re-attributed to co-op rules; setting marked unconfirmed; protect-role guardrail; Hurry-share playtest criterion (38). NOT ASSESSED: MDA aesthetics target (none stated); tone fit (tone unconfirmed).
> **Implements Pillar**: Pillar 1 "Seeing is the skill" (where you stand *is* composition: position and eye height are the first framing choice); Pillar 3 "Play together without violence" (through the co-op rules: no player collision and teammates ghosted, never in photos — R20, D9); the quiet tension of approaching shy subjects serves Pillar 1 (reading and timing). Supports Pillar 2 "Every photo matters" by making every recipe's camera pose trustworthy.
> **Review gates**: CD-GDD-ALIGN, TD feasibility and `/design-review` NOT RUN (subagent without Agent tool). Engine claims not found in `docs/engine-reference/godot/` are marked UNVERIFIED.

## Summary

Player Movement & Exploration moves one photographer through a small low-poly area in third person and, when the player raises the device, puts them in a first-person viewfinder whose eye position becomes the camera pose stored in the photo recipe. It owns walking, hurrying, sneaking, contextual traversal, look input (including Web pointer lock), the "presence" signal that tells shy subjects how noticeable the player is, and the rules the server uses to decide that a recipe's camera pose was physically reachable. There is no jumping, no combat, no stamina and no fall damage: movement is calm, readable and in service of standing in the right place at the right moment.

> **Quick reference** — Layer: `Foundation` · Priority: `MVP` · Key deps: `None` hard; interface contracts with Network Transport & Server Authority (pose trail, validation) and Settings & Accessibility (sensitivity, toggles). Read by Camera Model, Photo Recipe & Re-render, Subject & Spirit Behaviour, Zone Access & Travel, Expedition Rooms, Shared Hub.

## Overview

Aperture's core loop starts with **Explore**, and this system is what the player's hands are doing during it. (The coastal village and the shy-subject setting come from the art bible and concept proposals and are not yet confirmed by the user; the rules here do not depend on them.) The player walks a photographer through the coastal village (art bible A4: cliff, lighthouse, pier, houses, woodland strip) from a third-person over-the-shoulder camera, reading light, sky and subject behaviour from a distance. When they find a shot, they raise the device: the view cuts to a first-person viewfinder at the photographer's eye, movement slows to a careful shuffle, and look input becomes precise and scaled to the lens's field of view. The shutter only works in this mode, so **every photo's camera pose is an eye pose of a body standing on reachable ground**.

The system has three jobs. **For the player**, it makes position and eye height (standing or low) an expressive, low-friction choice, and it makes approaching a shy subject a quiet game of speed and footing rather than a fight. **For other systems**, it publishes the eye anchor and look orientation (Camera Model), the stance and body speed at the moment of capture (Photo Recipe), and a presence radius (Subject & Spirit Behaviour). **For the server**, it defines what "plausible camera position" means: the pose must sit inside a baked eye volume for the zone, and it must be consistent with the player's recent movement trail. The server does not simulate the player's physics; it checks the result.

Implementation approach (client prediction model, snapshot encoding, reachability-map format) is not decided here → becomes an ADR.

## Player Fantasy

**"I move like a photographer, not a soldier."** The player should feel like someone on a slow walk with a camera over their shoulder (art bible 2.1, Exploration: "calm curiosity"), who can stop anywhere, crouch for a low angle, and ease toward something that might bolt. The emotional beats are:

- **Unhurried noticing** (MDA: *Discovery*, *Sensation*). The third-person camera shows the sky and the light; walking feels light and responsive, never floaty, so the player looks at the world rather than at their feet.
- **The held breath of approach** (MDA: *Challenge*, *Fantasy*). Near a shy subject, the player chooses to slow down, sneak, and pick quiet ground (grass over planks). Their footsteps get softer and the subject's pose tells them whether they were noticed. Success comes from patience and reading, which is Pillar 1's "the player's eye and timing".
- **"I'm standing in exactly the right place"** (MDA: *Expression*). Raising the viewfinder is instant enough that framing feels like an extension of looking. Small adjustments (a half-step left to put the lighthouse on a third, crouching to put the horizon low) are cheap and precise.

SDT mapping: **Autonomy** from free positioning and stance with no "photo spots" forced on the player; **Competence** from readable presence feedback (footstep loudness, subject reactions) and precise look control; **Relatedness** in co-op from seeing teammates' stances and raised viewfinders, which reads as "they've found something".

What the player must never feel: punished for exploring (no fall damage, no getting lost outside the map), fighting the controls in the viewfinder (no smoothing lag on mouse look), or cheated by the browser (the first click never takes a photo).

## Detailed Design

### Core Rules

**R1. Perspective.** Exploration uses a third-person over-the-shoulder camera. Raising the device switches to a first-person viewfinder at the photographer's eye anchor. Lowering it returns to third person. The shutter is available **only** in the viewfinder (R14). (Art bible A6; see D1.)

**R2. Character body.** The photographer is a capsule character body (radius 0.30 m, standing height 1.75 m, sneak height 1.15 m) moved with a kinematic slide-and-collide step on the 3D physics engine (Jolt, the 4.7 default; `CharacterBody3D` + `move_and_slide()` per `physics.md`). Gravity applies when not on floor (`get_gravity()` per `physics.md`).

**R3. Locomotion modes.** Exactly three ground speeds exist, plus a viewfinder modifier:

| Mode | Default speed | How entered |
|---|---|---|
| Walk | 3.0 m/s | default with move input |
| Hurry | 5.0 m/s | hold Hurry (Shift) while moving; not in viewfinder |
| Sneak | 1.3 m/s | toggle Sneak (C) |
| Viewfinder raised | Walk × 0.40, Sneak × 0.60 | while raised (R12) |

There is **no stamina**; Hurry is unlimited. Its cost is presence (R9), not a resource. (D2.)

**R4. Analog input.** Move input is a 2D vector. Keyboard input is normalised (diagonals are not faster). Analog stick and virtual-joystick magnitude scales target speed linearly between the dead zone and full deflection, so a half-pushed stick walks slowly. Hurry requires stick magnitude ≥ 0.85.

**R5. Facing.** In third-person, the body turns to face its movement direction at `turn_rate` (720°/s) relative to the camera's yaw; the camera does not follow the body. In the viewfinder, the body yaw is locked to the look yaw, and movement becomes strafe-relative to the look direction.

**R6. Acceleration.** Horizontal velocity moves toward the target velocity at a constant rate: `accel` when speeding up, `decel` when slowing or reversing (Formula F2). Vertical velocity is gravity only. There is no momentum carry from slopes.

**R7. No jump. Contextual traversal only.** There is no jump button (D3). Instead:
- **Step-up:** ledges up to `step_height` (0.35 m) are climbed automatically while walking into them (stairs, kerbs, rocks). UNVERIFIED: `CharacterBody3D` has no built-in step-up in the engine reference; it is a gameplay-programmer implementation item.
- **Slopes:** walkable up to `floor_max_angle` (40°). Steeper surfaces behave as walls.
- **Authored traversal points:** ladders, rock scrambles and low walls are marked in the level as traversal volumes. Entering one shows a prompt (Interact, E); pressing it plays a fixed-duration move (ladder: 1.0 s per 2 m climbed; scramble/vault: 0.8 s) along an authored path. Input is ignored during the move except Lower/Cancel, which is not allowed mid-move (the move finishes). The viewfinder cannot be raised during a traversal move.
- **Drops:** the player may walk off any drop up to `safe_drop_height` (1.8 m) and lands with a soft landing animation, no damage and no stun. Edges with a larger drop have an **edge guard**: authored or auto-generated blocking collision that stops the player at the lip (cliff tops, the lighthouse gallery, the pier end). (D4.)

**R8. Water.** The player can wade into water up to `wade_depth` (0.6 m) at Walk × 0.6 speed (Hurry disabled). Deeper water has a soft push-back volume that slides the player back toward shallow water. There is no swimming in MVP.

**R9. Presence.** The player continuously emits a **presence radius** in metres: how far away a shy subject can notice them. It rises with stance, horizontal speed and footing (surface type), spikes on discrete events (landing from a drop, finishing a traversal move), and decays smoothly rather than vanishing when the player stops (Formulas F4, F5). This system **owns computing and publishing presence**; Subject & Spirit Behaviour **owns every reaction** (thresholds, line-of-sight checks, wary/curious/flee responses). Other systems may add presence events through the same channel (e.g. Camera Model for a loud shutter), with their own magnitudes. (D5.)

**R10. Eye anchor.** The eye anchor is the camera origin used in the viewfinder and recorded in the recipe:
- Standing eye height: 1.60 m above the capsule's foot. Sneaking: 1.05 m.
- The anchor's height is smoothed over 0.10 s on step-ups and stance changes so the viewfinder never jolts; the recipe records the **smoothed** value actually rendered.
- If the eye anchor would be closer than 0.15 m to collision geometry, it is pushed back along the look direction until clear.

**R11. Look.** Mouse look rotates yaw (unbounded) and pitch (clamped). Pitch limits: third-person −60° to +70°; viewfinder −85° to +85°. Roll is always 0 in this system (Camera Model may add a deliberate tilt later; D-open in Open Questions). Mouse look is **raw**: no smoothing, no acceleration (Game Feel). Gamepad look uses a response curve and dead zone (F7). Arrow keys are always bound to look as a keyboard fallback (prototype precedent and pointer-lock fallback, R13). In the viewfinder, all look sensitivity scales with the current field of view so a 200 mm lens is not twitchy (F6).

**R12. Viewfinder raise/lower.** Raise (hold RMB, or toggle F; hold-vs-toggle is a setting, default hold for RMB and toggle for F) plays a 0.22 s raise; Lower plays 0.18 s. During raise the camera blends from the third-person boom to the eye anchor; the shutter becomes enabled only when the raise completes. While raised: Hurry is ignored, speed is reduced (R3), and traversal prompts are hidden. Lowering is instant-cancelable back to raised (pressing raise again during a lower reverses from the current blend point).

**R13. Web pointer lock (mouse).**
- The game starts in **cursor mode** with a "Click to look" overlay over the 3D view.
- A click on the 3D view requests pointer lock (Godot `Input.mouse_mode = MOUSE_MODE_CAPTURED` mapping to the browser Pointer Lock API on Web: UNVERIFIED in the engine reference). **That click is consumed**: it never fires the shutter, interact or any other action, whether or not the lock is granted. This is the prototype's finding (the first click to focus the page took a photo).
- After a lock is gained, the shutter ignores mouse-button input for a further `lock_grace_ms` (250 ms) so a double-click cannot shoot.
- When pointer lock is lost for any reason (Esc, alt-tab, browser UI, tab hidden), the game: releases all held inputs, sets the target velocity to zero, keeps the current stance and viewfinder state, disables mouse shutter, and shows the pause/"Click to look" overlay. Keyboard shutter (Space) stays available only if the viewfinder is raised **and** the page has keyboard focus.
- Esc is browser-reserved for leaving pointer lock; the game never relies on receiving the Esc key event while locked (UNVERIFIED whether the event reaches the page). Pause opens on lock loss instead.
- If a lock request is refused (browsers rate-limit re-requests shortly after an exit: UNVERIFIED in engine reference, browser behaviour), the overlay stays and says "Click again to look"; keyboard look (arrow keys) and keyboard movement keep working.
- No bound key uses Ctrl or browser-reserved combinations (Ctrl+W, Ctrl+T, Ctrl+N, F5, F11). (D6.)

**R14. Shutter gate (owned here only as a gate).** Movement exposes `can_shoot`, which is true only when: viewfinder raise complete, not in a traversal move, not respawning, the current eye pose passes the same eye-band check the server uses (F8, run locally on the client's copy of the baked eye volume), and (for mouse shutter) pointer locked and past `lock_grace_ms`. A shot the server would reject on R18 can therefore never be taken from a lawful position. Camera Model owns what the shutter does.

**R15. Capture pose snapshot.** On the frame the shutter fires, this system writes a **capture pose** that Photo Recipe stores: eye position (m, zone space), yaw and pitch (degrees), stance (`stand`/`sneak`), horizontal body speed (m/s), surface ID under the feet, and the client timestamp. The pose is taken at shutter press, not after any shutter delay; Camera Model owns any delay-induced motion effects.

**R16. Safe position and respawn.** Every `safe_sample_interval` (1.0 s) while on a walkable floor, not in water deeper than 0.3 m, and not in a traversal move, the last safe position is updated. The player is respawned to it with a 0.4 s fade if they fall below the zone's kill plane, end up in deep water, or choose "Unstick" (offered after 3 s of move input with less than 0.1 m displacement, and always available in the pause menu). Respawn resets the server trail with a server-issued anchor (R19).

**R17. Zone bounds.** Each zone has a soft boundary: a push-back volume 2 m inside the hard edge. The player is never killed or warped by the boundary itself.

**R18. Server reachability check (what the server validates).** When a recipe is submitted, the server validates its capture pose against the zone's **baked eye volume**, without running player physics:
1. **Sanity:** all fields finite; pitch within ±85°; roll = 0 (or within Camera Model's roll limit when defined); stance is a known value; speed ≤ `hurry_speed × (1 + speed_tolerance)`.
2. **Eye band:** a walkable cell exists within horizontal distance `nav_tolerance` of the eye position whose ground height `h` gives an eye height inside the band for the recorded stance (F8). This also proves the eye is not inside solid geometry, because walkable cells are baked with headroom.
3. **Zone match:** the pose is inside the zone the server believes the player is in.
**Result:** failing any of 1-3 → the recipe is **rejected** (no score, no tier roll, no gallery entry), the client is told "The shot couldn't be developed", and a `pose_invalid` log entry records the failing check. (D7.)

**R19. Server trail plausibility.** The client sends a **pose sample** (position, yaw, stance, speed, timestamp) at `trail_rate` (2 Hz solo; in co-op the 10 Hz replication snapshots serve as samples). The server checks that each new sample, and each capture pose, is within the plausibility distance of the previous accepted sample (F9). A trail failure **does not reject** the photo if R18 passes; it is accepted, flagged `trail_anomaly`, and counted per account for Moderation/telemetry. Repeated anomalies (≥ `anomaly_threshold`, 5 in 10 min) cause the server to send a position correction to the last accepted sample. Respawn, zone travel and session start reset the trail with a server-issued anchor. (D7.)

**R20. Co-op replication (behaviour only).** In expedition rooms (Alpha):
- Each client predicts its own movement locally with no input delay. It sends pose snapshots at `snapshot_rate` (10 Hz) containing position, yaw, pitch, stance, viewfinder state, speed and surface ID.
- The server validates each snapshot with R19 and relays it to the room. The server uses the relayed data to compute each player's presence for server-side subject behaviour (F4 is designed to be computable from snapshot fields plus the baked surface map).
- Remote players are rendered with `interp_delay` (150 ms) of interpolation; when snapshots stop, they extrapolate for at most 250 ms, then hold.
- Players **do not collide** with each other (no body-blocking a shot spot).
- Teammates are **never part of a stored recipe** (they are not re-rendered in the photo). In the live viewfinder, teammates within the frame are drawn ghosted (30% opacity) so the player is not misled into composing around a person who will not appear. (D8, D9.)
- Transport and encoding → Network Transport GDD and an ADR.

**R21. Input map (defaults, all remappable later via Settings & Accessibility).**

| Action | Keyboard/Mouse | Gamepad (partial) | Touch (partial) |
|---|---|---|---|
| Move | WASD | Left stick | `VirtualJoystick` (Dynamic mode), left half of screen (node verified in `input.md` 4.7) |
| Look | Mouse (locked) / arrow keys | Right stick | Drag on right half |
| Hurry | Hold Shift | Hold L3 / LB | Joystick pushed to edge |
| Sneak | C (toggle) | B / East (toggle) | Sneak button |
| Raise/Lower viewfinder | Hold RMB / F toggle | Hold LT | Camera button (toggle) |
| Shutter | LMB / Space | RT | Shutter button (viewfinder only) |
| Interact / traversal | E | A / South | Contextual button |
| Pause | (lock loss) / P | Start | Pause button |

Zoom, focus and exposure bindings belong to Camera Model; the prototype's Q/E and Z/X are reserved for it. No interaction is hover-only (technical preferences).

### States and Transitions

Movement state is a small hierarchical machine: a **locomotion state** and an independent **view state**.

**View states:** `ThirdPerson` → `Raising` → `Viewfinder` → `Lowering` → `ThirdPerson`.

**Locomotion states:**

| State | Entry | Exit | Allowed view states | Notes |
|---|---|---|---|---|
| `Idle` | no move input, on floor | move input → Walk/Sneak | all | presence decays |
| `Walk` | move input, not Hurry/Sneak | release → Idle; Shift → Hurry; C → Sneak | all | |
| `Hurry` | Shift held + move input, view = ThirdPerson | Shift up → Walk; raise → Walk; C → Sneak | ThirdPerson only | raise request while hurrying first drops to Walk, then raises |
| `Sneak` (idle or moving) | C toggle | C again, or Shift (→ Hurry) if headroom | all | stand-up blocked under low ceiling (stays Sneak, auto-stands when clear) |
| `Wading` | feet in water 0.3–0.6 m | leave water | all | modifier on Walk/Sneak; Hurry disabled |
| `Airborne` | not on floor (walked off a drop) | land → previous ground state | ThirdPerson; Viewfinder is force-lowered if airborne > 0.3 s | lands soft; presence event `land` |
| `Traversing` | Interact on a traversal volume, view = ThirdPerson | move complete | ThirdPerson only | input ignored, cannot raise |
| `Respawning` | kill plane, deep water, Unstick | fade complete at safe position | ThirdPerson | all input ignored, `can_shoot` false |
| `Suspended` | pointer lock lost / tab hidden / page blur | lock regained (click) | keeps previous | inputs released, target velocity 0 |

**Transition rules worth stating exactly:**
- Raise is refused in `Traversing` and `Respawning`; in `Airborne` it is queued until landing.
- Entering `Respawning` from `Viewfinder` force-lowers instantly (no lower animation).
- `Suspended` overrides locomotion input but not physics: an airborne player still lands.
- Stance change (Sneak ↔ stand) takes 0.25 s; during it presence uses the **higher** of the two stance bases.

### Interactions with Other Systems

| System | Direction | What flows | Owner of the rule |
|---|---|---|---|
| Camera Model: Viewfinder & Exposure | Movement → Camera | eye anchor transform, look yaw/pitch, view state, `can_shoot`, body speed | Movement owns pose and gate; Camera owns FOV, zoom, focus, exposure, shutter, any handheld shake |
| Camera Model | Camera → Movement | current vertical FOV (for F6 sensitivity scaling) | Camera |
| Photo Recipe & Re-render | Movement → Recipe | capture pose (R15) | Recipe owns schema and versioning; Movement owns field meanings and ranges |
| Subject & Spirit Behaviour | Movement → Subject | presence radius, presence events, player position, stance | Movement computes presence; Subject owns reactions and any line-of-sight test |
| Network Transport & Server Authority | both | pose samples/snapshots up; corrections and trail anchors down; recipe pose validation | Network owns transport, versioning and range validation framework; Movement owns R18/R19 rules |
| Zone Access & Travel (VS) | Zone → Movement | zone ID, spawn points, bounds, eye-volume map; travel teleports reset trail | Zone |
| Expedition Rooms (Alpha) | both | 10 Hz snapshots, remote interpolation, no player collision | Rooms owns room lifecycle; Movement owns snapshot content and remote-player behaviour |
| Shared Hub (Full Vision) | Hub → Movement | larger player counts may lower `snapshot_rate` and interest-manage; Movement rules otherwise unchanged | Hub |
| Capture Encounter | Encounter → Movement | may request a soft movement constraint (e.g. encounter arena bounds); never a lock-out of movement | Encounter |
| Viewfinder HUD | Movement → HUD | view state, stance, raise progress | HUD |
| Audio: SFX & Ambience (VS) | Movement → Audio | footstep events with surface ID, stance and speed; landing; traversal | Audio owns sounds; footstep loudness must track presence (see Visual/Audio) |
| Settings & Accessibility (Alpha) | Settings → Movement | sensitivity, invert Y, hold/toggle, reduced motion, remaps | Settings; MVP uses defaults in data |
| Onboarding & Tutorial (VS) | reads | teaches sneak + presence and the raise/shoot gate | Onboarding |
| Found Photos (VS) | reads | placement positions must lie in the eye volume so finders can reach them | Found Photos |

## Formulas

All values in metres, seconds, degrees unless stated. All constants are data-driven (Tuning Knobs).

### F1. Target speed

The target_speed formula is defined as:

`target_speed = base_speed[mode] × vf_mult[stance] ^ is_vf × wade_mult ^ is_wading × input_mag`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| base_speed[mode] | float m/s | walk 2.0–4.0 (3.0), hurry 4.0–6.5 (5.0), sneak 0.8–2.0 (1.3) | data (tuning) | Ground speed for Walk/Hurry/Sneak |
| vf_mult[stance] | float | 0.2–0.8 (stand 0.40, sneak 0.60) | data | Viewfinder slowdown |
| is_vf | int | 0 or 1 | state | 1 when view state is Raising/Viewfinder/Lowering |
| wade_mult | float | 0.4–0.9 (0.6) | data | Wading slowdown |
| is_wading | int | 0 or 1 | state | 1 when in Wading |
| input_mag | float | 0–1 | input | Normalised move magnitude after dead zone (keyboard = 1) |
| target_speed | float m/s | 0–6.5 | calculated | Speed the body accelerates toward |

**Output Range:** 0 to 6.5 m/s (hurry cap). Hurry with is_vf = 1 cannot occur (R12).
**Example:** sneaking with viewfinder raised, keyboard: 1.3 × 0.60 × 1 × 1 = **0.78 m/s**. Walking in shallow water, half stick: 3.0 × 1 × 0.6 × 0.5 = **0.90 m/s**.

### F2. Horizontal acceleration

The velocity_step formula is defined as:

`v_new = move_toward(v_old, v_target, rate × dt)` where `rate = accel` if `|v_target| > |v_old|` and the angle between them < 90°, else `decel`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| v_old | Vector2 m/s | magnitude 0–6.5 | physics state | Current horizontal velocity |
| v_target | Vector2 m/s | magnitude 0–6.5 | F1 × move direction | Desired horizontal velocity |
| accel | float m/s² | 8–30 (16) | data | Speed-up rate |
| decel | float m/s² | 10–40 (22) | data | Slow-down/reverse rate |
| dt | float s | 1/60 (physics tick) | engine | Physics step |
| v_new | Vector2 m/s | magnitude 0–6.5 | calculated | Next velocity; `move_toward` moves by at most rate×dt and never overshoots |

**Output Range:** magnitude 0 to 6.5 m/s.
**Example:** from rest to Walk: time = 3.0 / 16 = **0.19 s** (11-12 ticks). Walk to stop: 3.0 / 22 = **0.14 s**, travelling 3.0² / (2 × 22) = **0.20 m** of slide.

### F3. Third-person camera follow smoothing

The follow_alpha formula is defined as:

`alpha = 1 − 2 ^ (−dt / half_life)`; `cam_pos_new = lerp(cam_pos_old, boom_target, alpha)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| dt | float s | 0.004–0.1 | engine (render frame) | Frame time |
| half_life | float s | 0.0–0.15 (follow 0.05; collision release 0.20; collision pull-in 0.0 = instant) | data | Time to close half the gap |
| boom_target | Vector3 | — | calculated | Pivot (1.55 m up) + shoulder offset (0.45 m right) − look × arm_length (3.2 m), shortened by boom collision |
| alpha | float | 0–1 | calculated | Lerp weight for this frame, frame-rate independent |

**Output Range:** alpha 0 to 1; half_life = 0 gives alpha = 1 (snap).
**Example:** 60 fps, half_life 0.05: alpha = 1 − 2^(−0.0167/0.05) = 1 − 2^(−0.333) = **0.206**. At 30 fps: 1 − 2^(−0.667) = **0.370**; both reach 50% of the gap in 0.05 s. Rotation is never smoothed (look is raw); only the boom's position follows.

### F4. Presence radius (instantaneous)

The presence_raw formula is defined as:

`presence_raw = min(presence_max, (r_stance + k_speed × h_speed) × surface_mult[surface] + event_bonus)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| r_stance | float m | stand 1.0–3.0 (2.0); sneak 0.2–1.0 (0.5) | data | Baseline presence of a still body by stance |
| k_speed | float m per m/s | 0.5–3.0 (1.5) | data | Extra radius per m/s of horizontal speed |
| h_speed | float m/s | 0–6.5 | physics state (or snapshot) | Actual horizontal speed, not input |
| surface_mult[surface] | float | 0.5–2.0 (grass 0.8, sand 0.9, cobble/stone 1.0, plank 1.3, shallow water 1.5) | data + baked surface map | Footing loudness |
| event_bonus | float m | 0–8 | presence events (land +4.0, traversal end +2.0; other systems add their own) | Sum of active event bonuses; each lasts 0.5 s |
| presence_max | float m | 8–25 (15) | data | Hard cap |
| presence_raw | float m | 0–presence_max | calculated | Instantaneous presence |

**Output Range:** 0.1 (sneak, still, grass: 0.5 × 0.8 = 0.4; lower only with lower data) to presence_max.
**Example:** walking on cobble: (2.0 + 1.5 × 3.0) × 1.0 = **6.5 m**. Hurrying on the pier: (2.0 + 1.5 × 5.0) × 1.3 = **12.35 m**. Sneaking on grass: (0.5 + 1.5 × 1.3) × 0.8 = **1.96 m**. Viewfinder walk on grass: (2.0 + 1.5 × 1.2) × 0.8 = **3.04 m**.

### F5. Presence decay (published value)

> Server evaluation (2026-11-04): the server runs this at `TICK_HZ` (30), so `dt` = 1/30 there; the client's 1/60 is presentation only. The server value is authoritative for Subject & Spirit Behaviour.

The presence formula is defined as:

`presence = presence_raw` if `presence_raw ≥ presence_prev`, else `presence_prev − (presence_prev − presence_raw) × (1 − 2 ^ (−dt / presence_half_life))`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| presence_prev | float m | 0–presence_max | previous tick | Last published presence |
| presence_raw | float m | 0–presence_max | F4 | Instantaneous target |
| presence_half_life | float s | 0.2–2.0 (0.6) | data | How long noise "lingers" after slowing |
| dt | float s | 1/60 | engine | Tick |
| presence | float m | 0–presence_max | calculated | Value published to Subject Behaviour |

**Output Range:** 0 to presence_max. Rises instantly, falls smoothly.
**Example:** hurrying on the pier (12.35) then stopping dead in sneak on plank (raw = 0.5 × 1.3 = 0.65): after 0.6 s presence ≈ 0.65 + (12.35 − 0.65) × 0.5 = **6.5 m**; after 1.2 s ≈ **3.6 m**; after 1.8 s ≈ **2.1 m**. Sprint-and-stop is not a free approach.

### F6. Mouse look delta (FOV-scaled)

The look_delta formula is defined as:

`yaw_delta = −mouse_dx × sens × fov_scale`; `pitch_delta = −mouse_dy × sens × fov_scale × invert_y`; `fov_scale = (vfov_current / vfov_ref) ^ fov_exp` when view = Viewfinder, else 1

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| mouse_dx, mouse_dy | float px (relative motion) | any | input event | Raw relative mouse motion |
| sens | float °/px | 0.02–0.60 (0.12) | Settings (data default) | Base sensitivity |
| vfov_current | float ° | ~3–90 | Camera Model | Current vertical FOV of the lens |
| vfov_ref | float ° | 50–80 (70) | data | Third-person vertical FOV |
| fov_exp | float | 0.0–1.0 (1.0) | Settings (data default) | 1 = fully proportional; 0 = no scaling |
| invert_y | int | +1 or −1 (+1) | Settings | Invert vertical look |
| yaw_delta, pitch_delta | float ° | — | calculated | Applied on the render frame; pitch then clamped (R11) |

**Output Range:** unbounded per event; pitch is clamped after applying.
**Example:** sens 0.12, mouse moves 100 px. Third person: **12°**. Viewfinder at 200 mm on full-frame (vfov = 2·atan(12/200) ≈ 6.87°, Camera Model's number): fov_scale = 6.87/70 = 0.098 → **1.18°**. At 24 mm (vfov ≈ 53.1°): fov_scale 0.759 → **9.1°**.

### F7. Gamepad / keyboard look rate

The stick_look formula is defined as:

`rate = max_look_rate × fov_scale × sign(s) × ((|s| − dz) / (1 − dz)) ^ curve_exp` if `|s| > dz`, else 0

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| s | float | −1 to 1 | input (per axis; arrow keys = ±1) | Stick axis value |
| dz | float | 0.05–0.30 (0.15) | Settings | Dead zone |
| curve_exp | float | 1.0–3.0 (2.0) | data | Response curve; 2 = fine control near centre |
| max_look_rate | float °/s | 90–360 (yaw 180, pitch 120) | Settings | Full-deflection turn rate |
| fov_scale | float | from F6 | F6 | Same FOV scaling in viewfinder |
| rate | float °/s | −360 to 360 | calculated | Multiplied by frame dt |

**Output Range:** −max_look_rate to +max_look_rate (before fov_scale).
**Example:** s = 0.5 yaw, third person: ((0.5 − 0.15)/0.85)² = 0.170 → 180 × 0.170 = **30.5 °/s**. Full deflection at 200 mm: 180 × 0.098 = **17.6 °/s**.

### F8. Server eye-band check (reachability)

The eye_band_ok formula is defined as:

`eye_band_ok = ∃ cell c in walkable(zone): horiz_dist(p_eye, c) ≤ nav_tolerance AND eye_min[stance] ≤ p_eye.y − c.ground_h ≤ eye_max[stance]`

with `eye_min[s] = eye_height[s] − eye_tol`, `eye_max[s] = eye_height[s] + eye_tol`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| p_eye | Vector3 m | inside zone AABB | recipe capture pose | Recorded eye position |
| walkable(zone) | set of cells | baked per zone | baked eye-volume map (Zone/level data) | Walkable cells on a 0.5 m grid with ground height, multiple layers allowed (stairs, pier over sand), each baked with ≥ standing headroom or flagged sneak-only |
| horiz_dist | float m | ≥ 0 | calculated | XZ distance from eye to cell centre |
| nav_tolerance | float m | 0.3–1.0 (0.65 ≈ half-diagonal 0.35 + capsule 0.30) | data | Horizontal slack |
| eye_height[stance] | float m | stand 1.60; sneak 1.05 | data (shared with R10) | Nominal eye height |
| eye_tol | float m | 0.05–0.40 (0.15) | data | Vertical slack (smoothing, step-ups, slope) |
| eye_band_ok | bool | — | calculated | Pass/fail for R18 check 2 |

**Output Range:** boolean. Sneak-only cells pass only with stance = sneak.
**Example:** a standing pose at p_eye = (12.0, 7.55, −3.2) on the cliff path; nearest walkable cell at 0.4 m with ground_h = 5.98 → eye height 1.57 ∈ [1.45, 1.75] → **pass**. Same pose with y = 9.40 (camera hovering 3.4 m up) → **fail**, recipe rejected.

### F9. Server trail plausibility

The trail_max formula is defined as:

`trail_max = v_cap × Δt × (1 + speed_tolerance) + jitter_m`; a sample passes if `horiz_dist(p_new, p_prev) ≤ trail_max`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| v_cap | float m/s | = hurry base_speed (5.0) | data | Fastest legal horizontal speed (traversal moves are slower than this by design) |
| Δt | float s | 0.05–10 | server receive time difference, clamped to ≥ 1/trail_rate | Time since last accepted sample (server clock, not client) |
| speed_tolerance | float | 0.10–0.50 (0.25) | data | Slack for frame timing |
| jitter_m | float m | 0.25–2.0 (0.75) | data | Constant slack for network jitter and smoothing |
| p_new, p_prev | Vector3 m | zone space | samples | New and last accepted positions |
| trail_max | float m | 0.8–65 | calculated | Allowed horizontal distance |

**Output Range:** ~0.8 m (at 10 Hz) up to the clamp at Δt = 10 s (63.25 m); longer gaps require a server re-anchor.
**Example:** 2 Hz solo, Δt = 0.5 s: 5.0 × 0.5 × 1.25 + 0.75 = **3.875 m**. Co-op 10 Hz, Δt = 0.1: 5.0 × 0.1 × 1.25 + 0.75 = **1.375 m**. A sample 9 m from the previous one after 0.5 s fails → `trail_anomaly`.

## Edge Cases

- **If the first click on the page lands on the 3D view**: it requests pointer lock and is consumed; no shutter, interact or raise fires, whether or not the lock is granted.
- **If the player double-clicks to lock and the second click is LMB in the viewfinder**: the second click is ignored because it falls inside `lock_grace_ms` (250 ms) after lock.
- **If pointer lock is lost while in the viewfinder** (Esc, alt-tab, browser popup): the state becomes `Suspended`, held inputs are released, the view stays raised, mouse shutter is disabled, and the "Click to look" overlay appears; the player's next click re-locks and is consumed.
- **If the browser refuses a lock request** (re-request too soon after exiting): the overlay reads "Click again to look"; arrow-key look and WASD continue to work; no error is shown as a failure.
- **If the tab is hidden or the window loses focus**: same as lock loss; additionally the client stops sending pose samples, and on return the first sample is checked with the real server Δt (F9 tolerates the gap up to 10 s, beyond that the server re-anchors without an anomaly).
- **If the player holds Hurry and raises the viewfinder**: Hurry is dropped to Walk first, then the raise starts; releasing the viewfinder while Shift is still held resumes Hurry.
- **If Sneak and Hurry are both pressed**: the most recent press wins; Hurry exits Sneak only if there is standing headroom, else the player stays in Sneak and Hurry is ignored.
- **If the player tries to stand under a low ceiling**: they stay in Sneak, the Sneak icon pulses once, and they auto-stand when headroom returns (toggle mode only).
- **If keyboard diagonal input is pressed (W+D)**: the vector is normalised to magnitude 1; diagonal speed equals straight speed.
- **If stick input is below the dead zone**: input_mag = 0 and the body decelerates per F2.
- **If the player walks off a drop of 1.8 m or less**: they fall, land with a soft-landing animation, add the +4.0 m landing presence event, and take no damage or stun.
- **If physics pushes the player past an edge guard onto a larger drop** (collision gap, bug): they fall with no damage; if they land below the kill plane or in deep water they respawn at the last safe position; otherwise play continues where they land.
- **If the player enters water deeper than 0.6 m**: the push-back volume slides them toward shallow water; if they still end up in deep water (≥ 1.2 m at the capsule centre) for 1.0 s, they respawn.
- **If the player is stuck** (3 s of move input, < 0.1 m displacement): an "Unstick" prompt appears; using it respawns to the last safe position and resets the trail anchor.
- **If no safe position has been recorded yet** (stuck on the first second of a session): respawn uses the zone's spawn point.
- **If the shutter is pressed during the raise animation**: it does nothing (`can_shoot` false) and the press is not buffered.
- **If the shutter is pressed while moving**: the photo is allowed; the capture pose records the actual horizontal speed so Camera Model/Scoring can apply motion effects.
- **If the player becomes airborne with the viewfinder raised for more than 0.3 s**: the viewfinder force-lowers (no shutter while falling).
- **If a step-up happens while in the viewfinder**: the eye anchor rises smoothly over 0.10 s; a photo during that window records the smoothed eye height, which F8's eye_tol covers.
- **If the eye anchor would be inside or within 0.15 m of a wall** (pressing face into a wall): it is pushed back along the look direction; the recipe records the pushed-back position.
- **If the third-person boom collides with geometry**: the boom shortens instantly (no clipping); if it becomes shorter than 0.6 m the player mesh fades to 20% so it does not fill the screen; the minimum boom is 0.4 m.
- **If the player tries to raise the viewfinder during a traversal move**: the request is ignored, not queued.
- **If a respawn or zone travel happens while a capture is in flight to the server**: the capture uses the pose recorded at shutter press; the trail check compares it with the sample before the teleport, and the server re-anchor is applied after it.
- **If a recipe's pose fails the eye-band check (F8)**: the recipe is rejected, no tier roll happens, the client shows "The shot couldn't be developed", and `pose_invalid` is logged with the failing check.
- **If a recipe's pose passes F8 but fails the trail check (F9)**: the photo is accepted and scored, flagged `trail_anomaly`, and counted toward `anomaly_threshold`.
- **If an account reaches `anomaly_threshold` (5 in 10 minutes)**: the server sends a correction that moves the client to the last accepted sample; further anomalies keep being logged; no automatic ban (Moderation decides).
- **If a pose field is non-finite (NaN/Inf) or pitch exceeds ±85°**: the message is rejected by sanity check 1 and logged; no state changes.
- **If two players stand in the same spot (co-op)**: they overlap without collision; each sees the other ghosted at 30% inside 0.8 m in third-person and ghosted at 30% anywhere in the viewfinder frame.
- **If a remote player's snapshots stop arriving**: they extrapolate for up to 250 ms, then hold their last pose; after 5 s they show a "connection" icon (Expedition Rooms owns disconnect).
- **If keyboard and gamepad look are used at once**: their deltas are summed; the input prompts follow the most recently used device.
- **If sensitivity is set to the minimum and FOV is at 200 mm**: 0.02 × 0.098 = 0.002 °/px, still non-zero; turning 180° takes ~92,000 px, which is why arrow-key/stick look also scales but retains max_look_rate, and why `fov_exp` is user-adjustable.
- **Degenerate: sprint up, then sneak at the last second.** Mitigated by F5 decay: presence lingers ~1.8 s to fall from hurry to sneak levels, so the last 10 m must be approached slowly.
- **Degenerate: jitter-strafing to fake low speed.** Presence uses actual horizontal velocity, not input, so jitter is measured as speed.
- **Degenerate: clipping the camera through a wall or onto a roof to shoot from an impossible spot.** The server eye-band check rejects any eye not above reachable ground at eye height; physics exploits gain nothing.
- **Degenerate: camping one perfect spot.** Movement allows it; repeat-subject diminishing returns are owned by Photo Pricing and score gaming by Photo Scoring.

## Dependencies

**Upstream (this system needs):**

| System | Type | Interface | Status |
|---|---|---|---|
| Network Transport & Server Authority | Interface (MVP) | pose sample message, correction/anchor message, recipe pose validation hook, field ranges from this doc | Not designed — R18/R19 are inputs to its message schema |
| Zone/level data (not an indexed system; level-designer output; later Zone Access & Travel) | Data | collision, traversal volumes, edge guards, water volumes, kill plane, spawn, bounds, **baked eye-volume map with surface IDs** | Not designed |
| Settings & Accessibility | Soft (Alpha) | sensitivity, invert, hold/toggle, remaps, reduced motion; MVP reads data defaults | Not designed |
| Camera Model | Soft, read-only | current vertical FOV for F6/F7 | Not designed (Camera depends on Movement for everything else, so this is a value read, not a design dependency) |

**Downstream (depend on this system):**

| System | What it needs from here | Hard/Soft |
|---|---|---|
| Camera Model: Viewfinder & Exposure | eye anchor, look, view state, `can_shoot`, body speed | Hard |
| Photo Recipe & Re-render | capture pose fields and ranges (R15) | Hard |
| Subject & Spirit Behaviour | presence radius and events, position, stance | Hard (not yet listed in systems-index row 7) |
| Zone Access & Travel | respawn/teleport behaviour, trail re-anchor on travel | Hard |
| Expedition Rooms | snapshot content, interpolation, no-collision rule | Hard |
| Shared Hub | same as Expedition Rooms at higher counts | Soft |
| Capture Encounter | arena soft bounds, presence | Soft |
| Viewfinder HUD | view state, raise progress, stance | Soft |
| Audio: SFX & Ambience | footstep/landing events | Soft |
| Onboarding & Tutorial | teaching moments (sneak, raise, pointer lock) | Soft |
| Found Photos | placement must be in the eye volume | Soft |

**Bidirectionality follow-ups (not edited here; this run may write only this file):** systems-index row 7 (Subject & Spirit Behaviour) and row 9 (Photo Recipe) should list Player Movement & Exploration as a dependency; rows 3 and 22 should note the pose-validation contract. Each of those GDDs must reference this one when authored.

## Tuning Knobs

All in data (e.g. `assets/data/movement/movement.json`; path → gameplay-programmer). Categories: **Feel** (playtest), **Curve** (math), **Gate** (pacing/security).

| Knob | Default | Safe range | Category | Affects | Rationale |
|---|---|---|---|---|---|
| walk_speed | 3.0 m/s | 2.0–4.0 | Feel | traversal time of the small area | ~2x real walking so a 150 m village crosses in ~50 s; slower feels sluggish on a small map |
| hurry_speed | 5.0 m/s | 4.0–6.5 | Feel | backtracking time; also v_cap for F9 | brisk jog, not a sprint; above 6.5 feels like an action game and widens F9 slack |
| sneak_speed | 1.3 m/s | 0.8–2.0 | Feel | approach pacing | close to real walking pace; below 0.8 feels like waiting |
| vf_mult_stand / vf_mult_sneak | 0.40 / 0.60 | 0.2–0.8 | Feel | reframing by walking | enough to reposition a step, too slow to roam in the viewfinder |
| wade_mult | 0.6 | 0.4–0.9 | Feel | shoreline shots | |
| accel / decel | 16 / 22 m/s² | 8–30 / 10–40 | Feel | responsiveness | 0.19 s start, 0.14 s stop (Game Feel targets) |
| turn_rate | 720 °/s | 360–1440 | Feel | body facing | half a second for a full turn reads natural |
| step_height | 0.35 m | 0.2–0.5 | Feel | stairs/kerbs | must exceed the tallest authored stair riser |
| floor_max_angle | 40° | 30–50 | Feel | which slopes walk | |
| safe_drop_height | 1.8 m | 1.0–3.0 | Gate | where edge guards go | anything taller gets a guard |
| wade_depth | 0.6 m | 0.3–1.0 | Gate | water reach | |
| eye_height_stand / sneak | 1.60 / 1.05 m | 1.4–1.75 / 0.7–1.2 | Curve | photo perspective, F8 | real eye heights; sneak gives a meaningful low angle |
| eye_smooth_time | 0.10 s | 0.0–0.2 | Feel | viewfinder stability on steps | |
| raise_time / lower_time | 0.22 / 0.18 s | 0.10–0.40 | Feel | shot readiness | under 0.25 keeps "seeing" fluid |
| arm_length / shoulder_offset / pivot_height | 3.2 / 0.45 / 1.55 m | 2.0–5.0 / 0–0.8 / 1.2–1.8 | Feel | third-person framing | sky visible above the character |
| follow_half_life / collision_release_half_life | 0.05 / 0.20 s | 0–0.15 / 0.05–0.5 | Feel | camera smoothness | |
| vfov_ref | 70° | 50–80 | Curve | F6 baseline | |
| sens (default) | 0.12 °/px | 0.02–0.60 | Feel (player setting) | aim | common FPS default range |
| fov_exp | 1.0 | 0–1 | Feel (player setting) | telephoto aim | |
| max_look_rate yaw/pitch | 180 / 120 °/s | 90–360 | Feel (player setting) | stick/arrow look | |
| stick_dead_zone / curve_exp | 0.15 / 2.0 | 0.05–0.30 / 1–3 | Feel | stick precision | |
| r_stance stand / sneak | 2.0 / 0.5 m | 1.0–3.0 / 0.2–1.0 | Curve | approach difficulty | co-tune with Subject thresholds |
| k_speed | 1.5 m per m/s | 0.5–3.0 | Curve | how much speed matters | |
| surface_mult table | grass 0.8, sand 0.9, stone 1.0, plank 1.3, water 1.5 | 0.5–2.0 | Curve | footing choice | spread ≥ 0.5 between quietest and loudest so the choice is noticeable |
| presence_max | 15 m | 8–25 | Curve | ceiling | |
| presence_half_life | 0.6 s | 0.2–2.0 | Curve | sprint-stop exploit | |
| land_event / traversal_event | +4.0 / +2.0 m, 0.5 s | 0–8 | Curve | | |
| lock_grace_ms | 250 ms | 100–500 | Gate | accidental shots | |
| safe_sample_interval | 1.0 s | 0.5–3.0 | Gate | respawn distance | |
| unstick_delay | 3.0 s | 2–10 | Gate | | |
| trail_rate (solo) | 2 Hz | 1–5 | Gate | server bandwidth vs check precision | |
| snapshot_rate (co-op) | 10 Hz | 5–20 | Gate | remote smoothness vs bandwidth | |
| interp_delay | 150 ms | 100–250 | Feel | remote smoothness vs lag | 1.5 snapshot intervals |
| nav_tolerance | 0.65 m | 0.3–1.0 | Gate (security) | false rejects vs exploit room | |
| eye_tol | 0.15 m | 0.05–0.40 | Gate (security) | | |
| speed_tolerance / jitter_m | 0.25 / 0.75 m | 0.1–0.5 / 0.25–2.0 | Gate (security) | false anomalies | |
| anomaly_threshold | 5 per 10 min | 3–20 | Gate (security) | correction trigger | |
| teammate_ghost_opacity | 0.30 | 0.0–0.6 | Feel | co-op viewfinder clarity | |

## Visual/Audio Requirements

**Animation (CC0 rigged human, art bible A5 and 5.1):** idle, walk, hurry (light jog), sneak idle, sneak walk, stand↔sneak transition (0.25 s), raise camera to eye / hold phone up (0.22 s), viewfinder idle (subtle breathing only on the body, never on the eye anchor), lower and glance at back screen (0.18 s), soft landing, ladder climb loop, scramble/vault (0.8 s), wade walk. No aggressive or heroic poses. Animation must follow velocity (no foot skating above 0.3 m/s mismatch) and never drive root motion (movement is code-driven).

**Readability:** stance must read at 20 m in third-person (sneak silhouette visibly lower), and teammates' raised-viewfinder pose must read at 30 m so a crew sees "they've found something". The camera remains the brightest detail on the figure (art bible 3.3).

**Audio (Audio system owns assets; this system owns events):**
- Footstep events per foot plant carry surface ID, stance and speed. **Footstep loudness must be monotonic with presence**: plank louder than grass, hurry louder than sneak. This is the main readable feedback for F4 and is required for Pillar 1 competence (the player hears why the spirit noticed them).
- Landing thump scaled to drop height; ladder rungs; wading splashes.
- Viewfinder raise: a soft cloth/strap rustle and a quiet ambient duck (−3 dB) in the lens view, matching "held breath" (art bible 2.1).
- Accessibility: every presence-relevant sound has a visual equivalent (the presence indicator, UI Requirements).

## Game Feel

**Input latency targets:**
- Mouse/stick look is applied in the **same render frame** the input is read (`_process`, not the 60 Hz physics tick), so look latency inside the game is ≤ 1 frame (16.6 ms at 60 fps). Look must not be quantised to physics ticks or delayed by physics interpolation (physics interpolation moved to SceneTree in 4.5 per `physics.md`; its effect on the camera node is UNVERIFIED and must be checked).
- Move input to visible body motion: ≤ 2 frames (33 ms).
- Total motion-to-photon on the Web target: ≤ 66 ms at 60 fps on a mid laptop in Chromium (browser compositing adds frames; UNVERIFIED, measure with a high-speed capture).
- Raise-to-shutter-ready: 0.22 s; there is no input buffering of the shutter during the raise.

**Acceleration feel:** quick and grounded, not slippery. Walk reached in ~0.19 s, stop in ~0.14 s with ~0.20 m slide (F2). Direction changes use decel, so reversing feels crisp. No momentum on slopes. Hurry ramps in ~0.31 s, giving it a slight "lean in".

**Camera smoothing:**
- Third-person boom **position** follows with a 0.05 s half-life (F3) for softness over steps; boom collision pulls in instantly and releases with 0.20 s.
- **Rotation is never smoothed for mouse** in either mode; smoothing adds latency and ruins small framing corrections. Gamepad uses the response curve (F7) instead of smoothing.
- Viewfinder: no head bob, no camera sway from this system. Handheld shake/stabilisation, if any, belongs to Camera Model and must be deterministic from recipe data.
- Third-person: no head bob, no camera shake, ever (art bible: "No screen shake"). Reduced-motion setting sets follow_half_life to 0 and disables the raise blend (cut instead).

**Feel playtest checks:** "Can you put the lighthouse exactly on the left third at 200 mm in under 5 s?"; "Did stopping ever feel like ice?"; "Did you ever lose a shot to the controls rather than the subject?"

## UI Requirements

- **"Click to look" overlay** (Web, mouse): centred, shown at start and on any pointer-lock loss; doubles as the pause overlay entry. Text: "Click to look" / "Click again to look" when a lock was refused.
- **Stance icon** in the exploration HUD's device corner (art bible 7.1 "minimal"): standing or sneaking; pulses when stand-up is blocked.
- **Presence indicator** (proposed, D10): a small footprint/ripple glyph next to the stance icon with three states (quiet/noticed/too close) derived from the intrusion and alarm values owned by Subject Behaviour. Not a number. Shown whenever a subject is within its own reach (up to 30 m) and otherwise hidden, to keep the HUD clear.
- **Traversal prompts:** contextual "E Climb", "E Vault" at the volume; glyph follows the last used device; never hover-only.
- **Unstick prompt** after 3 s stuck; "Unstick" also in the pause menu.
- **Respawn feedback:** 0.4 s fade; no failure text.
- **Pose rejection message:** "The shot couldn't be developed" in the darkroom flow (owned by Darkroom UI; trigger from R18).
- **Settings (Alpha, Settings & Accessibility):** mouse sensitivity, telephoto sensitivity scaling (fov_exp), invert Y, stick sensitivity and dead zone, hold/toggle for raise and sneak, reduced motion. UX check needed for all labels.
- **Touch (partial):** virtual joystick left, drag-look right, buttons for Sneak, Camera, Shutter (viewfinder only) and Interact; no hover states.
- Teammate markers are UI-only and never in photos (art bible 2.1, P4).

## Cross-References

- `design/gdd/game-concept.md` — Pillars, Core loop (Explore → Capture), Online play / Co-op crews, Technical considerations (photo as recipe, server authority).
- `design/gdd/systems-index.md` — row 4 rationale "supplies the camera position that the recipe records"; dependents rows 8, 22, 29, 44.
- `design/gdd/rarity-tier-ladder.md` — no tier logic in this system; listed only to confirm none is needed.
- `design/art/art-bible.md` — A4 (coastal village), A6 (third-person explore, first-person viewfinder), 2.1 (state moods, co-op markers), 3.3 and 5.1 (player poses), 6.1 (vistas, leading lines), 7.1 (minimal exploration HUD).
- `.claude/docs/technical-preferences.md` — Input & Platform (Web, KB/M primary, gamepad and touch partial, no hover-only), Performance Budgets (60 fps, 16.6 ms).
- `prototypes/aperture-concept/README.md` — keyboard aim; mouse-click shooting removed because the first focusing click took a photo (R13).
- `docs/engine-reference/godot/modules/physics.md` — Jolt default (4.6), `CharacterBody3D` / `move_and_slide()` / `get_gravity()` pattern, 4.5 physics interpolation change.
- `docs/engine-reference/godot/modules/input.md` — `Input.get_vector`, 4.7 `VirtualJoystick`, 4.7 device IDs (identify mouse/keyboard events by type), 4.6 dual focus (pause overlay buttons).
- **UNVERIFIED engine claims** (not in the reference): `MOUSE_MODE_CAPTURED` ↔ Web Pointer Lock mapping; browser lock re-request rate limits; whether Esc reaches the page while locked; built-in step-up support; `SpringArm3D` behaviour on Jolt; camera behaviour under 4.5+ physics interpolation.
- Future: Network Transport GDD (message schema), Photo Recipe GDD (pose fields), Subject & Spirit Behaviour GDD (presence thresholds), ADR "Movement replication and server pose validation".

## Acceptance Criteria

Tags: **[Logic]** automated gdUnit4 unit test (suggested name) · **[Integration]** integration test or documented playtest · **[UI]** retained screenshot in `production/qa/evidence/`. *(provisional)* = depends on an undesigned system.

**A. Locomotion (R3-R6, F1, F2)**

1. [Logic] **GIVEN** walk 3.0, vf_mult_sneak 0.60, keyboard input, **WHEN** target speed is computed for Sneak with viewfinder raised, **THEN** it is 0.78 m/s ± 0.001. `test_target_speed_sneak_viewfinder_returns_0_78`
2. [Logic] **GIVEN** W and D pressed together, **WHEN** the move vector is built, **THEN** its magnitude is 1.0 ± 0.001. `test_diagonal_keyboard_input_is_normalised`
3. [Logic] **GIVEN** v = 0 and target Walk 3.0 with accel 16 at dt 1/60, **WHEN** steps run until v ≥ 3.0, **THEN** it takes 12 steps (0.19-0.20 s) and never overshoots 3.0. `test_accel_from_rest_reaches_walk_in_12_ticks`
4. [Logic] **GIVEN** v = 3.0 and target 0 with decel 22, **WHEN** steps run, **THEN** v reaches 0 within 9 ticks and distance travelled ≤ 0.21 m. `test_decel_walk_to_stop_within_0_21m`
5. [Logic] **GIVEN** state Viewfinder and Hurry held, **WHEN** target speed is computed, **THEN** Hurry is ignored and speed equals walk × 0.40. `test_hurry_ignored_in_viewfinder`
6. [Logic] **GIVEN** state Sneak with no standing headroom, **WHEN** Hurry is pressed, **THEN** state stays Sneak. `test_hurry_blocked_under_low_ceiling_stays_sneak`

**B. Traversal and safety (R7, R8, R16, R17)**

7. [Integration] **GIVEN** a 0.30 m kerb and a 0.40 m ledge, **WHEN** the player walks into each, **THEN** the kerb is climbed without input change and the ledge blocks.
8. [Integration] **GIVEN** a 1.8 m drop and a cliff edge with a guard, **WHEN** the player walks off each, **THEN** the first lands with no damage, stun or health change (no health exists) and the second stops the player at the lip.
9. [Integration] **GIVEN** the player in 1.2 m deep water for 1.0 s, **WHEN** the timer elapses, **THEN** they respawn at the last safe position with a 0.4 s fade and the server receives a trail re-anchor.
10. [Logic] **GIVEN** 3.0 s of move input with < 0.1 m displacement, **WHEN** the stuck detector updates, **THEN** `unstick_available` becomes true. `test_stuck_detector_after_3s_offers_unstick`
11. [Integration] **GIVEN** a ladder traversal volume, **WHEN** the player presses Interact and then the raise button mid-climb, **THEN** the climb completes and the viewfinder does not raise.

**C. View and look (R10-R13, F3, F6, F7)**

12. [Logic] **GIVEN** sens 0.12, vfov 6.87, vfov_ref 70, fov_exp 1, **WHEN** a 100 px mouse delta is applied in Viewfinder, **THEN** yaw changes by 1.18° ± 0.01. `test_mouse_look_fov_scaled_200mm_returns_1_18deg`
13. [Logic] **GIVEN** pitch 84° in Viewfinder, **WHEN** +10° pitch is applied, **THEN** pitch is 85°. `test_pitch_clamped_at_85_in_viewfinder`
14. [Logic] **GIVEN** stick 0.5, dz 0.15, curve 2, max 180, **WHEN** look rate is computed in third person, **THEN** it is 30.5 °/s ± 0.2; and at stick 0.10 it is 0. `test_stick_look_curve_and_deadzone`
15. [Logic] **GIVEN** half_life 0.05, **WHEN** alpha is computed at dt 1/60 and 1/30, **THEN** alpha is 0.206 and 0.370 (± 0.002). `test_follow_alpha_is_framerate_independent`
16. [Logic] **GIVEN** state Raising at 0.10 s of 0.22 s, **WHEN** `can_shoot` is read, **THEN** it is false; at 0.22 s it is true. `test_can_shoot_false_until_raise_complete`
17. [Integration] **GIVEN** a Web export in Chromium with the page unfocused, **WHEN** the user clicks the 3D view while the viewfinder would otherwise be ready, **THEN** pointer lock engages and zero photos are taken (verify shot counter unchanged over 10 trials).
18. [Integration] **GIVEN** pointer lock active in the viewfinder, **WHEN** the user presses Esc, **THEN** the overlay appears, held inputs release, velocity decays to 0, and LMB does nothing until the next (consumed) click re-locks.
19. [UI] **GIVEN** a fresh page load, **WHEN** the game first renders, **THEN** the "Click to look" overlay is visible; screenshot retained.

**D. Presence (R9, F4, F5)**

20. [Logic] **GIVEN** Walk at 3.0 m/s on cobble, **WHEN** presence_raw is computed, **THEN** it is 6.5 m; Hurry 5.0 on plank gives 12.35 m; Sneak 1.3 on grass gives 1.96 m. `test_presence_raw_reference_cases`
21. [Logic] **GIVEN** presence 12.35 and raw dropping to 0.65 with half_life 0.6, **WHEN** 0.6 s of ticks elapse, **THEN** presence is 6.5 ± 0.1, and it never rises above 12.35 during decay. `test_presence_decay_half_life_0_6s`
22. [Logic] **GIVEN** a landing event (+4.0) on top of raw 14.0, **WHEN** presence is computed, **THEN** it is capped at 15.0. `test_presence_capped_at_max`
23. [Integration] *(provisional: Subject & Spirit Behaviour)* **GIVEN** a shy test subject with a 4 m notice threshold, **WHEN** a playtester approaches walking on planks versus sneaking on grass, **THEN** the subject reacts in the first case and not in the second in ≥ 9 of 10 trials.

**E. Capture pose and server validation (R15, R18, R19, F8, F9)**

24. [Logic] **GIVEN** the shutter fires while moving at 1.1 m/s in Sneak on grass, **WHEN** the capture pose is written, **THEN** it contains eye position, yaw, pitch, stance "sneak", speed 1.1, surface "grass" and a timestamp, and no field is missing. `test_capture_pose_contains_all_fields`
25. [Logic] **GIVEN** a walkable cell with ground_h 5.98 at 0.4 m, **WHEN** a standing pose with y 7.55 is checked, **THEN** eye_band_ok is true; with y 9.40 it is false. `test_eye_band_check_pass_and_fail`
26. [Logic] **GIVEN** a sneak-only cell, **WHEN** a standing pose above it is checked, **THEN** it fails; a sneak pose at 1.05 m passes. `test_eye_band_sneak_only_cell_rejects_standing`
27. [Logic] **GIVEN** v_cap 5.0, tolerance 0.25, jitter 0.75, Δt 0.5, **WHEN** trail_max is computed, **THEN** it is 3.875 m; a 9 m step is flagged anomaly. `test_trail_max_2hz_returns_3_875`
28. [Logic] **GIVEN** pitch NaN or pitch 95°, **WHEN** the server sanity check runs, **THEN** the message is rejected. `test_pose_sanity_rejects_nan_and_out_of_range_pitch`
29. [Integration] *(provisional: Network Transport, Photo Recipe)* **GIVEN** a client that submits a recipe with its eye 3 m above the roof of a house, **WHEN** the server processes it, **THEN** no score or tier roll is produced, the client shows "The shot couldn't be developed", and one `pose_invalid` log entry names check 2.
30. [Integration] *(provisional)* **GIVEN** a recipe that passes F8 but follows a 9 m jump in 0.5 s, **WHEN** processed, **THEN** it is scored and saved, flagged `trail_anomaly`, and the account anomaly count increases by 1.

**F. Co-op (R20) — Alpha, all provisional on Expedition Rooms**

31. [Integration] **GIVEN** two clients in a room with 100 ms simulated latency and 5% loss, **WHEN** one walks a figure-eight, **THEN** the other renders it without visible teleports > 0.5 m over 60 s.
32. [Integration] **GIVEN** two players at the same position, **WHEN** both move, **THEN** neither is blocked by the other.
33. [Integration] **GIVEN** a teammate inside the viewfinder frame, **WHEN** a photo is taken and re-rendered from its recipe, **THEN** the teammate appears ghosted in the live view and is absent from the re-rendered photo.

**G. Performance and feel**

34. [Integration] **GIVEN** the Web export on the reference laptop, **WHEN** movement, camera and presence run in the village with one player, **THEN** this system's per-frame CPU cost is ≤ 0.5 ms (of the 16.6 ms budget) measured over 60 s.
35. [Integration] **GIVEN** a high-speed capture of the Web build, **WHEN** the mouse moves, **THEN** first visible camera rotation is ≤ 66 ms after the motion (median of 20 trials).
36. [Integration] (playtest) **GIVEN** 5 first-time players, **WHEN** asked to frame the lighthouse on the left third at 200 mm, **THEN** ≥ 4 do it in under 5 s and none reports the aim as "twitchy" or "laggy".

37. [Integration] **GIVEN** any lawful standing or sneaking eye pose in the village, **WHEN** the client allows the shutter (`can_shoot` true) and the recipe is submitted, **THEN** the server never rejects it on R18. Any R18 rejection of a shot the client allowed is logged as an eye-volume bake defect, and the player sees an explained "position not valid" draft instead of a silently missing photo.
38. [Integration] (playtest) **GIVEN** 5 players exploring freely for 15 minutes, **WHEN** stance telemetry is collected, **THEN** Hurry accounts for at most 50% of moving time (initial threshold, tune after playtest); above it, revisit unlimited Hurry (Open Question 8).

## Open Questions

1. **Deliberate camera roll (Dutch tilt):** is it a Camera Model feature? If yes, R18 sanity check 1 must read Camera Model's roll limit. Owner: Camera Model GDD.
2. **Low angles below sneak (prone/ground-level) and high angles (stand on a bench):** is a third eye height worth a stance, or covered by authored perches? Owner: game-designer + level-designer, after prototype.
3. **Who simulates subject behaviour in MVP solo play** (client or server)? It decides whether solo pose samples need 2 Hz or more. Owner: Subject & Spirit Behaviour + Network Transport.
4. **Phone vs camera movement differences:** should holding a phone up be faster to raise (e.g. 0.15 s) than a camera? Owner: Starting Choice / Camera Model.
5. **Astro role "needs protecting while the shutter is open"** (concept, co-op): what does "protect" mean without violence — shielding light, keeping others' presence low? May need presence to be per-player-pair. Owner: Co-op Crew Roles.
6. **Eye-volume map baking pipeline:** who bakes it, from which collision layers, and how often it must be rebuilt. Owner: technical-director (ADR).
7. **Reference hardware** for criteria 34-35 is not defined. Owner: technical-director / producer.
8. **Does hurry need any limit** if testing shows players hurry everywhere and never notice the world? Owner: playtest.

**Guardrail (CD-GDD-ALIGN, 2026-11-03):** any future crew role that "protects" (e.g. Astro, Open Question 5) acts only through presence and light, never through physical blocking or body-blocking; player-player collision stays off (R20).

## Decisions to confirm

> **DECIDED 2026-11-03 (user):** all decisions D1–D15 = the recommended option (a).

Every item below was decided on the user's behalf in this draft.

**D1. Camera perspective**
- (a) Third-person exploring, first-person viewfinder for shooting (Recommended; matches art bible A6, shows the sky and light while walking, makes the recipe pose an eye pose).
- (b) First-person throughout: simpler, more immersive, but loses the character, gear-as-hero visibility and co-op readability.
- (c) Third-person shooting allowed too: friendlier, but the recipe camera floats behind the player and server validation gets looser.

**D2. Speeds and stamina**
- (a) Walk 3.0 / Hurry 5.0 / Sneak 1.3 m/s, no stamina; hurry's cost is presence (Recommended; calm, no resource bar, cost tied to the shy-subject fantasy).
- (b) Walk and Sneak only, no Hurry: purest calm, but backtracking a growing map gets tedious.
- (c) Hurry with stamina: adds a resource with no thematic reason in a non-violent game.

**D3. Jumping**
- (a) No jump; automatic step-up of 0.35 m plus authored ladders/scrambles/vaults (Recommended; no platforming skill, fewer out-of-bounds exploits, Space is free for the shutter).
- (b) Small jump (~0.6 m): more freedom, more exploits and more edge-guard work.
- (c) Free climbing on any surface: big scope and a validation headache.

**D4. Falls and edges**
- (a) Drops up to 1.8 m allowed with no damage; taller edges get guards; respawn only for deep water/kill plane (Recommended; no fall-damage drama, as requested).
- (b) All edges guarded: safest, but makes the world feel railed.
- (c) Unguarded edges with respawn on any big fall: freer but punishes curiosity on cliffs.

**D5. Who owns noise/approach toward shy subjects**
- (a) Movement computes and publishes a presence radius (stance, speed, surface, events, decay); Subject Behaviour owns all reactions (Recommended; one clear number, computable server-side from snapshots).
- (b) Subject Behaviour owns everything and reads raw speed/stance: fewer contracts, but footing and decay rules would be duplicated or lost.
- (c) No approach mechanic: subjects ignore the player; loses Pillar 3's tension.

**D6. Web pointer-lock behaviour**
- (a) Start in cursor mode with "Click to look"; the locking click is always consumed; 250 ms shutter grace after lock; lock loss = pause overlay; arrow keys always look as a fallback; no Ctrl bindings (Recommended; directly fixes the prototype's first-click photo).
- (b) No pointer lock: drag-to-look with RMB held. Avoids lock issues but conflicts with RMB raise and feels worse for precise framing.
- (c) Keyboard-only aim, as in the prototype: zero browser issues, but too slow for 3D exploration.

**D7. What the server validates about camera position**
- (a) Hard reject on a baked eye-volume check (eye at legal height above reachable ground, inside zone) plus a soft, flag-only trail-speed check (Recommended; stops impossible-position photos without false rejects from lag).
- (b) Eye-volume check only, no trail: simplest, but teleport hacks to legal spots go unseen.
- (c) Full server-side movement simulation: strongest, but costly and unnecessary while the server owns the things that matter (scores, rolls, inventory).

**D8. Co-op position replication (behaviour)**
- (a) Client-predicted own movement, 10 Hz snapshots, server sanity-checked and relayed, 150 ms remote interpolation, 250 ms extrapolation cap (Recommended; responsive, cheap, enough for a non-competitive walk).
- (b) Server-authoritative movement with client prediction and reconciliation: more secure, much more work, and corrections would feel bad in the viewfinder.
- (c) 5 Hz snapshots: half the bandwidth, visibly floatier teammates.

**D9. Teammates in photos and collision**
- (a) No player-player collision; teammates never in recipes; ghosted at 30% in the live viewfinder (Recommended; no spot-blocking griefing, what you see matches the photo).
- (b) Teammates fully visible in the viewfinder but absent from the photo: simple, but misleading framing.
- (c) Teammates can appear in photos: social and fun, but makes recipes include other players' poses and complicates scoring and ownership.

**D10. Presence feedback in the HUD**
- (a) Audio feedback (footstep loudness) plus a small three-state presence glyph shown only near subjects (Recommended; readable competence feedback, accessible without sound).
- (b) Audio only: cleaner HUD, fails players without sound.
- (c) Exact presence ring drawn on the ground: very readable, but turns sneaking into a numbers game and clutters the world.

**D11. Viewfinder movement**
- (a) Can walk slowly while raised (Walk × 0.40, Sneak × 0.60), no hurry, shooting while moving is allowed with speed recorded (Recommended; lets the player reframe a step without lowering).
- (b) Viewfinder locks movement: simplest, but every step means lower/raise.
- (c) Full speed in viewfinder: makes exploring in first person dominant over third person.

**D12. Look sensitivity in the viewfinder**
- (a) Scale with FOV (fully proportional by default, user-adjustable exponent), raw mouse with no smoothing (Recommended; telephoto framing stays precise).
- (b) Constant sensitivity: telephoto becomes unusably twitchy.
- (c) Fixed slow-down factor (e.g. 0.5 in viewfinder): simple, but wrong at both 24 mm and 200 mm.

**D13. Raise and sneak input style**
- (a) RMB hold / F toggle for raise; C toggle for sneak; all hold/toggle switchable in settings (Recommended; RMB-hold is the standard "aim" gesture, toggles help accessibility).
- (b) Raise toggle only: fewer modes, less natural for mouse players.
- (c) Sneak on hold (Ctrl): Ctrl risks browser shortcuts (Ctrl+W closes the tab).

**D14. Out-of-bounds and stuck handling**
- (a) Soft push-back boundaries, deep-water push-back, last-safe-position respawn with 0.4 s fade, "Unstick" after 3 s (Recommended; never punishing, never lost).
- (b) Hard invisible walls at boundaries only: simple, but no recovery for physics bugs.

**D15. Server trail sample rate in solo MVP**
- (a) 2 Hz pose samples (Recommended; cheap, enough for the F9 check).
- (b) Only at capture time (no trail): least traffic, no plausibility check at all.
- (c) 10 Hz, same as co-op: one code path, 5x the traffic for solo players.
