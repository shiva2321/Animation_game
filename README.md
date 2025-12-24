# Particle Animation Video Generator

**A professional Windows 11 application for creating mesmerizing physics-based particle collision videos with realistic 3D graphics, professional audio synthesis, and GPU acceleration.**

![Platform](https://img.shields.io/badge/platform-Windows%2011-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Key Features

- 🎨 **True 3D Graphics**: Realistic sphere shading, glass bubbles, depth effects
- 🎵 **Professional Audio**: Real instrument synthesis (Piano, Bell, Strings) + harmonic background music
- ⚡ **GPU Accelerated**: 2-3x faster rendering with hardware acceleration
- 🎮 **Intuitive UI**: Comprehensive PyQt6 interface with 6 organized tabs
- 🎬 **HD/4K Export**: Generate MP4 videos up to 4K resolution at 60 FPS
- 💾 **Save Presets**: Save and load your favorite configurations
- 🔊 **Real-time Preview**: See and hear your creation before exporting

---

## 🚀 Quick Start

### Installation

```powershell
# 1. Install Python 3.11+ (if not already installed)
python --version

# 2. Clone/download this repository
cd "D:\development project\Animation_video_generator"

# 3. Create virtual environment
python -m venv .venv

# 4. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 5. Install dependencies
pip install -r requirements.txt

# 6. Install FFmpeg (required for video export)
winget install FFmpeg
```

### Run the Application

```powershell
python main.py
```

---

## 📖 Documentation

**See [DOCUMENTATION.md](DOCUMENTATION.md) for:**
- Complete installation guide
- Feature reference
- User interface guide  
- Technical architecture
- Troubleshooting
- Advanced usage

**See [QUICKSTART.md](QUICKSTART.md) for:**
- First-time setup
- Creating your first video
- Common workflows

**See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for:**
- Common issues and fixes
- Performance optimization
- Error messages explained

---

## 🎨 What You Can Create

### Spawn-on-Collision Mode

The application uses a unique physics mode:
1. **Starts with 2 particles** in the container
2. **Particles collide and spawn** new particles
3. **Continues until max limit** reached
4. **Gradually settles** at bottom under gravity
5. **Auto-stops** when all particles are calm

### Customization Options

- **Container Shapes**: Circle, Square, Triangle, Polygon (5-12 sides)
- **Object Types**: Spheres, Bubbles, Stars, Hexagons, Triangles, Squares
- **Visual Styles**: 7 color palettes + 3D effects + glow + trails
- **Audio**: 5 instrument types + 4 musical scales + 3 background music styles
- **Physics**: Adjustable gravity, drag, bounciness, friction

---

## 🖼️ Interface Overview

```
┌─────────────────────────────────────────────────┐
│  Particle Video Generator                       │
├────────────┬──────────────────┬─────────────────┤
│ Controls   │  Preview Area    │  Export Panel   │
│            │                  │                 │
│ • Basic    │  [Live Preview]  │  Duration: 60s  │
│ • Objects  │                  │  Resolution: HD │
│ • Appear   │  ▶ Play/Pause    │  FPS: 60        │
│ • Audio    │                  │                 │
│ • Export   │  Status Bar      │  [Generate]     │
│ • Advanced │                  │                 │
└────────────┴──────────────────┴─────────────────┘
```

---

## 🔧 System Requirements

- **OS**: Windows 11 (Windows 10 may work)
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **GPU**: Optional (enables GPU acceleration for 2-3x faster rendering)
- **Disk Space**: 500MB + space for videos

---

## 📦 Dependencies

- **PyQt6**: Modern UI framework
- **Pygame**: Graphics rendering with GPU support
- **NumPy**: Numerical computations
- **SciPy**: Audio processing
- **MoviePy**: Video export
- **FFmpeg**: Video encoding (external)

---

## 🎯 Usage Example

### Create a Cosmic-Themed Video

1. **Open app** → Basic tab
   - Container: Circle
   - Duration: 60 seconds

2. **Objects tab**
   - Initial: 2 particles
   - Max: 100 particles
   - Types: ☑ Sphere ☑ Bubble

3. **Appearance tab**
   - Palette: Cosmic
   - 3D Effects: ✓
   - Trails: ✓

4. **Audio tab**
   - Instrument: Bell
   - BGM Style: Calm

5. **Click "Apply Changes"**
6. **Click "Play"** to preview
7. **Click "Generate Video"** when satisfied

---

## 🐛 Troubleshooting

### Application won't start
```powershell
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### No background music
1. Audio tab → Check "Enable Background Music"
2. Set BGM volume to 0.3
3. Click "Apply Changes"
4. Check system volume

### Video export fails
```powershell
# Verify FFmpeg is installed
ffmpeg -version

# If not installed
winget install FFmpeg
```

### Low FPS / Choppy performance
1. Reduce max particles to <150
2. Lower resolution to 1280x720
3. Use quality preset: "Balanced"
4. Check GPU acceleration is enabled (see logs)

**For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

---

## 📝 Recent Updates

### Version 1.0 (December 23, 2025)
- ✅ Spawn-on-collision physics mode
- ✅ GPU acceleration (2-3x faster)
- ✅ Professional audio synthesis
- ✅ Background music with chord progressions
- ✅ True 3D rendering (pixel-perfect spheres)
- ✅ Comprehensive 6-tab UI
- ✅ Save/load presets
- ✅ Settings apply immediately
- ✅ Anti-clustering system

---

## 📄 License

[Specify your license here - e.g., MIT, GPL, etc.]

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📞 Support

- **Documentation**: [DOCUMENTATION.md](DOCUMENTATION.md)
- **Issues**: Check troubleshooting guide first
- **Logs**: Found in `logs/` folder

---

## 🙏 Acknowledgments

- **PyQt6** for the excellent UI framework
- **Pygame** for flexible graphics rendering
- **NumPy/SciPy** for numerical computing
- **FFmpeg** for video encoding

---

**Made with ❤️ for creating beautiful particle animations**

*Last updated: December 23, 2025*

