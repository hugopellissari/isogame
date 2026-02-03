from graphics.mapper import AssetLibrary, SceneMapper
from graphics.renderer import UrsinaRenderer
from ursina import Ursina, window, EditorCamera, time, held_keys

from demo_game.logic.game import MoveCommand, simple_game
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
    dt = time.dt  # Time since last frame

    dx, dz = 0, 0
    if held_keys["up arrow"] or held_keys["w"]:
        dz += 1
    if held_keys["down arrow"] or held_keys["s"]:
        dz -= 1
    if held_keys["right arrow"] or held_keys["d"]:
        dx += 1
    if held_keys["left arrow"] or held_keys["a"]:
        dx -= 1

    if dx != 0 or dz != 0:
        move_speed = 5.0

        # Get current logical position
        # Remember: Logic is (x, y, z) where Y is Up.
        current_x, _, current_z = simple_game.entities.list()[0].position

        # Calculate target for this frame
        dest_x = current_x + (dx * move_speed * dt)
        dest_z = current_z + (dz * move_speed * dt)

        # Send the command
        # Note: We send (x, z) because your MovementSystem logic reads indices [0] and [1]
        cmd = MoveCommand(destination=(dest_x, dest_z, 0))
        simple_game.enqueue_command(cmd)

    simple_game.tick(dt)
    mapper.render(simple_game)


app.run()
