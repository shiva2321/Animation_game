
import numpy as np

SAMPLE_RATE = 44100  # Hz

# --- Musical Scales ---
SCALES = {
    "pentatonic_c": [261.63, 293.66, 329.63, 392.00, 440.00], # C4, D4, E4, G4, A4
    "pentatonic_g": [392.00, 440.00, 493.88, 587.33, 659.25], # G4, A4, B4, D5, E5
    "japanese":     [261.63, 277.18, 392.00, 415.30, 523.25], # C4, C#4, G4, G#4, C5
    "minor_a":      [440.00, 493.88, 523.25, 587.33, 659.25, 698.46, 783.99] # A minor scale
}

def get_note_from_scale(energy: float, scale_name: str, mood: str) -> float:
    """Selects a note frequency from a scale based on energy."""
    scale = SCALES.get(scale_name, SCALES["pentatonic_c"])

    # Energy determines octave and note index
    octave = int(np.clip(energy / 30000, 0, 2))
    note_index = int(np.clip(energy / 10000, 0, len(scale) - 1))

    # Mood can influence note selection (e.g., 'Calm' avoids high notes)
    if mood == "Calm":
        octave = min(1, octave)
        note_index = min(len(scale) - 2, note_index)

    return scale[note_index] * (2**octave)

# --- ADSR Envelope ---
def adsr_envelope(duration_samples: int, attack_s, decay_s, sustain_level, release_s):
    """Generates an ADSR envelope as a NumPy array."""
    attack_samples = int(attack_s * SAMPLE_RATE)
    decay_samples = int(decay_s * SAMPLE_RATE)
    release_samples = int(release_s * SAMPLE_RATE)
    sustain_samples = duration_samples - attack_samples - decay_samples - release_samples

    if sustain_samples < 0: # Handle short notes
        sustain_samples = 0
        release_samples = duration_samples - attack_samples - decay_samples
        if release_samples < 0:
            decay_samples = duration_samples - attack_samples
            release_samples = 0

    attack = np.linspace(0, 1, attack_samples)
    decay = np.linspace(1, sustain_level, decay_samples)
    sustain = np.full(sustain_samples, sustain_level)
    release = np.linspace(sustain_level, 0, release_samples)

    return np.concatenate((attack, decay, sustain, release))

# --- Instrument Synthesis ---
def generate_tone(freq, duration_s, waveform_func, envelope, harmonics):
    """Generates a tone with specified waveform, envelope, and harmonics."""
    t = np.linspace(0, duration_s, int(duration_s * SAMPLE_RATE), endpoint=False)
    signal = np.zeros_like(t)

    for amp, harm_freq_mult in harmonics:
        signal += amp * waveform_func(2 * np.pi * freq * harm_freq_mult * t)

    return signal * envelope[:len(signal)]

def sine_wave(t):
    return np.sin(t)

def square_wave(t):
    return np.sign(np.sin(t))

INSTRUMENTS = {
    "piano": {
        "envelope": (0.01, 0.2, 0.7, 0.2),
        "harmonics": [(0.8, 1), (0.4, 2), (0.2, 3), (0.1, 4)]
    },
    "violin": {
        "envelope": (0.1, 0.3, 0.6, 0.3),
        "harmonics": [(0.7, 1), (0.5, 2), (0.3, 3), (0.2, 4), (0.1, 5)] # Richer harmonics
    },
    "bell": {
        "envelope": (0.005, 0.5, 0.1, 0.8),
        "harmonics": [(0.6, 1), (0.3, 2.7), (0.2, 5.4), (0.1, 8.1)] # Inharmonic
    },
    "soft_pad": {
        "envelope": (0.4, 0.4, 0.5, 0.6),
        "harmonics": [(1.0, 1), (0.5, 2)]
    }
}

def synthesize_instrument(instrument_name: str, freq: float, duration_s: float, volume: float) -> np.ndarray:
    """Synthesizes a note for a given instrument."""
    config = INSTRUMENTS.get(instrument_name, INSTRUMENTS["piano"])
    duration_samples = int(duration_s * SAMPLE_RATE)

    envelope = adsr_envelope(duration_samples, *config["envelope"])
    tone = generate_tone(freq, duration_s, sine_wave, envelope, config["harmonics"])

    # Add vibrato for violin
    if instrument_name == "violin":
        vibrato_rate = 5  # Hz
        vibrato_depth = 0.005 # percentage of freq
        t = np.linspace(0, duration_s, len(tone))
        freq_modulation = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        # This is a simplified approach; true FM synthesis is more complex
        tone *= freq_modulation

    return tone * volume

# --- Effects ---
def apply_reverb(signal: np.ndarray, amount: float) -> np.ndarray:
    """Applies a simple multi-tap delay reverb."""
    if amount == 0:
        return signal

    delays = [int(SAMPLE_RATE * d) for d in [0.02, 0.035, 0.05]]
    decays = [0.6 * amount, 0.4 * amount, 0.2 * amount]

    reverb_signal = np.zeros_like(signal)
    for delay, decay in zip(delays, decays):
        if len(signal) > delay:
            reverb_signal[delay:] += signal[:-delay] * decay

    return signal + reverb_signal

def apply_limiter(signal: np.ndarray, threshold_db: float) -> np.ndarray:
    """Applies a simple peak limiter."""
    threshold = 10**(threshold_db / 20.0)

    # Find peaks above threshold
    peaks = np.where(np.abs(signal) > threshold)[0]

    if len(peaks) > 0:
        # Simple soft knee reduction
        signal[peaks] = np.sign(signal[peaks]) * (threshold + (np.abs(signal[peaks]) - threshold) * 0.5)

    # Normalize to -0.1 dB to be safe
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * 0.98

    return signal
