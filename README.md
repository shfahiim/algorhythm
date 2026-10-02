# ⚡ Algorhythm

> **100% Procedural, Algorithmic Music Synthesis in Python.**  
> *Zero DAWs. Zero External Samples. Pure Mathematics, DSP, and Code.*

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-DSP-013243.svg)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-Signal-196b99.svg)](https://scipy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Audio: CC BY 4.0](https://img.shields.io/badge/Audio-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## 🎧 What is Algorhythm?

**Algorhythm** is an open-source algorithmic music production suite and track library written entirely in Python. Every kick drum, sub-bass, detuned supersaw chord, delicate acoustic fingerpicking pluck, felt piano chord, and orchestral cello swell is generated mathematically from raw waveforms using `numpy` and `scipy.signal`.

No sample packs. No sound fonts. No MIDI plugins. No digital audio workstations.

The library features **14 ready-to-listen master tracks** spanning upbeat house, French filter-disco, synthwave, chiptune future-pop, organic indie folk-dance, and cinematic acoustic homage, plus a full **spectral reverse-engineering toolkit**.

---

## 🎼 The 14-Track Procedural Catalog

| # | Track Title | Genre / Vibe | BPM | Key & Harmony | Signature Timbres | Audio |
|---|---|---|---|---|---|---|
| **00** | **Motion Theme** | Dynamic Film Score | 96 | D Maj / Min (`D – A – Bm – G`) | The original 120s motion graphic score. House stabs, sub-bass, SFX drops. | [MP3](audio/mp3/tune_00_motion_theme.mp3) • [WAV](audio/wav/tune_00_motion_theme.wav) • [Code](tunes/tune_00_motion_theme.py) |
| **01** | **Sunlight Drift** | Uplifting Melodic House | 100 | A Major (`Dmaj7 – E – F#m – A`) | 16th-note clockwork bell arps, punchy 4-on-the-floor kick, rolling sub-bass. | [MP3](audio/mp3/tune_01_sunlight_drift.mp3) • [WAV](audio/wav/tune_01_sunlight_drift.wav) • [Code](tunes/tune_01_sunlight_drift.py) |
| **02** | **Golden Horizon** | Vibrant Nu-Disco | 112 | G Major (`Cadd9 – D – Em7 – G`) | Cascading fast-forward chime arpeggios, bouncy syncopated bass, brass stabs. | [MP3](audio/mp3/tune_02_golden_horizon.mp3) • [WAV](audio/wav/tune_02_golden_horizon.wav) • [Code](tunes/tune_02_golden_horizon.py) |
| **03** | **Neon Kinetic** | French Electro-House | 120 | E Minor (`Em – C – G – D`) | Punchy French-touch groove, resonant pulse arpeggios, disco octave bass. | [MP3](audio/mp3/tune_03_neon_kinetic.mp3) • [WAV](audio/wav/tune_03_neon_kinetic.wav) • [Code](tunes/tune_03_neon_kinetic.py) |
| **04** | **Morning Island** | Tropical Chill-House | 104 | F Major (`Bbmaj7 – C – Dm7 – F`) | Warm wooden kalimba & marimba plucks, organic shaker groove, breezy flute. | [MP3](audio/mp3/tune_04_morning_island.mp3) • [WAV](audio/wav/tune_04_morning_island.wav) • [Code](tunes/tune_04_morning_island.py) |
| **05** | **Retro Highway** | Outrun / Synthwave | 116 | B Minor (`Bm – G – A – F#m`) | Driving 16th rolling analog saw bassline, 80s gated reverb snare, vintage brass. | [MP3](audio/mp3/tune_05_retro_highway.mp3) • [WAV](audio/wav/tune_05_retro_highway.wav) • [Code](tunes/tune_05_retro_highway.py) |
| **06** | **Pixel Rush** | Chiptune Future-Pop | 128 | C Major (`F – G – Em – Am`) | 8-bit variable pulse arps, bouncy future-bass kicks, fizzy supersaw chords. | [MP3](audio/mp3/tune_06_pixel_rush.mp3) • [WAV](audio/wav/tune_06_pixel_rush.wav) • [Code](tunes/tune_06_pixel_rush.py) |
| **07** | **Solar Spark** | Nu-Funk & Slap Bass | 108 | D Major (`Gmaj7 – A7 – Bm7 – D`) | Resonant slap bass with octave pops, muted funk rhythm guitar, warm Rhodes. | [MP3](audio/mp3/tune_07_solar_spark.mp3) • [WAV](audio/wav/tune_07_solar_spark.wav) • [Code](tunes/tune_07_solar_spark.py) |
| **08** | **Quantum Leap** | Electro Swing & Shuffle | 96 | C Minor (`Cm – Ab – Bb – Eb`) | Triplet swing bounce, acoustic upright bass, vintage horn stabs, swung hats. | [MP3](audio/mp3/tune_08_quantum_leap.mp3) • [WAV](audio/wav/tune_08_quantum_leap.wav) • [Code](tunes/tune_08_quantum_leap.py) |
| **09** | **Skyline Sprint** | Euphoric Trance Anthem | 132 | G# Minor (`E – F# – G#m – B`) | Fast 16th rolling trance bassline, massive supersaw anthem chords, soaring lead. | [MP3](audio/mp3/tune_09_skyline_sprint.mp3) • [WAV](audio/wav/tune_09_skyline_sprint.wav) • [Code](tunes/tune_09_skyline_sprint.py) |
| **10** | **Coffeehouse Bloom** | Organic Indie Folk-Dance | 88 | C Major (`C – G – Am – F`) | Acoustic fingerstyle string plucks, deep wooden stomp kick, sunny whistle. | [MP3](audio/mp3/tune_10_coffeehouse_bloom.mp3) • [WAV](audio/wav/tune_10_coffeehouse_bloom.wav) • [Code](tunes/tune_10_coffeehouse_bloom.py) |
| **11** | **Cyber Arcade** | Tokyo City Pop / Funk | 112 | Eb Major (`Abmaj7 – Bb – Cm7 – Eb`) | Bright FM electric piano, snappy synth-bass, talkbox-style vocal formant lead. | [MP3](audio/mp3/tune_11_cyber_arcade.mp3) • [WAV](audio/wav/tune_11_cyber_arcade.wav) • [Code](tunes/tune_11_cyber_arcade.py) |
| **12** | **Daybreak Anthem** | Cinematic Orchestral-Dance | 100 | D Major (`D – G – Bm – A`) | Clockwork pizzicato strings, swelling cello/violin pads, cinematic taiko toms. | [MP3](audio/mp3/tune_12_daybreak_anthem.mp3) • [WAV](audio/wav/tune_12_daybreak_anthem.wav) • [Code](tunes/tune_12_daybreak_anthem.py) |
| **13** | **The Long Journey** | Max LL Cinematic Homage | 72 | F# Minor (`F#m – Dmaj7 – A – Eadd9`) | *Homage to Spiritfarer*. Acoustic fingerstyle guitar, felt piano, cello, music-box bells. | [MP3](audio/mp3/tune_13_departures_passerby_homage.mp3) • [WAV](audio/wav/tune_13_departures_passerby_homage.wav) • [Code](tunes/tune_13_departures_passerby_homage.py) |

---

## 🛠 DSP Architecture & Sound Synthesis

Everything is built from raw mathematical primitives inside [`engine/synth_lib.py`](engine/synth_lib.py):

### 1. Mathematical Oscillators
* **Multi-voice Supersaw:** Stacks 5 to 7 sawtooth oscillators detuned by cents ($2^{c/1200}$) with randomized initial phase.
* **Karplus-Strong String Synthesis:** Decaying recursive comb filtering and body resonance filters for realistic acoustic guitars.
* **FM Synthesis:** Carrier and modulator sine operators generating bright DX7-style electric tines and warm felt piano tones.
* **Variable Duty Pulse:** 12.5%, 25%, and 50% square waves for retro chiptune arpeggios.

### 2. Filtering & Dynamics
* **Butterworth Second-Order Cascades (`sosfilt`):** Low-pass, high-pass, and band-pass filtering with zero numerical instability.
* **Dynamic Sidechain Compressor (`duck`):** Exponential volume ducking curves keyed to the kick drum for dance pumping.
* **Filter Envelopes:** Real-time cutoff modulation sweeping smoothly from dark sub tones to wide-open presence.

### 3. Acoustic Space & Mastering
* **Algorithmic Convolution Reverb:** Generates stereo-decorrelated exponential noise impulse responses convolved via `scipy.signal.fftconvolve` to place instruments inside physical rooms.
* **Analog Soft Tape Saturation:** Driven through hyperbolic tangent soft-clipping ($\tanh(1.25 \cdot x) / \tanh(1.25)$) for tape-style harmonic saturation without harsh digital clipping.
* **Smooth Fades & Highpass Clean:** Subsonic 30 Hz rumble removal and natural exponential decay endings.

---

## 🔬 Spectral Reverse-Engineering Toolkit

Algorhythm includes a research-grade spectral analyzer in [`analysis/`](analysis/):
* **STFT Chromagram & Key Profiling:** Uses Krumhansl-Schmuckler key-finding correlations across all 24 major and minor modes.
* **Onset Strength Tempogram:** Autocorrelation of spectral flux to extract exact BPM and groove timings.
* **Spectral Centroid & Band Decomposition:** Measures energy across Sub-Bass (20–60Hz), Bass (60–250Hz), Low-Mids (250–1000Hz), High-Mids (1–4kHz), Presence (4–10kHz), and Air.

See the complete reverse-engineering study:  
📄 [`analysis/MAX_LL_SPECTRAL_ANALYSIS.md`](analysis/MAX_LL_SPECTRAL_ANALYSIS.md)

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install the lightweight requirements:
```bash
git clone https://github.com/shfahiim/algorhythm.git
cd algorhythm
pip install -r requirements.txt
```

### 2. Batch Render All Tracks
Synthesize all 14 master tracks in ~45 seconds:
```bash
python generate_all.py
```

### 3. Render an Individual Track
```bash
python tunes/tune_01_sunlight_drift.py
python tunes/tune_13_departures_passerby_homage.py
```

### 4. Run Spectral Analysis on Any Audio File
```bash
python analysis/spectral_analyzer.py
```

---

## 📜 License

* **Code & Engine:** Licensed under the [MIT License](LICENSE).
* **Music & Audio Assets:** Licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to use, remix, and share the music with attribution!
