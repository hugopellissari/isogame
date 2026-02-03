import pytest
from dataclasses import dataclass
from engine.core.terrain import TerrainMap, Tile, TerrainGenerationParams

# --- Mocks & Concrete Implementations ---

@dataclass
class MockTerrainParams(TerrainGenerationParams):
    pass

class ConcreteTerrainMap(TerrainMap):
    """
    A concrete implementation of the abstract TerrainMap class 
    required to instantiate it for testing.
    """
    @classmethod
    def generate(cls, width: int, height: int, params: TerrainGenerationParams | None = None) -> "ConcreteTerrainMap":
        # Creates a flat terrain by default
        tiles = [[Tile(terrain_id="grass", height=0.0) for _ in range(height)] for _ in range(width)]
        return cls(width, height, tiles, tile_scale=1.0)

# --- Fixtures ---

@pytest.fixture
def simple_terrain():
    """
    Creates a 3x3 grid with predictable heights.
    Scale is 10.0 to make math easy (1 grid unit = 10 world units).
    
    Grid Heights:
    (0,0)=0.0  (1,0)=10.0 (2,0)=20.0
    (0,1)=0.0  (1,1)=10.0 (2,1)=20.0
    (0,2)=0.0  (1,2)=10.0 (2,2)=20.0
    """
    width, height = 3, 3
    scale = 10.0
    
    tiles = []
    for x in range(width):
        row = []
        for z in range(height):
            # Height increases by 10 for every X step
            h = float(x * 10) 
            row.append(Tile(terrain_id="grass", height=h))
        tiles.append(row)
        
    return ConcreteTerrainMap(width, height, tiles, tile_scale=scale)

# --- Function-Based Tests ---

def test_in_bounds(simple_terrain):
    # Valid bounds
    assert simple_terrain.in_bounds(0, 0)
    assert simple_terrain.in_bounds(2, 2)
    
    # Invalid bounds (Negative)
    assert not simple_terrain.in_bounds(-1, 0)
    assert not simple_terrain.in_bounds(0, -1)
    
    # Invalid bounds (Overflow)
    assert not simple_terrain.in_bounds(3, 0)
    assert not simple_terrain.in_bounds(0, 3)

def test_tile_at_valid(simple_terrain):
    tile = simple_terrain.tile_at(1, 1)
    assert tile is not None
    assert tile.height == 10.0

def test_tile_at_invalid(simple_terrain):
    assert simple_terrain.tile_at(99, 99) is None

def test_neighbors_center(simple_terrain):
    """Test neighbors for a central tile (should have 4)."""
    # (1, 1) neighbors: (0,1), (2,1), (1,0), (1,2)
    neighbors = list(simple_terrain.neighbors(1, 1))
    coords = sorted([(n[0], n[1]) for n in neighbors])
    
    assert len(neighbors) == 4
    assert coords == [(0, 1), (1, 0), (1, 2), (2, 1)]

def test_neighbors_corner(simple_terrain):
    """Test neighbors for a corner tile (should have 2)."""
    # (0, 0) neighbors: (1,0) and (0,1)
    neighbors = list(simple_terrain.neighbors(0, 0))
    coords = sorted([(n[0], n[1]) for n in neighbors])
    
    assert len(neighbors) == 2
    assert coords == [(0, 1), (1, 0)]

def test_grid_to_world_conversion(simple_terrain):
    # Scale is 10.0
    assert simple_terrain.grid_to_world(0, 0) == (0.0, 0.0)
    assert simple_terrain.grid_to_world(1, 2) == (10.0, 20.0)

def test_world_to_grid_conversion(simple_terrain):
    # Scale is 10.0
    assert simple_terrain.world_to_grid(5.0, 5.0) == (0, 0)   # Truncates
    assert simple_terrain.world_to_grid(10.0, 20.0) == (1, 2) # Exact
    assert simple_terrain.world_to_grid(19.9, 19.9) == (1, 1) # Boundary check

def test_get_height_exact_grid_point(simple_terrain):
    """If we ask for height exactly at a vertex, it should return the tile height."""
    # World (10.0, 10.0) -> Grid (1, 1). Tile (1,1) height is 10.0
    h = simple_terrain.get_height(10.0, 10.0)
    assert h == 10.0

def test_get_height_midpoint_interpolation(simple_terrain):
    """
    Test exact center of a grid cell.
    Grid (0,0) h=0
    Grid (1,0) h=10
    World (5.0, 0.0) is exactly halfway.
    """
    h = simple_terrain.get_height(5.0, 0.0)
    assert h == pytest.approx(5.0)

def test_get_height_bilinear_interpolation():
    """
    Test bilinear interpolation on a complex slope.
    0,0 (h=0) --- 1,0 (h=10)
      |             |
    0,1 (h=10) -- 1,1 (h=20)
    """
    tiles = [
        [Tile("g", 0.0), Tile("g", 10.0)],
        [Tile("g", 10.0), Tile("g", 20.0)]
    ]
    terrain = ConcreteTerrainMap(2, 2, tiles, 1.0)
    
    # Midpoint (0.5, 0.5) should be average of all 4 corners: 10.0
    h = terrain.get_height(0.5, 0.5)
    assert h == pytest.approx(10.0)

def test_get_height_out_of_bounds(simple_terrain):
    """Should return 0.0 if outside the queryable area."""
    assert simple_terrain.get_height(-5.0, 0.0) == 0.0
    assert simple_terrain.get_height(500.0, 500.0) == 0.0

def test_get_height_edge_boundary(simple_terrain):
    """
    We cannot interpolate past the second-to-last index.
    Width 3 (Indices 0, 1, 2). Max interpolation base is Index 1.
    """
    # 1.5 * 10 = 15.0. Valid (between index 1 and 2).
    assert simple_terrain.get_height(15.0, 0.0) == pytest.approx(15.0)
    
    # 2.0 * 10 = 20.0. Index 2. Cannot interpolate to right. Returns 0.0.
    assert simple_terrain.get_height(20.0, 0.0) == 0.0
