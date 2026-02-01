from typing import Self, Type, TypeVar
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from engine.trait import ActorTrait, BaseTrait, InteractionVerb

T = TypeVar("T", bound=BaseTrait)

class BaseEntity(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    position: tuple[float, float]
    traits: list[BaseTrait] = Field(default_factory=list)
    _destination: tuple[float, float] | None = None
    _active_action_trait: ActorTrait | None = None
    _action_target_id: str | None = None

    @property
    def destination(self) -> tuple[float, float] | None:
        return self._destination
    
    @property
    def active_action_trait(self):
        return self._active_action_trait

    @property
    def action_target_id(self) -> str | None:
        return self._action_target_id
    
    @destination.setter
    def destination(self, value: tuple[float, float] | None):
        self._destination = value

    @property
    def is_moving(self) -> bool:
        return self.destination is not None

    @property
    def is_active(self) -> bool:
        """Determines if the entity needs system processing this frame."""
        return self.is_moving or self.active_action_trait is not None or self.action_target_id is not None

    def get_trait(self, trait_type: Type[T]) -> T | None:
        """Returns the first trait matching the given type."""
        for trait in self.traits:
            if isinstance(trait, trait_type):
                return trait
        return None

    def set_action(
        self, 
        interaction_verb: InteractionVerb, 
        target_id: str, 
        destination: tuple[float, float] | None = None
    ):
        # 1. Look for an ActorTrait that supports this verb
        trait = next(
            (t for t in self.traits 
             if isinstance(t, ActorTrait) and interaction_verb in t.can_act_on), 
            None
        )

        if not trait:
            raise ValueError(
                f"Entity {self.id} does not have a trait capable of verb: {interaction_verb}"
            )

        # 2. Assign to private attributes
        self._active_action_trait = trait
        self._action_target_id = target_id
        if destination:
            self._destination = destination
    
    def clear_action(self):
        if self._action_target_id and self._active_action_trait:
            self._active_action_trait = None
            self._action_target_id = None
            self._destination = None

    def move_to(self, target_position: tuple[float, float]):
        self._destination = target_position

    def stop_movement(self):
        self._destination = None


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

    def clear(self):
        self.entities.clear()
        self.active_ids.clear()

    def reconcile(self):
        """
        Refreshes the active_ids index. This is the only place 
        active_ids is modified during the simulation loop.
        """
        self.active_ids = {
            eid for eid, entity in self.entities.items() 
            if entity.is_active
        }

    def get_active_entities(self):
        """Returns a generator for systems to iterate over."""
        for eid in self.active_ids:
            yield self.entities[eid]
