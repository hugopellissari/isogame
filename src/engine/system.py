from abc import abstractmethod
from typing import TYPE_CHECKING
from math import sqrt

from engine.cqrs import EntityArrivedEvent
from engine.trait import MovableTrait, ReceiverTrait

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
        for entity in game.entities.get_active_entities():
            movable = entity.get_trait(MovableTrait)
            if not movable or not movable.destination:
                continue

            if not movable.path:
                # TODO If the trait has a destination set, and no path, we need to define
                # a path to that destination that overcomes obstacles.
                # For now, we just provide the destination
                movable.set_path([movable.destination])

            if not entity.is_moving:
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
                entity.stop_movement() 
                game.enqueue_event(EntityArrivedEvent(entity_id=entity.id))
            else:
                # STEP: Move toward destination
                ratio = move_distance / distance
                new_x = current_pos[0] + (dx * ratio)
                new_y = current_pos[1] + (dy * ratio)
                entity.position = (new_x, new_y)


class InteractionSystem(System):
    def update(self, game: "Game", dt: float):
        for actor in game.entities.get_active_entities():
            active_trait = actor.active_action_trait
            if not active_trait:
                continue

            if not active_trait.target_id:
                raise ValueError("Active trait has no target")

            target = game.entities.get(active_trait.target_id)
            
            # 1. Target Missing Cleanup
            if not target:
                actor.stop_action()
                continue

            receiver = self._find_matching_receiver(actor.active_action_trait, target)
            if not receiver:
                continue

            # 2. Spatial Validation with Epsilon
            interaction_range = getattr(actor.active_action_trait, 'range', 1.0)
            
            if self._is_in_range(actor, target, interaction_range):
                # If we are in range, stop moving so the interaction is stable
                if actor.is_moving:
                    actor.stop_movement()

                # 3. Logic Execution
                events = []
                events.extend(actor.active_action_trait.on_perform_action(actor, target))
                events.extend(receiver.on_receive_action(actor, target))

                for event in events:
                    game.enqueue_event(event)

    def _find_matching_receiver(self, actor_trait, target_entity):
        for trait in target_entity.traits:
            if isinstance(trait, ReceiverTrait):
                if trait.verb in actor_trait.can_act_on:
                    return trait
        return None

    def _is_in_range(self, actor, target, interaction_range):
        dx = actor.position[0] - target.position[0]
        dy = actor.position[1] - target.position[1]
        distance = sqrt(dx**2 + dy**2)
        # Use Epsilon here so that 'exactly 1.0' distance passes a '1.0' range check
        return distance <= (interaction_range + EPSILON)
