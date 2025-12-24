# Quick Start Guide

## Particle Video Generator - Quick Start

### Installation (5 minutes)

1. **Install Python 3.11+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Check "Add to PATH" during installation

2. **Install FFmpeg**
   ```powershell
   winget install ffmpeg
   ```

3. **Install Dependencies**
   ```powershell
   cd "D:\development project\Animation_video_generator"
   pip install -r requirements.txt
   ```

### Running the Application

```powershell
python main.py
```

### First Video (2 minutes)

1. Click **▶ Play** to see the preview
2. Watch particles collide with audio
3. Click **🎬 Generate Video** (default settings)
4. Wait 2-5 minutes for export
5. Find your video in `output/` folder

### Tips

- Start with presets: **Cosmic**, **Ocean**, or **Neon**
- For fast tests, set duration to 10-30 seconds
- Lower particle count (< 100) for smooth preview
- Use 720p resolution for faster exports

### Common Issues

**No audio?**
- Check "Enable Audio" checkbox
- Adjust master volume

**Slow preview?**
- Reduce particle count
- Disable trails
- Lower preview FPS

**Export fails?**
- Check FFmpeg is installed: `ffmpeg -version`
- Ensure 1GB+ free disk space
- Try shorter duration

### Next Steps

- Explore physics controls (gravity, vortex, forces)
- Try different visual schemes
- Experiment with audio instruments and scales
- Save your favorite presets

For full documentation, see [README.md](README.md)

