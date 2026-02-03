from engine.core.trait import BaseTrait
from engine.core.entity import BaseEntity, EntityMap, NullTrait


# --- Mocks for Testing ---

class MovableMock(BaseTrait):
    speed: float = 10.0
    
    def move(self): 
        return "moving"

class CombatMock(BaseTrait):
    damage: int = 50

# --- BaseEntity Tests ---

def test_entity_initialization():
    """Test that ID is auto-generated and defaults are set."""
    entity = BaseEntity(asset="player")
    
    assert isinstance(entity.id, str)
    assert len(entity.id) > 0
    assert entity.asset == "player"
    assert entity.position == (0, 0, 0)
    assert entity.traits == []

def test_entity_has_trait():
    """Test checking for trait existence."""
    movable = MovableMock()
    entity = BaseEntity(asset="player", traits=[movable])
    
    assert entity.has_trait(MovableMock) is True
    assert entity.has_trait(CombatMock) is False

def test_entity_get_trait():
    """Test retrieving a trait instance."""
    movable = MovableMock(speed=20.0)
    entity = BaseEntity(asset="player", traits=[movable])
    
    # 1. Retrieve existing
    retrieved = entity.get_trait(MovableMock)
    assert retrieved is not None
    assert retrieved.speed == 20.0
    
    # 2. Retrieve missing
    assert entity.get_trait(CombatMock) is None

def test_entity_as_a_existing():
    """Test the safe caster returns the actual trait if present."""
    movable = MovableMock()
    entity = BaseEntity(asset="player", traits=[movable])
    
    trait = entity.as_a(MovableMock)
    assert not isinstance(trait, NullTrait)
    assert trait.speed == 10.0

def test_entity_as_a_missing_null_safety():
    """
    Test that as_a returns a NullTrait that swallows method calls 
    instead of crashing.
    """
    entity = BaseEntity(asset="player", traits=[])
    
    # 1. Should return a NullTrait, not None
    trait = entity.as_a(MovableMock)
    assert isinstance(trait, NullTrait)
    
    # 2. Attribute access should return a callable (lambda)
    # This simulates calling entity.as_a(Movable).move_to(x,y)
    result = trait.move_to(10, 10) 
    
    # 3. The result of that call is None, but it didn't raise AttributeError
    assert result is None

# --- EntityMap Tests ---

def test_map_add_and_get():
    """Test adding and retrieving entities."""
    entity_map = EntityMap()
    entity = BaseEntity(asset="orc")
    
    entity_map.add(entity)
    
    assert entity_map.get(entity.id) == entity
    assert entity_map.get("non_existent_id") is None

def test_map_remove():
    """Test removing entities."""
    entity_map = EntityMap()
    entity = BaseEntity(asset="orc")
    entity_map.add(entity)
    
    entity_map.remove(entity.id)
    assert entity_map.get(entity.id) is None
    
    # Removing non-existent should be safe
    entity_map.remove("fake_id") 

def test_map_list():
    """Test listing all entities."""
    entity_map = EntityMap()
    e1 = BaseEntity(asset="orc_1")
    e2 = BaseEntity(asset="orc_2")
    
    entity_map.add(e1)
    entity_map.add(e2)
    
    all_entities = entity_map.list()
    assert len(all_entities) == 2
    assert e1 in all_entities
    assert e2 in all_entities

def test_yield_entities_with_trait():
    """
    Test the generator that filters entities by specific traits.
    Crucial for System updates.
    """
    entity_map = EntityMap()
    
    # Setup: 
    # E1: Movable
    # E2: Combat
    # E3: Movable + Combat
    
    e1 = BaseEntity(asset="scout", traits=[MovableMock()])
    e2 = BaseEntity(asset="turret", traits=[CombatMock()])
    e3 = BaseEntity(asset="tank", traits=[MovableMock(), CombatMock()])
    
    entity_map.add(e1)
    entity_map.add(e2)
    entity_map.add(e3)
    
    # 1. Query Movable (Should get E1 and E3)
    movables = list(entity_map.yield_entities_with_trait(MovableMock))
    assert len(movables) == 2
    
    # Verify we get tuples of (Entity, Trait)
    entities_only = [item[0] for item in movables]
    assert e1 in entities_only
    assert e3 in entities_only
    assert e2 not in entities_only

    # 2. Query Combat (Should get E2 and E3)
    fighters = list(entity_map.yield_entities_with_trait(CombatMock))
    assert len(fighters) == 2
    
    # 3. Verify trait instance is correct
    for entity, trait in fighters:
        assert isinstance(trait, CombatMock)

def test_map_clear():
    """Test clearing the map."""
    entity_map = EntityMap()
    entity_map.add(BaseEntity(asset="test"))
    
    entity_map.clear()
    assert len(entity_map.list()) == 0
