from abc import abstractmethod
from typing import TYPE_CHECKING, Type
from math import sqrt

from engine.cqrs import EntityArrivedEvent, BaseEvent
from engine.entity import BaseEntity
from engine.trait import ActorTrait, MovableTrait, ReceiverTrait

if TYPE_CHECKING:
    from engine.game import Game

# Used to prevent floating point "micro-misses"
EPSILON = 1e-6

class System:
    @abstractmethod
    def update(self, game: "Game", dt: float):
        ...

class MovementSystem(System):
    def update(self, game: "Game", dt: float):
        # Optimized: Only iterate over entities the map knows are active
        for entity, movable in game.entities.yield_entities_with_trait(MovableTrait):
            if not movable.destination:
                continue

            if not movable.path:
                # TODO If the trait has a destination set, and no path, we need to define
                # a path to that destination that overcomes obstacles.
                # For now, we just provide the destination
                movable.set_path([movable.destination])

            if not movable.is_moving:
                continue

            # Here we will have to navigate to the next waypoint in the path
            dest_pos = movable.path.pop()

            current_pos = entity.position
            dx = dest_pos[0] - current_pos[0]
            dy = dest_pos[1] - current_pos[1]
            distance = sqrt(dx**2 + dy**2)

            move_distance = movable.speed * dt

            # Check if we arrive this tick (with epsilon buffer)
            if distance <= move_distance + EPSILON:
                # SNAP: Force exact coordinates to prevent rounding drift
                entity.position = dest_pos
                movable.stop_movement() 
                game.enqueue_event(EntityArrivedEvent(entity_id=entity.id))
            else:
                # STEP: Move toward destination
                ratio = move_distance / distance
                new_x = current_pos[0] + (dx * ratio)
                new_y = current_pos[1] + (dy * ratio)
                entity.position = (new_x, new_y)


class InteractionSystem(System):
    @property
    @abstractmethod
    def actor_trait_subclass(self) -> Type[ActorTrait]:
        ...

    @abstractmethod
    def handle_action(self, actor: BaseEntity, target: BaseEntity) -> list[BaseEvent]:
        ...

    def can_act(self, actor: BaseEntity, target: BaseEntity) -> bool:
        return self._can_act(actor, target)

    def _can_act(self, actor: BaseEntity, target: BaseEntity):
        verb = self.actor_trait_subclass.verb
        for trait in target.traits:
            if isinstance(trait, ReceiverTrait):
                return trait.verb == verb
        return self.can_act(actor, target)

    def update(self, game: "Game", dt: float):
        for actor, action_trait in game.entities.yield_entities_with_trait(self.actor_trait_subclass):
            if not action_trait:
                continue

            if not action_trait.target_id:
                raise ValueError("Active trait has no target")

            target = game.entities.get(action_trait.target_id)
            if not target:
                action_trait.stop()
                continue
            
            if not self._can_act(actor, target):
                continue

            # 2. Spatial Validation with Epsilon
            movable_trait = actor.get_trait(MovableTrait)
            if not self._is_in_range(actor, target, action_trait.range):
                if movable_trait:
                    movable_trait.move_to(target.position[0], target.position[1])

            else:
                # If we are in range, stop moving so the interaction is stable
                if movable_trait and movable_trait.is_moving:
                    movable_trait.stop_movement()

                # 3. Logic Execution
                events = self.handle_action(actor, target)
                for event in events:
                    game.enqueue_event(event)

    def _is_in_range(self, actor, target, interaction_range):
        dx = actor.position[0] - target.position[0]
        dy = actor.position[1] - target.position[1]
        distance = sqrt(dx**2 + dy**2)
        # Use Epsilon here so that 'exactly 1.0' distance passes a '1.0' range check
        return distance <= (interaction_range + EPSILON)
