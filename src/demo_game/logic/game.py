from engine.terrain import TerrainMap, Tile
from engine.game import Game
from engine.entity import EntityMap, BaseEntity

class BasicTerrain(TerrainMap):
    @classmethod
    def generate(cls, width: int, height: int) -> "BasicTerrain":
        new_tiles = []
        for x in range(width):
            row = []
            for z in range(height):
                t = Tile(terrain_id="grass", height=0)
                row.append(t)
            new_tiles.append(row)

        return cls(width=width, height=height, tiles=new_tiles, tile_scale=1.0)


entity_map = EntityMap()
entity_map.add(BaseEntity(asset="player", position=(0, 0)))
simple_game = Game(BasicTerrain.generate(10, 10), entity_map)
