from typing import Type, TypeVar
import uuid

from pydantic import BaseModel, Field

from engine.trait import ActorTrait, BaseTrait

T = TypeVar("T", bound=BaseTrait)

class BaseEntity(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    position: tuple[float, float]
    traits: list[BaseTrait] = Field(default_factory=list)
    destination: tuple[float, float] | None = None
    active_action_trait: ActorTrait | None = None
    target_id: str | None = None

    @property
    def is_moving(self) -> bool:
        return self.destination is not None

    @property
    def is_active(self) -> bool:
        """Determines if the entity needs system processing this frame."""
        return self.is_moving or self.active_action_trait is not None or self.target_id is not None

    def get_trait(self, trait_type: Type[T]) -> T | None:
        """Returns the first trait matching the given type."""
        for trait in self.traits:
            if isinstance(trait, trait_type):
                return trait
        return None


class EntityMap(BaseModel):
    entities: dict[str, BaseEntity] = Field(default_factory=dict)
    active_ids: set[str] = Field(default_factory=set)

    def add(self, entity: BaseEntity):
        self.entities[entity.id] = entity
        self.update(entity)

    def remove(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]
            self.active_ids.discard(entity_id)

    def get(self, entity_id: str) -> BaseEntity | None:
        return self.entities.get(entity_id)

    def update(self, entity: BaseEntity):
        """
        Re-evaluates whether an entity should be in the active set.
        Call this whenever an entity's 'is_active' state might have changed.
        """
        if entity.is_active:
            self.active_ids.add(entity.id)
        else:
            self.active_ids.discard(entity.id)
