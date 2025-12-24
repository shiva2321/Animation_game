"""Enhanced audio system with soothing, realistic sounds"""

import numpy as np
import math
import time


class SoundSynthesizer:
    """Synthesize realistic soothing sounds"""

    SAMPLE_RATE = 44100

    @staticmethod
    def generate_singing_bowl(frequency=432, duration_ms=1200):
        """Generate very soothing singing bowl tone with smooth fade"""
        duration_s = duration_ms / 1000.0
        num_samples = int(SoundSynthesizer.SAMPLE_RATE * duration_s)
        t = np.linspace(0, duration_s, num_samples, False)

        # Rich harmonics with detuning for warmth
        fundamental = np.sin(2 * np.pi * frequency * t)
        harmonic2 = 0.4 * np.sin(2 * np.pi * frequency * 1.48 * t)
        harmonic3 = 0.25 * np.sin(2 * np.pi * frequency * 2.05 * t)
        harmonic4 = 0.15 * np.sin(2 * np.pi * frequency * 3.18 * t)

        wave = fundamental + harmonic2 + harmonic3 + harmonic4

        # Very smooth envelope with long sustain
        attack = int(num_samples * 0.08)
        decay = int(num_samples * 0.10)
        sustain_end = int(num_samples * 0.70)
        release = num_samples - sustain_end

        envelope = np.ones(num_samples)
        # Smooth attack
        envelope[:attack] = np.power(np.linspace(0, 1, attack), 2)
        # Smooth decay to sustain
        envelope[attack:sustain_end] = np.linspace(1, 0.6, sustain_end - attack)
        # Smooth release (fade out)
        envelope[sustain_end:] = np.power(np.linspace(1, 0, release), 2)

        wave = wave * envelope

        # Normalize gently
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val * 0.5

        return (wave * 32767).astype(np.int16).tobytes()

    @staticmethod
    def generate_raindrop(frequency=500, duration_ms=200):
        """Generate gentle raindrop sound with smooth fade"""
        duration_s = duration_ms / 1000.0
        num_samples = int(SoundSynthesizer.SAMPLE_RATE * duration_s)
        t = np.linspace(0, duration_s, num_samples, False)

        # Gentle falling pitch
        freq_sweep = frequency * np.exp(-4 * t / duration_s)
        phase = 2 * np.pi * np.cumsum(freq_sweep) / SoundSynthesizer.SAMPLE_RATE
        wave = np.sin(phase)

        # Very smooth envelope
        envelope = np.exp(-5 * t / duration_s)
        wave = wave * envelope

        # Minimal noise
        noise = np.random.normal(0, 0.08, num_samples)
        wave = 0.85 * wave + 0.15 * noise

        # Normalize
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val * 0.45

        return (wave * 32767).astype(np.int16).tobytes()

    @staticmethod
    def generate_violin_note(frequency=440, duration_ms=1000):
        """Generate smooth, bowed violin-like tone with fade"""
        duration_s = duration_ms / 1000.0
        num_samples = int(SoundSynthesizer.SAMPLE_RATE * duration_s)
        t = np.linspace(0, duration_s, num_samples, False)

        # Warm harmonics
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.35 * np.sin(2 * np.pi * frequency * 2 * t)
        wave += 0.2 * np.sin(2 * np.pi * frequency * 3 * t)
        wave += 0.1 * np.sin(2 * np.pi * frequency * 4 * t)

        # Smooth vibrato
        vibrato_freq = 4.5
        vibrato_depth = 0.04
        vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)
        wave = wave * vibrato

        # Very smooth envelope
        attack = int(num_samples * 0.20)
        sustain_end = int(num_samples * 0.70)
        release = num_samples - sustain_end

        envelope = np.ones(num_samples)
        envelope[:attack] = np.power(np.linspace(0, 1, attack), 2)
        envelope[sustain_end:] = np.power(np.linspace(1, 0, release), 2.5)

        wave = wave * envelope

        # Normalize
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val * 0.5

        return (wave * 32767).astype(np.int16).tobytes()

    @staticmethod
    def generate_ambient_pad(frequency=110, duration_ms=4000):
        """Generate very soothing ambient pad with ultra-smooth fade"""
        duration_s = duration_ms / 1000.0
        num_samples = int(SoundSynthesizer.SAMPLE_RATE * duration_s)
        t = np.linspace(0, duration_s, num_samples, False)

        # Multiple detuned sine waves for lush pad
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.5 * np.sin(2 * np.pi * (frequency * 0.995) * t)
        wave += 0.5 * np.sin(2 * np.pi * (frequency * 1.005) * t)
        wave += 0.35 * np.sin(2 * np.pi * frequency * 2 * t)

        # Very slow LFO for movement
        lfo_freq = 0.3
        lfo = 1 + 0.12 * np.sin(2 * np.pi * lfo_freq * t)
        wave = wave * lfo

        # Ultra-smooth fade in and out
        fade_in = int(num_samples * 0.4)
        fade_out = int(num_samples * 0.4)

        envelope = np.ones(num_samples)
        envelope[:fade_in] = np.power(np.linspace(0, 1, fade_in), 3)
        envelope[-fade_out:] = np.power(np.linspace(1, 0, fade_out), 3)

        wave = wave * envelope

        # Normalize
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val * 0.35

        return (wave * 32767).astype(np.int16).tobytes()

    @staticmethod
    def generate_wind_chime(frequency=880, duration_ms=600):
        """Generate bright, resonant wind chime with fade"""
        duration_s = duration_ms / 1000.0
        num_samples = int(SoundSynthesizer.SAMPLE_RATE * duration_s)
        t = np.linspace(0, duration_s, num_samples, False)

        # Bright but not harsh
        wave = np.sin(2 * np.pi * frequency * t)
        wave += 0.4 * np.sin(2 * np.pi * frequency * 1.55 * t)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2.2 * t)
        wave += 0.2 * np.sin(2 * np.pi * frequency * 3.3 * t)

        # Smooth decay
        envelope = np.exp(-3 * t / duration_s)
        wave = wave * envelope

        # Normalize
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val * 0.45

        return (wave * 32767).astype(np.int16).tobytes()


class AudioManager:
    """Manages all audio playback for the particle system"""

    def __init__(self):
        self.master_volume = 0.5
        self.collision_volume = 0.7
        self.bounce_volume = 0.4
        self.mute_all = False
        self.background_muted = False

        # Sound generators
        self.synthesizer = SoundSynthesizer()

        # Sound type cycling
        self.bounce_types = ['raindrop', 'wind_chime', 'singing_bowl']
        self.collision_types = ['violin', 'singing_bowl', 'wind_chime']
        self.bounce_index = 0
        self.collision_index = 0

        # Frequencies for notes (pentatonic scale for harmony)
        self.note_frequencies = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25, 783.99, 880.00]
        self.note_index = 0

        # Background music state
        self.background_active = False
        self.background_start_time = 0

    def _get_next_note_frequency(self):
        """Get next note from pentatonic scale"""
        freq = self.note_frequencies[self.note_index % len(self.note_frequencies)]
        self.note_index += 1
        return freq

    def generate_bounce_sound(self):
        """Generate realistic bounce sound"""
        if self.mute_all:
            return None

        # Cycle through sound types
        sound_type = self.bounce_types[self.bounce_index % len(self.bounce_types)]
        self.bounce_index += 1

        frequency = self._get_next_note_frequency()

        if sound_type == 'raindrop':
            data = self.synthesizer.generate_raindrop(frequency=frequency * 0.75, duration_ms=150)
        elif sound_type == 'wind_chime':
            data = self.synthesizer.generate_wind_chime(frequency=frequency, duration_ms=300)
        else:  # singing_bowl
            data = self.synthesizer.generate_singing_bowl(frequency=frequency * 0.5, duration_ms=400)

        return self._create_audio_segment(data)

    def generate_collision_sound(self):
        """Generate smooth collision tone"""
        if self.mute_all:
            return None

        # Cycle through sound types
        sound_type = self.collision_types[self.collision_index % len(self.collision_types)]
        self.collision_index += 1

        frequency = self._get_next_note_frequency()

        if sound_type == 'violin':
            data = self.synthesizer.generate_violin_note(frequency=frequency, duration_ms=600)
        elif sound_type == 'wind_chime':
            data = self.synthesizer.generate_wind_chime(frequency=frequency * 1.2, duration_ms=500)
        else:  # singing_bowl
            data = self.synthesizer.generate_singing_bowl(frequency=frequency * 0.75, duration_ms=800)

        return self._create_audio_segment(data)

    def generate_background_music(self):
        """Generate soothing ambient background music"""
        if self.background_muted or self.mute_all:
            return None

        # Use ambient pad for background
        data = self.synthesizer.generate_ambient_pad(frequency=110, duration_ms=3000)
        return self._create_audio_segment(data)

    def _create_audio_segment(self, audio_data):
        """Create audio segment from raw bytes"""
        class AudioSegment:
            def __init__(self, data):
                self.audio_data = data
                self.sample_rate = 44100
                self.channels = 1
                self.sample_width = 2

        return AudioSegment(audio_data)

