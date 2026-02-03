from graphics.meshers.mesh import MeshData
from graphics.meshers.terrain_mesher import TerrainMesher
from graphics.renderer import Renderer
from engine.core.game import Game


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
        """
        # TODO
        # THis is the most naive implementation possible, we myst make sure we only
        # render what we didn't render before or what has changed.
        # We also must make sure to destroy whatever is not present in the list anymore.
        # For this, we will probbaly need to keep a different map of the visuals created
        for entity in game.entities.list():
            self.renderer.render_instance(
                entity_id=entity.id,
                asset_name=entity.asset,
                # TODO we must convert logic position to game position
                position=entity.position,
            )
