
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout,
    QComboBox, QPushButton, QProgressBar, QTextEdit, QLabel
)

from ..core.settings import Settings

class ExportWidget(QWidget):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        # --- Layout ---
        main_layout = QVBoxLayout(self)
        group_box = QGroupBox("Export Video")
        form_layout = QFormLayout()

        # --- Controls ---
        self.duration_label = QLabel(f"{self.settings.simulation.duration_sec} seconds")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["720p", "1080p", "1440p"])
        self.resolution_combo.setCurrentText(f"{self.settings.simulation.resolution[1]}p")

        self.export_fps_combo = QComboBox()
        self.export_fps_combo.addItems(["30", "60"])
        self.export_fps_combo.setCurrentText(str(self.settings.simulation.fps_export))

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["preview_low", "export_medium", "export_high"])
        self.quality_combo.setCurrentText(self.settings.simulation.quality)

        form_layout.addRow("Duration:", self.duration_label)
        form_layout.addRow("Resolution:", self.resolution_combo)
        form_layout.addRow("Export FPS:", self.export_fps_combo)
        form_layout.addRow("Quality:", self.quality_combo)

        # --- Buttons and Progress ---
        self.generate_button = QPushButton("Generate Video")
        self.cancel_button = QPushButton("Cancel Export")
        self.cancel_button.setEnabled(False) # Disabled by default

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(150)

        # --- Assembly ---
        group_box.setLayout(form_layout)
        main_layout.addWidget(group_box)
        main_layout.addWidget(self.generate_button)
        main_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(QLabel("Export Log:"))
        main_layout.addWidget(self.log_box)
        main_layout.addStretch()

        self.connect_signals()

    def connect_signals(self):
        self.resolution_combo.currentTextChanged.connect(self._update_settings)
        self.export_fps_combo.currentTextChanged.connect(self._update_settings)
        self.quality_combo.currentTextChanged.connect(self._update_settings)

    def _update_settings(self):
        """Update the main settings object when UI controls change."""
        res_map = {"720p": (1280, 720), "1080p": (1920, 1080), "1440p": (2560, 1440)}
        self.settings.simulation.resolution = res_map.get(self.resolution_combo.currentText())
        self.settings.simulation.fps_export = int(self.export_fps_combo.currentText())
        self.settings.simulation.quality = self.quality_combo.currentText()
        # Duration is not editable in this UI, but could be added
        # For now, reflect the duration from the loaded preset/settings
        self.duration_label.setText(f"{self.settings.simulation.duration_sec} seconds")

    def on_export_start(self):
        self.generate_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.log_box.clear()
        self.log_box.append("Starting export...")

    def on_export_finish(self, success: bool):
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setValue(self.progress_bar.maximum() if success else 0)

    def update_progress(self, current, total, message):
        self.log_box.append(message)
        if total > 0:
            progress_percent = int((current / total) * 100)
            self.progress_bar.setValue(progress_percent)
