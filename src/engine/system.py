from abc import abstractmethod
from typing import TYPE_CHECKING, Type
from math import sqrt

from engine.cqrs import EntityArrivedEvent, BaseEvent
from engine.entity import BaseEntity
from engine.trait import ActorTrait, MovableTrait, ReceiverTrait, GroundableTrait

if TYPE_CHECKING:
    from engine.game import Game

# Used to prevent floating point "micro-misses"
EPSILON = 1e-6


class System:
    @abstractmethod
    def update(self, game: "Game", dt: float): ...


class MovementSystem(System):
    def update(self, game: "Game", dt: float):
        for entity, movable in game.entities.yield_entities_with_trait(MovableTrait):
            if not movable.destination or not movable.is_moving:
                continue

            if not movable.path:
                movable.set_path([movable.destination])

            # Peek target
            target_pos = movable.path[-1]

            # --- COORDINATES (Pure 2D X/Z) ---
            current_x, _, current_z = entity.position  # Ignore Y completely!
            target_x, target_z = target_pos[0], target_pos[1]

            dx = target_x - current_x
            dz = target_z - current_z

            distance = sqrt(dx**2 + dz**2)
            move_distance = movable.speed * dt

            # CHECK ARRIVAL
            if distance <= move_distance + EPSILON:
                # 1. Snap Logic X/Z only (Let SnappingSystem handle Y later)
                # We keep the current Y for now, or set it to 0, it doesn't matter
                # because TerrainSnappingSystem runs next.
                entity.position = (target_x, entity.position[1], target_z)

                movable.path.pop()
                if not movable.path:
                    movable.stop_movement()
                    game.enqueue_event(EntityArrivedEvent(entity_id=entity.id))
            else:
                # MOVE
                ratio = move_distance / distance
                new_x = current_x + (dx * ratio)
                new_z = current_z + (dz * ratio)

                # Update Position (Preserve current Y)
                entity.position = (new_x, entity.position[1], new_z)


class InteractionSystem(System):
    @property
    @abstractmethod
    def actor_trait_subclass(self) -> Type[ActorTrait]: ...

    @abstractmethod
    def handle_action(
        self, actor: BaseEntity, target: BaseEntity
    ) -> list[BaseEvent]: ...

    def can_act(self, actor: BaseEntity, target: BaseEntity) -> bool:
        """Subclasses can override this for specific logic (e.g., cooldowns)"""
        return True

    def _can_act(self, actor: BaseEntity, target: BaseEntity):
        verb = self.actor_trait_subclass.verb

        # Check if target has a ReceiverTrait that matches the verb
        # (e.g. Actor wants to 'CHOP', Target must be 'CHOPPABLE')
        has_matching_trait = False
        for trait in target.traits:
            if isinstance(trait, ReceiverTrait) and trait.verb == verb:
                has_matching_trait = True
                break

        if not has_matching_trait:
            return False

        return self.can_act(actor, target)

    def update(self, game: "Game", dt: float):
        for actor, action_trait in game.entities.yield_entities_with_trait(
            self.actor_trait_subclass
        ):
            if not action_trait:
                continue

            if not action_trait.target_id:
                # No target selected, nothing to do
                continue

            target = game.entities.get(action_trait.target_id)
            if not target:
                # Target died or vanished
                action_trait.stop()
                continue

            if not self._can_act(actor, target):
                action_trait.stop()
                continue

            # 2. Spatial Validation (Range Check)
            if not self._is_in_range(actor, target, action_trait.range):
                # If too far, delegate to Movement System
                # We assume target.position includes (x, y, z), but move_to expects (x, z)
                target_dest = (target.position[0], target.position[2])
                actor.as_a(MovableTrait).move_to(target_dest)

            else:
                # We are in range!

                # Stop moving to stabilize the interaction
                movable = actor.as_a(MovableTrait)
                if movable and movable.is_moving:
                    movable.stop_movement()

                # 3. Logic Execution
                events = self.handle_action(actor, target)
                for event in events:
                    game.enqueue_event(event)

                # Optionally clear the target if action is "one-shot"
                # action_trait.target_id = None

    def _is_in_range(self, actor, target, interaction_range):
        # Calculate 2D distance on ground plane (ignoring height difference)
        # Often better for interactions (you can chop a tree even if the root is slightly below you)
        dx = actor.position[0] - target.position[0]
        dz = actor.position[2] - target.position[2]  # Index 2 is Z

        distance = sqrt(dx**2 + dz**2)
        return distance <= (interaction_range + EPSILON)


class TerrainSnappingSystem(System):
    def update(self, game: "Game", dt: float):
        for entity, _ in game.entities.yield_entities_with_trait(GroundableTrait):

            # 1. Get current 2D position (Unity Standard: X and Z)
            current_x, current_y, current_z = entity.position

            # 2. Calculate the correct Height (Y)
            # The system asks the Terrain Map logic for the height at this X, Z
            target_y = game.terrain.get_height(current_x, current_z)

            # 3. Apply Snapping (Instant Gravity)
            # Optimization: Only write if the difference is significant
            if abs(current_y - target_y) > EPSILON:
                entity.position = (current_x, target_y, current_z)
