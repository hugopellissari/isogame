import pytest
from unittest.mock import MagicMock

from engine.entity import BaseEntity
from engine.system import InteractionSystem
from engine.trait import ActorTrait, ReceiverTrait, InteractionVerb


class Verb(InteractionVerb):
    CHOP = "chop"


# Mocking concrete traits for the test handshake
class CanChop(ActorTrait):
    range: float = 2.0
    can_act_on: list = [Verb.CHOP]
    def on_perform_action(self, actor, target): return ["axe_swing_event"]

class Choppable(ReceiverTrait):
    verb: InteractionVerb = Verb.CHOP
    def on_receive_action(self, actor, target): return ["wood_chip_event"]

def test_interaction_handshake_in_range():
    """Verify that events are emitted when actor is within range of target."""
    system = InteractionSystem()
    game = MagicMock()
    
    chop_trait = CanChop()
    actor = BaseEntity(position=(0, 0), active_action_trait=chop_trait, target_id="tree")
    
    target = BaseEntity(position=(1, 0)) # Within 2.0 range
    target.traits = [Choppable()]
    
    game.entity_map.get.side_effect = lambda id: target if id == "tree" else None
    game.entity_map.entities = {"lumberjack": actor}
    
    system.update(game, 0.1)
    
    # Should have enqueued both the actor event and the receiver event
    assert game.enqueue_event.call_count == 2
    calls = [call[0][0] for call in game.enqueue_event.call_args_list]
    assert "axe_swing_event" in calls
    assert "wood_chip_event" in calls

def test_interaction_out_of_range():
    """Verify no interaction occurs if the target is too far."""
    system = InteractionSystem()
    game = MagicMock()
    
    chop_trait = CanChop()
    actor = BaseEntity(position=(0, 0), active_action_trait=chop_trait, target_id="tree")
    target = BaseEntity(position=(10, 0)) # Out of 2.0 range
    target.traits = [Choppable()]
    
    game.entity_map.get.return_value = target
    game.entity_map.entities = {"lumberjack": actor}
    
    system.update(game, 0.1)
    
    game.enqueue_event.assert_not_called()

def test_interaction_target_missing():
    """Verify that if target is gone, the actor's intent is cleared."""
    system = InteractionSystem()
    game = MagicMock()
    
    actor = BaseEntity(position=(0,0), active_action_trait=CanChop(), target_id="dead_tree")
    game.entity_map.get.return_value = None # Target not found
    game.entity_map.entities = {"lumberjack": actor}
    
    system.update(game, 0.1)
    
    assert actor.target_id is None
    assert actor.active_action_trait is None
