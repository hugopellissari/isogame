from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel
from typing import Iterator, Tuple


class TerrainType(str, Enum):
    # To be extended by specific game implementations
    pass


class Tile(BaseModel):
    terrain: TerrainType


class TerrainGenerationParams(BaseModel):
    """Configuration for the generator remains a BaseModel for easy serialization."""
    pass


class TerrainMap(ABC):
    """
    Standard Python class for high-performance grid lookups.
    Using ABC (Abstract Base Class) instead of BaseModel.
    """
    def __init__(self, width: int, height: int, tiles: list[list[Tile]]):
        self.width = width
        self.height = height
        self.tiles = tiles

    @classmethod
    @abstractmethod
    def generate(
        cls,
        width: int,
        height: int,
        params: TerrainGenerationParams,
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
