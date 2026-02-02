from pydantic import BaseModel
from graphics.asset import AssetModel


class VisualProxy(BaseModel):
    entity_id: str
    asset: AssetModel
    position: tuple[float, float, float]
    is_visible: bool = True


class SceneMapper:
    def __init__(self, asset_library: dict[str, AssetModel]):
        self.library = asset_library

    def map_to_proxies(self, game) -> list[VisualProxy]:
        proxies = []
        
        # 1. Map Terrain (Static)
        # Fix: Iterate through the 2D list using indices
        for x in range(game.terrain.width):
            for y in range(game.terrain.height):
                tile = game.terrain.tiles[x][y]
                
                # Use the terrain enum value as the lookup key for the asset library
                asset = self.library.get(tile.terrain.value) 
                
                if asset:
                    pos = (float(x), asset.layer * 0.1, float(y)) 
                    proxies.append(VisualProxy(
                        entity_id=f"tile_{x}_{y}",
                        asset=asset,
                        position=pos
                    ))

        # 2. Map Entities (Dynamic)
        for eid, entity in game.entities.entities.items():
            # Ensure your BaseEntity has an asset_id attribute!
            asset = self.library.get(entity.asset)
            if asset:
                # Entity pos is (x, y), we map to Ursina (x, layer, z)
                pos = (entity.position[0], asset.layer * 0.1, entity.position[1])
                proxies.append(VisualProxy(
                    entity_id=eid,
                    asset=asset,
                    position=pos
                ))
        
        return proxies
