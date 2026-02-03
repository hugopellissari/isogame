from abc import abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from engine.core.game import Game

# Used to prevent floating point "micro-misses"
EPSILON = 1e-6


class System:
    @abstractmethod
    def update(self, game: "Game", dt: float): ...
