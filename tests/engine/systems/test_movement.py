from unittest.mock import MagicMock

from engine.entity import BaseEntity
from engine.system import MovementSystem
from engine.trait import MovableTrait


class EntityArrivedEvent: # Mocking the event for the test
    def __init__(self, entity_id):
        self.entity_id = entity_id


def test_movement_step():
    """Verify that the entity moves closer to the destination based on speed and dt."""
    system = MovementSystem()
    game = MagicMock()
    
    # Setup entity at (0,0) moving to (10,0) with speed 2.0
    entity = BaseEntity(position=(0, 0), destination=(10, 0))
    entity.traits = [MovableTrait(speed=2.0)]
    game.entity_map.entities = {"unit": entity}
    
    # Update with dt = 1.0 (should move 2 units)
    system.update(game, 1.0)
    
    assert entity.position == (2.0, 0.0)
    assert entity.is_moving is True


def test_movement_arrival():
    """Verify that entity snaps to destination and clears flag when close enough."""
    system = MovementSystem()
    game = MagicMock()
    
    # Entity is 0.5 units away, speed is 1.0, dt is 1.0 (should arrive)
    entity = BaseEntity(position=(9.5, 0), destination=(10, 0))
    entity.traits = [MovableTrait(speed=1.0)]
    game.entity_map.entities = {"unit": entity}
    
    system.update(game, 1.0)
    
    assert entity.position == (10, 0)
    assert entity.destination is None
    assert entity.is_moving is False
    # Verify the event was enqueued
    game.enqueue_event.assert_called_once()
