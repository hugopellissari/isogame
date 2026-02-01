from pydantic import BaseModel, Field
from typing import Union
from .base import BaseEntity
from .tree import Tree
from .units import Lumberjack


class EntityMap(BaseModel):
    # Unified storage. Supports Polymorphism (can hold Tree OR Lumberjack)
    entities: dict[str, Union[Tree, Lumberjack]] = Field(default_factory=dict)

    def add(self, entity: BaseEntity):
        self.entities[entity.id] = entity

    def remove(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def get(self, entity_id: str) -> BaseEntity | None:
        return self.entities.get(entity_id)

    @property
    def units(self) -> list[Lumberjack]:
        # Helper to get just units when we need them
        return [e for e in self.entities.values() if isinstance(e, Lumberjack)]

    @property
    def trees(self) -> list[Tree]:
        # Helper to get just trees
        return [e for e in self.entities.values() if isinstance(e, Tree)]
