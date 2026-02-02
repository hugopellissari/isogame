from enum import Enum
from typing import ClassVar
from pydantic import BaseModel, Field


class InteractionVerb(Enum):
    pass


class BaseTrait(BaseModel):
    pass


class MovableTrait(BaseTrait):
    speed: float = 1.0
    destination: tuple[float, float] | None = None
    path: list[tuple[float, float]] = Field(default_factory=list)

    @property
    def is_moving(self) -> bool:
        return self.destination is not None
    
    def set_path(self, path: list[tuple[float, float]]):
        self.path = path
    
    def move_to(self, x: float, y: float):
        self.destination = (x, y)
        self.path = []
    
    def stop_movement(self):
        self.destination = None
        self.path = []


class ActorTrait(BaseTrait):
    """Base for traits that INITIATE an action (Actor)."""
    verb: ClassVar[InteractionVerb]  # Must be defined by subclasses
    range: float = 1.0
    cooldown: float = 0.0
    # State tracking
    target_id: str | None = None
    is_active: bool = False

    def activate(self, target_id: str):
        self.target_id = target_id
        self.is_active = True

    def stop(self):
        self.target_id = None
        self.is_active = False


class ReceiverTrait(BaseTrait):
    """Base for traits that RECEIVE an action (Target)."""
    verb: ClassVar[InteractionVerb]  # Must be defined by subclasses
