"""
Video export with deterministic rendering and audio muxing.
"""
import os
from pathlib import Path
from datetime import datetime
import numpy as np
import logging
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
try:
    # MoviePy 2.x
    from moviepy import VideoClip, AudioFileClip
except ImportError:
    # MoviePy 1.x
    from moviepy.editor import VideoClip, AudioFileClip
import pygame

from src.core.settings import AppSettings
from src.physics.system import ParticleSystem
from src.physics.particle import Particle
from src.graphics.renderer import AdvancedRenderer
from src.audio.engine import OfflineAudioEngine
from src.audio.background_music import BackgroundMusicGenerator
from src.core.rng import DeterministicRNG


logger = logging.getLogger(__name__)


class VideoExportWorker(QThread):
    """Worker thread for video export."""

    # Signals
    progress = pyqtSignal(int)  # Progress percentage
    status = pyqtSignal(str)  # Status message
    finished = pyqtSignal(str)  # Finished with output path
    error = pyqtSignal(str)  # Error message

    def __init__(self, settings: AppSettings, output_dir: Path):
        super().__init__()
        self.settings = settings
        self.output_dir = output_dir
        self.cancelled = False
        self.temp_audio_path = None

    def cancel(self):
        """Cancel the export."""
        self.cancelled = True
        logger.info("Export cancelled by user")

    def run(self):
        """Main export thread."""
        try:
            self._export()
        except Exception as e:
            logger.exception("Export error")
            self.error.emit(f"Export failed: {str(e)}")

    def _export(self):
        """Execute export pipeline."""
        # Create timestamp for output files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"particle_video_{timestamp}"

        # Validate settings
        warnings = self.settings.validate_and_clamp()
        for warning in warnings:
            logger.warning(warning)

        # Save settings
        settings_path = self.output_dir / f"{output_name}_settings.json"
        self.settings.save_json(settings_path)
        logger.info(f"Settings saved to {settings_path}")

        # Initialize deterministic simulation
        self.status.emit("Initializing simulation...")
        rng = DeterministicRNG(self.settings.seed)
        physics_system = ParticleSystem(self.settings, rng)

        # Initialize renderer
        self.status.emit("Initializing renderer...")
        renderer = AdvancedRenderer(self.settings)

        # Initialize audio engine
        audio_engine = None
        if self.settings.audio_enabled:
            self.status.emit("Initializing audio engine...")
            audio_engine = OfflineAudioEngine(
                self.settings,
                self.settings.duration_sec
            )

        # Simulation parameters
        dt_sim = self.settings.dt_sim
        fps_export = self.settings.fps_export
        frame_dt = 1.0 / fps_export

        total_frames = int(self.settings.duration_sec * fps_export)

        # Storage for frames
        frames = []

        # Reset particle IDs for determinism
        Particle.reset_id_counter()

        # Simulation and rendering loop
        self.status.emit("Rendering frames...")

        sim_time = 0.0
        frame_count = 0

        while frame_count < total_frames:
            if self.cancelled:
                return

            # Advance simulation to next frame time
            target_time = frame_count * frame_dt

            while sim_time < target_time:
                # Step physics
                physics_system.step(dt_sim)

                # Collect events for audio
                if audio_engine:
                    events = physics_system.event_queue.get_all_events()

                    for event in events['collisions']:
                        audio_engine.schedule_collision(event)

                    for event in events['boundary']:
                        audio_engine.schedule_boundary_hit(event)

                    for event in events['spawns']:
                        audio_engine.schedule_spawn(event)

                # Add effects (for rendering)
                events = physics_system.event_queue.get_all_events()
                for event in events['collisions']:
                    renderer.add_collision_effect(
                        event.point,
                        event.normal,
                        event.mixed_color,
                        event.energy
                    )

                for event in events['boundary']:
                    renderer.add_boundary_effect(
                        event.point,
                        event.color,
                        event.energy
                    )

                sim_time += dt_sim

            # Update effects
            renderer.update_effects(dt_sim)

            # Render frame
            renderer.render_frame(physics_system.particles)

            # Get frame as array
            frame_array = renderer.get_frame_array()
            frames.append(frame_array)

            frame_count += 1

            # Update progress
            progress_pct = int((frame_count / total_frames) * 80)
            self.progress.emit(progress_pct)

            if frame_count % 30 == 0:
                logger.info(f"Rendered {frame_count}/{total_frames} frames")

        if self.cancelled:
            return

        # Generate audio
        audio_path = None
        if audio_engine:
            self.status.emit("Generating audio...")
            self.progress.emit(85)

            # Add ambient drone
            audio_engine.add_ambient_drone()

            # Export event audio (collisions, spawns, etc.)
            audio_path = self.output_dir / f"{output_name}_audio.wav"
            self.temp_audio_path = audio_path
            audio_engine.export_wav(str(audio_path))
            logger.info(f"Audio exported to {audio_path}")

            # Generate background music if enabled
            bgm_enabled = getattr(self.settings, 'bgm_enabled', False)
            bgm_volume = getattr(self.settings, 'bgm_volume', 0.15)

            if bgm_enabled and bgm_volume > 0:
                try:
                    self.status.emit("Generating background music...")
                    bgm_gen = BackgroundMusicGenerator(
                        duration=self.settings.duration_sec,
                        sample_rate=44100
                    )
                    bgm_audio = bgm_gen.generate(style="calm")

                    # Load event audio
                    from scipy.io import wavfile
                    event_rate, event_audio = wavfile.read(str(audio_path))

                    # Ensure same length
                    min_length = min(len(bgm_audio), len(event_audio))
                    bgm_audio = bgm_audio[:min_length]
                    event_audio = event_audio[:min_length]

                    # Convert event_audio to float if needed
                    if event_audio.dtype != np.float32:
                        event_audio = event_audio.astype(np.float32) / 32767.0

                    # Mix: background music + event sounds
                    mixed_audio = event_audio + (bgm_audio * bgm_volume)

                    # Normalize to prevent clipping
                    max_val = np.max(np.abs(mixed_audio))
                    if max_val > 0:
                        mixed_audio = mixed_audio / max_val * 0.95

                    # Convert back to int16
                    mixed_audio = (mixed_audio * 32767).astype(np.int16)

                    # Save mixed audio
                    wavfile.write(str(audio_path), 44100, mixed_audio)
                    logger.info("Background music mixed successfully")

                except Exception as e:
                    logger.warning(f"Failed to add background music: {e}")
                    # Continue with event audio only

        if self.cancelled:
            self._cleanup()
            return

        # Create video
        self.status.emit("Encoding video...")
        self.progress.emit(90)

        video_path = self.output_dir / f"{output_name}.mp4"

        # Create video clip from frames
        def make_frame(t):
            """Get frame at time t."""
            frame_idx = int(t * fps_export)
            if frame_idx >= len(frames):
                frame_idx = len(frames) - 1
            return frames[frame_idx]

        video_clip = VideoClip(make_frame, duration=self.settings.duration_sec)
        video_clip = video_clip.set_fps(fps_export)

        # Add audio if available
        if audio_path and audio_path.exists():
            audio_clip = AudioFileClip(str(audio_path))
            video_clip = video_clip.set_audio(audio_clip)

        # Write video file
        video_clip.write_videofile(
            str(video_path),
            fps=fps_export,
            codec='libx264',
            audio_codec='aac' if audio_path else None,
            preset='medium',
            threads=4,
            logger=None  # Suppress moviepy progress bars
        )

        logger.info(f"Video exported to {video_path}")

        # Cleanup
        self._cleanup()

        self.progress.emit(100)
        self.status.emit("Export complete!")
        self.finished.emit(str(video_path))

    def _cleanup(self):
        """Clean up temporary files."""
        if self.temp_audio_path and self.temp_audio_path.exists():
            try:
                os.remove(self.temp_audio_path)
                logger.info("Cleaned up temporary audio file")
            except Exception as e:
                logger.warning(f"Failed to clean up temp audio: {e}")

