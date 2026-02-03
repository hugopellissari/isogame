from abc import ABC, abstractmethod
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Generic, Iterator, Tuple, TypeVar


TerrainID = TypeVar("TerrainID")

@dataclass(slots=True)
class Tile(Generic[TerrainID]):
    terrain_id: TerrainID
    height: float = 0.0


class TerrainGenerationParams(BaseModel):
    """Configuration for the generator remains a BaseModel for easy serialization."""
    pass


class TerrainMap(ABC):
    """
    Standard Python class for high-performance grid lookups.
    Using ABC (Abstract Base Class) instead of BaseModel.
    """
    def __init__(self, width: int, height: int, tiles: list[list[Tile]], tile_scale: float):
        self.width = width
        self.height = height
        self.tiles = tiles
        self.tile_scale = tile_scale

    @classmethod
    @abstractmethod
    def generate(
        cls,
        width: int,
        height: int,
        params: TerrainGenerationParams | None = None,
    ) -> "TerrainMap":
        """Defines the terrain generation logic."""
        pass

    def in_bounds(self, x: int, z: int) -> bool:
        """Check if coordinates are within the grid."""
        return 0 <= x < self.width and 0 <= z < self.height

    def tile_at(self, x: int, z: int) -> Tile | None:
        """Retrieve a tile at specific coordinates."""
        if self.in_bounds(x, z):
            return self.tiles[x][z]
        return None

    def neighbors(self, x: int, z: int) -> Iterator[Tuple[int, int, Tile]]:
        """Yields adjacent coordinates and their tiles."""
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, nz = x + dx, z + dz
            if self.in_bounds(nx, nz):
                yield nx, nz, self.tiles[nx][nz]

    def grid_to_world(self, x: int, z: int) -> tuple[float, float]:
        return (x * self.tile_scale, z * self.tile_scale)

    def world_to_grid(self, wx: float, wz: float) -> tuple[int, int]:
        return (int(wx / self.tile_scale), int(wz / self.tile_scale))