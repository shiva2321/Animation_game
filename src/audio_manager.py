"""Audio engine optimized for real-time collision and bounce sounds"""

import numpy as np
import math
import time


class SimpleAudioSegment:
    """Simple audio without external dependencies"""

    def __init__(self, audio_data, sample_rate=44100, channels=1, sample_width=2):
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width

    def __len__(self):
        """Length in milliseconds"""
        if len(self.audio_data) == 0:
            return 0
        samples = len(self.audio_data) // self.sample_width
        return int((samples / self.sample_rate) * 1000)

    def export(self, path, format="wav"):
        """Export to WAV file"""
        import wave
        with wave.open(path, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(self.audio_data)


class AudioGenerator:
    """Fast tone generation for real-time audio"""

    SAMPLE_RATE = 44100

    # Pentatonic scale for pleasant sounds
    PENTATONIC_NOTES = {
        'C4': 261.63,
        'D4': 293.66,
        'E4': 329.63,
        'G4': 392.00,
        'A4': 440.00,
        'C5': 523.25,
        'D5': 587.33,
        'E5': 659.25,
        'G5': 783.99,
        'A5': 880.00,
        'C6': 1046.50,
    }

    @staticmethod
    def generate_collision_tone(frequency, duration_ms=150):
        """Generate a quick collision tone"""
        duration_s = duration_ms / 1000.0
        num_samples = int(AudioGenerator.SAMPLE_RATE * duration_s)
        t = np.linspace(0, duration_s, num_samples, False)

        # Main tone with harmonics
        wave = np.sin(2 * np.pi * frequency * t) * 0.7
        wave += np.sin(2 * np.pi * frequency * 2 * t) * 0.2  # Octave

        # ADSR envelope
        attack = int(num_samples * 0.05)
        release = int(num_samples * 0.4)
        sustain_end = num_samples - release

        envelope = np.ones(num_samples)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[sustain_end:] = np.linspace(1, 0, release)

        wave = wave * envelope

        # Normalize and convert
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val * 0.95

        wave_int = (wave * 32767).astype(np.int16)
        return SimpleAudioSegment(wave_int.tobytes(), AudioGenerator.SAMPLE_RATE, 1, 2)

    @staticmethod
    def generate_bounce_tone(frequency, duration_ms=100):
        """Generate a bounce percussion tone"""
        duration_s = duration_ms / 1000.0
        num_samples = int(AudioGenerator.SAMPLE_RATE * duration_s)
        t = np.linspace(0, duration_s, num_samples, False)

        # Short percussive sound
        wave = np.sin(2 * np.pi * frequency * t) * 0.6

        # Very quick envelope
        release = int(num_samples * 0.8)
        envelope = np.ones(num_samples)
        envelope[release:] = np.linspace(1, 0, num_samples - release)

        wave = wave * envelope

        # Normalize
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val * 0.9

        wave_int = (wave * 32767).astype(np.int16)
        return SimpleAudioSegment(wave_int.tobytes(), AudioGenerator.SAMPLE_RATE, 1, 2)


class AudioManager:
    """Manages real-time audio for collisions and bounces"""

    def __init__(self):
        self.instrument = "piano"
        self.master_volume = 0.6
        self.collision_volume = 0.8
        self.bounce_volume = 0.4
        self.mute_all = False

        self.note_index = 0
        self.collision_sounds = {}  # Cache for quick access
        self.bounce_sounds = {}

    def _get_next_note(self):
        """Cycle through pentatonic scale"""
        notes = list(AudioGenerator.PENTATONIC_NOTES.values())
        note = notes[self.note_index % len(notes)]
        self.note_index += 1
        return note

    def generate_collision_sound(self):
        """Generate a collision tone"""
        if self.mute_all:
            return None

        frequency = self._get_next_note()
        duration = 150

        sound = AudioGenerator.generate_collision_tone(frequency, duration)
        return sound

    def generate_bounce_sound(self):
        """Generate a bounce tone"""
        if self.mute_all:
            return None

        # Use lower frequency for bounce (more bass)
        notes = list(AudioGenerator.PENTATONIC_NOTES.values())
        frequency = notes[(self.note_index - 1) % len(notes)] / 2  # One octave lower
        duration = 100

        sound = AudioGenerator.generate_bounce_tone(frequency, duration)
        return sound

