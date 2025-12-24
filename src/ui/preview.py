"""
Preview widget embedding pygame into PyQt6.
"""
import pygame
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
import logging
import numpy as np

from src.physics.system import ParticleSystem
from src.graphics.renderer import AdvancedRenderer
from src.audio.preview_mixer import PreviewAudioMixer
from src.core.settings import AppSettings
from src.core.rng import DeterministicRNG


logger = logging.getLogger(__name__)


class PreviewWidget(QWidget):
    """Widget for real-time physics simulation preview."""

    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = settings

        # State
        self.running = False
        self.initialized = False
        self.last_render_time = 0
        self.render_errors = 0
        self.max_errors = 10  # Stop after too many errors
        self.rendering_lock = False  # Prevent concurrent renders

        # Components (initialized lazily)
        self.rng = None
        self.physics_system = None
        self.renderer = None
        self.audio_mixer = None

        # Display label
        self.display_label = None

        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.setSingleShot(False)  # Repeating timer

        # FPS tracking
        self.last_time = 0
        self.fps_counter = 0
        self.current_fps = 0

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup the widget UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Create display label for showing rendered frames
        self.display_label = QLabel()
        self.display_label.setMinimumSize(800, 600)
        self.display_label.setStyleSheet("background-color: #000000; border: 1px solid #0f3460;")
        self.display_label.setScaledContents(False)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.display_label)

        # Set minimum size
        self.setMinimumSize(800, 600)

    def initialize_preview(self):
        """Initialize preview components."""
        if self.initialized:
            return

        try:
            # Initialize pygame
            if not pygame.get_init():
                pygame.init()

            # Initialize pygame mixer for background music
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                    logger.info("Pygame mixer initialized for audio")
                except Exception as mixer_err:
                    logger.warning(f"Pygame mixer initialization failed: {mixer_err}")

            # Create RNG
            self.rng = DeterministicRNG(self.settings.seed)

            # Create physics system
            self.physics_system = ParticleSystem(self.settings, self.rng)

            # Create renderer
            self.renderer = AdvancedRenderer(self.settings)

            # Create audio mixer (with error handling)
            try:
                self.audio_mixer = PreviewAudioMixer(self.settings)

                # Generate and play background music if enabled
                if getattr(self.settings, 'bgm_enabled', False):
                    try:
                        from src.audio.background_music import BackgroundMusicGenerator
                        import scipy.io.wavfile as wavfile
                        import tempfile
                        import os

                        logger.info("Generating background music for preview...")
                        bgm_gen = BackgroundMusicGenerator(
                            duration=60.0,  # Generate 1 minute loop
                            sample_rate=44100
                        )
                        bgm_style = getattr(self.settings, 'bgm_style', 'calm')
                        bgm_audio = bgm_gen.generate(style=bgm_style)

                        # Save to temp file
                        self.bgm_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                        bgm_volume = getattr(self.settings, 'bgm_volume', 0.15)

                        # Scale volume
                        bgm_audio_scaled = (bgm_audio * bgm_volume * 32767).astype(np.int16)
                        wavfile.write(self.bgm_temp_file.name, 44100, bgm_audio_scaled)
                        self.bgm_temp_file.close()

                        # Load and play with pygame mixer
                        try:
                            pygame.mixer.music.load(self.bgm_temp_file.name)
                            pygame.mixer.music.play(loops=-1)  # Loop indefinitely
                            logger.info("Background music started")
                        except Exception as music_err:
                            logger.warning(f"Could not play background music: {music_err}")

                    except Exception as bgm_err:
                        logger.warning(f"Background music generation failed: {bgm_err}")
                        self.bgm_temp_file = None
                else:
                    self.bgm_temp_file = None

            except Exception as audio_error:
                logger.warning(f"Audio mixer initialization failed: {audio_error}")
                logger.warning("Continuing without audio preview")
                self.audio_mixer = None
                self.bgm_temp_file = None

            self.initialized = True
            logger.info("Preview initialized successfully")

        except Exception as e:
            logger.exception("Failed to initialize preview")
            raise

    def start_preview(self):
        """Start the preview simulation."""
        if not self.initialized:
            try:
                self.initialize_preview()
            except Exception as e:
                logger.error(f"Failed to initialize: {e}")
                return

        self.running = True
        self.render_errors = 0  # Reset error counter
        self.rendering_lock = False  # Reset lock

        # Start timer at SAFE FPS (max 30fps for stability)
        target_fps = min(self.settings.fps_preview, 30)  # Cap at 30fps
        interval_ms = max(int(1000 / target_fps), 33)  # Min 33ms (30fps)
        self.timer.start(interval_ms)

        logger.info(f"Preview started at {1000/interval_ms:.1f} fps (interval: {interval_ms}ms)")

    def pause_preview(self):
        """Pause the preview."""
        self.running = False
        self.timer.stop()

        # Pause background music
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
        except:
            pass

        logger.info("Preview paused")

    def cleanup(self):
        """Clean up resources."""
        try:
            # Stop and cleanup background music
            pygame.mixer.music.stop()
            if hasattr(self, 'bgm_temp_file') and self.bgm_temp_file:
                import os
                try:
                    os.unlink(self.bgm_temp_file.name)
                except:
                    pass
        except:
            pass

    def reset_preview(self):
        """Reset the simulation."""
        if not self.initialized:
            return

        was_running = self.running
        if was_running:
            self.pause_preview()

        # Reset systems
        self.physics_system.reset(self.settings.seed)
        self.renderer.clear_effects()

        if was_running:
            self.start_preview()

        logger.info("Preview reset")

    def update_simulation(self):
        """Update simulation and render - bulletproof version with lock."""
        # Check rendering lock - skip if previous frame still rendering
        if self.rendering_lock:
            logger.debug("Skipping frame - previous frame still rendering")
            return

        # Early exits for safety
        if not self.running:
            return

        if not self.initialized:
            return

        if not self.physics_system or not self.renderer or not self.display_label:
            return

        # Stop if too many errors
        if self.render_errors >= self.max_errors:
            return

        # Acquire lock
        self.rendering_lock = True

        try:
            import time
            current_time = time.time()

            # Throttle if needed (max 30fps for stability)
            if current_time - self.last_render_time < 1.0/30.0:
                return

            self.last_render_time = current_time

            # === PHYSICS UPDATE ===
            try:
                self.physics_system.step()
            except Exception as e:
                logger.error(f"Physics step error: {e}")
                raise

            # === EVENT HANDLING ===
            try:
                events = self.physics_system.event_queue.get_all_events()
            except Exception as e:
                logger.error(f"Event queue error: {e}")
                events = {'collisions': [], 'boundary': [], 'spawns': []}

            # === AUDIO (with error handling) ===
            if self.audio_mixer and self.audio_mixer.enabled:
                try:
                    for event in events.get('collisions', []):
                        self.audio_mixer.play_collision(event.energy)
                    for event in events.get('boundary', []):
                        self.audio_mixer.play_boundary_hit(event.energy)
                    for event in events.get('spawns', []):
                        self.audio_mixer.play_spawn()
                except Exception as audio_err:
                    # Don't crash on audio errors
                    logger.debug(f"Audio error: {audio_err}")

            # === VISUAL EFFECTS ===
            try:
                for event in events.get('collisions', []):
                    self.renderer.add_collision_effect(
                        event.point, event.normal, event.mixed_color, event.energy
                    )
                for event in events.get('boundary', []):
                    self.renderer.add_boundary_effect(
                        event.point, event.color, event.energy
                    )
                self.renderer.update_effects(self.settings.dt_sim)
            except Exception as e:
                logger.debug(f"Effects error: {e}")

            # === RENDERING ===
            try:
                surface = self.renderer.render_frame(self.physics_system.particles)
                if surface:
                    self._display_surface(surface)
            except Exception as e:
                logger.error(f"Render error: {e}")
                raise

            # Check if simulation is complete (all objects settled)
            if self.physics_system.is_settled:
                logger.info("All objects have settled - pausing preview")
                self.pause_preview()
                return

            # Success - reset error counter
            self.render_errors = 0

            # === FPS COUNTER ===
            try:
                self._update_fps()
            except:
                pass

        except Exception as e:
            self.render_errors += 1
            if self.render_errors == 1:
                logger.exception(f"Simulation error (1/{self.max_errors})")
            else:
                logger.error(f"Simulation error ({self.render_errors}/{self.max_errors}): {e}")

            if self.render_errors >= self.max_errors:
                logger.error("Too many errors, stopping preview")
                try:
                    self.pause_preview()
                except:
                    self.running = False
                    self.timer.stop()

        finally:
            # Always release lock
            self.rendering_lock = False

    def _display_surface(self, surface):
        """Convert pygame surface to QPixmap - file-based safe method."""
        if not surface or not self.display_label:
            return

        try:
            import tempfile
            import os

            # Get surface dimensions
            width, height = surface.get_size()

            if width <= 0 or height <= 0:
                return

            # Save to temporary file (completely safe - no memory sharing)
            with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as tmp:
                tmp_path = tmp.name

            try:
                # Save pygame surface to BMP file
                pygame.image.save(surface, tmp_path)

                # Load as QPixmap from file
                pixmap = QPixmap(tmp_path)

                if not pixmap.isNull():
                    # Scale to fit
                    scaled_pixmap = pixmap.scaled(
                        self.display_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.FastTransformation
                    )

                    # Display
                    self.display_label.setPixmap(scaled_pixmap)

            finally:
                # Clean up temp file
                try:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                except:
                    pass

        except Exception as e:
            logger.debug(f"Display error: {e}")

    def _update_fps(self):
        """Update FPS counter."""
        import time
        current_time = time.time()

        if self.last_time > 0:
            self.fps_counter += 1
            elapsed = current_time - self.last_time

            if elapsed >= 1.0:
                self.current_fps = self.fps_counter
                self.fps_counter = 0
                self.last_time = current_time
        else:
            self.last_time = current_time

    def get_stats(self):
        """Get current statistics."""
        if not self.initialized or not self.physics_system:
            return {
                'fps': 0,
                'particles': 0,
                'time': 0.0
            }

        stats = self.physics_system.get_stats()
        stats['fps'] = self.current_fps
        return stats

    def update_settings(self, settings: AppSettings):
        """Update settings and apply changes immediately."""
        was_running = self.running
        old_bgm_enabled = getattr(self.settings, 'bgm_enabled', False)
        old_bgm_style = getattr(self.settings, 'bgm_style', 'calm')
        old_bgm_volume = getattr(self.settings, 'bgm_volume', 0.15)

        self.settings = settings

        if self.initialized:
            # Update audio mixer
            if self.audio_mixer:
                try:
                    self.audio_mixer.update_settings(settings)
                except:
                    pass

            # Update renderer
            if self.renderer:
                self.renderer.settings = settings
                # Regenerate background if scheme changed
                try:
                    self.renderer._render_background()
                except:
                    pass

            # Update physics system
            if self.physics_system:
                self.physics_system.settings = settings

            # Check if background music settings changed
            new_bgm_enabled = getattr(settings, 'bgm_enabled', False)
            new_bgm_style = getattr(settings, 'bgm_style', 'calm')
            new_bgm_volume = getattr(settings, 'bgm_volume', 0.15)

            bgm_changed = (old_bgm_enabled != new_bgm_enabled or
                          old_bgm_style != new_bgm_style or
                          abs(old_bgm_volume - new_bgm_volume) > 0.01)

            # Restart background music if settings changed
            if bgm_changed:
                logger.info("Background music settings changed, restarting...")
                self._restart_background_music()

            # If was running, keep it running
            if was_running and not self.running:
                self.start_preview()

            logger.info("Settings updated and applied immediately")
        else:
            logger.info("Settings updated (will apply on initialization)")

    def _restart_background_music(self):
        """Restart background music with new settings."""
        try:
            # Stop current music
            pygame.mixer.music.stop()

            # Clean up old temp file
            if hasattr(self, 'bgm_temp_file') and self.bgm_temp_file:
                try:
                    import os
                    os.unlink(self.bgm_temp_file.name)
                except:
                    pass

            # Generate new music if enabled
            if getattr(self.settings, 'bgm_enabled', False):
                try:
                    from src.audio.background_music import BackgroundMusicGenerator
                    import scipy.io.wavfile as wavfile
                    import tempfile

                    logger.info("Generating new background music...")
                    bgm_gen = BackgroundMusicGenerator(
                        duration=60.0,
                        sample_rate=44100
                    )
                    bgm_style = getattr(self.settings, 'bgm_style', 'calm')
                    bgm_audio = bgm_gen.generate(style=bgm_style)

                    # Save to temp file
                    self.bgm_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                    bgm_volume = getattr(self.settings, 'bgm_volume', 0.15)

                    # Scale volume
                    bgm_audio_scaled = (bgm_audio * bgm_volume * 32767).astype(np.int16)
                    wavfile.write(self.bgm_temp_file.name, 44100, bgm_audio_scaled)
                    self.bgm_temp_file.close()

                    # Load and play
                    pygame.mixer.music.load(self.bgm_temp_file.name)
                    pygame.mixer.music.play(loops=-1)
                    logger.info("Background music restarted successfully")

                except Exception as bgm_err:
                    logger.warning(f"Failed to restart background music: {bgm_err}")
            else:
                logger.info("Background music disabled")
                self.bgm_temp_file = None

        except Exception as e:
            logger.warning(f"Error restarting background music: {e}")

    def cleanup(self):
        """Clean up resources."""
        self.pause_preview()

        if self.audio_mixer:
            self.audio_mixer.cleanup()

        if self.initialized:
            pygame.quit()



