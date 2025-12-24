"""Audio synthesis and management engine"""

import math
import numpy as np
import io
import wave


class SimpleAudioSegment:
    """Simple in-memory audio representation without pydub"""

    def __init__(self, audio_data, sample_rate=44100, channels=1, sample_width=2):
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width

    def __len__(self):
        """Return length in milliseconds"""
        if len(self.audio_data) == 0:
            return 0
        samples = len(self.audio_data) // self.sample_width
        return int((samples / self.sample_rate) * 1000)

    def __add__(self, other):
        """Concatenate audio"""
        if isinstance(other, SimpleAudioSegment):
            return SimpleAudioSegment(
                self.audio_data + other.audio_data,
                self.sample_rate,
                self.channels,
                self.sample_width
            )
        return self

    def __mul__(self, factor):
        """Adjust volume"""
        # Convert to int16
        audio_array = np.frombuffer(self.audio_data, dtype=np.int16)
        audio_array = (audio_array * factor).astype(np.int16)
        return SimpleAudioSegment(
            audio_array.tobytes(),
            self.sample_rate,
            self.channels,
            self.sample_width
        )

    def overlay(self, other, position=0):
        """Overlay another audio segment"""
        if position == 0 and len(other.audio_data) > len(self.audio_data):
            # Extend self
            extended = self.audio_data + b'\x00' * (len(other.audio_data) - len(self.audio_data))
            self_array = np.frombuffer(extended, dtype=np.int16)
        else:
            self_array = np.frombuffer(self.audio_data, dtype=np.int16)

        other_array = np.frombuffer(other.audio_data, dtype=np.int16)

        # Ensure same size
        if len(self_array) < len(other_array):
            self_array = np.concatenate([self_array, np.zeros(len(other_array) - len(self_array), dtype=np.int16)])
        else:
            other_array = np.concatenate([other_array, np.zeros(len(self_array) - len(other_array), dtype=np.int16)])

        # Mix
        mixed = (self_array.astype(np.float32) + other_array.astype(np.float32)) / 2
        mixed = np.clip(mixed, -32768, 32767).astype(np.int16)

        return SimpleAudioSegment(
            mixed.tobytes(),
            self.sample_rate,
            self.channels,
            self.sample_width
        )

    def fade_in(self, duration_ms):
        """Fade in"""
        samples = int(self.sample_rate * duration_ms / 1000)
        audio_array = np.frombuffer(self.audio_data, dtype=np.int16).astype(np.float32)

        if len(audio_array) > 0:
            envelope = np.linspace(0, 1, min(samples, len(audio_array)))
            audio_array[:len(envelope)] *= envelope

        return SimpleAudioSegment(
            audio_array.astype(np.int16).tobytes(),
            self.sample_rate,
            self.channels,
            self.sample_width
        )

    def fade_out(self, duration_ms):
        """Fade out"""
        samples = int(self.sample_rate * duration_ms / 1000)
        audio_array = np.frombuffer(self.audio_data, dtype=np.int16).astype(np.float32)

        if len(audio_array) > 0:
            envelope = np.linspace(1, 0, min(samples, len(audio_array)))
            audio_array[-len(envelope):] *= envelope

        return SimpleAudioSegment(
            audio_array.astype(np.int16).tobytes(),
            self.sample_rate,
            self.channels,
            self.sample_width
        )

    @property
    def dBFS(self):
        """Get loudness in dBFS"""
        audio_array = np.frombuffer(self.audio_data, dtype=np.int16).astype(np.float32)
        if len(audio_array) == 0:
            return -100
        rms = np.sqrt(np.mean(audio_array ** 2))
        if rms > 0:
            return 20 * np.log10(rms / 32768)
        return -100

    def __radd__(self, other):
        """Right add for silent segments"""
        if other == 0:
            return self
        return self + other

    def export(self, path, format="wav"):
        """Export to file"""
        if format == "wav":
            with wave.open(path, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(self.sample_width)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(self.audio_data)


def silent(duration_ms, sample_rate=44100):
    """Create silent audio segment"""
    samples = int(sample_rate * duration_ms / 1000)
    return SimpleAudioSegment(
        b'\x00' * (samples * 2),
        sample_rate,
        1,
        2
    )


class AudioGenerator:
    """Generate synthetic audio tones"""

    SAMPLE_RATE = 44100

    # Pentatonic scale frequencies (Hz)
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
    def generate_sine_wave(frequency, duration_ms, amplitude=0.8):
        """Generate a pure sine wave"""
        duration_s = duration_ms / 1000.0
        num_samples = int(AudioGenerator.SAMPLE_RATE * duration_s)

        t = np.linspace(0, duration_s, num_samples, False)
        wave = amplitude * np.sin(2 * np.pi * frequency * t)

        return wave.astype(np.float32)

    @staticmethod
    def apply_adsr_envelope(wave, attack_ms=10, decay_ms=50, sustain_level=0.8, release_ms=100):
        """Apply ADSR envelope to audio wave"""
        sample_rate = AudioGenerator.SAMPLE_RATE
        total_samples = len(wave)
        duration_s = total_samples / sample_rate

        attack_samples = int(sample_rate * attack_ms / 1000)
        decay_samples = int(sample_rate * decay_ms / 1000)
        release_samples = int(sample_rate * release_ms / 1000)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples

        # Create envelope
        envelope = np.ones_like(wave)

        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        # Decay
        decay_start = attack_samples
        decay_end = decay_start + decay_samples
        if decay_end <= total_samples:
            envelope[decay_start:decay_end] = np.linspace(1, sustain_level, decay_samples)

        # Sustain
        sustain_start = decay_end
        sustain_end = sustain_start + sustain_samples
        if sustain_end <= total_samples:
            envelope[sustain_start:sustain_end] = sustain_level

        # Release
        release_start = sustain_end
        if release_start < total_samples:
            remaining = total_samples - release_start
            envelope[release_start:] = np.linspace(sustain_level, 0, remaining)

        return wave * envelope

    @staticmethod
    def generate_piano_tone(frequency, duration_ms=500):
        """Generate a piano-like tone with harmonics"""
        wave = AudioGenerator.generate_sine_wave(frequency, duration_ms, amplitude=0.6)

        # Add harmonics with decreasing amplitude
        harmonics = [
            (2, 0.3),  # Octave
            (3, 0.15),  # Twelfth
            (4, 0.1),   # Two octaves
        ]

        for harmonic, amplitude in harmonics:
            harmonic_wave = AudioGenerator.generate_sine_wave(
                frequency * harmonic, duration_ms, amplitude=amplitude
            )
            wave = wave[:len(harmonic_wave)] + harmonic_wave

        wave = AudioGenerator.apply_adsr_envelope(
            wave, attack_ms=20, decay_ms=100, sustain_level=0.7, release_ms=150
        )

        return wave

    @staticmethod
    def generate_violin_tone(frequency, duration_ms=500):
        """Generate a violin-like tone with vibrato"""
        wave = AudioGenerator.generate_sine_wave(frequency, duration_ms, amplitude=0.7)

        # Add vibrato (frequency modulation)
        vibrato_rate = 5  # Hz
        vibrato_depth = frequency * 0.02  # 2% frequency modulation

        duration_s = duration_ms / 1000.0
        num_samples = len(wave)
        t = np.linspace(0, duration_s, num_samples, False)

        vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        vibrato_wave = np.sin(2 * np.pi * (frequency + vibrato) * t) * 0.7

        wave = vibrato_wave.astype(np.float32)

        # Add harmonics
        harmonics = [
            (2, 0.2),
            (3, 0.1),
        ]

        for harmonic, amplitude in harmonics:
            harmonic_wave = AudioGenerator.generate_sine_wave(
                frequency * harmonic, duration_ms, amplitude=amplitude
            )
            wave = wave[:len(harmonic_wave)] + harmonic_wave

        wave = AudioGenerator.apply_adsr_envelope(
            wave, attack_ms=50, decay_ms=80, sustain_level=0.8, release_ms=200
        )

        return wave

    @staticmethod
    def generate_synth_tone(frequency, duration_ms=500):
        """Generate a synth tone (square wave with envelope)"""
        duration_s = duration_ms / 1000.0
        num_samples = int(AudioGenerator.SAMPLE_RATE * duration_s)
        t = np.linspace(0, duration_s, num_samples, False)

        # Square wave
        wave = np.sign(np.sin(2 * np.pi * frequency * t)) * 0.6

        # Add sub-harmonic
        sub_wave = np.sign(np.sin(2 * np.pi * frequency * 0.5 * t)) * 0.2
        wave = wave + sub_wave

        wave = AudioGenerator.apply_adsr_envelope(
            wave, attack_ms=5, decay_ms=80, sustain_level=0.6, release_ms=100
        )

        return wave.astype(np.float32)

    @staticmethod
    def generate_pluck_sound(frequency, duration_ms=200):
        """Generate a pluck sound (short and percussive)"""
        wave = AudioGenerator.generate_sine_wave(frequency, duration_ms, amplitude=0.8)

        # Very short envelope for percussive effect
        wave = AudioGenerator.apply_adsr_envelope(
            wave, attack_ms=2, decay_ms=50, sustain_level=0, release_ms=150
        )

        return wave

    @staticmethod
    def wave_to_audio_segment(wave, sample_rate=44100):
        """Convert numpy wave array to AudioSegment"""
        # Normalize to -1 to 1
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val * 0.95

        # Convert to 16-bit PCM
        wave_int = (wave * 32767).astype(np.int16)

        # Convert to bytes
        audio_bytes = wave_int.tobytes()

        # Create AudioSegment
        audio = SimpleAudioSegment(
            audio_bytes,
            sample_rate,
            1,
            2
        )

        return audio


class AudioEngine:
    """Main audio engine for managing sound generation and mixing"""

    def __init__(self):
        self.instrument = "Piano"
        self.master_volume = 0.5
        self.collision_volume = 0.7
        self.spawn_volume = 0.3
        self.ambient_volume = 0.2
        self.enable_reverb = True
        self.mute_all = False

        self.sound_cache = {}  # Cache generated sounds
        self.note_index = 0  # For cycling through pentatonic notes

    def get_instrument_generator(self):
        """Get the appropriate tone generator for current instrument"""
        generators = {
            "Piano": AudioGenerator.generate_piano_tone,
            "Violin": AudioGenerator.generate_violin_tone,
            "Synth": AudioGenerator.generate_synth_tone,
            "Mixed": self._generate_mixed_tone,
        }
        return generators.get(self.instrument, AudioGenerator.generate_piano_tone)

    def _generate_mixed_tone(self, frequency, duration_ms=500):
        """Generate a mixed tone combining piano and violin"""
        piano = AudioGenerator.generate_piano_tone(frequency, duration_ms) * 0.6
        violin = AudioGenerator.generate_violin_tone(frequency, duration_ms) * 0.4

        # Ensure same length
        length = min(len(piano), len(violin))
        return (piano[:length] + violin[:length]).astype(np.float32)

    def generate_collision_sound(self):
        """Generate a sound for particle collision"""
        if self.mute_all:
            return silent(500)

        generator = self.get_instrument_generator()

        # Cycle through pentatonic notes
        notes = list(AudioGenerator.PENTATONIC_NOTES.values())
        frequency = notes[self.note_index % len(notes)]
        self.note_index += 1

        wave = generator(frequency, duration_ms=300)
        audio = AudioGenerator.wave_to_audio_segment(wave)

        # Apply volume
        return audio * (self.collision_volume * self.master_volume)

    def generate_spawn_sound(self):
        """Generate a sound for particle spawn"""
        if self.mute_all:
            return silent(100)

        generator = self.get_instrument_generator()

        # Use a fixed note for spawn
        frequency = AudioGenerator.PENTATONIC_NOTES['A4']

        wave = AudioGenerator.generate_pluck_sound(frequency, duration_ms=100)
        audio = AudioGenerator.wave_to_audio_segment(wave)

        return audio * (self.spawn_volume * self.master_volume)

    def generate_boundary_bounce_sound(self):
        """Generate a sound for boundary collision"""
        if self.mute_all:
            return silent(150)

        # Simple percussion-like sound
        frequency = AudioGenerator.PENTATONIC_NOTES['C4']
        wave = AudioGenerator.generate_pluck_sound(frequency, duration_ms=150)
        audio = AudioGenerator.wave_to_audio_segment(wave)

        return audio * (self.spawn_volume * 0.5 * self.master_volume)

    def generate_ambient_drone(self, duration_ms=1000):
        """Generate ambient drone sound"""
        if self.mute_all:
            return silent(duration_ms)

        # Low C note
        frequency = AudioGenerator.PENTATONIC_NOTES['C4'] / 2  # One octave lower
        wave = AudioGenerator.generate_sine_wave(frequency, duration_ms, amplitude=0.3)

        # Apply slow fade
        num_samples = len(wave)
        fade_envelope = np.linspace(0.1, 0.3, num_samples)
        wave = wave * fade_envelope

        audio = AudioGenerator.wave_to_audio_segment(wave)
        return audio * (self.ambient_volume * self.master_volume)

    def create_collision_audio_track(self, collision_log, total_duration_ms):
        """
        Create audio track from collision events

        Args:
            collision_log: List of collision events with timestamps
            total_duration_ms: Total duration of the track

        Returns:
            AudioSegment: Complete audio track
        """
        # Start with ambient drone
        track = self.generate_ambient_drone(total_duration_ms)

        # Add collision sounds
        for collision in collision_log:
            collision_type = collision.get('type', 'particle')
            time_ms = int(collision.get('time', 0) * 1000)

            if collision_type == 'particle':
                sound = self.generate_collision_sound()
            else:
                sound = self.generate_boundary_bounce_sound()

            # Overlay sound at collision time
            if 0 <= time_ms < total_duration_ms:
                # Ensure track is long enough
                if len(track) < time_ms + len(sound):
                    track = track + silent(time_ms + len(sound) - len(track))

                # Mix sounds
                track = track.overlay(sound, position=time_ms)

        # Ensure correct total duration
        if len(track) > total_duration_ms:
            # Truncate by creating new track with correct length
            track_array = np.frombuffer(track.audio_data, dtype=np.int16)
            samples_to_keep = int(total_duration_ms * 44100 / 1000)
            track_array = track_array[:samples_to_keep]
            track = SimpleAudioSegment(
                track_array.tobytes(),
                track.sample_rate,
                track.channels,
                track.sample_width
            )
        elif len(track) < total_duration_ms:
            track = track + silent(total_duration_ms - len(track))

        # Normalize to prevent clipping
        return self._normalize_audio(track)

    def _normalize_audio(self, audio):
        """Normalize audio to prevent clipping"""
        loudness = audio.dBFS

        # If too loud, reduce volume
        if loudness > -6:
            reduction = -6 - loudness
            factor = 10 ** (reduction / 20)
            return audio * factor

        return audio

    def apply_reverb(self, audio, room_size=0.5):
        """Apply simple reverb effect using delay and mixing"""
        # Create multiple delayed copies
        delays = [50, 100, 200]
        reverb_audio = audio

        for delay_ms in delays:
            delayed = silent(delay_ms) + audio
            reverb_audio = reverb_audio.overlay(delayed, position=0)

        return reverb_audio * (1.0 / (len(delays) + 1))

    def apply_fade(self, audio, fade_in_ms=100, fade_out_ms=100):
        """Apply fade in and fade out effects"""
        audio = audio.fade_in(fade_in_ms)
        audio = audio.fade_out(fade_out_ms)
        return audio

