from abc import abstractmethod
from enum import Enum
from pydantic import BaseModel


class TerrainType(str, Enum):
    pass


class Tile(BaseModel):
    terrain: TerrainType


class TerrainGenerationParams(BaseModel):
    pass


class TerrainMap(BaseModel):
    width: int
    height: int
    tiles: list[list[Tile]]

    @abstractmethod
    @classmethod
    def generate(
        cls,
        width: int,
        height: int,
        params: TerrainGenerationParams,
    ) -> "TerrainMap":
        """
        Defines the terrain generation logic.
        """

    def in_bounds(self, x: int, z: int) -> bool:
        return 0 <= x < self.width and 0 <= z < self.height

    def tile_at(self, x: int, z: int) -> Tile | None:
        return self.tiles[x][z] if self.in_bounds(x, z) else None

    def neighbors(self, x: int, z: int):
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, nz = x + dx, z + dz
            if self.in_bounds(nx, nz):
                yield nx, nz, self.tiles[nx][nz]
