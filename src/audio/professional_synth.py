"""
Professional audio synthesis using proper ADSR envelopes and harmonic synthesis.
Much better than our basic sine waves.
"""
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ProfessionalSynthesizer:
    """
    High-quality audio synthesis with realistic instrument sounds.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def adsr_envelope(self, duration: float, attack: float = 0.01,
                     decay: float = 0.1, sustain: float = 0.7,
                     release: float = 0.2) -> np.ndarray:
        """
        Create ADSR (Attack, Decay, Sustain, Release) envelope.

        Args:
            duration: Total duration in seconds
            attack: Attack time in seconds
            decay: Decay time in seconds
            sustain: Sustain level (0-1)
            release: Release time in seconds

        Returns:
            Envelope array
        """
        samples = int(duration * self.sample_rate)
        envelope = np.zeros(samples)

        # Calculate sample counts for each phase
        attack_samples = int(attack * self.sample_rate)
        decay_samples = int(decay * self.sample_rate)
        release_samples = int(release * self.sample_rate)
        sustain_samples = samples - attack_samples - decay_samples - release_samples

        if sustain_samples < 0:
            sustain_samples = 0
            release_samples = samples - attack_samples - decay_samples

        current = 0

        # Attack phase (0 to 1)
        if attack_samples > 0:
            envelope[current:current+attack_samples] = np.linspace(0, 1, attack_samples)
            current += attack_samples

        # Decay phase (1 to sustain)
        if decay_samples > 0 and current < samples:
            end = min(current + decay_samples, samples)
            envelope[current:end] = np.linspace(1, sustain, end - current)
            current = end

        # Sustain phase (constant sustain level)
        if sustain_samples > 0 and current < samples:
            end = min(current + sustain_samples, samples)
            envelope[current:end] = sustain
            current = end

        # Release phase (sustain to 0)
        if release_samples > 0 and current < samples:
            envelope[current:] = np.linspace(sustain, 0, samples - current)

        return envelope

    def synth_piano(self, frequency: float, duration: float, velocity: float = 1.0) -> np.ndarray:
        """
        Synthesize realistic piano sound using additive synthesis.

        Args:
            frequency: Note frequency in Hz
            duration: Duration in seconds
            velocity: Note velocity (0-1)

        Returns:
            Audio array
        """
        t = np.linspace(0, duration, int(duration * self.sample_rate), False)

        # Piano has strong fundamental and specific harmonic structure
        harmonics = [
            (1.0, 1.0),      # Fundamental
            (2.0, 0.5),      # 2nd harmonic
            (3.0, 0.3),      # 3rd harmonic
            (4.0, 0.2),      # 4th harmonic
            (5.0, 0.15),     # 5th harmonic
            (6.0, 0.1),      # 6th harmonic
            (7.0, 0.05),     # 7th harmonic
        ]

        audio = np.zeros_like(t)
        for harmonic_ratio, amplitude in harmonics:
            audio += amplitude * np.sin(2 * np.pi * frequency * harmonic_ratio * t)

        # Piano envelope: fast attack, medium decay, no sustain, medium release
        envelope = self.adsr_envelope(duration, attack=0.002, decay=0.1,
                                     sustain=0.3, release=0.3)

        # Apply envelope and velocity
        audio = audio * envelope * velocity * 0.3

        return audio.astype(np.float32)

    def synth_bell(self, frequency: float, duration: float, velocity: float = 1.0) -> np.ndarray:
        """
        Synthesize bell/chime sound with inharmonic partials.

        Args:
            frequency: Base frequency in Hz
            duration: Duration in seconds
            velocity: Note velocity (0-1)

        Returns:
            Audio array
        """
        t = np.linspace(0, duration, int(duration * self.sample_rate), False)

        # Bell sounds have inharmonic partials (not integer multiples)
        partials = [
            (1.0, 1.0),      # Fundamental
            (2.76, 0.6),     # First overtone
            (5.40, 0.4),     # Second overtone
            (8.93, 0.3),     # Third overtone
            (13.34, 0.2),    # Fourth overtone
        ]

        audio = np.zeros_like(t)
        for partial_ratio, amplitude in partials:
            # Each partial decays at different rate
            decay = np.exp(-3 * partial_ratio * t / duration)
            audio += amplitude * np.sin(2 * np.pi * frequency * partial_ratio * t) * decay

        # Bell envelope: very fast attack, long decay
        envelope = self.adsr_envelope(duration, attack=0.001, decay=0.2,
                                     sustain=0.1, release=0.5)

        audio = audio * envelope * velocity * 0.4

        return audio.astype(np.float32)

    def synth_pad(self, frequency: float, duration: float, velocity: float = 1.0) -> np.ndarray:
        """
        Synthesize soft pad sound (smooth, atmospheric).

        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            velocity: Note velocity (0-1)

        Returns:
            Audio array
        """
        t = np.linspace(0, duration, int(duration * self.sample_rate), False)

        # Pad uses many harmonics with slow modulation
        audio = np.zeros_like(t)

        # Multiple detuned oscillators for richness
        for detune in [-0.02, 0, 0.02]:
            freq = frequency * (1 + detune)
            # Rich harmonic content
            for harmonic in range(1, 9):
                amplitude = 1.0 / harmonic  # Lower harmonics louder
                # Slow LFO modulation for movement
                lfo = 1 + 0.1 * np.sin(2 * np.pi * 0.5 * harmonic * t)
                audio += amplitude * np.sin(2 * np.pi * freq * harmonic * t) * lfo

        # Pad envelope: slow attack, long sustain, slow release
        envelope = self.adsr_envelope(duration, attack=0.3, decay=0.2,
                                     sustain=0.8, release=0.4)

        audio = audio * envelope * velocity * 0.15

        return audio.astype(np.float32)

    def synth_string(self, frequency: float, duration: float, velocity: float = 1.0) -> np.ndarray:
        """
        Synthesize string sound (violin-like).

        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            velocity: Note velocity (0-1)

        Returns:
            Audio array
        """
        t = np.linspace(0, duration, int(duration * self.sample_rate), False)

        # Strings have rich harmonic content with vibrato
        audio = np.zeros_like(t)

        # Vibrato (slight pitch modulation)
        vibrato_rate = 5.5  # Hz
        vibrato_depth = 0.008  # ~0.8% pitch variation
        vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)

        # Rich harmonics
        for harmonic in range(1, 12):
            amplitude = 1.0 / (harmonic ** 0.8)  # Gradual rolloff
            audio += amplitude * np.sin(2 * np.pi * frequency * harmonic * t * vibrato)

        # String envelope: medium attack, long sustain
        envelope = self.adsr_envelope(duration, attack=0.1, decay=0.15,
                                     sustain=0.7, release=0.25)

        audio = audio * envelope * velocity * 0.25

        return audio.astype(np.float32)

    def synth_percussion(self, duration: float, velocity: float = 1.0) -> np.ndarray:
        """
        Synthesize percussion sound (cymbal-like).

        Args:
            duration: Duration in seconds
            velocity: Note velocity (0-1)

        Returns:
            Audio array
        """
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)

        # Metallic sound with noise and high harmonics
        # Generate filtered noise
        noise = np.random.randn(samples) * 0.5

        # Add metallic partials
        for freq in [3000, 4500, 7000, 9000, 11000]:
            noise += 0.2 * np.sin(2 * np.pi * freq * t)

        # Fast decay envelope
        envelope = np.exp(-8 * t / duration)

        audio = noise * envelope * velocity * 0.3

        return audio.astype(np.float32)


def generate_professional_tone(frequency: float, duration: float,
                              instrument: str = "bell",
                              velocity: float = 1.0,
                              sample_rate: int = 44100) -> np.ndarray:
    """
    Generate professional-quality instrument sound.

    Args:
        frequency: Note frequency in Hz
        duration: Duration in seconds
        instrument: Instrument type (piano, bell, pad, string, percussion)
        velocity: Note velocity (0-1)
        sample_rate: Sample rate

    Returns:
        Audio array (float32)
    """
    synth = ProfessionalSynthesizer(sample_rate)

    if instrument == "piano":
        return synth.synth_piano(frequency, duration, velocity)
    elif instrument == "bell":
        return synth.synth_bell(frequency, duration, velocity)
    elif instrument == "pad" or instrument == "soft_pad":
        return synth.synth_pad(frequency, duration, velocity)
    elif instrument == "string" or instrument == "violin":
        return synth.synth_string(frequency, duration, velocity)
    elif instrument == "percussion":
        return synth.synth_percussion(duration, velocity)
    else:
        # Default to bell
        return synth.synth_bell(frequency, duration, velocity)

