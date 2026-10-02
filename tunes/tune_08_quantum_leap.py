"""Tune 08: 'Quantum Leap' (Electro Swing & Shuffle Hop)
Duration: 60.0s @ 96 BPM (24 bars @ 2.5s/bar)
Key: C Minor / Eb Major (Cm -> Ab -> Bb -> Eb)
Character: Energetic swing-quantized shuffle bounce, upright acoustic bass, playful vintage horn stabs, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse, supersaw,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 96.0
    TOTAL_BARS = 24
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=108)
    BEAT = engine.beat
    BAR = engine.bar

    # Upright Acoustic Bass Pluck (warm woody body + finger thump)
    def upright_bass(f, d):
        t = tt(d)
        body = np.sin(2.0 * np.pi * f * t) * 0.8 + 0.25 * saw(f, t)
        thump = lp(engine.rng.standard_normal(len(t)), 800) * np.exp(-t * 80.0) * 0.35
        out = (lp(body, 600) + thump) * env(len(t), 0.004, 0.05) * np.exp(-t * 4.5)
        return np.tanh(out * 1.6) * 0.38

    # Vintage Swing Horn / Brass Stab
    def swing_horn(f, d=BEAT * 0.4):
        s = supersaw(f, d, (-14, -6, 0, 6, 14), rng=engine.rng)
        t = tt(d)
        dark = lp(s, 1000)
        bright = lp(s, 4800)
        sweep = dark + (bright - dark) * np.exp(-t * 16.0)
        return hp(sweep, 220) * env(len(t), 0.006, 0.04) * 0.20

    # Swing Clarinet / Lead Synth
    def swing_lead(f, d):
        t = tt(d)
        vib = 0.006 * np.sin(2.0 * np.pi * 5.4 * t) * np.minimum(1.0, t / 0.18)
        fm = f * (1.0 + vib)
        ph = np.cumsum(fm) / engine.sr
        w = pulse(1.0, ph, 0.5) * 0.7 + saw(1.0, ph) * 0.3
        dark = lp(w, 1800)
        bright = lp(w, 6000)
        out = dark + (bright - dark) * np.exp(-t * 7.0)
        return hp(out, 240) * env(len(t), 0.005, min(0.12, d / 3.0)) * np.exp(-t * 1.1) * 0.23

    CHORDS = {
        'Cm': ['C4', 'Eb4', 'G4', 'C5'],
        'Ab': ['C4', 'Eb4', 'Ab4', 'C5'],
        'Bb': ['D4', 'F4', 'Bb4', 'D5'],
        'Eb': ['Eb4', 'G4', 'Bb4', 'Eb5']
    }
    ROOTS = {'Cm': 'C2', 'Ab': 'Ab1', 'Bb': 'Bb1', 'Eb': 'Eb2'}
    PROG = ['Cm', 'Ab', 'Bb', 'Eb']

    HOOK = {
        'Cm': [(0.0, 'G4', 0.5), (0.66, 'C5', 0.5), (1.0, 'Eb5', 0.75), (1.66, 'D5', 0.5), (2.0, 'C5', 0.5), (2.66, 'G4', 0.5), (3.0, 'C5', 0.75)],
        'Ab': [(0.0, 'C5', 0.5), (0.66, 'Eb5', 0.5), (1.0, 'Ab5', 1.0), (2.0, 'G5', 0.5), (2.66, 'Eb5', 0.5), (3.0, 'C5', 0.5), (3.66, 'Eb5', 0.5)],
        'Bb': [(0.0, 'D5', 0.5), (0.66, 'F5', 0.5), (1.0, 'Bb5', 1.0), (2.0, 'Ab5', 0.5), (2.66, 'F5', 0.5), (3.0, 'D5', 0.5), (3.66, 'F5', 0.5)],
        'Eb': [(0.0, 'G5', 0.5), (0.66, 'Bb5', 0.5), (1.0, 'Eb6', 0.75), (1.66, 'D6', 0.5), (2.0, 'C6', 0.5), (2.66, 'Bb5', 0.5), (3.0, 'Eb6', 0.75)]
    }

    # 24-bar plan
    PLAN = (
        ['intro'] * 4 +
        ['groove'] * 5 +
        ['verse'] * 4 +
        ['build'] * 3 +
        ['climax'] * 5 +
        ['outro'] * 3
    )

    LV = {
        'intro': dict(kick=0.5, horn=0.6, bass=0.7),
        'groove': dict(kick=1.0, clap=0.9, chh=0.85, ohh=0.7, bass=1.0, horn=0.9, shk=0.6),
        'verse': dict(kick=1.0, clap=0.95, chh=0.9, ohh=0.75, bass=1.0, horn=0.8, hook=1.0, shk=0.7),
        'build': dict(horn=0.85, bass=0.7),
        'climax': dict(kick=1.05, clap=1.0, chh=0.95, ohh=0.9, bass=1.05, horn=1.0, hook=1.1, big=1),
        'outro': dict(horn=0.8, bass=0.5, chh=0.4)
    }

    print("Synthesizing Tune 08: 'Quantum Leap'...")

    for b, sec in enumerate(PLAN):
        b0 = b * BAR
        L = LV[sec]
        g = lambda k: L.get(k, 0.0)
        ch = PROG[b % 4]
        nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

        for bt in range(4):
            tb = b0 + bt * BEAT
            if tb >= engine.dur:
                break

            if g('kick') and (sec != 'intro' or b >= 1):
                engine.add('drums', tb, synth_kick(160, 48, 7.2, rng=engine.rng), g('kick'))
                engine.duck(tb, 0.32, 0.28)

            if g('clap') and bt in (1, 3):
                engine.add('drums', tb, synth_clap(rng=engine.rng), g('clap'), send=0.25)

            # Swing triplet hi-hats (downbeat + swung offbeat at 2/3 beat)
            if g('chh'):
                engine.add('drums', tb, synth_hat_closed(rng=engine.rng), g('chh') * 0.7, pan=0.2)
                t_swing = tb + BEAT * 0.66
                if t_swing < engine.dur:
                    engine.add('drums', t_swing, synth_hat_closed(rng=engine.rng), g('chh') * 0.95, pan=0.25)

            # Swing offbeat horn stab (placed at swing offset 0.66 beat)
            t_off = tb + BEAT * 0.66
            if t_off < engine.dur and g('horn'):
                for k_i, nn in enumerate(CHORDS[ch]):
                    engine.add('music', t_off, swing_horn(hz(nn)), g('horn') * 0.85, pan=(-0.5, -0.15, 0.15, 0.5)[k_i], send=0.25)

            # Walking Upright Bass: Downbeat root, walking tones
            if g('bass'):
                rf = hz(ROOTS[ch])
                engine.add('music', tb, upright_bass(rf, BEAT * 0.55), g('bass'))
                if bt in (1, 3) and t_off < engine.dur:
                    engine.add('music', t_off, upright_bass(rf * 1.5, BEAT * 0.35), g('bass') * 0.8)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = swing_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = swing_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
                        m_len = max(len(sig), len(sig_oct))
                        sc = np.zeros(m_len, dtype=np.float32)
                        sc[:len(sig)] += sig
                        sc[:len(sig_oct)] += sig_oct
                        sig = sc
                    engine.add('music', ts, sig, 1.0, pan=0.0, send=0.35)
                    for r, (dl, pn) in enumerate(((0.66, -0.5), (1.33, 0.5))):
                        dt = ts + dl * BEAT
                        if dt < engine.dur:
                            engine.add('music', dt, lp(sig, 3200) * (0.4 ** (r + 1)), 0.9, pan=pn)

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

    engine.ramp_filter(0.0, 10.0, 0.25, 0.95)
    engine.ramp_filter(30.0, 40.0, 0.35, 1.0)
    engine.ramp_filter(52.5, 60.0, 1.0, 0.35)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_08_quantum_leap.wav')
    mp3_out = os.path.join(here, 'tune_08_quantum_leap.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
