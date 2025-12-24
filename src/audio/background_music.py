"""
Professional background music generator using proper music theory and synthesis.
Creates ambient, cinematic background music with chord progressions.
"""
import numpy as np
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class BackgroundMusicGenerator:
    """Generates professional ambient background music."""

    # Musical scales (note intervals from root)
    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'pentatonic_major': [0, 2, 4, 7, 9],
        'pentatonic_minor': [0, 3, 5, 7, 10],
        'dorian': [0, 2, 3, 5, 7, 9, 10],
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],
    }

    # Chord progressions (scale degrees)
    PROGRESSIONS = {
        'calm': [
            (0, 4, 5, 3),  # I-V-vi-IV (very common, peaceful)
            (0, 5, 3, 4),  # I-vi-IV-V (also very common)
        ],
        'meditative': [
            (0, 3, 0, 3),  # I-IV-I-IV (simple, zen)
            (0, 4, 0, 4),  # I-V-I-V (drone-like)
        ],
        'uplifting': [
            (0, 4, 5, 5),  # I-V-vi-vi (upward feel)
            (3, 4, 0, 0),  # IV-V-I-I (resolution)
        ]
    }

    def __init__(self, duration: float, sample_rate: int = 44100):
        self.duration = duration
        self.sample_rate = sample_rate
        self.num_samples = int(duration * sample_rate)

    def freq_from_midi(self, midi_note: int) -> float:
        """Convert MIDI note number to frequency."""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    def generate(self, style: str = "calm", key: str = "C",
                 scale: str = "major") -> np.ndarray:
        """
        Generate professional ambient music.

        Args:
            style: Music style (calm, meditative, uplifting)
            key: Musical key (C, D, E, F, G, A, B)
            scale: Scale type

        Returns:
            Audio array (mono, float32)
        """
        logger.info(f"Generating {style} music in {key} {scale}...")

        if style == "calm":
            return self._generate_calm(key, scale)
        elif style == "meditative":
            return self._generate_meditative(key, scale)
        elif style == "uplifting":
            return self._generate_uplifting(key, scale)
        else:
            return self._generate_calm(key, scale)

    def _generate_calm(self, key: str = "C", scale_type: str = "major") -> np.ndarray:
        """Generate calm, peaceful ambient music."""
        # Get root note
        root_midi = self._get_root_midi(key)
        scale = self.SCALES.get(scale_type, self.SCALES['major'])

        # Create timeline
        t = np.linspace(0, self.duration, self.num_samples, False)
        audio = np.zeros(self.num_samples, dtype=np.float32)

        # Chord progression (I-V-vi-IV)
        chord_duration = self.duration / 4
        chords = [
            [root_midi + 12, root_midi + scale[2] + 12, root_midi + scale[4] + 12],  # I (C-E-G)
            [root_midi + scale[4] + 12, root_midi + scale[6] + 12, root_midi + scale[1] + 24],  # V (G-B-D)
            [root_midi + scale[5] + 12, root_midi + scale[0] + 12, root_midi + scale[2] + 12],  # vi (A-C-E)
            [root_midi + scale[3] + 12, root_midi + scale[0] + 12, root_midi + scale[2] + 12],  # IV (F-A-C)
        ]

        # Generate each chord
        for idx, chord_notes in enumerate(chords):
            start_sample = int(idx * chord_duration * self.sample_rate)
            end_sample = int((idx + 1) * chord_duration * self.sample_rate)
            chord_t = t[start_sample:end_sample]

            # Synthesize chord with pad-like sound
            chord_audio = self._synth_pad_chord(chord_notes, chord_t)

            # Crossfade between chords
            if idx > 0:
                fade_samples = int(0.5 * self.sample_rate)
                fade_in = np.linspace(0, 1, fade_samples)
                chord_audio[:fade_samples] *= fade_in

            if idx < len(chords) - 1:
                fade_samples = int(0.5 * self.sample_rate)
                fade_out = np.linspace(1, 0, fade_samples)
                chord_audio[-fade_samples:] *= fade_out

            audio[start_sample:end_sample] += chord_audio

        # Add subtle bass drone
        bass_freq = self.freq_from_midi(root_midi - 12)  # One octave below
        bass = 0.15 * np.sin(2 * np.pi * bass_freq * t)
        audio += bass

        # Add shimmer (high octave)
        shimmer_notes = [root_midi + 24, root_midi + scale[2] + 24]
        for note in shimmer_notes:
            freq = self.freq_from_midi(note)
            shimmer = 0.03 * np.sin(2 * np.pi * freq * t)
            # Slow modulation
            mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
            audio += shimmer * mod

        # Normalize
        audio = self._normalize(audio)

        return audio.astype(np.float32)

    def _generate_meditative(self, key: str = "C", scale_type: str = "minor") -> np.ndarray:
        """Generate meditative, zen-like music."""
        root_midi = self._get_root_midi(key)

        t = np.linspace(0, self.duration, self.num_samples, False)
        audio = np.zeros(self.num_samples, dtype=np.float32)

        # Deep drone
        drone_freq = self.freq_from_midi(root_midi - 24)  # Two octaves below
        audio += 0.25 * np.sin(2 * np.pi * drone_freq * t)

        # Singing bowl-like tones (specific harmonic ratios)
        bowl_freqs = [
            self.freq_from_midi(root_midi) * 1.0,
            self.freq_from_midi(root_midi) * 1.5,
            self.freq_from_midi(root_midi) * 2.0,
            self.freq_from_midi(root_midi) * 3.0,
        ]

        for i, freq in enumerate(bowl_freqs):
            # Slow decay
            decay = np.exp(-0.3 * t / self.duration)
            # Slight modulation
            mod = 1 + 0.05 * np.sin(2 * np.pi * 0.1 * (i + 1) * t)
            audio += 0.08 * np.sin(2 * np.pi * freq * t) * decay * mod

        audio = self._normalize(audio)
        return audio.astype(np.float32)

    def _generate_uplifting(self, key: str = "C", scale_type: str = "major") -> np.ndarray:
        """Generate uplifting, positive music."""
        root_midi = self._get_root_midi(key)
        scale = self.SCALES['major']

        t = np.linspace(0, self.duration, self.num_samples, False)
        audio = np.zeros(self.num_samples, dtype=np.float32)

        # Major chord (I)
        chord_notes = [
            root_midi,
            root_midi + scale[2],  # Major third
            root_midi + scale[4],  # Perfect fifth
        ]

        # Arpeggiated chord for movement
        arp_rate = 0.5  # Hz
        note_duration = 0.5  # seconds

        for i, note_midi in enumerate(chord_notes * 4):  # Repeat pattern
            freq = self.freq_from_midi(note_midi + 12)
            # Phase offset for each note
            phase = i * np.pi / 3
            mod = 0.5 + 0.5 * np.sin(2 * np.pi * arp_rate * t + phase)
            audio += 0.06 * np.sin(2 * np.pi * freq * t) * mod

        # Bass
        bass_freq = self.freq_from_midi(root_midi - 12)
        audio += 0.2 * np.sin(2 * np.pi * bass_freq * t)

        audio = self._normalize(audio)
        return audio.astype(np.float32)

    def _synth_pad_chord(self, midi_notes: List[int], t: np.ndarray) -> np.ndarray:
        """
        Synthesize a pad-like chord sound.

        Args:
            midi_notes: List of MIDI note numbers
            t: Time array

        Returns:
            Audio array
        """
        audio = np.zeros_like(t, dtype=np.float32)

        for note in midi_notes:
            freq = self.freq_from_midi(note)

            # Multiple detuned oscillators per note
            for detune in [-0.01, 0, 0.01]:
                f = freq * (1 + detune)

                # Rich harmonics
                for harmonic in range(1, 6):
                    amplitude = 1.0 / harmonic
                    # Slow modulation
                    mod = 1 + 0.1 * np.sin(2 * np.pi * 0.2 * harmonic * t)
                    audio += amplitude * np.sin(2 * np.pi * f * harmonic * t) * mod

        # Normalize chord
        audio = audio / (len(midi_notes) * 3 * 5)  # Divide by oscillator count

        return audio * 0.15

    def _get_root_midi(self, key: str) -> int:
        """Get MIDI note number for key root."""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        try:
            offset = notes.index(key.upper())
        except ValueError:
            offset = 0  # Default to C

        return 48 + offset  # C3

    def _normalize(self, audio: np.ndarray, target: float = 0.9) -> np.ndarray:
        """Normalize audio to target level."""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val * target
        return audio

