from typing import Protocol
from pydantic import BaseModel


class System(BaseModel):
    def update(self, world, dt: float):
        ...
