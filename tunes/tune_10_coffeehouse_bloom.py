"""Tune 10: 'Coffeehouse Bloom' (Organic Indie Folk-Dance)
Duration: 60.0s @ 88 BPM (22 bars @ 2.72727s/bar)
Key: C Major (C -> G -> Am -> F)
Character: Warm acoustic fingerstyle string plucks, stomping kick, wooden claps, sunny whistle lead, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse, organ_timbre,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 88.0
    TOTAL_BARS = 22
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=110)
    BEAT = engine.beat
    BAR = engine.bar

    # Acoustic Plucked String (Karplus-inspired harmonic decay)
    def acoustic_pluck(f, d=0.28):
        t = tt(d)
        w = (
            np.sin(2.0 * np.pi * f * t) * 1.0 +
            np.sin(2.0 * np.pi * f * 2.0 * t) * 0.45 * np.exp(-t * 14.0) +
            np.sin(2.0 * np.pi * f * 3.0 * t) * 0.25 * np.exp(-t * 24.0) +
            np.sin(2.0 * np.pi * f * 4.0 * t) * 0.12 * np.exp(-t * 36.0)
        )
        nail = hp(engine.rng.standard_normal(len(t)), 3500) * np.exp(-t * 220.0) * 0.14
        out = (w * np.exp(-t * 7.5) + nail) * env(len(t), 0.003, 0.04)
        return lp(out, 4200) * 0.18

    # Acoustic Stomp Kick (deep woody resonance)
    def stomp_kick():
        t = tt(0.45)
        f = 42.0 + 90.0 * np.exp(-t * 28.0)
        body = np.sin(2.0 * np.pi * np.cumsum(f) / engine.sr) * np.exp(-t * 5.5)
        wood = lp(engine.rng.standard_normal(len(t)), 1800) * np.exp(-t * 120.0) * 0.4
        return np.tanh((body + wood) * 1.5) * 0.85

    # Sunny Whistle Lead
    def whistle_lead(f, d):
        t = tt(d)
        vib = 0.005 * np.sin(2.0 * np.pi * 5.0 * t) * np.minimum(1.0, t / 0.2)
        fm = f * (1.0 + vib)
        ph = np.cumsum(fm) / engine.sr
        s = np.sin(2.0 * np.pi * ph) * 0.9 + 0.1 * np.sin(4.0 * np.pi * ph)
        air = bp(engine.rng.standard_normal(len(t)), 2200, 4800) * 0.06 * np.exp(-t * 2.5)
        out = (s + air) * env(len(t), 0.015, min(0.12, d / 3.0)) * np.exp(-t * 0.75)
        return lp(out, 4200) * 0.24

    # Warm Organ Pad
    def warm_organ(f, d):
        return organ_timbre(f, d, drawbars=(1.0, 0.5, 0.25, 0.15)) * 0.12

    CHORDS = {
        'C': ['C4', 'E4', 'G4', 'C5'],
        'G': ['B3', 'D4', 'G4', 'B4'],
        'Am': ['C4', 'E4', 'A4', 'C5'],
        'F': ['C4', 'F4', 'A4', 'C5']
    }
    ROOTS = {'C': 'C2', 'G': 'G1', 'Am': 'A1', 'F': 'F1'}
    PROG = ['C', 'G', 'Am', 'F']

    ARP_NOTES = {
        'C': ['C4', 'E4', 'G4', 'C5', 'E5', 'C5', 'G4', 'E4', 'C4', 'E4', 'G4', 'B4', 'C5', 'E5', 'G5', 'C6'],
        'G': ['G3', 'B3', 'D4', 'G4', 'B4', 'G4', 'D4', 'B3', 'G3', 'B3', 'D4', 'F#4', 'G4', 'B4', 'D5', 'G5'],
        'Am': ['A3', 'C4', 'E4', 'A4', 'C5', 'A4', 'E4', 'C4', 'A3', 'C4', 'E4', 'G4', 'A4', 'C5', 'E5', 'A5'],
        'F': ['F3', 'A3', 'C4', 'F4', 'A4', 'F4', 'C4', 'A3', 'F3', 'A3', 'C4', 'E4', 'F4', 'A4', 'C5', 'F5']
    }

    HOOK = {
        'C': [(0.0, 'E5', 0.5), (0.5, 'G5', 0.5), (1.0, 'C6', 0.75), (1.75, 'B5', 0.5), (2.25, 'G5', 0.5), (2.75, 'E5', 0.5), (3.25, 'G5', 0.75)],
        'G': [(0.0, 'D5', 0.5), (0.5, 'G5', 0.5), (1.0, 'B5', 1.0), (2.0, 'A5', 0.5), (2.5, 'G5', 0.5), (3.0, 'D5', 0.5), (3.5, 'G5', 0.5)],
        'Am': [(0.0, 'C5', 0.5), (0.5, 'E5', 0.5), (1.0, 'A5', 1.0), (2.0, 'G5', 0.5), (2.5, 'E5', 0.5), (3.0, 'C5', 0.5), (3.5, 'E5', 0.5)],
        'F': [(0.0, 'A4', 0.5), (0.5, 'C5', 0.5), (1.0, 'F5', 0.75), (1.75, 'G5', 0.5), (2.25, 'A5', 0.5), (2.75, 'C6', 0.5), (3.25, 'F5', 0.75)]
    }

    # 22-bar plan
    PLAN = (
        ['intro'] * 3 +
        ['groove'] * 5 +
        ['verse'] * 4 +
        ['build'] * 3 +
        ['climax'] * 5 +
        ['outro'] * 2
    )

    LV = {
        'intro': dict(kick=0.5, pluck=0.85, organ=0.6),
        'groove': dict(kick=1.0, clap=0.9, chh=0.8, ohh=0.65, bass=1.0, pluck=0.8, organ=0.5, shk=0.6),
        'verse': dict(kick=1.0, clap=0.95, chh=0.85, ohh=0.7, bass=1.0, pluck=0.75, organ=0.5, hook=1.0, shk=0.7),
        'build': dict(organ=0.8, pluck=0.95, bass=0.6),
        'climax': dict(kick=1.05, clap=1.0, chh=0.9, ohh=0.85, bass=1.05, pluck=0.9, organ=0.8, hook=1.1, big=1),
        'outro': dict(organ=0.8, pluck=0.75, bass=0.4, chh=0.4)
    }

    print("Synthesizing Tune 10: 'Coffeehouse Bloom'...")

    for b, sec in enumerate(PLAN):
        b0 = b * BAR
        L = LV[sec]
        g = lambda k: L.get(k, 0.0)
        ch = PROG[b % 4]
        nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

        # Fingerstyle Pluck Arpeggio
        if g('pluck'):
            notes = ARP_NOTES[ch]
            for i in range(16):
                t_arp = b0 + i * (BEAT / 4.0)
                if t_arp < engine.dur:
                    sig = acoustic_pluck(hz(notes[i]), 0.24) * g('pluck')
                    engine.add('music', t_arp, sig, 1.0, pan=-0.45 + (i % 4) * 0.3, send=0.3)

        for bt in range(4):
            tb = b0 + bt * BEAT
            if tb >= engine.dur:
                break

            if g('kick') and (sec != 'intro' or b >= 1):
                engine.add('drums', tb, stomp_kick(), g('kick'))
                engine.duck(tb, 0.34, 0.30)

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

        if g('organ'):
            d_p = min(BAR + 0.1, engine.dur - b0)
            for k_i, nn in enumerate(CHORDS[ch]):
                engine.add('music', b0, warm_organ(hz(nn), d_p), g('organ'), pan=(-0.5, -0.15, 0.15, 0.5)[k_i], send=0.35)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = whistle_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = whistle_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
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

        if sec == 'build' and nxt == 'climax':
            t_s = b0
            for div, frac in ((2, 0.4), (4, 0.75), (8, 1.0)):
                while t_s < b0 + BAR * frac - 1e-5:
                    v = (0.25 + 0.75 * ((t_s - b0) / BAR) ** 1.6) * 0.95
                    engine.add('drums', t_s, synth_snare(190, rng=engine.rng), v, send=0.2)
                    t_s += BEAT / div
            engine.add('sfx', b0, synth_riser(BAR, rng=engine.rng), 0.3)

        if sec == 'climax' and (b == 0 or PLAN[b - 1] != 'climax'):
            engine.add('drums', b0, synth_crash(rng=engine.rng), 1.0, send=0.35)
            engine.add('sfx', b0, synth_impact(0.7, rng=engine.rng), send=0.3)
            engine.add('sfx', b0, synth_whoosh(0.85, rng=engine.rng), 0.3)

    engine.ramp_filter(0.0, 10.0, 0.3, 0.95)
    engine.ramp_filter(28.0, 38.0, 0.4, 1.0)
    engine.ramp_filter(52.0, 60.0, 1.0, 0.3)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_10_coffeehouse_bloom.wav')
    mp3_out = os.path.join(here, 'tune_10_coffeehouse_bloom.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
