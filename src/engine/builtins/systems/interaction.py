from abc import abstractmethod
from math import sqrt
from engine.builtins.traits import ActorTrait, MovableTrait, ReceiverTrait
from engine.core.cqrs import BaseEvent
from engine.core.entity import BaseEntity
from engine.core.game import Game
from engine.core.system import EPSILON, System


class InteractionSystem(System):
    @property
    @abstractmethod
    def actor_trait_subclass(self) -> type[ActorTrait]: ...

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
