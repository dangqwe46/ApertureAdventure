# Audio: sound effects and music

## Sound effects (`sfx_synth.py`)
Presets: coin, pickup, jump, laser, shoot, explosion, hit, hurt, powerup,
select, confirm, cancel, click, footstep, whoosh, magic, error.

Map the spec's description to a preset, then tune with a recipe:

```json
{ "preset": "laser", "freq_start": 900, "freq_end": 120, "decay": 0.3,
  "lowpass_start": 5000, "lowpass_end": 800 }
```

Tuning cheatsheet:
- **Heavier / bigger** -> lower `freq_start`/`freq_end`, longer `decay`, more `punch`, lower `lowpass_end`.
- **Lighter / smaller / cuter** -> higher pitch, shorter `sustain`/`decay`, `triangle` or `sine`.
- **Retro / harsher** -> `square` with small `duty` (0.125-0.25) or `saw`.
- **Rising = positive** (pickups, power-ups, confirm); **falling = negative** (hurt, cancel, fail).
- **Impacts** = `noise` with a fast falling low-pass, plus a `sine` thump layer (see `hit`).
- **Magical / UI shimmer** -> `sine` + `vibrato_depth`, layered octave-up `triangle`.
- Always make 3-4 `--variants` for anything heard repeatedly (footsteps, hits, shots).

Naming per CCGS: `[category]_[context]_[name]_[variant].ogg`, e.g. `sfx_player_jump_01.ogg`.
Pass `--ogg` when ffmpeg is available (CCGS's `/asset-audit` expects OGG); otherwise
WAV is fine for Godot and Unity and the report must say OGG conversion did not run.

## Music (`music_synth.py`)
Loops are seamless: note tails past the end wrap to the start. Keep loops
8-32 bars; that is enough for menus, levels and stingers.

Writing a track:
1. Pick tempo and mood from the spec: menu 90-110 bpm, exploration 80-110,
   combat 130-160, puzzle 90-120, boss 140-170.
2. Choose a key and stay in it (A minor / C major are safe). Write the chord
   progression first in the `pad` track, then a `bass` following chord roots,
   then the `lead` melody using chord tones on strong beats, then `drums`.
3. Common progressions: i-VI-III-VII (Am-F-C-G) for adventure; I-V-vi-IV for
   upbeat; i-iv-v for tense; i-VI-iv-V for epic.
4. Use 2-3 sections (A, B, maybe a quieter C) and an `order` like A A B A.
5. Mix: bass 0.35-0.45, pad 0.12-0.2, lead 0.18-0.25, drums 0.4-0.5. Echo on
   the lead adds space cheaply.

Instrument keys: `wave` (square, saw, triangle, sine, noise), `duty`, `volume`,
`attack`, `decay`, `sustain_level`, `release`, `vibrato_depth`, `vibrato_rate`,
`detune` (chorus thickness, 0.003-0.008), `echo` {`time_steps`, `feedback`, `mix`},
or `"kind": "drums"`.

Full example: `examples/music_menu_loop.json`.

Limits: chiptune / synth character only. Orchestral, vocal, or realistic
instrument music is out of scope; say so and suggest CC0 libraries or a composer.
