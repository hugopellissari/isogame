from game.world.entities.traits import Chopper, Mover
from .base import BaseEntity


class Lumberjack(BaseEntity):
    mover: Mover = Mover(speed=2.0)
    chopper: Chopper = Chopper(power=10.0)
