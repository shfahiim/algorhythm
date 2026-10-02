# In-Depth Spectral & Musicological Analysis: Max LL ("Departures" & "Passerby")

**Analyst / Sound Engineer**: AI Audio Research & DSP Engineering  
**Analyzed Tracks**:
1. **"Departures"** by Max LL (*Spiritfarer OST*) — [YouTube: 2nF0Y4YSUtk](https://www.youtube.com/watch?v=2nF0Y4YSUtk)
2. **"Passerby"** by Max LL (*Spiritfarer OST*) — [YouTube: -p2AW5gS6tU](https://www.youtube.com/watch?v=-p2AW5gS6tU)
**Raw Data**: [`tune/analysis/spectral_analysis_results.json`](file:///home/fahim/Storage/DesktopMoved/medwise/tune/analysis/spectral_analysis_results.json)

---

## 1. Executive Summary: The Sonic & Emotional DNA of Max LL

Both tracks originate from the celebrated *Spiritfarer* score composed by **Max LL**. The music functions as an emotional anchor: it explores themes of transition, memories, passage of time, nostalgia, and acceptance. 

Rather than relying on modern electronic sidechaining or synthetic high-frequency energy, Max LL uses:
1. **Intimate Acoustic Chamber Timbres**: Close-mic'd acoustic fingerstyle guitar, felted upright piano, expressive solo cello, and orchestral violin section.
2. **Subtle Percussive Clockwork**: Rhythmic motion is carried not by drum kits, but by delicate acoustic guitar arpeggiation (fingerpicking patterns), subtle finger taps on the guitar body, and high glockenspiel / music-box chime transients.
3. **Warm, Unhyped Spectral Balance**: The vast majority of acoustic energy (>80%) resides below 1 kHz, creating an intimate, nostalgic, and non-fatiguing auditory environment.
4. **Organic Dynamic Breathing**: Wide crest factor (5.27 to 6.68 dB peak-to-RMS) with long natural room reverbs (~2.5s) and gentle rubato phrasing.

---

## 2. Comparative Technical Measurements

| Metric | "Departures" (2nF0Y4YSUtk) | "Passerby" (-p2AW5gS6tU) | Engineering Deduction |
|---|---|---|---|
| **Duration** | 3m 19s (199.3s) | 2m 37s (157.2s) | Standard contemplative cinematic piece duration |
| **Detected Primary Tempo** | **61.5 BPM** (123.0 pulse) | **71.8 BPM** (143.6 pulse) | Gentle walking / breathing tempo; slow ballad / waltz pulse |
| **Primary Tonality (Key)** | **F Major / D Minor** (corr: 0.843) | **A Major / F# Minor** (corr: 0.764) | Melancholic yet hopeful modal interchange (I - vi - IV - V) |
| **Spectral Centroid (Brightness)** | **2,181 Hz** (std: 1,264 Hz) | **1,925 Hz** (std: 1,068 Hz) | Extremely warm; rolled-off top end (>8 kHz is softly muted) |
| **Spectral Rolloff (85% Energy)** | **4,388 Hz** | **3,848 Hz** | 85% of all musical power is concentrated below ~4 kHz |
| **Crest Factor (Dynamic Range)** | **5.27** | **6.68** | Highly uncompressed; preservation of delicate acoustic attacks |
| **Overall RMS Level** | -14.68 dBFS | -16.55 dBFS | Mastered with classical/film headroom, not pushed to the 0 dB limiter |
| **Stereo Width Ratio** | **0.827** | **0.834** | Ultra-wide acoustic soundstage with natural stereo hall reverb |

---

## 3. Frequency Band Energy Decomposition

Both tracks exhibit an identical acoustic mixing signature:

```
Energy Distribution:
┌────────────────────────────────────────────────────────┐
│ Sub-Bass (20-60 Hz)     : 11% - 21%  (warm cello body, floor resonance)
│ Bass (60-250 Hz)        : 36% - 49%  (guitar lower strings, cello fundamental)
│ Low-Mids (250-1000 Hz)  : 27%        (woody guitar chamber, felt piano body)
│ High-Mids (1000-4000 Hz): 11% - 14%  (finger slide, string bow friction)
│ Presence (4-10 kHz)     : 0.7% - 1.2% (sparkle of bells, air breath)
│ Ultra-Air (10-20 kHz)   : 0.05%      (essentially silent, zero digital hiss)
└────────────────────────────────────────────────────────┘
```

### Critical Audio Engineering Deductions:
* **The "Anti-EDM" Curve**: Notice the presence band (4–10 kHz) accounts for only ~1% of total energy. In electronic dance music, hi-hats and supersaws push this band to 15–25%. Here, the sound is intentionally attenuated above 5 kHz to replicate vintage ribbon microphones and felt dampers.
* **Low-Mid Dominance (250–1000 Hz)**: Sitting at 27%, this is where the "emotional warmth" lives. It represents the resonant wood of the acoustic guitar soundboard and the felt-covered hammers of an upright piano.

---

## 4. Musical & Harmonic Structure

### A. "Departures"
- **Progression**: Centered around `Dm – Bb – F – C` with modal drift to `Am`.
- **Top Pitch Classes**: `A (14.6%)`, `C (14.3%)`, `D (13.5%)`, `F (12.5%)`, `A# (11.4%)`.
- **Arrangement Curve**:
  - `0:00 – 0:30`: Minimalist intro (-30 dB RMS). Solo acoustic fingerpicking.
  - `0:32 – 1:00`: Swelling emotional entry (-14 dB to -10 dB RMS). Warm sustained cello and violins enter, creating a lush bed.
  - `1:00 – 2:40`: Full emotional height (-12 dB RMS). Interweaving counter-melodies on piano and high woodwind/glockenspiel.
  - `2:45 – 3:19`: Natural deceleration and gentle exponential decay to absolute silence (-63 dB RMS).

### B. "Passerby"
- **Progression**: Centered around `F#m – D – A – E` and `A – E – F#m – D`.
- **Top Pitch Classes**: `A (15.0%)`, `C# (12.0%)`, `D (10.3%)`, `F# (9.3%)`, `G# (8.6%)`.
- **Arrangement Curve**:
  - Gentle acoustic guitar arpeggiation establishing a comforting, steady walking rhythm.
  - High pitch bells / music-box chiming accents playing syncopated grace notes on offbeats.
  - Slow harmonic shifts with suspensions (sus2 and add9 intervals) providing a bitter-sweet, nostalgic feeling.

---

## 5. Architectural Blueprint for Companion Track Synthesis

To recreate a track with this exact spirit and sonic fingerprint procedurally in Python:

1. **Tempo & Meter**: 68–72 BPM in 3/4 or gentle 6/8 walking time ($1 \text{ bar} \approx 2.5\text{s} - 2.8\text{s}$).
2. **Key**: **F# Minor / A Major** (`F#m – D – A – E`).
3. **Core Timbral Synthesis**:
   * **Acoustic Guitar**: Karplus-Strong string synthesis with wood body resonance filter and random micro-timing humanization.
   * **Felt Piano**: Multi-operator FM/sine with muted harmonics (low-pass at 1,800 Hz) and soft velocity response.
   * **Cinematic Cello & Violin Pad**: Multi-detuned sawtooth oscillators heavily low-passed at 1,400 Hz with slow exponential attack ($0.4\text{s}$) and expressive vibrato ($5.2\text{ Hz}$).
   * **Celestial Glockenspiel**: High sine cluster ($1\text{x}, 2.76\text{x}, 5.4\text{x}$) with crystal-clear exponential decay, echoing in stereo.
4. **Mix & Space**:
   * Steep 6 kHz high-shelf rolloff to emulate the warm acoustic character.
   * 2.8-second convolution room reverb simulating a wooden concert hall.
   * Gentle exponential fade-out over the final 8 seconds.
