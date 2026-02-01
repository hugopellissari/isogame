from game.world.entities.base import BaseEntity
from game.world.entities.traits import Destructible


class Tree(BaseEntity):
    destructible: Destructible = Destructible(health=50)
