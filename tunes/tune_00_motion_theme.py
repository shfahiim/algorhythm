"""MedWise film score v2: upbeat, feel-good house at 96 BPM, energetic start to finish.
(v1, the moody drone version, is kept in score_v1_moody.py.)

    python3 audio/score.py  →  audio/score.wav (48 kHz stereo, 120 s)
"""
import os

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
DUR = 120.0
N = int(SR * DUR)
BPM = 96
BEAT = 60 / BPM
BAR = BEAT * 4
rng = np.random.default_rng(11)
WARP = [(0, 0), (7.5, 10), (17.5, 22.5), (21.25, 30), (25, 35), (32.5, 45), (42.5, 57.5), (55, 75), (62.5, 85), (120, 142.5)]


def film(s):
    for (f0, s0), (f1, s1) in zip(WARP, WARP[1:]):
        if s <= s1:
            return f0 + (s - s0) * (f1 - f0) / (s1 - s0)
    (f0, s0), (f1, s1) = WARP[-2], WARP[-1]
    return f0 + (s - s0) * (f1 - f0) / (s1 - s0)


NAMES = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def hz(note):
    return 440.0 * 2 ** ((NAMES[note[:-1]] + 12 * (int(note[-1]) + 1) - 69) / 12)


drums = np.zeros((N, 2)); music = np.zeros((N, 2)); sfx = np.zeros((N, 2)); verb_send = np.zeros((N, 2))
pump = np.ones(N); filt = np.ones(N)


def add(bus, t0, sig, gain=1.0, pan=0.0, send=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or len(sig) == 0:
        return
    if i0 < 0:
        sig, i0 = sig[-i0:], 0
    sig = sig[: N - i0]
    l, r = np.cos((pan + 1) * np.pi / 4) * gain, np.sin((pan + 1) * np.pi / 4) * gain
    bus[i0:i0 + len(sig), 0] += sig * l; bus[i0:i0 + len(sig), 1] += sig * r
    if send:
        verb_send[i0:i0 + len(sig), 0] += sig * l * send; verb_send[i0:i0 + len(sig), 1] += sig * r * send


def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, fc, o=2): return sosfilt(butter(o, min(fc, SR / 2 - 100), 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, min(hi, SR / 2 - 100)], 'band', fs=SR, output='sos'), x)


def env(n, a=0.005, r=0.08):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr and nr < n: e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def mixsig(*s):
    out = np.zeros(max(len(x) for x in s))
    for x in s: out[:len(x)] += x
    return out


def saw(f, t, ph=0.0): return 2 * ((f * t + ph) % 1.0) - 1


def supersaw(f, d, voices=(-18, -9, 0, 9, 18)):
    t = tt(d)
    return sum(saw(f * 2 ** (c / 1200), t, rng.uniform()) for c in voices) / len(voices)


def stab(f, d=BEAT * 0.45):
    s = supersaw(f, d); t = tt(d); dark, br = lp(s, 1100), lp(s, 5200)
    return hp(dark + (br - dark) * np.exp(-t * 22), 180) * env(len(t), 0.003, 0.05) * 0.16


def chord_pad(f, d, cutoff=2400):
    s = supersaw(f, d, (-22, -12, -4, 4, 12, 22))
    return hp(lp(s, cutoff), 200) * env(len(s), 0.02, 0.25) * 0.085


def lead(f, d):
    t = tt(d); fm = f * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.25)); ph = np.cumsum(fm) / SR
    sq = np.sign(np.sin(2 * np.pi * ph)) * 0.55 + (2 * (ph % 1) - 1) * 0.45
    dark, br = lp(sq, 1800), lp(sq, 7000)
    y = dark + (br - dark) * np.exp(-t * 9) + 0.35 * np.sin(4 * np.pi * ph) * np.exp(-t * 6)
    return y * env(len(t), 0.004, min(0.12, d / 3)) * np.exp(-t * 1.2) * 0.2


def sub_bass(f, d):
    t = tt(d)
    return np.tanh((np.sin(2 * np.pi * f * t) + 0.35 * lp(saw(f, t), 600)) * 1.4) * env(len(t), 0.004, 0.04) * 0.3


def kick():
    t = tt(0.42); f = 46 + 110 * np.exp(-t * 32)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5) + lp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 260) * 0.35
    return np.tanh(s * 1.6) * 0.75


def clap():
    t = tt(0.3)
    e = sum(np.exp(-np.maximum(0, t - o) * (170 if k < 3 else 16)) * (t >= o) for k, o in enumerate((0, 0.009, 0.018, 0.027)))
    return bp(rng.standard_normal(len(t)), 900, 4000) * e * 0.32


def snare():
    t = tt(0.22)
    return (np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5 + bp(rng.standard_normal(len(t)), 1500, 8000) * np.exp(-t * 22)) * 0.3


def hat_closed(): t = tt(0.05); return hp(rng.standard_normal(len(t)), 8000) * np.exp(-t * 90) * 0.12
def hat_open(): t = tt(0.32); return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * 11) * 0.09
def shaker(): t = tt(0.07); return bp(rng.standard_normal(len(t)), 5000, 11000) * np.sin(np.pi * np.minimum(1, t / 0.07)) * 0.07
def crash(): t = tt(2.6); return hp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 1.6) * 0.16


def riser(d, g=0.25):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(t); L = len(t) // 40 + 1
    for b in range(40):
        c = 300 * 30 ** (b / 40); seg = n[b * L:(b + 1) * L]; out[b * L:b * L + len(seg)] = bp(seg, c * 0.7, c * 1.4)
    return (out + np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2.5 * t / d)) / SR) * 0.25) * (t / d) ** 2 * g


def impact(g=0.8):
    t = tt(2.0)
    s = np.sin(2 * np.pi * np.cumsum(40 + 80 * np.exp(-t * 18)) / SR) * np.exp(-t * 2.4) + lp(rng.standard_normal(len(t)), 1200) * np.exp(-t * 6) * 0.4
    return np.tanh(s * 1.5) * g


def whoosh(d=0.8, lo=300, hi=5000, g=0.35, rise=0.6):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(t); L = len(t) // 24 + 1
    for b in range(24):
        c = lo * (hi / lo) ** (np.sin(np.pi * b / 23) ** 0.8); seg = n[b * L:(b + 1) * L]; out[b * L:b * L + len(seg)] = bp(seg, c * 0.6, c * 1.6)
    return out * np.where(t < d * rise, (t / (d * rise)) ** 2, np.exp(-(t - d * rise) / (d * (1 - rise) / 3))) * g


def tick(f=2600, d=0.03, g=0.25):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 160) + 0.4 * hp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 400)) * g


def bell(f, d=2.0, g=0.25):
    t = tt(d)
    return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) for r, a, k in ((1, 1, 1.8), (2.0, .5, 2.6), (2.76, .3, 3.5), (5.4, .12, 6))) * np.minimum(1, t / 0.002) * g


def pop(f0=520, f1=880, d=0.09, g=0.22):
    t = tt(d); return np.sin(2 * np.pi * np.cumsum(f0 + (f1 - f0) * (t / d)) / SR) * np.exp(-t * 45) * g


def shutter():
    t = tt(0.12); a = hp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 300); b = np.zeros_like(t); o = int(0.045 * SR)
    b[o:] = hp(rng.standard_normal(len(t) - o), 1200) * np.exp(-t[:len(t) - o] * 220)
    return (a + 0.8 * b) * 0.35


CH = {'D': ['D4', 'F#4', 'A4', 'D5'], 'A': ['C#4', 'E4', 'A4', 'C#5'], 'Bm': ['D4', 'F#4', 'B4', 'D5'], 'G': ['D4', 'G4', 'B4', 'D5']}
ROOT = {'D': 'D2', 'A': 'A1', 'Bm': 'B1', 'G': 'G1'}
MAJOR = ['D', 'A', 'Bm', 'G']
TENSE = ['Bm', 'G', 'D', 'A']
HOOK = {
    'D': [(0, 'F#5', .5), (.5, 'A5', .5), (1, 'F#5', .5), (1.5, 'E5', .5), (2, 'D5', 1), (3, 'E5', .5), (3.5, 'F#5', .5)],
    'A': [(0, 'E5', .5), (.5, 'C#5', .5), (1, 'E5', .5), (1.5, 'A5', 1.5), (3, 'E5', .5), (3.5, 'C#5', .5)],
    'Bm': [(0, 'D5', .5), (.5, 'F#5', .5), (1, 'B5', 1), (2, 'A5', .5), (2.5, 'F#5', .5), (3, 'D5', 1)],
    'G': [(0, 'B4', .5), (.5, 'D5', .5), (1, 'G5', .5), (1.5, 'F#5', .5), (2, 'E5', 1), (3, 'D5', .5), (3.5, 'E5', .5)],
}
COUNTER = {'D': [(2.5, 'A5', .5), (3, 'F#5', .5)], 'A': [(2.5, 'E5', .5), (3, 'C#5', .5)], 'Bm': [(2.5, 'F#5', .5), (3, 'D5', .5)], 'G': [(2.5, 'B5', .5), (3, 'A5', .5)]}

PLAN = (['intro'] * 3 + ['drive'] * 4 + ['build'] * 2 + ['break'] + ['rise'] * 2 + ['drop'] + ['verse'] * 4 + ['verse2'] * 8
        + ['chorus'] * 8 + ['brief'] * 4 + ['big'] * 3 + ['light'] * 3 + ['drop'] * 2 + ['outro'] * 3)
assert len(PLAN) == 48
FREEZE = film(30)
CLOCK_STOP = film(115.0)
LV = {
    'intro': dict(kick=0.7, chh=0.5, stab=0.9, bass=0.5, shk=0.6),
    'drive': dict(kick=1, clap=0.9, chh=0.8, ohh=0.6, bass=1, stab=1, pad=0.5, tense=1),
    'build': dict(kick=1, clap=0.9, chh=0.9, ohh=0.7, bass=1, stab=1, pad=0.7, tense=1),
    'break': dict(pad=0.7, tense=1),
    'rise': dict(half=0.8, chh=0.5, stab=0.9, pad=0.6, bass=0.6),
    'drop': dict(kick=1, clap=1, chh=0.9, ohh=0.9, bass=1, stab=0.8, pad=1, hook=1),
    'verse': dict(kick=1, clap=0.8, chh=0.8, shk=0.6, bass=1, stab=1, pad=0.4),
    'verse2': dict(kick=1, clap=0.9, chh=0.85, ohh=0.6, shk=0.5, bass=1, stab=1, pad=0.5, counter=0.9),
    'chorus': dict(kick=1, clap=1, chh=0.9, ohh=0.9, bass=1, stab=0.7, pad=1, hook=1),
    'brief': dict(half=0.8, chh=0.6, shk=0.6, bass=0.7, stab=0.9, pad=0.6),
    'big': dict(kick=1.05, clap=1, chh=1, ohh=1, bass=1.05, stab=0.8, pad=1.1, hook=1.1),
    'light': dict(kick=0.9, clap=0.7, chh=0.7, shk=0.6, bass=0.9, stab=0.9, pad=0.4, counter=0.7),
    'outro': dict(stab=0.8, pad=0.9, bass=0.5, chh=0.4),
}

for b, sec in enumerate(PLAN):
    b0 = b * BAR; L = LV[sec]; g = lambda k: L.get(k, 0)
    ch = (TENSE if g('tense') else MAJOR)[b % 4]
    nxt = PLAN[b + 1] if b + 1 < 48 else None
    stop = FREEZE if b0 <= FREEZE < b0 + BAR else 1e9
    for bt in range(4):
        tb = b0 + bt * BEAT
        if tb >= stop: break
        if g('kick') or (g('half') and bt in (0, 2)):
            add(drums, tb, kick(), g('kick') or g('half'))
            i0, i1 = int(tb * SR), min(N, int((tb + 0.32) * SR))
            pump[i0:i1] = np.minimum(pump[i0:i1], 0.28 + 0.72 * np.linspace(0, 1, i1 - i0) ** 0.7)
        if g('clap') and bt in (1, 3): add(drums, tb, clap(), g('clap'), send=0.25)
        for q in range(4):
            tq = tb + q * BEAT / 4
            if tq >= stop: break
            if g('chh') and q in (1, 3): add(drums, tq, hat_closed(), g('chh') * (1 if q == 3 else 0.6), pan=0.3)
            if g('shk'): add(drums, tq, shaker(), g('shk') * (1 if q % 2 else 0.6), pan=-0.35)
        off = tb + BEAT / 2
        if off >= stop: continue
        if g('ohh'): add(drums, off, hat_open(), g('ohh'), pan=0.2)
        if g('stab'):
            for k, nn in enumerate(CH[ch]): add(music, off, stab(hz(nn)), g('stab') * 0.8, pan=(-0.5, -0.15, 0.15, 0.5)[k])
        if g('bass'):
            add(music, off, sub_bass(hz(ROOT[ch]), BEAT * 0.42), g('bass'))
            if bt == 3: add(music, tb + BEAT * 0.75, sub_bass(hz(ROOT[ch]) * 2, BEAT * 0.2), g('bass') * 0.6)
    if g('pad'):
        d = min(BAR, stop - b0)
        for k, nn in enumerate(CH[ch]): add(music, b0, chord_pad(hz(nn), d + 0.05), g('pad'), pan=(-0.6, -0.2, 0.2, 0.6)[k], send=0.3)
    for key, table, scale in (('hook', HOOK, 1.0), ('counter', COUNTER, 0.7)):
        if not g(key): continue
        for o, nn, ln in table[ch]:
            sig = lead(hz(nn), ln * BEAT * 0.95) * scale
            if sec == 'big' and key == 'hook': sig = mixsig(sig, lead(hz(nn) * 2, ln * BEAT * 0.95) * 0.45)
            ts = b0 + o * BEAT
            add(music, ts, sig, g(key), send=0.3)
            for r, (dl, pn) in enumerate(((0.75, -0.6), (1.5, 0.6), (2.25, -0.4))):
                add(music, ts + dl * BEAT, lp(sig, 3500) * 0.42 ** (r + 1), g(key), pan=pn)
    # snare-roll builds into drops
    if (sec == 'build' and nxt != 'build') or (sec == 'rise' and nxt != 'rise') or (sec == 'brief' and nxt == 'big') or (sec == 'verse2' and nxt == 'chorus') or (sec == 'light' and nxt == 'drop'):
        end = FREEZE if sec == 'build' else b0 + BAR
        start = end - BAR; t_ = start
        for div, frac in ((2, 0.5), (4, 0.8), (8, 1.0)):
            while t_ < start + (end - start) * frac - 1e-6:
                add(drums, t_, snare(), (0.25 + 0.75 * ((t_ - start) / (end - start)) ** 1.5) * 0.9, send=0.15); t_ += BEAT / div
        add(sfx, start, riser(end - start, 0.2))
    if sec in ('drop', 'chorus', 'big') and (b == 0 or PLAN[b - 1] != sec):
        add(drums, b0, crash(), 1.0, send=0.3); add(sfx, b0, impact(0.55))


def ramp(a, b, v0, v1):
    i0, i1 = int(a * SR), int(b * SR); filt[i0:i1] = np.linspace(v0, v1, i1 - i0)


ramp(0, 7.5, 0.15, 0.7); ramp(7.5, 17.5, 0.7, 0.85); ramp(17.5, FREEZE, 0.85, 1.0); ramp(FREEZE, 25, 0.2, 0.2)
ramp(25, 30, 0.25, 0.9); ramp(82.5, CLOCK_STOP, 0.35, 0.95); ramp(112.5, 120, 0.9, 0.3)

# story SFX (quieter; the music carries the energy)
for s_ in (5.45, 6.05, 6.6): add(sfx, film(s_), mixsig(tick(1500, 0.04, 0.3), tick(3200, 0.02, 0.15)), 0.7)
add(sfx, film(7.5), impact(0.45)); add(sfx, film(7.5), bell(hz('D6'), 1.6, 0.08), send=0.6)
add(sfx, film(11.15), whoosh(1.2, 200, 6000, 0.35), send=0.3)
for k in range(1, 49): add(sfx, film(10 + k * 20 / 48), tick(2800 if k < 38 else 3200, 0.025, 0.07 + 0.05 * k / 48), pan=0.6)
add(sfx, FREEZE, impact(0.9), send=0.5); add(sfx, FREEZE, bell(hz('D5'), 2.5, 0.1), send=0.8)
add(sfx, film(41.25), bell(hz('A5'), 2.0, 0.07), pan=-0.2, send=0.7); add(sfx, film(41.25) + 0.06, bell(hz('D6'), 2.0, 0.06), pan=0.2, send=0.7)
add(sfx, film(44.35), whoosh(0.7, 400, 8000, 0.25)); add(sfx, film(47.4), pop(500, 820), 0.9)
for s_ in (49.4, 50.65, 51.9): add(sfx, film(s_), shutter(), 0.9, send=0.15)
add(sfx, film(55.9), whoosh(0.9, 300, 6000, 0.2))
for i in range(3):
    add(sfx, film(61.2 + i * 0.55 + 0.8), pop(700, 1100, 0.07, 0.15), pan=0.4); add(sfx, film(68.4 + i * 0.45 + 0.8), pop(700, 1100, 0.07, 0.15), pan=0.4)
add(sfx, film(66.25), whoosh(0.6, 300, 5000, 0.18)); add(sfx, film(76.9), pop(600, 900, 0.07, 0.18)); add(sfx, film(80.6), pop(450, 700, 0.09, 0.24))
add(sfx, film(80.9), bell(hz('A5'), 1.2, 0.06), send=0.4); add(sfx, film(81.05), bell(hz('D6'), 1.5, 0.06), send=0.4)
add(sfx, film(93.3), bell(hz('E5'), 1.5, 0.07), send=0.4); add(sfx, film(93.4), bell(hz('A5'), 1.8, 0.07), send=0.4)
add(sfx, film(102.95), bell(hz('F#5'), 1.5, 0.07), send=0.5); add(sfx, film(103.05), bell(hz('B5'), 1.8, 0.07), send=0.5)
add(sfx, film(104.7), whoosh(0.8, 200, 4000, 0.2))
for i in range(1, 11): add(sfx, film(109.8 + i * 0.52), tick(2400, 0.03, 0.12), pan=0.6)
add(sfx, CLOCK_STOP, bell(hz('D6'), 2.5, 0.1), send=0.6)
for s_ in (122.6, 124.4, 126.2, 128.0): add(sfx, film(s_), pop(600, 950, 0.08, 0.17))
add(sfx, film(130.6), whoosh(1.1, 200, 4000, 0.2), send=0.3); add(sfx, film(130.7), bell(hz('D6'), 3, 0.07), send=0.8)
for k, nn in enumerate(['D4', 'F#4', 'A4', 'D5', 'A5']):
    add(music, 112.5, chord_pad(hz(nn), 7.5) * np.linspace(1, 0, int(7.5 * SR)) ** 0.8, 0.9, pan=(-0.6, -0.3, 0, 0.3, 0.6)[k], send=0.6)
for o, nn, ln in HOOK['D'][:5]: add(music, 113.75 + o * BEAT * 1.5, lead(hz(nn), ln * BEAT * 1.4) * 0.8, 0.8, send=0.6)

# mix
mus_lp = np.stack([lp(music[:, c], 700) for c in range(2)], axis=1)
music = (mus_lp + (music - mus_lp) * filt[:, None]) * pump[:, None]
ir_t = tt(2.4)
ir = np.stack([lp(rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 2.8), 7000) for _ in range(2)], axis=1)
ir /= np.sqrt((ir ** 2).sum(axis=0))
send_total = verb_send + music * 0.1
wet = np.stack([fftconvolve(send_total[:, c], ir[:, c])[:N] for c in range(2)], axis=1)
mix = drums * 0.95 + music + sfx * 0.9 + wet * 0.45
for c in range(2): mix[:, c] = hp(mix[:, c], 30)
mix = mix / (np.sqrt(np.mean(mix ** 2)) * 6.5)
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
mix /= np.abs(mix).max()
fade = np.ones(N); fl = int(2.0 * SR); fade[-fl:] = np.linspace(1, 0, fl) ** 1.3; fade[:960] = np.linspace(0, 1, 960)
mix *= fade[:, None] * 0.89
out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'audio'))
wav_out = os.path.join(out_dir, 'wav', 'tune_00_motion_theme.wav') if os.path.exists(os.path.join(out_dir, 'wav')) else os.path.join(os.path.dirname(__file__), 'tune_00_motion_theme.wav')
mp3_out = os.path.join(out_dir, 'mp3', 'tune_00_motion_theme.mp3') if os.path.exists(os.path.join(out_dir, 'mp3')) else os.path.join(os.path.dirname(__file__), 'tune_00_motion_theme.mp3')
wavfile.write(wav_out, SR, (mix * 32767).astype(np.int16))
print(f"Generated WAV: {wav_out} (Peak: {round(float(np.abs(mix).max()), 3)})")
import subprocess
cmd = ['ffmpeg', '-y', '-i', wav_out, '-b:a', '320k', mp3_out]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"Generated MP3: {mp3_out}")

