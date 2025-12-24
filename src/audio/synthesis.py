"""
Audio synthesis using professional synthesis library.
This module now uses high-quality synthesis with proper ADSR and harmonics.
"""
import numpy as np
from typing import Tuple, List
from src.audio.professional_synth import generate_professional_tone, ProfessionalSynthesizer


# Musical scales (note frequencies in Hz for C4 octave)
SCALES = {
    "pentatonic_c": [261.63, 293.66, 329.63, 392.00, 440.00],  # C D E G A
    "pentatonic_g": [392.00, 440.00, 493.88, 587.33, 659.25],  # G A B D E
    "japanese": [261.63, 277.18, 329.63, 392.00, 415.30],      # C Db E G Ab
    "minor_a": [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00]  # A minor scale
}

# Legacy ADSR class for compatibility
class ADSREnvelope:
    """ADSR envelope - now uses professional synthesizer internally."""

    def __init__(self, attack: float = 0.01, decay: float = 0.1,
                 sustain: float = 0.7, release: float = 0.2):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.synth = ProfessionalSynthesizer()

    def generate(self, duration: float, sample_rate: int = 44100) -> np.ndarray:
        """Generate ADSR envelope."""
        return self.synth.adsr_envelope(duration, self.attack, self.decay,
                                       self.sustain, self.release)

        # Ensure non-negative
        sustain_samples = max(0, sustain_samples)

        idx = 0

        # Attack
        if attack_samples > 0:
            envelope[idx:idx+attack_samples] = np.linspace(0, 1, attack_samples)
            idx += attack_samples

        # Decay
        if decay_samples > 0 and idx < n_samples:
            end_idx = min(idx + decay_samples, n_samples)
            envelope[idx:end_idx] = np.linspace(1, self.sustain, end_idx - idx)
            idx = end_idx

        # Sustain
        if sustain_samples > 0 and idx < n_samples:
            end_idx = min(idx + sustain_samples, n_samples)
            envelope[idx:end_idx] = self.sustain
            idx = end_idx

        # Release
        if idx < n_samples:
            envelope[idx:] = np.linspace(self.sustain, 0, n_samples - idx)

        return envelope


class Synthesizer:
    """Audio synthesizer with multiple waveform types and instruments."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

        # Instrument presets
        self.instruments = {
            "piano": {
                "waveform": "mixed",
                "harmonics": [1.0, 0.5, 0.25, 0.125],
                "envelope": ADSREnvelope(0.01, 0.2, 0.5, 0.3)
            },
            "violin": {
                "waveform": "sawtooth",
                "harmonics": [1.0, 0.7, 0.5, 0.3, 0.2],
                "envelope": ADSREnvelope(0.05, 0.1, 0.8, 0.2)
            },
            "bell": {
                "waveform": "sine",
                "harmonics": [1.0, 0.6, 0.4, 0.3, 0.2, 0.1],
                "envelope": ADSREnvelope(0.001, 0.3, 0.3, 0.5)
            },
            "soft_pad": {
                "waveform": "sine",
                "harmonics": [1.0, 0.3, 0.2],
                "envelope": ADSREnvelope(0.1, 0.2, 0.7, 0.5)
            }
        }

    def generate_note(
        self,
        frequency: float,
        duration: float,
        instrument: str = "piano",
        amplitude: float = 0.5
    ) -> np.ndarray:
        """
        Generate a musical note.

        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            instrument: Instrument preset name
            amplitude: Amplitude [0, 1]

        Returns:
            NumPy array of audio samples
        """
        # Get instrument settings
        if instrument not in self.instruments:
            instrument = "piano"

        settings = self.instruments[instrument]

        # Generate waveform with harmonics
        audio = self._generate_waveform(
            frequency,
            duration,
            settings["waveform"],
            settings["harmonics"]
        )

        # Apply envelope
        envelope = settings["envelope"].generate(duration, self.sample_rate)
        audio = audio * envelope

        # Apply amplitude
        audio = audio * amplitude

        return audio

    def _generate_waveform(
        self,
        frequency: float,
        duration: float,
        waveform: str,
        harmonics: List[float]
    ) -> np.ndarray:
        """Generate waveform with harmonics."""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        audio = np.zeros(n_samples)

        # Add harmonics
        for i, amplitude in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)

            if waveform == "sine":
                wave = np.sin(2 * np.pi * harmonic_freq * t)
            elif waveform == "square":
                wave = np.sign(np.sin(2 * np.pi * harmonic_freq * t))
            elif waveform == "sawtooth":
                wave = 2 * (t * harmonic_freq % 1) - 1
            elif waveform == "triangle":
                wave = 2 * np.abs(2 * (t * harmonic_freq % 1) - 1) - 1
            else:  # "mixed"
                wave = (np.sin(2 * np.pi * harmonic_freq * t) +
                       0.3 * np.sign(np.sin(2 * np.pi * harmonic_freq * t)))

            audio += wave * amplitude

        # Normalize
        if len(harmonics) > 0:
            total_amplitude = sum(harmonics)
            if total_amplitude > 0:
                audio = audio / total_amplitude

        return audio

    def frequency_from_energy(
        self,
        energy: float,
        scale: str = "pentatonic_c",
        base_octave: int = 4,
        energy_range: Tuple[float, float] = (0, 1000)
    ) -> float:
        """
        Map energy to a frequency in the given scale.

        Args:
            energy: Collision energy
            scale: Musical scale name
            base_octave: Base octave (C4 = 4)
            energy_range: Min/max energy for mapping

        Returns:
            Frequency in Hz
        """
        # Get scale frequencies
        scale_freqs = SCALES.get(scale, SCALES["pentatonic_c"])

        # Normalize energy to [0, 1]
        norm_energy = (energy - energy_range[0]) / (energy_range[1] - energy_range[0])
        norm_energy = max(0, min(1, norm_energy))

        # Map to octave range (e.g., -1 to +1 octaves)
        octave_shift = norm_energy * 2 - 1

        # Select note from scale based on energy
        note_idx = int(norm_energy * len(scale_freqs)) % len(scale_freqs)
        base_freq = scale_freqs[note_idx]

        # Apply octave shift
        frequency = base_freq * (2 ** octave_shift)

        # Clamp to reasonable range
        frequency = max(100, min(2000, frequency))

        return frequency

    def duration_from_energy(
        self,
        energy: float,
        min_duration: float = 0.1,
        max_duration: float = 0.8,
        energy_range: Tuple[float, float] = (0, 1000)
    ) -> float:
        """
        Map energy to note duration.

        Args:
            energy: Event energy
            min_duration: Minimum duration
            max_duration: Maximum duration
            energy_range: Min/max energy for mapping

        Returns:
            Duration in seconds
        """
        norm_energy = (energy - energy_range[0]) / (energy_range[1] - energy_range[0])
        norm_energy = max(0, min(1, norm_energy))

        duration = min_duration + norm_energy * (max_duration - min_duration)
        return duration


def apply_reverb(
    audio: np.ndarray,
    amount: float = 0.3,
    decay: float = 0.5,
    sample_rate: int = 44100
) -> np.ndarray:
    """
    Apply simple reverb effect (multi-tap delay).

    Args:
        audio: Input audio
        amount: Reverb amount [0, 1]
        decay: Decay factor [0, 1]
        sample_rate: Sample rate

    Returns:
        Audio with reverb
    """
    if amount <= 0:
        return audio

    # Multi-tap delays (in seconds)
    delays = [0.029, 0.037, 0.041, 0.043, 0.047, 0.053]

    output = audio.copy()

    for i, delay_time in enumerate(delays):
        delay_samples = int(delay_time * sample_rate)
        if delay_samples >= len(audio):
            continue

        # Create delayed signal with decay
        decay_factor = decay ** (i + 1)
        delayed = np.zeros_like(audio)
        delayed[delay_samples:] = audio[:-delay_samples] * decay_factor * amount

        output += delayed

    # Normalize
    max_val = np.abs(output).max()
    if max_val > 0:
        output = output / max_val * 0.95

    return output


def apply_limiter(
    audio: np.ndarray,
    threshold: float = 0.95
) -> np.ndarray:
    """
    Apply peak limiter to prevent clipping.

    Args:
        audio: Input audio
        threshold: Threshold [0, 1]

    Returns:
        Limited audio
    """
    # Soft clipping
    audio = np.tanh(audio / threshold) * threshold
    return audio

