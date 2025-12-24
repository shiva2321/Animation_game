"""
Real-time preview audio mixer with polyphony limiting and pygame.mixer integration.
"""
import pygame
import numpy as np
from typing import Dict, List
import time
from collections import deque

from src.audio.synthesis import Synthesizer
from src.core.settings import AppSettings


class PreviewAudioMixer:
    """Real-time audio mixer for preview playback."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.enabled = settings.audio_enabled and settings.audio_preview_enabled

        if not self.enabled:
            return

        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.sample_rate = 22050
        except Exception as e:
            print(f"Failed to initialize audio: {e}")
            self.enabled = False
            return

        # Synthesizer
        self.synthesizer = Synthesizer(self.sample_rate)

        # Active sounds tracking
        self.active_channels: List[pygame.mixer.Channel] = []
        self.max_polyphony = settings.audio_preview_polyphony

        # Rate limiting
        self.event_times = deque(maxlen=100)
        self.max_events_per_second = settings.audio_preview_rate_limit

        # Volume settings
        self.master_volume = settings.audio_master_volume
        self.collision_volume = settings.audio_collision_volume
        self.spawn_volume = settings.audio_spawn_volume
        self.boundary_volume = settings.audio_boundary_volume

        # Cache for frequently used notes
        self.note_cache: Dict[Tuple[float, str], pygame.mixer.Sound] = {}
        self.cache_size_limit = 50

    def play_collision(self, energy: float):
        """Play collision sound."""
        if not self.enabled or not self._check_rate_limit():
            return

        # Map energy to frequency
        frequency = self.synthesizer.frequency_from_energy(
            energy,
            scale=self.settings.audio_scale,
            energy_range=(0, 500)
        )

        # Duration based on energy
        duration = self.synthesizer.duration_from_energy(
            energy,
            min_duration=0.05,
            max_duration=0.2,
            energy_range=(0, 500)
        )

        # Volume based on energy
        volume = min(1.0, energy / 200.0) * self.collision_volume * self.master_volume

        self._play_note(frequency, duration, volume, "collision")

    def play_spawn(self):
        """Play spawn sound."""
        if not self.enabled or not self._check_rate_limit():
            return

        # Higher pitched, short sound
        frequency = 523.25  # C5
        duration = 0.1
        volume = self.spawn_volume * self.master_volume * 0.5

        self._play_note(frequency, duration, volume, "spawn")

    def play_boundary_hit(self, energy: float):
        """Play boundary hit sound."""
        if not self.enabled or not self._check_rate_limit():
            return

        # Lower frequency for boundary
        frequency = self.synthesizer.frequency_from_energy(
            energy,
            scale=self.settings.audio_scale,
            energy_range=(0, 300)
        ) * 0.7

        duration = 0.15
        volume = min(1.0, energy / 150.0) * self.boundary_volume * self.master_volume

        self._play_note(frequency, duration, volume, "boundary")

    def _play_note(self, frequency: float, duration: float, volume: float, event_type: str):
        """Play a note with polyphony management."""
        if not self.enabled:
            return

        # Check cache
        cache_key = (round(frequency, 1), event_type)

        if cache_key in self.note_cache:
            sound = self.note_cache[cache_key]
        else:
            # Generate note
            instrument = self.settings.audio_instrument
            if instrument == "mixed":
                # Randomly choose instrument based on event type
                instruments = ["piano", "violin", "bell", "soft_pad"]
                instrument = instruments[int(time.time() * 1000) % len(instruments)]

            audio = self.synthesizer.generate_note(
                frequency,
                duration,
                instrument,
                amplitude=0.8
            )

            # Convert to 16-bit PCM
            audio_int = (audio * 32767).astype(np.int16)

            # Create stereo by duplicating
            stereo = np.column_stack((audio_int, audio_int))

            # Create pygame Sound
            try:
                sound = pygame.mixer.Sound(stereo)

                # Cache if under limit
                if len(self.note_cache) < self.cache_size_limit:
                    self.note_cache[cache_key] = sound
            except Exception as e:
                print(f"Failed to create sound: {e}")
                return

        # Find available channel or stop oldest
        channel = pygame.mixer.find_channel()

        if channel is None:
            # All channels busy, stop the first one
            if pygame.mixer.get_num_channels() > 0:
                channel = pygame.mixer.Channel(0)
                channel.stop()

        if channel:
            try:
                channel.set_volume(min(1.0, volume))
                channel.play(sound)
            except Exception as e:
                print(f"Failed to play sound: {e}")

    def _check_rate_limit(self) -> bool:
        """Check if we're under the rate limit."""
        current_time = time.time()
        self.event_times.append(current_time)

        # Count events in last second
        one_second_ago = current_time - 1.0
        recent_events = sum(1 for t in self.event_times if t > one_second_ago)

        return recent_events <= self.max_events_per_second

    def update_settings(self, settings: AppSettings):
        """Update mixer settings."""
        self.settings = settings
        self.master_volume = settings.audio_master_volume
        self.collision_volume = settings.audio_collision_volume
        self.spawn_volume = settings.audio_spawn_volume
        self.boundary_volume = settings.audio_boundary_volume
        self.max_polyphony = settings.audio_preview_polyphony
        self.max_events_per_second = settings.audio_preview_rate_limit

    def cleanup(self):
        """Clean up audio resources."""
        if self.enabled:
            try:
                pygame.mixer.stop()
                pygame.mixer.quit()
            except:
                pass

