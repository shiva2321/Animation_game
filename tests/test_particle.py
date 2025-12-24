"""Tests for particle collision detection and physics"""

import unittest
import math
from src.particle_engine import Particle, ParticleEngine


class TestParticle(unittest.TestCase):
    """Test particle class"""

    def test_particle_creation(self):
        """Test particle initialization"""
        particle = Particle(100, 100, 1.0, 1.0, 5, (255, 0, 0))

        self.assertEqual(particle.x, 100)
        self.assertEqual(particle.y, 100)
        self.assertEqual(particle.vx, 1.0)
        self.assertEqual(particle.vy, 1.0)
        self.assertEqual(particle.radius, 5)
        self.assertEqual(particle.color, (255, 0, 0))

    def test_particle_update(self):
        """Test particle position update"""
        particle = Particle(100, 100, 1.0, 0.0, 5, (255, 0, 0))
        particle.update(dt=1.0)

        # Position should change by velocity
        self.assertAlmostEqual(particle.x, 100.9995, places=3)

    def test_boundary_collision(self):
        """Test boundary collision detection and response"""
        particle = Particle(400, 300, 10.0, 0.0, 5, (255, 0, 0))

        # Move particle out of boundary and check collision
        collisions = particle.check_boundary_collision(
            center_x=300, center_y=300, boundary_radius=100
        )

        # Should be in collision
        self.assertEqual(len(collisions), 1)

    def test_particle_particle_collision(self):
        """Test collision between two particles"""
        p1 = Particle(100, 100, 1.0, 0.0, 5, (255, 0, 0))
        p2 = Particle(109, 100, 0.0, 0.0, 5, (0, 255, 0))

        # Should detect collision (distance = 9, radii sum = 10)
        self.assertTrue(p1.check_particle_collision(p2))

    def test_particle_no_collision(self):
        """Test no collision between distant particles"""
        p1 = Particle(100, 100, 0.0, 0.0, 5, (255, 0, 0))
        p2 = Particle(200, 100, 0.0, 0.0, 5, (0, 255, 0))

        # Should not detect collision
        self.assertFalse(p1.check_particle_collision(p2))

    def test_collision_creates_new_particles(self):
        """Test that collisions create new particles"""
        p1 = Particle(100, 100, 2.0, 0.0, 5, (255, 0, 0))
        p2 = Particle(109, 100, -2.0, 0.0, 5, (0, 255, 0))

        new_particles = p1.resolve_collision(p2)

        # Should create 1-3 new particles
        self.assertGreater(len(new_particles), 0)
        self.assertLessEqual(len(new_particles), 3)

        # New particles should have shorter lifetime
        for particle in new_particles:
            self.assertIsNotNone(particle.lifetime)


class TestParticleEngine(unittest.TestCase):
    """Test particle engine"""

    def test_engine_creation(self):
        """Test engine initialization"""
        engine = ParticleEngine(800, 600, 250)

        self.assertEqual(engine.width, 800)
        self.assertEqual(engine.height, 600)
        self.assertEqual(engine.boundary_radius, 250)
        self.assertEqual(len(engine.particles), 0)

    def test_spawn_particle(self):
        """Test particle spawning"""
        engine = ParticleEngine(800, 600, 250)
        engine.spawn_particle(5)

        self.assertEqual(len(engine.particles), 5)

    def test_max_particles_limit(self):
        """Test maximum particle limit"""
        engine = ParticleEngine(800, 600, 250)
        engine.max_particles = 10
        engine.spawn_particle(20)

        self.assertEqual(len(engine.particles), 10)

    def test_reset(self):
        """Test engine reset"""
        engine = ParticleEngine(800, 600, 250)
        engine.spawn_particle(10)
        engine.reset()

        self.assertEqual(len(engine.particles), 0)
        self.assertEqual(len(engine.collision_log), 0)

    def test_set_spawn_rate(self):
        """Test spawn rate setting"""
        engine = ParticleEngine(800, 600, 250)

        engine.set_spawn_rate(15)
        self.assertEqual(engine.spawn_rate, 15)

        # Should be clamped to max
        engine.set_spawn_rate(100)
        self.assertEqual(engine.spawn_rate, 20)

    def test_set_max_particles(self):
        """Test max particles setting"""
        engine = ParticleEngine(800, 600, 250)

        engine.set_max_particles(150)
        self.assertEqual(engine.max_particles, 150)

        # Should be clamped to limits
        engine.set_max_particles(300)
        self.assertEqual(engine.max_particles, 200)

    def test_particle_shape_setting(self):
        """Test particle shape setting"""
        engine = ParticleEngine(800, 600, 250)
        engine.set_particle_shape("Square")

        self.assertEqual(engine.particle_shape, "Square")


if __name__ == '__main__':
    unittest.main()

