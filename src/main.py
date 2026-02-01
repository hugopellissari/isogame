from ursina import Ursina, camera, Vec3, window, time, Entity, color
from game.world.world import World
from game.world.terrain.tile import TerrainType
from graphics.scene import SceneManager 

# CONFIGURATION
MAP_SIZE = 10 

# 1. INITIALIZE CORE OBJECTS AT GLOBAL SCOPE
# This allows the update() function to "see" them.
app = Ursina()
world = World.generate(width=MAP_SIZE, height=MAP_SIZE)
scene = SceneManager()

def configure_app():
    window.title = "My Engine"
    window.borderless = False 
    
    # 1. Calculate the dynamic center
    # If MAP_SIZE is 10, center is 5. If 100, center is 50.
    center_coord = MAP_SIZE / 2
    # Camera Setup
    camera.orthographic = True
    # 2. Dynamic FOV (Optional)
    # This keeps the whole map in view even if you change size
    camera.fov = MAP_SIZE * 1.2 
    camera.clip_plane_far = 2000 
    # 3. Position the camera at the center of the grid
    # We set Y to 0 because our terrain is on the XZ plane
    camera.position = Vec3(center_coord, 0, center_coord)
    # 4. Apply Isometric Rotation
    camera.rotation = Vec3(35.264, 45, 0)
    # 5. Pull the camera back along its local "forward" vector 
    # so it doesn't clip through the floor
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