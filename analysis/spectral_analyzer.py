"""Spectral and Musicological Analyzer
Performs complete Fourier Transform, STFT Chromagram, Krumhansl-Schmuckler Key Detection,
Onset Strength / Autocorrelation Tempo Extraction, Spectral Centroid, Band Energy Splits,
and Form Segmentation on reference audio tracks using pure numpy & scipy.
"""

import os
import json
import numpy as np
from scipy.io import wavfile
from scipy.signal import stft, butter, sosfilt

PITCH_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Krumhansl-Kessler key profiles
KRUMHANSL_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KRUMHANSL_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

def analyze_track(file_path, track_title):
    sr, data = wavfile.read(file_path)
    if data.dtype == np.int16:
        x = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        x = data.astype(np.float32) / 2147483648.0
    else:
        x = data.astype(np.float32)

    # Convert to mono if stereo for analysis, preserve stereo width metric
    if x.ndim == 2:
        mono = np.mean(x, axis=1)
        stereo_diff = x[:, 0] - x[:, 1]
        stereo_width = float(np.sqrt(np.mean(stereo_diff ** 2)) / (np.sqrt(np.mean(mono ** 2)) + 1e-9))
    else:
        mono = x
        stereo_width = 0.0

    duration = len(mono) / sr
    rms = float(np.sqrt(np.mean(mono ** 2)))
    peak = float(np.max(np.abs(mono)))
    crest_factor = float(peak / (rms + 1e-9))

    # STFT parameters
    nperseg = 4096
    noverlap = 3072
    hop = nperseg - noverlap
    f, t, Zxx = stft(mono, fs=sr, nperseg=nperseg, noverlap=noverlap)
    mag = np.abs(Zxx)

    # 1. Frequency Band Energy Splits
    f_bins = f
    sub_mask = (f_bins >= 20) & (f_bins < 60)
    bass_mask = (f_bins >= 60) & (f_bins < 250)
    low_mid_mask = (f_bins >= 250) & (f_bins < 1000)
    high_mid_mask = (f_bins >= 1000) & (f_bins < 4000)
    presence_mask = (f_bins >= 4000) & (f_bins < 10000)
    air_mask = (f_bins >= 10000) & (f_bins < 20000)

    total_energy = np.sum(mag ** 2) + 1e-9
    energy_bands = {
        'sub_bass_20_60Hz': float(np.sum(mag[sub_mask, :] ** 2) / total_energy * 100),
        'bass_60_250Hz': float(np.sum(mag[bass_mask, :] ** 2) / total_energy * 100),
        'low_mids_250_1000Hz': float(np.sum(mag[low_mid_mask, :] ** 2) / total_energy * 100),
        'high_mids_1000_4000Hz': float(np.sum(mag[high_mid_mask, :] ** 2) / total_energy * 100),
        'presence_4000_10000Hz': float(np.sum(mag[presence_mask, :] ** 2) / total_energy * 100),
        'air_10000_20000Hz': float(np.sum(mag[air_mask, :] ** 2) / total_energy * 100),
    }

    # 2. Spectral Centroid (Brightness curve)
    f_weighted = np.sum(f[:, None] * mag, axis=0) / (np.sum(mag, axis=0) + 1e-9)
    mean_centroid = float(np.mean(f_weighted))
    std_centroid = float(np.std(f_weighted))

    # 3. Spectral Rolloff (85% energy point)
    cum_mag = np.cumsum(mag, axis=0)
    tot_mag = cum_mag[-1, :]
    rolloff_idx = np.apply_along_axis(lambda col: np.searchsorted(col, 0.85 * col[-1]), 0, cum_mag)
    rolloff_freqs = f[rolloff_idx]
    mean_rolloff = float(np.mean(rolloff_freqs))

    # 4. Chromagram & Key Detection
    chroma = np.zeros((12, mag.shape[1]))
    valid_f = (f >= 55.0) & (f <= 2500.0)
    f_valid = f[valid_f]
    mag_valid = mag[valid_f, :]
    midi_notes = 12.0 * np.log2(f_valid / 440.0) + 69.0
    pitch_classes = (np.round(midi_notes).astype(int)) % 12

    for p in range(12):
        mask_p = (pitch_classes == p)
        if np.any(mask_p):
            chroma[p, :] = np.sum(mag_valid[mask_p, :], axis=0)

    # Normalize chroma
    chroma_norm = chroma / (np.sum(chroma, axis=0, keepdims=True) + 1e-9)
    global_chroma = np.sum(chroma, axis=1)
    global_chroma /= (np.sum(global_chroma) + 1e-9)

    # Key Correlation
    best_key = None
    best_corr = -1.0
    key_correlations = {}

    for i in range(12):
        # Major
        rot_maj = np.roll(KRUMHANSL_MAJOR, i)
        corr_maj = float(np.corrcoef(global_chroma, rot_maj)[0, 1])
        key_name_maj = f"{PITCH_NAMES[i]} Major"
        key_correlations[key_name_maj] = corr_maj
        if corr_maj > best_corr:
            best_corr = corr_maj
            best_key = key_name_maj

        # Minor
        rot_min = np.roll(KRUMHANSL_MINOR, i)
        corr_min = float(np.corrcoef(global_chroma, rot_min)[0, 1])
        key_name_min = f"{PITCH_NAMES[i]} Minor"
        key_correlations[key_name_min] = corr_min
        if corr_min > best_corr:
            best_corr = corr_min
            best_key = key_name_min

    # Sort top 5 candidate keys
    sorted_keys = sorted(key_correlations.items(), key=lambda kv: kv[1], reverse=True)[:5]

    # Time-varying Chord Progressions (segmented in 4-second blocks)
    block_dur = 4.0
    block_frames = int(block_dur / (hop / sr))
    num_blocks = mag.shape[1] // block_frames
    chord_progression = []

    for b in range(num_blocks):
        b_slice = slice(b * block_frames, (b + 1) * block_frames)
        b_chroma = np.sum(chroma[:, b_slice], axis=1)
        b_chroma /= (np.sum(b_chroma) + 1e-9)

        # Find best triad for this block
        best_chord_name = "Unknown"
        best_c_score = -1.0
        for root in range(12):
            # Major triad (0, 4, 7)
            maj_triad = np.zeros(12)
            maj_triad[root] = 1.0; maj_triad[(root + 4) % 12] = 0.8; maj_triad[(root + 7) % 12] = 0.8
            sc_maj = float(np.dot(b_chroma, maj_triad))
            if sc_maj > best_c_score:
                best_c_score = sc_maj
                best_chord_name = f"{PITCH_NAMES[root]}"

            # Minor triad (0, 3, 7)
            min_triad = np.zeros(12)
            min_triad[root] = 1.0; min_triad[(root + 3) % 12] = 0.8; min_triad[(root + 7) % 12] = 0.8
            sc_min = float(np.dot(b_chroma, min_triad))
            if sc_min > best_c_score:
                best_c_score = sc_min
                best_chord_name = f"{PITCH_NAMES[root]}m"

        chord_progression.append({
            'time_sec': round(b * block_dur, 2),
            'detected_chord': best_chord_name,
            'top_pitch_classes': [PITCH_NAMES[p] for p in np.argsort(b_chroma)[-3:][::-1]]
        })

    # 5. Onset Strength Envelope & Tempo / BPM Estimation
    # Half-wave rectified spectral flux
    flux = np.maximum(0, mag[:, 1:] - mag[:, :-1])
    onset_env = np.sum(flux, axis=0)
    # Smooth onset envelope
    onset_env = np.convolve(onset_env, np.hanning(11), mode='same')
    onset_env -= np.mean(onset_env)
    onset_sr = sr / hop

    # Autocorrelation of onset envelope
    corr = np.correlate(onset_env, onset_env, mode='full')
    corr = corr[len(corr) // 2:]

    # Search for BPM between 45 and 180 BPM
    min_lag = int(onset_sr * (60.0 / 180.0))
    max_lag = int(onset_sr * (60.0 / 45.0))
    corr_search = corr[min_lag:max_lag]
    best_lag = min_lag + np.argmax(corr_search)
    detected_bpm = round(60.0 * onset_sr / best_lag, 1)

    # Check for half / double tempo harmonics
    half_bpm = round(detected_bpm / 2.0, 1)
    double_bpm = round(detected_bpm * 2.0, 1)

    # 6. Dynamic Energy Timeline (Structural Segmentation)
    rms_timeline = []
    step_sec = 2.0
    step_samples = int(step_sec * sr)
    for s_idx in range(0, len(mono) - step_samples, step_samples):
        chunk = mono[s_idx:s_idx + step_samples]
        chunk_rms = float(np.sqrt(np.mean(chunk ** 2)))
        rms_timeline.append({
            'time': round(s_idx / sr, 1),
            'rms_db': round(float(20 * np.log10(chunk_rms + 1e-9)), 1)
        })

    # Build Analysis Output Dictionary
    report = {
        'track_title': track_title,
        'filename': os.path.basename(file_path),
        'duration_seconds': round(duration, 2),
        'sample_rate': sr,
        'overall_rms_db': round(float(20 * np.log10(rms + 1e-9)), 2),
        'peak_level': round(peak, 3),
        'crest_factor': round(crest_factor, 2),
        'stereo_width_ratio': round(stereo_width, 3),
        'rhythm_tempo': {
            'primary_bpm': detected_bpm,
            'half_bpm': half_bpm,
            'double_bpm': double_bpm,
            'groove_type': 'Rubato / Floating Acoustic' if detected_bpm < 75 else 'Steady Pulse / Midtempo'
        },
        'tonality_harmony': {
            'detected_key': best_key,
            'confidence_correlation': round(best_corr, 3),
            'top_key_candidates': [{'key': k, 'corr': round(c, 3)} for k, c in sorted_keys],
            'global_pitch_distribution': {PITCH_NAMES[i]: round(float(global_chroma[i]), 4) for i in range(12)}
        },
        'spectral_timbre': {
            'mean_spectral_centroid_hz': round(mean_centroid, 1),
            'centroid_std_hz': round(std_centroid, 1),
            'mean_spectral_rolloff_85pct_hz': round(mean_rolloff, 1),
            'energy_band_distribution_pct': energy_bands,
            'tonal_balance': 'Warm, Mellow, Acoustic' if mean_centroid < 1800 else 'Bright, Crisp, Modern'
        },
        'chord_sequence_sample': chord_progression[:16],
        'energy_curve_sample': rms_timeline[::4]
    }

    return report

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    tracks = [
        ('/home/fahim/Storage/DesktopMoved/medwise/tune/analysis/2nF0Y4YSUtk.wav', 'Departures - Max LL'),
        ('/home/fahim/Storage/DesktopMoved/medwise/tune/analysis/-p2AW5gS6tU.wav', 'Passerby - Max LL')
    ]

    results = {}
    for p, title in tracks:
        print(f"\nAnalyzing: {title} ({p})...")
        res = analyze_track(p, title)
        results[title] = res
        print(f"-> Key: {res['tonality_harmony']['detected_key']} (corr: {res['tonality_harmony']['confidence_correlation']})")
        print(f"-> Tempo: {res['rhythm_tempo']['primary_bpm']} BPM (half: {res['rhythm_tempo']['half_bpm']} BPM)")
        print(f"-> Brightness (Centroid): {res['spectral_timbre']['mean_spectral_centroid_hz']} Hz ({res['spectral_timbre']['tonal_balance']})")
        print(f"-> Low-Mids Energy: {res['spectral_timbre']['energy_band_distribution_pct']['low_mids_250_1000Hz']:.1f}%")
        print(f"-> Stereo Width: {res['stereo_width_ratio']}")

    out_json = os.path.join(here, 'spectral_analysis_results.json')
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nAnalysis complete! Saved structured results to {out_json}")

if __name__ == '__main__':
    main()
