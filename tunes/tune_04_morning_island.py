"""Tune 04: 'Morning Island' (Tropical Melodic Chill-House)
Duration: 60.0s @ 104 BPM (26 bars @ 2.3077s/bar)
Key: F Major / D Minor (Bbmaj7 -> C -> Dm7 -> F)
Character: Sun-drenched, breezy, wooden marimba/kalimba arpeggios, uplifting flute lead, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse, pluck_chime,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 104.0
    TOTAL_BARS = 26
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=104)
    BEAT = engine.beat
    BAR = engine.bar

    # Wooden Marimba / Kalimba timbre
    def marimba_pluck(f, d=0.22):
        t = tt(d)
        w = (
            np.sin(2.0 * np.pi * f * t) * 1.0 +
            np.sin(2.0 * np.pi * f * 2.75 * t) * 0.35 * np.exp(-t * 22.0) +
            np.sin(2.0 * np.pi * f * 4.0 * t) * 0.15 * np.exp(-t * 35.0)
        )
        wood_click = lp(engine.rng.standard_normal(len(t)), 3200) * np.exp(-t * 300.0) * 0.18
        return (w * np.exp(-t * 11.0) + wood_click) * 0.18

    # Warm Sub-Bass
    def tropical_bass(f, d):
        t = tt(d)
        s = np.sin(2.0 * np.pi * f * t) + 0.25 * lp(saw(f, t), 450)
        return np.tanh(s * 1.4) * env(len(t), 0.005, 0.04) * 0.36

    # Airy Flute / Whistle Lead
    def flute_lead(f, d):
        t = tt(d)
        vib = 0.005 * np.sin(2.0 * np.pi * 5.2 * t) * np.minimum(1.0, t / 0.2)
        fm = f * (1.0 + vib)
        ph = np.cumsum(fm) / engine.sr
        s = np.sin(2.0 * np.pi * ph) * 0.85 + 0.15 * np.sin(4.0 * np.pi * ph)
        breath = bp(engine.rng.standard_normal(len(t)), 2000, 5000) * 0.08 * np.exp(-t * 3.0)
        out = (s + breath) * env(len(t), 0.015, min(0.12, d / 3.0)) * np.exp(-t * 0.8)
        return lp(out, 4500) * 0.24

    # Warm Island Chord Pad
    def warm_pad(f, d):
        t = tt(d)
        w = (
            np.sin(2.0 * np.pi * f * t) * 0.6 +
            saw(f, t) * 0.25 +
            saw(f * 1.003, t) * 0.15
        )
        return lp(hp(w, 200), 2200) * env(len(t), 0.04, 0.3) * 0.10

    CHORDS = {
        'Bb': ['D4', 'F4', 'A4', 'D5'],
        'C': ['C4', 'E4', 'G4', 'C5'],
        'Dm': ['D4', 'F4', 'A4', 'F5'],
        'F': ['C4', 'F4', 'A4', 'C5']
    }
    ROOTS = {'Bb': 'Bb1', 'C': 'C2', 'Dm': 'D2', 'F': 'F1'}
    PROG = ['Bb', 'C', 'Dm', 'F']

    ARP_NOTES = {
        'Bb': ['D5', 'F5', 'A5', 'D6', 'F6', 'D6', 'A5', 'F5', 'D5', 'F5', 'A5', 'C6', 'D6', 'F6', 'A6', 'D7'],
        'C': ['C5', 'E5', 'G5', 'C6', 'E6', 'C6', 'G5', 'E5', 'C5', 'E5', 'G5', 'B5', 'C6', 'E6', 'G6', 'C7'],
        'Dm': ['D5', 'F5', 'A5', 'D6', 'F6', 'D6', 'A5', 'F5', 'D5', 'F5', 'A5', 'E6', 'F6', 'A6', 'C7', 'D7'],
        'F': ['C5', 'F5', 'A5', 'C6', 'F6', 'C6', 'A5', 'F5', 'C5', 'F5', 'A5', 'D6', 'F6', 'A6', 'C7', 'F7']
    }

    HOOK = {
        'Bb': [(0.0, 'F5', 0.5), (0.5, 'A5', 0.5), (1.0, 'D6', 0.75), (1.75, 'C6', 0.5), (2.25, 'A5', 0.5), (2.75, 'F5', 0.5), (3.25, 'A5', 0.75)],
        'C': [(0.0, 'G5', 0.5), (0.5, 'C6', 0.5), (1.0, 'E6', 1.0), (2.0, 'D6', 0.5), (2.5, 'C6', 0.5), (3.0, 'G5', 0.5), (3.5, 'C6', 0.5)],
        'Dm': [(0.0, 'A5', 0.5), (0.5, 'D6', 0.5), (1.0, 'F6', 1.0), (2.0, 'E6', 0.5), (2.5, 'D6', 0.5), (3.0, 'A5', 0.5), (3.5, 'D6', 0.5)],
        'F': [(0.0, 'C6', 0.5), (0.5, 'A5', 0.5), (1.0, 'F5', 0.75), (1.75, 'G5', 0.5), (2.25, 'A5', 0.5), (2.75, 'C6', 0.5), (3.25, 'F6', 0.75)]
    }

    # 26 bars
    PLAN = (
        ['intro'] * 4 +
        ['groove'] * 6 +
        ['verse'] * 4 +
        ['build'] * 4 +
        ['drop'] * 5 +
        ['outro'] * 3
    )

    LV = {
        'intro': dict(kick=0.5, marimba=0.85, pad=0.7, shk=0.5),
        'groove': dict(kick=1.0, clap=0.85, chh=0.8, ohh=0.65, bass=1.0, marimba=0.8, pad=0.5, shk=0.7),
        'verse': dict(kick=1.0, clap=0.9, chh=0.85, ohh=0.7, bass=1.0, marimba=0.75, pad=0.5, hook=1.0, shk=0.75),
        'build': dict(pad=0.8, marimba=1.0, bass=0.6),
        'drop': dict(kick=1.05, clap=0.95, chh=0.9, ohh=0.85, bass=1.05, marimba=0.9, pad=0.8, hook=1.1, shk=0.8, big=1),
        'outro': dict(pad=0.8, marimba=0.8, bass=0.4)
    }

    print("Synthesizing Tune 04: 'Morning Island'...")

    for b, sec in enumerate(PLAN):
        b0 = b * BAR
        L = LV[sec]
        g = lambda k: L.get(k, 0.0)
        ch = PROG[b % 4]
        nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

        # Marimba Arpeggio
        if g('marimba'):
            notes = ARP_NOTES[ch]
            for i in range(16):
                t_arp = b0 + i * (BEAT / 4.0)
                if t_arp < engine.dur:
                    sig = marimba_pluck(hz(notes[i]), 0.20) * g('marimba')
                    engine.add('music', t_arp, sig, 1.0, pan=-0.5 + (i % 4) * 0.33, send=0.35)

        for bt in range(4):
            tb = b0 + bt * BEAT
            if tb >= engine.dur:
                break

            if g('kick') and (sec != 'intro' or b >= 1):
                engine.add('drums', tb, synth_kick(150, 48, 6.8, rng=engine.rng), g('kick'))
                engine.duck(tb, 0.30, 0.28)

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
                if g('bass'):
                    engine.add('music', off, tropical_bass(hz(ROOTS[ch]), BEAT * 0.44), g('bass'))

        if g('pad'):
            d_p = min(BAR + 0.1, engine.dur - b0)
            for k_i, nn in enumerate(CHORDS[ch]):
                engine.add('music', b0, warm_pad(hz(nn), d_p), g('pad'), pan=(-0.6, -0.2, 0.2, 0.6)[k_i], send=0.35)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = flute_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = flute_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
                        m_len = max(len(sig), len(sig_oct))
                        sc = np.zeros(m_len, dtype=np.float32)
                        sc[:len(sig)] += sig
                        sc[:len(sig_oct)] += sig_oct
                        sig = sc
                    engine.add('music', ts, sig, 1.0, pan=0.0, send=0.35)
                    for r, (dl, pn) in enumerate(((0.75, -0.5), (1.5, 0.5))):
                        dt = ts + dl * BEAT
                        if dt < engine.dur:
                            engine.add('music', dt, lp(sig, 3000) * (0.4 ** (r + 1)), 0.9, pan=pn)

        if sec == 'build' and nxt == 'drop':
            t_s = b0
            for div, frac in ((2, 0.4), (4, 0.75), (8, 1.0)):
                while t_s < b0 + BAR * frac - 1e-5:
                    v = (0.25 + 0.75 * ((t_s - b0) / BAR) ** 1.6) * 0.95
                    engine.add('drums', t_s, synth_snare(190, rng=engine.rng), v, send=0.2)
                    t_s += BEAT / div
            engine.add('sfx', b0, synth_riser(BAR, rng=engine.rng), 0.3)

        if sec == 'drop' and (b == 0 or PLAN[b - 1] != 'drop'):
            engine.add('drums', b0, synth_crash(rng=engine.rng), 1.0, send=0.35)
            engine.add('sfx', b0, synth_impact(0.7, rng=engine.rng), send=0.3)
            engine.add('sfx', b0, synth_whoosh(0.85, rng=engine.rng), 0.3)

    engine.ramp_filter(0.0, 9.0, 0.3, 0.95)
    engine.ramp_filter(27.0, 36.0, 0.4, 1.0)
    engine.ramp_filter(53.0, 60.0, 1.0, 0.3)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_04_morning_island.wav')
    mp3_out = os.path.join(here, 'tune_04_morning_island.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
