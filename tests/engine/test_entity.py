from unittest.mock import MagicMock
from engine.entity import BaseEntity, EntityMap
from engine.trait import ActorTrait, BaseTrait

# --- Mock Traits for testing ---
class MockActorTrait(ActorTrait):
    def on_perform_action(self, actor_entity, target_entity):
        return []


def test_get_trait_helper():
    """Verify we can retrieve specific traits by type."""
    class HealthTrait(BaseTrait): hp: int = 100
    
    h_trait = HealthTrait()
    entity = BaseEntity(position=(0,0), traits=[h_trait])
    
    # Retrieve by type
    found = entity.get_trait(HealthTrait)
    assert found == h_trait
    assert found.hp == 100
    
    # Non-existent type
    assert entity.get_trait(ActorTrait) is None


def test_entity_map_active_tracking():
    """Verify that adding a destination makes an entity 'active' in the map via update()."""
    emap = EntityMap()
    entity = BaseEntity(position=(0,0))
    emap.add(entity) # add() calls update() internally
    
    # Initially idle
    assert entity.id not in emap.active_ids
    
    # Start moving
    entity.destination = (10, 10)
    emap.update(entity) 
    assert entity.id in emap.active_ids
    
    # Stop moving
    entity.destination = None
    emap.update(entity)
    assert entity.id not in emap.active_ids


def test_entity_map_active_action_tracking():
    """Verify that having an active_action_trait makes an entity 'active'."""
    emap = EntityMap()
    
    # Use a concrete mock or the class to satisfy Pydantic/type checks
    mock_trait = MagicMock(spec=MockActorTrait)
    entity = BaseEntity(position=(0,0), active_action_trait=mock_trait)
    
    emap.add(entity) # add() should recognize it's active immediately
    assert entity.id in emap.active_ids


def test_entity_map_update_lifecycle():
    """Verify the full toggle cycle of an entity's activeness."""
    emap = EntityMap()
    entity = BaseEntity(position=(0,0))
    emap.add(entity)
    
    # 1. Start Idle
    assert entity.id not in emap.active_ids
    
    # 2. Add intent (Should become active)
    entity.target_id = "some_tree_id"
    emap.update(entity)
    assert entity.id in emap.active_ids
    
    # 3. Clear intent (Should become idle)
    entity.target_id = None
    emap.update(entity)
    assert entity.id not in emap.active_ids

def test_entity_map_remove_cleans_active_set():
    """Ensure removing an entity also cleans up the active_ids index."""
    emap = EntityMap()
    entity = BaseEntity(position=(0,0), destination=(1,1))
    emap.add(entity)
    
    assert entity.id in emap.active_ids
    
    emap.remove(entity.id)
    assert entity.id not in emap.active_ids
    assert entity.id not in emap.entities
