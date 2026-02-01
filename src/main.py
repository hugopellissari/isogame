from ursina import Ursina, camera, Vec3, window, time, EditorCamera
from game.world.world import World
from game.world.terrain.tile import TerrainType
from graphics.scene import SceneManager 

# CONFIGURATION
MAP_SIZE = 64 

def configure_app():
    app = Ursina()
    window.title = "My Engine"
    window.borderless = False 
    
    # Camera Setup
    camera.orthographic = True
    camera.fov = 60
    camera.clip_plane_far = 2000 
    map_center = 32
    camera.position = Vec3(map_center, 0, map_center)
    camera.rotation = Vec3(35.264, 45, 0)
    camera.position -= camera.forward * 100

    return app


def main():
    app = configure_app()

    # 1. GENERATE DATA
    print(f"Generating {MAP_SIZE}x{MAP_SIZE} World...")
    world = World.generate(width=MAP_SIZE, height=MAP_SIZE)

    # 2. SETUP SCENE
    scene = SceneManager()

    # A. Draw Terrain (Static)
    # We still loop manually for terrain because it's a grid, not entities.
    print("Building Terrain...")
    for x in range(world.terrain_map.width):
        for z in range(world.terrain_map.height):
             tile = world.terrain_map.tile_at(x, z)
             scene.add_tile(x, z, tile.terrain == TerrainType.water)
    
    # Important: Merge terrain into one mesh for FPS
    # TODO Let's leave this out for now as it is making everything white!!
    # scene.finish_terrain() 

    # B. Draw Entities (Dynamic)
    # This replaces your old 'sync_scene' function.
    # It automatically looks at the dictionary and draws all trees/units.
    print("Spawning Entities...")
    scene.init_world(world.entity_map)
    
    # 3. GAME LOOP
    def update():
        # A. Logic Systems (Update Data)
        world.tick(time.dt)

        scene.sync(
            world_events=world.events, 
            dynamic_entities=world.entity_map.units
        )

        # C. Cleanup Events
        world.events.clear()

    app.run()

if __name__ == "__main__":
    main()
