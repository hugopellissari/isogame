from engine.commons import Position
from engine.system import MovementSystem, TerrainSnappingSystem
from engine.terrain import TerrainMap, Tile
from engine.game import Game
from engine.entity import EntityMap, BaseEntity
from engine.trait import MovableTrait
from engine.cqrs import BaseCommand


class BasicTerrain(TerrainMap):
    @classmethod
    def generate(cls, width: int, height: int, params=None) -> "BasicTerrain":
        new_tiles = []

        # STEEPNESS CONTROL:
        # 0.0 = Flat
        # 0.5 = Gentle Slope
        # 1.0 = 45 Degree Angle (Steep)
        slope_factor = 0.2

        for x in range(width):
            row = []
            for z in range(height):
                # SIMPLE RAMP LOGIC:
                # The further 'Right' (X) you go, the higher the ground gets.
                # We use float() to ensure we store decimal heights for smoothness.
                y_height = float(x) * slope_factor

                # Option B: Corner Ramp (Diagonally up)
                # y_height = (x + z) * 0.25

                t = Tile(terrain_id="grass", height=y_height)
                row.append(t)
            new_tiles.append(row)

        return cls(width=width, height=height, tiles=new_tiles, tile_scale=1.0)


entity_map = EntityMap()
player_entity = BaseEntity(asset="player", position=(0, 0, 0), traits=[MovableTrait()])
entity_map.add(player_entity)

simple_game = Game(
    terrain=BasicTerrain.generate(10, 10),
    entities=entity_map,
    systems=[TerrainSnappingSystem(), MovementSystem()],
)


class MoveCommand(BaseCommand):
    destination: Position


def move_handler(game: Game, command: MoveCommand):
    player_entity.as_a(MovableTrait).move_to(command.destination)


simple_game.command_processor.register_handler(MoveCommand, move_handler)
