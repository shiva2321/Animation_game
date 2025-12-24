"""Tests for video export functionality"""

import unittest
import tempfile
import os
from pathlib import Path
from src.video_exporter import VideoExporter
from src.utils.config import ConfigManager, DEFAULT_CONFIG


class TestVideoExporter(unittest.TestCase):
    """Test video exporter"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = VideoExporter(output_dir=self.temp_dir)

    def tearDown(self):
        """Clean up"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_exporter_creation(self):
        """Test exporter initialization"""
        exporter = VideoExporter(output_dir=self.temp_dir)

        self.assertEqual(exporter.output_dir, Path(self.temp_dir))
        self.assertTrue(exporter.output_dir.exists())

    def test_resolutions(self):
        """Test resolution presets"""
        resolutions = VideoExporter.RESOLUTIONS

        self.assertIn("720p", resolutions)
        self.assertIn("1080p", resolutions)
        self.assertIn("4K", resolutions)

        self.assertEqual(resolutions["720p"], (1280, 720))
        self.assertEqual(resolutions["1080p"], (1920, 1080))
        self.assertEqual(resolutions["4K"], (3840, 2160))

    def test_fps_options(self):
        """Test FPS options"""
        fps_options = VideoExporter.FPS_OPTIONS

        self.assertIn(30, fps_options)
        self.assertIn(60, fps_options)

    def test_estimate_export_time(self):
        """Test export time estimation"""
        exporter = VideoExporter(output_dir=self.temp_dir)

        # Estimate time for 30 second video at 1080p 60fps with 90% quality
        estimate = exporter.estimate_export_time(
            duration_seconds=30,
            fps=60,
            resolution="1080p",
            quality=90
        )

        self.assertGreater(estimate, 0)

        # Higher quality should take longer
        estimate_high = exporter.estimate_export_time(
            duration_seconds=30,
            fps=60,
            resolution="1080p",
            quality=100
        )

        self.assertGreater(estimate_high, estimate)

    def test_estimate_scales_with_resolution(self):
        """Test that estimation scales with resolution"""
        exporter = VideoExporter(output_dir=self.temp_dir)

        estimate_720 = exporter.estimate_export_time(30, 60, "720p", 90)
        estimate_1080 = exporter.estimate_export_time(30, 60, "1080p", 90)
        estimate_4k = exporter.estimate_export_time(30, 60, "4K", 90)

        # Higher resolution should take longer
        self.assertLess(estimate_720, estimate_1080)
        self.assertLess(estimate_1080, estimate_4k)


class TestConfigManager(unittest.TestCase):
    """Test configuration management"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_config_creation(self):
        """Test configuration creation"""
        config = ConfigManager(config_dir=self.temp_dir)

        self.assertIsNotNone(config.config)
        self.assertGreater(len(config.config), 0)

    def test_get_config_value(self):
        """Test getting configuration values"""
        config = ConfigManager(config_dir=self.temp_dir)

        spawn_rate = config.get("particle_settings", "spawn_rate")
        self.assertEqual(spawn_rate, 5)

        max_particles = config.get("particle_settings", "max_particles")
        self.assertEqual(max_particles, 100)

    def test_set_config_value(self):
        """Test setting configuration values"""
        config = ConfigManager(config_dir=self.temp_dir)

        config.set("particle_settings", "spawn_rate", value=10)

        spawn_rate = config.get("particle_settings", "spawn_rate")
        self.assertEqual(spawn_rate, 10)

    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        config = ConfigManager(config_dir=self.temp_dir)

        config.set("particle_settings", "spawn_rate", value=15)
        config.save_config()

        # Load new instance
        config2 = ConfigManager(config_dir=self.temp_dir)
        spawn_rate = config2.get("particle_settings", "spawn_rate")

        self.assertEqual(spawn_rate, 15)

    def test_reset_to_defaults(self):
        """Test reset to defaults"""
        config = ConfigManager(config_dir=self.temp_dir)

        config.set("particle_settings", "spawn_rate", value=20)
        config.reset_to_defaults()

        spawn_rate = config.get("particle_settings", "spawn_rate")
        self.assertEqual(spawn_rate, DEFAULT_CONFIG["particle_settings"]["spawn_rate"])

    def test_presets(self):
        """Test preset management"""
        config = ConfigManager(config_dir=self.temp_dir)

        # Save preset
        config.set("particle_settings", "spawn_rate", value=8)
        config.save_preset("TestPreset")

        # List presets
        presets = config.list_presets()
        self.assertIn("TestPreset", presets)

        # Load preset
        config.set("particle_settings", "spawn_rate", value=5)
        config.load_preset("TestPreset")

        spawn_rate = config.get("particle_settings", "spawn_rate")
        self.assertEqual(spawn_rate, 8)

        # Delete preset
        config.delete_preset("TestPreset")
        presets = config.list_presets()
        self.assertNotIn("TestPreset", presets)


if __name__ == '__main__':
    unittest.main()

