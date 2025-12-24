# Development Guide

## Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Main Application                      │
│                   (src/app.py)                          │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐   ┌───▼───┐  ┌────▼────┐
   │Dashboard│   │Config │  │ Export  │
   │(UI)     │   │Manager│  │Thread  │
   └────┬────┘   └───────┘  └────────┘
        │
   ┌────┴────────────────────────┐
   │                             │
┌──▼──────┐  ┌────────┐  ┌──────▼──┐
│Preview  │  │Particle│  │ Audio  │
│Canvas   │  │Engine  │  │Engine  │
└────┬────┘  └───┬────┘  └────────┘
     │           │
  ┌──▼───────────▼──┐
  │ Renderer        │
  │ (Pygame)        │
  └────────────────┘
        │
   ┌────▼──────────┐
   │ Video Exporter│
   │ (OpenCV)      │
   └────────────────┘
```

---

## Module Responsibilities

### Core Modules

#### `particle_engine.py`
- **Class: Particle**
  - Individual particle state and behavior
  - Physics: position, velocity, acceleration
  - Collision detection with other particles
  - Collision response and new particle generation
  - Lifetime management

- **Class: ParticleEngine**
  - Manages all particles
  - Updates physics each frame
  - Handles particle spawning
  - Detects and logs collisions
  - Tracks collision events

#### `renderer.py`
- **Class: Renderer**
  - Converts particles to visual representation
  - Renders to pygame surface
  - Applies visual effects (glow, trails, collisions)
  - Handles color schemes
  - Draws boundary and HUD

#### `audio_engine.py`
- **Class: AudioGenerator**
  - Generates synthetic tones
  - Applies ADSR envelopes
  - Creates different instruments (Piano, Violin, Synth)
  - Generates percussion sounds

- **Class: AudioEngine**
  - Manages audio generation
  - Creates audio track from collision log
  - Applies effects (reverb, fade)
  - Handles volume mixing

#### `video_exporter.py`
- **Class: VideoExporter**
  - Manages video export process
  - Combines rendering and audio
  - Handles resolution and FPS conversion
  - Integrates with FFmpeg for audio

#### `utils/config.py`
- **Class: ConfigManager**
  - Manages configuration persistence
  - Handles presets
  - Validates settings

#### `utils/colors.py`
- Color scheme definitions
- Color manipulation functions
- HSV/RGB conversion utilities

#### `utils/shapes.py`
- Shape drawing functions
- All particle shape implementations
- Glow and effect rendering

### UI Modules

#### `ui/dashboard.py`
- **Class: Dashboard (QMainWindow)**
  - Main window
  - Layout management
  - Signal/slot connections
  - Settings synchronization

#### `ui/preview.py`
- **Class: PreviewCanvas (QWidget)**
  - Real-time simulation preview
  - Play/Pause/Reset controls
  - FPS monitoring
  
- **Class: CanvasWidget (QWidget)**
  - Pygame surface rendering
  - Scaling and display

#### `ui/controls.py`
- **Class: ParticleControlPanel**
  - Particle settings widgets
  
- **Class: VisualControlPanel**
  - Visual settings widgets
  
- **Class: AudioControlPanel**
  - Audio settings widgets

#### `ui/export_panel.py`
- **Class: ExportPanel**
  - Export configuration
  - Progress monitoring
  - Preset management
  
- **Class: ExportThread (QThread)**
  - Non-blocking video export
  - Progress callbacks

---

## Data Flow

### Simulation Loop

```
1. User clicks Play
   ↓
2. Timer starts (16ms interval for 60fps)
   ↓
3. ParticleEngine.update(dt)
   - Update particle velocities
   - Check boundary collisions
   - Check particle-particle collisions
   - Generate new particles from collisions
   - Remove dead particles
   ↓
4. Renderer.render(particles)
   - Apply color scheme
   - Draw particles with effects
   - Draw boundary
   ↓
5. Display on canvas
   ↓
6. Emit signals (FPS, particle count)
   ↓
7. Repeat (go to step 3)
```

### Export Process

```
1. User clicks "Generate Video"
   ↓
2. Create ExportThread
   ↓
3. Configure ParticleEngine from settings
   ↓
4. For each frame:
   a. ParticleEngine.update(dt)
   b. Renderer.render(particles)
   c. Write frame to video file
   d. Emit progress signal
   ↓
5. AudioEngine.create_collision_audio_track()
   - Generate ambient drone
   - Add collision sounds
   - Add spawn/bounce sounds
   - Mix all layers
   ↓
6. Combine video + audio with FFmpeg
   ↓
7. Save to output/ directory
   ↓
8. Emit finished signal
```

---

## Physics Implementation

### Collision Detection

**Particle-Particle**:
```python
distance = sqrt((p2.x - p1.x)^2 + (p2.y - p1.y)^2)
collision = distance < (p1.radius + p2.radius)
```

**Particle-Boundary**:
```python
distance_to_center = sqrt((p.x - center.x)^2 + (p.y - center.y)^2)
collision = distance_to_center + p.radius > boundary_radius
```

### Collision Response

**Elastic Collision**:
```python
# Normal vector from p1 to p2
nx = (p2.x - p1.x) / distance
ny = (p2.y - p1.y) / distance

# Relative velocity
dvx = p2.vx - p1.vx
dvy = p2.vy - p1.vy

# Velocity along normal
dvn = dvx * nx + dvy * ny

# Update velocities (equal mass)
p1.vx += dvn * nx * 0.5
p1.vy += dvn * ny * 0.5
p2.vx -= dvn * nx * 0.5
p2.vy -= dvn * ny * 0.5
```

**Boundary Collision**:
```python
# Reflect velocity
normal_velocity = v·n
reflected = v - 2(v·n)n
# Apply damping
reflected *= 0.95
```

---

## Audio Synthesis

### ADSR Envelope

```
Amplitude
   1.0 │     ╱‾‾‾‾╲
       │    ╱       ╲
       │   ╱         ╲
       │  ╱           ╲___
     0 │_╱_______________╲____
       │  A  D  S    R
```

- **Attack**: Fade in (10-50ms)
- **Decay**: Fall to sustain level (50-100ms)
- **Sustain**: Hold level (remaining time minus release)
- **Release**: Fade out (100-200ms)

### Sound Generation

**Piano Tone**:
- Fundamental frequency + harmonics (2x, 3x, 4x)
- ADSR: Attack 20ms, Decay 100ms, Sustain 70%, Release 150ms

**Violin Tone**:
- Fundamental + vibrato (5Hz modulation)
- Harmonics with lower amplitude
- ADSR: Attack 50ms, Decay 80ms, Sustain 80%, Release 200ms

**Synth Tone**:
- Square wave + sub-harmonic (0.5x)
- Sharp attack, quick decay
- ADSR: Attack 5ms, Decay 80ms, Sustain 60%, Release 100ms

---

## Rendering Pipeline

### Visual Effects

**Glow Effect**:
```
For each particle:
  For glow_radius from radius*1.5 down to 0:
    Draw circle with decreasing opacity
```

**Trail Effect**:
```
For each particle:
  For each previous position in trail:
    Draw line with fade based on age
```

**Collision Ripple**:
```
If collision_time < 0.3 seconds ago:
  pulse = 1 - (time_since_collision / 0.3)
  Draw expanding circle at collision point
```

**Collision Sparkle**:
```
If collision_time < 0.3 seconds ago:
  For i in 0 to pulse*5:
    Draw small circle at random angle around collision
```

---

## Testing Strategy

### Unit Tests (`tests/test_particle.py`)
- Particle creation and properties
- Position updates
- Collision detection
- Collision response
- New particle generation

### Audio Tests (`tests/test_audio.py`)
- Tone generation
- ADSR envelope application
- Instrument variations
- Audio mixing

### Export Tests (`tests/test_export.py`)
- Configuration management
- Preset save/load
- Export time estimation
- Resolution scaling

### Integration Testing
- Full simulation loop
- Video export pipeline
- UI responsiveness

---

## Performance Optimization

### Current Optimizations
1. **Collision Detection**
   - Only check nearby particles (spatial optimization available)
   - Short-circuit if velocities moving apart

2. **Rendering**
   - Cached color scheme lookup
   - Minimal surface copies
   - Per-pixel alpha for effects

3. **Audio**
   - Cached tone generation
   - Note cycling for variation
   - Efficient mixing

### Future Optimizations
1. **Spatial Partitioning**
   - Quadtree for collision detection
   - Reduce O(n²) to O(n log n)

2. **GPU Acceleration**
   - PyOpenGL for rendering
   - Compute shaders for physics

3. **Audio Streaming**
   - Generate audio on-the-fly during export
   - Avoid loading entire audio in memory

---

## Code Style & Conventions

### Naming
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants

### Documentation
- Module docstrings at top
- Class and function docstrings
- Inline comments for complex logic

### Type Hints
- Used in function signatures
- Optional but encouraged for clarity

### Testing
- Test file names: `test_*.py`
- Test class names: `Test*`
- Test method names: `test_*`

---

## Adding New Features

### Example: Add Triangle Burst Collision Effect

1. **In `renderer.py`**:
```python
def _draw_collision_effect(self, particle):
    if self.collision_effect == "TriangleBurst":
        pulse = particle.get_collision_pulse()
        if pulse > 0:
            # Draw expanding triangles
            for i in range(int(pulse * 6)):
                angle = (2 * math.pi / 6) * i
                length = particle.radius * (1 + pulse * 5)
                # Draw triangle at angle
```

2. **In `ui/controls.py`**:
```python
self.effect_combo.addItems([..., "TriangleBurst"])
```

3. **Test it**:
```python
def test_triangle_burst(self):
    self.renderer.collision_effect = "TriangleBurst"
    # Test rendering
```

### Example: Add New Color Scheme

1. **In `utils/colors.py`**:
```python
COLOR_SCHEMES["Electric Storm"] = {
    "particles": [(100, 200, 255), (255, 100, 200), ...],
    "background": (20, 10, 30),
    "boundary": (100, 200, 255),
}
```

2. **In `ui/controls.py`** (automatic via dropdown)

---

## Debugging Tips

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Collision Log
```python
for event in engine.collision_log:
    print(f"Collision at {event['time']:.2f}s: {event['type']}")
```

### Profile Performance
```python
import cProfile
cProfile.run('main()')
```

### Visual Debugging in Preview
- Watch particle trails (shows velocity)
- Watch glow effect (shows collision timing)
- Watch boundary interactions

---

## Distribution

### Creating Executable (Windows)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

### Creating DMG (macOS)
```bash
pip install py2app
py2applet --make-setup main.py
python setup.py py2app
```

### Creating AppImage (Linux)
```bash
pip install appimage-builder
appimage-builder --skip-test
```

---

## Common Issues & Solutions

### Issue: Particles teleport
**Solution**: Check dt parameter in physics updates

### Issue: Memory leak
**Solution**: Ensure dead particles are removed from list

### Issue: Audio synchronization
**Solution**: Use frame count * frame_time for audio timing

### Issue: Low FPS export
**Solution**: Pre-calculate particle positions, render in background thread

---

## Resources

- **Physics**: https://en.wikipedia.org/wiki/Elastic_collision
- **Audio**: https://en.wikipedia.org/wiki/Envelope_(music)
- **PyQt5**: https://doc.qt.io/qt-5/
- **Pygame**: https://www.pygame.org/docs/

---

This guide covers the essential architecture and implementation details. For specific questions, refer to inline code comments and docstrings.

