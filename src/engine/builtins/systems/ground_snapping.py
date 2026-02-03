from engine.builtins.traits import GroundableTrait
from engine.core.game import Game
from engine.core.system import EPSILON, System


class TerrainSnappingSystem(System):
    def update(self, game: "Game", dt: float):
        for entity, _ in game.entities.yield_entities_with_trait(GroundableTrait):

            # 1. Get current 2D position (Unity Standard: X and Z)
            current_x, current_y, current_z = entity.position

            # 2. Calculate the correct Height (Y)
            # The system asks the Terrain Map logic for the height at this X, Z
            target_y = game.terrain.get_height(current_x, current_z)

            # 3. Apply Snapping (Instant Gravity)
            # Optimization: Only write if the difference is significant
            if abs(current_y - target_y) > EPSILON:
                entity.position = (current_x, target_y, current_z)
