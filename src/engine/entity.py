from typing import Generator, Type, TypeVar, cast
import uuid

from engine.commons import Position
from pydantic import BaseModel, ConfigDict, Field

from engine.trait import BaseTrait

T = TypeVar("T", bound=BaseTrait)


class NullTrait:
    """Swallows calls so entity.movable_trait.move_to() doesn't crash if missing."""
    def __getattr__(self, _):
        return lambda *args, **kwargs: None


class BaseEntity(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    id: str = Field(default_factory=lambda: uuid.uuid4().hex) # this is the instane id
    asset: str # this is the identifier of the 'class'
    position: Position = (0, 0, 0)
    traits: list[BaseTrait] = Field(default_factory=list)

    def as_a(self, trait_type: Type[T]) -> T | NullTrait:
        trait = self.get_trait(trait_type)
        return cast(T, trait or NullTrait())

    def get_trait(self, trait_type: Type[T]) -> T | None:
        # TODO make use of dicts to ensure O(1) access
        for trait in self.traits:
            if isinstance(trait, trait_type):
                return trait
        return None

    def has_trait(self, trait_type: Type[T]) -> bool:
        return self.get_trait(trait_type) is not None


class EntityMap(BaseModel):
    entities: dict[str, BaseEntity] = Field(default_factory=dict)
    # TODO we don't have an active_ids anymore, so we don't have quite a way to notify
    # the engine what we need to update

    def list(self) -> list[BaseEntity]:
        # TODO make this a egnerator instead
        return list(self.entities.values())

    def add(self, entity: BaseEntity):
        self.entities[entity.id] = entity
 
    def remove(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def get(self, entity_id: str) -> BaseEntity | None:
        return self.entities.get(entity_id)

    def yield_entities_with_trait(self, trait_class: Type[T]) -> Generator[tuple[BaseEntity, T], None, None]:
        """
        Iterates through all entities and yields pairs of (entity, trait_instance)
        only for entities that possess the requested trait.
        """
        for entity in self.entities.values():
            trait = entity.get_trait(trait_class)
            if trait is not None:
                # We yield the entity and the specific trait instance
                yield entity, trait

    def clear(self):
        self.entities.clear()
