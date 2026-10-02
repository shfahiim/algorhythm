"""Tune 06: 'Pixel Rush' (Chiptune-Infused Future Pop)
Duration: 60.0s @ 128 BPM (32 bars @ 1.875s/bar)
Key: C Major / A Minor (F -> G -> Em -> Am)
Character: Fast, playful 8-bit pulse arpeggios, bouncy future-pop rhythm, video-game joy, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse, supersaw,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 128.0
    TOTAL_BARS = 32
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=106)
    BEAT = engine.beat
    BAR = engine.bar

    # 8-bit Chiptune Pulse Arp (25% and 50% duty cycle)
    def chip_arp(f, d=0.10, duty=0.25):
        t = tt(d)
        w = pulse(f, t, duty)
        return hp(w, 200) * env(len(t), 0.002, 0.015) * 0.13

    # Future-pop Bouncy Synth Bass
    def chip_bass(f, d):
        t = tt(d)
        w = saw(f, t) * 0.5 + pulse(f, t, 0.5) * 0.5
        filt_sweep = lp(w, 1600) * np.exp(-t * 26.0) + lp(w, 500) * 0.5
        return np.tanh(filt_sweep * 1.8) * env(len(t), 0.002, 0.03) * 0.36

    # Bright Fizzy Chords
    def chip_chord(f, d=BEAT * 0.4):
        s = supersaw(f, d, (-16, -8, 0, 8, 16), rng=engine.rng)
        t = tt(d)
        dark = lp(s, 1400)
        bright = lp(s, 6500)
        out = dark + (bright - dark) * np.exp(-t * 16.0)
        return hp(out, 200) * env(len(t), 0.003, 0.03) * 0.18

    # Happy Lead Synth
    def chip_lead(f, d):
        t = tt(d)
        w = pulse(f, t, 0.5) * 0.6 + saw(f, t) * 0.4
        return lp(hp(w, 250), 6000) * env(len(t), 0.003, min(0.08, d / 3.0)) * np.exp(-t * 1.2) * 0.22

    CHORDS = {
        'F': ['C4', 'F4', 'A4', 'C5'],
        'G': ['D4', 'G4', 'B4', 'D5'],
        'Em': ['E4', 'G4', 'B4', 'E5'],
        'Am': ['E4', 'A4', 'C5', 'E5']
    }
    ROOTS = {'F': 'F1', 'G': 'G1', 'Em': 'E2', 'Am': 'A1'}
    PROG = ['F', 'G', 'Em', 'Am']

    ARP_NOTES = {
        'F': ['F5', 'A5', 'C6', 'F6', 'A6', 'F6', 'C6', 'A5', 'F5', 'A5', 'C6', 'E6', 'F6', 'A6', 'C7', 'F7'],
        'G': ['G5', 'B5', 'D6', 'G6', 'B6', 'G6', 'D6', 'B5', 'G5', 'B5', 'D6', 'F#6', 'G6', 'B6', 'D7', 'G7'],
        'Em': ['E5', 'G5', 'B5', 'E6', 'G6', 'E6', 'B5', 'G5', 'E5', 'G5', 'B5', 'D6', 'E6', 'G6', 'B6', 'E7'],
        'Am': ['A5', 'C6', 'E6', 'A6', 'C7', 'A6', 'E6', 'C6', 'A5', 'C6', 'E6', 'G6', 'A6', 'C7', 'E7', 'A7']
    }

    HOOK = {
        'F': [(0.0, 'A5', 0.5), (0.5, 'C6', 0.5), (1.0, 'F6', 0.75), (1.75, 'E6', 0.5), (2.25, 'C6', 0.5), (2.75, 'A5', 0.5), (3.25, 'C6', 0.75)],
        'G': [(0.0, 'B5', 0.5), (0.5, 'D6', 0.5), (1.0, 'G6', 1.0), (2.0, 'F#6', 0.5), (2.5, 'D6', 0.5), (3.0, 'B5', 0.5), (3.5, 'D6', 0.5)],
        'Em': [(0.0, 'G5', 0.5), (0.5, 'B5', 0.5), (1.0, 'E6', 1.0), (2.0, 'D6', 0.5), (2.5, 'B5', 0.5), (3.0, 'G5', 0.5), (3.5, 'B5', 0.5)],
        'Am': [(0.0, 'C6', 0.5), (0.5, 'E6', 0.5), (1.0, 'A6', 0.75), (1.75, 'B6', 0.5), (2.25, 'A6', 0.5), (2.75, 'E6', 0.5), (3.25, 'C6', 0.75)]
    }

    # 32-bar plan
    PLAN = (
        ['intro'] * 4 +
        ['groove'] * 8 +
        ['verse'] * 4 +
        ['build'] * 4 +
        ['climax'] * 8 +
        ['outro'] * 4
    )

    LV = {
        'intro': dict(kick=0.5, arp=0.85, chord=0.6),
        'groove': dict(kick=1.0, clap=0.9, chh=0.8, ohh=0.7, bass=1.0, chord=0.9, arp=0.7, shk=0.6),
        'verse': dict(kick=1.0, clap=0.95, chh=0.85, ohh=0.75, bass=1.0, chord=0.85, hook=1.0, arp=0.75, shk=0.7),
        'build': dict(chord=0.8, arp=1.0, bass=0.6),
        'climax': dict(kick=1.05, clap=1.0, chh=0.95, ohh=0.9, bass=1.05, chord=1.0, hook=1.1, arp=0.9, big=1),
        'outro': dict(chord=0.8, arp=0.75, bass=0.4, chh=0.4)
    }

    print("Synthesizing Tune 06: 'Pixel Rush'...")

    for b, sec in enumerate(PLAN):
        b0 = b * BAR
        L = LV[sec]
        g = lambda k: L.get(k, 0.0)
        ch = PROG[b % 4]
        nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

        # 16th Chip Arpeggio
        if g('arp'):
            notes = ARP_NOTES[ch]
            for i in range(16):
                t_arp = b0 + i * (BEAT / 4.0)
                if t_arp < engine.dur:
                    duty = 0.25 if i % 2 == 0 else 0.5
                    sig = chip_arp(hz(notes[i]), 0.12, duty=duty) * g('arp')
                    engine.add('music', t_arp, sig, 1.0, pan=-0.5 + (i % 4) * 0.33, send=0.25)

        for bt in range(4):
            tb = b0 + bt * BEAT
            if tb >= engine.dur:
                break

            if g('kick') and (sec != 'intro' or b >= 1):
                engine.add('drums', tb, synth_kick(175, 52, 7.8, rng=engine.rng), g('kick'))
                engine.duck(tb, 0.26, 0.25)

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
                if g('chord'):
                    for k_i, nn in enumerate(CHORDS[ch]):
                        engine.add('music', off, chip_chord(hz(nn)), g('chord') * 0.85, pan=(-0.5, -0.15, 0.15, 0.5)[k_i], send=0.2)
                if g('bass'):
                    engine.add('music', off, chip_bass(hz(ROOTS[ch]) * 2.0, BEAT * 0.38), g('bass'))

            if g('bass') and bt in (0, 2):
                engine.add('music', tb, chip_bass(hz(ROOTS[ch]), BEAT * 0.42), g('bass') * 0.95)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = chip_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = chip_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
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

    engine.ramp_filter(0.0, 7.5, 0.25, 0.95)
    engine.ramp_filter(30.0, 37.5, 0.35, 1.0)
    engine.ramp_filter(52.5, 60.0, 1.0, 0.35)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_06_pixel_rush.wav')
    mp3_out = os.path.join(here, 'tune_06_pixel_rush.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
