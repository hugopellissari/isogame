import pytest
from unittest.mock import MagicMock
from engine.entity import BaseEntity, EntityMap
from engine.game import Game
from engine.system import InteractionSystem
from engine.trait import ActorTrait, ReceiverTrait, InteractionVerb
from tests.integration_tests.test_game import MyVerbs

class Verb(InteractionVerb):
    CHOP = "chop"

# Concrete traits for testing
class CanChop(ActorTrait):
    range: float = 2.0
    can_act_on: list = [Verb.CHOP]
    def on_perform_action(self, actor, target): 
        return ["axe_swing_event"]

class Choppable(ReceiverTrait):
    verb: InteractionVerb = Verb.CHOP
    def on_receive_action(self, actor, target): 
        return ["wood_chip_event"]

def test_interaction_handshake_in_range():
    system = InteractionSystem()
    emap = EntityMap()
    game = Game(MagicMock(), emap)
    
    # Standardize Verb: Use Verb.CHOP consistently
    actor = BaseEntity(position=(0, 0), traits=[CanChop(range=2.0)], asset="lumberjack")
    actor.set_action(Verb.CHOP, "tree_1") 

    target = BaseEntity(id="tree_1", position=(1, 0), traits=[Choppable()], asset="tree")
    
    emap.add(actor)
    emap.add(target)
    emap.reconcile()
    
    system.update(game, 0.1)
    assert len(game.event_queue) == 2


def test_interaction_out_of_range():
    """Verify no interaction occurs if the target is too far."""
    system = InteractionSystem()
    game = MagicMock()
    
    actor = BaseEntity(position=(0, 0), traits=[CanChop()], asset="lumberjack")
    actor.set_action(Verb.CHOP, "tree_1")
    
    target = BaseEntity(position=(10, 0), asset="tree") # Way out of range
    target.traits = [Choppable()]
    
    game.entity_map.get.return_value = target
    game.entity_map.entities = {"lumberjack": actor}
    
    system.update(game, 0.1)
    
    game.enqueue_event.assert_not_called()


def test_interaction_target_missing_clears_action():
    system = InteractionSystem()
    game = MagicMock() # Still using mock here, so we must prime it
    
    actor = BaseEntity(position=(0, 0), traits=[CanChop()], asset="lumberjack")
    actor.set_action(Verb.CHOP, "dead_tree")
    
    # PRIME THE MOCK: Tell it to return our actor in the loop
    game.entity_map.get_active_entities.return_value = [actor]
    game.entity_map.get.return_value = None 
    
    system.update(game, 0.1)
    
    assert actor.active_action_trait is None
