from engine.entity import BaseEntity
from game.world.entities.traits import Destructible


class Tree(BaseEntity):
    destructible: Destructible = Destructible(health=50)


class Lumberjack(BaseEntity):
    mover: Mover = Mover(speed=2.0)
    chopper: Chopper = Chopper(power=10.0)
