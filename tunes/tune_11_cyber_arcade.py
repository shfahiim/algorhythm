"""Tune 11: 'Cyber Arcade' (Tokyo Electro-Funk / City Pop)
Duration: 60.0s @ 112 BPM (28 bars @ 2.142857s/bar)
Key: Eb Major (Abmaj7 -> Bb -> Cm7 -> Eb)
Character: FM electric piano, snappy funk synth-bass, talkbox-style lead, upbeat city pop bounce, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 112.0
    TOTAL_BARS = 28
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=111)
    BEAT = engine.beat
    BAR = engine.bar

    # FM Electric Piano (DX7-style bright chime tine)
    def fm_epiano(f, d=BEAT * 0.45):
        t = tt(d)
        # 2-operator FM: carrier + modulator at ratio 14:1
        mod = np.sin(2.0 * np.pi * f * 14.0 * t) * np.exp(-t * 22.0) * 0.4
        car = np.sin(2.0 * np.pi * f * (1.0 + mod) * t) * np.exp(-t * 8.0)
        tine = np.sin(2.0 * np.pi * f * 3.0 * t) * np.exp(-t * 18.0) * 0.3
        out = (car + tine) * env(len(t), 0.003, 0.04)
        return hp(out, 180) * 0.20

    # Snappy Funk Synth-Bass
    def funk_bass(f, d):
        t = tt(d)
        w = saw(f, t) * 0.75 + pulse(f, t, 0.4) * 0.25
        filt_sweep = lp(w, 2000) * np.exp(-t * 24.0) + lp(w, 450) * 0.5
        return np.tanh(filt_sweep * 1.7) * env(len(t), 0.003, 0.035) * 0.38

    # Talkbox / Formant Vocal Synth Lead
    def talkbox_lead(f, d):
        t = tt(d)
        vib = 0.005 * np.sin(2.0 * np.pi * 5.8 * t) * np.minimum(1.0, t / 0.16)
        fm = f * (1.0 + vib)
        ph = np.cumsum(fm) / engine.sr
        w = pulse(1.0, ph, 0.4) * 0.6 + saw(1.0, ph) * 0.4
        # Vocal formant peaks (A/O vowel resonance: ~800 Hz and ~2400 Hz)
        f1 = bp(w, 600, 1100) * 0.7
        f2 = bp(w, 1800, 3000) * 0.5
        out = (f1 + f2) * env(len(t), 0.004, min(0.12, d / 3.0)) * np.exp(-t * 0.9)
        return np.tanh(out * 1.5) * 0.25

    CHORDS = {
        'Ab': ['C4', 'Eb4', 'G4', 'C5'],
        'Bb': ['D4', 'F4', 'Bb4', 'D5'],
        'Cm': ['Eb4', 'G4', 'Bb4', 'Eb5'],
        'Eb': ['Eb4', 'G4', 'Bb4', 'Eb5']
    }
    ROOTS = {'Ab': 'Ab1', 'Bb': 'Bb1', 'Cm': 'C2', 'Eb': 'Eb2'}
    PROG = ['Ab', 'Bb', 'Cm', 'Eb']

    HOOK = {
        'Ab': [(0.0, 'C5', 0.5), (0.5, 'Eb5', 0.5), (1.0, 'G5', 0.75), (1.75, 'F5', 0.5), (2.25, 'Eb5', 0.5), (2.75, 'C5', 0.5), (3.25, 'Eb5', 0.75)],
        'Bb': [(0.0, 'D5', 0.5), (0.5, 'F5', 0.5), (1.0, 'Bb5', 1.0), (2.0, 'Ab5', 0.5), (2.5, 'F5', 0.5), (3.0, 'D5', 0.5), (3.5, 'F5', 0.5)],
        'Cm': [(0.0, 'Eb5', 0.5), (0.5, 'G5', 0.5), (1.0, 'C6', 1.0), (2.0, 'Bb5', 0.5), (2.5, 'G5', 0.5), (3.0, 'Eb5', 0.5), (3.5, 'G5', 0.5)],
        'Eb': [(0.0, 'G5', 0.5), (0.5, 'Bb5', 0.5), (1.0, 'Eb6', 0.75), (1.75, 'D6', 0.5), (2.25, 'C6', 0.5), (2.75, 'Bb5', 0.5), (3.25, 'Eb6', 0.75)]
    }

    # 28-bar plan
    PLAN = (
        ['intro'] * 4 +
        ['groove'] * 6 +
        ['verse'] * 4 +
        ['build'] * 4 +
        ['climax'] * 7 +
        ['outro'] * 3
    )

    LV = {
        'intro': dict(kick=0.5, epiano=0.8, bass=0.7),
        'groove': dict(kick=1.0, clap=0.9, chh=0.8, ohh=0.7, bass=1.0, epiano=0.85, shk=0.6),
        'verse': dict(kick=1.0, clap=0.95, chh=0.85, ohh=0.75, bass=1.0, epiano=0.8, hook=1.0, shk=0.7),
        'build': dict(epiano=0.9, bass=0.65),
        'climax': dict(kick=1.05, clap=1.0, chh=0.95, ohh=0.9, bass=1.05, epiano=1.0, hook=1.1, big=1),
        'outro': dict(epiano=0.8, bass=0.4, chh=0.4)
    }

    print("Synthesizing Tune 11: 'Cyber Arcade'...")

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
                engine.add('drums', tb, synth_kick(170, 50, 7.5, rng=engine.rng), g('kick'))
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
                if g('epiano'):
                    for k_i, nn in enumerate(CHORDS[ch]):
                        engine.add('music', off, fm_epiano(hz(nn)), g('epiano') * 0.85, pan=(-0.5, -0.15, 0.15, 0.5)[k_i], send=0.25)
                if g('bass'):
                    rf = hz(ROOTS[ch])
                    engine.add('music', off, funk_bass(rf * 2.0, BEAT * 0.36), g('bass'))

            if g('bass') and bt in (0, 2):
                engine.add('music', tb, funk_bass(hz(ROOTS[ch]), BEAT * 0.42), g('bass') * 0.95)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = talkbox_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = talkbox_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
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
    engine.ramp_filter(28.0, 36.5, 0.35, 1.0)
    engine.ramp_filter(52.0, 60.0, 1.0, 0.35)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_11_cyber_arcade.wav')
    mp3_out = os.path.join(here, 'tune_11_cyber_arcade.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
