"""Video export and generation pipeline"""

import cv2
import numpy as np
import os
from pathlib import Path
from src.particle_engine import ParticleEngine
from src.renderer import Renderer
from src.audio_engine import AudioEngine
import tempfile
import shutil
import time
import pygame


class VideoExporter:
    """Handles video generation and export"""

    # Resolution presets
    RESOLUTIONS = {
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4K": (3840, 2160),
    }

    FPS_OPTIONS = [30, 60]

    def __init__(self, output_dir="output"):
        """
        Initialize video exporter

        Args:
            output_dir: Directory to save exported videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = None

    def export_video(self, config, progress_callback=None):
        """
        Export a video with the given configuration

        Args:
            config: ConfigManager object with all settings
            progress_callback: Function to call with (current_frame, total_frames)

        Returns:
            str: Path to output video file
        """
        try:
            # Parse settings
            particle_settings = config.get("particle_settings")
            visual_settings = config.get("visual_settings")
            audio_settings = config.get("audio_settings")
            export_settings = config.get("export_settings")

            # Get resolution and dimensions
            res_name = export_settings.get("resolution", "1080p")
            width, height = self.RESOLUTIONS.get(res_name, (1920, 1080))
            fps = export_settings.get("fps", 60)
            duration_seconds = export_settings.get("duration", 90)
            quality = export_settings.get("quality", 90)

            total_frames = int(fps * duration_seconds)

            # Create temporary directory for frames
            self.temp_dir = tempfile.mkdtemp()

            # Initialize particle engine
            boundary_radius = min(width, height) / 3
            engine = ParticleEngine(width, height, boundary_radius)

            # Configure particle engine
            engine.spawn_rate = particle_settings.get("spawn_rate", 5)
            engine.max_particles = particle_settings.get("max_particles", 100)
            engine.set_particle_size_range(
                particle_settings.get("min_size", 3),
                particle_settings.get("max_size", 15)
            )
            engine.set_particle_speed_range(
                particle_settings.get("min_speed", 1),
                particle_settings.get("max_speed", 5)
            )
            engine.set_particle_shape(particle_settings.get("shape", "Circle"))

            # Spawn initial particles
            initial_count = particle_settings.get("initial_particles", 10)
            engine.spawn_particle(initial_count)

            # Initialize renderer
            renderer = Renderer(width, height)
            renderer.set_color_scheme(visual_settings.get("color_scheme", "Pastel Dreams"))
            renderer.boundary_style = visual_settings.get("boundary_style", "Solid")
            renderer.enable_glow = visual_settings.get("enable_glow", True)
            renderer.enable_trails = visual_settings.get("enable_trails", True)
            renderer.trail_length = visual_settings.get("trail_length", 20)
            renderer.collision_effect = visual_settings.get("collision_effect", "Sparkle")
            renderer.motion_blur = visual_settings.get("motion_blur", False)

            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_path = self.output_dir / f"particle_video_{int(time.time())}.mp4"
            video_writer = cv2.VideoWriter(
                str(video_path), fourcc, fps, (width, height)
            )

            # Initialize audio engine
            audio_engine = AudioEngine()
            audio_engine.instrument = audio_settings.get("instrument", "Piano")
            audio_engine.master_volume = audio_settings.get("master_volume", 0.5)
            audio_engine.collision_volume = audio_settings.get("collision_volume", 0.7)
            audio_engine.spawn_volume = audio_settings.get("spawn_volume", 0.3)
            audio_engine.ambient_volume = audio_settings.get("ambient_volume", 0.2)
            audio_engine.enable_reverb = audio_settings.get("enable_reverb", True)
            audio_engine.mute_all = audio_settings.get("mute_all", False)

            # Render frames
            dt = 1.0 / fps

            for frame_num in range(total_frames):
                # Update simulation
                engine.update(dt)

                # Render frame
                frame_surface = renderer.render(
                    engine.particles, engine.boundary_radius
                )

                # Draw HUD
                renderer.draw_hud(frame_surface, engine.get_particle_count(), fps)

                # Convert pygame surface to OpenCV image
                frame_array = pygame.surfarray.array3d(frame_surface)
                frame_array = np.transpose(frame_array, (1, 0, 2))
                frame_array = cv2.cvtColor(frame_array.astype(np.uint8), cv2.COLOR_RGB2BGR)

                # Write frame
                video_writer.write(frame_array)

                # Progress callback
                if progress_callback:
                    progress_callback(frame_num + 1, total_frames)

            # Release video writer
            video_writer.release()

            # Generate audio track
            if progress_callback:
                progress_callback(total_frames, total_frames, "Generating audio...")

            total_duration_ms = int(duration_seconds * 1000)
            audio_track = audio_engine.create_collision_audio_track(
                engine.collision_log, total_duration_ms
            )

            # Apply effects if enabled
            if audio_settings.get("enable_reverb", True):
                audio_track = audio_engine.apply_reverb(audio_track)

            # Combine video and audio
            if progress_callback:
                progress_callback(total_frames, total_frames, "Combining video and audio...")

            output_with_audio = self._combine_video_audio(
                str(video_path), audio_track
            )

            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

            return output_with_audio

        except Exception as e:
            print(f"Error during video export: {e}")
            raise

    def _combine_video_audio(self, video_path, audio_segment):
        """
        Combine video file with audio segment

        Args:
            video_path: Path to video file
            audio_segment: AudioSegment to combine

        Returns:
            str: Path to output video with audio
        """
        import subprocess

        # Save audio to temporary file
        audio_path = os.path.join(self.temp_dir or tempfile.gettempdir(), "audio.wav")
        audio_segment.export(audio_path, format="wav")

        # Output path
        output_path = str(self.output_dir / f"final_{int(time.time())}.mp4")

        # Use ffmpeg to combine
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]

            # Try to use ffmpeg if available
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                os.remove(video_path)  # Remove video-only file
                return output_path
            except (FileNotFoundError, subprocess.CalledProcessError):
                # If ffmpeg not available, just return video without audio
                print("Warning: FFmpeg not found. Video exported without audio.")
                return video_path

        except Exception as e:
            print(f"Error combining video and audio: {e}")
            return video_path

    def estimate_export_time(self, duration_seconds, fps, resolution, quality):
        """
        Estimate time to export video

        Args:
            duration_seconds: Video duration in seconds
            fps: Frames per second
            resolution: Resolution name ("720p", "1080p", "4K")
            quality: Quality setting (0-100)

        Returns:
            float: Estimated time in seconds
        """
        total_frames = duration_seconds * fps

        # Base time per frame (in seconds)
        width, height = self.RESOLUTIONS.get(resolution, (1920, 1080))
        pixels = width * height
        base_time = pixels / 2000000.0  # Rough estimate

        # Quality factor
        quality_factor = 1.0 + (quality - 50) / 100.0

        # Total estimate
        estimate = total_frames * base_time * quality_factor

        # Add time for audio generation (roughly 0.1x realtime)
        estimate += duration_seconds * 0.1

        return estimate


# Import pygame for video rendering
import pygame
pygame.init()

