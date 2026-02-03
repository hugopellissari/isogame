from ursina import Entity, Mesh, color, destroy
from graphics.meshers.mesh import MeshData


class Renderer:
    def register_mesh(self, name: str, mesh_data: MeshData):
        raise NotImplementedError

    def render_instance(
        self, entity_id: str, asset_name: str, position: tuple, collider: str = "box"
    ):
        raise NotImplementedError

    def destroy_instance(self, entity_id: str):
        """Removes a specific entity from the scene and memory."""
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class UrsinaRenderer(Renderer):
    def __init__(self):
        self.entities = {}  # Active instances: { "id": Entity }
        self._models = {}  # GPU Cache: { "asset_name": Mesh }

    def register_mesh(self, name: str, mesh_data: MeshData):
        """
        Uploads geometry to GPU.
        Works for 'tree' (reused) AND 'terrain' (unique).
        """
        # If we are regenerating the map, we might want to overwrite the old mesh
        # so we don't return early if it exists.

        ursina_colors = [color.rgba(*c) for c in mesh_data.colors]

        hw_mesh = Mesh(
            vertices=mesh_data.vertices,
            triangles=mesh_data.triangles,
            colors=ursina_colors,
            uvs=mesh_data.uvs,
            static=True,
        )

        self._models[name] = hw_mesh

    def render_instance(
        self, entity_id: str, asset_name: str, position: tuple, collider: str = "box"
    ):
        """
        Spawns or updates an object.
        collider: Use 'box' for entities, 'mesh' for terrain.
        """
        # 1. Get GPU Model
        target_model = self._models.get(asset_name)
        if not target_model:
            print(f"Error: Asset '{asset_name}' not found!")
            return None

        # 2. Update existing
        if entity_id in self.entities:
            ent = self.entities[entity_id]
            ent.position = position
            return ent

        # 3. Create new
        else:
            ent = Entity(
                model=target_model,
                position=position,
                texture="white_cube",
                collider=collider,  # <--- Pass this through!
            )
            self.entities[entity_id] = ent
            return ent

    def destroy_instance(self, entity_id: str):
        if entity_id in self.entities:
            # 1. Remove from the Screen (Ursina)
            ursina_ent = self.entities[entity_id]
            destroy(ursina_ent)

            # 2. Remove from Memory (Your Cache)
            del self.entities[entity_id]
        else:
            print(f"Warning: Tried to destroy non-existent entity '{entity_id}'")

    def clear(self):
        for e in self.entities.values():
            destroy(e)
        self.entities.clear()
