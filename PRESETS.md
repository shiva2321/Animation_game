## Sample Presets

Here are some example preset configurations you can use:

### 1. Ocean Dreams
```json
{
  "particle_settings": {
    "spawn_rate": 8,
    "max_particles": 150,
    "initial_particles": 20,
    "min_size": 4,
    "max_size": 12,
    "min_speed": 0.5,
    "max_speed": 3,
    "shape": "Circle"
  },
  "visual_settings": {
    "color_scheme": "Ocean Breeze",
    "boundary_style": "Glow",
    "enable_glow": true,
    "enable_trails": true,
    "trail_length": 30,
    "collision_effect": "Ripple"
  },
  "audio_settings": {
    "instrument": "Piano",
    "master_volume": 0.6,
    "collision_volume": 0.8,
    "spawn_volume": 0.4,
    "ambient_volume": 0.3,
    "enable_reverb": true
  }
}
```

### 2. Neon Burst
```json
{
  "particle_settings": {
    "spawn_rate": 15,
    "max_particles": 200,
    "initial_particles": 30,
    "min_size": 2,
    "max_size": 8,
    "min_speed": 2,
    "max_speed": 6,
    "shape": "Star"
  },
  "visual_settings": {
    "color_scheme": "Neon Nights",
    "boundary_style": "Solid",
    "enable_glow": true,
    "enable_trails": true,
    "trail_length": 15,
    "collision_effect": "Burst"
  },
  "audio_settings": {
    "instrument": "Synth",
    "master_volume": 0.7,
    "collision_volume": 0.9,
    "spawn_volume": 0.5,
    "ambient_volume": 0.2,
    "enable_reverb": false
  }
}
```

### 3. Pastel Fantasy
```json
{
  "particle_settings": {
    "spawn_rate": 4,
    "max_particles": 80,
    "initial_particles": 8,
    "min_size": 5,
    "max_size": 18,
    "min_speed": 0.5,
    "max_speed": 2,
    "shape": "Heart"
  },
  "visual_settings": {
    "color_scheme": "Pastel Dreams",
    "boundary_style": "Dashed",
    "enable_glow": true,
    "enable_trails": true,
    "trail_length": 40,
    "collision_effect": "Sparkle"
  },
  "audio_settings": {
    "instrument": "Violin",
    "master_volume": 0.5,
    "collision_volume": 0.6,
    "spawn_volume": 0.3,
    "ambient_volume": 0.4,
    "enable_reverb": true
  }
}
```

### 4. Geometric Mayhem
```json
{
  "particle_settings": {
    "spawn_rate": 10,
    "max_particles": 120,
    "initial_particles": 15,
    "min_size": 3,
    "max_size": 10,
    "min_speed": 1,
    "max_speed": 4,
    "shape": "Hexagon"
  },
  "visual_settings": {
    "color_scheme": "Forest Magic",
    "boundary_style": "Solid",
    "enable_glow": false,
    "enable_trails": true,
    "trail_length": 25,
    "collision_effect": "Sparkle"
  },
  "audio_settings": {
    "instrument": "Mixed",
    "master_volume": 0.6,
    "collision_volume": 0.7,
    "spawn_volume": 0.4,
    "ambient_volume": 0.25,
    "enable_reverb": true
  }
}
```

### 5. High Energy
```json
{
  "particle_settings": {
    "spawn_rate": 20,
    "max_particles": 200,
    "initial_particles": 40,
    "min_size": 1,
    "max_size": 6,
    "min_speed": 3,
    "max_speed": 8,
    "shape": "Circle"
  },
  "visual_settings": {
    "color_scheme": "Sunset Glow",
    "boundary_style": "Glow",
    "enable_glow": true,
    "enable_trails": false,
    "trail_length": 10,
    "collision_effect": "Burst"
  },
  "audio_settings": {
    "instrument": "Synth",
    "master_volume": 0.8,
    "collision_volume": 0.9,
    "spawn_volume": 0.6,
    "ambient_volume": 0.1,
    "enable_reverb": false
  }
}
```

### How to Use These Presets

1. **Via Dashboard**:
   - Configure settings manually using the control panels
   - Click "Save Current Settings"
   - Enter preset name (e.g., "Ocean Dreams")

2. **Via Files**:
   - Save the JSON above to `config/presets/[preset_name].json`
   - Restart the application or click refresh in preset selector
   - Select from dropdown and click Load

### Preset Export Settings

All presets above use these export defaults:
- **Duration**: 90 seconds
- **Resolution**: 1080p
- **FPS**: 60
- **Quality**: 90%

Adjust these in the Export panel before generating video.

### Tips for Creating Your Own Presets

1. **Performance-focused**: Use Circle shape, low spawn rate, fewer max particles
2. **Visual richness**: Enable glow + trails, choose interesting color schemes
3. **Audio interesting**: Mix instruments, adjust collision volume for melodies
4. **Export quality**: Match resolution/FPS to your hardware capabilities

### Recommended Combinations

- **Beautiful slow motion**: Low spawn rate + enabled trails + Glow boundary
- **Chaotic energy**: High spawn rate + Star/Hexagon shape + Burst effect
- **Meditative**: Low spawn rate + soft colors + ambient-heavy audio
- **Intense action**: High spawn rate + small particles + high-frequency audio

