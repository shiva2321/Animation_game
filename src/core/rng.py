"""
Deterministic random number generator helper.
"""
import numpy as np


class DeterministicRNG:
    """Wrapper for NumPy random generator with seed control."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.RandomState(seed)

    def reset(self, seed: int = None):
        """Reset with new seed (or use original seed)."""
        if seed is not None:
            self.seed = seed
        self.rng = np.random.RandomState(self.seed)

    def random(self) -> float:
        """Random float [0, 1)."""
        return self.rng.random()

    def uniform(self, low: float, high: float) -> float:
        """Uniform random float."""
        return self.rng.uniform(low, high)

    def normal(self, mean: float = 0, std: float = 1) -> float:
        """Normal distribution."""
        return self.rng.normal(mean, std)

    def choice(self, options, weights=None):
        """Random choice from options with optional weights."""
        if weights is not None:
            weights = np.array(weights)
            weights = weights / weights.sum()
            return self.rng.choice(options, p=weights)
        return self.rng.choice(options)

    def randint(self, low: int, high: int) -> int:
        """Random integer [low, high)."""
        return self.rng.randint(low, high)

    def randn(self, *shape) -> np.ndarray:
        """Standard normal distribution array."""
        return self.rng.randn(*shape)

    def rand(self, *shape) -> np.ndarray:
        """Uniform [0, 1) distribution array."""
        return self.rng.rand(*shape)

