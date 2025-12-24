"""
Offline audio engine for high-quality video export audio.
"""
import numpy as np
from typing import List, Dict
from scipy.io import wavfile
import io

from src.audio.synthesis import Synthesizer, apply_reverb, apply_limiter
from src.core.settings import AppSettings
from src.core.events import CollisionEvent, BoundaryHitEvent, SpawnEvent


class OfflineAudioEngine:
    """High-quality offline audio rendering for export."""

    def __init__(self, settings: AppSettings, duration: float):
        self.settings = settings
        self.duration = duration
        self.sample_rate = 44100

        # Synthesizer
        self.synthesizer = Synthesizer(self.sample_rate)

        # Audio buffer
        self.buffer = np.zeros(int(duration * self.sample_rate), dtype=np.float32)

        # Volume settings
        self.master_volume = settings.audio_master_volume
        self.collision_volume = settings.audio_collision_volume
        self.spawn_volume = settings.audio_spawn_volume
        self.boundary_volume = settings.audio_boundary_volume
        self.ambient_volume = settings.audio_ambient_volume

    def schedule_collision(self, event: CollisionEvent):
        """Schedule a collision sound event."""
        # Map energy to frequency
        frequency = self.synthesizer.frequency_from_energy(
            event.energy,
            scale=self.settings.audio_scale,
            energy_range=(0, 500)
        )

        # Duration based on energy
        duration = self.synthesizer.duration_from_energy(
            event.energy,
            min_duration=0.1,
            max_duration=0.5,
            energy_range=(0, 500)
        )

        # Volume based on energy
        volume = min(1.0, event.energy / 200.0) * self.collision_volume * self.master_volume

        # Generate note
        self._add_note(event.timestamp, frequency, duration, volume)

    def schedule_boundary_hit(self, event: BoundaryHitEvent):
        """Schedule a boundary hit sound event."""
        # Lower frequency for boundary
        frequency = self.synthesizer.frequency_from_energy(
            event.energy,
            scale=self.settings.audio_scale,
            energy_range=(0, 300)
        ) * 0.7

        duration = 0.2
        volume = min(1.0, event.energy / 150.0) * self.boundary_volume * self.master_volume

        self._add_note(event.timestamp, frequency, duration, volume)

    def schedule_spawn(self, event: SpawnEvent):
        """Schedule a spawn sound event."""
        # Higher pitched, short sound
        frequency = 523.25  # C5
        duration = 0.15
        volume = self.spawn_volume * self.master_volume * 0.6

        self._add_note(event.timestamp, frequency, duration, volume)

    def _add_note(self, timestamp: float, frequency: float, duration: float, volume: float):
        """Add a note to the audio buffer."""
        # Start sample
        start_sample = int(timestamp * self.sample_rate)

        if start_sample >= len(self.buffer):
            return

        # Instrument selection
        instrument = self.settings.audio_instrument
        if instrument == "mixed":
            # Cycle through instruments
            instruments = ["piano", "violin", "bell", "soft_pad"]
            instrument = instruments[int(timestamp * 10) % len(instruments)]

        # Generate note
        audio = self.synthesizer.generate_note(
            frequency,
            duration,
            instrument,
            amplitude=volume
        )

        # Add to buffer
        end_sample = min(start_sample + len(audio), len(self.buffer))
        samples_to_add = end_sample - start_sample

        if samples_to_add > 0:
            self.buffer[start_sample:end_sample] += audio[:samples_to_add]

    def add_ambient_drone(self):
        """Add ambient drone background."""
        if self.ambient_volume <= 0:
            return

        # Low frequency drone
        t = np.linspace(0, self.duration, len(self.buffer), endpoint=False)

        # Multiple frequencies for richness
        frequencies = [65.41, 98.00, 130.81]  # C2, G2, C3

        ambient = np.zeros_like(self.buffer)
        for freq in frequencies:
            ambient += np.sin(2 * np.pi * freq * t) / len(frequencies)

        # Apply slow amplitude modulation
        modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
        ambient *= modulation

        # Add to buffer with volume
        self.buffer += ambient * self.ambient_volume * self.master_volume * 0.3

    def finalize(self) -> np.ndarray:
        """
        Finalize audio buffer with effects.

        Returns:
            Final audio as float32 array
        """
        audio = self.buffer.copy()

        # Normalize to prevent clipping before effects
        max_val = np.abs(audio).max()
        if max_val > 0.8:
            audio = audio / max_val * 0.8

        # Apply reverb
        if self.settings.audio_reverb_enabled:
            audio = apply_reverb(
                audio,
                amount=self.settings.audio_reverb_amount,
                sample_rate=self.sample_rate
            )

        # Apply limiter
        if self.settings.audio_limiter_enabled:
            audio = apply_limiter(
                audio,
                threshold=self.settings.audio_limiter_threshold
            )

        # Final normalization
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val * 0.95

        return audio

    def export_wav(self, output_path: str):
        """
        Export audio to WAV file using scipy.

        Args:
            output_path: Output file path
        """
        # Finalize audio
        audio = self.finalize()

        # Convert to 16-bit PCM
        audio_int = (audio * 32767).astype(np.int16)

        # Create stereo by duplicating
        stereo = np.column_stack((audio_int, audio_int))

        # Export using scipy
        wavfile.write(output_path, self.sample_rate, stereo)

    def get_audio_array(self) -> np.ndarray:
        """
        Get finalized audio as array.

        Returns:
            Audio array (samples,)
        """
        return self.finalize()

