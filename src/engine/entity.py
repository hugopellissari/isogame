from typing import Self, Type, TypeVar
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from engine.trait import ActorTrait, BaseTrait, InteractionVerb, MovableTrait

T = TypeVar("T", bound=BaseTrait)


class BaseEntity(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    asset: str  # defines a name to map with the asset visually
    position: tuple[float, float]
    traits: list[BaseTrait] = Field(default_factory=list)
    # TODO refactor this. Should we keep those methods to set movement 
    # and action? I am starting to thing we should not! There are some
    # rules we still need to enforce, such as not having multiple actions
    # having at the same time, moving and acting at the same time is allowed 
    # (unless outherwise specificied)

    @property
    def active_action_trait(self):
        """Returns the ActorTrait that is currently active."""
        actor_traits = [t for t in self.traits if isinstance(t, ActorTrait)]
        active_traits = [t for t in actor_traits if t.is_active]
        return active_traits[0] if active_traits else None

    @property
    def is_moving(self) -> bool:
        # TODO has a MovableTrait and destination is not None
        movable_trait = self.get_trait(MovableTrait)
        return movable_trait is not None and movable_trait.is_moving

    @property
    def is_active(self) -> bool:
        """Determines if the entity needs system processing this frame."""
        return self.is_moving or self.active_action_trait is not None

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
        # TODO what happens if the user tries to set an action when something is already going on?
        # I think we should cancel the previous action and start the new one
        self.stop_action()

        trait = next(
            (t for t in self.traits 
             if isinstance(t, ActorTrait) and interaction_verb in t.can_act_on), 
            None
        )

        if not trait:
            raise ValueError(
                f"Entity {self.id} does not have a trait capable of verb: {interaction_verb}"
            )
        
        trait.activate(target_id)
        if destination:
            self.move_to(destination)

    def move_to(self, destination: tuple[float, float]):
        movable_trait = self.get_trait(MovableTrait)
        if not movable_trait:
            raise ValueError("Entity does not have a MovableTrait")
        movable_trait.set_destination(destination)

    @property
    def destination(self):
        movable_trait = self.get_trait(MovableTrait)
        return movable_trait.destination if movable_trait else None

    def stop_action(self):
        active_action = self.active_action_trait
        if active_action:
            active_action.deactivate()
        
        self.stop_movement()

    def stop_movement(self):
        movable_trait = self.get_trait(MovableTrait)
        if movable_trait:
            movable_trait.stop()


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
