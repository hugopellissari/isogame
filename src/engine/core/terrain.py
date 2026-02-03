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

    def __init__(
        self, width: int, height: int, tiles: list[list[Tile]], tile_scale: float
    ):
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

    def get_height(self, wx: float, wz: float) -> float:
        """
        Calculates the interpolated height at world coordinates (wx, wz).
        Returns 0.0 if out of bounds.
        """
        # 1. Convert World Space -> Grid Space (Float)
        gx = wx / self.tile_scale
        gz = wz / self.tile_scale

        # 2. Get the integer base coordinates (Top-Left of the cell)
        x0 = int(gx)
        z0 = int(gz)

        # 3. Check Bounds
        # We need x0+1 and z0+1 to be valid for interpolation,
        # so we subtract 1 from the upper limit check.
        if x0 < 0 or z0 < 0 or x0 >= self.width - 1 or z0 >= self.height - 1:
            return 0.0  # Return default sea level or clamp

        # 4. Calculate fractional part (Weights for interpolation)
        tx = gx - x0
        tz = gz - z0

        # 5. Fetch heights of the 4 surrounding tiles
        # Access tiles directly for speed (we already checked bounds)
        h00 = self.tiles[x0][z0].height  # Top-Left
        h10 = self.tiles[x0 + 1][z0].height  # Top-Right
        h01 = self.tiles[x0][z0 + 1].height  # Bottom-Left
        h11 = self.tiles[x0 + 1][z0 + 1].height  # Bottom-Right

        # 6. Bilinear Interpolation
        # Interpolate along X
        lerp_x_top = h00 * (1 - tx) + h10 * tx
        lerp_x_bot = h01 * (1 - tx) + h11 * tx

        # Interpolate along Z
        final_height = lerp_x_top * (1 - tz) + lerp_x_bot * tz

        return final_height
