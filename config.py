"""
Configuration and FFmpeg detection for Windows 11.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration and environment detection."""

    # Project paths
    ROOT_DIR = Path(__file__).parent
    OUTPUT_DIR = ROOT_DIR / "output"
    PRESETS_DIR = ROOT_DIR / "presets"
    LOG_FILE = OUTPUT_DIR / "app.log"

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    @staticmethod
    def detect_ffmpeg() -> Optional[str]:
        """
        Detect FFmpeg on Windows 11.
        Returns the path to ffmpeg.exe or None if not found.
        """
        # Check common locations
        candidates = [
            # System PATH
            shutil.which("ffmpeg"),
            # Common install locations
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            # User local
            Path.home() / "ffmpeg" / "bin" / "ffmpeg.exe",
        ]

        for candidate in candidates:
            if candidate and Path(candidate).exists():
                try:
                    # Verify it works
                    result = subprocess.run(
                        [str(candidate), "-version"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return str(candidate)
                except Exception:
                    continue

        return None

    @staticmethod
    def get_ffmpeg_install_instructions() -> str:
        """Get Windows 11 FFmpeg installation instructions."""
        return """
FFmpeg Installation Instructions for Windows 11:

Option 1: Using winget (Recommended)
1. Open PowerShell or Command Prompt
2. Run: winget install ffmpeg
3. Restart this application

Option 2: Manual Installation
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract the archive to C:\\ffmpeg
3. Add C:\\ffmpeg\\bin to your system PATH, or
4. Set custom FFmpeg path in Settings

Option 3: Using Chocolatey
1. Install Chocolatey from https://chocolatey.org/
2. Run: choco install ffmpeg
3. Restart this application

After installation, restart this application.
"""

    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return sys.platform.startswith('win')


# Global config instance
config = Config()

