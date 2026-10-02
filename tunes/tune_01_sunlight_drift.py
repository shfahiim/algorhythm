"""Tune 01: 'Sunlight Drift' (Uplifting / Enthusiastic House)
Duration: 60.0s @ 100 BPM (25 bars @ 2.4s/bar)
Key: A Major / F# Minor
Character: Very enthusiastic, uplifting, time passing (clockwork arps & driving groove), smooth fade.

Generates:
    tune/tune_01_sunlight_drift.wav (48 kHz stereo 16-bit PCM)
    tune/tune_01_sunlight_drift.mp3 (320 kbps MP3 via ffmpeg)
"""

import os
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 60.0
N = int(SR * DUR)
BPM = 100.0
BEAT = 60.0 / BPM          # 0.6 s
BAR = BEAT * 4.0           # 2.4 s
TOTAL_BARS = 25            # 25 * 2.4s = 60.0s

rng = np.random.default_rng(42)

# Note names to frequency
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

def supersaw(f, d, voices=(-20, -11, -3, 3, 11, 20)):
    t = tt(d)
    s = np.zeros_like(t)
    for c in voices:
        s += saw(f * (2.0 ** (c / 1200.0)), t, rng.uniform())
    return s / len(voices)

# Sound Generators
def kick():
    t = tt(0.40)
    # Punchy pitch drop: 160Hz -> 50Hz
    f = 48.0 + 115.0 * np.exp(-t * 36.0)
    body = np.sin(2.0 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.8)
    click = lp(rng.standard_normal(len(t)), 4500) * np.exp(-t * 300.0) * 0.35
    return np.tanh((body + click) * 1.7) * 0.82

def clap():
    t = tt(0.28)
    e = sum(np.exp(-np.maximum(0, t - o) * (180.0 if k < 3 else 20.0)) * (t >= o)
            for k, o in enumerate((0.0, 0.008, 0.017, 0.026)))
    noise = bp(rng.standard_normal(len(t)), 900, 4200)
    return noise * e * 0.38

def hat_closed():
    t = tt(0.045)
    return hp(rng.standard_normal(len(t)), 8200) * np.exp(-t * 110.0) * 0.14

def hat_open():
    t = tt(0.30)
    return hp(rng.standard_normal(len(t)), 7200) * np.exp(-t * 12.0) * 0.11

def shaker():
    t = tt(0.065)
    return bp(rng.standard_normal(len(t)), 5500, 11500) * np.sin(np.pi * np.minimum(1.0, t / 0.065)) * 0.08

def snare():
    t = tt(0.24)
    body = np.sin(2.0 * np.pi * 210.0 * t) * np.exp(-t * 32.0) * 0.45
    noise = bp(rng.standard_normal(len(t)), 1600, 8500) * np.exp(-t * 24.0) * 0.35
    return (body + noise) * 0.36

def crash():
    t = tt(2.8)
    return hp(rng.standard_normal(len(t)), 4200) * np.exp(-t * 1.5) * 0.20

def sub_bass(f, d):
    t = tt(d)
    s = np.sin(2.0 * np.pi * f * t) + 0.38 * lp(saw(f, t), 550)
    return np.tanh(s * 1.5) * env(len(t), 0.004, 0.04) * 0.34

def stab_chord(f, d=BEAT * 0.42):
    s = supersaw(f, d, (-18, -8, 0, 8, 18))
    t = tt(d)
    dark, br = lp(s, 1200), lp(s, 5600)
    filt_env = dark + (br - dark) * np.exp(-t * 20.0)
    return hp(filt_env, 180) * env(len(t), 0.003, 0.04) * 0.18

def chord_pad(f, d, cutoff=2600):
    s = supersaw(f, d, (-24, -14, -5, 5, 14, 24))
    return hp(lp(s, cutoff), 220) * env(len(s), 0.03, 0.3) * 0.09

def lead_synth(f, d):
    t = tt(d)
    # Subtle pitch vibrato
    fm = f * (1.0 + 0.004 * np.sin(2.0 * np.pi * 5.8 * t) * np.minimum(1.0, t / 0.2))
    ph = np.cumsum(fm) / SR
    wave = np.sign(np.sin(2.0 * np.pi * ph)) * 0.5 + (2.0 * (ph % 1.0) - 1.0) * 0.5
    dark = lp(wave, 2000)
    bright = lp(wave, 7500)
    y = dark + (bright - dark) * np.exp(-t * 8.0) + 0.3 * np.sin(4.0 * np.pi * ph) * np.exp(-t * 5.0)
    return y * env(len(t), 0.003, min(0.12, d / 3.0)) * np.exp(-t * 1.1) * 0.22

# "Time passes" clockwork bell-pluck arpeggiator
def arp_pluck(f, d=0.18):
    t = tt(d)
    s = (np.sin(2.0 * np.pi * f * t) +
         0.45 * np.sin(4.0 * np.pi * f * t) * np.exp(-t * 18.0) +
         0.20 * np.sin(6.0 * np.pi * f * t) * np.exp(-t * 32.0))
    click = hp(rng.standard_normal(len(t)), 6000) * np.exp(-t * 250.0) * 0.12
    return (s * np.exp(-t * 12.0) + click) * 0.15

# SFX: Ticking clock, Risers, Impacts, Whooshes
def clock_tick(f=2800, d=0.03, g=0.25):
    t = tt(d)
    return (np.sin(2.0 * np.pi * f * t) * np.exp(-t * 180.0) +
            0.35 * hp(rng.standard_normal(len(t)), 4500) * np.exp(-t * 420.0)) * g

def riser(d, g=0.28):
    t = tt(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    L = len(t) // 40 + 1
    for b in range(40):
        c = 350.0 * (28.0 ** (b / 40.0))
        seg = n[b * L:(b + 1) * L]
        out[b * L:b * L + len(seg)] = bp(seg, c * 0.7, c * 1.4)
    sweep = np.sin(2.0 * np.pi * np.cumsum(220.0 * (2.0 ** (2.6 * t / d))) / SR) * 0.25
    return (out + sweep) * ((t / d) ** 2) * g

def impact(g=0.75):
    t = tt(2.0)
    sub = np.sin(2.0 * np.pi * np.cumsum(45.0 + 85.0 * np.exp(-t * 20.0)) / SR) * np.exp(-t * 2.5)
    noise = lp(rng.standard_normal(len(t)), 1400) * np.exp(-t * 6.5) * 0.4
    return np.tanh((sub + noise) * 1.5) * g

def whoosh(d=0.8, lo=300, hi=5500, g=0.32):
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

# Harmony & Chords: Uplifting A Major progression
# Chords: Dmaj7 (IV) -> E (V) -> F#m (vi) -> A (I)
CHORDS = {
    'D': ['D4', 'F#4', 'A4', 'C#5'],
    'E': ['E4', 'G#4', 'B4', 'E5'],
    'F#m': ['F#4', 'A4', 'C#5', 'F#5'],
    'A': ['E4', 'A4', 'C#5', 'E5']
}
ROOTS = {'D': 'D2', 'E': 'E2', 'F#m': 'F#2', 'A': 'A1'}
PROG = ['D', 'E', 'F#m', 'A']

# Arpeggio note sequences per chord (16th notes: 16 notes per bar)
ARP_NOTES = {
    'D': ['D5', 'F#5', 'A5', 'C#6', 'D6', 'C#6', 'A5', 'F#5', 'D5', 'F#5', 'A5', 'C#6', 'D6', 'E6', 'F#6', 'A6'],
    'E': ['E5', 'G#5', 'B5', 'E6', 'G#6', 'E6', 'B5', 'G#5', 'E5', 'G#5', 'B5', 'E6', 'F#6', 'E6', 'B5', 'G#5'],
    'F#m': ['F#5', 'A5', 'C#6', 'F#6', 'A6', 'F#6', 'C#6', 'A5', 'F#5', 'A5', 'C#6', 'E6', 'F#6', 'A6', 'C#7', 'F#6'],
    'A': ['A5', 'C#6', 'E6', 'A6', 'C#7', 'A6', 'E6', 'C#6', 'A5', 'C#6', 'E6', 'A6', 'B6', 'A6', 'E6', 'C#6']
}

# Melodic Hook: Enthusiastic, memorable, uplifting
HOOK = {
    'D': [(0.0, 'F#5', 0.5), (0.5, 'A5', 0.5), (1.0, 'C#6', 0.75), (1.75, 'B5', 0.5), (2.25, 'A5', 0.5), (2.75, 'F#5', 0.5), (3.25, 'A5', 0.75)],
    'E': [(0.0, 'G#5', 0.5), (0.5, 'B5', 0.5), (1.0, 'E6', 1.0), (2.0, 'D#6', 0.5), (2.5, 'B5', 0.5), (3.0, 'G#5', 0.5), (3.5, 'B5', 0.5)],
    'F#m': [(0.0, 'A5', 0.5), (0.5, 'C#6', 0.5), (1.0, 'F#6', 1.0), (2.0, 'E6', 0.5), (2.5, 'C#6', 0.5), (3.0, 'A5', 0.5), (3.5, 'C#6', 0.5)],
    'A': [(0.0, 'E5', 0.5), (0.5, 'A5', 0.5), (1.0, 'C#6', 0.75), (1.75, 'D6', 0.5), (2.25, 'C#6', 0.5), (2.75, 'B5', 0.5), (3.25, 'A5', 0.75)]
}

# 25-Bar Arrangement Structure
# 0..3: intro (0.0 - 9.6s)
# 4..7: groove (9.6 - 19.2s)
# 8..11: verse_lead (19.2 - 28.8s)
# 12..15: build (28.8 - 38.4s)
# 16..21: peak_drop (38.4 - 52.8s)
# 22..24: outro_fade (52.8 - 60.0s)
PLAN = (
    ['intro'] * 4 +
    ['groove'] * 4 +
    ['verse_lead'] * 4 +
    ['build'] * 4 +
    ['peak_drop'] * 6 +
    ['outro_fade'] * 3
)
assert len(PLAN) == TOTAL_BARS

LV = {
    'intro': dict(kick=0.5, pad=0.7, arp=0.8, shk=0.5, tick=1),
    'groove': dict(kick=1.0, clap=0.9, chh=0.8, ohh=0.7, bass=1.0, stab=1.0, pad=0.5, arp=0.7, shk=0.6),
    'verse_lead': dict(kick=1.0, clap=0.95, chh=0.85, ohh=0.8, bass=1.0, stab=0.9, pad=0.6, hook=1.0, arp=0.7, shk=0.7),
    'build': dict(pad=0.85, arp=1.0, tick=1, stab=0.8, bass=0.6),
    'peak_drop': dict(kick=1.05, clap=1.0, chh=0.95, ohh=0.9, bass=1.05, stab=1.0, pad=0.85, hook=1.1, arp=0.9, shk=0.8, big=1),
    'outro_fade': dict(pad=0.8, arp=0.75, stab=0.5, bass=0.4, chh=0.4)
}

print("Synthesizing Tune 01: 'Sunlight Drift'...")

for b, sec in enumerate(PLAN):
    b0 = b * BAR
    L = LV[sec]
    g = lambda k: L.get(k, 0.0)
    ch = PROG[b % 4]
    nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

    # Ticking clock rhythm for "time passing" sensation
    if g('tick'):
        for i in range(16):
            t_tick = b0 + i * (BEAT / 4.0)
            if t_tick < DUR:
                add(sfx, t_tick, clock_tick(3000 if i % 4 == 0 else 2400, 0.025, 0.06), pan=0.4)

    # Arpeggio (16th notes - sparkles and energetic flow)
    if g('arp'):
        arp_scale = g('arp')
        notes = ARP_NOTES[ch]
        for i in range(16):
            t_arp = b0 + i * (BEAT / 4.0)
            if t_arp < DUR:
                note_hz = hz(notes[i])
                pan_val = -0.5 + (i % 4) * 0.33
                sig = arp_pluck(note_hz, 0.22) * arp_scale
                add(music, t_arp, sig, 1.0, pan=pan_val, send=0.35)

    # 4 beats per bar
    for bt in range(4):
        tb = b0 + bt * BEAT
        if tb >= DUR:
            break

        # Kick
        if g('kick'):
            # Intro bar 0 kick is muted, starts on bar 1 softly
            if sec != 'intro' or b >= 1:
                kick_gain = g('kick') * (0.75 if (sec == 'intro' and b < 2) else 1.0)
                add(drums, tb, kick(), kick_gain)
                # Sidechain duck envelope
                i0 = int(tb * SR)
                i1 = min(N, int((tb + 0.35) * SR))
                pump[i0:i1] = np.minimum(pump[i0:i1], 0.26 + 0.74 * (np.linspace(0, 1, i1 - i0) ** 0.7))

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
            # Offbeat Chord Stab
            if g('stab'):
                for k_i, nn in enumerate(CHORDS[ch]):
                    add(music, off, stab_chord(hz(nn)), g('stab') * 0.85, pan=(-0.5, -0.15, 0.15, 0.5)[k_i], send=0.2)
            # Bassline: Offbeat sub bass
            if g('bass'):
                add(music, off, sub_bass(hz(ROOTS[ch]), BEAT * 0.45), g('bass'))
                if bt == 3:  # Bouncy octave jump before next bar
                    add(music, tb + BEAT * 0.75, sub_bass(hz(ROOTS[ch]) * 2.0, BEAT * 0.22), g('bass') * 0.65)

    # Sustained Chord Pad
    if g('pad'):
        d_pad = min(BAR + 0.1, DUR - b0)
        for k_i, nn in enumerate(CHORDS[ch]):
            add(music, b0, chord_pad(hz(nn), d_pad, cutoff=2800), g('pad'), pan=(-0.6, -0.2, 0.2, 0.6)[k_i], send=0.35)

    # Melodic Hook
    if g('hook'):
        for o, nn, ln in HOOK[ch]:
            ts = b0 + o * BEAT
            if ts < DUR:
                sig = lead_synth(hz(nn), ln * BEAT * 0.95) * g('hook')
                if g('big'):
                    # Layer 1 octave higher in the big peak section
                    sig_oct = lead_synth(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
                    max_len = max(len(sig), len(sig_oct))
                    sig_combined = np.zeros(max_len, dtype=np.float32)
                    sig_combined[:len(sig)] += sig
                    sig_combined[:len(sig_oct)] += sig_oct
                    sig = sig_combined
                add(music, ts, sig, 1.0, pan=0.0, send=0.35)
                # Stereo delay reflections
                for r, (dl, pn) in enumerate(((0.75, -0.55), (1.5, 0.55), (2.25, -0.35))):
                    delayed_t = ts + dl * BEAT
                    if delayed_t < DUR:
                        add(music, delayed_t, lp(sig, 3400) * (0.42 ** (r + 1)), 0.9, pan=pn)

    # Transitions & Builds
    if sec == 'build' and nxt == 'peak_drop':
        # Snare roll accelerating into the drop
        start = b0
        end = b0 + BAR
        t_snare = start
        for div, frac in ((2, 0.4), (4, 0.75), (8, 1.0)):
            while t_snare < start + (end - start) * frac - 1e-5:
                vol = (0.25 + 0.75 * ((t_snare - start) / (end - start)) ** 1.6) * 0.95
                add(drums, t_snare, snare(), vol, send=0.2)
                t_snare += BEAT / div
        add(sfx, start, riser(BAR, 0.32))

    if sec == 'peak_drop' and (b == 0 or PLAN[b - 1] != 'peak_drop'):
        # Crash & impact hit at the drop
        add(drums, b0, crash(), 1.0, send=0.35)
        add(sfx, b0, impact(0.7), send=0.3)
        add(sfx, b0, whoosh(0.9, 250, 6000, 0.3))

# Dynamic Filter Sweeps for the music bus
def ramp_filter(a, b, v0, v1):
    i0, i1 = int(a * SR), min(N, int(b * SR))
    if i1 > i0:
        filt[i0:i1] = np.linspace(v0, v1, i1 - i0)

# Filter opens up during intro, drops at build, surges at drop
ramp_filter(0.0, 9.6, 0.25, 0.95)
ramp_filter(28.8, 38.4, 0.40, 1.0)
ramp_filter(52.8, 60.0, 1.0, 0.35)

print("Applying mixing, sidechain pump & convolution reverb...")

# Music filtering & sidechain pumping
mus_lp = np.stack([lp(music[:, c], 650) for c in range(2)], axis=1)
music = (mus_lp + (music - mus_lp) * filt[:, None]) * pump[:, None]

# Stereo Impulse Response for Reverb (2.4s decaying stereo noise)
ir_t = tt(2.2)
ir = np.stack([lp(rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 2.7), 6800) for _ in range(2)], axis=1)
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
mix = mix / (rms * 6.6)
mix = np.tanh(mix * 1.25) / np.tanh(1.25)
mix /= np.abs(mix).max()

# Smooth Fade In (first 0.05s) and Master Fade Out across last 6.5 seconds into silence
fade = np.ones(N, dtype=np.float32)
fade_in_len = int(0.05 * SR)
fade[:fade_in_len] = np.linspace(0, 1, fade_in_len)

fade_out_len = int(6.5 * SR)
fade[-fade_out_len:] = np.linspace(1, 0, fade_out_len) ** 1.5
mix *= fade[:, None] * 0.92

# Export WAV
here = os.path.dirname(os.path.abspath(__file__))
wav_out = os.path.join(here, 'tune_01_sunlight_drift.wav')
mp3_out = os.path.join(here, 'tune_01_sunlight_drift.mp3')

wavfile.write(wav_out, SR, (mix * 32767).astype(np.int16))
print(f"Generated WAV: {wav_out} (Peak: {round(float(np.abs(mix).max()), 3)})")

# Export high quality MP3
cmd = ['ffmpeg', '-y', '-i', wav_out, '-b:a', '320k', mp3_out]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"Generated MP3: {mp3_out}")
