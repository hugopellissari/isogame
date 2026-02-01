
import uuid
from pydantic import BaseModel, Field

class BaseEntity(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    position: tuple[float, float]
