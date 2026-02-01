from abc import abstractmethod
from enum import Enum
from pydantic import BaseModel, Field
from engine.services.events import BaseEvent


class BaseTrait(BaseModel):
    pass


# Defines traits where entities can act on each other
class InteractionVerb(Enum):
    # To be implenented by each game
    pass


class ActorTrait(BaseTrait):
    """
    Traits that allow an entity to initiate actions.
    Example: CanChop, CanMine, CanHeal.
    """
    can_act_on: list[InteractionVerb] = Field(default_factory=list)

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
