from enum import Enum
from pydantic import BaseModel


class TerrainType(str, Enum):
    land = "land"
    water = "water"


class Tile(BaseModel):
    terrain: TerrainType
