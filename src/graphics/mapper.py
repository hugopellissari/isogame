from graphics.meshers.mesh import MeshData
from graphics.meshers.terrain_mesher import TerrainMesher
from graphics.renderer import Renderer
from engine.game import Game


class AssetLibrary:
    def __init__(self):
        self.meshes = {}

    def register_mesh(self, name: str, mesh: MeshData):
        self.meshes[name] = mesh

    def get_mesh(self, name: str) -> MeshData | None:
        return self.meshes.get(name)


class SceneMapper:
    def __init__(self, renderer: Renderer, asset_library: AssetLibrary):
        self.renderer = renderer
        self.asset_library = asset_library
        self.visual_instances = {}

    def setup(self, game: Game):
        """
        Responsible for registering the meshes
        """
        for entity in game.entities.list():
            mesh = self.asset_library.get_mesh(entity.asset)
            if not mesh:
                raise ValueError(f"Mesh {entity.asset} not registered")
            self.renderer.register_mesh(entity.asset, mesh)

        terrain_mesh = TerrainMesher().generate_mesh(game.terrain)
        self.renderer.register_mesh("terrain", terrain_mesh)
        self.renderer.render_instance("level_ground", "terrain", (0, 0, 0))

    def render(self, game: Game):
        """
        Takes the current state of the game and renders it.

        TODO: 
        - Make it efficient so we do not render things that did not change among other otpimizations 
        - Ensure we can handle dynamic spawns and despawns
        """
        for entity in game.entities.list():
            
            # 1. LAZY CREATION: If this entity has no visual yet, create it now.
            if entity.id not in self.visual_instances:
                # TODO:
                # Ensure the mesh is registered (just in case it's a new dynamic spawn)
                self.visual_instances[entity.id] = self.renderer.render_instance(
                    f"vis_{entity.id}", 
                    entity.asset, 
                    entity.position
                )

            # 2. UPDATE: Force position sync
            visual = self.visual_instances[entity.id]
            visual.position = entity.position
    