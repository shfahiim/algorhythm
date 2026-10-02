"""Tune 13: 'The Long Journey' (Homage to Max LL: 'Departures' & 'Passerby')
Duration: 60.0s @ 72.0 BPM (18 bars @ 3.3333s/bar)
Key: F# Minor / A Major (F#m -> Dmaj7 -> A -> Eadd9)
Character: Delicate acoustic fingerstyle guitar, warm felt piano, sweeping cello & violin ensemble,
           celestial music-box glockenspiel chimes, natural room breathing, and a gentle fade.

Synthesized purely in Python via mathematical DSP based on spectral analysis deductions.
"""

import os
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 60.0
N = int(SR * DUR)
BPM = 72.0
BEAT = 60.0 / BPM          # 0.833333 s
BAR = BEAT * 4.0           # 3.333333 s
TOTAL_BARS = 18            # 18 * 3.33333s = 60.0s exactly

rng = np.random.default_rng(2026)

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
    if 0 < na < n:
        e[:na] = np.linspace(0, 1, na)
    if 0 < nr < n:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e

def saw(f, t, ph=0.0):
    return 2.0 * ((f * t + ph) % 1.0) - 1.0

# 1. Acoustic Fingerstyle Guitar (Woody body resonance + nail pluck)
def acoustic_guitar_pluck(f, d=0.35):
    t = tt(d)
    w = (
        np.sin(2.0 * np.pi * f * t) * 1.0 +
        np.sin(2.0 * np.pi * f * 2.0 * t) * 0.42 * np.exp(-t * 12.0) +
        np.sin(2.0 * np.pi * f * 3.01 * t) * 0.22 * np.exp(-t * 22.0) +
        np.sin(2.0 * np.pi * f * 4.02 * t) * 0.12 * np.exp(-t * 32.0)
    )
    # Fingertip string release transient
    fingertip = hp(rng.standard_normal(len(t)), 3200) * np.exp(-t * 240.0) * 0.12
    # Guitar soundboard body resonance (around 220Hz - 850Hz)
    body = bp(w, 180, 1200) * 0.6
    out = (w * 0.5 + body + fingertip) * env(len(t), 0.004, 0.05) * np.exp(-t * 6.5)
    return lp(out, 4200) * 0.22

# 2. Felt Piano (Dampened hammers, warm low-mids, soft felt transients)
def felt_piano(f, d=1.8):
    t = tt(d)
    # FM felt hammer: subtle modulator decaying quickly
    mod = np.sin(2.0 * np.pi * f * 2.0 * t) * np.exp(-t * 18.0) * 0.25
    car = np.sin(2.0 * np.pi * f * (1.0 + mod) * t) * np.exp(-t * 3.2)
    warmth = np.sin(2.0 * np.pi * f * 0.5 * t) * np.exp(-t * 2.5) * 0.15
    felt = lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 80.0) * 0.08
    out = (car + warmth + felt) * env(len(t), 0.008, min(0.2, d / 3.0))
    return lp(out, 1800) * 0.20

# 3. Sweeping Cello & Violin Ensemble (Breathing bows, slow swell, warm vibrato)
def orchestral_strings(f, d):
    t = tt(d)
    vib = 0.006 * np.sin(2.0 * np.pi * 5.3 * t) * np.minimum(1.0, t / 0.3)
    fm = f * (1.0 + vib)
    ph = np.cumsum(fm) / SR
    # 5 detuned saw voices
    w = (
        saw(1.0, ph) * 0.35 +
        saw(1.003, ph) * 0.25 +
        saw(0.997, ph) * 0.25 +
        saw(1.006, ph) * 0.15
    )
    # Slow expressive bow attack
    att = min(0.4, d * 0.35)
    e = np.ones_like(t)
    na = int(att * SR)
    if na > 0:
        e[:na] = np.linspace(0, 1, na) ** 1.8
    # Max LL acoustic signature: steep lowpass filter
    filtered = lp(hp(w, 140), 1600)
    return filtered * e * 0.09

# 4. Celestial Music-Box / Glockenspiel Chime
def music_box_bell(f, d=1.4):
    t = tt(d)
    bell = (
        np.sin(2.0 * np.pi * f * t) * 1.0 +
        np.sin(2.0 * np.pi * f * 2.76 * t) * 0.35 * np.exp(-t * 14.0) +
        np.sin(2.0 * np.pi * f * 5.40 * t) * 0.15 * np.exp(-t * 26.0)
    )
    return bell * np.exp(-t * 4.5) * env(len(t), 0.002, 0.08) * 0.13

# 5. Soft Acoustic Percussion (Wood tap & brush rustle)
def wood_tap():
    t = tt(0.12)
    click = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 180.0) * 0.35
    thump = np.sin(2.0 * np.pi * 95.0 * t) * np.exp(-t * 45.0) * 0.4
    return (click + thump) * 0.28

def soft_brush():
    t = tt(0.15)
    rustle = bp(rng.standard_normal(len(t)), 2200, 6000) * np.exp(-t * 28.0) * 0.12
    return rustle * 0.4

# Harmony: Max LL's signature F# Minor / A Major progression
CHORDS = {
    'F#m': ['F#3', 'A3', 'C#4', 'F#4'],
    'D': ['F#3', 'A3', 'D4', 'F#4'],
    'A': ['E3', 'A3', 'C#4', 'E4'],
    'E': ['E3', 'G#3', 'B3', 'E4']
}
ROOTS = {'F#m': 'F#2', 'D': 'D2', 'A': 'A1', 'E': 'E2'}
PROG = ['F#m', 'D', 'A', 'E']

# Fingerstyle picking arpeggios (16th notes: 16 notes per bar in 4/4)
GUITAR_ARPS = {
    'F#m': ['F#3', 'C#4', 'A3', 'F#4', 'A3', 'C#4', 'A3', 'F#4', 'F#3', 'C#4', 'A3', 'F#4', 'C#4', 'E4', 'F#4', 'A4'],
    'D': ['D3', 'A3', 'F#4', 'D4', 'F#4', 'A3', 'D4', 'F#4', 'D3', 'A3', 'F#4', 'D4', 'E4', 'F#4', 'A4', 'D5'],
    'A': ['A2', 'E3', 'C#4', 'A3', 'C#4', 'E3', 'A3', 'C#4', 'A2', 'E3', 'C#4', 'A3', 'B3', 'C#4', 'E4', 'A4'],
    'E': ['E2', 'B2', 'G#3', 'E3', 'G#3', 'B2', 'E3', 'G#3', 'E2', 'B2', 'G#3', 'E3', 'F#3', 'G#3', 'B3', 'E4']
}

# Celestial Glockenspiel motifs
GLOCK_NOTES = {
    'F#m': [(0.5, 'C#6'), (1.5, 'F#6'), (2.25, 'A6'), (3.0, 'E6')],
    'D': [(0.5, 'D6'), (1.5, 'F#6'), (2.25, 'A6'), (3.0, 'F#6')],
    'A': [(0.5, 'C#6'), (1.5, 'E6'), (2.25, 'A6'), (3.0, 'G#6')],
    'E': [(0.5, 'B5'), (1.5, 'E6'), (2.25, 'G#6'), (3.0, 'B6')]
}

# Expressive Lead Melody (Felt Piano & Flute-like resonance)
MELODY = {
    'F#m': [(0.0, 'A4', 1.0), (1.0, 'C#5', 1.2), (2.5, 'E5', 0.6), (3.0, 'F#5', 1.0)],
    'D': [(0.0, 'F#5', 1.0), (1.0, 'A5', 1.2), (2.25, 'G#5', 0.6), (2.75, 'F#5', 0.6), (3.25, 'D5', 0.8)],
    'A': [(0.0, 'E5', 1.2), (1.25, 'C#5', 0.8), (2.0, 'E5', 1.0), (3.0, 'A5', 1.0)],
    'E': [(0.0, 'G#5', 1.2), (1.25, 'B5', 0.8), (2.0, 'F#5', 0.8), (2.75, 'E5', 1.2)]
}

# 18-bar structural plan (0..17 = 60.0s)
# 0..2:   Intro (solo fingerstyle guitar)
# 3..6:   Gentle Entry (felt piano + soft cello pad)
# 7..13:  Full Emotional Swell (sweeping strings, glockenspiel chimes, lead melody)
# 14..17: Peaceful Outro Fade (guitar & piano dissolve into reverb)
PLAN = (
    ['intro'] * 3 +
    ['entry'] * 4 +
    ['swell'] * 7 +
    ['outro'] * 4
)
assert len(PLAN) == TOTAL_BARS

LV = {
    'intro': dict(guitar=0.9, tap=0.4),
    'entry': dict(guitar=0.85, piano=0.85, strings=0.6, tap=0.5, brush=0.5),
    'swell': dict(guitar=0.9, piano=0.9, strings=0.9, glock=0.85, melody=1.0, tap=0.55, brush=0.6),
    'outro': dict(guitar=0.75, piano=0.7, strings=0.6, glock=0.6)
}

print("Synthesizing Tune 13: 'The Long Journey' (Max LL Homage)...")

music = np.zeros((N, 2), dtype=np.float32)
verb_send = np.zeros((N, 2), dtype=np.float32)

def add(t0, sig, gain=1.0, pan=0.0, send=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or len(sig) == 0:
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    sig = sig[: N - i0]
    l = np.cos((pan + 1.0) * np.pi / 4.0) * gain
    r = np.sin((pan + 1.0) * np.pi / 4.0) * gain
    music[i0:i0 + len(sig), 0] += sig * l
    music[i0:i0 + len(sig), 1] += sig * r
    if send > 0:
        verb_send[i0:i0 + len(sig), 0] += sig * l * send
        verb_send[i0:i0 + len(sig), 1] += sig * r * send

for b, sec in enumerate(PLAN):
    b0 = b * BAR
    L = LV[sec]
    g = lambda k: L.get(k, 0.0)
    ch = PROG[b % 4]

    # 1. Fingerstyle Guitar Arpeggio (Continuously carrying the time-passing motion)
    if g('guitar'):
        notes = GUITAR_ARPS[ch]
        for i in range(16):
            t_arp = b0 + i * (BEAT / 4.0)
            if t_arp < DUR:
                # Subtle humanization micro-timing (+/- 3ms)
                t_jitter = t_arp + rng.uniform(-0.003, 0.003)
                sig = acoustic_guitar_pluck(hz(notes[i]), 0.32) * g('guitar')
                pan_pos = -0.35 + (i % 4) * 0.22
                add(t_jitter, sig, 1.0, pan=pan_pos, send=0.35)

    # 2. Felt Piano Chords & Bass Foundation
    if g('piano'):
        for k_i, nn in enumerate(CHORDS[ch]):
            sig = felt_piano(hz(nn), BAR * 0.9) * g('piano')
            add(b0, sig, 1.0, pan=(-0.4, -0.15, 0.15, 0.4)[k_i], send=0.4)
        # Deep acoustic piano root note
        rf = hz(ROOTS[ch])
        add(b0, felt_piano(rf, BAR * 0.95) * 1.1, 1.0, pan=0.0, send=0.4)

    # 3. Sweeping Cello & Violin Ensemble Pad
    if g('strings'):
        d_str = min(BAR + 0.2, DUR - b0)
        for k_i, nn in enumerate(CHORDS[ch]):
            sig = orchestral_strings(hz(nn), d_str) * g('strings')
            add(b0, sig, 1.0, pan=(-0.6, -0.2, 0.2, 0.6)[k_i], send=0.55)
        # Deep cello root
        add(b0, orchestral_strings(hz(ROOTS[ch]), d_str) * 1.15, 1.0, pan=0.0, send=0.5)

    # 4. Celestial Glockenspiel Chimes
    if g('glock'):
        for o_beat, note_name in GLOCK_NOTES[ch]:
            t_g = b0 + o_beat * BEAT
            if t_g < DUR:
                sig = music_box_bell(hz(note_name), 1.6) * g('glock')
                add(t_g, sig, 1.0, pan=rng.uniform(-0.5, 0.5), send=0.6)
                # Delicate ping-pong delay reflection
                add(t_g + BEAT * 0.5, sig * 0.35, 1.0, pan=0.4, send=0.6)

    # 5. Expressive Felt Piano Lead Melody
    if g('melody'):
        for o_beat, note_name, ln_beats in MELODY[ch]:
            t_m = b0 + o_beat * BEAT
            if t_m < DUR:
                sig = felt_piano(hz(note_name), ln_beats * BEAT * 0.95) * g('melody')
                add(t_m, sig, 1.0, pan=0.05, send=0.45)
                # Dotted delay reflection for spatial depth
                add(t_m + BEAT * 0.75, lp(sig, 1200) * 0.3, 1.0, pan=-0.35, send=0.5)

    # 6. Subtle Acoustic Percussion (Wood tap on 2 & 4, soft brush on 8ths)
    for bt in range(4):
        tb = b0 + bt * BEAT
        if tb >= DUR:
            break
        if g('tap') and bt in (1, 3):
            add(tb, wood_tap(), g('tap'), pan=0.15, send=0.2)
        if g('brush'):
            add(tb + BEAT * 0.5, soft_brush(), g('brush'), pan=-0.25, send=0.25)

# Applying Max LL Acoustic Mixing Signature:
# 1. Warm Chamber Reverb Impulse Response (2.6s decay, high-frequency dampening)
print("Applying acoustic room convolution & warm acoustic mastering...")
ir_t = tt(2.6)
# High-frequency damped room impulse response
ir_decay = np.exp(-ir_t * 2.2)
ir_l = lp(rng.standard_normal(len(ir_t)) * ir_decay, 4500)
ir_r = lp(rng.standard_normal(len(ir_t)) * ir_decay, 4500)
ir = np.stack([ir_l, ir_r], axis=1)
ir /= np.sqrt((ir ** 2).sum(axis=0))

wet = np.stack([fftconvolve(verb_send[:, c], ir[:, c])[:N] for c in range(2)], axis=1)

# Sum Mix
mix = music + wet * 0.48

# 2. Master EQ matching spectral analysis deductions:
# Steep high-shelf rolloff above 5.5 kHz to preserve intimate felt & wood warmth
for c in range(2):
    mix[:, c] = hp(mix[:, c], 25)           # Remove subsonic rumble
    mix[:, c] = lp(mix[:, c], 6000)         # Max LL signature warm acoustic top-end

# 3. Preservation of Classical / Cinematic Headroom
rms = np.sqrt(np.mean(mix ** 2))
mix = mix / (rms * 7.5)                     # Dynamic acoustic headroom (high crest factor)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)     # Gentle warm tape rounding
mix /= np.abs(mix).max()

# 4. Smooth Fade In (first 0.1s) and Peaceful Exponential Fade Out over final 8 seconds
fade = np.ones(N, dtype=np.float32)
fi = int(0.1 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fo = int(8.0 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 1.6
mix *= fade[:, None] * 0.90

here = os.path.dirname(os.path.abspath(__file__))
wav_out = os.path.join(here, 'tune_13_departures_passerby_homage.wav')
mp3_out = os.path.join(here, 'tune_13_departures_passerby_homage.mp3')

wavfile.write(wav_out, SR, (mix * 32767).astype(np.int16))
print(f"Generated WAV: {wav_out} (Peak: {round(float(np.abs(mix).max()), 3)})")

cmd = ['ffmpeg', '-y', '-i', wav_out, '-b:a', '320k', mp3_out]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"Generated MP3: {mp3_out}")
