"""Tune 09: 'Skyline Sprint' (Uplifting Euphoric Trance / Festival Drive)
Duration: 60.0s @ 132 BPM (33 bars @ 1.81818s/bar)
Key: G# Minor / B Major (E -> F# -> G#m -> B)
Character: Fast 132 BPM rolling trance bassline, massive supersaw anthem chords, soaring festival lead, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse, supersaw,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 132.0
    TOTAL_BARS = 33
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=109)
    BEAT = engine.beat
    BAR = engine.bar

    # Fast 16th Rolling Trance Bass
    def trance_bass(f, d=0.10):
        t = tt(d)
        w = saw(f, t) * 0.8 + saw(f * 1.004, t) * 0.2
        filt_sweep = lp(w, 2200) * np.exp(-t * 28.0) + lp(w, 450) * 0.6
        return np.tanh(filt_sweep * 1.8) * env(len(t), 0.002, 0.02) * 0.38

    # Massive Supersaw Trance Chord
    def trance_supersaw(f, d):
        s = supersaw(f, d, (-28, -18, -8, 0, 8, 18, 28), rng=engine.rng)
        t = tt(d)
        dark = lp(s, 1200)
        bright = lp(s, 7000)
        sweep = dark + (bright - dark) * np.exp(-t * 10.0)
        return hp(sweep, 180) * env(len(t), 0.005, 0.08) * 0.18

    # Soaring Stadium Anthem Lead
    def stadium_lead(f, d):
        t = tt(d)
        vib = 0.007 * np.sin(2.0 * np.pi * 6.0 * t) * np.minimum(1.0, t / 0.15)
        fm = f * (1.0 + vib)
        ph = np.cumsum(fm) / engine.sr
        w = saw(1.0, ph) * 0.7 + pulse(1.0, ph, 0.45) * 0.3
        dark = lp(w, 2400)
        bright = lp(w, 9000)
        out = dark + (bright - dark) * np.exp(-t * 6.0) + 0.35 * np.sin(4.0 * np.pi * ph) * np.exp(-t * 3.5)
        return hp(out, 200) * env(len(t), 0.003, min(0.12, d / 3.0)) * np.exp(-t * 0.8) * 0.24

    CHORDS = {
        'E': ['E4', 'G#4', 'B4', 'E5'],
        'F#': ['F#4', 'A#4', 'C#5', 'F#5'],
        'G#m': ['D#4', 'G#4', 'B4', 'D#5'],
        'B': ['D#4', 'F#4', 'B4', 'F#5']
    }
    ROOTS = {'E': 'E1', 'F#': 'F#1', 'G#m': 'G#1', 'B': 'B1'}
    PROG = ['E', 'F#', 'G#m', 'B']

    HOOK = {
        'E': [(0.0, 'G#5', 0.5), (0.5, 'B5', 0.5), (1.0, 'E6', 0.75), (1.75, 'D#6', 0.5), (2.25, 'B5', 0.5), (2.75, 'G#5', 0.5), (3.25, 'B5', 0.75)],
        'F#': [(0.0, 'A#5', 0.5), (0.5, 'C#6', 0.5), (1.0, 'F#6', 1.0), (2.0, 'E6', 0.5), (2.5, 'C#6', 0.5), (3.0, 'A#5', 0.5), (3.5, 'C#6', 0.5)],
        'G#m': [(0.0, 'B5', 0.5), (0.5, 'D#6', 0.5), (1.0, 'G#6', 1.0), (2.0, 'F#6', 0.5), (2.5, 'D#6', 0.5), (3.0, 'B5', 0.5), (3.5, 'D#6', 0.5)],
        'B': [(0.0, 'F#5', 0.5), (0.5, 'B5', 0.5), (1.0, 'D#6', 0.75), (1.75, 'E6', 0.5), (2.25, 'D#6', 0.5), (2.75, 'B5', 0.5), (3.25, 'F#6', 0.75)]
    }

    # 33-bar plan
    PLAN = (
        ['intro'] * 4 +
        ['drive'] * 7 +
        ['verse'] * 4 +
        ['build'] * 4 +
        ['climax'] * 10 +
        ['outro'] * 4
    )

    LV = {
        'intro': dict(kick=0.5, bass=0.7, saw=0.6),
        'drive': dict(kick=1.0, clap=0.9, chh=0.85, ohh=0.75, bass=1.0, saw=0.85, shk=0.6),
        'verse': dict(kick=1.0, clap=0.95, chh=0.9, ohh=0.8, bass=1.0, saw=0.8, hook=1.0, shk=0.7),
        'build': dict(saw=0.9, bass=0.7),
        'climax': dict(kick=1.05, clap=1.0, chh=0.95, ohh=0.9, bass=1.05, saw=1.0, hook=1.1, big=1),
        'outro': dict(saw=0.8, bass=0.5, chh=0.4)
    }

    print("Synthesizing Tune 09: 'Skyline Sprint'...")

    for b, sec in enumerate(PLAN):
        b0 = b * BAR
        L = LV[sec]
        g = lambda k: L.get(k, 0.0)
        ch = PROG[b % 4]
        nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

        # Rolling 16th Trance Bass
        if g('bass'):
            rf = hz(ROOTS[ch])
            for i in range(16):
                t_b = b0 + i * (BEAT / 4.0)
                if t_b < engine.dur:
                    # Trance triplet feel: mute beat 1 (where kick lands), play remaining 16ths
                    if i % 4 != 0:
                        engine.add('music', t_b, trance_bass(rf, 0.11), g('bass'))

        for bt in range(4):
            tb = b0 + bt * BEAT
            if tb >= engine.dur:
                break

            if g('kick') and (sec != 'intro' or b >= 1):
                engine.add('drums', tb, synth_kick(180, 52, 7.8, rng=engine.rng), g('kick'))
                engine.duck(tb, 0.25, 0.22)

            if g('clap') and bt in (1, 3):
                engine.add('drums', tb, synth_clap(rng=engine.rng), g('clap'), send=0.25)

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
                if g('saw'):
                    for k_i, nn in enumerate(CHORDS[ch]):
                        engine.add('music', off, trance_supersaw(hz(nn), BEAT * 0.45), g('saw') * 0.85, pan=(-0.6, -0.2, 0.2, 0.6)[k_i], send=0.25)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = stadium_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = stadium_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
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
                    engine.add('drums', t_s, synth_snare(230, rng=engine.rng), v, send=0.2)
                    t_s += BEAT / div
            engine.add('sfx', b0, synth_riser(BAR, rng=engine.rng), 0.32)

        if sec == 'climax' and (b == 0 or PLAN[b - 1] != 'climax'):
            engine.add('drums', b0, synth_crash(rng=engine.rng), 1.0, send=0.35)
            engine.add('sfx', b0, synth_impact(0.75, rng=engine.rng), send=0.3)
            engine.add('sfx', b0, synth_whoosh(0.9, rng=engine.rng), 0.3)

    engine.ramp_filter(0.0, 7.0, 0.25, 0.95)
    engine.ramp_filter(27.0, 34.5, 0.35, 1.0)
    engine.ramp_filter(52.0, 60.0, 1.0, 0.35)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_09_skyline_sprint.wav')
    mp3_out = os.path.join(here, 'tune_09_skyline_sprint.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
