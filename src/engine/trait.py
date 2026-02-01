from abc import abstractmethod
from enum import Enum
from pydantic import BaseModel, Field
from engine.cqrs import BaseEvent


class BaseTrait(BaseModel):
    pass


class MovableTrait(BaseTrait):
    """
    Traits that allow an entity to move to a destination.
    """
    speed: float = 1.0
    destination: tuple[float, float] | None = None
    path: list[tuple[float, float]] | None = None

    def set_destination(self, destination: tuple[float, float]):
        self.destination = destination

    def set_path(self, path: list[tuple[float, float]]):
        self.path = path

    def stop(self):
        self.destination = None
        self.path = None

    @property
    def is_moving(self) -> bool:
        return self.destination is not None



# Defines traits where entities can act on each other
class InteractionVerb(Enum):
    # To be implenented by each game
    pass


class ActorTrait(BaseTrait):
    """
    Traits that allow an entity to initiate actions.
    Example: CanChop, CanMine, CanHeal.
    """
    range: float
    target_id: str | None = None
    is_active: bool = False
    can_act_on: list[InteractionVerb] = Field(default_factory=list)

    def activate(self, target_id: str):
        self.target_id = target_id
        self.is_active = True
    
    def deactivate(self):
        self.target_id = None
        self.is_active = False

    @abstractmethod
    def on_perform_action(self, actor_entity, target_entity) -> list[BaseEvent]:
        """
        The 'Cost' or 'Effort' side.
        Example: Reduce stamina, play swing sound, or wear down a tool.
        """


class ReceiverTrait(BaseTrait):
    verb: InteractionVerb

    @abstractmethod
    def on_receive_action(self, actor_entity, target_entity) -> list[BaseEvent]:
        """
        The 'Effect' or 'Reaction' side.
        Example: Reduce health, drop items, or explode.
        """
