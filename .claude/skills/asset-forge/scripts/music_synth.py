#!/usr/bin/env python3
"""Pattern-based chiptune / synth music -> seamless looping 16-bit WAV.

Pure Python standard library. Optional OGG conversion if ffmpeg is installed.

Usage:
    python3 music_synth.py song.json -o assets/audio/music/music_level_forest_loop.wav
    python3 music_synth.py song.json -o out.wav --ogg

Song format (see references/audio-recipes.md for a full example):
{
  "name": "music_level_forest_loop",
  "bpm": 112, "beats_per_bar": 4, "steps_per_beat": 4, "loop": true,
  "instruments": {
    "lead":  { "wave": "square", "duty": 0.25, "volume": 0.22, "attack": 0.005, "decay": 0.12,
               "sustain_level": 0.55, "release": 0.06, "vibrato_depth": 0.004, "vibrato_rate": 6,
               "echo": { "time_steps": 3, "feedback": 0.3, "mix": 0.25 } },
    "bass":  { "wave": "triangle", "volume": 0.4 },
    "drums": { "kind": "drums", "volume": 0.5 }
  },
  "sections": {
    "A": { "bars": 2, "tracks": {
        "lead":  "E5 - G5 - | A5 - - . | G5 . E5 . | D5 - - - | ...",
        "bass":  "A2 - - - A2 - - - ...",
        "drums": "k . h . s . h . k k h . s . h ." } }
  },
  "order": ["A", "A", "B", "A"]
}
Pattern tokens (one per step, whitespace separated, '|' ignored):
  note      C4, F#3, Bb5 - starts a note; join with + for a chord: C4+E4+G4
  -         hold the previous note one more step
  .         rest
  drums:    k kick, s snare, h closed hat, o open hat, c clap, t tom; join with + (k+h)
A pattern shorter than the section is repeated to fill it (its length must divide evenly).
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
NOTE_INDEX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note_freq(tok):
    name = tok[0].upper()
    if name not in NOTE_INDEX:
        raise ValueError("bad note '%s'" % tok)
    i, semis = 1, NOTE_INDEX[name]
    while i < len(tok) and tok[i] in "#b":
        semis += 1 if tok[i] == "#" else -1
        i += 1
    try:
        octave = int(tok[i:])
    except ValueError:
        raise ValueError("bad note '%s' (expected like C4, F#3, Bb5)" % tok)
    midi = 12 * (octave + 1) + semis
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def osc(wave_t, phase, duty, rng_state):
    if wave_t == "square":
        return 1.0 if phase < duty else -1.0
    if wave_t == "saw":
        return 2 * phase - 1
    if wave_t == "triangle":
        return 4 * abs(phase - 0.5) - 1
    if wave_t == "sine":
        return math.sin(2 * math.pi * phase)
    if wave_t == "noise":
        return rng_state.uniform(-1, 1)
    raise ValueError("unknown wave '%s'" % wave_t)


def synth_note(inst, freqs, dur, rng):
    a = inst.get("attack", 0.005)
    dcy = inst.get("decay", 0.1)
    sl = inst.get("sustain_level", 0.7)
    rel = inst.get("release", 0.05)
    duty = inst.get("duty", 0.5)
    vd, vr = inst.get("vibrato_depth", 0.0), inst.get("vibrato_rate", 5.0)
    wave_t = inst.get("wave", "square")
    detune = inst.get("detune", 0.0)
    n = int((dur + rel) * RATE)
    out = [0.0] * n
    voices = []
    for f in freqs:
        voices.append(f)
        if detune:
            voices.append(f * (1 + detune))
    scale = 1.0 / math.sqrt(len(voices))
    for f in voices:
        ph = rng.random()
        for i in range(n):
            t = i / RATE
            ff = f * (1 + vd * math.sin(2 * math.pi * vr * t)) if vd else f
            ph = (ph + ff / RATE) % 1.0
            out[i] += osc(wave_t, ph, duty, rng) * scale
    for i in range(n):
        t = i / RATE
        if t < a:
            env = t / a
        elif t < a + dcy:
            env = 1 - (1 - sl) * (t - a) / dcy
        else:
            env = sl
        if t > dur:
            env *= max(0.0, 1 - (t - dur) / rel) if rel > 0 else 0
        out[i] *= env
    return out


def synth_drum(kind, rng):
    if kind == "k":
        n, out, ph = int(0.28 * RATE), [], 0.0
        for i in range(n):
            t = i / RATE
            f = 45 + 110 * math.exp(-t * 28)
            ph += f / RATE
            out.append(math.sin(2 * math.pi * ph) * math.exp(-t * 11) * 1.1)
        return out
    if kind in ("s", "c"):
        n, out, ph, lp = int(0.2 * RATE), [], 0.0, 0.0
        for i in range(n):
            t = i / RATE
            ph += 185 / RATE
            noise = rng.uniform(-1, 1)
            lp += 0.6 * (noise - lp)
            tone = math.sin(2 * math.pi * ph) * math.exp(-t * 30) * (0.5 if kind == "s" else 0.0)
            env = math.exp(-t * (18 if kind == "s" else 26))
            if kind == "c":
                env *= 1.0 if (t % 0.012) < 0.008 or t > 0.03 else 0.3
            out.append((lp * 0.8 + tone) * env)
        return out
    if kind in ("h", "o"):
        dec = 60 if kind == "h" else 9
        n, out, px, py = int((0.06 if kind == "h" else 0.35) * RATE), [], 0.0, 0.0
        k = math.exp(-2 * math.pi * 7000 / RATE)
        for i in range(n):
            t = i / RATE
            x = rng.uniform(-1, 1)
            py = k * (py + x - px)
            px = x
            out.append(py * math.exp(-t * dec) * 0.6)
        return out
    if kind == "t":
        n, out, ph = int(0.3 * RATE), [], 0.0
        for i in range(n):
            t = i / RATE
            ph += (90 + 60 * math.exp(-t * 15)) / RATE
            out.append(math.sin(2 * math.pi * ph) * math.exp(-t * 9))
        return out
    raise ValueError("unknown drum '%s' (use k s h o c t)" % kind)


def apply_echo(buf, echo, step_s, loop):
    d = int(echo.get("time_steps", 3) * step_s * RATE)
    fb, mix = echo.get("feedback", 0.3), echo.get("mix", 0.25)
    if d <= 0:
        return buf
    wet = [0.0] * len(buf)
    n = len(buf)
    for i in range(n):
        j = i - d
        prev = wet[j % n] if (loop or j >= 0) else 0.0
        src = buf[j % n] if (loop or j >= 0) else 0.0
        wet[i] = src + prev * fb
    return [buf[i] + wet[i] * mix for i in range(n)]


def tokens(pat):
    return [t for t in pat.replace("|", " ").split() if t]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("song")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--ogg", action="store_true", help="convert to .ogg with ffmpeg")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    with open(a.song, encoding="utf-8") as f:
        song = json.load(f)
    rng = random.Random(a.seed)
    bpm = song.get("bpm", 120)
    bpb = song.get("beats_per_bar", 4)
    spb = song.get("steps_per_beat", 4)
    step_s = 60.0 / bpm / spb
    loop = song.get("loop", True)
    insts = song["instruments"]
    order = song.get("order", list(song["sections"].keys()))
    total_steps = sum(song["sections"][s]["bars"] * bpb * spb for s in order)
    n = int(round(total_steps * step_s * RATE))
    tracks = {name: [0.0] * n for name in insts}
    cache = {}
    step0 = 0
    for sec_name in order:
        if sec_name not in song["sections"]:
            sys.exit("order names section '%s', which is not defined" % sec_name)
        sec = song["sections"][sec_name]
        steps = sec["bars"] * bpb * spb
        for tname, pat in sec.get("tracks", {}).items():
            if tname not in insts:
                sys.exit("section %s uses track '%s', which has no instrument" % (sec_name, tname))
            inst = insts[tname]
            toks = tokens(pat)
            if not toks or steps % len(toks):
                sys.exit("section %s track %s: %d steps does not divide the section's %d steps "
                         "(%d bars x %d beats x %d steps)" % (sec_name, tname, len(toks), steps, sec["bars"], bpb, spb))
            toks = toks * (steps // len(toks))
            buf = tracks[tname]
            i = 0
            while i < steps:
                tok = toks[i]
                if tok in (".", "-"):
                    i += 1
                    continue
                length = 1
                while i + length < steps and toks[i + length] == "-":
                    length += 1
                start = int(round((step0 + i) * step_s * RATE))
                if inst.get("kind") == "drums":
                    parts = tok.split("+")
                    for d in parts:
                        key = ("drum", d)
                        if key not in cache:
                            try:
                                cache[key] = synth_drum(d, rng)
                            except ValueError as e:
                                sys.exit("section %s track %s: %s" % (sec_name, tname, e))
                        smp = cache[key]
                        for j, v in enumerate(smp):
                            k = start + j
                            if k >= n:
                                if not loop:
                                    break
                                k %= n
                            buf[k] += v
                else:
                    try:
                        freqs = [note_freq(t) for t in tok.split("+")]
                    except ValueError as e:
                        sys.exit("section %s track %s step %d: %s" % (sec_name, tname, i, e))
                    key = (tname, tok, length)
                    if key not in cache:
                        cache[key] = synth_note(inst, freqs, length * step_s, rng)
                    for j, v in enumerate(cache[key]):
                        k = start + j
                        if k >= n:
                            if not loop:
                                break
                            k %= n  # wrap the tail to the start => seamless loop
                        buf[k] += v
                i += length
        step0 += steps
    mix = [0.0] * n
    for tname, buf in tracks.items():
        inst = insts[tname]
        if inst.get("echo"):
            buf = apply_echo(buf, inst["echo"], step_s, loop)
        vol = inst.get("volume", 0.3)
        for i in range(n):
            mix[i] += buf[i] * vol
    peak = max(1e-9, max(abs(v) for v in mix))
    gain = min(1.0, 0.95 / peak)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    path = os.path.splitext(a.out)[0] + ".wav"
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(v * gain * 32767)) for v in mix))
    print("wrote %s  (%.1fs, %d bars at %s bpm, loop=%s, peak gain %.2f)"
          % (path, n / RATE, total_steps // (bpb * spb), bpm, loop, gain))
    if a.ogg:
        if not shutil.which("ffmpeg"):
            print("NOT CONVERTED to OGG: ffmpeg not found (WAV kept)")
            return
        ogg = os.path.splitext(path)[0] + ".ogg"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-c:a", "libvorbis", "-q:a", "5", ogg],
                           capture_output=True, text=True)
        if r.returncode:
            print("NOT CONVERTED to OGG: %s" % r.stderr.strip())
        else:
            os.remove(path)
            print("wrote %s" % ogg)


if __name__ == "__main__":
    main()
