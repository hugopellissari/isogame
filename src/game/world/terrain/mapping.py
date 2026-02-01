import random
from copy import deepcopy
from pydantic import BaseModel

from .tile import TerrainType, Tile

class TerrainMap(BaseModel):
    width: int
    height: int
    tiles: list[list[Tile]]

    @classmethod
    def generate(
        cls,
        width: int,
        height: int,
        water_ratio: float = 0.45, # Higher ratio needed for smoothing to work
        seed: int | None = None,
        smoothing_passes: int = 5
    ) -> "TerrainMap":
        """
        Generates terrain using Cellular Automata to create distinct lakes/islands.
        """
        if seed is not None:
            random.seed(seed)

        # 1. INITIAL RANDOM FILL (The "Noise")
        # We start with a messy map of random dots
        tiles = [
            [
                Tile(
                    terrain=TerrainType.water
                    if random.random() < water_ratio
                    else TerrainType.land
                )
                for _ in range(height)
            ]
            for _ in range(width)
        ]

        # 2. SMOOTHING PASSES (The "Geography")
        # Repeatedly apply the "4-5 Rule" to clump tiles together
        for _ in range(smoothing_passes):
            tiles = cls._smooth_step(tiles, width, height)

        return cls(width=width, height=height, tiles=tiles)

    @staticmethod
    def _smooth_step(current_tiles: list[list[Tile]], w: int, h: int) -> list[list[Tile]]:
        """
        Applies one iteration of cellular automata smoothing.
        Returns a new grid of tiles.
        """
        new_tiles = deepcopy(current_tiles)

        for x in range(w):
            for z in range(h):
                # Count water neighbors (including diagonals)
                water_neighbors = 0
                for dx in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if dx == 0 and dz == 0:
                            continue
                        
                        nx, nz = x + dx, z + dz
                        
                        # Edges count as water (encourages island look)
                        if nx < 0 or nx >= w or nz < 0 or nz >= h:
                            water_neighbors += 1
                        elif current_tiles[nx][nz].terrain == TerrainType.water:
                            water_neighbors += 1

                # THE RULES (Standard Cellular Automata)
                # If more than 4 neighbors are water, I become water.
                # If less than 4, I become land.
                if water_neighbors > 4:
                    new_tiles[x][z].terrain = TerrainType.water
                elif water_neighbors < 4:
                    new_tiles[x][z].terrain = TerrainType.land
                # If exactly 4, stay the same (already handled by deepcopy)

        return new_tiles

    def in_bounds(self, x: int, z: int) -> bool:
        return 0 <= x < self.width and 0 <= z < self.height

    def tile_at(self, x: int, z: int) -> Tile | None:
        return self.tiles[x][z] if self.in_bounds(x, z) else None

    def neighbors(self, x: int, z: int):
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, nz = x + dx, z + dz
            if self.in_bounds(nx, nz):
                yield nx, nz, self.tiles[nx][nz]
