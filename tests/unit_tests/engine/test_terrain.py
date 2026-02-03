from engine.terrain import TerrainGenerationParams, TerrainMap, TerrainType, Tile


# Mock implementation for tests
class GameTerrain(TerrainType):
    GRASS = "grass"
    WATER = "water"


class GameParams(TerrainGenerationParams):
    default: GameTerrain = GameTerrain.GRASS


class GameMap(TerrainMap):
    @classmethod
    def generate(cls, width: int, height: int, params: GameParams) -> "GameMap":
        grid = [
            [Tile(terrain=params.default) for _ in range(height)] for _ in range(width)
        ]
        return cls(width, height, grid)


def test_terrain_map_standard_class_init():
    """Verify the standard class constructor works as expected."""
    tiles = [[Tile(terrain=GameTerrain.GRASS)]]
    t_map = GameMap(width=1, height=1, tiles=tiles)

    assert t_map.width == 1
    assert t_map.tile_at(0, 0).terrain == GameTerrain.GRASS


def test_terrain_neighbors_boundary():
    """Ensure neighbors don't leak outside the width/height."""
    t_map = GameMap.generate(2, 2, GameParams())

    # Corner (0,0) should only have (1,0) and (0,1)
    adj = list(t_map.neighbors(0, 0))
    assert len(adj) == 2

    coords = {(n[0], n[1]) for n in adj}
    assert (1, 0) in coords
    assert (0, 1) in coords


def test_tile_at_out_of_bounds():
    """Verify safe handling of out-of-bounds requests."""
    t_map = GameMap.generate(5, 5, GameParams())
    assert t_map.tile_at(-1, 2) is None
    assert t_map.tile_at(5, 5) is None
