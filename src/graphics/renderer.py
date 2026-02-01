from ursina import Entity, destroy

from graphics.mapper import VisualProxy

class UrsinaRenderer:
    def __init__(self):
        self.hardware_entities = {} # Map[id, ursina.Entity]

    def render(self, proxies: list[VisualProxy]):
        active_ids = set()
        
        for proxy in proxies:
            active_ids.add(proxy.entity_id)
            
            # Create hardware entity if it doesn't exist
            if proxy.entity_id not in self.hardware_entities:
                self.hardware_entities[proxy.entity_id] = Entity(
                    model=proxy.asset.model,
                    texture=proxy.asset.texture,
                    scale=proxy.asset.scale,
                    # If it's a quad, we usually want it flat on the ground
                    rotation=(90, 0, 0) if proxy.asset.model == 'quad' else (0,0,0)
                )

            # Update position
            hw_ent = self.hardware_entities[proxy.entity_id]
            hw_ent.position = proxy.position
            hw_ent.enabled = proxy.is_visible

        # Cleanup: Remove hardware entities that are no longer in the proxy list
        to_remove = set(self.hardware_entities.keys()) - active_ids
        for rid in to_remove:
            destroy(self.hardware_entities[rid])
            del self.hardware_entities[rid]
