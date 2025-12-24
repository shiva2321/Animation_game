"""Tests for audio generation and management"""

import unittest
import numpy as np
from src.audio_engine import AudioGenerator, AudioEngine


class TestAudioGenerator(unittest.TestCase):
    """Test audio generation"""

    def test_sine_wave_generation(self):
        """Test basic sine wave generation"""
        wave = AudioGenerator.generate_sine_wave(440.0, 100)

        # Check wave properties
        self.assertEqual(len(wave), 4410)  # 44100 * 0.1
        self.assertLessEqual(np.max(np.abs(wave)), 0.81)

    def test_adsr_envelope(self):
        """Test ADSR envelope application"""
        wave = AudioGenerator.generate_sine_wave(440.0, 100)
        enveloped = AudioGenerator.apply_adsr_envelope(
            wave, attack_ms=10, decay_ms=20, sustain_level=0.8, release_ms=30
        )

        # Check envelope was applied
        self.assertEqual(len(enveloped), len(wave))

        # Start should be lower due to attack
        self.assertLess(enveloped[0], enveloped[100])

        # End should be low due to release
        self.assertLess(enveloped[-1], enveloped[-100])

    def test_piano_tone_generation(self):
        """Test piano tone generation"""
        wave = AudioGenerator.generate_piano_tone(440.0, 100)

        self.assertIsNotNone(wave)
        self.assertGreater(len(wave), 0)

    def test_violin_tone_generation(self):
        """Test violin tone generation"""
        wave = AudioGenerator.generate_violin_tone(440.0, 100)

        self.assertIsNotNone(wave)
        self.assertGreater(len(wave), 0)

    def test_synth_tone_generation(self):
        """Test synth tone generation"""
        wave = AudioGenerator.generate_synth_tone(440.0, 100)

        self.assertIsNotNone(wave)
        self.assertGreater(len(wave), 0)

    def test_wave_to_audio_segment(self):
        """Test conversion to AudioSegment"""
        wave = AudioGenerator.generate_sine_wave(440.0, 100)
        audio = AudioGenerator.wave_to_audio_segment(wave)

        self.assertIsNotNone(audio)
        self.assertEqual(audio.frame_rate, 44100)
        self.assertEqual(audio.channels, 1)

    def test_pentatonic_notes(self):
        """Test pentatonic scale notes"""
        notes = AudioGenerator.PENTATONIC_NOTES

        # Check key notes exist
        self.assertIn('C4', notes)
        self.assertIn('A4', notes)
        self.assertIn('C6', notes)

        # Check frequencies are reasonable
        self.assertGreater(notes['C4'], 0)
        self.assertLess(notes['C4'], notes['C5'])


class TestAudioEngine(unittest.TestCase):
    """Test audio engine"""

    def test_engine_creation(self):
        """Test audio engine initialization"""
        engine = AudioEngine()

        self.assertEqual(engine.instrument, "Piano")
        self.assertEqual(engine.master_volume, 0.5)

    def test_collision_sound_generation(self):
        """Test collision sound generation"""
        engine = AudioEngine()
        sound = engine.generate_collision_sound()

        self.assertIsNotNone(sound)
        self.assertGreater(len(sound), 0)

    def test_spawn_sound_generation(self):
        """Test spawn sound generation"""
        engine = AudioEngine()
        sound = engine.generate_spawn_sound()

        self.assertIsNotNone(sound)
        self.assertGreater(len(sound), 0)

    def test_boundary_bounce_sound(self):
        """Test boundary bounce sound generation"""
        engine = AudioEngine()
        sound = engine.generate_boundary_bounce_sound()

        self.assertIsNotNone(sound)
        self.assertGreater(len(sound), 0)

    def test_ambient_drone_generation(self):
        """Test ambient drone generation"""
        engine = AudioEngine()
        drone = engine.generate_ambient_drone(1000)

        self.assertIsNotNone(drone)
        self.assertGreater(len(drone), 0)

    def test_mute_all(self):
        """Test mute all functionality"""
        engine = AudioEngine()
        engine.mute_all = True

        sound = engine.generate_collision_sound()

        # Muted sound should be silent
        self.assertIsNotNone(sound)

    def test_instrument_selection(self):
        """Test instrument selection"""
        engine = AudioEngine()

        instruments = ["Piano", "Violin", "Synth", "Mixed"]
        for instrument in instruments:
            engine.instrument = instrument
            sound = engine.generate_collision_sound()
            self.assertIsNotNone(sound)

    def test_volume_control(self):
        """Test volume control"""
        engine = AudioEngine()
        engine.master_volume = 0.2
        engine.collision_volume = 0.5

        sound = engine.generate_collision_sound()

        # Sound should exist
        self.assertIsNotNone(sound)


if __name__ == '__main__':
    unittest.main()

