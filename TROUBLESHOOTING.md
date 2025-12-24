# TROUBLESHOOTING GUIDE

## Application Crashes When Clicking Play

### Problem
The application crashes with exit code `-1073740791 (0xC0000409)` when you click the Play button.

### What We've Fixed

1. **Memory Safety**
   - Changed pygame surface to QImage conversion to use buffer copies
   - Added comprehensive error handling at every step
   - Implemented error counting to gracefully degrade instead of crash

2. **Reduced Resource Usage**
   - Lowered default particle count from 50 to 30
   - Reduced max particles from 200 to 100
   - Added frame rate throttling

3. **Better Error Handling**
   - Audio errors won't crash the app
   - Render errors are logged but caught
   - Timer is set with safe intervals

### Testing Steps

1. **Run the diagnostic version**:
   ```powershell
   cd "D:\development project\Animation_video_generator"
   .\.venv\Scripts\python.exe run_diagnostic.py
   ```

2. **Check the log**:
   - If it crashes, check `diagnostic.log` for the exact error
   - Look for the last line before crash

3. **Try with minimal settings**:
   - Load the application
   - Before clicking Play:
     - Go to Physics tab
     - Set "Initial Count" to 10
     - Set "Max Particles" to 20
     - Disable "Trails" in Visuals tab
     - Uncheck "Enable Audio" in Audio tab
   - Now try Play

### Common Causes

1. **Audio System**
   - Pygame mixer can crash on some systems
   - **Fix**: Disable audio before clicking Play

2. **Too Many Particles**
   - System gets overwhelmed
   - **Fix**: Use lower particle counts (10-30)

3. **Graphics Driver**
   - Old or incompatible graphics drivers
   - **Fix**: Update your graphics drivers

4. **Memory Corruption**
   - Pygame/Qt interaction issue
   - **Fix**: Use FastTransformation instead of SmoothTransformation

### If It Still Crashes

1. **Check System Requirements**:
   - Minimum 4GB RAM
   - Windows 11 64-bit
   - Updated graphics drivers

2. **Try Safe Mode**:
   Edit `src/core/settings.py` and change:
   ```python
   initial_count: int = 5  # Ultra-low
   max_particles: int = 10
   fps_preview: int = 30   # Lower FPS
   ```

3. **Disable Features**:
   - Set `glow_enabled = False`
   - Set `trails_enabled = False`
   - Set `audio_enabled = False`
   - Set `collision_fx_style = "none"`

4. **Check Logs**:
   ```powershell
   # Look at the detailed log
   type diagnostic.log
   
   # Look at application log
   type output\app.log
   ```

### Known Working Configuration

```python
# In settings:
initial_count = 10
max_particles = 20
spawn_rate_per_sec = 1.0
size_min = 10.0
size_max = 15.0
glow_enabled = False
trails_enabled = False
audio_enabled = False
fps_preview = 30
```

### Debug Commands

```powershell
# Test rendering only (no Qt)
.\.venv\Scripts\python.exe test_render.py

# Test with full logging
.\.venv\Scripts\python.exe run_diagnostic.py

# Check if pygame works
.\.venv\Scripts\python.exe -c "import pygame; pygame.init(); print('Pygame OK')"

# Check if PyQt6 works
.\.venv\Scripts\python.exe -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

### Report an Issue

If none of these work, please provide:
1. Contents of `diagnostic.log`
2. Your Windows version
3. GPU model
4. RAM amount
5. Python version (`python --version`)

### Emergency Workaround

If you just want to generate videos without preview:
1. Edit your preset JSON file directly
2. Use the export functionality without starting preview
3. Or use the test_render.py script to verify physics work

