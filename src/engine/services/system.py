from abc import abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.game import Game


class System:
    """
    Systems control changes of state of the game. This is the only place where we update
    entities and emit events to the world. It is what handles the countinous actions triggered
    by the events.
    """
    @abstractmethod
    def update(self, game: Game, dt: float):
        ...


class InteractionSystem(System):
    """
    This system is responsible to coordinate the actions between two entities that
    can interact with each other based on the traits they have. 
    """
    def update(self, world: "Game", dt: float):
        pass
