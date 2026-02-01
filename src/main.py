from ursina import Ursina, camera, Vec3, window, time, Entity, color
from game.world.world import World
from game.world.terrain.tile import TerrainType
from graphics.scene import SceneManager 

# CONFIGURATION
MAP_SIZE = 64 

# 1. INITIALIZE CORE OBJECTS AT GLOBAL SCOPE
# This allows the update() function to "see" them.
app = Ursina()
world = World.generate(width=MAP_SIZE, height=MAP_SIZE)
scene = SceneManager()

def configure_app():
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

def update():
    """Ursina automatically looks for this function in the global scope."""
    # This print will now appear in your console every frame
    # print(f"Ticking world at {1/time.dt:.1f} FPS") 
    
    # A. Logic Systems (Update Data)
    world.tick(time.dt)

    # B. Graphics Sync
    scene.sync(
        world_events=world.events, 
        dynamic_entities=world.entity_map.units
    )

    # C. Cleanup Events
    world.events.clear()

def main():
    configure_app()

    # 1. GENERATE TERRAIN
    print("Building Terrain...")
    for x in range(world.terrain_map.width):
        for z in range(world.terrain_map.height):
             tile = world.terrain_map.tile_at(x, z)
             # Passing parent=scene or specific logic here if needed
             scene.add_tile(x, z, tile.terrain == TerrainType.water)
    
    # 2. SPAWN ENTITIES
    print("Spawning Entities...")
    scene.init_world(world.entity_map)
    
    # 3. START ENGINE
    app.run()

if __name__ == "__main__":
    main()