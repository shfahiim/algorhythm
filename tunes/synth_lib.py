"""Shared DSP Synthesis Engine & Instrument Toolkit for Procedural Tunes.
Provides mathematical waveform synthesis, state-of-the-art Butterworth filtering,
sidechain ducking, algorithmic convolution reverb, and master tape saturation.
"""

import os
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000

NAMES = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

def hz(note):
    """Convert note name like 'C4', 'F#5', 'Bb2' to Hz."""
    name = note[:-1]
    octave = int(note[-1])
    semitones = NAMES[name] + 12 * (octave + 1) - 69
    return 440.0 * (2.0 ** (semitones / 12.0))

def tt(d):
    """Time vector for duration d in seconds."""
    return np.arange(int(d * SR)) / SR

def lp(x, fc, o=2):
    """Butterworth low-pass filter."""
    return sosfilt(butter(o, min(fc, SR / 2 - 100), 'low', fs=SR, output='sos'), x)

def hp(x, fc, o=2):
    """Butterworth high-pass filter."""
    return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)

def bp(x, lo, hi, o=2):
    """Butterworth band-pass filter."""
    return sosfilt(butter(o, [lo, min(hi, SR / 2 - 100)], 'band', fs=SR, output='sos'), x)

def env(n, a=0.005, r=0.08):
    """Attack-Release amplitude envelope."""
    e = np.ones(n, dtype=np.float32)
    na = int(a * SR)
    nr = int(r * SR)
    if 0 < na < n:
        e[:na] = np.linspace(0, 1, na)
    if 0 < nr < n:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e

def saw(f, t, ph=0.0):
    """Sawtooth wave."""
    return 2.0 * ((f * t + ph) % 1.0) - 1.0

def pulse(f, t, duty=0.5, ph=0.0):
    """Pulse / Square wave with variable duty cycle."""
    return np.where(((f * t + ph) % 1.0) < duty, 1.0, -1.0)

def supersaw(f, d, voices=(-20, -11, -3, 3, 11, 20), rng=None):
    """Multi-oscillator detuned supersaw."""
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    s = np.zeros_like(t)
    for c in voices:
        s += saw(f * (2.0 ** (c / 1200.0)), t, rng.uniform())
    return s / len(voices)

def pluck_chime(f, d, brightness=0.5, damping=14.0, rng=None):
    """Sparkling bell/chime/marimba pluck with harmonic overtones."""
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    s = (
        np.sin(2.0 * np.pi * f * t) * 1.0 +
        np.sin(2.0 * np.pi * f * 2.0 * t) * (0.45 * brightness) * np.exp(-t * (damping * 1.2)) +
        np.sin(2.0 * np.pi * f * 3.01 * t) * (0.25 * brightness) * np.exp(-t * (damping * 1.8)) +
        np.sin(2.0 * np.pi * f * 4.16 * t) * (0.15 * brightness) * np.exp(-t * (damping * 2.5))
    )
    click = hp(rng.standard_normal(len(t)), 6000) * np.exp(-t * 280.0) * 0.12
    return (s * np.exp(-t * damping) + click) * 0.16

def organ_timbre(f, d, drawbars=(1.0, 0.7, 0.4, 0.3)):
    """Rich drawbar organ / electric piano tone."""
    t = tt(d)
    s = np.zeros_like(t)
    mults = (1.0, 2.0, 3.0, 4.0)
    for m, g in zip(mults, drawbars):
        s += g * np.sin(2.0 * np.pi * f * m * t)
    return s * env(len(t), 0.005, min(0.15, d / 3.0)) * 0.16

# Standard Percussion
def synth_kick(f_start=160.0, f_end=48.0, decay=7.0, click_vol=0.35, d=0.40, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    f = f_end + (f_start - f_end) * np.exp(-t * 36.0)
    body = np.sin(2.0 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay)
    click = lp(rng.standard_normal(len(t)), 4800) * np.exp(-t * 300.0) * click_vol
    return np.tanh((body + click) * 1.7) * 0.82

def synth_clap(d=0.28, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    e = sum(np.exp(-np.maximum(0, t - o) * (180.0 if k < 3 else 20.0)) * (t >= o)
            for k, o in enumerate((0.0, 0.008, 0.017, 0.026)))
    noise = bp(rng.standard_normal(len(t)), 900, 4200)
    return noise * e * 0.38

def synth_hat_closed(d=0.045, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    return hp(rng.standard_normal(len(t)), 8200) * np.exp(-t * 110.0) * 0.14

def synth_hat_open(d=0.30, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    return hp(rng.standard_normal(len(t)), 7200) * np.exp(-t * 12.0) * 0.11

def synth_shaker(d=0.065, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    return bp(rng.standard_normal(len(t)), 5500, 11500) * np.sin(np.pi * np.minimum(1.0, t / 0.065)) * 0.08

def synth_snare(pitch=210.0, d=0.24, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    body = np.sin(2.0 * np.pi * pitch * t) * np.exp(-t * 32.0) * 0.45
    noise = bp(rng.standard_normal(len(t)), 1600, 8500) * np.exp(-t * 24.0) * 0.35
    return (body + noise) * 0.36

def synth_crash(d=2.8, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    return hp(rng.standard_normal(len(t)), 4200) * np.exp(-t * 1.5) * 0.20

def synth_tick(f=2800, d=0.03, g=0.25, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    return (np.sin(2.0 * np.pi * f * t) * np.exp(-t * 180.0) +
            0.35 * hp(rng.standard_normal(len(t)), 4500) * np.exp(-t * 420.0)) * g

def synth_riser(d, f_start=220.0, f_mult=2.6, g=0.28, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    L = len(t) // 40 + 1
    for b_idx in range(40):
        c = 350.0 * (28.0 ** (b_idx / 40.0))
        seg = n[b_idx * L:(b_idx + 1) * L]
        out[b_idx * L:b_idx * L + len(seg)] = bp(seg, c * 0.7, c * 1.4)
    sweep = np.sin(2.0 * np.pi * np.cumsum(f_start * (2.0 ** (f_mult * t / d))) / SR) * 0.25
    return (out + sweep) * ((t / d) ** 2) * g

def synth_impact(g=0.75, d=2.0, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    sub = np.sin(2.0 * np.pi * np.cumsum(45.0 + 85.0 * np.exp(-t * 20.0)) / SR) * np.exp(-t * 2.5)
    noise = lp(rng.standard_normal(len(t)), 1400) * np.exp(-t * 6.5) * 0.4
    return np.tanh((sub + noise) * 1.5) * g

def synth_whoosh(d=0.8, lo=300, hi=5500, g=0.32, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)
    t = tt(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    L = len(t) // 24 + 1
    for b_idx in range(24):
        c = lo * ((hi / lo) ** (np.sin(np.pi * b_idx / 23.0) ** 0.8))
        seg = n[b_idx * L:(b_idx + 1) * L]
        out[b_idx * L:b_idx * L + len(seg)] = bp(seg, c * 0.6, c * 1.6)
    rise = 0.6
    env_w = np.where(t < d * rise, (t / (d * rise)) ** 2, np.exp(-(t - d * rise) / (d * (1 - rise) / 3.0)))
    return out * env_w * g


class MusicEngine:
    """Manages audio buses, timing grid, sidechain, reverb, and mastering."""
    def __init__(self, bpm, total_bars, dur=60.0, seed=42):
        self.dur = dur
        self.sr = SR
        self.n = int(SR * dur)
        self.bpm = bpm
        self.beat = 60.0 / bpm
        self.bar = self.beat * 4.0
        self.total_bars = total_bars
        self.rng = np.random.default_rng(seed)

        self.drums = np.zeros((self.n, 2), dtype=np.float32)
        self.music = np.zeros((self.n, 2), dtype=np.float32)
        self.sfx = np.zeros((self.n, 2), dtype=np.float32)
        self.verb_send = np.zeros((self.n, 2), dtype=np.float32)
        self.pump = np.ones(self.n, dtype=np.float32)
        self.filt = np.ones(self.n, dtype=np.float32)

    def add(self, bus_name, t0, sig, gain=1.0, pan=0.0, send=0.0):
        if bus_name == 'drums':
            bus = self.drums
        elif bus_name == 'music':
            bus = self.music
        elif bus_name == 'sfx':
            bus = self.sfx
        else:
            bus = self.music

        i0 = int(round(t0 * self.sr))
        if i0 >= self.n or len(sig) == 0:
            return
        if i0 < 0:
            sig = sig[-i0:]
            i0 = 0
        sig = sig[: self.n - i0]
        l = np.cos((pan + 1.0) * np.pi / 4.0) * gain
        r = np.sin((pan + 1.0) * np.pi / 4.0) * gain
        bus[i0:i0 + len(sig), 0] += sig * l
        bus[i0:i0 + len(sig), 1] += sig * r
        if send > 0:
            self.verb_send[i0:i0 + len(sig), 0] += sig * l * send
            self.verb_send[i0:i0 + len(sig), 1] += sig * r * send

    def duck(self, t0, duration=0.32, min_gain=0.26):
        i0 = int(t0 * self.sr)
        i1 = min(self.n, int((t0 + duration) * self.sr))
        if i1 > i0:
            self.pump[i0:i1] = np.minimum(
                self.pump[i0:i1],
                min_gain + (1.0 - min_gain) * (np.linspace(0, 1, i1 - i0) ** 0.7)
            )

    def ramp_filter(self, t_start, t_end, v0, v1):
        i0 = int(t_start * self.sr)
        i1 = min(self.n, int(t_end * self.sr))
        if i1 > i0:
            self.filt[i0:i1] = np.linspace(v0, v1, i1 - i0)

    def export(self, wav_path, mp3_path=None, fade_out_sec=6.5):
        # Filter and sidechain music
        mus_lp = np.stack([lp(self.music[:, c], 680) for c in range(2)], axis=1)
        music_proc = (mus_lp + (self.music - mus_lp) * self.filt[:, None]) * self.pump[:, None]

        # Convolution Reverb
        ir_t = tt(2.2)
        ir = np.stack([lp(self.rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 2.7), 6800) for _ in range(2)], axis=1)
        ir /= np.sqrt((ir ** 2).sum(axis=0))
        send_total = self.verb_send + music_proc * 0.12
        wet = np.stack([fftconvolve(send_total[:, c], ir[:, c])[:self.n] for c in range(2)], axis=1)

        # Mixdown
        mix = self.drums * 0.95 + music_proc + self.sfx * 0.85 + wet * 0.42

        # 30Hz highpass rumble filter
        for c in range(2):
            mix[:, c] = hp(mix[:, c], 30)

        # RMS Normalization & Soft Tape Saturation
        rms = np.sqrt(np.mean(mix ** 2))
        mix = mix / (rms * 6.5)
        mix = np.tanh(mix * 1.25) / np.tanh(1.25)
        mix /= np.abs(mix).max()

        # Fades
        fade = np.ones(self.n, dtype=np.float32)
        fi = int(0.05 * self.sr)
        fade[:fi] = np.linspace(0, 1, fi)
        fo = int(fade_out_sec * self.sr)
        fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
        mix *= fade[:, None] * 0.92

        # Write WAV
        wavfile.write(wav_path, self.sr, (mix * 32767).astype(np.int16))
        print(f"Generated WAV: {wav_path} (Peak: {round(float(np.abs(mix).max()), 3)})")

        # Encode MP3 if requested
        if mp3_path:
            cmd = ['ffmpeg', '-y', '-i', wav_path, '-b:a', '320k', mp3_path]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Generated MP3: {mp3_path}")
