import pytest
import math
from game.world.world import World
from game.world.entities.units import Lumberjack
from game.systems.movement import MovementSystem

# --- FIXTURES ---

@pytest.fixture
def movement_world():
    """Creates a stripped-down world with ONLY the MovementSystem."""
    # Generate a tiny dummy world
    world = World.generate(width=5, height=5)
    
    # Replace default systems with JUST MovementSystem for isolation
    world.systems = [MovementSystem()]
    
    # Clear random entities so we have a clean slate
    world.entity_map.entities.clear()
    
    return world

@pytest.fixture
def walker():
    """A standard unit starting at (0, 0) with speed=2.0"""
    unit = Lumberjack(position=(0.0, 0.0))
    unit.mover.speed = 2.0
    return unit

# --- TEST CASES ---

def test_unit_moves_towards_destination(movement_world, walker):
    """
    Verify that after one tick, the unit is closer to the target.
    """
    # 1. Setup
    movement_world.entity_map.add(walker)
    target = (10.0, 0.0) # Far away to the right
    walker.mover.destination = target
    
    # 2. Action: Tick for 1 second
    # Speed is 2.0, so it should move exactly 2.0 units to the right
    dt = 1.0
    movement_world.tick(dt)
    
    # 3. Assert
    # Expected position: (2.0, 0.0)
    assert walker.position[0] == 2.0
    assert walker.position[1] == 0.0
    # Destination should still be active (we haven't arrived yet)
    assert walker.mover.destination == target

def test_unit_arrives_and_snaps(movement_world, walker):
    """
    Verify that when the unit is very close (< 0.1), it snaps to the exact target
    and clears its destination.
    """
    # 1. Setup
    movement_world.entity_map.add(walker)
    # Target is very close (0.05 units away)
    target = (0.05, 0.0) 
    walker.mover.destination = target
    
    # 2. Action: Tick (dt=0.1 is enough to cover the distance)
    movement_world.tick(dt=0.1)
    
    # 3. Assert
    # Should snap exactly to (0.05, 0.0), not 0.04999 or 0.2
    assert walker.position == target
    # Destination should be cleared (None) indicating 'Idle'
    assert walker.mover.destination is None

def test_unit_moves_diagonally_correctly(movement_world, walker):
    """
    Verify vector normalization: Moving to (3, 4) should respect speed limit.
    """
    movement_world.entity_map.add(walker)
    
    # Target is a 3-4-5 triangle away (Distance = 5.0)
    walker.mover.destination = (3.0, 4.0)
    walker.mover.speed = 5.0 # Set speed so we could arrive in exactly 1 second
    
    # Action: Tick for 0.5 seconds
    # We should cover half the distance (2.5 units)
    movement_world.tick(dt=0.5)
    
    # Assert
    # We should be exactly halfway: (1.5, 2.0)
    assert math.isclose(walker.position[0], 1.5)
    assert math.isclose(walker.position[1], 2.0)

def test_idle_unit_does_nothing(movement_world, walker):
    """
    Verify that units with destination=None stay put.
    """
    movement_world.entity_map.add(walker)
    start_pos = walker.position
    walker.mover.destination = None
    
    # Tick reasonably hard
    movement_world.tick(dt=1.0)
    
    # Should not have moved
    assert walker.position == start_pos

def test_system_handles_multiple_units(movement_world):
    """
    Verify the system updates multiple units independently in one tick.
    """
    u1 = Lumberjack(position=(0,0))
    u1.mover.destination = (10, 0) # Moving Right
    u1.mover.speed = 1.0

    u2 = Lumberjack(position=(0,0))
    u2.mover.destination = (0, 10) # Moving Up
    u2.mover.speed = 1.0
    
    movement_world.entity_map.add(u1)
    movement_world.entity_map.add(u2)
    
    movement_world.tick(dt=1.0)
    
    # u1 should be at (1, 0)
    assert u1.position == (1.0, 0.0)
    # u2 should be at (0, 1)
    assert u2.position == (0.0, 1.0)
