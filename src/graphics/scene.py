import random
from ursina import Entity, Vec3, color, destroy
from .assets import get_color_texture, ColorPalette

from game.world.entities.tree import Tree
from game.world.entities.units import Lumberjack


class SceneManager:
    def __init__(self):
        # Optimized parent for static terrain
        self.terrain_parent = Entity()
        
        # CENTRAL REGISTRY: Maps Entity ID (str) -> Ursina Entity
        self.visuals: dict[str, Entity] = {}

    def clear(self):
        """Wipes the slate clean."""
        if self.terrain_parent: 
            destroy(self.terrain_parent)
        self.terrain_parent = Entity()
        
        for visual in self.visuals.values():
            destroy(visual)
        self.visuals.clear()

    # ---------------------------------------------------------
    # 1. THE FACTORY (Decides HOW to draw things)
    # ---------------------------------------------------------
    def _create_visual(self, entity_data) -> Entity | None:
        """
        Takes raw data (Tree/Lumberjack) and returns a formatted Ursina Entity.
        """
        x, z = entity_data.position
        
        # --- CASE A: LUMBERJACK ---
        if isinstance(entity_data, Lumberjack):
            # Container
            actor = Entity(position=Vec3(x, 0.5, z), scale=Vec3(1, 1, 1))
            
            # Body (Red Capsule)
            Entity(parent=actor, model='capsule', color=color.red, y=0, scale=Vec3(0.4, 0.8, 0.4))
            
            # Axe
            Entity(parent=actor, model='cube', color=color.gray, 
                   scale=Vec3(0.1, 0.4, 0.1), position=Vec3(0.3, 0.2, 0.3), rotation_x=45)
            
            return actor

        # --- CASE B: TREE ---
        elif isinstance(entity_data, Tree):
            # FACTORIO STYLE LOGIC (Copied from your previous code)
            offset_x = random.uniform(-0.3, 0.3)
            offset_z = random.uniform(-0.3, 0.3)
            size_mod = random.uniform(0.6, 0.9)

            # Container with offset
            root = Entity(
                position=Vec3(x + offset_x, 0, z + offset_z),
                scale=Vec3(size_mod, size_mod, size_mod)
            )

            # Shadow
            Entity(parent=root, model='circle', color=color.rgba(0, 0, 0, 100),
                   position=Vec3(0, 0.06, 0), scale=Vec3(0.5, 0.5, 0.5), rotation_x=90)

            # Trunk
            Entity(parent=root, model='cube', texture=get_color_texture(*ColorPalette.TRUNK),
                   color=color.white, scale=Vec3(0.2, 0.8, 0.2), position=Vec3(0, 0.4, 0))

            # Leaves (Bottom)
            leaf_rgb = ColorPalette.random_leaf_color()
            leaf_tex = get_color_texture(*leaf_rgb)
            Entity(parent=root, model='cube', texture=leaf_tex, color=color.white,
                   scale=Vec3(0.5, 0.35, 0.5), position=Vec3(0, 0.7, 0))
            
            # Leaves (Top)
            Entity(parent=root, model='cube', texture=leaf_tex, color=color.white,
                   scale=Vec3(0.3, 0.5, 0.3), position=Vec3(0, 1.05, 0))

            return root

        return None

    # ---------------------------------------------------------
    # 2. TERRAIN HANDLING
    # ---------------------------------------------------------
    def add_tile(self, x: int, z: int, is_water: bool):
        if is_water:
            tex = ColorPalette.get_water_texture()
            y_pos, y_scale = -0.1, 0.1 
        else:
            tex = ColorPalette.get_land_texture()
            y_pos, y_scale = 0, 0.1

        Entity(
            parent=self.terrain_parent, # Attach to parent for optimization
            model='cube',
            texture=tex,
            color=color.white,
            position=Vec3(x, y_pos, z),
            scale=Vec3(1, y_scale, 1),
        )

    def finish_terrain(self):
        """Optimizes terrain into one mesh."""
        if self.terrain_parent:
            self.terrain_parent.combine()
            self.terrain_parent.texture = 'white_cube'

    # ---------------------------------------------------------
    # 3. SYNC METHODS (The Interface)
    # ---------------------------------------------------------
    def init_world(self, entity_map):
        """
        Bulk loads the initial state. Call this ONCE at startup.
        """
        # Clear old dynamic entities (but keep terrain if you want)
        for visual in self.visuals.values():
            destroy(visual)
        self.visuals.clear()

        # Load everything in the map
        for entity in entity_map.entities.values():
            visual = self._create_visual(entity)
            if visual:
                self.visuals[entity.id] = visual

    def sync(self, world_events: list, dynamic_entities: list):
        """
        Called every frame to update positions and handle spawns/deaths.
        """
        # A. HANDLE EVENTS (Spawn/Destroy)
        for event in world_events:
            # Note: We access properties of your Event object now
            if event.event_type.value == "spawn":
                if event.entity and event.entity_id not in self.visuals:
                    visual = self._create_visual(event.entity)
                    if visual:
                        self.visuals[event.entity_id] = visual

            elif event.event_type.value == "destroy":
                if event.entity_id in self.visuals:
                    destroy(self.visuals[event.entity_id])
                    del self.visuals[event.entity_id]

        # B. HANDLE MOVEMENT (Continuous)
        for entity in dynamic_entities:
            if entity.id in self.visuals:
                v = self.visuals[entity.id]
                # Smoothly interpolate or snap position
                v.position = Vec3(entity.position[0], 0.5, entity.position[1])
                
                # Optional: Visual Polish
                # If you added a 'rotation' field to your Unit entity, sync it here:
                # v.rotation_y = entity.rotation
    