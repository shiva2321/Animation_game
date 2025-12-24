"""Export panel widgets for PyQt5"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QPushButton, QProgressBar, QGroupBox, QSpinBox, QTextEdit,
    QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from src.video_exporter import VideoExporter


class ExportThread(QThread):
    """Thread for video export to prevent UI freezing"""

    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.exporter = VideoExporter()

    def run(self):
        """Run video export"""
        try:
            def progress_callback(current, total, status="Rendering"):
                self.progress.emit(current, total, status)

            output_path = self.exporter.export_video(self.config, progress_callback)
            self.finished.emit(output_path)
        except Exception as e:
            self.error.emit(str(e))


class ExportPanel(QGroupBox):
    """Control panel for video export"""

    export_started = pyqtSignal()
    export_finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("Video Export", parent)
        self.config = None
        self.export_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()

        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (seconds):"))
        self.duration_slider = QSlider(Qt.Horizontal)
        self.duration_slider.setRange(30, 300)
        self.duration_slider.setValue(90)
        self.duration_slider.setTickInterval(10)
        self.duration_slider.setTickPosition(QSlider.TicksBelow)
        duration_layout.addWidget(self.duration_slider)
        self.duration_label = QLabel("90")
        duration_layout.addWidget(self.duration_label)
        layout.addLayout(duration_layout)
        self.duration_slider.valueChanged.connect(
            lambda: self.duration_label.setText(str(self.duration_slider.value()))
        )

        # Resolution
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Resolution:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["720p", "1080p", "4K"])
        self.resolution_combo.setCurrentText("1080p")
        res_layout.addWidget(self.resolution_combo)
        layout.addLayout(res_layout)

        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30", "60"])
        self.fps_combo.setCurrentText("60")
        fps_layout.addWidget(self.fps_combo)
        layout.addLayout(fps_layout)

        # Quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(50, 100)
        self.quality_slider.setValue(90)
        self.quality_slider.setTickInterval(5)
        self.quality_slider.setTickPosition(QSlider.TicksBelow)
        quality_layout.addWidget(self.quality_slider)
        self.quality_label = QLabel("90")
        quality_layout.addWidget(self.quality_label)
        layout.addLayout(quality_layout)
        self.quality_slider.valueChanged.connect(
            lambda: self.quality_label.setText(str(self.quality_slider.value()))
        )

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status text
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        layout.addWidget(self.status_text)

        # Export button
        self.export_button = QPushButton("Generate Video")
        self.export_button.clicked.connect(self.start_export)
        layout.addWidget(self.export_button)

        # Preset management
        preset_group = QGroupBox("Preset Management")
        preset_layout = QVBoxLayout()

        # Save preset button
        save_preset_layout = QHBoxLayout()
        save_preset_layout.addWidget(QLabel("Preset Name:"))
        from PyQt5.QtWidgets import QLineEdit
        self.preset_name_input = QLineEdit()
        save_preset_layout.addWidget(self.preset_name_input)
        self.save_preset_button = QPushButton("Save Current Settings")
        self.save_preset_button.clicked.connect(self.save_preset)
        save_preset_layout.addWidget(self.save_preset_button)
        preset_layout.addLayout(save_preset_layout)

        # Load preset dropdown
        load_preset_layout = QHBoxLayout()
        load_preset_layout.addWidget(QLabel("Load Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.currentTextChanged.connect(self.on_preset_selected)
        load_preset_layout.addWidget(self.preset_combo)

        self.delete_preset_button = QPushButton("Delete")
        self.delete_preset_button.clicked.connect(self.delete_preset)
        load_preset_layout.addWidget(self.delete_preset_button)
        preset_layout.addLayout(load_preset_layout)

        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)

        # Reset button
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def set_config(self, config):
        """Set configuration manager"""
        self.config = config
        self.load_export_settings()
        self.refresh_presets()

    def load_export_settings(self):
        """Load export settings from config"""
        if not self.config:
            return

        export_settings = self.config.get("export_settings")

        duration = export_settings.get("duration", 90)
        self.duration_slider.setValue(duration)

        resolution = export_settings.get("resolution", "1080p")
        index = self.resolution_combo.findText(resolution)
        if index >= 0:
            self.resolution_combo.setCurrentIndex(index)

        fps = export_settings.get("fps", 60)
        index = self.fps_combo.findText(str(fps))
        if index >= 0:
            self.fps_combo.setCurrentIndex(index)

        quality = export_settings.get("quality", 90)
        self.quality_slider.setValue(quality)

    def save_export_settings(self):
        """Save export settings to config"""
        if not self.config:
            return

        self.config.set("export_settings", "duration", value=self.duration_slider.value())
        self.config.set("export_settings", "resolution", value=self.resolution_combo.currentText())
        self.config.set("export_settings", "fps", value=int(self.fps_combo.currentText()))
        self.config.set("export_settings", "quality", value=self.quality_slider.value())
        self.config.save_config()

    def start_export(self):
        """Start video export"""
        if not self.config:
            QMessageBox.warning(self, "Error", "Configuration not set")
            return

        if self.export_thread and self.export_thread.isRunning():
            QMessageBox.warning(self, "Warning", "Export already in progress")
            return

        self.save_export_settings()

        self.export_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_text.setText("Starting export...\n")

        self.export_thread = ExportThread(self.config)
        self.export_thread.progress.connect(self.on_progress)
        self.export_thread.finished.connect(self.on_export_finished)
        self.export_thread.error.connect(self.on_export_error)
        self.export_thread.start()

        self.export_started.emit()

    @pyqtSlot(int, int, str)
    def on_progress(self, current, total, status):
        """Update progress"""
        progress_percent = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(progress_percent)

        # Append status to text
        text = self.status_text.toPlainText()
        if "\n" in status or status not in text:
            self.status_text.append(f"{status}: {current}/{total}")

    @pyqtSlot(str)
    def on_export_finished(self, output_path):
        """Export finished"""
        self.export_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_text.append(f"\nExport completed!\nSaved to: {output_path}")
        self.export_finished.emit(output_path)

        # Ask if user wants to open the video
        reply = QMessageBox.question(
            self, "Export Complete",
            f"Video saved to:\n{output_path}\n\nOpen file location?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            import subprocess
            try:
                subprocess.Popen(f'explorer /select,"{output_path}"')
            except:
                pass

    @pyqtSlot(str)
    def on_export_error(self, error_msg):
        """Export error"""
        self.export_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_text.append(f"\nError: {error_msg}")
        QMessageBox.critical(self, "Export Error", f"Export failed:\n{error_msg}")

    def save_preset(self):
        """Save current settings as preset"""
        preset_name = self.preset_name_input.text().strip()
        if not preset_name:
            QMessageBox.warning(self, "Warning", "Please enter a preset name")
            return

        if self.config:
            self.config.save_preset(preset_name)
            QMessageBox.information(self, "Success", f"Preset '{preset_name}' saved")
            self.preset_name_input.clear()
            self.refresh_presets()

    def refresh_presets(self):
        """Refresh preset list"""
        if not self.config:
            return

        current_text = self.preset_combo.currentText()
        self.preset_combo.clear()

        presets = self.config.list_presets()
        self.preset_combo.addItems(presets)

        # Try to restore previous selection
        if current_text in presets:
            index = self.preset_combo.findText(current_text)
            self.preset_combo.setCurrentIndex(index)

    def on_preset_selected(self, preset_name):
        """Load selected preset"""
        if not self.config or not preset_name:
            return

        if self.config.load_preset(preset_name):
            self.load_export_settings()

    def delete_preset(self):
        """Delete current preset"""
        preset_name = self.preset_combo.currentText()
        if not preset_name:
            QMessageBox.warning(self, "Warning", "No preset selected")
            return

        if self.config:
            self.config.delete_preset(preset_name)
            QMessageBox.information(self, "Success", f"Preset '{preset_name}' deleted")
            self.refresh_presets()

    def reset_to_defaults(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes and self.config:
            self.config.reset_to_defaults()
            self.load_export_settings()

