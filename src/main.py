from graphics.mapper import AssetLibrary, SceneMapper
from graphics.renderer import UrsinaRenderer
from ursina import Ursina, window, EditorCamera, time

from demo_game.logic.game import simple_game
from demo_game.visual.assets import player_asset


# TODO this should be abstracted away
app = Ursina()
window.title = "Terrain Slope Test"
EditorCamera()

# Ensures to register all the visual assets we need to render out entities
asset_library = AssetLibrary()
asset_library.register_mesh("player", player_asset)

mapper = SceneMapper(renderer=UrsinaRenderer(), asset_library=asset_library)
mapper.setup(simple_game)
mapper.render(simple_game)

def update():
    """
    Ursina calls this function every single frame (60 times per second).
    """
    dt = time.dt # Time since last frame

    simple_game.tick(dt)
    mapper.render(simple_game)

app.run()
