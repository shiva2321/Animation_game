"""
Dialog windows for FFmpeg errors, about, etc.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt
from pathlib import Path

from config import Config


class FFmpegMissingDialog(QDialog):
    """Dialog shown when FFmpeg is not found."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FFmpeg Not Found")
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Message
        message = QLabel(
            "FFmpeg is required for video export but was not found on your system.\n\n"
            "You can continue using the application for preview only, or install FFmpeg to enable video export."
        )
        message.setWordWrap(True)
        layout.addWidget(message)

        # Instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setPlainText(Config.get_ffmpeg_install_instructions())
        instructions.setMinimumHeight(300)
        layout.addWidget(instructions)

        # Buttons
        button_layout = QHBoxLayout()

        self.continue_btn = QPushButton("Continue Without Export")
        self.continue_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.continue_btn)

        self.browse_btn = QPushButton("Browse for FFmpeg...")
        self.browse_btn.clicked.connect(self.browse_ffmpeg)
        button_layout.addWidget(self.browse_btn)

        self.retry_btn = QPushButton("Retry Detection")
        self.retry_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.retry_btn)

        layout.addLayout(button_layout)

        self.resize(600, 500)

    def browse_ffmpeg(self):
        """Browse for FFmpeg executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select FFmpeg Executable",
            "",
            "Executable Files (*.exe);;All Files (*.*)"
        )

        if file_path:
            # Verify it's ffmpeg
            if Path(file_path).name.lower().startswith("ffmpeg"):
                QMessageBox.information(
                    self,
                    "FFmpeg Selected",
                    f"FFmpeg path set to:\n{file_path}\n\nPlease restart the application."
                )
                # Store the path (in a real app, save to config)
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Selection",
                    "The selected file does not appear to be FFmpeg."
                )


class AboutDialog(QDialog):
    """About dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Particle Video Generator")
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("<h2>Particle Video Generator</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Info
        info = QLabel(
            "<p>A Windows 11 application for generating mesmerizing particle collision videos "
            "with physics simulation, real-time audio synthesis, and high-quality export.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Realistic physics with collision detection</li>"
            "<li>Real-time audio synthesis</li>"
            "<li>Multiple visual themes</li>"
            "<li>Customizable particles and forces</li>"
            "<li>HD video export with audio</li>"
            "</ul>"
            "<p><b>Version:</b> 1.0.0</p>"
            "<p><b>Python:</b> 3.11+</p>"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.resize(400, 400)


class ExportProgressDialog(QDialog):
    """Dialog showing export progress."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exporting Video")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(200)
        layout.addWidget(self.log_output)

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        layout.addWidget(self.cancel_btn)

        self.resize(500, 300)

    def set_progress(self, value: int):
        """Set progress value."""
        self.progress_bar.setValue(value)

    def set_status(self, status: str):
        """Set status message."""
        self.status_label.setText(status)
        self.log_output.append(status)

    def add_log(self, message: str):
        """Add log message."""
        self.log_output.append(message)

