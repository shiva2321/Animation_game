"""Setup script for installing the application"""

import os
import sys
import subprocess
from pathlib import Path


def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False


def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = ["output", "config", "assets", "assets/sounds", "assets/presets"]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created {directory}")


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\nChecking FFmpeg installation...")
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg not found (optional)")
        print("  Install from: https://ffmpeg.org/download.html")
        print("  Without FFmpeg, videos will export without audio")
        return False


def run_tests():
    """Run test suite"""
    print("\nRunning tests...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Could not run tests: {e}")
        return False


def main():
    """Main setup function"""
    print("=" * 50)
    print("Particle Collision Video Generator - Setup")
    print("=" * 50)

    # Create directories
    create_directories()

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Check FFmpeg
    check_ffmpeg()

    # Optional: Run tests
    run_tests_prompt = input("\nRun tests? (y/n): ").lower()
    if run_tests_prompt == 'y':
        run_tests()

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nTo start the application, run:")
    print("  python main.py")


if __name__ == "__main__":
    main()

