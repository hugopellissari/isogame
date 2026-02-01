import random
from game.world.terrain.tile import TerrainType
from game.systems.base import System


class WanderingSystem(System):
    """
    Simple AI: If a unit is standing still, pick a random spot nearby.
    """
    def update(self, world, dt: float):
        for unit in world.entity_map.units:
            # 1. Filter: Only moving units
            if not hasattr(unit, "mover"):
                continue

            # 2. Check: Is it already busy walking?
            if unit.mover.destination is not None:
                continue
                
            # 3. Decision: Pick a random spot
            # Try 5 times to find a valid spot (not water)
            for _ in range(5):
                wander_radius = 5.0
                
                # Random offset from current position
                rand_x = unit.position[0] + random.uniform(-wander_radius, wander_radius)
                rand_z = unit.position[1] + random.uniform(-wander_radius, wander_radius)
                
                # Bounds check (don't walk off the map)
                if not (0 <= rand_x < world.terrain_map.width and 0 <= rand_z < world.terrain_map.height):
                    continue
                    
                # Terrain check (don't walk on water)
                tile_x, tile_z = int(rand_x), int(rand_z)
                tile = world.terrain_map.tile_at(tile_x, tile_z)
                
                if tile and tile.terrain == TerrainType.land:
                    # FOUND A SPOT! Set the destination.
                    # The Movement System will handle the actual walking.
                    unit.mover.destination = (rand_x, rand_z)
                    break
