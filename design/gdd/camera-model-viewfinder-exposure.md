# Camera Model: Viewfinder & Exposure

> **Status**: Designed 2026-11-05 (pending `/design-review` in a fresh session)
> **Author**: user + agents (game-designer)
> **Last Updated**: 2026-11-05
> **Last Verified**: 2026-11-04
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-05 — CONCERNS fixed: low-frames cue and empty-press response, shutter wording, manual-control claim, phone assist recorded as an exception, stale text. NOT ASSESSED: MDA target; Pillar 1 in practice (needs Photo Scoring and a human playtest); spoofed settings (Open Question 3).
> **Implements Pillar**: Pillar 1 "Seeing is the skill" (reading light, choosing focus and timing the shutter are the player's skills; gear widens what is possible and never replaces them); supports Pillar 2 "Every photo matters" (a shot records exactly what the camera did, and a frame allowance makes each press a choice) and Pillar 3 "Play together without violence" (the only pressure is fleeting light and shy subjects; a shutter sound can make a shy subject wary, never harm)

## Summary

Camera Model is the in-game camera: everything between raising the device and pressing the shutter. It turns the equipped gear into a working viewfinder with zoom, focus (automatic and manual), aperture, shutter speed, ISO, exposure metering and compensation, automatic programs and the phone's modes. It defines the settings a shot records, the rules for camera shake, motion blur and noise, the frame allowance and burst, and the live preview. Every exposure and focus result is a pure integer function of recorded settings, gear specs and server world and subject state, so the headless server computes them without rendering. A new player needs no manual control at all. It owns neither scoring nor the recipe format.

> **Quick reference** — Layer: `Core` · Priority: `MVP` · Key deps: `Player Movement & Exploration` (eye anchor, look, `can_shoot`), `Gear Catalog & Specs` (specs, F1–F6, F8, F10), `World Time, Weather & Light` (`scene_ev_deci`, key light, condition), `Network Transport & Server Authority` (`SHUTTER`, `capture_tick`, rate limit), `Subject & Spirit Behaviour` (subject positions, lens-only rule) · Engine: Godot 4.7.2, Web/Compatibility; rendering claims absent from `docs/engine-reference/godot/` are marked UNVERIFIED

## Overview

This system answers four questions for the rest of the game.

1. **What does the camera see?** It converts the equipped lens, zoom position and sensor into a field of view (Gear F3), and it switches on the **lens world**, the only place spirits and memories are drawn (Subject Rule 14).
2. **How is the shot set?** Three body programs (`AUTO`, `APERTURE`, `MANUAL`) and the phone's always-on auto exposure decide aperture, shutter speed and ISO. Focus comes from continuous autofocus, a held focus lock or a manual ring.
3. **What did the shot come out like?** The server computes the exposure error, noise level, shake, subject motion blur and defocus from integers. These are facts about the shot, not a judgement of it. Photo Scoring decides what they are worth.
4. **What may be pressed, and how often?** The shutter works only when Movement's `can_shoot` is true, the device is ready, the network session is live and a frame is available. The frame allowance and the burst rate limit how many shots a player can spend on one moment.

The system is split into a **client half**, which is everything the player touches and must never wait for the network (Network Game Feel: 1 frame or less), and a **server half**, a set of pure functions called `evaluate_shot`. Exposure and focus are designed so that the two halves share one integer library, and the client's preview uses the same numbers the server will compute.

Solo play runs in a 1-player server session, so this path is identical solo and in a crew. There is no offline shutter (Network Rule 5). Results are revealed only after the database commit (Network Rule 29); this system never shows a score, a tier or an evaluation.

**Not owned here:** what any result is worth (Photo Scoring); the recipe schema and re-render pipeline (Photo Recipe & Re-render); the capture rule and roll (Capture Tier Resolution); HUD layout (Viewfinder HUD); gear data and fit rules (Gear Catalog, Inventory & Loadout); pose, look and `can_shoot` (Player Movement).

## Player Fantasy

**Framing: direct.** This is the system the player is holding whenever they are playing the game as a photographer.

**"The world narrows, and I'm ready."** The fantasy is the quiet competence of a photographer who has read the light before the moment arrives. The anchor moment: golden hour on the pier, the sun low behind a Driftfin. The player raises the camera and the world narrows. The spirit appears, a dark shape against the glare, and they know that look now. They turn the compensation dial up a stop and the shape fills with colour. The focus brackets close in Lumen. The glow starts to build, they hold their breath, and they press at the peak. The iris blinks. They know what they did and why, before the darkroom says anything.

**The phone: "I just saw it, and I have it."** The phone player raises a bright, friendly screen, taps nothing and shoots. The device handles exposure and focus, and it even half-corrects a difficult sky. What it cannot do is blur a background or hold a moving subject in the dark. That honesty is the path from phone to camera, and it is a choice, never a trap.

**The manual photographer: "I chose this."** The player who switches to `MANUAL` gives up the safety of automatic settings to shoot 1/500 s and freeze a spirit in flight, or to hold ISO down on a still memory in the fog. It is more attention for more control, never a strictly better mode.

**MDA aesthetics served** (primary first): *Expression* (aperture, focal length and exposure as personal choices), *Challenge* (reading light and timing, never reflexes under threat), *Sensation* (the click of dials, the iris blink, focus closing in), *Submission* (the phone and `AUTO` let a player simply walk and look). **SDT:** *Autonomy* through three programs and many valid settings for one scene; *Competence* through a meter, focus brackets and readouts that explain every result before it happens; *Relatedness* through the spirits themselves, seen only through this lens.

**Language.** Cozy, photographic, never stat talk. "It's bright behind them", not "Backlight penalty". "Too close to focus", not "Below MFD". "Frames left", not "Ammo". The camera never scolds: a dark photo is a dark photo.

**What the player must never feel:** that the controls stole a shot, that manual control is homework, or that the preview lied about what they framed.

## Detailed Design

### Core Rules

**A. The viewfinder**

1. **Entering the viewfinder.** The camera is live only in Movement's `Viewfinder` view state (Movement R12). The raise takes 0.22 s for every device in MVP (Decision D19). The eye anchor (Movement R10) is the camera origin. There is no arm's-length or overhead hold (Decision D18).
2. **Lens world.** Spirits and memories are drawn only in the viewfinder (Subject Rule 14, art bible A1). This system turns the lens layer on when the raise blend reaches `LENS_REVEAL_PERMILLE` (default 500‰) and off at the same point on the way down. The frozen frame and every re-render always show the lens world. Gear never affects this: a phone sees everything a camera sees (Subject Rule 6). In third person only Subject's shimmer (Subject F16) is shown.
3. **Field of view.** The camera's vertical field of view is `vfov_deg` from Gear F3, using the current `f_deci`, `crop_eff_milli` and `zoom_milli`. It is published to Movement for look scaling (Movement F6). The frame is always 3:2 (Gear D11). Where the browser window has another aspect ratio, the 3:2 frame is pillarboxed or letterboxed, and only the 3:2 area is the photo.
4. **No roll.** Roll is always 0 in MVP (Decision D17). Movement's R18 sanity check stays `roll = 0`.
5. **No live sway.** The viewfinder never shakes, sways or bobs (Movement Game Feel; art bible "No screen shake"). Handheld instability is shown by a HUD readout and appears only in the photo (Rule 33).
6. **Input map (viewfinder only; defaults, remappable through Settings & Accessibility).** Movement R21 reserves these for this system. C is Sneak, so the prototype's C/V compensation keys move to the active dial. E is free in the viewfinder because traversal prompts are hidden there (Movement R12).

   | Action | Keyboard / mouse | Gamepad (partial) | Touch (partial) |
   |---|---|---|---|
   | Zoom | Wheel, or Q / E | D-pad up / down | Zoom pill |
   | Turn active dial | Z / X, or Shift + wheel | D-pad left / right | Drag the dial |
   | Next dial | G | North button | Tap the dial |
   | Program (bodies) or phone mode | M | View / Back | Mode button |
   | Phone module | N | West button | Module pill |
   | Hold focus lock | Hold T | Hold LB | Tap a point to focus |
   | Shutter | LMB / Space (Movement R21) | RT | Shutter button |

**B. Programs: how the shot is set**

7. **Three body programs (Decision D2).** Every body starts in `AUTO`.

   | Program | Player sets | Camera sets | Active dial on entry |
   |---|---|---|---|
   | `AUTO` | exposure compensation | aperture, shutter speed, ISO | compensation |
   | `APERTURE` | aperture, exposure compensation | shutter speed, ISO | aperture |
   | `MANUAL` | aperture, shutter speed, ISO | nothing (the meter still reads) | shutter speed |

   Dials cycle only through those the program allows. Focus mode is separate from the program (Rules 18–24). A shutter-priority program is not in MVP: `MANUAL` covers the same need.
8. **The phone has no programs.** A phone is always in auto exposure (Gear Rule 18). The player may set exposure compensation and choose a mode (`AUTO`, `NIGHT`, `PORTRAIT`) and a module. Aperture is fixed by the module.
9. **No manual control is ever required (Decision D1).** A new player can raise, frame, zoom and shoot, on either device, for the whole game. Nothing is locked behind a skill level. Inside the loadout's reach, `AUTO` can reach a correct exposure in every condition by using one dial, compensation, so a player never needs `MANUAL` for a good Exposure result. `APERTURE` and `MANUAL` add creative control (background blur, freezing motion, lower noise), not access. Shooting never requires a manual control; a correct exposure in difficult light does need the compensation dial, and that is the skill.
10. **Shutter speed and ISO are in MVP (Decision D3).** They are always simulated and always recorded, because the handheld limit, low-light reach and `SHUTTER` validation all depend on them. Players meet them as HUD readouts in `AUTO` and `APERTURE`, and as dials only in `MANUAL`.
11. **Stops.** Aperture, shutter speed, ISO and compensation move only in third stops. Aperture values come from Gear's `THIRD_STOPS`; shutter and ISO values come from the lists in F1. Variable-aperture zooms follow Gear F4: zooming in past the set aperture stops it down, and zooming back does not reopen it in `APERTURE` or `MANUAL`.
12. **Exposure compensation.** Range ±3 EV in third stops (matching the art bible's −3 to +3 scale). Compensation shifts what the automatic system aims for. In `MANUAL` it has no effect and the dial is not offered.

**C. Metering and the correct exposure**

13. **One metered value.** The meter reads World's `scene_ev_deci` (World F12). There are no metering patterns in MVP. The client reads it from the world feed; the server reads it from the WorldSnapshot at `capture_ms`.
14. **The meter can be fooled (Decision D4).** Auto exposure aims for the metered value, but the *correct* exposure can differ: a subject against a low sun is darker than the scene, fog wants lifting and night wants to stay dark. `ideal_comp_deci` (F3) is the compensation that gives a correct exposure, derived from the light condition and from how directly the camera faces the key light. This is what makes compensation a skill. Reading the light is the Pillar 1 check, and `AUTO` alone is usable but imperfect in difficult light.
15. **Exposure error.** `exposure_err_deci` (F4) measures how far the shot is from correct, in tenths of a stop. Positive is too bright. It is a fact, and Photo Scoring owns its tolerance.
16. **Phone assist.** The phone applies a share of `ideal_comp_deci` by itself (`PHONE_SCENE_ASSIST_PERMILLE`, default 500‰), so it copes with difficult light better than an uncorrected camera but not perfectly. Bodies apply none: the art bible's *"phone feel easy and the camera feel honest"* (§2.1). This is a deliberate entry-device exception to Pillar 1, kept below full correction.
17. **Noise.** Any ISO above the body's `iso_clean` adds noise (F6). The solver (F5) raises ISO only after the aperture is at its widest allowed and the shutter is at its slowest safe speed, so noise is the last resort. It may go up to `iso_max`. The rest stays underexposed.

**D. Focus**

18. **Continuous autofocus by default (Decision D8).** Mouse and keyboard have no half-press, so a lens with `lens_af_eff ≥ 1` seeks focus whenever the viewfinder is live. Gear F10's "time from half-press" is read here as time from the moment focus starts seeking.
19. **Focus target.** Each frame, the client picks a target: the photographable subject inside the AF zone (F11) nearest the frame centre, with a clear line from the eye to its centre; otherwise the first surface hit by a ray through the frame centre. Ghosted teammates are never targets (they are not in photos, Movement R20). Subjects are tested against their `BOUNDS_MM` sphere, because the ray must find spirits, which have no physics collision.
20. **Seeking and lock.** When the target changes, or its distance changes by more than `AF_RETARGET_PERMILLE`, focus moves to the new distance over `af_eff_ms` (F10) and then locks. While locked on a moving subject, focus follows it with a lag of `track_lag_ms` (F10).
21. **Focus lock.** Holding the focus-lock input freezes `focus_mm` at its current value, so the player can focus and recompose to place a subject outside the AF zone. Releasing resumes seeking.
22. **Too close.** If the target is nearer than the lens's `mfd_mm`, focus stops at `mfd_mm` and the HUD shows "too close". `CURIOUS_MIN_GAP_MM` (1,500 mm) is above every MVP lens's `mfd_mm` (the largest is 1,200 mm), so a curious subject never comes closer than focus allows unless the player walks in.
23. **Manual focus.** A lens with `lens_af_eff = 0` (natively or through a DUMB adapter) is focused only by the ring, which is the active dial on entry. The ring moves through `FOCUS_RING_STEPS` positions evenly spaced in reciprocal distance, as real rings are (F9). There is no timer and no minigame (Gear Game Feel). Focus peaking (Rule 45) shows what is sharp. Bodies with an AF lens can also switch to the ring through the dial cycle.
24. **Phone focus.** The phone's AF zone is the whole frame (Gear Rule 18: continuous subject-detect). On touch, a tap chooses the nearest subject or surface at that point and holds it until the next tap or until the viewfinder lowers. A phone has no manual ring.
25. **Release priority (Decision D9).** The shutter always fires at once, whatever the focus state. A player must never lose a shot to the camera; a soft photo is a readable result, and a refused press is a stolen moment.
26. **Focus results.** The server takes the recorded `focus_mm` and the true subject distance at `capture_ms` and computes depth of field (F7, an integer evaluation of Gear F6) and `defocus_bp` (F8) for every photographable subject. A subject that moved after focus locked is therefore honestly soft. Which subject counts is Photo Scoring's choice.

**E. Zoom**

27. **Optical zoom.** Primes do not zoom. Zooms move through `f_min_deci`..`f_max_deci` in multiplicative steps (F12), so a wheel notch feels the same at both ends. The FOV changes on the same frame, with no easing, so the recorded value is the rendered value.
28. **Phone zoom.** The phone switches module in `module_switch_ms` (300 ms). During a switch the shutter is unavailable. Digital zoom runs from 1000 to `digital_zoom_max_milli` on the main module only and resets to 1000 on a module switch. The ultrawide has no digital zoom (Gear Edge Cases).
29. **Lens changes.** A lens swap happens in third person only, is performed through Inventory & Loadout and takes the mount's `swap_ms`; a raise is refused until it finishes. After a swap, `f_deci` becomes `f_min_deci`, the aperture clamps to the new lens's legal range, and focus restarts.

**F. The shot**

30. **What a shot records (`ShotSettings`).** All integers or enums, sent in `SHUTTER` (Network Rule 7 and the 512-byte cap). Photo Recipe owns the schema; this system owns the content and meaning.

    | Field | Type | Range | Sent when | Meaning |
    |---|---|---|---|---|
    | `program` | enum | `AUTO`, `APERTURE`, `MANUAL`, `PHONE` | always | How the shot was set |
    | `phone_mode` | enum | `AUTO`, `NIGHT`, `PORTRAIT` | phone | Computational mode |
    | `module_id` | int | phone's module list | phone | Active module |
    | `f_deci` | int | lens or module range | always | Real focal length |
    | `zoom_milli` | int | 1000..`digital_zoom_max_milli` | phone | Digital zoom |
    | `n_deci` | int | Gear Rule 19 at `f_deci`, on `THIRD_STOPS` | `APERTURE`, `MANUAL` | Aperture |
    | `t_us` | int | body range, on `SHUTTER_STOPS` | `MANUAL` | Shutter speed |
    | `iso` | int | body range, on `ISO_STOPS` | `MANUAL` | ISO |
    | `comp_t` | int | −9..+9 | not `MANUAL` | Compensation in third stops |
    | `focus_mm` | int | `mfd_mm`..`FOCUS_INF_MM` | always | Focus distance |
    | `focus_mode` | enum | `AF`, `AF_HELD`, `RING` | always | How focus was set (telemetry and darkroom wording) |
    | `burst_id` | int | 0 = single; else per-session counter | always | Groups frames of one burst |
    | `burst_index` | int | 0..`BURST_MAX_FRAMES − 1` | always | Frame number in the burst |

    Camera pose comes from Movement R15, and `view_tick` from Network Rule 24. Gear IDs, `spec_rev`, world state and subject state come from the server (Network Rule 7).
31. **Automatic values are derived on the server (Decision D16).** Anything the program sets is not sent. The server runs the same solver (F5) at `capture_ms` and stores the resolved `n_deci`, `t_us` and `iso`. A client therefore cannot claim an automatic value it did not earn, the message stays small, and the player's auto exposure is always right for the true capture instant. The HUD's values are a prediction that differs from the result only if the light changes across the rewind (Edge Cases).
32. **Server evaluation (`ShotEvaluation`).** After Network's seven checks and `capture_tick`, the server calls `evaluate_shot`, a pure function of `ShotSettings`, the capture pose, the catalog specs at the server loadout's `spec_rev`, the WorldSnapshot and the SubjectSnapshots. It outputs:

    | Output | Type | Formula | Read by |
    |---|---|---|---|
    | `n_deci`, `t_us`, `iso` (resolved) | int | F5 or as sent | Recipe, Scoring |
    | `cam_ev_t`, `exposure_err_deci`, `ideal_comp_deci` | int | F2–F4 | Scoring |
    | `noise_permille` | int | F6 | Scoring, re-render |
    | `shake_bp` | int | F13 | Scoring, re-render |
    | `night_applied`, `portrait_applied` | bool | F16, Rule 36 | Scoring, re-render |
    | Per subject: `d_mm`, `in_dof`, `defocus_bp`, `motion_bp`, `x_bp`, `y_bp`, `in_frame` | int, bool | F7, F8, F14, F15 | Scoring |

    Everything except the frame position (F15) is integer-only, under World Core Rule 10. These values are inputs to the score. They are never sent to the client before the commit, because they are part of the result (Network Rule 29).
33. **Camera shake.** Below the safe handheld time (F13) the shot has no shake. Above it, `shake_bp` grows with shutter time. Moving while shooting shortens the safe time. Stabilisation comes only through Gear F8. Shake is a recorded result drawn in the photo. It is not a live effect, so art bible P4's rule against baking client-side camera shake is not broken: nothing the client invented reaches the photo.
34. **Subject motion blur.** The exposure is treated as one instant at `capture_ms`, with a blur length of the subject's on-frame speed × shutter time (F14). No future simulation is needed, because velocity comes from a backward sample of the subject's position. Panning with a subject is not modelled in MVP (Open Question 6).
35. **Phone `NIGHT`.** The stack is built from the *preceding* `NIGHT_MODE_HOLD_MS` (Decision D14). A ring fills while the phone and the subject have been still. If the ring is full at the press, `NIGHT_MODE_STOPS` are gained (F16); otherwise the shot is a normal exposure, as Gear Rule 18 requires. The capture stays at the press, so Movement R15, Network F8 and the decisive moment are all honoured, and no shot is ever delayed.
36. **Phone `PORTRAIT`.** If a photographable subject is inside the frame at `capture_ms`, `portrait_applied` is true and the background beyond it gets `PORTRAIT_SYNTH_BLUR_BP` in the render. With no subject it is a normal AUTO shot (Gear Edge Cases). Artefact penalties belong to Photo Scoring.

**G. Shot limits**

37. **Frame allowance (Decision D12).** The player holds up to `FRAME_CAP` frames (default 36, a roll of film). Each accepted shot spends one. Frames return at one per `FRAME_REFILL_MS` (default 30,000 ms) of server time, online or offline (F18). The counter is the same for phone and camera. Its purpose is that each press is a choice (Pillar 2), that the number of rarity rolls stays bounded, and that a gentle, time-based limit replaces any town trip or purchase. Frames are never sold. Added 2026-11-05: when frames run low, the HUD shows a calm cue before they reach 0, and an empty press gives a soft click plus the time until the next frame, so a shot is never silently lost. Playtest the "punished" question; lower `BURST_MAX_FRAMES` if bursts drain the roll too fast.
38. **The server owns frames.** The session server applies F18 and spends the frame when the shot passes validation. The client predicts locally and reconciles from the value the server returns. A shot refused for any reason spends nothing. A shot lost before it reached the server spends nothing (Network Edge Cases: "shot count restored by Camera Model"). Frames are written in the same commit as the photo, so a crash that loses a shot also loses its frame spend.
39. **Battery.** No battery drain in MVP (Gear D12, decided). The HUD shows no battery meter.
40. **Burst (Decision D13).** Pressing fires one frame. Holding past `BURST_HOLD_MS` fires more at `frame_interval_ms` (F17), up to `BURST_MAX_FRAMES` frames or until frames run out. Each frame is its own `SHUTTER`, with its own pose, settings, `view_tick` and `rid`. Frames in one burst share `burst_id`. Pressing repeatedly is limited by the same interval. Because F17 never exceeds Network's refill rate (F1b), a normal client never reaches a rate-limit violation.
41. **Long exposures.** The shutter cannot fire again until the exposure ends (`fire_gap_ms`, F17). For `t_us ≥ LONG_EXPOSURE_US`, the device shows a calm progress ring and the state is `Exposing`. The shot is already sent and judged at the press, so lowering the camera during this time does not cancel it. `bulb` is not offered in MVP.

**H. Sound and presence**

42. **The shutter makes a sound spirits can hear.** On each accepted shot the server adds a presence event of `SHUTTER_PRESENCE_M[shutter_sound_id]` through Movement's channel (Movement R9). Quiet shutters are a real side-grade. Subject & Spirit owns every reaction.
43. **Shutter events refresh, never stack.** A burst must not add up to a shout. A new shutter event replaces any active one from the same player and restarts its 0.5 s (F19).

**I. The preview**

44. **The preview shows the same facts as the photo, not the same pixels (Decision D7).** The live view uses the true FOV, aperture, focus distance and exposure, computed by the same library the server uses. It must agree with the re-render within the limits in F20, F21 and the acceptance criteria. It may be cheaper in blur quality. Motion blur, shake and final noise appear only in the photo, because a still's blur does not exist until the shutter fires. The live view signals them with HUD readouts instead (Rules 46–47).
45. **Depth preview and peaking.** Depth blur is drawn by a custom depth-based post effect, because native depth of field does not work on the Compatibility renderer (prototype finding). Per-pixel blur comes from the same `defocus_bp` as F8. On a manual ring, or whenever the peaking setting is on, surfaces between `D_near` and `D_far` get a soft Lumen tint.
46. **Exposure preview.** The camera view shows true exposure, so a dark scene stays dark (art bible §2.1), within the clamp in F21. The phone view is compressed to be brighter and flatter, and its photos use the same tone, so preview and photo agree. Exposure gain is applied in the same post pass (UNVERIFIED).
47. **Noise and motion indicators (Decisions D5, D6).** Noise above `iso_clean` is shown in the live view as a fine grain overlay, and the ISO readout gains a small marker. Shake and motion risk are shown by a three-state **steadiness** readout (steady, soft, shaky) from `t_us` against `t_safe_us` (F13). In the photo, grain, shake and subject smear are drawn from the recorded integers.
48. **Quality fallback.** If the depth blur is too costly on a device, a lower preview quality reduces taps, and the lowest level turns blur off and relies on peaking and a depth-of-field bar in the HUD. The photo's re-render is unaffected. Thresholds wait for measurement (Open Question 1).
49. **The frozen frame.** At the press the client freezes the current frame for `FREEZE_MS`, plays the iris blink (under 150 ms, art bible §2.1) and the body's `shutter_sound_id`, all within 1 frame and with no network wait (Network Game Feel). The frozen frame shows no result. If the server never acknowledges the shot, it shows "not sent", never "developing" (Network Edge Cases).

**J. Validation**

50. **`validate_settings`.** This pure function runs on the server inside Network's Range and identity check (Network Rule 20) and Rule 25. For the server's loadout it requires: `f_deci` in range; `zoom_milli` legal for the module; `n_deci` on `THIRD_STOPS` and within `n_max_at(f)`..`n_min`; `t_us` on `SHUTTER_STOPS` within the body range; `iso` on `ISO_STOPS` within the body range; `comp_t` within ±9; `focus_mm` within `mfd_mm`..`FOCUS_INF_MM`; and only the fields the program sends. A failure is `ERR_OUT_OF_RANGE`: the shot is not spent, and nothing is rolled. Bodies with no lens are rejected (Gear Edge Cases).

**What this system does not own:** the worth of any value it reports (Photo Scoring); the recipe schema (Photo Recipe); `capture_tick` and the rate limit (Network); world light (World); subject simulation (Subject & Spirit); spec values and gear functions (Gear Catalog); the equipped loadout (Inventory & Loadout); HUD layout (Viewfinder HUD); the look of the lens-world grade (art bible, technical-artist); sounds (Audio: SFX & Ambience).

### States and Transitions

**Device state** (client; independent of Movement's view state, which gates it)

| State | Entered when | Left when | Shutter | Notes |
|---|---|---|---|---|
| `Stowed` | view state is not `Viewfinder` | raise completes → `Live` | no | Settings are kept; lens layer off (except during the blend, Rule 2) |
| `Swapping` | lens swap starts (third person) | `swap_ms` elapsed → `Stowed` | no | Raise is refused |
| `Live` | raise complete; or a state below ends | lower → `Stowed`; press → `Firing`; module switch → `Switching` | yes, if the gate passes | Dials, zoom and focus all run |
| `Switching` | phone module change | `module_switch_ms` elapsed → `Live` | no | Preview stays live |
| `Firing` | a frame fires | `fire_gap_ms` elapsed → `Live`, or next burst frame | no | Iris, sound and frozen frame |
| `Exposing` | a frame fires with `t_us ≥ LONG_EXPOSURE_US` | `t_us` elapsed → `Live` | no | Progress ring; lowering is allowed and cancels nothing |
| `Paused` | Network session is not `Synced` | `Synced` → `Live` | no | Preview stays live; "Reconnecting, shutter paused" |

**Shutter gate.** A press fires only when all hold: Movement `can_shoot` is true; the device state is `Live`; Network is `Synced`; the loadout is valid; predicted `frames_now ≥ 1`. A press that fails the gate does nothing and is not buffered (Movement Edge Cases).

**Focus state** (client)

| State | Entered when | Left when | HUD |
|---|---|---|---|
| `AF_SEEK` | viewfinder live with an AF lens, or the target changes | `af_eff_ms` elapsed → `AF_LOCK`; hold input → `AF_HELD` | Brackets open |
| `AF_LOCK` | seek completes | target changes → `AF_SEEK`; hold input → `AF_HELD` | Brackets closed, Lumen |
| `AF_HELD` | focus-lock input is held | release → `AF_SEEK` | Brackets closed, lock mark |
| `AF_NEAR` | target nearer than `mfd_mm` | target beyond `mfd_mm` → `AF_SEEK` | "Too close" |
| `RING` | manual lens, or ring chosen on the dial cycle | AF chosen again → `AF_SEEK` | Ring scale and peaking |

**Phone `NIGHT` hold** (shown as a ring; the server recomputes eligibility): `Filling` while still → `Ready` at `NIGHT_MODE_HOLD_MS` → back to `Filling` from 0 on any movement.

### Interactions with Other Systems

| System | Direction | What flows | Owner of the rule |
|---|---|---|---|
| Player Movement & Exploration | Movement → this | eye anchor, look yaw and pitch, view state, `can_shoot`, body speed, capture pose | Movement owns pose and the gate |
| Player Movement & Exploration | this → Movement | current `vfov_deg` (Movement F6); shutter presence event (F19) | This system owns FOV and the magnitude |
| Gear Catalog & Specs | Catalog → this | specs, setting ranges (Rule 19), F1–F6, F8, F10, `NIGHT_MODE_*`, `PORTRAIT_SYNTH_BLUR_BP`, `shutter_sound_id`, `swap_ms`, `module_switch_ms` | Catalog owns specs and those formulas; this system calls them unchanged |
| Inventory & Loadout | Loadout → this | server loadout at the capture tick; client copy for the dials | Loadout |
| World Time, Weather & Light | World → this | `scene_ev_deci`, `condition`, key-light angles and source (feed on the client, WorldSnapshot on the server) | World owns the values; this system owns exposure maths (World Rule 9) |
| Subject & Spirit Behaviour | Subject → this | SubjectSnapshots at `capture_ms`, position function for backward samples, `BOUNDS_MM`, live snapshots for AF | Subject |
| Subject & Spirit Behaviour | this → Subject | nothing directly; shutter presence passes through Movement | Subject owns reactions |
| Network Transport & Server Authority | this → Network | `ShotSettings`, `validate_settings`, `frame_interval_ms` pacing | This system owns the content |
| Network Transport & Server Authority | Network → this | `capture_tick`, session state, `SHUTTER_RESULT` (`frames_left`, refusal reasons), `NOTICE throttled` | Network owns transport and rewind |
| Photo Recipe & Re-render | this → Recipe | `ShotSettings`, resolved values, re-render inputs (`noise_permille`, `shake_bp`, per-subject `motion_bp`, flags) | Recipe owns the schema |
| Photo Scoring | this → Scoring | `ShotEvaluation` | Scoring owns every score effect and tolerance, and picks the primary subject |
| Capture Tier Resolution | indirect | `burst_id` for any burst rule | Resolution owns the roll |
| Viewfinder HUD | this → HUD | all readouts in UI Requirements | HUD owns layout |
| Accounts & Server Persistence | both | `frames_prev`, `frames_ts_ms` per account, written with the photo commit | Accounts owns storage |
| Capture Encounter | Encounter → this | may request a temporary input hint; no rule changes | This system stays unchanged in encounters |
| Onboarding & Tutorial (VS) | this → Onboarding | teaching order: frame, zoom, compensation, then aperture | Onboarding |
| Audio: SFX & Ambience (VS) | this → Audio | shutter, dial click, focus confirm, zoom and lens-layer events | Audio owns sounds |
| Co-op Crew Roles (Alpha) | Roles → this | tripod or Astro hooks (Open Question 5) | Roles |
| Settings & Accessibility (Alpha) | Settings → this | remapping, peaking, grid, assist layer, reduce flashing | Settings |

## Formulas

Notation: integers unless stated. `floordiv` rounds toward negative infinity, as in World and Subject. `rdiv(a, b) = floordiv(2a + b, 2b)` for `b > 0` (round half up). `ceil_div` rounds up. `isqrt` is Subject's integer floor square root. All products stay within signed 64-bit for the ranges shown. **Reused unchanged:** Gear F1 (`crop_eff_milli`), F2 (`f_eq_mm`), F3 (`vfov_deg`), F4 (`n_max_at`), F5 (`coc_dum`), F6 (depth of field; F7 below evaluates the same equations in integers), F8 (`t_hand_us`), F10 (`af_ms`), F13 (`lens_af_eff`, `ois_eff`); World F12 (`scene_ev_deci`), F11 (key light).

### F1. Stop scale

The stop_scale formula is defined as:

`av_t(n) = index of n in THIRD_STOPS`;  `tv_t(t)` and `sv_t(iso)` = table lookups;  `thirds(x_deci) = floordiv(3 × x_deci + 5, 10)`;  `deci(x_t) = floordiv(20 × x_t + 3, 6)`

`SHUTTER_STOPS` (`tv_t` → µs): 39: 125 · 38: 156 · 37: 200 · 36: 250 · 35: 313 · 34: 400 · 33: 500 · 32: 625 · 31: 800 · 30: 1,000 · 29: 1,250 · 28: 1,563 · 27: 2,000 · 26: 2,500 · 25: 3,125 · 24: 4,000 · 23: 5,000 · 22: 6,250 · 21: 8,000 · 20: 10,000 · 19: 12,500 · 18: 16,667 · 17: 20,000 · 16: 25,000 · 15: 33,333 · 14: 40,000 · 13: 50,000 · 12: 66,667 · 11: 76,923 · 10: 100,000 · 9: 125,000 · 8: 166,667 · 7: 200,000 · 6: 250,000 · 5: 300,000 · 4: 400,000 · 3: 500,000 · 2: 600,000 · 1: 800,000 · 0: 1,000,000 · −1: 1,300,000 · −2: 1,600,000 · −3: 2,000,000 · −4: 2,500,000 · −5: 3,200,000 · −6: 4,000,000 · −7: 5,000,000 · −8: 6,000,000 · −9: 8,000,000 · −10: 10,000,000 · −11: 13,000,000 · −12: 15,000,000 · −13: 20,000,000 · −14: 25,000,000 · −15: 30,000,000

`ISO_STOPS` (`sv_t` → ISO): −3: 50 · −2: 64 · −1: 80 · 0: 100 · 1: 125 · 2: 160 · 3: 200 · 4: 250 · 5: 320 · 6: 400 · 7: 500 · 8: 640 · 9: 800 · 10: 1000 · 11: 1250 · 12: 1600 · 13: 2000 · 14: 2500 · 15: 3200 · 16: 4000 · 17: 5000 · 18: 6400 · 19: 8000 · 20: 10000 · 21: 12800 · 22: 16000 · 23: 20000 · 24: 25600 · 25: 32000 · 26: 40000 · 27: 51200

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| n | int (deci f) | on `THIRD_STOPS` | setting / F5 | Aperture; index 0 = f/1.0, 3 = f/1.4, 15 = f/5.6, 30 = f/32 |
| t | int (µs) | on `SHUTTER_STOPS` | setting / F5 | Shutter speed |
| iso | int | on `ISO_STOPS` | setting / F5 | ISO |
| x_deci | int (0.1 EV) | −300 to 300 | calculated | A value in tenths of a stop |
| x_t | int (third stops) | −90 to 90 | calculated | A value in third stops |
| av_t, tv_t, sv_t | int (third stops) | 0–30; −15–39; −3–27 | calculated | Stop index of each setting |

**Output Range:** exact integers. Using nominal stops rather than `log2` of marked values is deliberate: it needs no float on the server, and it matches how real dials are marked. The difference from true `log2` is below 0.1 EV at every entry.
**Example:** f/5.6 → index 15; 1/60 s → 18; ISO 3200 → 15. `thirds(105)` = floordiv(320, 10) = **32**. `deci(32)` = floordiv(643, 6) = **107**. `deci(−2)` = floordiv(−37, 6) = **−7**.

### F2. Camera exposure value

The camera_ev formula is defined as:

`cam_ev_t = av_t(n) + tv_t(t) − sv_t(iso) − (night_applied ? NIGHT_MODE_STOPS × 3 : 0)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| av_t, tv_t, sv_t | int (third stops) | see F1 | calculated (F1) | Settings on the stop scale |
| night_applied | bool | — | calculated (F16) | Phone stack succeeded |
| NIGHT_MODE_STOPS | int (stops) | 0–4; default 3 | data file (Gear) | Stack gain |
| cam_ev_t | int (third stops) | −54 to 72 | calculated | Scene EV these settings expose correctly, at ISO 100 |

**Output Range:** −54 to 72 third stops. It is the same unit as World F12 after `thirds`, so it matches Gear F9 at its reach point.
**Example:** Kanro Hearth, kit zoom at f/4.5 (13), 1/60 s (18), ISO 3200 (15): 13 + 18 − 15 = **16** third stops, `deci` = 53 (EV 5.3), agreeing with Gear F9's reach of 52 for this loadout.

### F3. Ideal compensation

The ideal_comp formula is defined as:

`delta_deci = abs(mod(bearing_deci − azim_deci + 1800, 3600) − 1800)`;  `backlit_permille = (key_source = SUN and elev_deci > 0) ? max(0, 1000 − floordiv(1000 × delta_deci, BACKLIT_ARC_DECI)) : 0`;  `ideal_comp_deci = clamp(COND_COMP[condition] + floordiv(BACKLIT_COMP[condition] × backlit_permille, 1000), −IDEAL_COMP_MAX, IDEAL_COMP_MAX)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| bearing_deci | int (0.1°) | 0–3599 | calculated (capture pose yaw, floored at the boundary, converted to World's clockwise-from-north convention) | Compass bearing of the camera's look |
| azim_deci, elev_deci | int (0.1°) | 0–3599; −900–900 | World F11 | Key-light azimuth and elevation |
| key_source | enum | SUN, MOON | World F11 | Which body is the key light |
| condition | enum | 7 conditions | World F5 | Light condition |
| BACKLIT_ARC_DECI | int (0.1°) | 200–900; default 450 | data file | Half-angle within which the camera counts as facing the sun |
| COND_COMP | map (0.1 EV) | −15 to 15; defaults DAWN +3, MIDDAY 0, GOLDEN_HOUR 0, BLUE_HOUR −3, NIGHT −7, OVERCAST_FOG +3, RAIN 0 | data file | What the meter gets wrong in this light |
| BACKLIT_COMP | map (0.1 EV) | 0–20; defaults DAWN 7, MIDDAY 7, GOLDEN_HOUR 10, others 0 | data file | Extra light needed when facing the sun |
| IDEAL_COMP_MAX | int (0.1 EV) | 10–30; default 20 | data file | Limit |
| backlit_permille | int (‰) | 0–1000 | calculated | How directly the camera faces the sun |
| ideal_comp_deci | int (0.1 EV) | −20 to 20 | calculated | The compensation that gives a correct exposure; positive means "add light" |

**Output Range:** ±2 EV, always inside the ±3 EV dial, so `AUTO` can always reach it. Overcast light has no backlight, because the table gives it 0.
**Example:** golden hour at phase 2,300 s, key light azimuth 2773, elevation 44 (World F11's example); the camera looks along bearing 2800. `delta` = abs(mod(1827, 3600) − 1800) = 27. `backlit` = 1000 − floordiv(27,000, 450) = **940**. `ideal_comp_deci` = 0 + floordiv(10 × 940, 1000) = **9**: about one stop up.

### F4. Exposure error

The exposure_error formula is defined as:

`exposure_err_deci = clamp(scene_ev_deci − ideal_comp_deci − deci(cam_ev_t), −EXP_ERR_MAX, EXP_ERR_MAX)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| scene_ev_deci | int (0.1 EV) | −40 to 160 | World F12 at `capture_ms` | Metered brightness |
| ideal_comp_deci | int (0.1 EV) | −20 to 20 | calculated (F3) | Correct compensation |
| cam_ev_t | int (third stops) | −54 to 72 | calculated (F2) | Settings used |
| EXP_ERR_MAX | int (0.1 EV) | 50–150; default 100 | data file | Keeps the value bounded |
| exposure_err_deci | int (0.1 EV) | −100 to 100 | calculated | 0 is correct; positive is too bright |

**Output Range:** ±10 EV. Third-stop steps and rounding mean the best achievable value can be up to ±4 (0.4 EV) from 0, so Photo Scoring's full-marks tolerance must be at least that wide.
**Example:** the F3 scene (`scene_ev_deci` 105, ideal 9). Lantern, KR 85 at f/2 (6), `APERTURE`, compensation 0: F5 gives ISO 100 and 1/400 s, `cam_ev_t` = 6 + 26 − 0 = 32, `deci` = 107. Error = 105 − 9 − 107 = **−11** (a stop dark). With compensation +3 thirds, F5 gives 1/200 s, `cam_ev_t` = 29, `deci` = 97. Error = 105 − 9 − 97 = **−1**.

### F5. Auto exposure solver

The auto_exposure formula is defined as:

`target_t = thirds(scene_ev_deci − floordiv(ideal_comp_deci × ASSIST, 1000)) − comp_t + gain_t`, then, in order:

1. `sv = sv_lo`;  `av` = the set aperture (`APERTURE`, phone), or `clamp(AUTO_AV_T, av_lo, av_hi)` (`AUTO`);  `tv = target_t − av + sv`.
2. **Too bright** (`tv > tv_hi`), `AUTO` only: `av = min(av_hi, av + tv − tv_hi)`;  `tv = target_t − av + sv`.
3. **Too dark** (`tv < tv_floor`), `AUTO` only: `av = max(av_lo, av − (tv_floor − tv))`;  `tv = target_t − av + sv`.
4. **Still too dark** (`tv < tv_floor`): `sv = min(sv_hi, sv + tv_floor − tv)`;  `tv = target_t − av + sv`.
5. `tv = clamp(tv, tv_floor, tv_hi)`. Whatever cannot be reached stays in the exposure error.

with `tv_floor = max(tv_lo, the smallest tv_t whose time ≤ min(t_hand_us, T_SUBJECT_US))`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| scene_ev_deci | int (0.1 EV) | −40 to 160 | World F12 | Metered brightness |
| ideal_comp_deci | int (0.1 EV) | −20 to 20 | calculated (F3) | Correct compensation |
| ASSIST | int (‰) | 0 for bodies; `PHONE_SCENE_ASSIST_PERMILLE` (0–1000, default 500) for phones | data file | Share of the correction applied automatically |
| comp_t | int (third stops) | −9 to 9 | setting | Exposure compensation |
| gain_t | int (third stops) | 0 or `NIGHT_MODE_STOPS` × 3 | calculated (F16) | Phone stack gain |
| AUTO_AV_T | int (index) | 12–18; default 15 (f/5.6) | data file | Aperture `AUTO` prefers |
| av_lo, av_hi | int | from `n_max_at(f)` and `n_min` | Gear F4, Rule 19 | Widest and smallest aperture indices |
| tv_lo, tv_hi | int | from `shutter_slow_us`, `shutter_fast_us` | data file (body) | Slowest and fastest shutter indices |
| sv_lo, sv_hi | int | from `iso_min`, `iso_max` | data file (body) | ISO limits |
| t_hand_us | int (µs) | 2,222–5,333,333 | Gear F8 | Handheld limit |
| T_SUBJECT_US | int (µs) | 8,000–33,333; default 16,667 | data file (Gear) | Slowest shutter for a gently moving subject |
| av, tv, sv | int | see above | calculated | Result; mapped back to `n_deci`, `t_us`, `iso` through F1 |

**Output Range:** always legal settings for the loadout. The order matches Gear F9: at the scene where `sv` reaches `iso_clean` with `tv = tv_floor` and the widest aperture, the solver lands exactly on the reach value. Past that, noise rises (F6) up to `iso_max`, and then the shot goes dark.
**Example:** Hearth + kit at 18 mm, `AUTO`, `scene_ev_deci` 52, compensation 0. `target_t` = 16; `tv_floor` = 18 (1/60 s, as 16,667 < 296,296). Step 1: `sv` 0, `av` 15, `tv` 1. Step 3: `av` = max(13, 15 − 17) = 13, `tv` 3. Step 4: `sv` = min(21, 15) = 15, `tv` = 16 − 13 + 15 = 18. Result: **f/4.5, 1/60 s, ISO 3200**, Gear F9's reach case. Phone NIGHT with the stack ready, `scene_ev_deci` 16, taking `ideal_comp_deci` as 0 to match Gear F9: `target_t` = 5 + 9 = 14, `av` 5, `sv` −3, `tv` 6; step 4: `sv` = min(15, −3 + 12) = 9, `tv` 18. Result: **1/60 s, ISO 800**, matching Gear F9's NIGHT reach of 16.

### F6. Noise level

The noise_level formula is defined as:

`noise_permille = min(1000, max(0, sv_t(iso) − sv_t(iso_clean)) × NOISE_PER_THIRD_PERMILLE)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| iso | int | body range | resolved setting | ISO used |
| iso_clean | int | 400–25,600 | data file (body) | Highest noise-free ISO |
| NOISE_PER_THIRD_PERMILLE | int (‰) | 30–120; default 60 | data file | Grain per third stop above clean |
| noise_permille | int (‰) | 0–1000 | calculated | Grain strength |

**Output Range:** 0–1000; 0 at or below `iso_clean`. Photo Scoring decides its effect (Gear Rule 9).
**Example:** Hearth at ISO 12800: (21 − 15) × 60 = **360**. Lantern at ISO 51200: (27 − 18) × 60 = **540**. Phone at ISO 800: **0**.

### F7. Depth of field in integers

The dof_int formula is defined as (the equations of Gear F6, in deci-mm):

`H_d = floordiv(f_deci² × 10,000, n_deci × coc_dum) + f_deci`;  `s_d = focus_mm × 10`;  `D_near_mm = rdiv(focus_mm × (H_d − f_deci), H_d + s_d − 2 × f_deci)`;  `D_far_mm = rdiv(focus_mm × (H_d − f_deci), H_d − s_d)` if `s_d < H_d`, else `DOF_INF`;  `in_dof = D_near_mm ≤ d_mm ≤ D_far_mm`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| f_deci | int (deci-mm) | 19–3000 | setting | Real focal length |
| n_deci | int (deci f) | 10–320 | resolved setting | Aperture |
| coc_dum | int (0.1 µm) | 42–420 | Gear F5 | Circle of confusion |
| focus_mm | int (mm) | `mfd_mm`..`FOCUS_INF_MM` | setting | Focus distance |
| d_mm | int (mm) | ≥ 1 | calculated (`isqrt` of eye-to-subject offset, mm) | True subject distance at `capture_ms` |
| DOF_INF | int | 2,147,483,647 | constant | Stands for infinity |
| H_d | int (deci-mm) | — | calculated | Hyperfocal distance |
| D_near_mm, D_far_mm | int (mm) | `mfd_mm`..`DOF_INF` | calculated | Sharp range |
| in_dof | bool | — | calculated | Subject is acceptably sharp |

**Output Range:** `D_near_mm ≤ focus_mm ≤ D_far_mm`. Agrees with Gear F6's floats to the nearest millimetre on its examples. Gear Rule 6 leaves depth of field to the consumer; doing it in integers keeps the server deterministic.
**Example:** KR 50 f/1.8 on the Hearth, focused at 2 m: `H_d` = floordiv(2,500,000,000, 3,600) + 500 = **694,944** (69,494 mm, as Gear F6). `D_near_mm` = rdiv(1,388,888,000, 713,944) = **1,945**. `D_far_mm` = rdiv(1,388,888,000, 674,944) = **2,058**. Phone main at 2 m: `H_d` = 21,815, near **1,044**, far **23,988**.

### F8. Defocus blur

The defocus formula is defined as:

`defocus_bp = rdiv(f_deci² × abs(d_mm − focus_mm) × crop_eff_milli, 36 × n_deci × (focus_mm − floordiv(f_deci, 10)) × d_mm)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| f_deci, n_deci, focus_mm, d_mm | int | see F7 | see F7 | Same inputs as F7; `d_mm` capped at `FOCUS_INF_MM` |
| crop_eff_milli | int | 790–7000 | Gear F1 | Effective crop |
| defocus_bp | int (basis points of frame width) | 0–about 3,000 | calculated | Blur disc diameter of a point at `d_mm`, as a share of frame width |

**Output Range:** 0 when `d_mm = focus_mm`. This is Gear F7's blur index generalised to any distance: as `d_mm` grows large it tends to F7's value. A full-frame 30 µm circle of confusion is 8.3 bp of a 36 mm frame, so `defocus_bp` ≤ 8 corresponds to `in_dof`.
**Example:** KR 50 f/1.8 on the Hearth, focus 2,000, subject at 2,300: 250,000 × 300 × 1500 = 112,500,000,000 over 36 × 18 × 1,950 × 2,300 = 2,906,280,000 → **39 bp**. At the far limit `d_mm` 2,058: **8 bp**. KR 85 f/1.4 on the Lantern, focus 2,000, `d_mm` at the 1,000,000 cap: 722,500 × 998,000 × 1000 over 36 × 14 × 1,915 × 1,000,000 → **747 bp**, close to Gear F7's 749 for a background at infinity.

### F9. Focus ring

The focus_ring formula is defined as:

`s_mm(p) = floordiv(mfd_mm × FOCUS_INF_MM × FOCUS_RING_STEPS, FOCUS_INF_MM × (FOCUS_RING_STEPS − p) + mfd_mm × p)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| p | int | 0..`FOCUS_RING_STEPS` | client state | Ring position |
| mfd_mm | int (mm) | 80–1200 in MVP | data file (lens) | Minimum focus distance |
| FOCUS_INF_MM | int (mm) | default 1,000,000 | data file | The ring's far end, matching Gear F6's range for `s` |
| FOCUS_RING_STEPS | int | 200–800; default 400 | data file | Ring resolution |
| s_mm | int (mm) | `mfd_mm`..`FOCUS_INF_MM` | calculated | Focus distance at `p` |

**Output Range:** `mfd_mm` at `p` = 0 and `FOCUS_INF_MM` at the end, evenly spaced in reciprocal distance like a real ring. The default keeps one step smaller than the depth of field for the longest MVP lens at 10 m (about 208 mm per step against about 315 mm of depth at 300 mm f/7.1 on APS-C).
**Example:** Hollin 58 (`mfd_mm` 600): `p` = 0 → **600**; `p` = 200 → floordiv(240,000,000,000, 200,120,000) = **1,199**; `p` = 400 → **1,000,000**.

### F10. Autofocus timing

The af_timing formula is defined as:

`af_eff_ms = floordiv(af_ms × (scene_ev_deci < AF_DARK_EV_DECI ? AF_DARK_PERMILLE : 1000), 1000)`;  `track_lag_ms = floordiv(af_eff_ms × TRACK_LAG_PERMILLE, 1000)`;  while locked, `focus_mm(t) = d_mm(t − track_lag_ms)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| af_ms | int (ms) | 105–780 | Gear F10 | Base time to lock |
| scene_ev_deci | int (0.1 EV) | −40 to 160 | World F12 (feed) | Metered brightness |
| AF_DARK_EV_DECI | int (0.1 EV) | 0–60; default 30 | data file | Below this, focus slows |
| AF_DARK_PERMILLE | int (‰) | 1000–2000; default 1500 | data file | Slowdown in the dark |
| TRACK_LAG_PERMILLE | int (‰) | 50–500; default 200 | data file | Tracking lag as a share of lock time |
| af_eff_ms | int (ms) | 105–1,170 | calculated | Seek time now |
| track_lag_ms | int (ms) | 5–585 | calculated | How far focus trails a moving subject |

**Output Range:** the slowest case, 1,170 ms, still fits inside one anticipation plus decisive window (at least 1,000 + 1,200 ms, Subject F11). Autofocus never fails in MVP, because hunting and refusal would break the cozy tone. Focus is client-side, and the server only sees `focus_mm`.
**Example:** kit zoom on the Hearth, `af_ms` 517: daylight **517 ms**, lag **103 ms**; at EV 2.5, **775 ms**, lag **155 ms**. KR 85 on the Lantern in daylight: **320 ms**, lag **64 ms**.

### F11. Autofocus zone

The af_zone formula is defined as:

`in_zone = abs(x_bp) ≤ AF_ZONE_BP[af_class] and abs(y_bp) ≤ AF_ZONE_BP[af_class]`  (phone in any mode: always true while `in_frame`)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| x_bp, y_bp | int (bp of frame width / height) | −5000 to 5000 inside the frame | calculated (F15) | Subject position from the frame centre |
| af_class | int | 1–5 | data file (body) | Body AF class |
| AF_ZONE_BP | map int → int | 1000–5000; defaults 1: 1200, 2: 1800, 3: 2400, 4: 3000, 5: 3600 | data file | Zone half-size |
| in_zone | bool | — | calculated | Subject can be picked automatically |

**Output Range:** true or false. Every MVP body reaches the rule-of-thirds lines at ±1,667 bp, so composing on a third never needs a focus lock (Pillar 1: composition is not gated by gear). A better class widens the zone; focus lock reaches anywhere.
**Example:** Hearth (class 2, 1,800): a subject at `x_bp` 1,667 is **in**; at 2,000 it is **out**, and the player locks focus and recomposes. Lantern (class 3, 2,400): 2,000 is **in**.

### F12. Zoom step

The zoom_step formula is defined as:

`f_next = clamp(rdiv(f_deci × ZOOM_NOTCH_PERMILLE, 1000), f_min_deci, f_max_deci)` (zoom in);  `f_next = clamp(rdiv(f_deci × 1000, ZOOM_NOTCH_PERMILLE), f_min_deci, f_max_deci)` (zoom out)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| f_deci | int (deci-mm) | lens range | client state | Current focal length; for phone digital zoom the same rule runs on `zoom_milli` |
| ZOOM_NOTCH_PERMILLE | int (‰) | 1020–1150; default 1060 | data file | Ratio per notch |
| ZOOM_HOLD_NOTCHES_PER_S | int | 8–40; default 20 | data file | Notches per second on a held key, applied in fractions per render frame and rounded to integer `f_deci` |
| f_next | int (deci-mm) | lens range | calculated | New focal length |

**Output Range:** always inside the lens range. The full range of the widest MVP zoom (100–300) takes 19 notches, about 0.95 s held.
**Example:** kit zoom at 300: rdiv(318,000, 1000) = **318** (31.8 mm). At 440: 466 → clamped to **450**.

### F13. Handheld shake

The shake formula is defined as:

`t_safe_us = floordiv(t_hand_us × 1000, 1000 + floordiv(SHAKE_MOVE_PERMILLE × speed_mm_s, 1000))`;  `shake_bp = (t_us ≤ t_safe_us) ? 0 : rdiv(SHAKE_BASE_BP × t_us, t_safe_us)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t_hand_us | int (µs) | 2,222–5,333,333 | Gear F8 | Reciprocal-rule limit with stabilisation |
| speed_mm_s | int (mm/s) | 0–1,200 in the viewfinder (Movement: Walk × 0.40) | capture pose body speed, floored at the boundary | Body speed at the press |
| SHAKE_MOVE_PERMILLE | int (‰ per m/s) | 500–3000; default 1500 | data file | How much moving shortens the safe time |
| SHAKE_BASE_BP | int (bp) | 4–20; default 8 | data file | Blur at the limit, set to the circle of confusion as a share of frame width (8.3 bp) |
| t_us | int (µs) | body range | resolved setting | Shutter speed |
| t_safe_us | int (µs) | ≥ 0 | calculated | Safe time now |
| shake_bp | int (bp of frame width) | 0–about 3,000 | calculated | Whole-frame blur length; the render's direction is `mod(capture_ms, 16)` on Subject's `DIR16` table |

**Output Range:** 0 at or below the safe time, then proportional to `t_us`. The steadiness readout: *steady* when `t_us ≤ t_safe_us`, *soft* up to 2 × `t_safe_us`, *shaky* above. The body's speed is taken from the capture pose, which Movement records (Movement Edge Cases: shooting while moving is allowed).
**Example:** KR 50 on the Hearth, `t_hand_us` 13,333, standing still at 1/30 s (33,333): rdiv(266,664, 13,333) = **20 bp**. Walking in the viewfinder at 1,200 mm/s: `t_safe_us` = floordiv(13,333,000, 2,800) = 4,761; at 1/125 s (8,000): rdiv(64,000, 4,761) = **13 bp**.

### F14. Subject motion blur

The subject_motion formula is defined as:

`v = (pos(capture_ms) − pos(capture_ms − BLUR_SAMPLE_MS)) × 1000 / BLUR_SAMPLE_MS` (per axis, floordiv);  `r` = subject − eye (mm);  `v_perp = isqrt(max(0, v·v − floordiv((v·r)², r·r)))`;  `motion_bp = rdiv(v_perp × t_us × f_eq_mm, d_mm × 3,600)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| pos | function (mm, ×3) | zone space | Subject F8, F9 (journal and schedule) | Subject position at a time |
| BLUR_SAMPLE_MS | int (ms) | 50–200; default 100 | data file | Backward sampling gap, so the server needs no future state |
| v | int ×3 (mm/s) | ±4,000 | calculated | Subject velocity |
| r | int ×3 (mm) | length up to 700,000 (keeps `(v·r)²` inside signed 64-bit) | calculated | Eye to subject |
| v_perp | int (mm/s) | 0–4,000 | calculated | Speed across the frame |
| t_us | int (µs) | body range | resolved setting | Shutter speed |
| f_eq_mm | int (mm) | 12–450 | Gear F2 | Equivalent focal length |
| d_mm | int (mm) | ≥ 1 | calculated (F7) | Distance; if `d_mm` < 1 the value is treated as 1 |
| motion_bp | int (bp of frame width) | 0–about 5,000 (capped at 5,000) | calculated | Smear length of the subject |

**Output Range:** 0 for a still subject. Typical drift (100–420 mm/s) at 1/60 s stays below about 45 bp across MVP lenses. That is why 1/60 s is the auto floor, and why a player with a long lens gains from `MANUAL`. The factor 3,600 is 36 mm × 10⁶ µs/s ÷ 10⁴ bp.
**Example:** Driftfin crossing at 420 mm/s, 8 m away, kit zoom at 45 mm on the Hearth (`f_eq_mm` 68), 1/60 s: 420 × 16,667 × 68 / (8,000 × 3,600) = 476,009,520 / 28,800,000 → **17 bp**; at 1/250 s, **4 bp**. KR 100–300 at 450 mm equivalent, 20 m, 1/60 s: **44 bp**; at 1/250 s, **11 bp**.

### F15. Frame position

The frame_position formula is defined as (float; the only float evaluation in this system):

`w = subject − eye;  zc = w · fwd;  x_bp = 10,000 × (w · right) × f_eq_real / (zc × 36);  y_bp = 10,000 × (w · up) × f_eq_real / (zc × 24);  in_frame = zc > 0 and abs(x_bp) ≤ 5,000 and abs(y_bp) ≤ 5,000`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| subject, eye | float ×3 (mm) | zone space | SubjectSnapshot; capture pose | Positions |
| fwd, right, up | float ×3 (unit) | — | calculated (capture pose yaw, pitch; roll 0) | Camera axes |
| f_eq_real | float (mm) | 12–450 | Gear F3 | Unrounded equivalent focal length |
| zc | float (mm) | any | calculated | Depth along the look |
| x_bp, y_bp | int (rounded half up) | any | calculated | Position from frame centre as a share of frame width and height |
| in_frame | bool | — | calculated | Subject centre is in the 3:2 frame |

**Output Range:** ±5,000 inside the frame. World Core Rule 10 allows float trig downstream if the consumer owns its tolerance: this runs only on the server for gameplay, and Photo Scoring owns any tolerance at frame edges and the use of `BOUNDS_MM` for partial framing.
**Example:** 75 mm equivalent, subject 8 m ahead and 1 m to the right: 10,000 × 1,000 × 75 / (8,000 × 36) = **2,604**, a quarter of the frame width right of centre.

### F16. Night stack eligibility

The night_ok formula is defined as:

`night_ok = (phone_mode = NIGHT) and (capture_ms − still_since_ms ≥ NIGHT_MODE_HOLD_MS) and (no in-frame subject, or isqrt(|pos(capture_ms) − pos(capture_ms − NIGHT_MODE_HOLD_MS)|²) ≤ NIGHT_MODE_DRIFT_MM)`;  `gain_t = night_ok ? NIGHT_MODE_STOPS × 3 : 0`;  `night_applied = night_ok`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| still_since_ms | int (ms) | server time | calculated (server, per player; reset on any accepted `MOVE` that moves more than `NIGHT_STILL_MM` or turns more than `NIGHT_STILL_DECI` since the last) | One integer per player, so no long history is needed (Network's buffer holds 14 ticks) |
| NIGHT_MODE_HOLD_MS | int (ms) | 1000–4000; default 2000 | data file (Gear) | Hold time |
| NIGHT_MODE_DRIFT_MM | int (mm) | 50–500; proposed default 150 | data file (Gear; no value set there yet) | Subject drift allowed |
| NIGHT_STILL_MM, NIGHT_STILL_DECI | int | 20–200 mm; 5–50 (0.1°); defaults 50, 10 | data file | Camera stillness limits |
| pos | function (mm) | — | Subject F9 | Position of the in-frame subject nearest the frame centre |
| night_ok | bool | — | calculated | Stack succeeds |

**Output Range:** true or false. With defaults the still Hearth Echo qualifies and a Mossmote does not, matching Gear's *"holds still scenes"* and *"a moving subject ends the stack"*. A failed stack is an ordinary exposure.
**Example:** player still for 2,400 ms; a Hearth Echo moved 0 mm → **true**, `gain_t` 9. A Mossmote moved 340 mm → **false**, `gain_t` 0.

### F17. Frame interval and burst

The frame_interval formula is defined as:

`frame_interval_ms = max(ceil_div(10,000, burst_deci), ceil_div(1000, SHUTTER_RATE_CAP))`;  `fire_gap_ms = max(frame_interval_ms × throttle_factor, ceil_div(t_us, 1000))`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| burst_deci | int (0.1 fps) | 5–200 | data file (body or phone) | Burst rate |
| SHUTTER_RATE_CAP | int (/s) | 2–15; default 10 | config (Network F1b) | Server rate ceiling |
| throttle_factor | int | 1, or 2 while `Throttled` | Network `NOTICE throttled` | Halves the rate as Network Rule 36 does |
| t_us | int (µs) | body range | current setting | Shutter speed |
| frame_interval_ms | int (ms) | 67–2,000 | calculated | Gap between frames |
| fire_gap_ms | int (ms) | 67–30,000 | calculated | Gap until the next press can fire |

**Output Range:** the send rate is at most `1000 / frame_interval_ms`, which never exceeds Network's `RATE_shutter` (`min(cap, 1.25 × fps)`), so a normal client never drains the bucket. The `SHUTTER_BURST` of 5 absorbs network jitter.
**Example:** phone (30): **334 ms**. Hearth (50): **200 ms**. Lantern (80): **125 ms**. Kestrel (120): max(84, 100) = **100 ms**, so the Kestrel's real rate is 10 fps, not its listed 12 (Open Question 8).

### F18. Frame allowance

The frame_allowance formula is defined as:

`n = floordiv(now_ms − frames_ts_ms, FRAME_REFILL_MS)`;  `frames_now = min(FRAME_CAP, frames_prev + n)`;  `frames_ts_ms' = (frames_now = FRAME_CAP) ? now_ms : frames_ts_ms + n × FRAME_REFILL_MS`;  on an accepted shot `frames_prev' = frames_now − 1`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| now_ms | int (ms) | ≥ 0 | server UTC | Current time |
| frames_prev, frames_ts_ms | int | 0–`FRAME_CAP`; ms | Accounts (per account) | Stored count and last refill mark |
| FRAME_CAP | int | 12–120; default 36 | data file | Frames held |
| FRAME_REFILL_MS | int (ms) | 5,000–120,000; default 30,000 | data file | Time per returned frame |
| frames_now | int | 0–`FRAME_CAP` | calculated | Frames available |

**Output Range:** 0 to `FRAME_CAP`, computed lazily, so no timer runs. A full roll returns in 18 minutes. Over a 63-minute world day a player can shoot at most 36 + 126 = **162** frames. New accounts start at `FRAME_CAP`.
**Example:** 20 frames left, `frames_ts_ms` 95 s ago: `n` = 3, `frames_now` = **23**, mark moves forward 90 s, so the spare 5 s is kept.

### F19. Shutter presence

The shutter_presence formula is defined as:

`event_bonus_shutter = SHUTTER_PRESENCE_M[shutter_sound_id]`, added to Movement F4's `event_bonus` for 0.5 s; a new shutter event from the same player replaces the old one and restarts the 0.5 s

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| shutter_sound_id | enum | `ML_SOFT`, `ML_LEAF`, `PHONE_SYNTH` | data file (body or phone) | Which shutter the device has |
| SHUTTER_PRESENCE_M | map (m) | 0–4; defaults `ML_SOFT` 1.5, `ML_LEAF` 0.8, `PHONE_SYNTH` 0.5 | data file | Presence added |
| event_bonus_shutter | float (m) | 0–4 | calculated (server) | Added to `presence_raw` |

**Output Range:** 0–4 m, inside Movement's 0–8 event range, and it is not scaled by surface.
**Example:** sneaking on grass, still, in the viewfinder: presence 0.4 m + 1.5 = **1.9 m**. A Puffwisp (`SENSE_PCT` 100) at 3 m: `reach_cm` 190 < 300, so intrusion is negative and it does not stir, satisfying Subject criterion 34. A Halo Keeper (`SENSE_PCT` 180) at 3 m: reach 342, intrusion 42, +2 alarm per tick for 0.5 s: noticed, not startled.

### F20. Preview blur radius

The preview_blur formula is defined as (float; client presentation only):

`blur_radius_px = min(PREVIEW_BLUR_MAX_PX, defocus_bp(pixel depth) × frame_width_px / 20,000)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| defocus_bp | float (bp) | 0–3,000 | F8 per pixel, from linearised depth | Blur disc diameter |
| frame_width_px | int (px) | 640–3840 | client | Width of the 3:2 frame on screen |
| PREVIEW_BLUR_MAX_PX | float (px) | 6–32; default 14 (prototype value) | data file | Largest blur the tap count can draw without visible gaps |
| blur_radius_px | float (px) | 0–`PREVIEW_BLUR_MAX_PX` | calculated | Radius used by the post effect |

**Output Range:** true to F8 up to the cap. Above the cap the preview understates blur: a preview is allowed to be softer in degree, never different in what is sharp. The re-render has its own higher cap (`RENDER_BLUR_MAX_PX`, UNVERIFIED cost).
**Example:** 1,280 px frame. 39 bp → **2.5 px**. KR 85 at f/1.4 and 749 bp → 47.9 px → capped at **14 px** in the preview.

### F21. Preview exposure gain

The preview_gain formula is defined as (float; client presentation only):

`e = clamp(exposure_err_deci × (phone ? PHONE_TONE_PERMILLE : 1000) / 1000, −PREVIEW_EV_CLAMP, PREVIEW_EV_CLAMP);  preview_gain = 2 ^ (e / 10)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| exposure_err_deci | int (0.1 EV) | −100 to 100 | F4 evaluated on the client | Predicted error |
| PHONE_TONE_PERMILLE | int (‰) | 300–1000; default 600 | data file | Phone's flatter tone, used by preview and re-render alike |
| PREVIEW_EV_CLAMP | int (0.1 EV) | 20–50; default 30 | data file | Matches the HUD's ±3 scale; a framing view never goes fully black or white |
| preview_gain | float | 0.125–8 | calculated | Multiplier on the rendered image |

**Output Range:** 1.0 at a correct exposure, because World's presets are authored to look right at that point. The re-render uses the same formula and clamp, so preview and photo agree.
**Example:** error −11 on a camera: 2^(−1.1) = **0.47**. On a phone: −6.6 → 2^(−0.66) = **0.63**.

## Edge Cases

**Exposure and settings**

- **If a scene is brighter than the settings can handle** (f/1.4 in `APERTURE` at noon on a 1/4000 s body): the solver stops at the fastest shutter and ISO `iso_min`; `exposure_err_deci` stays positive; the HUD shows "too bright for this aperture". There are no filters in MVP.
- **If a scene is darker than the settings can reach**: ISO stops at `iso_max`, the shutter stops at `tv_floor`, and the error stays negative. The shot is allowed and comes out dark.
- **If the player zooms a variable-aperture lens in while wide open**: the aperture stops down by Gear F4; the set aperture stays stopped down when zooming out in `APERTURE` and `MANUAL` (Gear Edge Cases). In `AUTO` the solver re-chooses it.
- **If a lens's maximum aperture is not on `THIRD_STOPS`** (the dormant `lens_std80_f19_sss_01` is f/1.9): this cannot occur in MVP (`enabled_cap` A, never minted). It must be resolved before that lens is enabled (Open Question 9).
- **If the light changes between the client's prediction and `capture_ms`** (weather reaches its 500‰ switch during the rewind): automatic values are solved at `capture_ms`, so the shot is correct for the true instant, and the HUD's last value may differ by up to that weather change (at most 4 EV, CLEAR to RAIN) for that one shot. `MANUAL` settings are kept, and the error reflects the true light.
- **If a shot is taken in `MANUAL` and the meter is off the ±3 scale**: the scale pins at its end with an arrow; the shutter still fires.
- **If compensation is set and the program changes to `MANUAL`**: the compensation value is kept and ignored, returning when the program changes back.
- **If the phone's assist and player compensation both apply**: they add (F5). A phone player can over-correct.
- **If a photographable interior is added**: `scene_ev_deci`, key light and condition come from zone data (World Rule 15). F3 applies unchanged. MVP interiors are not photographable.
- **If camera bearing is exactly opposite the sun**: `backlit_permille` is 0.

**Focus**

- **If the shutter is pressed during `AF_SEEK`**: the shot fires at once with the current `focus_mm` (Rule 25).
- **If a subject moves after focus locks**: the server measures `d_mm` at `capture_ms`, and `defocus_bp` reports the miss.
- **If several subjects are in the AF zone**: the one nearest the frame centre wins; on a tie, the nearer in depth; then the lower `appearance_id`.
- **If nothing is hit by the focus ray** (open sky): focus goes to `FOCUS_INF_MM`.
- **If a subject is farther than `FOCUS_INF_MM`**: `d_mm` is capped there for F8, and `in_dof` is evaluated normally. MVP anchors are within 40 m (Subject `ANCHOR_MAX_SHOT_M`).
- **If a subject is nearer than `mfd_mm`**: focus stops at `mfd_mm`; "too close" shows; the shot is allowed and soft.
- **If the eye and a subject share a position**: `d_mm` is treated as 1 (F14, F8), and `zc` ≤ 0 gives `in_frame` false (F15).
- **If a manual lens is on any program**: autofocus input does nothing and the ring is the active dial. Exposure programs are unaffected.
- **If `focus_mm` from a client is exactly the subject's distance every time**: it is accepted, as settings are client-chosen (Network authority table). The risk is logged (Open Question 3).
- **If a lens's `mfd_mm` is not greater than its focal length**: F8's denominator could reach 0. Catalog CI must reject it (Open Question 9). No MVP model does this.
- **If a teammate stands in the frame**: they are ignored by AF, drawn ghosted, and absent from the photo (Movement R20).

**Shutter, frames and network**

- **If the shutter is pressed during the raise**: nothing happens and the press is not buffered (Movement Edge Cases).
- **If `frames_now` is 0**: the press does nothing except a soft "no frames" click; the HUD shows when the next frame returns. The viewfinder stays fully usable. No server message is sent.
- **If a client sends a `SHUTTER` with no frames left**: the server refuses it in `SHUTTER_RESULT` with reason `no_frames`, nothing is scored or rolled, and no violation is added, because a client's prediction can honestly lag.
- **If a server rejects a shot on Movement R18 or Network Rule 25**: no frame is spent; the client restores its prediction.
- **If a `SHUTTER` is retried with the same `rid`**: the stored result returns and no second frame is spent (Network Rule 21).
- **If `ERR_SERVER_BUSY` is returned**: the frame is not spent until the retry is accepted. The moment is preserved (Network Edge Cases).
- **If the connection drops after the press and `RESULT_QUERY` returns "unknown `rid`"**: the frozen frame shows "not sent", the predicted frame is restored, and the shot is never shown as taken (Network Edge Cases).
- **If the session is not `Synced`**: state is `Paused`; the preview stays live; the shutter does nothing.
- **If the meta service is down**: `saved: false` carries no result; the frame stays spent because the shot was accepted, and the photo is committed later from the outbox. If the outbox is full, `ERR_SERVICE_DEGRADED` refuses shots and no frame is spent.
- **If a crash loses validated but uncommitted shots**: their frame spends are lost with them, because frames commit with the photo.
- **If a burst runs out of frames**: it stops at the last frame.
- **If `can_shoot` goes false mid-burst** (forced lower, lock loss): the burst stops at once. Frames already fired stand.
- **If the player is `Throttled`**: `throttle_factor` doubles the interval, so an honest client stays within the halved rate.
- **If a player mashes the shutter faster than `fire_gap_ms`**: extra presses are ignored locally and do not queue.
- **If the player lowers the camera during a long exposure**: the shot stands, and the state returns to `Stowed` after `t_us`. The shutter is unavailable until then.
- **If the player presses the shutter while walking**: the shot is allowed (Movement D11), and `t_safe_us` shrinks (F13).
- **If `Airborne` force-lowers the viewfinder** (Movement): the device goes to `Stowed`; any held burst stops.
- **If pointer lock is lost in the viewfinder**: mouse shutter is disabled (Movement R13), and dials stop until focus returns. Keyboard shutter follows Movement's rule.

**Phone**

- **If `NIGHT` is selected and the player moves**: the ring resets to 0, and the next shot is a normal exposure if pressed before it refills.
- **If the ring looks full but the server disagrees** (a `MOVE` the client did not count as motion): the server's result stands, and the shot is a normal exposure. The darkroom says so in plain words.
- **If `PORTRAIT` has no subject in frame**: `portrait_applied` is false, a normal AUTO shot.
- **If digital zoom is above 1000 and the module switches**: it resets to 1000.
- **If a phone holds `focus_mm` from a tap and the subject moves**: focus stays where it was tapped, as on a real phone tap, until the next tap.

**Degenerate strategies**

- **Spraying bursts at every decisive pose for extra rolls**: bounded by the frame allowance (36 frames is 4.5 s of Lantern burst) and by Capture Tier Resolution's burst rule (Decision D13). Without one of these, burst would turn timing into volume.
- **f/22 everywhere so everything is sharp**: legal, and it costs light: slower shutters, more ISO and no separation. Photo Scoring must reward subject separation or Focus becomes trivial (Open Question 2).
- **Staying in `AUTO` forever**: intended to be viable. Its limit is a fixed aperture preference and a 1/60 s floor, so it cannot produce shallow depth or freeze fast motion on purpose. The dominance check is that `MANUAL` has a clear win (freezing a long-lens subject, F14) and a clear cost (attention, risk of error), and that `AUTO` has the mirror of both.
- **Using `MANUAL` values copied from a chart**: fine. Light changes across the day and with weather, so copied values stop working, which teaches reading the light.
- **Waiting at full frames for rare subjects only**: frames cap at 36, so saving beyond that gives nothing, and waiting is a valid cozy play style.
- **Raising and lowering to reset autofocus**: gives nothing, because AF seeks on its own.
- **Holding still in `NIGHT` mode for free light on everything**: only still subjects benefit (F16); the moving spirits at night stay hard, keeping the camera's niche.
- **Shooting with a quiet body to avoid presence**: an intended side-grade. Fujin's leaf shutter is a real reason to own it, and it does not affect the gear ceiling.

## Dependencies

**Upstream (this system depends on):**

| System | Hard / soft | Interface | GDD status |
|---|---|---|---|
| Player Movement & Exploration | Hard | eye anchor, look, view state, `can_shoot`, capture pose, presence channel | Designed |
| Gear Catalog & Specs | Hard | specs, Rule 19 ranges, F1–F6, F8, F10, F13, phone modes | Designed |
| World Time, Weather & Light | Hard | `scene_ev_deci`, condition, key light, WorldSnapshot | Designed |
| Network Transport & Server Authority | Hard | `SHUTTER`, `capture_tick`, session state, rate limit | Designed |
| Subject & Spirit Behaviour | Hard | SubjectSnapshots, `pos` function, `BOUNDS_MM`, lens-only rule | Designed |
| Inventory & Loadout | Hard | server loadout | Not started |
| Accounts & Server Persistence | Soft | stores `frames_prev`, `frames_ts_ms` with the photo commit | Designed (does not list this yet) |
| Rarity Tier Ladder | None | This system reads no tier; `enabled_cap` acts only through which gear exists | Designed |

Systems index row 8 lists Movement, Gear and World. This draft adds Network and Subject as design dependencies (Open Question 10; not edited here, as instructed).

**Downstream (systems that depend on this one):**

| System | Hard / soft | Interface | GDD status |
|---|---|---|---|
| Photo Recipe & Re-render | Hard | `ShotSettings`, resolved values, re-render inputs | Not started |
| Photo Scoring | Hard | `ShotEvaluation` | Not started |
| Viewfinder HUD | Hard | readouts, states, dial model | Not started |
| Capture Encounter | Hard | shutter gate and programs, unchanged | Not started |
| Onboarding & Tutorial (VS) | Hard | teaching order | Not started |
| Audio: SFX & Ambience (VS) | Soft | events | Not started |
| Co-op Crew Roles (Alpha) | Soft | tripod and long-exposure hooks | Not started |
| Capture Tier Resolution | Soft | `burst_id` | Not started |
| Network Transport & Server Authority | Soft | `validate_settings`, `frames_left` | Designed (lists this system) |

Bidirectional note: Movement, Gear, World, Network and Subject already list Camera Model. Accounts does not yet. Every other downstream GDD must list "depends on Camera Model" when it is authored.

## Tuning Knobs

All values live in data (proposed `assets/data/camera/camera_model.json`; path → gameplay-programmer). Knobs in `NIGHT_MODE_*`, `T_SUBJECT_US` and `STAB_CAP` stay in Gear's data. Categories: **Feel** (playtest), **Curve** (maths), **Gate** (pacing).

| Knob | Default | Safe range | Category | Affects | Too low / too high |
|---|---|---|---|---|---|
| `AUTO_AV_T` | 15 (f/5.6) | 12–18 | Curve | `AUTO`'s depth and speed | Low: thin focus for new players. High: `AUTO` hits ISO early |
| `COND_COMP` | see F3 | −15–15 each | Curve | How much each light fools the meter | Near 0: compensation is pointless. Large: `AUTO` feels broken |
| `BACKLIT_COMP` | DAWN 7, MIDDAY 7, GOLDEN 10 | 0–20 | Curve | Reward for reading low sun | 0: no light reading. High: every sunset is a chore |
| `BACKLIT_ARC_DECI` | 450 | 200–900 | Curve | How often backlight applies | Low: rare. High: applies to side light |
| `IDEAL_COMP_MAX` | 20 | 10–30 | Curve | Limit of required compensation | Must stay under the ±3 EV dial |
| `PHONE_SCENE_ASSIST_PERMILLE` | 500 | 0–1000 | Curve | How easy the phone is | 0: no phone advantage. 1000: the phone beats a body in tricky light, so the camera loses honesty as a reward |
| `NOISE_PER_THIRD_PERMILLE` | 60 | 30–120 | Curve | Cost of high ISO | Low: ISO is free. High: `iso_clean` is a hard wall |
| `SHAKE_BASE_BP` | 8 | 4–20 | Curve | Blur past the handheld limit | Tied to the circle of confusion (F13) |
| `SHAKE_MOVE_PERMILLE` | 1500 | 500–3000 | Curve | Cost of shooting on the move | Low: walking is free. High: every moving shot is soft |
| `BLUR_SAMPLE_MS` | 100 | 50–200 | Curve | Velocity sampling | Low: noisy on tick rounding. High: misses sudden moves |
| `AF_ZONE_BP` | 1200 / 1800 / 2400 / 3000 / 3600 | 1000–5000 | Curve | Focus convenience per AF class | Class 2 under 1,667 gates thirds behind focus lock, against Pillar 1 |
| `AF_DARK_EV_DECI` / `AF_DARK_PERMILLE` | 30 / 1500 | 0–60 / 1000–2000 | Feel | Slower focus in the dark | Must keep `af_eff_ms` under anticipation + decisive windows |
| `TRACK_LAG_PERMILLE` | 200 | 50–500 | Feel | Tracking accuracy on moving subjects | High: fast primes feel unreliable on drift |
| `AF_RETARGET_PERMILLE` | 150 | 50–400 | Feel | How easily AF re-seeks | Low: focus breathes constantly. High: AF sticks on the wrong plane |
| `FOCUS_RING_STEPS` | 400 | 200–800 | Feel | Manual focus resolution | Low: steps skip the depth of field (F9). High: slow |
| `ZOOM_NOTCH_PERMILLE` / `ZOOM_HOLD_NOTCHES_PER_S` | 1060 / 20 | see F12 | Feel | Zoom speed | Low: slow. High: hard to frame precisely |
| `LENS_REVEAL_PERMILLE` | 500 | 0–1000 | Feel | When spirits appear in the raise | Low: visible in third-person blend. High: late pop |
| `FRAME_CAP` | 36 | 12–120 | Gate | Frames in hand | Low: tension, not cozy. High: no choice left |
| `FRAME_REFILL_MS` | 30,000 | 5,000–120,000 | Gate | Sustained shooting rate, photo income, server load | Low: limit disappears. High: players run out in a session |
| `BURST_MAX_FRAMES` | 12 | 3–30 | Gate | Longest burst | High: one press empties the roll |
| `BURST_HOLD_MS` | 250 | 150–500 | Feel | Single shot versus burst | Low: accidental bursts spend frames. High: burst feels late |
| `LONG_EXPOSURE_US` | 1,000,000 | 250,000–2,000,000 | Feel | When the progress ring shows | — |
| `FREEZE_MS` | 120 | 60–300 | Feel | Frozen frame time | Low: no "got it". High: blocks the next frame of the moment |
| `SHUTTER_PRESENCE_M` | 1.5 / 0.8 / 0.5 | 0–4 | Curve | Cost of a loud shutter near subjects | High: breaks Subject criterion 34 |
| `NIGHT_MODE_DRIFT_MM` (proposed; belongs in Gear) | 150 | 50–500 | Curve | Which subjects `NIGHT` can hold | High: `NIGHT` works on drifting spirits, so the phone out-reaches A gear |
| `NIGHT_STILL_MM` / `NIGHT_STILL_DECI` | 50 / 10 | see F16 | Feel | How still is still | Low: the ring never fills on touch input |
| `PREVIEW_BLUR_MAX_PX` | 14 | 6–32 | Feel | Preview blur reach | High: visible tap gaps and cost |
| `PREVIEW_EV_CLAMP` | 30 | 20–50 | Feel | How dark or bright the live view may go | High: cannot frame |
| `PHONE_TONE_PERMILLE` | 600 | 300–1000 | Feel | Phone's flat look | Low: errors invisible on phone |
| `EXP_ERR_MAX` | 100 | 50–150 | Curve | Range sent to Scoring | — |

**Rationale for the defaults.** `tv_floor` uses Gear's `T_SUBJECT_US` so auto exposure lands exactly where Gear's low-light reach says it should: kit EV 5.2, KR 50 EV 2.9, KR 85 EV 0.9, phone EV 4.6 (1.6 in `NIGHT`). The day therefore reads as in World's table: the kit holds into early blue hour (EV 4–9) on clean ISO, and the KR 85 reaches night. `FRAME_CAP` 36 echoes a film roll. At a cadence of a shot every 30 s the player never runs out, and it is a shared default until Photo Pricing states what income a frame represents (Open Question 7).

**Not knobs:** the stop tables (F1) are fixed vocabulary. `ShotSettings` field meanings are versioned by Photo Recipe.

## Visual/Audio Requirements

(Required for Gameplay systems.) The art bible owns the look; these are this system's needs.

- **Lens-world grade** (art bible §2.1): contrast up one step, saturation up slightly at the centre, a soft vignette, Lumen glow on subjects. Phone: brighter, flatter, smaller vignette. Camera: true exposure, so a dark scene stays dark (A13).
- **One post pass.** Depth blur, exposure gain, grain, peaking, grade and vignette should share one full-screen pass to limit cost. Prototype finding (Chromium/WebGL 2, Godot 4.7.2, Compatibility): native `CameraAttributesPractical` depth of field does **not** work on this renderer, and a custom full-screen spatial shader **can** read `hint_depth_texture` and `hint_screen_texture`; a 17-tap disc blur shows a visible aperture blur. `textureLod` on the screen texture showed no blur. These are observed, not covered by `docs/engine-reference/godot/`.
- **Frame cost is not measured.** The blur's cost on a real low-end machine is unknown, and the prototype's 17 taps run at one quality level only (Open Question 1).
- **Shader standard conflict.** `.claude/rules/shader-code.md` forbids texture reads inside loops and asks for two-pass blur. The prototype samples in a loop, and a disc blur is not separable. The production shader needs a technical-artist decision (unrolled taps, or an approved exception).
- **UNVERIFIED engine claims** (not in the engine reference): mapping `vfov_deg` to `Camera3D.fov` with height kept fixed; a lens layer through the camera's cull mask; exposure gain in the post pass, or through `CameraAttributes`, on Compatibility; capturing the frozen frame on Web; glow on Compatibility (halo cards are the art bible's fallback); tele precision of the depth buffer at 450 mm equivalent, which affects `defocus_bp` per pixel.
- **Grain, shake and smear in photos.** Grain from `noise_permille`, seeded from `capture_ms`. Shake as a directional blur of `shake_bp`. Subject smear of `motion_bp` along the on-frame velocity, masked to the subject's bounds. All driven by recipe data (art bible P4). The mask approach and its cost belong to technical-artist.
- **Look tags** (`SWIRL_BOKEH`, `WARM_FLARE`, `SOFT_CORNERS`) modify the same post pass in the re-render and, if cost allows, in the preview.
- **Capture** (art bible §2.1): six-blade iris under 150 ms, one frame of slight white flash within flash-safety limits and removable by reduce-flashing (the iris stays). The red "live" dot goes out. No screen shake.
- **Audio** (owned by Audio: SFX & Ambience; requirements from here): per-body shutter sounds from `shutter_sound_id`, gentle, never aggressive; a soft third-stop dial click; a quiet focus confirmation at lock; a faint zoom ring sound; the raise rustle and −3 dB ambient duck belong to Movement. The shutter plays at the press, never waiting for the server (Network Visual/Audio). All cues have visual equivalents.

## Game Feel

- **Nothing waits for the network.** Zoom, focus, dials and preview respond within 1 frame (Network Game Feel). The shutter's sound, iris and freeze land within 1 frame of the press.
- **Dials click.** Each third stop is one audible, visible step. Holding a key repeats at about 8 steps per second after a 250 ms delay.
- **Focus is felt.** The gap between 517 ms and 320 ms (Gear Game Feel) must be noticeable on a subject that turns away. The brackets close at exactly `af_eff_ms`, with the focus confirmation sound on the same frame.
- **The phone is effortless.** One tap between modules, no dials to learn, a gentle filling ring for `NIGHT`.
- **Manual focus is calm.** Peaking and a ring scale, no timer.
- **Held breath.** Raising narrows the sound and the frame. Spirits appear partway through the raise, so the reveal is part of the gesture.
- **The press is decisive.** An instant spike, then straight back to calm (art bible §2.1). `FREEZE_MS` is long enough to register and short enough that the live view returns before a decisive pose has moved on.
- **Failure is gentle and readable.** A dark or soft photo is explained in the darkroom by Photo Scoring. A missed shot costs one frame, and frames return. Failure is frequent while learning, so recovery is fast (flow principle).
- **Reduced motion.** Cuts the raise blend (Movement) and removes the iris animation's scale change while keeping a clear capture cue.
- **Feel playtest checks:** "Did you ever lose a shot to the controls?"; "Could you tell why a shot came out dark before the darkroom told you?"; "Did the phone feel like a real choice?"; "Did you reach for compensation by yourself in golden hour?"; "Did frames ever make you feel punished, rather than careful?"

## UI Requirements

This system supplies data. Viewfinder HUD owns layout, and every item needs a ux-designer pass (art bible §7, not reviewed by UX).

- **Camera skin** (art bible §7.1, A13): corner brackets; optional rule-of-thirds grid; focus brackets that turn Lumen and close in at lock (shape as well as colour, art bible §7.6 item 4); a −3 to +3 exposure scale; a data strip with focal length (equivalent), f-number, shutter speed, ISO and frames left; the program letter; the active dial marked; the red "live" dot. No battery icon in MVP (Gear D12).
- **Phone skin:** rounded screen edge, circular shutter button, zoom pill (0.5×, 1×, 2×), a sun slider for compensation, a mode switch and frames left. No data strip.
- **Readouts supplied:** `f_eq_mm`, `n_deci`, `t_us`, `iso`, `comp_t`, program, active dial, focus state, `focus_mm` on the ring scale, meter position, predicted `frames_now`, time to next frame when at 0, steadiness state, noise marker, "crop mode" flag (Gear Edge Cases), `NIGHT` ring progress, Network's "Reconnecting, shutter paused".
- **Assist layer (toggle; proposal for art bible §7.6 item 1):** a plain hint that points the way to correct exposure without giving the amount ("It's bright behind them: try adding light"), from the sign of `ideal_comp_deci − comp`. On by default. The hint is computed from public data (world feed and the player's own look).
- **Depth-of-field bar:** near and far limits against the focus distance, used when blur is reduced (Rule 48) and always on the ring.
- **Subject tier badge and presence glyph** come from Subject & Spirit and Movement.
- **Never in the viewfinder:** a score, a tier prediction, an image tier or a "good shot" indicator. The result belongs to the darkroom, after commit.
- **Nothing UI is in a stored photo** (art bible P4).
- **Accessibility:** every state has a shape or text, not colour alone (noise marker, steadiness, focus lock). Data strip size is an open art-versus-readability conflict (art bible §7.6 item 3). All inputs remappable. No hover-only controls. Peaking colour must pass the colourblind check (art bible §4.7).
- **First use:** the Hearth and the phone both open in their simplest state, with one visible dial.

**UX Flag — Camera Model:** the viewfinder skins, dial model and assist layer need `/ux-design` specs (HUD) before UI epics are written.

## Cross-References

| Referenced document | What is used | Where |
|---|---|---|
| `design/gdd/game-concept.md`: Pillars, Photo evaluation, Capture rule | Pillars; Focus and Exposure parts measure "sharp where it matters" and "not too dark or too bright"; a fast lens helps blur and low light | Player Fantasy, Rules 14–15, 26 |
| `design/gdd/systems-index.md`: rows 8, 19; rationale | Scope; "simulates field of view, depth of field, exposure, autofocus, phone auto-modes" | Summary, Dependencies |
| `design/gdd/gear-catalog-specs.md`: Rules 9–11, 18–19; F1–F10, F13; D7, D11, D12, D16; Game Feel | Spec fields, phone modes, setting ranges and all reused formulas | Rules 3, 8, 11, 18, 35–36; F2, F5, F7, F8, F10 |
| `design/gdd/player-movement-exploration.md`: R10–R15, R18, R20–R21; F4, F6; D11–D13; Open Questions 1, 4 | Eye anchor, look, `can_shoot`, capture pose, presence events, input reservation, no sway | Rules 1, 4–6; F13, F19; D17, D19 |
| `design/gdd/world-time-weather-light.md`: Rules 9–12, 14–15; F5, F11, F12 | `scene_ev_deci`, condition, key light, feed, snapshot, determinism rule | Rules 13–14; F3, F4 |
| `design/gdd/network-transport-server-authority.md`: Rules 5–7, 20, 24–29, 36; F1, F1b, F8, F9; Game Feel; Edge Cases; Open Questions 2, 3 | Authority split, `SHUTTER`, reveal after commit, rate limit, pacing | Rules 30–32, 38, 40, 49–50; F16, F17 |
| `design/gdd/subject-spirit-behaviour.md`: Rules 6, 14–15, 28, 31–32; F4, F8, F9, F11; criterion 34; tuning table | Lens-only rule, gear never gates, subject positions and speeds, windows | Rules 2, 19, 22; F10, F14, F16, F19 |
| `design/gdd/rarity-tier-ladder.md`: Core Rule 8 | Gear is a ceiling; this system reads no tier | Dependencies |
| `design/art/art-bible.md`: A1, A6, A13, §2.1, §7.1, §7.6, §8.5, §8.9, P4 | Viewfinder skins, capture blink, lens world, depth-of-field risk, re-render rule | Rules 2, 5, 44–49; Visual/Audio; UI Requirements |
| `prototypes/aperture-concept/README.md`, `dof.gdshader` | Native DoF fails on Compatibility; 17-tap custom blur works on Web; cost not measured; first-click finding | Rule 45, F20, Visual/Audio |
| `.claude/rules/shader-code.md` | Blur and loop rules that conflict with the prototype | Visual/Audio |

## Acceptance Criteria

**Stop scale and exposure**

1. [Logic] **GIVEN** `THIRD_STOPS`, **WHEN** indices are read, **THEN** f/1.4 = 3, f/5.6 = 15, f/32 = 30, and every aperture value in the enabled catalog is on the list. `test_stop_scale_aperture_indices_match_nominal_stops`
2. [Logic] **GIVEN** `SHUTTER_STOPS` and `ISO_STOPS`, **WHEN** each catalog body's limits are looked up, **THEN** every limit is on its list. `test_stop_tables_cover_all_enabled_body_limits`
3. [Logic] **GIVEN** values 105 and −2, **WHEN** `thirds(105)` and `deci(−2)` are computed, **THEN** results are 32 and −7. `test_thirds_and_deci_round_as_specified`
4. [Logic] **GIVEN** f/4.5, 1/60 s, ISO 3200, **WHEN** F2 runs, **THEN** `cam_ev_t` = 16. `test_camera_ev_kit_reach_case_returns_16`
5. [Logic] **GIVEN** the F3 example, **WHEN** computed, **THEN** `backlit_permille` = 940 and `ideal_comp_deci` = 9. `test_ideal_comp_golden_backlit_returns_9`
6. [Logic] **GIVEN** OVERCAST_FOG facing the sun, **WHEN** F3 runs, **THEN** the backlit term adds 0. `test_ideal_comp_overcast_has_no_backlit_term`
7. [Logic] **GIVEN** `key_source = MOON` or `elev_deci ≤ 0`, **WHEN** F3 runs, **THEN** `backlit_permille` = 0. `test_backlit_zero_below_horizon_or_moon`
8. [Logic] **GIVEN** the F4 example, **WHEN** computed with compensation 0 and +3, **THEN** errors are −11 and −1. `test_exposure_error_comp_corrects_backlit_scene`
9. [Logic] **GIVEN** every condition, **WHEN** `ideal_comp_deci` is at its extreme, **THEN** `AUTO` with legal compensation brings `abs(exposure_err_deci)` to at most 4 in a scene inside the loadout's reach. `test_auto_reaches_correct_exposure_in_every_condition`
10. [Logic] **GIVEN** the F5 kit example, **WHEN** solved, **THEN** the result is f/4.5, 1/60 s, ISO 3200. `test_solver_kit_at_ev52_matches_gear_reach`
11. [Logic] **GIVEN** the F5 phone NIGHT example, **WHEN** solved, **THEN** the result is 1/60 s, ISO 800. `test_solver_phone_night_at_ev16_matches_gear_reach`
12. [Logic] **GIVEN** every enabled loadout and `scene_ev_deci` from −40 to 160, **WHEN** solved, **THEN** every result lies within `validate_settings`. `test_solver_output_always_legal_for_all_loadouts`
13. [Logic] **GIVEN** f/1.4 in `APERTURE` at `scene_ev_deci` 150 on a 1/4000 s body, **WHEN** solved, **THEN** `tv` = 36, `iso` = `iso_min`, and the error is positive. `test_solver_too_bright_keeps_positive_error`
14. [Logic] **GIVEN** ISO at or below `iso_clean`, **WHEN** F6 runs, **THEN** 0; at Hearth 12800, 360. `test_noise_zero_at_clean_and_360_at_hearth_max`

**Focus**

15. [Logic] **GIVEN** Gear F6's two examples, **WHEN** F7 runs, **THEN** results are 1,945 / 2,058 and 1,044 / 23,988. `test_dof_integer_matches_gear_examples`
16. [Logic] **GIVEN** `s_d ≥ H_d`, **WHEN** F7 runs, **THEN** `D_far_mm` = `DOF_INF`. `test_dof_far_infinite_at_hyperfocal`
17. [Logic] **GIVEN** the F8 example, **WHEN** computed, **THEN** 39 bp at 2,300 mm, 8 bp at 2,058 mm, 0 at the focus distance. `test_defocus_examples_and_zero_at_focus`
18. [Logic] **GIVEN** the KR 85 f/1.4 on the Lantern at focus 2,000 and a very far subject, **WHEN** F8 runs, **THEN** the value is within 3 bp of Gear F7's 749. `test_defocus_approaches_gear_blur_index`
19. [Logic] **GIVEN** the Hollin 58, **WHEN** F9 runs at `p` = 0, 200, 400, **THEN** 600, 1,199 and 1,000,000. `test_focus_ring_ends_and_midpoint`
20. [Logic] **GIVEN** `af_ms` 517, **WHEN** F10 runs at EV 5 and EV 2.5, **THEN** 517 and 775, with lags 103 and 155. `test_af_timing_dark_slowdown_and_lag`
21. [Logic] **GIVEN** every enabled body, **WHEN** F11 runs at `x_bp` = 1,667, **THEN** `in_zone` is true. `test_af_zone_reaches_thirds_on_all_bodies`
22. [Logic] **GIVEN** every enabled lens, **WHEN** the worst `af_eff_ms` is taken, **THEN** it is under the shortest anticipation + decisive window of any enabled species. `test_af_slowest_fits_shortest_window`
23. [Integration] **GIVEN** a target beyond the focus point and the shutter pressed during `AF_SEEK`, **WHEN** the shot is taken, **THEN** it fires on that frame with the current `focus_mm`, and the server's `defocus_bp` reflects the miss.
24. [Integration] **GIVEN** a spirit inside the AF zone and a ghosted teammate nearer the centre, **WHEN** AF picks a target, **THEN** it picks the spirit.

**Zoom, shake and motion**

25. [Logic] **GIVEN** the kit zoom at 300 and 440, **WHEN** F12 zooms in, **THEN** 318 and 450. `test_zoom_notch_multiplies_and_clamps`
26. [Logic] **GIVEN** a prime, **WHEN** zoom input arrives, **THEN** `f_deci` does not change. `test_prime_ignores_zoom_input`
27. [Logic] **GIVEN** the F13 examples, **WHEN** computed, **THEN** 20 bp still and 13 bp walking; at or below `t_safe_us`, 0. `test_shake_examples_and_zero_below_safe_time`
28. [Logic] **GIVEN** the F14 examples, **WHEN** computed, **THEN** 17, 4, 44 and 11 bp. `test_subject_motion_examples`
29. [Logic] **GIVEN** a subject moving directly toward the camera, **WHEN** F14 runs, **THEN** `motion_bp` = 0. `test_subject_motion_zero_for_radial_movement`
30. [Logic] **GIVEN** the F15 example, **WHEN** computed, **THEN** `x_bp` is 2,604 ± 1 and `in_frame` is true; a subject behind the camera is `in_frame` false. `test_frame_position_example_and_behind_camera`

**Shot flow, server and limits**

31. [Logic] **GIVEN** identical `ShotSettings`, pose and snapshots, **WHEN** `evaluate_shot` runs twice on two processes, **THEN** every integer output is identical, and no rendering API is called. `test_evaluate_shot_deterministic_headless`
32. [Logic] **GIVEN** a `SHUTTER` with a shutter value not on `SHUTTER_STOPS`, **WHEN** validated, **THEN** `ERR_OUT_OF_RANGE`, and no frame is spent. `test_validate_settings_rejects_off_list_shutter`
33. [Logic] **GIVEN** program `AUTO` and a client `t_us` field, **WHEN** the server resolves the shot, **THEN** the field is ignored and the solver's value is stored. `test_auto_program_ignores_client_exposure_fields`
34. [Logic] **GIVEN** the F16 examples, **WHEN** computed, **THEN** true for still with 0 mm drift, false with 340 mm drift, false below the hold time. `test_night_stack_eligibility_cases`
35. [Logic] **GIVEN** each MVP body, **WHEN** F17 runs, **THEN** 334, 200, 125 or 100 ms, and the send rate is at most Network's `RATE_shutter`. `test_frame_interval_never_exceeds_shutter_rate`
36. [Logic] **GIVEN** a 30-second burst at each body's interval against Network's F1 bucket, **WHEN** simulated, **THEN** no shot is rejected. `test_held_burst_never_rate_limited`
37. [Logic] **GIVEN** the F18 example, **WHEN** computed, **THEN** 23 frames with the mark advanced 90 s; at cap, the mark is `now_ms`. `test_frame_refill_lazy_and_cap`
38. [Logic] **GIVEN** a retry with the same `rid`, **WHEN** processed, **THEN** frames do not change. `test_frame_not_spent_twice_on_retry`
39. [Logic] **GIVEN** three shutter events within 0.5 s, **WHEN** presence is computed, **THEN** `event_bonus` from the shutter equals one event's value. `test_shutter_presence_refreshes_not_stacks`
40. [Integration] **GIVEN** Subject criterion 34's setup with `ML_SOFT`, **WHEN** one accepted shot fires, **THEN** the Puffwisp does not enter `WARY`.
41. [Integration] **GIVEN** the shutter pressed with `can_shoot` true, **WHEN** the frame fires, **THEN** iris, sound and freeze occur within 1 frame with the network disconnected at the socket level after the press.
42. [Integration] **GIVEN** a shot accepted while the meta service is down, **WHEN** `saved: false` arrives, **THEN** the client shows no score, tier or evaluation until `saved: true`, and one frame is spent.
43. [Integration] **GIVEN** a shot whose `RESULT_QUERY` returns "unknown `rid`", **WHEN** the client resumes, **THEN** the frozen frame shows "not sent", the frame count is restored, and no photo appears.
44. [Integration] **GIVEN** a solo player, **WHEN** a shot is taken, **THEN** the same server path as a crew runs in a 1-player session; with no session, the shutter does nothing.

**Preview and lens world**

45. [Integration] **GIVEN** a spirit near the player, **WHEN** the view changes from third person to the viewfinder and back, **THEN** it is drawn only in the viewfinder, on phone and camera alike, and at most the shimmer shows in third person.
46. [Integration] **GIVEN** a recipe from a shot in the Web export, **WHEN** it is re-rendered, **THEN** FOV and camera pose are identical, subject position differs by no more than Network's view tolerance allows, brightness matches within one third stop, and sharp regions match.
47. [Integration] **GIVEN** the Web export on the reference low-end device (to be defined), **WHEN** the viewfinder runs with blur at each quality level, **THEN** frame time is recorded, and the default level holds the project's frame budget. Screenshot and log retained.
48. [Integration] **GIVEN** a depth-blur quality of off, **WHEN** a photo is taken, **THEN** its re-render still shows full depth blur.

**UI**

49. [UI] **GIVEN** the camera in `AUTO`, **WHEN** the viewfinder is live, **THEN** the data strip, exposure scale and frames left are shown and the only dial offered is compensation. Screenshot retained.
50. [UI] **GIVEN** the phone, **WHEN** the viewfinder is live, **THEN** the phone skin shows no data strip, and shows the zoom pill, sun slider and frames left. Screenshot retained.
51. [UI] **GIVEN** focus lock reached, **WHEN** shown in greyscale, **THEN** lock is still readable by shape. Screenshot retained.
52. [UI] **GIVEN** a shot at any state, **WHEN** the viewfinder or frozen frame is on screen, **THEN** no score, tier or evaluation appears. Screenshot retained.
53. [UI] **GIVEN** `t_us` above `t_safe_us`, **WHEN** the readout shows, **THEN** steadiness reads soft or shaky, and the view itself does not shake. Screenshot retained.
54. [UI] **GIVEN** frames at 0, **WHEN** the shutter is pressed, **THEN** the HUD shows when the next frame returns, with no error styling. Screenshot retained.

**Experience (documented playtests)**

55. [Integration] **GIVEN** new players in the first playable, **WHEN** they play 15 minutes using only raise, zoom and shutter, **THEN** every player produces at least one photo they would keep, with no manual setting used (Decision D1).
56. [Integration] **GIVEN** players shown golden-hour backlight, **WHEN** they play 30 minutes, **THEN** most reach for compensation unprompted or say why a shot was dark (Rule 14).
57. [Integration] **GIVEN** the playtest question "Did you ever lose a shot to the controls?", **WHEN** asked after a session, **THEN** fewer than 1 in 5 players answer yes.
58. [Integration] **GIVEN** a 30-minute session, **WHEN** frames are logged, **THEN** fewer than 1 in 5 players reach 0 frames, and those who do do not describe the limit as punishing.

## Open Questions

> 2026-11-05 (Photo Recipe): `evaluate_shot` also outputs `motion_dir`; `exposure_err_deci` is read by re-render (F21); F20 names `RENDER_BLUR_CAP_BP`; confirm which subject `PORTRAIT` uses; NPCs are ghosted in the viewfinder and absent from photos in MVP.

| # | Question | Owner | Resolve by |
|---|---|---|---|
| 1 | Frame cost of the depth blur on real low-end hardware is unmeasured, and reference hardware is undefined (also Movement Open Question 7). Sets `PREVIEW_BLUR_MAX_PX`, tap count and fallback thresholds. | technical-artist + godot-shader-specialist | First spike, before implementation |
| 2 | Photo Scoring must set tolerances for `exposure_err_deci`, `defocus_bp`, `shake_bp`, `motion_bp`, `noise_permille`, and must reward subject separation, or f/22 dominates Focus. Recommended check: 25 bp as the point where `motion_bp` starts to read as soft. | systems-designer (Photo Scoring GDD) | Photo Scoring design |
| 3 | Settings are client-chosen (Network authority table), so a modified client can send a perfect `focus_mm` or perfect `MANUAL` exposure every time, bypassing focus and exposure skill. Is a server plausibility check needed, or is this an accepted risk? | security-engineer + game-designer | Before leaderboards (VS) |
| 4 | Does the shake direction, or a subject smear mask, cost too much in the re-render? Is an MVP photo acceptable without smear (HUD and score only)? | technical-artist | First spike |
| 5 | Tripod and long-exposure play for the Astro role: a stability hook on F13 (Gear Open Question 4), and whether MVP's handheld long exposures should remain offered at all. | game-designer (Co-op Crew Roles) | Alpha |
| 6 | Panning with a subject to reduce `motion_bp`: needs a look-rate field in the capture pose, which the server cannot verify. | game-designer | After first playtest |
| 7 | Economy link: `FRAME_CAP` and `FRAME_REFILL_MS` cap photo income at 162 frames per world day. The value must be set against the Currency & Wallet budget table. | economy-designer | Before the shared budget table is locked |
| 8 | **Gear Catalog requests:** (a) the Nokta Kestrel's 12 fps exceeds Network's `SHUTTER_RATE_CAP` of 10; raise the cap to 12 or list the Kestrel as 10 fps. (b) The Lumo Pebble table has no body `af_class`, which F10 needs; this draft assumes 3. (c) `NIGHT_MODE_DRIFT_MM` has no value in Gear; this draft proposes 150. (d) Gear F10 says "from half-press"; there is no half-press here (Rule 18). | economy-designer | Before Camera implementation |
| 9 | **Gear Catalog requests:** (a) dormant `lens_std80_f19_sss_01` is f/1.9, which is not on `THIRD_STOPS`, so Gear F4's claim and its edge case both fail for it; change it to f/1.8 or f/2, or add 19 to the list with a defined index. (b) Add a CI check that `mfd_mm` exceeds the longest focal length. | economy-designer | Before `enabled_cap` rises; CI check before implementation |
| 10 | **Network requests:** (a) `SHUTTER_RESULT` needs `frames_left` and a `no_frames` reason. (b) Rule 25 should name `validate_settings`, and automatic fields are server-derived (Rule 31). (c) `CAMERA_REACH_M` is 1.0 m, but a standing eye is 1.60 m above the capsule foot, so if "player position" is the foot, every standing shot fails. Compare against position + eye offset (Decision D18). (d) This resolves Network Open Questions 2 and 3. **Systems index:** add Network and Subject to row 8's "Depends On". | network-programmer + game-designer | Before Camera implementation |
| 11 | **Movement requests:** (a) F4 sums `event_bonus`, but shutter events must refresh, not stack (Rule 43). (b) The yaw convention must map to World's clockwise-from-north azimuth for F3. (c) Open Questions 1 and 4 are answered by Decisions D17 and D19. | gameplay-programmer | Before Camera implementation |
| 12 | **Accounts request:** add `frames_prev`, `frames_ts_ms` to the player record, written in the photo commit. | backend owner | Before Camera implementation |
| 13 | Registry: the stop tables, `ideal_comp`, `evaluate_shot` outputs and `FRAME_CAP` cross system boundaries and should be registered in `design/registry/entities.yaml` (not edited here). | game-designer, with user approval | After this GDD is approved |
| 14 | Prototype playtest is still NOT ASSESSED: no human has confirmed that a geometry-only score feels fair, or that framing with focal length, aperture and exposure feels like skill. This GDD rests on that hypothesis. | game-designer | First human playtest of `prototypes/aperture-concept` |

## Decisions to confirm

> **DECIDED 2026-11-05 (user):** every item = the recommended option; D12 confirmed: 36 frames, one back per 30 s.


- **D1. How much manual control a new player must use.** (a) **None: raise, frame, zoom and shoot works all game; compensation is the first optional dial, and aperture the second.** It keeps the cozy tone and makes Pillar 1 about seeing, not dial knowledge. (b) Compensation required from the start: a stronger exposure lesson, but a heavier first hour. (c) Everything manual after a tutorial: authentic, but gatekeeps the fantasy and makes the phone the only friendly choice. **Recommendation: (a).**
- **D2. Program model.** (a) **Three programs: `AUTO`, `APERTURE`, `MANUAL`.** Covers the prototype's dials with one clear step between each. (b) Two programs, `AUTO` and `MANUAL`: fewer modes, but a big jump, and background blur needs full manual. (c) Full PASM with shutter priority: familiar to photographers, more UI and more to balance. **Recommendation: (a).**
- **D3. Shutter speed and ISO in MVP.** (a) **Always simulated and recorded, shown as readouts, and dials only in `MANUAL`.** The specs, Network validation and Gear F8/F9 already need them. (b) Simulated but never player-set in MVP: less UI, but freezing motion has no player control, and `MANUAL` is removed. (c) Dials in every program: more control, more clutter. **Recommendation: (a).**
- **D4. What makes compensation matter.** (a) **The meter can be fooled: `ideal_comp_deci` from light condition and backlight, tuned to at most ±2 EV.** It turns reading the light into a skill and gives the phone's assist a purpose. (b) No bias: correct exposure is always the metered value, and compensation only adds taste, which can never help the Exposure part. (c) Subject-based metering with spot and matrix modes: richer, but needs more per-subject data and more UI. **Recommendation: (a).** The `COND_COMP` and `BACKLIT_COMP` numbers need a playtest.
- **D5. How noise is shown.** (a) **Fine grain in the live view and the photo, plus an ISO marker.** Honest and cheap. (b) In the photo only, with a HUD marker live: cheaper, but a surprise at the darkroom. (c) HUD only, no visible grain: cheapest, but a noisy photo looks clean. **Recommendation: (a),** with (b) as the fallback if the extra shader work costs too much.
- **D6. How motion blur and shake are shown.** (a) **A steadiness readout live, with real blur only in the photo.** A live image cannot honestly show a still's blur, and the art bible forbids screen shake. (b) Live sway in the viewfinder: readable, but breaks "no screen shake" and hurts precise framing. (c) Score only, with no visible blur in the photo: cheapest, but Pillar 2's "the photo shows what happened" weakens (see Open Question 4). **Recommendation: (a).**
- **D7. Must the preview exactly match the re-render?** (a) **Same facts, not same pixels: FOV, pose, exposure and what is sharp must match; blur amount may be capped and motion effects appear only in the photo.** Achievable, and honest to art bible P4. (b) Pixel-exact: strongest promise, but needs the preview at full re-render cost, unaffordable while frame cost is unknown. (c) Loose match: cheapest, but players stop trusting the viewfinder. **Recommendation: (a).**
- **D8. Autofocus input.** (a) **Continuous AF with a held focus lock.** There is no half-press on a mouse or keyboard, and a new player needs no focus input. (b) A hold-to-focus key: more deliberate, but one more thing to hold while framing. (c) Right-trigger style two-stage shutter on gamepad only: differs per device. **Recommendation: (a).**
- **D9. Shutter behaviour when focus has not locked.** (a) **Release priority: it always fires.** The controls never steal a moment. (b) Focus priority: fewer soft photos, but missed decisive poses feel unfair. (c) Focus priority on the phone only: friendly, but the phone would miss moments. **Recommendation: (a).**
- **D10. AF zone by body class.** (a) **Zone widens with class, and every MVP body reaches the thirds lines.** A real side-grade without gating composition. (b) One zone for all: simple, but AF class matters less. (c) Centre point only on low classes: real, but forces focus lock for every thirds composition on the starter body. **Recommendation: (a).**
- **D11. Manual focus aid.** (a) **Lumen peaking on sharp surfaces, plus a ring scale.** Calm and clear, and reads the same `D_near`/`D_far`. (b) A distance scale only: authentic but hard to judge on a screen. (c) A magnified focus inset: precise, but needs a second render. **Recommendation: (a).**
- **D12. Shot limit.** (a) **36 frames, returning one per 30 s of server time, with no battery.** Each press is a choice, rolls and photo income stay bounded, and there is no town trip. (b) No limit beyond Network's rate limit: simplest, but spraying becomes optimal and every shot costs a database commit. (c) A daily allowance: hard economy control, but it can end a session, which is not cozy. **Recommendation: (a).**
- **D13. Burst.** (a) **Hold to fire, one `SHUTTER` per frame, shared `burst_id`, up to 12 frames.** It answers Network Open Question 3 with no new message type. Capture Tier Resolution should then decide whether frames in one burst share a single roll. Recommended: yes, so that burst helps timing and not luck. (b) One message per burst, with N frames: fewer messages, but a larger message against the 512-byte cap and more server logic. (c) No burst in MVP: simplest, but makes `burst_deci` meaningless. **Recommendation: (a),** with one shared roll per burst.
- **D14. Phone `NIGHT` timing.** (a) **The stack comes from the preceding 2 s: a ring fills while still, and the capture is at the press.** Respects Movement R15 and Network F8 and never delays a moment. (b) Press, then hold for 2 s: more like a real phone, but the capture falls outside `MAX_REWIND_MS` and needs a new message flow. (c) Remove the hold: simplest, but makes `NIGHT` a free stop. **Recommendation: (a).**
- **D15. Phone assist strength.** (a) **500‰: the phone fixes half of a tricky scene.** Easy but not perfect. (b) 1000‰: fully automatic, so the camera is never better at exposure. (c) 0: the phone is no easier, and only its limits remain. **Recommendation: (a).**
- **D16. Who computes automatic settings.** (a) **The server solves them at `capture_ms`; the client sends only the program and compensation.** No claim to trust, a smaller message, always right for the true instant. (b) The client sends them and the server range-checks: closer to Network's table as written, but open to spoofed values and to mismatch at the capture instant. **Recommendation: (a).**
- **D17. Dutch tilt (Movement Open Question 1).** (a) **No roll in MVP.** One less input, and Composition stays simple. (b) A small roll limit (±15°): expressive, more UI and more Scoring work. **Recommendation: (a).**
- **D18. Camera position and reach (Network Open Question 2).** (a) **The camera is always the eye anchor; no held-out or overhead poses. Network compares against position plus eye offset, keeping `CAMERA_REACH_M` as tolerance.** (b) Allow arm's length: more angles, but it needs a new pose model and baked volume. **Recommendation: (a).**
- **D19. Phone raise time (Movement Open Question 4).** (a) **0.22 s for every device in MVP.** One constant; the phone's ease comes from its automation. (b) 0.15 s for the phone: a nice "always in the pocket" touch, at the cost of a per-device value in Movement. **Recommendation: (a).**
- **D20. Shutter sound and spirits.** (a) **A small, per-body presence event that refreshes rather than stacks.** Makes quiet bodies a side-grade, and Subject criterion 34 stays true. (b) No presence event: simpler, loses a stake and the Fujin's identity. (c) A loud event that startles: harsh, and against the cozy tone. **Recommendation: (a).**
- **D21. Long exposures in MVP.** (a) **Keep each body's full shutter range; handheld shake makes very long exposures poor, and a progress ring covers the wait.** Honours Gear Rule 19 with no extra rule. (b) Cap the dial at 1 s until tripods exist: tidier, but needs a second range in Network validation. **Recommendation: (a).**
