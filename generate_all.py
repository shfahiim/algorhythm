"""Batch generation runner for all 14 procedural tunes.
Renders all tracks (tune_00 through tune_13), exporting 48kHz WAV and 320k MP3 files.
"""

import os
import sys
import time
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TUNES_DIR = os.path.join(HERE, 'tunes')

# List of all 14 procedural tunes in chronological order
TRACKS = [
    ('tune_00_motion_theme.py', 'Motion Theme (Original 120s Film Score)'),
    ('tune_01_sunlight_drift.py', 'Sunlight Drift (Uplifting Melodic House)'),
    ('tune_02_golden_horizon.py', 'Golden Horizon (Vibrant Nu-Disco)'),
    ('tune_03_neon_kinetic.py', 'Neon Kinetic (French Electro-House)'),
    ('tune_04_morning_island.py', 'Morning Island (Tropical Chill-House)'),
    ('tune_05_retro_highway.py', 'Retro Highway (Outrun / Synthwave)'),
    ('tune_06_pixel_rush.py', 'Pixel Rush (Chiptune Future-Pop)'),
    ('tune_07_solar_spark.py', 'Solar Spark (Nu-Funk & Slap Bass)'),
    ('tune_08_quantum_leap.py', 'Quantum Leap (Electro Swing & Shuffle)'),
    ('tune_09_skyline_sprint.py', 'Skyline Sprint (Euphoric Trance Anthem)'),
    ('tune_10_coffeehouse_bloom.py', 'Coffeehouse Bloom (Organic Indie Folk-Dance)'),
    ('tune_11_cyber_arcade.py', 'Cyber Arcade (Tokyo City Pop / Funk)'),
    ('tune_12_daybreak_anthem.py', 'Daybreak Anthem (Cinematic Orchestral-Dance)'),
    ('tune_13_departures_passerby_homage.py', 'The Long Journey (Max LL Cinematic Homage)'),
]

def main():
    start_total = time.time()
    print("=" * 70)
    print(f"🎵 ALGORHYTHM: Synthesizing {len(TRACKS)} Procedural Audio Tracks...")
    print("   100% Mathematical DSP via NumPy & SciPy | Zero DAWs | Zero Samples")
    print("=" * 70)

    for idx, (filename, label) in enumerate(TRACKS):
        script_path = os.path.join(TUNES_DIR, filename)
        t0 = time.time()
        print(f"\n[{idx:02d}/{len(TRACKS)-1:02d}] Synthesizing {label} ({filename})...")
        
        proc = subprocess.run([sys.executable, script_path], cwd=TUNES_DIR, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"❌ Error rendering {filename}:")
            print(proc.stderr)
        else:
            for line in proc.stdout.strip().split('\n'):
                if 'Generated' in line or 'peak' in line or 'Peak' in line:
                    print(f"   ✓ {line}")
            dt = time.time() - t0
            print(f"   ⏱ Completed in {dt:.2f}s")

    total_time = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"🎉 Complete! All {len(TRACKS)} tracks synthesized in {total_time:.2f}s!")
    print("   Files saved in audio/wav/ and audio/mp3/")
    print("=" * 70)

if __name__ == '__main__':
    main()
