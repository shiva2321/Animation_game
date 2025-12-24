"""
GPU-accelerated rendering utilities using OpenGL/pygame with hardware acceleration.
"""
import pygame
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class GPURenderer:
    """
    Hardware-accelerated renderer using OpenGL through pygame.
    Falls back to software rendering if GPU not available.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize GPU renderer.

        Args:
            width: Render width
            height: Render height
        """
        self.width = width
        self.height = height
        self.gpu_available = False
        self.surface = None

        # Try to enable hardware acceleration
        try:
            # Check if OpenGL is available
            pygame.display.gl_get_attribute(pygame.GL_ACCELERATED_VISUAL)

            # Create hardware-accelerated surface
            self.surface = pygame.display.set_mode(
                (width, height),
                pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.ASYNCBLIT
            )
            self.gpu_available = True
            logger.info("GPU acceleration ENABLED for rendering")

        except Exception as e:
            # Fall back to software rendering
            logger.warning(f"GPU acceleration not available: {e}")
            logger.info("Using software rendering")
            self.surface = pygame.Surface((width, height))
            self.gpu_available = False

    def create_surface(self, size: Tuple[int, int], flags=0) -> pygame.Surface:
        """
        Create a surface with hardware acceleration if available.

        Args:
            size: Surface size (width, height)
            flags: Pygame surface flags

        Returns:
            Accelerated or software surface
        """
        if self.gpu_available:
            try:
                # Try hardware surface with alpha
                return pygame.Surface(size, pygame.HWSURFACE | pygame.SRCALPHA | flags).convert_alpha()
            except:
                pass

        # Fallback to software with convert for speed
        return pygame.Surface(size, pygame.SRCALPHA | flags).convert_alpha()

    def blit_optimized(self, dest: pygame.Surface, source: pygame.Surface,
                       pos: Tuple[int, int], area=None, special_flags=0):
        """
        Optimized blit operation.

        Args:
            dest: Destination surface
            source: Source surface
            pos: Position to blit at
            area: Source area to blit
            special_flags: Blend flags
        """
        try:
            if area:
                dest.blit(source, pos, area, special_flags)
            else:
                dest.blit(source, pos, special_flags=special_flags)
        except Exception as e:
            logger.debug(f"Blit error: {e}")

    def get_info(self) -> dict:
        """Get GPU info."""
        return {
            'gpu_enabled': self.gpu_available,
            'driver': pygame.display.get_driver(),
            'hw_surfaces': pygame.display.get_surface() is not None
        }


def check_gpu_available() -> bool:
    """
    Check if GPU acceleration is available.

    Returns:
        True if GPU available
    """
    try:
        # Try to get OpenGL info
        pygame.display.gl_get_attribute(pygame.GL_ACCELERATED_VISUAL)
        return True
    except:
        return False


def optimize_surface_for_gpu(surface: pygame.Surface) -> pygame.Surface:
    """
    Optimize a surface for GPU rendering.

    Args:
        surface: Surface to optimize

    Returns:
        Optimized surface
    """
    try:
        # Convert to display format for faster blitting
        if surface.get_alpha() or surface.get_colorkey():
            return surface.convert_alpha()
        else:
            return surface.convert()
    except:
        return surface

