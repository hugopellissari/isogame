import pytest
import math
from game.world.world import World
from game.world.entities.units import Lumberjack
from game.world.terrain.tile import TerrainType
from game.systems.wandering import WanderingSystem

# --- FIXTURES ---

@pytest.fixture
def wandering_world():
    """Creates a world with ONLY the WanderingSystem."""
    # 20x20 world so we have space to wander
    world = World.generate(width=20, height=20)
    world.systems = [WanderingSystem()]
    world.entity_map.entities.clear()
    
    # Force map to be 100% LAND by default for easy testing
    for tile_row in world.terrain_map.tiles:
        for tile in tile_row:
            tile.terrain = TerrainType.land
        
    return world

@pytest.fixture
def idle_unit():
    """Unit at center (10, 10) with NO destination."""
    return Lumberjack(position=(10.0, 10.0))

# --- TEST CASES ---

def test_idle_unit_gets_destination(wandering_world, idle_unit):
    """
    Verify that an idle unit on valid land eventually picks a spot.
    """
    wandering_world.entity_map.add(idle_unit)
    
    # It should be None initially
    assert idle_unit.mover.destination is None
    
    # Tick the system
    wandering_world.tick(dt=1.0)
    
    # It should now have a destination
    assert idle_unit.mover.destination is not None
    
    # Validate the destination is DIFFERENT from current position
    dest = idle_unit.mover.destination
    assert dest != idle_unit.position

def test_busy_unit_is_ignored(wandering_world, idle_unit):
    """
    Verify that if a unit is already walking somewhere, 
    the wandering system doesn't override it.
    """
    wandering_world.entity_map.add(idle_unit)
    
    # Manually give it a specific job
    important_job = (15.0, 15.0)
    idle_unit.mover.destination = important_job
    
    # Tick the system
    wandering_world.tick(dt=1.0)
    
    # Verify it didn't get distracted
    assert idle_unit.mover.destination == important_job

def test_unit_respects_wander_radius(wandering_world, idle_unit):
    """
    Verify the random spot is actually nearby (within 5 units),
    not teleporting across the map.
    """
    wandering_world.entity_map.add(idle_unit)
    
    # Run loop
    wandering_world.tick(dt=1.0)
    
    if idle_unit.mover.destination:
        dest_x, dest_z = idle_unit.mover.destination
        start_x, start_z = idle_unit.position
        
        # Check X distance
        assert abs(dest_x - start_x) <= 5.0
        # Check Z distance
        assert abs(dest_z - start_z) <= 5.0

def test_water_avoidance_logic(wandering_world, idle_unit):
    """
    Verify that if the unit is surrounded by water, it refuses to pick a spot.
    """
    wandering_world.entity_map.add(idle_unit)
    
    # 1. Terraform the map into an Ocean
    for tile_row in wandering_world.terrain_map.tiles:
        for tile in tile_row:
            tile.terrain = TerrainType.water
            
    # 2. Tick the system
    # Since all 5 random attempts will hit water, it should give up.
    wandering_world.tick(dt=1.0)
    
    # 3. Assert
    # It should remain Idle (None) because no valid land was found
    assert idle_unit.mover.destination is None

def test_boundary_check(wandering_world, idle_unit):
    """
    Verify unit doesn't pick a spot outside the map (e.g., -5, -5).
    """
    # Place unit at the very edge of the map (0, 0)
    idle_unit.position = (0.0, 0.0)
    wandering_world.entity_map.add(idle_unit)
    
    # Tick multiple times to try and force a bad roll
    for _ in range(10):
        # Reset destination to force a new pick
        idle_unit.mover.destination = None
        wandering_world.tick(dt=1.0)
        
        dest = idle_unit.mover.destination
        if dest:
            # Should NEVER be negative
            assert dest[0] >= 0
            assert dest[1] >= 0
            # Should NEVER be > width
            assert dest[0] < wandering_world.terrain_map.width
            assert dest[1] < wandering_world.terrain_map.height
