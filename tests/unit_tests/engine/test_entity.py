import pytest
from unittest.mock import MagicMock
from engine.entity import BaseEntity, EntityMap
from engine.trait import ActorTrait, BaseTrait, InteractionVerb

# --- Mock Implementation for Testing ---

class MockVerbs(InteractionVerb):
    CHOP = "chop"
    EAT = "eat"

class MockChopTrait(ActorTrait):
    can_act_on: list = [MockVerbs.CHOP]
    range: float = 1.5

    def on_perform_action(self, actor_entity, target_entity):
        """Mock implementation of the required abstract method."""
        return ["mock_event"]

# --- Tests ---

def test_set_action_by_verb():
    """Verify set_action finds the correct trait based on the verb."""
    chop_trait = MockChopTrait()
    entity = BaseEntity(position=(0, 0), traits=[chop_trait])
    
    # We pass the VERB, not the trait object
    entity.set_action(MockVerbs.CHOP, "tree_1", (5, 5))
    
    assert entity.active_action_trait == chop_trait
    assert entity.action_target_id == "tree_1"
    assert entity.destination == (5, 5)

def test_set_action_invalid_verb():
    """Verify error is raised if the entity lacks a trait for the requested verb."""
    entity = BaseEntity(position=(0, 0), traits=[]) # No traits
    
    with pytest.raises(ValueError, match="does not have a trait capable of verb"):
        entity.set_action(MockVerbs.CHOP, "target_1")

def test_clear_action_resets_everything():
    """Ensure clear_action wipes all internal action state."""
    entity = BaseEntity(position=(0, 0), traits=[MockChopTrait()])
    entity.set_action(MockVerbs.CHOP, "target_1", (1, 1))
    
    entity.clear_action()

    assert entity.active_action_trait is None
    assert entity.action_target_id is None
    assert entity.is_active is False

def test_entity_map_sync_after_verb_action():
    """Verify EntityMap correctly indexes entity after setting action by verb."""
    emap = EntityMap()
    entity = BaseEntity(position=(0, 0), traits=[MockChopTrait()])
    emap.add(entity)
    
    assert entity.id not in emap.active_ids
    
    entity.set_action(MockVerbs.CHOP, "target_1")
    
    emap.reconcile()
    assert entity.id in emap.active_ids