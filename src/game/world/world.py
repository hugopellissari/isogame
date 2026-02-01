from enum import Enum
import random

from pydantic import BaseModel, Field
from game.world.entities.mapping import EntityMap
from game.world.terrain.mapping import TerrainMap
from game.world.terrain.tile import TerrainType
from game.world.entities.base import BaseEntity
from game.world.entities.tree import Tree
from game.world.entities.units import Lumberjack
from game.systems.base import System
from game.systems.movement import MovementSystem
from game.systems.wandering import WanderingSystem


class EventType(Enum):
    SPAWN = "spawn"
    DESTROY = "destroy"


class Event(BaseModel):
    entity_id: str # We only need ID for destroy
    entity: BaseEntity | None = None # We need full object for spawn
    event_type: EventType


class World(BaseModel):
    terrain_map: TerrainMap
    entity_map: EntityMap
    events: list[Event] = Field(default_factory=list, exclude=True)
    systems: list[System] = Field(default_factory=list, exclude=True)

    def tick(self, dt: float):
        print(f"Ticking {len(self.systems)} systems...")
        for system in self.systems:
            system.update(self, dt)

    def spawn_entity(self, entity: BaseEntity):
        # 1. Add to Data
        self.entity_map.add(entity)
        
        # 2. Queue Event
        self.events.append(Event(
            entity=entity, 
            entity_id=entity.id, 
            event_type=EventType.SPAWN
        ))

    def kill_entity(self, entity_id: str):
        # 1. Remove from Data (Instant lookup!)
        if self.entity_map.get(entity_id):
            self.entity_map.remove(entity_id)
            
            # 2. Queue Event
            self.events.append(Event(
                entity_id=entity_id, 
                event_type=EventType.DESTROY
            ))

    @classmethod
    def generate(cls, width: int, height: int) -> "World":

        terrain = TerrainMap.generate(width, height)
        entities = EntityMap()
        world = cls(
            terrain_map=terrain, 
            entity_map=entities,
            systems=[
                WanderingSystem(),
                MovementSystem(),
            ]
        )
        
        spawn_trees(world)
        spawn_units(world)
        return world


def spawn_units(world: World, density: float = 0.005) -> None:
    """
    Procedurally spawn units (Lumberjacks) on valid land tiles.
    Density is much lower than trees because units are rare.
    """
    for x in range(world.terrain_map.width):
        for z in range(world.terrain_map.height):
            tile = world.terrain_map.tile_at(x, z)
            
            # Don't spawn in water
            if tile.terrain != TerrainType.land:
                continue

            # Random chance to spawn
            if random.random() < density:
                # Add a single unit at the center of the tile
                # (You can add random offset if you want, but center is cleaner for units)
                lumberjack = Lumberjack(
                    position=(x + 0.5, z + 0.5) 
                )
                world.entity_map.add(lumberjack)


def spawn_trees(world: World, density: float = 0.08) -> None:
    for x in range(world.terrain_map.width):
        for z in range(world.terrain_map.height):
            tile = world.terrain_map.tile_at(x, z)

            if tile.terrain != TerrainType.land:
                continue

            if random.random() < density:
                count = random.randint(2, 5)

                for _ in range(count):
                    world.entity_map.add(
                        Tree(
                            position=(
                                x + random.uniform(-0.4, 0.4),
                                z + random.uniform(-0.4, 0.4),
                            )
                        )
                    )
