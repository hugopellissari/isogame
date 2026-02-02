from typing import Type, TypeVar
import uuid

from pydantic import BaseModel, ConfigDict, Field

from engine.trait import BaseTrait

T = TypeVar("T", bound=BaseTrait)


class BaseEntity(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    asset: str
    position: tuple[float, float]
    traits: list[BaseTrait] = Field(default_factory=list)

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

    def add(self, entity: BaseEntity):
        self.entities[entity.id] = entity
 
    def remove(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def get(self, entity_id: str) -> BaseEntity | None:
        return self.entities.get(entity_id)

    def list_with_trait(self, trait_class: type[T]) -> list[BaseEntity]: # TODO fix typing
        for entity in self.entities.values():
            for trait in entity.traits:
                if isinstance(trait, trait_class):  
                    yield entity

    def clear(self):
        self.entities.clear()
