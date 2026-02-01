from pydantic import BaseModel

class Destructible(BaseModel):
    health: float = 100.0
    max_health: float = 100.0


class Chopper(BaseModel):
    power: float = 10.0
    range: float = 1.0
    cooldown: float = 0.5


class Mover(BaseModel):
    speed: float = 2.0
    destination: tuple[float, float] | None = None
    path: list[tuple[int, int]] = [] # Add this!
