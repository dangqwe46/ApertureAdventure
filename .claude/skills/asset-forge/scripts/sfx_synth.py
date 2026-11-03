#!/usr/bin/env python3
"""Retro / stylised sound effects synthesiser (sfxr-style) -> 16-bit mono WAV.

Pure Python standard library. Optional OGG conversion if ffmpeg is installed.

Usage:
    python3 sfx_synth.py --preset coin -o assets/audio/sfx/sfx_pickup_coin_01.wav
    python3 sfx_synth.py --preset jump --variants 3 --seed 4 -o assets/audio/sfx/sfx_player_jump.wav
    python3 sfx_synth.py --recipe my_sfx.json -o out.wav --ogg
    python3 sfx_synth.py --list

--variants N writes N slightly different takes named <name>_01.wav, _02.wav ...
(variation stops repeated sounds from feeling mechanical).

Recipe keys (any preset key can be overridden; start from one with "preset"):
  wave            square | saw | triangle | sine | noise
  freq_start      Hz at the start            freq_end   Hz at the end (exponential slide)
  attack, sustain, decay   seconds           punch      0-1 extra loudness at sustain start
  duty, duty_end  square pulse width 0.05-0.5
  vibrato_depth   0-0.5 (fraction of pitch)  vibrato_rate  Hz
  arp_mult, arp_time   jump pitch by arp_mult after arp_time seconds (coin "ding")
  repeat          seconds between retriggers of the pitch slide (0 = off)
  lowpass_start, lowpass_end   Hz one-pole low-pass sweep (0 = off)
  highpass        Hz (0 = off)
  volume          0-1
  layers          list of extra recipes mixed on top (e.g. a noise thump under a laser)
"""
import argparse
import json
import math
import os
import random
import shutil
import struct
import subprocess
import sys
import wave

RATE = 44100

PRESETS = {
    "coin":     {"wave": "square", "freq_start": 988, "freq_end": 988, "attack": 0.0, "sustain": 0.05, "decay": 0.25,
                 "punch": 0.4, "duty": 0.5, "arp_mult": 1.335, "arp_time": 0.06, "volume": 0.5},
    "pickup":   {"wave": "triangle", "freq_start": 660, "freq_end": 1320, "attack": 0.0, "sustain": 0.04, "decay": 0.16,
                 "punch": 0.3, "volume": 0.6},
    "jump":     {"wave": "square", "freq_start": 300, "freq_end": 620, "attack": 0.0, "sustain": 0.08, "decay": 0.14,
                 "duty": 0.3, "duty_end": 0.45, "volume": 0.45},
    "laser":    {"wave": "saw", "freq_start": 1400, "freq_end": 180, "attack": 0.0, "sustain": 0.06, "decay": 0.16,
                 "punch": 0.2, "lowpass_start": 9000, "lowpass_end": 2500, "volume": 0.4},
    "explosion": {"wave": "noise", "freq_start": 2200, "freq_end": 90, "attack": 0.0, "sustain": 0.12, "decay": 0.75,
                  "punch": 0.6, "lowpass_start": 6000, "lowpass_end": 400, "volume": 0.75},
    "hit":      {"wave": "noise", "freq_start": 4000, "freq_end": 700, "attack": 0.0, "sustain": 0.02, "decay": 0.12,
                 "punch": 0.5, "lowpass_start": 7000, "lowpass_end": 1500, "volume": 0.6,
                 "layers": [{"wave": "sine", "freq_start": 180, "freq_end": 60, "sustain": 0.02, "decay": 0.1, "volume": 0.6}]},
    "hurt":     {"wave": "square", "freq_start": 520, "freq_end": 140, "attack": 0.0, "sustain": 0.05, "decay": 0.2,
                 "duty": 0.2, "vibrato_depth": 0.12, "vibrato_rate": 28, "volume": 0.45},
    "powerup":  {"wave": "square", "freq_start": 330, "freq_end": 1320, "attack": 0.0, "sustain": 0.25, "decay": 0.25,
                 "duty": 0.4, "repeat": 0.09, "volume": 0.4},
    "select":   {"wave": "square", "freq_start": 880, "freq_end": 880, "attack": 0.0, "sustain": 0.03, "decay": 0.05,
                 "duty": 0.5, "volume": 0.35},
    "confirm":  {"wave": "triangle", "freq_start": 660, "freq_end": 660, "attack": 0.0, "sustain": 0.05, "decay": 0.12,
                 "arp_mult": 1.5, "arp_time": 0.05, "volume": 0.55},
    "cancel":   {"wave": "triangle", "freq_start": 520, "freq_end": 330, "attack": 0.0, "sustain": 0.05, "decay": 0.12,
                 "volume": 0.55},
    "click":    {"wave": "noise", "freq_start": 9000, "freq_end": 6000, "attack": 0.0, "sustain": 0.004, "decay": 0.02,
                 "highpass": 1500, "volume": 0.5},
    "footstep": {"wave": "noise", "freq_start": 1800, "freq_end": 500, "attack": 0.002, "sustain": 0.01, "decay": 0.07,
                 "lowpass_start": 2500, "lowpass_end": 900, "volume": 0.5},
    "whoosh":   {"wave": "noise", "freq_start": 6000, "freq_end": 6000, "attack": 0.12, "sustain": 0.02, "decay": 0.22,
                 "lowpass_start": 600, "lowpass_end": 5000, "highpass": 300, "volume": 0.5},
    "shoot":    {"wave": "noise", "freq_start": 3000, "freq_end": 300, "attack": 0.0, "sustain": 0.03, "decay": 0.22,
                 "punch": 0.7, "lowpass_start": 8000, "lowpass_end": 1200, "volume": 0.65},
    "magic":    {"wave": "sine", "freq_start": 600, "freq_end": 1500, "attack": 0.05, "sustain": 0.2, "decay": 0.35,
                 "vibrato_depth": 0.06, "vibrato_rate": 9, "volume": 0.5,
                 "layers": [{"wave": "triangle", "freq_start": 1200, "freq_end": 3000, "attack": 0.05, "sustain": 0.2,
                             "decay": 0.35, "volume": 0.25}]},
    "error":    {"wave": "square", "freq_start": 160, "freq_end": 160, "attack": 0.0, "sustain": 0.18, "decay": 0.05,
                 "duty": 0.5, "repeat": 0.1, "volume": 0.35},
}

JITTER = {"freq_start": 0.08, "freq_end": 0.08, "sustain": 0.1, "decay": 0.12, "duty": 0.1, "lowpass_start": 0.1,
          "lowpass_end": 0.1, "vibrato_rate": 0.1}


def render(p, rng):
    wave_t = p.get("wave", "square")
    a, s, d = p.get("attack", 0.0), p.get("sustain", 0.1), p.get("decay", 0.2)
    n = max(1, int((a + s + d) * RATE))
    f0 = max(10.0, p.get("freq_start", 440.0))
    f1 = max(10.0, p.get("freq_end", f0))
    duty0 = p.get("duty", 0.5)
    duty1 = p.get("duty_end", duty0)
    vib_d, vib_r = p.get("vibrato_depth", 0.0), p.get("vibrato_rate", 0.0)
    arp_m, arp_t = p.get("arp_mult", 1.0), p.get("arp_time", 0.0)
    rep = p.get("repeat", 0.0)
    lp0, lp1 = p.get("lowpass_start", 0.0), p.get("lowpass_end", p.get("lowpass_start", 0.0))
    hp = p.get("highpass", 0.0)
    punch = p.get("punch", 0.0)
    vol = p.get("volume", 0.5)
    phase, noise_val, lp_y, hp_y, hp_x = 0.0, rng.uniform(-1, 1), 0.0, 0.0, 0.0
    out = []
    total = a + s + d
    for i in range(n):
        t = i / RATE
        st = (t % rep) / rep if rep > 0 else t / total
        freq = f0 * (f1 / f0) ** st
        if arp_t and t >= arp_t:
            freq *= arp_m
        if vib_d:
            freq *= 1 + vib_d * math.sin(2 * math.pi * vib_r * t)
        prev = phase
        phase = (phase + freq / RATE) % 1.0
        if wave_t == "square":
            duty = duty0 + (duty1 - duty0) * (t / total)
            x = 1.0 if phase < duty else -1.0
        elif wave_t == "saw":
            x = 2 * phase - 1
        elif wave_t == "triangle":
            x = 4 * abs(phase - 0.5) - 1
        elif wave_t == "sine":
            x = math.sin(2 * math.pi * phase)
        elif wave_t == "noise":
            if phase < prev:  # wrapped: new random value (pitched noise)
                noise_val = rng.uniform(-1, 1)
            x = noise_val
        else:
            sys.exit("unknown wave '%s'" % wave_t)
        lp = lp0 + (lp1 - lp0) * (t / total)
        if lp > 0:
            k = 1 - math.exp(-2 * math.pi * lp / RATE)
            lp_y += k * (x - lp_y)
            x = lp_y
        if hp > 0:
            k = math.exp(-2 * math.pi * hp / RATE)
            hp_y = k * (hp_y + x - hp_x)
            hp_x = x
            x = hp_y
        if t < a:
            env = t / a
        elif t < a + s:
            env = 1 + punch * (1 - (t - a) / s) if s > 0 else 1
        else:
            env = max(0.0, 1 - (t - a - s) / d) if d > 0 else 0
        out.append(x * env * vol)
    for layer in p.get("layers", []):
        lo = render(layer, rng)
        if len(lo) > len(out):
            out += [0.0] * (len(lo) - len(out))
        for i, v in enumerate(lo):
            out[i] += v
    return out


def finish(samples):
    fade = min(len(samples), int(0.005 * RATE))
    for i in range(fade):
        samples[-1 - i] *= i / fade
    peak = max(1e-9, max(abs(v) for v in samples))
    if peak > 0.98:
        samples = [v * 0.98 / peak for v in samples]
    return samples


def write_wav(path, samples):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in samples))


def to_ogg(path):
    if not shutil.which("ffmpeg"):
        print("NOT CONVERTED to OGG: ffmpeg not found (WAV kept; Godot/Unity import WAV fine)")
        return None
    ogg = os.path.splitext(path)[0] + ".ogg"
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-c:a", "libvorbis", "-q:a", "5", ogg],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("NOT CONVERTED to OGG: ffmpeg failed: %s" % r.stderr.strip())
        return None
    os.remove(path)
    return ogg


def jittered(p, rng, amount):
    q = json.loads(json.dumps(p))
    for k, j in JITTER.items():
        if k in q and isinstance(q[k], (int, float)) and q[k]:
            q[k] = q[k] * (1 + rng.uniform(-j, j) * amount)
    return q


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preset", choices=sorted(PRESETS))
    ap.add_argument("--recipe")
    ap.add_argument("-o", "--out")
    ap.add_argument("--variants", type=int, default=1)
    ap.add_argument("--variation", type=float, default=1.0, help="0 = identical variants, 1 = default, 2 = wild")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--ogg", action="store_true", help="convert to .ogg with ffmpeg (CCGS audit prefers OGG)")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        print("presets: " + ", ".join(sorted(PRESETS)))
        return
    if not a.out:
        sys.exit("give -o OUT.wav")
    p = {}
    if a.recipe:
        with open(a.recipe, encoding="utf-8") as f:
            rec = json.load(f)
        if rec.get("preset"):
            p.update(PRESETS[rec["preset"]])
        p.update(rec)
    elif a.preset:
        p.update(PRESETS[a.preset])
    else:
        sys.exit("give --preset or --recipe (see --list)")
    base, _ = os.path.splitext(a.out)
    for v in range(a.variants):
        rng = random.Random(a.seed * 1000 + v)
        q = jittered(p, rng, a.variation) if a.variants > 1 else p
        path = "%s_%02d.wav" % (base, v + 1) if a.variants > 1 else base + ".wav"
        samples = finish(render(q, rng))
        write_wav(path, samples)
        if a.ogg:
            path = to_ogg(path) or path
        print("wrote %s  (%.2fs)" % (path, len(samples) / RATE))


if __name__ == "__main__":
    main()
