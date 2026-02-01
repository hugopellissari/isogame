from pydantic import BaseModel


class AssetModel(BaseModel):
    """
    Defines the visual assets of the game, the model, the texture, and in the future, the animations
    """
    asset_id: str

    # Visuals
    model: str        # 'quad', 'cube', or a file path
    texture: str
    scale: tuple[float, float, float] = (1, 1, 1)
    
    # Behavior Flags (The real distinction)
    is_static: bool = True     # If True, the renderer builds it once and stops watching it
    layer: int = 0             # 0 for ground, 1 for objects on ground
