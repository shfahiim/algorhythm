"""Tune 02: 'Golden Horizon' (Vibrant, Enthusiastic Nu-Disco / Melodic House)
Duration: 60.0s @ 112 BPM (28 bars @ 2.142857s/bar)
Key: G Major / E Minor
Character: Very enthusiastic, driving, time passes (cascading chime arpeggios & bouncy groove), smooth fade.

Generates:
    tune/tune_02_golden_horizon.wav (48 kHz stereo 16-bit PCM)
    tune/tune_02_golden_horizon.mp3 (320 kbps MP3 via ffmpeg)
"""

import os
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 60.0
N = int(SR * DUR)
BPM = 112.0
BEAT = 60.0 / BPM          # 0.535714 s
BAR = BEAT * 4.0           # 2.142857 s
TOTAL_BARS = 28            # 28 * 2.142857s = 60.0s exactly

rng = np.random.default_rng(77)

NAMES = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

def hz(note):
    name = note[:-1]
    octave = int(note[-1])
    semitones = NAMES[name] + 12 * (octave + 1) - 69
    return 440.0 * (2.0 ** (semitones / 12.0))

# Buses
drums = np.zeros((N, 2), dtype=np.float32)
music = np.zeros((N, 2), dtype=np.float32)
sfx = np.zeros((N, 2), dtype=np.float32)
verb_send = np.zeros((N, 2), dtype=np.float32)
pump = np.ones(N, dtype=np.float32)
filt = np.ones(N, dtype=np.float32)

def add(bus, t0, sig, gain=1.0, pan=0.0, send=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or len(sig) == 0:
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    sig = sig[: N - i0]
    l = np.cos((pan + 1.0) * np.pi / 4.0) * gain
    r = np.sin((pan + 1.0) * np.pi / 4.0) * gain
    bus[i0:i0 + len(sig), 0] += sig * l
    bus[i0:i0 + len(sig), 1] += sig * r
    if send > 0:
        verb_send[i0:i0 + len(sig), 0] += sig * l * send
        verb_send[i0:i0 + len(sig), 1] += sig * r * send

def tt(d):
    return np.arange(int(d * SR)) / SR

def lp(x, fc, o=2):
    return sosfilt(butter(o, min(fc, SR / 2 - 100), 'low', fs=SR, output='sos'), x)

def hp(x, fc, o=2):
    return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)

def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, min(hi, SR / 2 - 100)], 'band', fs=SR, output='sos'), x)

def env(n, a=0.005, r=0.08):
    e = np.ones(n, dtype=np.float32)
    na = int(a * SR)
    nr = int(r * SR)
    if na > 0 and na < n:
        e[:na] = np.linspace(0, 1, na)
    if nr > 0 and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e

def saw(f, t, ph=0.0):
    return 2.0 * ((f * t + ph) % 1.0) - 1.0

def supersaw(f, d, voices=(-22, -12, -4, 4, 12, 22)):
    t = tt(d)
    s = np.zeros_like(t)
    for c in voices:
        s += saw(f * (2.0 ** (c / 1200.0)), t, rng.uniform())
    return s / len(voices)

# Sound Generators
def kick():
    t = tt(0.38)
    f = 50.0 + 125.0 * np.exp(-t * 38.0)
    body = np.sin(2.0 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.2)
    click = lp(rng.standard_normal(len(t)), 5000) * np.exp(-t * 320.0) * 0.38
    return np.tanh((body + click) * 1.7) * 0.84

def clap():
    t = tt(0.26)
    e = sum(np.exp(-np.maximum(0, t - o) * (190.0 if k < 3 else 22.0)) * (t >= o)
            for k, o in enumerate((0.0, 0.007, 0.015, 0.024)))
    noise = bp(rng.standard_normal(len(t)), 950, 4400)
    return noise * e * 0.36

def hat_closed():
    t = tt(0.04)
    return hp(rng.standard_normal(len(t)), 8500) * np.exp(-t * 120.0) * 0.13

def hat_open():
    t = tt(0.28)
    return hp(rng.standard_normal(len(t)), 7400) * np.exp(-t * 13.0) * 0.11

def shaker():
    t = tt(0.06)
    return bp(rng.standard_normal(len(t)), 5200, 11000) * np.sin(np.pi * np.minimum(1.0, t / 0.06)) * 0.075

def snare():
    t = tt(0.22)
    body = np.sin(2.0 * np.pi * 220.0 * t) * np.exp(-t * 34.0) * 0.45
    noise = bp(rng.standard_normal(len(t)), 1700, 8800) * np.exp(-t * 26.0) * 0.35
    return (body + noise) * 0.38

def crash():
    t = tt(3.0)
    return hp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 1.4) * 0.22

# Bouncy Nu-Disco Synth Bass (saw + sub with resonant pluck filter)
def disco_bass(f, d):
    t = tt(d)
    osc = 0.65 * saw(f, t) + 0.35 * np.sin(2.0 * np.pi * f * t)
    filt_env = 400.0 + 1600.0 * np.exp(-t * 24.0)
    # 2-pole lowpass sweep
    ph = np.cumsum(filt_env) / SR
    filtered = lp(osc, 1200) * 0.7 + lp(osc, 2400) * 0.3 * np.exp(-t * 16.0)
    return np.tanh(filtered * 1.6) * env(len(t), 0.003, 0.03) * 0.38

# Brassy Chord Stabs
def brass_stab(f, d=BEAT * 0.45):
    s = supersaw(f, d, (-16, -7, 0, 7, 16))
    t = tt(d)
    dark = lp(s, 1100)
    bright = lp(s, 6000)
    sweep = dark + (bright - dark) * np.exp(-t * 18.0)
    return hp(sweep, 190) * env(len(t), 0.004, 0.04) * 0.17

def chord_pad(f, d, cutoff=2800):
    s = supersaw(f, d, (-26, -15, -6, 6, 15, 26))
    return hp(lp(s, cutoff), 220) * env(len(s), 0.025, 0.28) * 0.095

# Uplifting Lead Synth
def lead_synth(f, d):
    t = tt(d)
    # Modulated vibrato
    fm = f * (1.0 + 0.0035 * np.sin(2.0 * np.pi * 6.2 * t) * np.minimum(1.0, t / 0.18))
    ph = np.cumsum(fm) / SR
    pulse = np.sign(np.sin(2.0 * np.pi * ph)) * 0.55 + (2.0 * (ph % 1.0) - 1.0) * 0.45
    dark = lp(pulse, 2200)
    bright = lp(pulse, 7800)
    y = dark + (bright - dark) * np.exp(-t * 7.5) + 0.35 * np.sin(4.0 * np.pi * ph) * np.exp(-t * 4.5)
    return y * env(len(t), 0.003, min(0.12, d / 3.0)) * np.exp(-t * 1.0) * 0.23

# Cascading Chime Arpeggio: "Time Passes / Fast Forward"
def chime_pluck(f, d=0.16):
    t = tt(d)
    bell = (
        np.sin(2.0 * np.pi * f * t) * 1.0 +
        np.sin(2.0 * np.pi * f * 2.01 * t) * 0.5 * np.exp(-t * 16.0) +
        np.sin(2.0 * np.pi * f * 3.0 * t) * 0.25 * np.exp(-t * 28.0)
    )
    click = hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * 300.0) * 0.10
    return (bell * np.exp(-t * 14.0) + click) * 0.14

# SFX Elements
def clock_tick(f=3200, d=0.025, g=0.22):
    t = tt(d)
    return (np.sin(2.0 * np.pi * f * t) * np.exp(-t * 220.0) +
            0.3 * hp(rng.standard_normal(len(t)), 5000) * np.exp(-t * 450.0)) * g

def riser(d, g=0.30):
    t = tt(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    L = len(t) // 40 + 1
    for b in range(40):
        c = 380.0 * (26.0 ** (b / 40.0))
        seg = n[b * L:(b + 1) * L]
        out[b * L:b * L + len(seg)] = bp(seg, c * 0.7, c * 1.4)
    sweep = np.sin(2.0 * np.pi * np.cumsum(240.0 * (2.0 ** (2.8 * t / d))) / SR) * 0.25
    return (out + sweep) * ((t / d) ** 2) * g

def impact(g=0.75):
    t = tt(2.0)
    sub = np.sin(2.0 * np.pi * np.cumsum(48.0 + 90.0 * np.exp(-t * 22.0)) / SR) * np.exp(-t * 2.8)
    noise = lp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 7.0) * 0.42
    return np.tanh((sub + noise) * 1.5) * g

def whoosh(d=0.75, lo=300, hi=6000, g=0.30):
    t = tt(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    L = len(t) // 24 + 1
    for b in range(24):
        c = lo * ((hi / lo) ** (np.sin(np.pi * b / 23.0) ** 0.8))
        seg = n[b * L:(b + 1) * L]
        out[b * L:b * L + len(seg)] = bp(seg, c * 0.6, c * 1.6)
    rise = 0.6
    env_w = np.where(t < d * rise, (t / (d * rise)) ** 2, np.exp(-(t - d * rise) / (d * (1 - rise) / 3.0)))
    return out * env_w * g

# Harmony & Chords: G Major / E Minor progression
# Progression: C (IV) -> D (V) -> Em (vi) -> G (I)
CHORDS = {
    'C': ['C4', 'E4', 'G4', 'D5'],
    'D': ['D4', 'F#4', 'A4', 'D5'],
    'Em': ['E4', 'G4', 'B4', 'E5'],
    'G': ['D4', 'G4', 'B4', 'D5']
}
ROOTS = {'C': 'C2', 'D': 'D2', 'Em': 'E2', 'G': 'G1'}
PROG = ['C', 'D', 'Em', 'G']

# 16th-note Chime Arpeggio sequences per chord (cascading motion)
ARP_NOTES = {
    'C': ['C5', 'E5', 'G5', 'D6', 'E6', 'D6', 'G5', 'E5', 'C5', 'E5', 'G5', 'D6', 'E6', 'G6', 'A6', 'C7'],
    'D': ['D5', 'F#5', 'A5', 'D6', 'F#6', 'D6', 'A5', 'F#5', 'D5', 'F#5', 'A5', 'D6', 'E6', 'F#6', 'A6', 'D7'],
    'Em': ['E5', 'G5', 'B5', 'E6', 'G6', 'E6', 'B5', 'G5', 'E5', 'G5', 'B5', 'E6', 'F#6', 'G6', 'B6', 'E7'],
    'G': ['G5', 'B5', 'D6', 'G6', 'B6', 'G6', 'D6', 'B5', 'G5', 'B5', 'D6', 'G6', 'A6', 'B6', 'D7', 'G7']
}

# Melodic Hook: Joyful, enthusiastic, driving
HOOK = {
    'C': [(0.0, 'E5', 0.5), (0.5, 'G5', 0.5), (1.0, 'D6', 0.75), (1.75, 'C6', 0.5), (2.25, 'B5', 0.5), (2.75, 'G5', 0.5), (3.25, 'C6', 0.75)],
    'D': [(0.0, 'F#5', 0.5), (0.5, 'A5', 0.5), (1.0, 'D6', 0.75), (1.75, 'E6', 0.5), (2.25, 'D6', 0.5), (2.75, 'A5', 0.5), (3.25, 'F#5', 0.75)],
    'Em': [(0.0, 'G5', 0.5), (0.5, 'B5', 0.5), (1.0, 'E6', 1.0), (2.0, 'D6', 0.5), (2.5, 'B5', 0.5), (3.0, 'G5', 0.5), (3.5, 'B5', 0.5)],
    'G': [(0.0, 'D5', 0.5), (0.5, 'G5', 0.5), (1.0, 'B5', 0.75), (1.75, 'C6', 0.5), (2.25, 'B5', 0.5), (2.75, 'A5', 0.5), (3.25, 'G5', 0.75)]
}

# 28-Bar Arrangement Structure
# 0..3:   intro (0.0 - 8.57s)
# 4..7:   drive (8.57 - 17.14s)
# 8..11:  verse_lead (17.14 - 25.71s)
# 12..15: build (25.71 - 34.29s)
# 16..23: peak_climax (34.29 - 51.43s) [8 bars of full energy!]
# 24..27: outro_fade (51.43 - 60.00s)
PLAN = (
    ['intro'] * 4 +
    ['drive'] * 4 +
    ['verse_lead'] * 4 +
    ['build'] * 4 +
    ['peak_climax'] * 8 +
    ['outro_fade'] * 4
)
assert len(PLAN) == TOTAL_BARS

LV = {
    'intro': dict(kick=0.5, pad=0.7, chime=0.85, shk=0.5, tick=1),
    'drive': dict(kick=1.0, clap=0.9, chh=0.8, ohh=0.7, bass=1.0, stab=1.0, pad=0.5, chime=0.7, shk=0.6),
    'verse_lead': dict(kick=1.0, clap=0.95, chh=0.85, ohh=0.8, bass=1.0, stab=0.9, pad=0.6, hook=1.0, chime=0.75, shk=0.7),
    'build': dict(pad=0.85, chime=1.0, tick=1, stab=0.8, bass=0.6),
    'peak_climax': dict(kick=1.05, clap=1.0, chh=0.95, ohh=0.9, bass=1.05, stab=1.0, pad=0.9, hook=1.1, chime=0.9, shk=0.8, big=1),
    'outro_fade': dict(pad=0.8, chime=0.8, stab=0.5, bass=0.4, chh=0.4)
}

print("Synthesizing Tune 02: 'Golden Horizon'...")

for b, sec in enumerate(PLAN):
    b0 = b * BAR
    L = LV[sec]
    g = lambda k: L.get(k, 0.0)
    ch = PROG[b % 4]
    nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

    # Ticking clock rhythm ("time passes" motif)
    if g('tick'):
        for i in range(16):
            t_tick = b0 + i * (BEAT / 4.0)
            if t_tick < DUR:
                add(sfx, t_tick, clock_tick(3400 if i % 4 == 0 else 2600, 0.02, 0.06), pan=0.35)

    # Cascading Chime Arpeggio
    if g('chime'):
        chime_scale = g('chime')
        notes = ARP_NOTES[ch]
        for i in range(16):
            t_chime = b0 + i * (BEAT / 4.0)
            if t_chime < DUR:
                note_hz = hz(notes[i])
                pan_val = -0.6 + (i % 5) * 0.3
                sig = chime_pluck(note_hz, 0.20) * chime_scale
                add(music, t_chime, sig, 1.0, pan=pan_val, send=0.35)

    # 4 beats per bar
    for bt in range(4):
        tb = b0 + bt * BEAT
        if tb >= DUR:
            break

        # Kick
        if g('kick'):
            if sec != 'intro' or b >= 1:
                kick_gain = g('kick') * (0.75 if (sec == 'intro' and b < 2) else 1.0)
                add(drums, tb, kick(), kick_gain)
                # Sidechain duck envelope
                i0 = int(tb * SR)
                i1 = min(N, int((tb + 0.32) * SR))
                pump[i0:i1] = np.minimum(pump[i0:i1], 0.27 + 0.73 * (np.linspace(0, 1, i1 - i0) ** 0.7))

        # Clap on 2 and 4
        if g('clap') and bt in (1, 3):
            add(drums, tb, clap(), g('clap'), send=0.25)

        # 16th Hats & Shakers
        for q in range(4):
            tq = tb + q * (BEAT / 4.0)
            if tq >= DUR:
                break
            if g('chh') and q in (1, 3):
                accent = 1.0 if q == 3 else 0.65
                add(drums, tq, hat_closed(), g('chh') * accent, pan=0.25)
            if g('shk'):
                accent = 1.0 if q % 2 == 1 else 0.6
                add(drums, tq, shaker(), g('shk') * accent, pan=-0.3)

        # Offbeat open hi-hat
        off = tb + BEAT / 2.0
        if off < DUR:
            if g('ohh'):
                add(drums, off, hat_open(), g('ohh'), pan=0.2)
            # Offbeat brass stab
            if g('stab'):
                for k_i, nn in enumerate(CHORDS[ch]):
                    add(music, off, brass_stab(hz(nn)), g('stab') * 0.85, pan=(-0.5, -0.15, 0.15, 0.5)[k_i], send=0.22)

        # Bouncy Nu-Disco Bass Pattern: Root on 1, octave on offbeat, syncopations on 3 and 4
        if g('bass'):
            root_f = hz(ROOTS[ch])
            # Beat 0: downbeat root
            if bt == 0:
                add(music, tb, disco_bass(root_f, BEAT * 0.42), g('bass') * 0.95)
            # Offbeats of each beat
            if off < DUR:
                add(music, off, disco_bass(root_f * 2.0, BEAT * 0.38), g('bass'))
            # Funky pickup on the 16th before beat 3
            if bt == 2:
                t_funky = tb + BEAT * 0.75
                if t_funky < DUR:
                    add(music, t_funky, disco_bass(root_f * 1.5, BEAT * 0.22), g('bass') * 0.75)

    # Sustained Chord Pad
    if g('pad'):
        d_pad = min(BAR + 0.1, DUR - b0)
        for k_i, nn in enumerate(CHORDS[ch]):
            add(music, b0, chord_pad(hz(nn), d_pad, cutoff=3000), g('pad'), pan=(-0.6, -0.2, 0.2, 0.6)[k_i], send=0.35)

    # Melodic Hook
    if g('hook'):
        for o, nn, ln in HOOK[ch]:
            ts = b0 + o * BEAT
            if ts < DUR:
                sig = lead_synth(hz(nn), ln * BEAT * 0.95) * g('hook')
                if g('big'):
                    # Layer 1 octave higher in the big peak section
                    sig_oct = lead_synth(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.48
                    max_len = max(len(sig), len(sig_oct))
                    sig_combined = np.zeros(max_len, dtype=np.float32)
                    sig_combined[:len(sig)] += sig
                    sig_combined[:len(sig_oct)] += sig_oct
                    sig = sig_combined
                add(music, ts, sig, 1.0, pan=0.0, send=0.35)
                # Dotted delay reflections
                for r, (dl, pn) in enumerate(((0.75, -0.55), (1.5, 0.55), (2.25, -0.35))):
                    delayed_t = ts + dl * BEAT
                    if delayed_t < DUR:
                        add(music, delayed_t, lp(sig, 3600) * (0.42 ** (r + 1)), 0.9, pan=pn)

    # Transitions & Builds into the Climax
    if sec == 'build' and nxt == 'peak_climax':
        start = b0
        end = b0 + BAR
        t_snare = start
        for div, frac in ((2, 0.4), (4, 0.75), (8, 1.0)):
            while t_snare < start + (end - start) * frac - 1e-5:
                vol = (0.25 + 0.75 * ((t_snare - start) / (end - start)) ** 1.6) * 0.95
                add(drums, t_snare, snare(), vol, send=0.2)
                t_snare += BEAT / div
        add(sfx, start, riser(BAR, 0.32))

    if sec == 'peak_climax' and (b == 0 or PLAN[b - 1] != 'peak_climax'):
        add(drums, b0, crash(), 1.05, send=0.35)
        add(sfx, b0, impact(0.75), send=0.3)
        add(sfx, b0, whoosh(0.9, 250, 6500, 0.32))

# Dynamic Filter Sweeps
def ramp_filter(a, b, v0, v1):
    i0, i1 = int(a * SR), min(N, int(b * SR))
    if i1 > i0:
        filt[i0:i1] = np.linspace(v0, v1, i1 - i0)

# Filter opens during intro, tightens at build, expands at drop
ramp_filter(0.0, 8.57, 0.25, 0.95)
ramp_filter(25.71, 34.29, 0.40, 1.0)
ramp_filter(51.43, 60.0, 1.0, 0.35)

print("Applying mixing, sidechain pump & convolution reverb...")

# Music filtering & sidechain pumping
mus_lp = np.stack([lp(music[:, c], 680) for c in range(2)], axis=1)
music = (mus_lp + (music - mus_lp) * filt[:, None]) * pump[:, None]

# Stereo Impulse Response for Reverb (2.4s decaying stereo noise)
ir_t = tt(2.2)
ir = np.stack([lp(rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 2.7), 7000) for _ in range(2)], axis=1)
ir /= np.sqrt((ir ** 2).sum(axis=0))

# Wet Reverb Bus
send_total = verb_send + music * 0.12
wet = np.stack([fftconvolve(send_total[:, c], ir[:, c])[:N] for c in range(2)], axis=1)

# Master Mix Sum
mix = drums * 0.95 + music + sfx * 0.85 + wet * 0.42

# High-pass filter master (30Hz subsonic rumble removal)
for c in range(2):
    mix[:, c] = hp(mix[:, c], 30)

# RMS Level Normalization & Analog Soft Tape Saturation
rms = np.sqrt(np.mean(mix ** 2))
mix = mix / (rms * 6.5)
mix = np.tanh(mix * 1.25) / np.tanh(1.25)
mix /= np.abs(mix).max()

# Smooth Fade In (0.05s) and Master Fade Out across last 7.0 seconds into silence
fade = np.ones(N, dtype=np.float32)
fade_in_len = int(0.05 * SR)
fade[:fade_in_len] = np.linspace(0, 1, fade_in_len)

fade_out_len = int(7.0 * SR)
fade[-fade_out_len:] = np.linspace(1, 0, fade_out_len) ** 1.5
mix *= fade[:, None] * 0.92

# Export WAV
here = os.path.dirname(os.path.abspath(__file__))
wav_out = os.path.join(here, 'tune_02_golden_horizon.wav')
mp3_out = os.path.join(here, 'tune_02_golden_horizon.mp3')

wavfile.write(wav_out, SR, (mix * 32767).astype(np.int16))
print(f"Generated WAV: {wav_out} (Peak: {round(float(np.abs(mix).max()), 3)})")

# Export high quality MP3
cmd = ['ffmpeg', '-y', '-i', wav_out, '-b:a', '320k', mp3_out]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"Generated MP3: {mp3_out}")
