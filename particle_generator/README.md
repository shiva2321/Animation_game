
# Advanced Particle Collision Video Generator

This is a production-ready desktop application built with Python and PyQt5 for generating high-quality videos of particle collisions. It features a stable physics engine, a high-performance rendering preview, harmonic audio synthesis, and a responsive interactive dashboard.

![Screenshot (Placeholder)](placeholder.png)

## Features

- **Deterministic Physics**: Reproducible simulations using a seed.
- **Stable Engine**: Semi-implicit Euler integration with substeps to prevent tunneling and ensure stability.
- **Advanced Forces**: Includes gravity, attractors, vortex, drag, and Brownian motion.
- **High-Performance Preview**: 60fps live preview powered by Pygame, running in a non-blocking Qt widget.
- **Asynchronous Export**: Video generation runs in a background thread, never freezing the UI, with progress updates and cancellation support.
- **Harmonic Audio**: Event-driven audio engine synthesizes musical notes and soundscapes based on simulation events.
- **Rich Visuals**: Features particle trails, glow effects, and event-driven ripples, with configurable color schemes.
- **Preset System**: Save and load complete simulation settings as JSON files.

## Tech Stack

- **UI**: PyQt5 (Dark Theme)
- **Preview Graphics**: Pygame
- **Audio Synthesis**: NumPy + Pydub
- **Video Export**: MoviePy (FFmpeg backend)
- **Presets**: JSON
- **Math/Arrays**: NumPy

## Requirements

- Python 3.10+
- FFmpeg

## Installation on Windows 11

1.  **Install Python**:
    - Download and install Python from the [official website](https://www.python.org/).
    - Ensure you check "Add Python to PATH" during installation.

2.  **Install FFmpeg (Required for Video Export)**:
    - The easiest method is to use the `winget` package manager in a Command Prompt or PowerShell:
      ```sh
      winget install -e --id Gyan.FFmpeg
      ```
    - Alternatively, you can [download a build from gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract it, and add the `bin` folder to your system's PATH environment variable.

3.  **Clone the Repository**:
    ```sh
    git clone https://github.com/your-repo/particle_generator.git
    cd particle_generator
    ```

4.  **Create a Virtual Environment (Recommended)**:
    ```sh
    python -m venv venv
    .\venv\Scripts\activate
    ```

5.  **Install Python Dependencies**:
    - Install the required libraries using the `requirements.txt` file:
      ```sh
      pip install -r requirements.txt
      ```

## How to Run

With your virtual environment activated, run the `main.py` script:

```sh
python main.py
```

The application will first check for FFmpeg and then launch the main dashboard.

## Using the Application

1.  **Live Preview**:
    - Click **Play** to start the simulation in the central preview panel.
    - Click **Pause** to freeze the simulation.
    - Click **Reset** to restart the simulation with the current settings.

2.  **Adjusting Settings**:
    - Use the controls in the left-hand **Physics**, **Visuals**, and **Audio** tabs to modify the simulation in real-time.
    - Click **Show Advanced** to reveal more detailed parameters for fine-tuning.

3.  **Presets**:
    - Click **Load Preset** to load a `.json` file containing simulation settings. Three sample presets (`cosmic`, `ocean`, `neon`) are included in the `presets/` directory.
    - Click **Save Preset** to save your current configuration to a `.json` file.

4.  **Exporting a Video**:
    - In the right-hand **Export** panel, select your desired resolution, frame rate, and quality.
    - Click **Generate Video**. The export will begin in the background.
    - You can monitor the progress bar and log. Click **Cancel Export** at any time to stop the process.
    - Once complete, a confirmation message will show the location of the final `.mp4` video file in the `output/` directory.
