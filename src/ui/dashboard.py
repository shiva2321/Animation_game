"""
Main dashboard window with preview, controls, and export panel.
"""
import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QSpinBox, QComboBox,
    QFileDialog, QMessageBox, QStatusBar, QMenuBar
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction

from src.core.settings import AppSettings
from src.core.logging_utils import QtLogHandler, setup_logging
from src.ui.preview import PreviewWidget
from src.ui.controls import ControlsWidget
from src.ui.dialogs import (
    FFmpegMissingDialog, AboutDialog, ExportProgressDialog
)
from src.export.video import VideoExportWorker
from config import Config


logger = logging.getLogger(__name__)


class MainDashboard(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Particle Video Generator")

        # Settings
        self.settings = AppSettings()
        self.settings.validate_and_clamp()

        # Setup logging
        self.log_handler = QtLogHandler()
        setup_logging(Config.LOG_FILE, self.log_handler)

        # Check FFmpeg
        self.ffmpeg_available = self.check_ffmpeg()

        # Export worker
        self.export_worker = None
        self.export_dialog = None

        # Setup UI
        self.setup_ui()
        self.apply_dark_theme()

        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(500)

        logger.info("Application started")

    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        ffmpeg_path = Config.detect_ffmpeg()

        if ffmpeg_path:
            logger.info(f"FFmpeg found at: {ffmpeg_path}")
            self.settings.ffmpeg_path = ffmpeg_path
            return True
        else:
            logger.warning("FFmpeg not found")
            # Show dialog
            dialog = FFmpegMissingDialog(self)
            dialog.exec()
            return False

    def setup_ui(self):
        """Setup the main UI."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout: 3 columns
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # Left: Controls
        self.controls_widget = ControlsWidget(self.settings)
        self.controls_widget.settings_changed.connect(self.on_settings_changed)
        self.controls_widget.setMaximumWidth(350)
        main_layout.addWidget(self.controls_widget)

        # Center: Preview
        center_widget = QWidget()
        center_layout = QVBoxLayout()
        center_widget.setLayout(center_layout)

        # Preview controls
        preview_controls = QHBoxLayout()

        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.on_play)
        preview_controls.addWidget(self.play_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.clicked.connect(self.on_pause)
        self.pause_btn.setEnabled(False)
        preview_controls.addWidget(self.pause_btn)

        self.reset_btn = QPushButton("⟲ Reset")
        self.reset_btn.clicked.connect(self.on_reset)
        preview_controls.addWidget(self.reset_btn)

        preview_controls.addStretch()

        center_layout.addLayout(preview_controls)

        # Preview widget
        self.preview_widget = PreviewWidget(self.settings)
        center_layout.addWidget(self.preview_widget, 1)

        # Stats label
        self.stats_label = QLabel("FPS: 0 | Particles: 0 | Time: 0.0s")
        center_layout.addWidget(self.stats_label)

        main_layout.addWidget(center_widget, 1)

        # Right: Export panel
        export_panel = self.create_export_panel()
        export_panel.setMaximumWidth(300)
        main_layout.addWidget(export_panel)

        # Menu bar
        self.create_menu_bar()

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # Connect log handler to status
        self.log_handler.log_signal.connect(self.on_log_message)

        # Window size
        self.resize(1600, 900)

    def create_export_panel(self):
        """Create the export panel."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Title
        title = QLabel("<h3>Export</h3>")
        layout.addWidget(title)

        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (s):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setMinimum(10)
        self.duration_spin.setMaximum(300)
        self.duration_spin.setValue(self.settings.duration_sec)
        self.duration_spin.valueChanged.connect(
            lambda v: setattr(self.settings, 'duration_sec', v)
        )
        duration_layout.addWidget(self.duration_spin)
        layout.addLayout(duration_layout)

        # Resolution
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Resolution:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "1280x720",
            "1920x1080",
            "2560x1440"
        ])
        self.resolution_combo.setCurrentText("1920x1080")
        self.resolution_combo.currentTextChanged.connect(self.on_resolution_changed)
        resolution_layout.addWidget(self.resolution_combo)
        layout.addLayout(resolution_layout)

        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30", "60"])
        self.fps_combo.setCurrentText(str(self.settings.fps_export))
        self.fps_combo.currentTextChanged.connect(
            lambda v: setattr(self.settings, 'fps_export', int(v))
        )
        fps_layout.addWidget(self.fps_combo)
        layout.addLayout(fps_layout)

        # Quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "preview_low",
            "export_balanced",
            "export_high"
        ])
        self.quality_combo.setCurrentText(self.settings.quality)
        self.quality_combo.currentTextChanged.connect(
            lambda v: setattr(self.settings, 'quality', v)
        )
        quality_layout.addWidget(self.quality_combo)
        layout.addLayout(quality_layout)

        # Generate button
        self.generate_btn = QPushButton("🎬 Generate Video")
        self.generate_btn.clicked.connect(self.on_generate)
        self.generate_btn.setEnabled(self.ffmpeg_available)
        if not self.ffmpeg_available:
            self.generate_btn.setToolTip("FFmpeg is required for export")
        layout.addWidget(self.generate_btn)

        layout.addSpacing(20)

        # Presets
        presets_group = QGroupBox("Presets")
        presets_layout = QVBoxLayout()
        presets_group.setLayout(presets_layout)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["cosmic", "ocean", "neon"])
        presets_layout.addWidget(self.preset_combo)

        load_preset_btn = QPushButton("Load Preset")
        load_preset_btn.clicked.connect(self.on_load_preset)
        presets_layout.addWidget(load_preset_btn)

        save_preset_btn = QPushButton("Save Preset")
        save_preset_btn.clicked.connect(self.on_save_preset)
        presets_layout.addWidget(save_preset_btn)

        layout.addWidget(presets_group)

        layout.addStretch()

        return widget

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        save_action = QAction("Save Settings", self)
        save_action.triggered.connect(self.on_save_settings)
        file_menu.addAction(save_action)

        load_action = QAction("Load Settings", self)
        load_action.triggered.connect(self.on_load_settings)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        quick_render_action = QAction("Quick Render (30s)", self)
        quick_render_action.triggered.connect(self.on_quick_render)
        tools_menu.addAction(quick_render_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        ffmpeg_help_action = QAction("FFmpeg Setup Instructions", self)
        ffmpeg_help_action.triggered.connect(self.on_ffmpeg_help)
        help_menu.addAction(ffmpeg_help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def apply_dark_theme(self):
        """Apply dark theme stylesheet."""
        style = """
        QMainWindow, QWidget {
            background-color: #1a1a2e;
            color: #eee;
        }
        QGroupBox {
            border: 1px solid #0f3460;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            color: #e94560;
        }
        QPushButton {
            background-color: #0f3460;
            border: 1px solid #e94560;
            border-radius: 3px;
            padding: 5px;
            color: #eee;
        }
        QPushButton:hover {
            background-color: #16213e;
        }
        QPushButton:pressed {
            background-color: #e94560;
        }
        QPushButton:disabled {
            background-color: #0a0a1a;
            border-color: #333;
            color: #666;
        }
        QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #16213e;
            border: 1px solid #0f3460;
            border-radius: 3px;
            padding: 3px;
            color: #eee;
        }
        QSlider::groove:horizontal {
            background: #0f3460;
            height: 6px;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #e94560;
            width: 14px;
            margin: -4px 0;
            border-radius: 7px;
        }
        QTabWidget::pane {
            border: 1px solid #0f3460;
        }
        QTabBar::tab {
            background-color: #0f3460;
            border: 1px solid #0f3460;
            padding: 5px 10px;
            color: #eee;
        }
        QTabBar::tab:selected {
            background-color: #e94560;
        }
        QScrollArea {
            border: none;
        }
        QStatusBar {
            background-color: #0f3460;
            color: #eee;
        }
        """
        self.setStyleSheet(style)

    def on_play(self):
        """Handle play button."""
        self.preview_widget.start_preview()
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)

    def on_pause(self):
        """Handle pause button."""
        self.preview_widget.pause_preview()
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)

    def on_reset(self):
        """Handle reset button."""
        self.preview_widget.reset_preview()

    def on_settings_changed(self):
        """Handle settings change."""
        self.preview_widget.update_settings(self.settings)

    def on_resolution_changed(self, text):
        """Handle resolution change."""
        width, height = map(int, text.split('x'))
        self.settings.resolution = (width, height)

    def on_generate(self):
        """Handle generate video button."""
        if self.export_worker and self.export_worker.isRunning():
            QMessageBox.warning(self, "Export Running", "An export is already in progress.")
            return

        # Pause preview
        if self.preview_widget.running:
            self.on_pause()

        # Create export dialog
        self.export_dialog = ExportProgressDialog(self)
        self.export_dialog.cancel_btn.clicked.connect(self.on_cancel_export)

        # Create worker
        self.export_worker = VideoExportWorker(self.settings, Config.OUTPUT_DIR)
        self.export_worker.progress.connect(self.export_dialog.set_progress)
        self.export_worker.status.connect(self.export_dialog.set_status)
        self.export_worker.finished.connect(self.on_export_finished)
        self.export_worker.error.connect(self.on_export_error)

        # Start export
        self.export_worker.start()
        self.export_dialog.exec()

    def on_cancel_export(self):
        """Cancel export."""
        if self.export_worker:
            self.export_worker.cancel()

    def on_export_finished(self, output_path):
        """Handle export finished."""
        if self.export_dialog:
            self.export_dialog.accept()

        QMessageBox.information(
            self,
            "Export Complete",
            f"Video exported successfully!\n\n{output_path}"
        )

    def on_export_error(self, error_msg):
        """Handle export error."""
        if self.export_dialog:
            self.export_dialog.reject()

        QMessageBox.critical(self, "Export Error", error_msg)

    def on_quick_render(self):
        """Quick 30-second test render."""
        self.settings.duration_sec = 30
        self.duration_spin.setValue(30)
        self.on_generate()

    def on_load_preset(self):
        """Load a preset."""
        preset_name = self.preset_combo.currentText()
        preset_path = Config.PRESETS_DIR / f"{preset_name}.json"

        if preset_path.exists():
            try:
                self.settings = AppSettings.load_json(preset_path)
                self.settings.validate_and_clamp()

                # Update controls widget UI
                if hasattr(self, 'controls_widget'):
                    self.controls_widget.settings = self.settings
                    self.controls_widget.update_from_settings(self.settings)

                # Update preview with new settings (will restart background music)
                self.preview_widget.update_settings(self.settings)

                QMessageBox.information(self, "Preset Loaded", f"Loaded and applied preset: {preset_name}")
                logger.info(f"Preset '{preset_name}' loaded and applied")

            except Exception as e:
                logger.exception("Failed to load preset")
                QMessageBox.warning(self, "Load Error", f"Failed to load preset: {e}")

    def on_save_preset(self):
        """Save current settings as preset."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Preset",
            str(Config.PRESETS_DIR),
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                self.settings.save_json(Path(file_path))
                QMessageBox.information(self, "Preset Saved", "Preset saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Save Error", f"Failed to save preset: {e}")

    def on_save_settings(self):
        """Save settings to file."""
        self.on_save_preset()

    def on_load_settings(self):
        """Load settings from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Settings",
            str(Config.PRESETS_DIR),
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                self.settings = AppSettings.load_json(Path(file_path))
                self.settings.validate_and_clamp()

                # Update controls widget UI
                if hasattr(self, 'controls_widget'):
                    self.controls_widget.settings = self.settings
                    self.controls_widget.update_from_settings(self.settings)

                # Update preview with new settings
                self.preview_widget.update_settings(self.settings)

                QMessageBox.information(self, "Settings Loaded", "Settings loaded and applied successfully!")
                logger.info(f"Settings loaded from {file_path}")

            except Exception as e:
                logger.exception("Failed to load settings")
                QMessageBox.warning(self, "Load Error", f"Failed to load settings: {e}")

    def on_ffmpeg_help(self):
        """Show FFmpeg help."""
        msg = QMessageBox(self)
        msg.setWindowTitle("FFmpeg Setup Instructions")
        msg.setText(Config.get_ffmpeg_install_instructions())
        msg.exec()

    def on_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def update_status(self):
        """Update status bar with stats."""
        stats = self.preview_widget.get_stats()

        # Build status message
        status_parts = [
            f"FPS: {stats.get('fps', 0)}",
            f"Objects: {stats.get('particle_count', 0)}/{self.settings.max_particles}",
            f"Time: {stats.get('time', 0.0):.1f}s"
        ]

        # Add status indicators
        if stats.get('spawn_limit_reached', False):
            status_parts.append("✓ Limit Reached")
        if stats.get('is_settled', False):
            status_parts.append("✓ Settled")

        self.stats_label.setText(" | ".join(status_parts))

    def on_log_message(self, message):
        """Handle log message."""
        # Could display in a log panel or status bar
        pass

    def closeEvent(self, event):
        """Handle window close."""
        # Stop preview
        self.preview_widget.cleanup()

        # Cancel any running export
        if self.export_worker and self.export_worker.isRunning():
            self.export_worker.cancel()
            self.export_worker.wait(5000)

        event.accept()

