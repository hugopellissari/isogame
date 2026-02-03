from abc import abstractmethod
from typing import TYPE_CHECKING, Type
from math import sqrt

from engine.core.cqrs import EntityArrivedEvent, BaseEvent
from engine.core.entity import BaseEntity
from engine.core.trait import ActorTrait, MovableTrait, ReceiverTrait, GroundableTrait

if TYPE_CHECKING:
    from engine.core.game import Game

# Used to prevent floating point "micro-misses"
EPSILON = 1e-6


class System:
    @abstractmethod
    def update(self, game: "Game", dt: float): ...
