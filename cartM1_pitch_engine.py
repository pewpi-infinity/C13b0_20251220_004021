#!/usr/bin/env python3

# Infinity OS — Advanced Grok/Gemini Hybrid Pitch Engine
# Cart M1 — Pure Intelligence Layer 1

import numpy as np
import sounddevice as sd
import argparse
from scipy.io import wavfile
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import sys

# -----------------------------------
# Utility: Next power of 2 for FFT pad
# -----------------------------------
def next_power_of_2(n):
    return 1 << (int(np.log2(n - 1)) + 1) if n > 1 else 1

# -----------------------------------
# FFT Pitch Detection
# -----------------------------------
def get_freq_fft(data, sr):
    """
    Detect pitch using FFT with Blackman window, zero-padding, and
    logarithmic parabolic interpolation.
    """
    window = np.blackman(len(data))
    data = data * window
    N = len(data)
    pad = next_power_of_2(N * 4)
    fft = np.fft.rfft(data, n=pad)
    mag = np.abs(fft)
    freqs = np.fft.rfftfreq(pad, 1 / sr)

    peak = np.argmax(mag)
    if 0 < peak < len(mag) - 1:
        y0, y1, y2 = np.log(mag[peak - 1:peak + 2] + 1e-10)
        offset = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
        freq = freqs[peak] + offset * (freqs[1] - freqs[0])
    else:
        freq = freqs[peak]
    return freq

# -----------------------------------
# Autocorrelation Detection
# -----------------------------------
def get_freq_autocorr(data, sr):
    data = data * np.hanning(len(data))
    data -= np.mean(data)
    corr = np.correlate(data, data, mode='full')[len(data) - 1:]
    corr = corr / (np.max(corr) + 1e-10)

    valleys, _ = find_peaks(-corr)
    start = valleys[0] if len(valleys) > 0 else 5

    peak_idx = np.argmax(corr[start:]) + start
    if peak_idx <= start:
        return 0.0

    if start < peak_idx < len(corr) - 1:
        y0, y1, y2 = corr[peak_idx - 1:peak_idx + 2]
        offset = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
        peak_idx += offset

    return sr / peak_idx

# -----------------------------------
# HPS (Harmonic Product Spectrum)
# -----------------------------------
def get_freq_hps(data, sr, harmonics=5):
    data = data * np.hanning(len(data))
    N = len(data)
    pad = next_power_of_2(N * 4)
    spec = np.abs(np.fft.rfft(data, n=pad))
    hps = np.copy(spec)

    for h in range(2, harmonics + 1):
        decimated = spec[::h]
        hps[:len(decimated)] *= decimated

    peak = np.argmax(hps)
    bin_size = sr / pad

    if 0 < peak < len(hps) - 1:
        y0, y1, y2 = np.log(hps[peak - 1:peak + 2] + 1e-10)
        offset = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
        freq = (peak + offset) * bin_size
    else:
        freq = peak * bin_size
    return freq

# -----------------------------------
# Frequency → Note
# -----------------------------------
def freq_to_note(freq):
    if freq < 20:
        return "N/A"
    a4 = 440.0
    midi_note = 69 + 12 * np.log2(freq / a4)
    note_num = round(midi_note)

    note_names = [
        "C", "C#", "D", "D#", "E", "F",
        "F#", "G", "G#", "A", "A#", "B"
    ]

    note_name = note_names[note_num % 12]
    octave = note_num // 12 - 1

    exact_freq = a4 * (2 ** ((note_num - 69) / 12))
    cents = round(1200 * np.log2(freq / exact_freq))

    return f"{note_name}{octave} ({cents:+d} cents)"

# -----------------------------------
# Main Analyzer
# -----------------------------------
def detect_pitch(args):
    try:
        print("Listening...")
        audio = sd.rec(
            int(args.duration * args.samplerate),
            samplerate=args.samplerate,
            channels=1,
            dtype='float32'
        )
        sd.wait()
        data = audio.flatten()

        amp = np.max(np.abs(data))
        if amp < args.threshold:
            return "Silence detected (amplitude too low)"

        if args.save_audio:
            wavfile.write(args.save_audio, args.samplerate, audio)
            print(f"Audio saved to {args.save_audio}")

        if args.method == 'fft':
            freq = get_freq_fft(data, args.samplerate)
        elif args.method == 'autocorr':
            freq = get_freq_autocorr(data, args.samplerate)
        else:
            freq = get_freq_hps(data, args.samplerate)

        note = freq_to_note(freq)

        if args.plot:
            if args.method == 'autocorr':
                corr = np.correlate(data, data, mode='full')[len(data) - 1:]
                plt.plot(corr)
                plt.title("Autocorrelation")
                plt.xlabel("Lag")
                plt.ylabel("Correlation")
                plt.show()
            else:
                pad = next_power_of_2(len(data) * 4)
                spec = np.abs(np.fft.rfft(data * np.hanning(len(data)), n=pad))
                freqs = np.fft.rfftfreq(pad, 1 / args.samplerate)
                plt.plot(freqs, 20 * np.log10(spec + 1e-10))
                plt.title("Spectrum")
                plt.xlabel("Frequency (Hz)")
                plt.ylabel("Magnitude (dB)")
                plt.xlim(0, 2000)
                plt.show()

        return f"Detected frequency: {freq:.2f} Hz — Note: {note}"

    except Exception as e:
        return f"Error during detection: {str(e)}"

# -----------------------------------
# CLI
# -----------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Infinity OS | Advanced Pitch Detection Engine"
    )

    parser.add_argument('--duration', type=float, default=0.5)
    parser.add_argument('--samplerate', type=int, default=44100)
    parser.add.add_argument('--method', choices=['fft','autocorr','hps'], default='hps')
    parser.add_argument('--harmonics', type=int, default=5)
    parser.add_argument('--continuous', action='store_true')
    parser.add_argument('--device', type=int, default=None)
    parser.add_argument('--list-devices', action='store_true')
    parser.add_argument('--threshold', type=float, default=0.01)
    parser.add_argument('--plot', action='store_true')
    parser.add_argument('--save-audio', type=str, default=None)

    args = parser.parse_args()

    if args.list_devices:
        print("Available devices:")
        for i, dev in enumerate(sd.query_devices()):
            print(f"{i}: {dev['name']} (inputs: {dev['max_input_channels']})")
        sys.exit(0)

    if args.device is not None:
        sd.default.device = args.device

    if args.continuous:
        print("Continuous mode. Ctrl+C to stop.")
        while True:
            try:
                print(detect_pitch(args))
            except KeyboardInterrupt:
                print("\nStopped.")
                break
    else:
        print(detect_pitch(args))
