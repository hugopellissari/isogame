from abc import abstractmethod
from typing import TYPE_CHECKING

from engine.trait import MovableTrait, ReceiverTrait

if TYPE_CHECKING:
    from engine.game import Game

class System:
    """
    Systems control changes of state of the game. This is the only place where we update
    entities and emit events to the world. It is what handles the countinous actions triggered
    by the events.
    """
    @abstractmethod
    def update(self, game: "Game", dt: float):
        ...

class MovementSystem(System):
    """
    The universal engine system for spatial translation. 
    It moves any entity that has a MovableTrait and a set destination.
    """
    def update(self, game: "Game", dt: float):
        for entity in game.entity_map.entities.values():
            # 1. Check if the entity is capable and intends to move
            if not entity.is_moving:
                continue
            
            # 2. Get the movement capability (MovableTrait)
            # We assume a helper exists to find the trait by type
            movable = entity.get_trait(MovableTrait)
            if not movable:
                continue

            # 3. Calculate Vector and Distance
            current_pos = entity.position
            dest_pos = entity.destination
            
            dx = dest_pos[0] - current_pos[0]
            dy = dest_pos[1] - current_pos[1]
            distance = (dx**2 + dy**2)**0.5

            # 4. Move or Arrive
            move_distance = movable.speed * dt

            if distance <= move_distance:
                # Arrived! 
                entity.position = dest_pos
                entity.destination = None # This triggers is_moving = False
                
                # Emit an Event so other systems know the journey ended
                game.enqueue_event(EntityArrivedEvent(entity_id=entity.id))
            else:
                # Step toward destination
                ratio = move_distance / distance
                new_x = current_pos[0] + dx * ratio
                new_y = current_pos[1] + dy * ratio
                entity.position = (new_x, new_y)


class InteractionSystem(System):
    """
    Coordinates the handshake between an ActorTrait and a ReceiverTrait.
    It validates spatial requirements and triggers the logic defined in the traits.
    """
    def update(self, game: "Game", dt: float):
        # We iterate through entities that are currently 'trying' to do something
        for actor in game.entity_map.entities.values():
            if not actor.active_action_trait or not actor.target_id:
                continue

            # 1. Resolve the Target
            target = game.entity_map.get(actor.target_id)
            if not target:
                # Target is gone (deleted or despawned)
                actor.target_id = None
                actor.active_action_trait = None
                continue

            # 2. Find the matching ReceiverTrait on the target
            # An ActorTrait might be "CanChop", we need the target's "Choppable" trait
            receiver = self._find_matching_receiver(actor.active_action_trait, target)
            if not receiver:
                # The target can't be interacted with in this way
                continue

            # 3. Spatial Validation (The "Reality Check")
            # For simplicity, we assume traits have a 'range' attribute.
            # If not in range, we let the MovementSystem handle the 'Chasing'.
            if self._is_in_range(actor, target, getattr(actor.active_action_trait, 'range', 1.5)):
                # 4. Logic Execution (The Handshake)
                # We collect events from both sides of the interaction
                events = []
                
                # Actor side: "I swung my axe" (maybe durability loss)
                events.extend(actor.active_action_trait.on_perform_action(actor, target))
                
                # Receiver side: "I got hit" (maybe health loss)
                events.extend(receiver.on_receive_action(actor, target))

                # 5. Emit to the World
                for event in events:
                    game.enqueue_event(event)

    def _find_matching_receiver(self, actor_trait, target_entity):
        """Finds a ReceiverTrait on the target that matches the Actor's intent."""
        # This assumes your ActorTrait has a list of verbs it can perform
        for trait in target_entity.traits:
            if isinstance(trait, ReceiverTrait):
                if trait.verb in actor_trait.can_act_on:
                    return trait
        return None

    def _is_in_range(self, actor, target, interaction_range):
        from math import sqrt
        dx = actor.position[0] - target.position[0]
        dy = actor.position[1] - target.position[1]
        return sqrt(dx**2 + dy**2) <= interaction_range
