"""Tune 07: 'Solar Spark' (Nu-Funk & Slap Bass Groove)
Duration: 60.0s @ 108 BPM (27 bars @ 2.2222s/bar)
Key: D Major (Gmaj7 -> A7 -> Bm7 -> D)
Character: California funk, bouncy slap bass with octave pops, muted rhythm guitar plucks, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse, organ_timbre,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 108.0
    TOTAL_BARS = 27
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=107)
    BEAT = engine.beat
    BAR = engine.bar

    # Resonant Slap Bass with Thumb Thump & Pop
    def slap_bass(f, d, pop=False):
        t = tt(d)
        w = saw(f, t) * 0.7 + pulse(f, t, 0.4) * 0.3
        f_cut = 3500.0 if pop else 1500.0
        filt_sweep = lp(w, f_cut) * np.exp(-t * (30.0 if pop else 22.0)) + lp(w, 400) * 0.4
        thumb = np.sin(2.0 * np.pi * 70.0 * t) * np.exp(-t * 40.0) * 0.3
        return np.tanh((filt_sweep + thumb) * 1.8) * env(len(t), 0.002, 0.03) * 0.38

    # Muted Rhythm Guitar Pluck
    def funk_guitar(f, d=0.14):
        t = tt(d)
        w = saw(f, t) * 0.5 + pulse(f, t, 0.35) * 0.5
        pick = hp(engine.rng.standard_normal(len(t)), 4000) * np.exp(-t * 260.0) * 0.15
        filt_sweep = bp(w, 800, 3200) * np.exp(-t * 18.0)
        return (filt_sweep + pick) * env(len(t), 0.002, 0.02) * 0.16

    # Warm Rhodes / Organ Chords
    def rhodes_chord(f, d):
        return organ_timbre(f, d, drawbars=(1.0, 0.6, 0.3, 0.2)) * 0.15

    # Funky Melodic Lead
    def funk_lead(f, d):
        t = tt(d)
        vib = 0.005 * np.sin(2.0 * np.pi * 5.6 * t) * np.minimum(1.0, t / 0.18)
        fm = f * (1.0 + vib)
        ph = np.cumsum(fm) / engine.sr
        w = saw(1.0, ph) * 0.6 + pulse(1.0, ph, 0.4) * 0.4
        dark = lp(w, 2000)
        bright = lp(w, 7000)
        out = dark + (bright - dark) * np.exp(-t * 7.0)
        return hp(out, 200) * env(len(t), 0.003, min(0.12, d / 3.0)) * np.exp(-t * 1.0) * 0.22

    CHORDS = {
        'G': ['D4', 'G4', 'B4', 'F#5'],
        'A': ['C#4', 'E4', 'G4', 'A4'],
        'Bm': ['D4', 'F#4', 'A4', 'D5'],
        'D': ['D4', 'F#4', 'A4', 'C#5']
    }
    ROOTS = {'G': 'G1', 'A': 'A1', 'Bm': 'B1', 'D': 'D2'}
    PROG = ['G', 'A', 'Bm', 'D']

    HOOK = {
        'G': [(0.0, 'B4', 0.5), (0.5, 'D5', 0.5), (1.0, 'G5', 0.75), (1.75, 'F#5', 0.5), (2.25, 'D5', 0.5), (2.75, 'B4', 0.5), (3.25, 'D5', 0.75)],
        'A': [(0.0, 'C#5', 0.5), (0.5, 'E5', 0.5), (1.0, 'A5', 1.0), (2.0, 'G5', 0.5), (2.5, 'E5', 0.5), (3.0, 'C#5', 0.5), (3.5, 'E5', 0.5)],
        'Bm': [(0.0, 'D5', 0.5), (0.5, 'F#5', 0.5), (1.0, 'B5', 1.0), (2.0, 'A5', 0.5), (2.5, 'F#5', 0.5), (3.0, 'D5', 0.5), (3.5, 'F#5', 0.5)],
        'D': [(0.0, 'F#5', 0.5), (0.5, 'A5', 0.5), (1.0, 'D6', 0.75), (1.75, 'C#6', 0.5), (2.25, 'B5', 0.5), (2.75, 'A5', 0.5), (3.25, 'D6', 0.75)]
    }

    # 27-bar plan
    PLAN = (
        ['intro'] * 4 +
        ['groove'] * 6 +
        ['verse'] * 4 +
        ['build'] * 4 +
        ['climax'] * 6 +
        ['outro'] * 3
    )

    LV = {
        'intro': dict(kick=0.5, guitar=0.8, rhodes=0.6),
        'groove': dict(kick=1.0, clap=0.9, chh=0.8, ohh=0.7, bass=1.0, guitar=0.85, rhodes=0.5, shk=0.6),
        'verse': dict(kick=1.0, clap=0.95, chh=0.85, ohh=0.75, bass=1.0, guitar=0.8, rhodes=0.5, hook=1.0, shk=0.7),
        'build': dict(rhodes=0.85, guitar=0.9, bass=0.6),
        'climax': dict(kick=1.05, clap=1.0, chh=0.95, ohh=0.9, bass=1.05, guitar=0.95, rhodes=0.8, hook=1.1, big=1),
        'outro': dict(rhodes=0.8, guitar=0.7, bass=0.4, chh=0.4)
    }

    print("Synthesizing Tune 07: 'Solar Spark'...")

    for b, sec in enumerate(PLAN):
        b0 = b * BAR
        L = LV[sec]
        g = lambda k: L.get(k, 0.0)
        ch = PROG[b % 4]
        nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

        # Funk Guitar 16th Pattern
        if g('guitar'):
            chord_notes = CHORDS[ch]
            for i in range(16):
                # Syncopated rhythm hits
                if i in (2, 5, 8, 10, 14):
                    t_g = b0 + i * (BEAT / 4.0)
                    if t_g < engine.dur:
                        note = chord_notes[i % len(chord_notes)]
                        sig = funk_guitar(hz(note), 0.16) * g('guitar')
                        engine.add('music', t_g, sig, 1.0, pan=-0.4 if i % 2 == 0 else 0.4, send=0.2)

        for bt in range(4):
            tb = b0 + bt * BEAT
            if tb >= engine.dur:
                break

            if g('kick') and (sec != 'intro' or b >= 1):
                engine.add('drums', tb, synth_kick(165, 50, 7.2, rng=engine.rng), g('kick'))
                engine.duck(tb, 0.28, 0.26)

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
                # Slap bass offbeat pop
                if g('bass'):
                    rf = hz(ROOTS[ch])
                    engine.add('music', off, slap_bass(rf * 2.0, BEAT * 0.36, pop=True), g('bass'))

            # Slap bass downbeat thumb thump
            if g('bass') and bt in (0, 2):
                engine.add('music', tb, slap_bass(hz(ROOTS[ch]), BEAT * 0.42, pop=False), g('bass') * 0.95)

        if g('rhodes'):
            d_p = min(BAR + 0.1, engine.dur - b0)
            for k_i, nn in enumerate(CHORDS[ch]):
                engine.add('music', b0, rhodes_chord(hz(nn), d_p), g('rhodes'), pan=(-0.5, -0.15, 0.15, 0.5)[k_i], send=0.3)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = funk_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = funk_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
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

    engine.ramp_filter(0.0, 8.8, 0.25, 0.95)
    engine.ramp_filter(29.0, 37.0, 0.35, 1.0)
    engine.ramp_filter(52.0, 60.0, 1.0, 0.35)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_07_solar_spark.wav')
    mp3_out = os.path.join(here, 'tune_07_solar_spark.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
