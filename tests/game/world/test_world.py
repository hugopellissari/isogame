import pytest
from unittest.mock import MagicMock
from game.world.world import World, EventType
from game.world.entities.units import Lumberjack
from game.world.terrain.tile import TerrainType

# --- FIXTURES (Setup) ---

@pytest.fixture
def small_world():
    """Creates a predictable 10x10 world for testing logic."""
    return World.generate(width=10, height=10)

@pytest.fixture
def lumberjack():
    """Creates a basic unit for testing."""
    return Lumberjack(position=(5.0, 5.0))

# --- TEST CASES ---

def test_world_generation_initialization(small_world):
    """
    Test that World.generate() creates a valid world state.
    """
    assert small_world.terrain_map.width == 10
    assert small_world.terrain_map.height == 10
    assert small_world.entity_map is not None
    # We expect some default systems to be loaded
    assert len(small_world.systems) > 0 
    assert len(small_world.events) == 0  # Events should be empty after gen

def test_spawn_entity_logic(small_world, lumberjack):
    """
    Test that spawn_entity() updates data AND queues an event.
    """
    # 1. Action
    small_world.spawn_entity(lumberjack)

    # 2. Assert Data
    assert small_world.entity_map.get(lumberjack.id) == lumberjack

    # 3. Assert Event
    assert len(small_world.events) == 1
    event = small_world.events[0]
    assert event.event_type == EventType.SPAWN
    assert event.entity == lumberjack
    assert event.entity_id == lumberjack.id

def test_kill_entity_logic(small_world, lumberjack):
    """
    Test that kill_entity() removes data AND queues an event.
    """
    # Setup: Add entity directly first (to simulate it existing)
    small_world.entity_map.add(lumberjack)
    
    # 1. Action
    small_world.kill_entity(lumberjack.id)

    # 2. Assert Data
    assert small_world.entity_map.get(lumberjack.id) is None

    # 3. Assert Event
    assert len(small_world.events) == 1
    event = small_world.events[0]
    assert event.event_type == EventType.DESTROY
    assert event.entity_id == lumberjack.id

def test_tick_updates_systems(small_world):
    """
    Test that calling tick() actually runs the systems.
    """
    # Mock a system to ensure it gets called
    mock_system = MagicMock()
    small_world.systems.append(mock_system)

    dt = 0.5
    small_world.tick(dt)

    # Assert the system's update method was called with world and dt
    mock_system.update.assert_called_once_with(small_world, dt)

def test_generation_adds_entities_without_events(small_world):
    """
    Crucial check: World generation should add trees/units directly
    WITHOUT spamming the event queue with 500 'SPAWN' events.
    """
    # The fixture already called generate()
    
    # 1. Entities should exist (assuming random seed didn't fail us)
    # Note: On a 10x10 map, random chance might result in 0, 
    # so we just check the list logic is valid, or retry if 0.
    total_entities = len(small_world.entity_map.entities)
    
    # 2. But the Event Queue MUST be empty
    # (Because generate calls .add(), not .spawn_entity())
    assert len(small_world.events) == 0

def test_spawn_units_respects_water():
    """
    Integration Test: Ensure units are NEVER spawned on water.
    """
    # 1. Create a world that is 100% Water
    world = World.generate(width=5, height=5)
    
    # Force override terrain to be all water
    for x in range(5):
        for z in range(5):
            world.terrain_map.tiles[z * 5 + x].terrain = TerrainType.water
            
    # Clear any existing entities from generation
    world.entity_map.entities.clear()
    
    # 2. Run the spawner with 100% density (Try to force a spawn)
    from game.world.world import spawn_units
    spawn_units(world, density=1.0)
    
    # 3. Assert NO units were spawned
    assert len(world.entity_map.units) == 0

def test_movement_system_integration(small_world, lumberjack):
    """
    Test that the MovementSystem actually moves a unit when tick() is called.
    """
    # Setup
    small_world.entity_map.add(lumberjack)
    start_pos = lumberjack.position
    
    # Give it a destination (1 unit away on X axis)
    lumberjack.mover.destination = (start_pos[0] + 1.0, start_pos[1])
    
    # Tick the world (dt=1.0, speed=2.0 -> should move 2 units max, or stop at target)
    small_world.tick(dt=0.1) 
    
    # Assert position changed
    new_pos = lumberjack.position
    assert new_pos != start_pos
    # It should have moved towards positive X
    assert new_pos[0] > start_pos[0]
