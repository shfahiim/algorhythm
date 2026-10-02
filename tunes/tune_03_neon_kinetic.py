"""Tune 03: 'Neon Kinetic' (French Electro-House / Filter House)
Duration: 60.0s @ 120 BPM (30 bars @ 2.0s/bar)
Key: E Minor / G Major (Em -> C -> G -> D)
Character: Fast-paced, punchy, filtered French-touch disco house, energetic pulse arps, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse, supersaw,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 120.0
    TOTAL_BARS = 30
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=103)
    BEAT = engine.beat
    BAR = engine.bar

    # French House Bass: Bouncy disco octaves with filter bite
    def disco_bass(f, d):
        t = tt(d)
        w = saw(f, t) * 0.7 + pulse(f, t, 0.4) * 0.3
        filt_sweep = lp(w, 1400) * 0.75 + lp(w, 3200) * 0.25 * np.exp(-t * 22.0)
        return np.tanh(filt_sweep * 1.7) * env(len(t), 0.003, 0.035) * 0.36

    # Staccato filtered disco stabs
    def filter_stab(f, d=BEAT * 0.4):
        s = supersaw(f, d, (-18, -9, 0, 9, 18), rng=engine.rng)
        t = tt(d)
        filtered = lp(s, 2200) * np.exp(-t * 14.0) + lp(s, 700) * 0.4
        return hp(filtered, 180) * env(len(t), 0.003, 0.03) * 0.19

    # Fast 16th pulse arp
    def pulse_arp(f, d=0.12):
        t = tt(d)
        w = pulse(f, t, 0.3)
        return lp(w, 3500) * np.exp(-t * 16.0) * env(len(t), 0.002, 0.02) * 0.12

    # Melodic vocal-style lead
    def neon_lead(f, d):
        t = tt(d)
        fm = f * (1.0 + 0.004 * np.sin(2.0 * np.pi * 6.0 * t) * np.minimum(1.0, t / 0.15))
        ph = np.cumsum(fm) / engine.sr
        w = pulse(1.0, ph, 0.45) * 0.6 + saw(1.0, ph) * 0.4
        dark = lp(w, 2400)
        bright = lp(w, 8000)
        out = dark + (bright - dark) * np.exp(-t * 8.0)
        return hp(out, 200) * env(len(t), 0.003, min(0.1, d / 3.0)) * np.exp(-t * 1.0) * 0.22

    CHORDS = {
        'Em': ['E4', 'G4', 'B4', 'E5'],
        'C': ['C4', 'E4', 'G4', 'D5'],
        'G': ['D4', 'G4', 'B4', 'D5'],
        'D': ['D4', 'F#4', 'A4', 'D5']
    }
    ROOTS = {'Em': 'E2', 'C': 'C2', 'G': 'G1', 'D': 'D2'}
    PROG = ['Em', 'C', 'G', 'D']

    ARP_NOTES = {
        'Em': ['E5', 'B5', 'G5', 'E6', 'B5', 'G5', 'E5', 'B5', 'E5', 'G5', 'B5', 'E6', 'G6', 'E6', 'B5', 'G5'],
        'C': ['C5', 'G5', 'E5', 'C6', 'G5', 'E5', 'C5', 'G5', 'C5', 'E5', 'G5', 'C6', 'D6', 'C6', 'G5', 'E5'],
        'G': ['G5', 'D6', 'B5', 'G6', 'D6', 'B5', 'G5', 'D6', 'G5', 'B5', 'D6', 'G6', 'B6', 'G6', 'D6', 'B5'],
        'D': ['D5', 'A5', 'F#5', 'D6', 'A5', 'F#5', 'D5', 'A5', 'D5', 'F#5', 'A5', 'D6', 'E6', 'D6', 'A5', 'F#5']
    }

    HOOK = {
        'Em': [(0.0, 'E5', 0.5), (0.5, 'G5', 0.5), (1.0, 'B5', 0.75), (1.75, 'A5', 0.5), (2.25, 'G5', 0.5), (2.75, 'E5', 0.5), (3.25, 'G5', 0.75)],
        'C': [(0.0, 'G5', 0.5), (0.5, 'C6', 0.5), (1.0, 'E6', 1.0), (2.0, 'D6', 0.5), (2.5, 'C6', 0.5), (3.0, 'G5', 0.5), (3.5, 'C6', 0.5)],
        'G': [(0.0, 'B5', 0.5), (0.5, 'D6', 0.5), (1.0, 'G6', 1.0), (2.0, 'F#6', 0.5), (2.5, 'D6', 0.5), (3.0, 'B5', 0.5), (3.5, 'D6', 0.5)],
        'D': [(0.0, 'A5', 0.5), (0.5, 'D6', 0.5), (1.0, 'F#6', 0.75), (1.75, 'G6', 0.5), (2.25, 'F#6', 0.5), (2.75, 'E6', 0.5), (3.25, 'D6', 0.75)]
    }

    # 30-bar plan
    PLAN = (
        ['intro'] * 4 +
        ['groove'] * 6 +
        ['verse'] * 4 +
        ['build'] * 4 +
        ['climax'] * 8 +
        ['outro'] * 4
    )

    LV = {
        'intro': dict(kick=0.5, arp=0.8, pad=0.6),
        'groove': dict(kick=1.0, clap=0.9, chh=0.8, ohh=0.7, bass=1.0, stab=1.0, arp=0.65, shk=0.6),
        'verse': dict(kick=1.0, clap=0.9, chh=0.85, ohh=0.8, bass=1.0, stab=0.9, hook=1.0, arp=0.7, shk=0.7),
        'build': dict(pad=0.8, arp=0.95, stab=0.75, bass=0.6),
        'climax': dict(kick=1.05, clap=1.0, chh=0.95, ohh=0.9, bass=1.05, stab=1.0, hook=1.1, arp=0.9, big=1),
        'outro': dict(pad=0.8, arp=0.7, stab=0.5, bass=0.4, chh=0.4)
    }

    print("Synthesizing Tune 03: 'Neon Kinetic'...")

    for b, sec in enumerate(PLAN):
        b0 = b * BAR
        L = LV[sec]
        g = lambda k: L.get(k, 0.0)
        ch = PROG[b % 4]
        nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

        # Arpeggios (16th notes - energetic clockwork drive)
        if g('arp'):
            notes = ARP_NOTES[ch]
            for i in range(16):
                t_arp = b0 + i * (BEAT / 4.0)
                if t_arp < engine.dur:
                    sig = pulse_arp(hz(notes[i]), 0.14) * g('arp')
                    engine.add('music', t_arp, sig, 1.0, pan=-0.5 + (i % 4) * 0.33, send=0.3)

        for bt in range(4):
            tb = b0 + bt * BEAT
            if tb >= engine.dur:
                break

            if g('kick') and (sec != 'intro' or b >= 1):
                engine.add('drums', tb, synth_kick(170, 52, 7.5, rng=engine.rng), g('kick'))
                engine.duck(tb, 0.28, 0.25)

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
                if g('stab'):
                    for k_i, nn in enumerate(CHORDS[ch]):
                        engine.add('music', off, filter_stab(hz(nn)), g('stab') * 0.85, pan=(-0.5, -0.15, 0.15, 0.5)[k_i], send=0.2)
                if g('bass'):
                    rf = hz(ROOTS[ch])
                    engine.add('music', off, disco_bass(rf * 2.0, BEAT * 0.38), g('bass'))

            if g('bass') and bt in (0, 2):
                engine.add('music', tb, disco_bass(hz(ROOTS[ch]), BEAT * 0.42), g('bass') * 0.95)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = neon_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = neon_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
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
                    engine.add('drums', t_s, synth_snare(220, rng=engine.rng), v, send=0.2)
                    t_s += BEAT / div
            engine.add('sfx', b0, synth_riser(BAR, rng=engine.rng), 0.32)

        if sec == 'climax' and (b == 0 or PLAN[b - 1] != 'climax'):
            engine.add('drums', b0, synth_crash(rng=engine.rng), 1.0, send=0.35)
            engine.add('sfx', b0, synth_impact(0.75, rng=engine.rng), send=0.3)
            engine.add('sfx', b0, synth_whoosh(0.9, rng=engine.rng), 0.3)

    engine.ramp_filter(0.0, 8.0, 0.25, 0.95)
    engine.ramp_filter(28.0, 36.0, 0.35, 1.0)
    engine.ramp_filter(52.0, 60.0, 1.0, 0.35)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_03_neon_kinetic.wav')
    mp3_out = os.path.join(here, 'tune_03_neon_kinetic.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
