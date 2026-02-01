import uuid
from pydantic import BaseModel, Field

from engine.trait import BaseTrait


class BaseEntity(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    position: tuple[float, float]
    traits: list[BaseTrait] = Field(default_factory=list)
    # This only makes sense for entities that have ActorTraits, as defined
    # on which entity this is acting upon.
    target_id: str | None = None


class EntityMap(BaseModel):
    entities: dict[str, BaseEntity] = Field(default_factory=dict)

    def add(self, entity: BaseEntity):
        self.entities[entity.id] = entity

    def remove(self, entity_id: str):
        if entity_id in self.entities:
            del self.entities[entity_id]

    def get(self, entity_id: str) -> BaseEntity | None:
        return self.entities.get(entity_id)
