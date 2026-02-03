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
                # GENERATE HEIGHTS:
                # Let's make it bumpy so we can test your slope logic!
                # We use a simple formula (or random) to create hills.
                
                # Option A: Random Bumps
                h = 0.0
                # if random.random() > 0.7: # 30% chance of a bump
                #     h = random.choice([0.5, 1.0])
                
                # Option B: A simple slope across the map
                h = x * -0.2 
                
                t = Tile(terrain_id="grass", height=h)
                row.append(t)
            new_tiles.append(row)

        return cls(width=width, height=height, tiles=new_tiles, tile_scale=1.0)


entity_map = EntityMap()
entity_map.add(BaseEntity(asset="player", position=(0, 0)))
simple_game = Game(BasicTerrain.generate(10, 10), entity_map)
