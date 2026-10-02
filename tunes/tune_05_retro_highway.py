"""Tune 05: 'Retro Highway' (Synthwave / Outrun 80s Driving Energy)
Duration: 60.0s @ 116 BPM (29 bars @ 2.06896s/bar)
Key: B Minor / D Major (Bm -> G -> A -> F#m)
Character: Fast running 16th analog bassline, 80s synth brass stabs, soaring nostalgic lead, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse, supersaw,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 116.0
    TOTAL_BARS = 29
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=105)
    BEAT = engine.beat
    BAR = engine.bar

    # Rolling 16th-note Synthwave Bass
    def outrun_bass(f, d=0.12):
        t = tt(d)
        w = saw(f, t) * 0.7 + pulse(f, t, 0.45) * 0.3
        filtered = lp(w, 1800) * np.exp(-t * 22.0) + lp(w, 500) * 0.5
        return np.tanh(filtered * 1.8) * env(len(t), 0.002, 0.025) * 0.38

    # 80s Synth Brass Stab
    def synth_brass(f, d=BEAT * 0.45):
        s = supersaw(f, d, (-15, -7, 0, 7, 15), rng=engine.rng)
        t = tt(d)
        dark = lp(s, 900)
        bright = lp(s, 5500)
        sweep = dark + (bright - dark) * np.exp(-t * 12.0)
        return hp(sweep, 160) * env(len(t), 0.005, 0.05) * 0.20

    # Gated Reverb Snare (80s style)
    def gated_snare():
        d = 0.35
        t = tt(d)
        body = np.sin(2.0 * np.pi * 180.0 * t) * np.exp(-t * 28.0) * 0.5
        noise = bp(engine.rng.standard_normal(len(t)), 1200, 7000) * 0.6
        # Sudden gate cutoff at 0.22s
        gate = np.where(t < 0.22, 1.0, np.exp(-(t - 0.22) * 80.0))
        return (body + noise) * gate * 0.42

    # Heroic Soaring Lead
    def outrun_lead(f, d):
        t = tt(d)
        vib = 0.006 * np.sin(2.0 * np.pi * 5.8 * t) * np.minimum(1.0, t / 0.18)
        fm = f * (1.0 + vib)
        ph = np.cumsum(fm) / engine.sr
        w = saw(1.0, ph) * 0.65 + pulse(1.0, ph, 0.5) * 0.35
        dark = lp(w, 2000)
        bright = lp(w, 7500)
        out = dark + (bright - dark) * np.exp(-t * 6.5) + 0.3 * np.sin(4.0 * np.pi * ph) * np.exp(-t * 4.0)
        return hp(out, 180) * env(len(t), 0.004, min(0.12, d / 3.0)) * np.exp(-t * 0.9) * 0.24

    CHORDS = {
        'Bm': ['D4', 'F#4', 'B4', 'D5'],
        'G': ['D4', 'G4', 'B4', 'D5'],
        'A': ['C#4', 'E4', 'A4', 'C#5'],
        'F#m': ['C#4', 'F#4', 'A4', 'C#5']
    }
    ROOTS = {'Bm': 'B1', 'G': 'G1', 'A': 'A1', 'F#m': 'F#1'}
    PROG = ['Bm', 'G', 'A', 'F#m']

    HOOK = {
        'Bm': [(0.0, 'B4', 0.5), (0.5, 'D5', 0.5), (1.0, 'F#5', 0.75), (1.75, 'E5', 0.5), (2.25, 'D5', 0.5), (2.75, 'C#5', 0.5), (3.25, 'B4', 0.75)],
        'G': [(0.0, 'D5', 0.5), (0.5, 'G5', 0.5), (1.0, 'B5', 1.0), (2.0, 'A5', 0.5), (2.5, 'G5', 0.5), (3.0, 'D5', 0.5), (3.5, 'G5', 0.5)],
        'A': [(0.0, 'C#5', 0.5), (0.5, 'E5', 0.5), (1.0, 'A5', 1.0), (2.0, 'G#5', 0.5), (2.5, 'E5', 0.5), (3.0, 'C#5', 0.5), (3.5, 'E5', 0.5)],
        'F#m': [(0.0, 'F#5', 0.5), (0.5, 'A5', 0.5), (1.0, 'C#6', 0.75), (1.75, 'B5', 0.5), (2.25, 'A5', 0.5), (2.75, 'G#5', 0.5), (3.25, 'F#5', 0.75)]
    }

    # 29-bar plan
    PLAN = (
        ['intro'] * 4 +
        ['drive'] * 6 +
        ['verse'] * 4 +
        ['build'] * 4 +
        ['climax'] * 7 +
        ['outro'] * 4
    )

    LV = {
        'intro': dict(kick=0.5, bass=0.8, brass=0.6),
        'drive': dict(kick=1.0, snare=0.9, chh=0.8, ohh=0.7, bass=1.0, brass=0.9, shk=0.6),
        'verse': dict(kick=1.0, snare=0.9, chh=0.85, ohh=0.75, bass=1.0, brass=0.8, hook=1.0, shk=0.7),
        'build': dict(brass=0.85, bass=0.75),
        'climax': dict(kick=1.05, snare=1.0, chh=0.95, ohh=0.9, bass=1.05, brass=1.0, hook=1.1, big=1),
        'outro': dict(brass=0.8, bass=0.5, chh=0.4)
    }

    print("Synthesizing Tune 05: 'Retro Highway'...")

    for b, sec in enumerate(PLAN):
        b0 = b * BAR
        L = LV[sec]
        g = lambda k: L.get(k, 0.0)
        ch = PROG[b % 4]
        nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

        # Rolling 16th Synthwave Bassline (driving forward constantly)
        if g('bass'):
            rf = hz(ROOTS[ch])
            for i in range(16):
                t_b = b0 + i * (BEAT / 4.0)
                if t_b < engine.dur:
                    # Octave variations on the 16ths
                    pitch = rf * 2.0 if (i % 4 == 2 or i % 4 == 3) else rf
                    sig = outrun_bass(pitch, 0.12) * g('bass')
                    engine.add('music', t_b, sig, 1.0)

        for bt in range(4):
            tb = b0 + bt * BEAT
            if tb >= engine.dur:
                break

            if g('kick') and (sec != 'intro' or b >= 1):
                engine.add('drums', tb, synth_kick(160, 46, 7.0, rng=engine.rng), g('kick'))
                engine.duck(tb, 0.28, 0.28)

            if g('snare') and bt in (1, 3):
                engine.add('drums', tb, gated_snare(), g('snare'), send=0.35)

            for q in range(4):
                tq = tb + q * (BEAT / 4.0)
                if tq >= engine.dur:
                    break
                if g('chh') and q in (1, 3):
                    engine.add('drums', tq, synth_hat_closed(rng=engine.rng), g('chh') * (1.0 if q == 3 else 0.6), pan=0.25)
                if g('shk'):
                    engine.add('drums', tq, synth_shaker(rng=engine.rng), g('shk') * (1.0 if q % 2 else 0.6), pan=-0.3)

            off = tb + BEAT / 2.0
            if off < engine.dur:
                if g('ohh'):
                    engine.add('drums', off, synth_hat_open(rng=engine.rng), g('ohh'), pan=0.2)
                if g('brass'):
                    for k_i, nn in enumerate(CHORDS[ch]):
                        engine.add('music', off, synth_brass(hz(nn)), g('brass') * 0.85, pan=(-0.5, -0.15, 0.15, 0.5)[k_i], send=0.25)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = outrun_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = outrun_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
                        m_len = max(len(sig), len(sig_oct))
                        sc = np.zeros(m_len, dtype=np.float32)
                        sc[:len(sig)] += sig
                        sc[:len(sig_oct)] += sig_oct
                        sig = sc
                    engine.add('music', ts, sig, 1.0, pan=0.0, send=0.35)
                    for r, (dl, pn) in enumerate(((0.75, -0.5), (1.5, 0.5))):
                        dt = ts + dl * BEAT
                        if dt < engine.dur:
                            engine.add('music', dt, lp(sig, 3400) * (0.4 ** (r + 1)), 0.9, pan=pn)

        if sec == 'build' and nxt == 'climax':
            t_s = b0
            for div, frac in ((2, 0.4), (4, 0.75), (8, 1.0)):
                while t_s < b0 + BAR * frac - 1e-5:
                    v = (0.25 + 0.75 * ((t_s - b0) / BAR) ** 1.6) * 0.95
                    engine.add('drums', t_s, synth_snare(210, rng=engine.rng), v, send=0.2)
                    t_s += BEAT / div
            engine.add('sfx', b0, synth_riser(BAR, rng=engine.rng), 0.32)

        if sec == 'climax' and (b == 0 or PLAN[b - 1] != 'climax'):
            engine.add('drums', b0, synth_crash(rng=engine.rng), 1.0, send=0.35)
            engine.add('sfx', b0, synth_impact(0.75, rng=engine.rng), send=0.3)
            engine.add('sfx', b0, synth_whoosh(0.9, rng=engine.rng), 0.3)

    engine.ramp_filter(0.0, 8.5, 0.25, 0.95)
    engine.ramp_filter(29.0, 37.0, 0.35, 1.0)
    engine.ramp_filter(52.0, 60.0, 1.0, 0.35)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_05_retro_highway.wav')
    mp3_out = os.path.join(here, 'tune_05_retro_highway.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
