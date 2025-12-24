
import numpy as np
import wave
from pydub import AudioSegment

from ..core.settings import Settings
from ..core.events import BaseEvent, CollisionEvent, SpawnEvent, BoundaryHitEvent
from .synthesis import (
    synthesize_instrument,
    get_note_from_scale,
    apply_reverb,
    apply_limiter,
    SAMPLE_RATE,
    SCALES
)

class AudioEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.buffer = None
        self.reset()

    def reset(self):
        """Resets the audio buffer to silence."""
        duration_samples = int(self.settings.simulation.duration_sec * SAMPLE_RATE)
        self.buffer = np.zeros(duration_samples, dtype=np.float32)

    def process_events(self, events: list[BaseEvent]):
        """Processes a list of simulation events and synthesizes audio for them."""
        if not self.settings.audio.enabled:
            return

        for event in events:
            sound = self._synthesize_event(event)
            if sound is not None:
                start_sample = int(event.timestamp * SAMPLE_RATE)
                end_sample = start_sample + len(sound)

                # Mix sound into buffer, preventing overflow
                if end_sample <= len(self.buffer):
                    self.buffer[start_sample:end_sample] += sound

    def _synthesize_event(self, event: BaseEvent) -> np.ndarray | None:
        """Generates an audio waveform for a single event."""
        a_settings = self.settings.audio
        scale_notes = SCALES.get(a_settings.scale, SCALES["pentatonic_c"])

        if isinstance(event, CollisionEvent):
            freq = get_note_from_scale(event.energy, a_settings.scale, a_settings.music_mood)
            duration = np.clip(event.energy / 20000, 0.1, 1.5)
            volume = np.clip(event.relative_speed / 200, 0.2, 1.0) * a_settings.collision_volume
            return synthesize_instrument(a_settings.instrument, freq, duration, volume)

        elif isinstance(event, SpawnEvent):
            duration = 0.5
            volume = a_settings.spawn_volume
            # Play a soft, high note for spawn
            freq = max(scale_notes) * 2
            return synthesize_instrument("bell", freq, duration, volume)

        elif isinstance(event, BoundaryHitEvent):
            duration = 1.0
            volume = np.clip(event.energy / 5000, 0.1, 0.8) * a_settings.master_volume
            # Play a low pad note for boundary hit
            freq = min(scale_notes) / 2
            return synthesize_instrument("soft_pad", freq, duration, volume)

        return None

    def finalize_audio(self, output_path: str):
        """Applies final effects and exports the buffer to a WAV file."""
        if not self.settings.audio.enabled:
            # Create a silent WAV file of the correct duration
            final_buffer = np.zeros_like(self.buffer)
        else:
            final_buffer = self.buffer.copy()
            a_settings = self.settings.audio
            scale_notes = SCALES.get(a_settings.scale, SCALES["pentatonic_c"])

            # Add ambient drone
            drone_freq1 = min(scale_notes) / 2
            drone_freq2 = scale_notes[2] if len(scale_notes) > 2 else min(scale_notes)
            drone1 = synthesize_instrument("soft_pad", drone_freq1, self.settings.simulation.duration_sec, a_settings.ambient_volume * 0.5)
            drone2 = synthesize_instrument("soft_pad", drone_freq2, self.settings.simulation.duration_sec, a_settings.ambient_volume * 0.5)
            final_buffer[:len(drone1)] += drone1
            final_buffer[:len(drone2)] += drone2

            if a_settings.reverb_enabled:
                final_buffer = apply_reverb(final_buffer, a_settings.reverb_amount)

            if a_settings.limiter_enabled:
                final_buffer = apply_limiter(final_buffer, a_settings.limiter_threshold)

        # Convert to 16-bit PCM for WAV export
        pcm_buffer = (final_buffer * 32767).astype(np.int16)

        # Use pydub for robust WAV export
        audio_segment = AudioSegment(
            pcm_buffer.tobytes(),
            frame_rate=SAMPLE_RATE,
            sample_width=pcm_buffer.dtype.itemsize,
            channels=1
        )
        audio_segment.export(output_path, format="wav")
