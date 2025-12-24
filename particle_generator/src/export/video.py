
import os
import time
import numpy as np
import pygame
from PyQt5.QtCore import QThread, pyqtSignal
from moviepy.editor import ImageSequenceClip, AudioFileClip

from ..core.settings import Settings
from ..physics.system import ParticleSystem
from ..graphics.renderer import Renderer
from ..audio.engine import AudioEngine
from ..core.events import event_queue

class ExportWorker(QThread):
    progress = pyqtSignal(int, int, str)  # current_frame, total_frames, message
    finished = pyqtSignal(str)           # output_filepath
    error = pyqtSignal(str)              # error_message

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self._is_cancelled = False

    def run(self):
        try:
            # --- 1. SETUP ---
            self.progress.emit(0, 100, "Initializing export...")

            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            base_filename = f"final_{timestamp}"

            video_filepath = os.path.join(output_dir, f"{base_filename}.mp4")
            settings_filepath = os.path.join(output_dir, f"{base_filename}.json")
            audio_filepath = os.path.join(output_dir, f"temp_audio_{timestamp}.wav")

            # Save the settings used for this export
            self.settings.save_to_json(settings_filepath)

            # --- 2. DETERMINISTIC SIMULATION & FRAME RENDERING ---
            sim_settings = self.settings.simulation
            total_frames = int(sim_settings.duration_sec * sim_settings.fps_export)
            frame_dt = 1.0 / sim_settings.fps_export

            # Setup deterministic environment
            system = ParticleSystem(self.settings)
            system.reset() # Seeds the RNG
            renderer = Renderer(self.settings)
            audio_engine = AudioEngine(self.settings)

            frames = []

            for i in range(total_frames):
                if self._is_cancelled:
                    raise InterruptedError("Export was cancelled.")

                self.progress.emit(i, total_frames, f"Simulating frame {i+1}/{total_frames}")

                # Advance simulation to the exact time of the next frame
                target_time = (i + 1) * frame_dt
                while system.time < target_time:
                    system.update(sim_settings.dt_sim)

                # Render the frame
                surface = pygame.Surface(sim_settings.resolution)
                frame_events = event_queue.get_events()
                renderer.draw(surface, system, frame_events, frame_dt)

                # Process events for audio
                audio_engine.process_events(frame_events)

                # Convert Pygame surface to a NumPy array for MoviePy
                frame_data = pygame.surfarray.array3d(surface)
                frames.append(np.transpose(frame_data, (1, 0, 2))) # H, W, C -> W, H, C

            # --- 3. AUDIO SYNTHESIS ---
            self.progress.emit(total_frames, total_frames, "Finalizing audio...")
            audio_engine.finalize_audio(audio_filepath)

            # --- 4. VIDEO ENCODING ---
            self.progress.emit(total_frames, total_frames, "Encoding video with MoviePy...")

            clip = ImageSequenceClip(frames, fps=sim_settings.fps_export)
            audio_clip = AudioFileClip(audio_filepath)

            final_clip = clip.set_audio(audio_clip)
            final_clip.write_videofile(
                video_filepath,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=f'temp-audio_{timestamp}.m4a',
                remove_temp=True
            )

            self.finished.emit(video_filepath)

        except InterruptedError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"An unexpected error occurred: {e}")
        finally:
            # --- 5. CLEANUP ---
            if os.path.exists(audio_filepath):
                os.remove(audio_filepath)

    def cancel(self):
        self._is_cancelled = True

class InterruptedError(Exception):
    pass
