# QUICK START GUIDE

## Launch the Application

```bash
python main.py
```

That's it! The dashboard opens immediately.

---

## Basic Usage

1. **Select a color theme** (left panel)
   - Ocean, Sunset, Forest, Pastel, or Neon

2. **Click Play** (center)
   - Animation starts with 2 particles

3. **Particles begin falling**
   - Gravity pulls them down
   - They bounce off boundaries
   - Collisions create new particles
   - Soothing sounds play

4. **Adjust settings anytime**
   - Speed slider
   - Max objects
   - Boundary type
   - Object shape

5. **Click Apply New Settings** to restart with new config

6. **Particles calm down** automatically when max reached

---

## Key Controls

| Button | Function |
|--------|----------|
| Play | Start animation |
| Pause | Pause/resume |
| Apply New Settings | Restart with current settings |
| Reset | Clear everything |
| Save as Preset | Save configuration |
| Reset to Default | Restore defaults |

---

## Main Settings

**Boundary Type**
- Circle - smooth, curved
- Square - angular, contained
- Triangle - geometric, challenging

**Object Shape**
- Sphere - classic, smooth
- Cube - angular, modern
- Star - artistic, dynamic
- Triangle - geometric, unique

**Color Schemes**
- Ocean - cool, calming
- Sunset - warm, vibrant
- Forest - natural, earthy
- Pastel - soft, gentle
- Neon - bright, energetic

**Particle Controls**
- Max Objects: How many particles (5-200)
- Size Range: Particle size (5-15 px)
- Speed Range: Movement speed (5-20 px/s)

**Audio Controls**
- Master Volume: Overall volume
- Collision Tone: Sound on collision
- Bounce Tone: Sound on bounce

---

## Tips for Best Results

### For Meditation
- Max Objects: 50
- Speed: 5/10
- Calm-down: 45 seconds
- Theme: Ocean or Pastel

### For Energy
- Max Objects: 150
- Speed: 8/10
- Calm-down: 15 seconds
- Theme: Neon or Sunset

### For Art
- Max Objects: 80
- Speed: 6/10
- Calm-down: 30 seconds
- Theme: Forest or Sunset
- Boundary: Triangle

---

## What You'll See

✓ Particles fall due to gravity
✓ They bounce off boundaries realistically
✓ Collisions create new particles
✓ Speed gradually increases
✓ Smooth, 60 FPS animation
✓ Beautiful gradient background
✓ Thick, visible boundaries
✓ Color-coordinated visuals

---

## What You'll Hear

✓ Soothing tones on collisions
✓ Gentle sounds on bounces
✓ Smooth, calming audio
✓ Background ambient music
✓ No harsh or annoying sounds
✓ Smooth fade-outs
✓ Harmonic pentatonic scale

---

## Physics Behavior

**Objects**
- Start with gravity pulling down
- Bounce off walls/boundaries
- Create new objects on collision
- Speed increases over time
- Accelerate due to gravity

**At Maximum**
- No new objects spawn
- Existing objects calm down
- Movement gradually reduces
- Objects gather at bottom
- Smooth, peaceful finale

---

## Troubleshooting

**Q: Nothing is happening**
A: Click Play button (it should say "Pause")

**Q: Objects moving very slowly**
A: Increase Speed slider to 8-10

**Q: No sounds playing**
A: Check Master Volume slider, Mute checkbox

**Q: Can't see boundary**
A: Try different color theme

**Q: Objects escaping**
A: This is fixed! But try smaller Max Objects

---

## Settings Examples

### Configuration 1: Gentle Meditation
```
Boundary: Circle
Shape: Sphere
Color: Pastel
Max: 40
Speed: 4/10
Calm-down: 60 sec
```

### Configuration 2: Dynamic Energy
```
Boundary: Square
Shape: Cube
Color: Neon
Max: 150
Speed: 8/10
Calm-down: 15 sec
```

### Configuration 3: Artistic Chaos
```
Boundary: Triangle
Shape: Star
Color: Sunset
Max: 100
Speed: 7/10
Calm-down: 30 sec
```

---

## Advanced Features

### Save Your Settings
1. Configure everything as desired
2. Click "Save as Preset"
3. Enter a name (e.g., "My Meditation")
4. Click OK

### Load Saved Settings
- Settings load automatically next time
- Or click "Reset to Default" to restore

### Adjust Calm-Down
1. Left side: "Calm down after (sec)" - when slowdown starts
2. Left side: "Duration (sec)" - how long slowdown takes

---

## System Info

- **Target FPS**: 60 (usually 58-60)
- **Max Particles**: 200+ at 60 FPS
- **Memory**: ~250 MB typical
- **Audio Quality**: 44.1 kHz, CD quality
- **Display**: 1400x900 recommended

---

## Files & Structure

```
main.py              ← Run this file
src/
├── engine_3d.py     ← Physics simulation
├── audio_enhanced.py ← Sound synthesis
├── colors_enhanced.py ← Themes and gradients
└── ui/
    ├── enhanced_preview.py ← Visualization
    └── enhanced_dashboard.py ← Control panel
```

---

## That's All!

The application is ready to use immediately.

```bash
python main.py
```

Enjoy the mesmerizing particle collisions! ✨

