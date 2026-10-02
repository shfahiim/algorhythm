"""Tune 12: 'Daybreak Anthem' (Cinematic Orchestral-Dance Hybrid)
Duration: 60.0s @ 100 BPM (25 bars @ 2.4s/bar)
Key: D Major (D -> G -> Bm -> A)
Character: Clockwork pizzicato strings, swelling orchestral pads, cinematic taiko impacts, triumphant crescendo, smooth fade.
"""

import os
import numpy as np
from synth_lib import (
    MusicEngine, hz, tt, lp, hp, bp, env, saw, pulse, supersaw,
    synth_kick, synth_clap, synth_hat_closed, synth_hat_open,
    synth_shaker, synth_snare, synth_crash, synth_riser, synth_impact, synth_whoosh
)

def run():
    BPM = 100.0
    TOTAL_BARS = 25
    engine = MusicEngine(bpm=BPM, total_bars=TOTAL_BARS, dur=60.0, seed=112)
    BEAT = engine.beat
    BAR = engine.bar

    # Pizzicato String Arpeggio (Short string pluck with rosin scratch)
    def pizzicato(f, d=0.18):
        t = tt(d)
        w = (
            np.sin(2.0 * np.pi * f * t) * 1.0 +
            saw(f * 2.0, t) * 0.35 * np.exp(-t * 18.0) +
            saw(f * 3.0, t) * 0.20 * np.exp(-t * 28.0)
        )
        bow_scratch = hp(engine.rng.standard_normal(len(t)), 4500) * np.exp(-t * 260.0) * 0.15
        out = (lp(w, 3800) * np.exp(-t * 12.0) + bow_scratch) * env(len(t), 0.002, 0.03)
        return out * 0.18

    # Swelling Orchestral String Ensemble Pad
    def orchestral_strings(f, d):
        s = supersaw(f, d, (-30, -18, -9, 0, 9, 18, 30), rng=engine.rng)
        t = tt(d)
        # Slow cinematic swelling envelope
        att = min(0.35, d * 0.3)
        e = np.ones_like(t)
        na = int(att * engine.sr)
        if na > 0:
            e[:na] = np.linspace(0, 1, na) ** 1.5
        dark = lp(s, 1200)
        bright = lp(s, 5000)
        sweep = dark + (bright - dark) * np.minimum(1.0, t / 1.5)
        return hp(sweep, 150) * e * 0.10

    # Cinematic Taiko / Low Tom Impact
    def cinematic_tom(pitch=65.0):
        d = 1.2
        t = tt(d)
        f = pitch + 40.0 * np.exp(-t * 18.0)
        body = np.sin(2.0 * np.pi * np.cumsum(f) / engine.sr) * np.exp(-t * 4.0)
        skin = lp(engine.rng.standard_normal(len(t)), 1200) * np.exp(-t * 25.0) * 0.45
        return np.tanh((body + skin) * 1.6) * 0.75

    # Triumphant Cinematic Lead
    def anthem_lead(f, d):
        t = tt(d)
        vib = 0.006 * np.sin(2.0 * np.pi * 5.5 * t) * np.minimum(1.0, t / 0.2)
        fm = f * (1.0 + vib)
        ph = np.cumsum(fm) / engine.sr
        w = saw(1.0, ph) * 0.65 + pulse(1.0, ph, 0.45) * 0.35
        dark = lp(w, 2200)
        bright = lp(w, 8500)
        out = dark + (bright - dark) * np.exp(-t * 6.5) + 0.3 * np.sin(4.0 * np.pi * ph) * np.exp(-t * 4.0)
        return hp(out, 180) * env(len(t), 0.005, min(0.12, d / 3.0)) * np.exp(-t * 0.85) * 0.23

    # Warm Sub-Bass
    def sub_bass(f, d):
        t = tt(d)
        s = np.sin(2.0 * np.pi * f * t) + 0.3 * lp(saw(f, t), 500)
        return np.tanh(s * 1.5) * env(len(t), 0.004, 0.04) * 0.35

    CHORDS = {
        'D': ['D4', 'F#4', 'A4', 'D5'],
        'G': ['D4', 'G4', 'B4', 'D5'],
        'Bm': ['D4', 'F#4', 'B4', 'F#5'],
        'A': ['C#4', 'E4', 'A4', 'E5']
    }
    ROOTS = {'D': 'D2', 'G': 'G1', 'Bm': 'B1', 'A': 'A1'}
    PROG = ['D', 'G', 'Bm', 'A']

    ARP_NOTES = {
        'D': ['D5', 'F#5', 'A5', 'D6', 'F#6', 'D6', 'A5', 'F#5', 'D5', 'F#5', 'A5', 'C#6', 'D6', 'F#6', 'A6', 'D7'],
        'G': ['G5', 'B5', 'D6', 'G6', 'B6', 'G6', 'D6', 'B5', 'G5', 'B5', 'D6', 'F#6', 'G6', 'B6', 'D7', 'G7'],
        'Bm': ['B4', 'D5', 'F#5', 'B5', 'D6', 'B5', 'F#5', 'D5', 'B4', 'D5', 'F#5', 'A5', 'B5', 'D6', 'F#6', 'B6'],
        'A': ['A4', 'C#5', 'E5', 'A5', 'C#6', 'A5', 'E5', 'C#5', 'A4', 'C#5', 'E5', 'G#5', 'A5', 'C#6', 'E6', 'A6']
    }

    HOOK = {
        'D': [(0.0, 'F#5', 0.5), (0.5, 'A5', 0.5), (1.0, 'D6', 0.75), (1.75, 'C#6', 0.5), (2.25, 'B5', 0.5), (2.75, 'A5', 0.5), (3.25, 'D6', 0.75)],
        'G': [(0.0, 'G5', 0.5), (0.5, 'B5', 0.5), (1.0, 'D6', 1.0), (2.0, 'C6', 0.5), (2.5, 'B5', 0.5), (3.0, 'G5', 0.5), (3.5, 'B5', 0.5)],
        'Bm': [(0.0, 'F#5', 0.5), (0.5, 'B5', 0.5), (1.0, 'D6', 1.0), (2.0, 'C#6', 0.5), (2.5, 'B5', 0.5), (3.0, 'F#5', 0.5), (3.5, 'B5', 0.5)],
        'A': [(0.0, 'E5', 0.5), (0.5, 'A5', 0.5), (1.0, 'C#6', 0.75), (1.75, 'D6', 0.5), (2.25, 'C#6', 0.5), (2.75, 'B5', 0.5), (3.25, 'A5', 0.75)]
    }

    # 25-bar plan
    PLAN = (
        ['intro'] * 4 +
        ['groove'] * 5 +
        ['verse'] * 4 +
        ['build'] * 4 +
        ['climax'] * 5 +
        ['outro'] * 3
    )

    LV = {
        'intro': dict(kick=0.5, pizz=0.85, strings=0.7),
        'groove': dict(kick=1.0, clap=0.9, chh=0.8, ohh=0.7, bass=1.0, pizz=0.8, strings=0.55, shk=0.6),
        'verse': dict(kick=1.0, clap=0.95, chh=0.85, ohh=0.75, bass=1.0, pizz=0.75, strings=0.6, hook=1.0, shk=0.7),
        'build': dict(strings=0.85, pizz=0.95, bass=0.6),
        'climax': dict(kick=1.05, clap=1.0, chh=0.95, ohh=0.9, bass=1.05, strings=0.9, hook=1.1, pizz=0.9, big=1),
        'outro': dict(strings=0.8, pizz=0.75, bass=0.4, chh=0.4)
    }

    print("Synthesizing Tune 12: 'Daybreak Anthem'...")

    for b, sec in enumerate(PLAN):
        b0 = b * BAR
        L = LV[sec]
        g = lambda k: L.get(k, 0.0)
        ch = PROG[b % 4]
        nxt = PLAN[b + 1] if b + 1 < TOTAL_BARS else None

        # Pizzicato Arpeggio (Clockwork time passing)
        if g('pizz'):
            notes = ARP_NOTES[ch]
            for i in range(16):
                t_arp = b0 + i * (BEAT / 4.0)
                if t_arp < engine.dur:
                    sig = pizzicato(hz(notes[i]), 0.18) * g('pizz')
                    engine.add('music', t_arp, sig, 1.0, pan=-0.5 + (i % 4) * 0.33, send=0.3)

        for bt in range(4):
            tb = b0 + bt * BEAT
            if tb >= engine.dur:
                break

            if g('kick') and (sec != 'intro' or b >= 1):
                engine.add('drums', tb, synth_kick(160, 48, 7.2, rng=engine.rng), g('kick'))
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
                if g('bass'):
                    rf = hz(ROOTS[ch])
                    engine.add('music', off, sub_bass(rf * 2.0, BEAT * 0.38), g('bass'))

            if g('bass') and bt in (0, 2):
                engine.add('music', tb, sub_bass(hz(ROOTS[ch]), BEAT * 0.42), g('bass') * 0.95)

        # Taiko tom impact on bar downbeat of drop/climax
        if sec == 'climax' and b % 2 == 0:
            engine.add('drums', b0, cinematic_tom(55.0), 0.7, send=0.4)

        if g('strings'):
            d_p = min(BAR + 0.1, engine.dur - b0)
            for k_i, nn in enumerate(CHORDS[ch]):
                engine.add('music', b0, orchestral_strings(hz(nn), d_p), g('strings'), pan=(-0.6, -0.2, 0.2, 0.6)[k_i], send=0.35)

        if g('hook'):
            for o, nn, ln in HOOK[ch]:
                ts = b0 + o * BEAT
                if ts < engine.dur:
                    sig = anthem_lead(hz(nn), ln * BEAT * 0.95) * g('hook')
                    if g('big'):
                        sig_oct = anthem_lead(hz(nn) * 2.0, ln * BEAT * 0.95) * 0.45
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

    engine.ramp_filter(0.0, 9.6, 0.25, 0.95)
    engine.ramp_filter(28.8, 38.4, 0.35, 1.0)
    engine.ramp_filter(52.8, 60.0, 1.0, 0.35)

    here = os.path.dirname(os.path.abspath(__file__))
    wav_out = os.path.join(here, 'tune_12_daybreak_anthem.wav')
    mp3_out = os.path.join(here, 'tune_12_daybreak_anthem.mp3')
    engine.export(wav_out, mp3_out, fade_out_sec=6.5)

if __name__ == '__main__':
    run()
