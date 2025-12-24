
import numpy as np

class RNG:
    def __init__(self, seed: int):
        self._rng = np.random.default_rng(seed)

    def set_seed(self, seed: int):
        self._rng = np.random.default_rng(seed)

    def random(self, size=None):
        return self._rng.random(size)

    def uniform(self, low=0.0, high=1.0, size=None):
        return self._rng.uniform(low, high, size)

    def normal(self, loc=0.0, scale=1.0, size=None):
        return self._rng.normal(loc, scale, size)

    def integers(self, low, high=None, size=None, endpoint=False):
        return self._rng.integers(low, high, size, endpoint)

# Global RNG instance
# This will be seeded at the start of each simulation.
rng = RNG(42)
