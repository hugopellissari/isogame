from unittest.mock import MagicMock

import pytest

from engine.entity import BaseEntity, EntityMap
from engine.game import Game
from engine.system import MovementSystem
from engine.trait import MovableTrait


class EntityArrivedEvent: # Mocking the event for the test
    def __init__(self, entity_id):
        self.entity_id = entity_id


def test_movement_step():
    """Verify that the entity moves closer to the destination based on speed and dt."""
    system = MovementSystem()
    emap = EntityMap()
    game = Game(MagicMock(), emap) # Terrain can stay mocked
    
    # Setup entity
    entity = BaseEntity(position=(0, 0), traits=[MovableTrait(speed=2.0)], asset="lumberjack")
    entity.move_to((10, 0))
    emap.add(entity)
    
    # 1. Sync the map (This replaces the manual mock setup)
    emap.reconcile()
    
    # 2. Update (dt = 1.0, speed = 2.0 -> should move 2 units)
    system.update(game, 1.0)
    
    assert entity.position[0] == pytest.approx(2.0)
    assert entity.is_moving is True


def test_movement_arrival():
    """Verify that entity snaps to destination and clears flag."""
    system = MovementSystem()
    emap = EntityMap()
    game = Game(MagicMock(), emap)
    
    entity = BaseEntity(position=(9.5, 0), traits=[MovableTrait(speed=1.0)], asset="lumberjack")
    entity.move_to((10, 0))
    emap.add(entity)
    emap.reconcile()
    
    # Should arrive in 1.0s (covers 1.0 distance, only needs 0.5)
    system.update(game, 1.0)
    
    assert entity.position == (10.0, 0.0)
    assert entity.is_moving is False
