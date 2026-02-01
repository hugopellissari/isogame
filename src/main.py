
import math
from ursina import Ursina, EditorCamera, time, held_keys

# Engine Imports
from engine.game import Game
from engine.entity import BaseEntity, EntityMap
from engine.system import System, MovementSystem, InteractionSystem
from engine.terrain import TerrainGenerationParams, TerrainType, Tile, TerrainMap
from engine.trait import MovableTrait
from engine.cqrs import BaseCommand, BaseEvent

# Graphics Imports
from graphics.asset import AssetModel
from graphics.renderer import UrsinaRenderer
from graphics.mapper import SceneMapper, VisualProxy

# --- 1. CONCRETE ENGINE IMPLEMENTATIONS ---

class MyTerrainType(TerrainType):
    GRASS = "grass"

class BasicTerrain(TerrainMap):
    @classmethod
    def generate(cls, width: int, height: int, params: TerrainGenerationParams) -> "BasicTerrain":
        tiles = [[Tile(terrain=MyTerrainType.GRASS) for _ in range(height)] for _ in range(width)]
        return cls(width=width, height=height, tiles=tiles)

# --- 2. CQRS: COMMANDS, EVENTS, AND HANDLERS ---

class MoveCommand(BaseCommand):
    entity_id: str
    target_pos: tuple[float, float]

class EntityCollisionEvent(BaseEvent):
    source_id: str
    target_id: str

def handle_move_command(game: Game, command: MoveCommand):
    entity = game.entity_map.get(command.entity_id)
    if entity:
        entity.move_to(command.target_pos)

def handle_collision_event(game: Game, event: EntityCollisionEvent):
    """Instead of killing, we push both entities away from each other."""
    source = game.entity_map.get(event.source_id)
    target = game.entity_map.get(event.target_id)
    
    if not source or not target:
        return

    # 1. Calculate the Vector between them
    dx = source.position[0] - target.position[0]
    dy = source.position[1] - target.position[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance == 0: return # Prevent division by zero

    # 2. Normalize the vector (Direction only)
    nx = dx / distance
    ny = dy / distance

    # 3. Apply a 'Bounce' (Push them apart)
    # We move them just enough to stop overlapping
    push_strength = 0.2
    
    # Source (Jack) moves away from Target (Tree)
    source.position = (
        source.position[0] + nx * push_strength,
        source.position[1] + ny * push_strength
    )
    
    # Target (Tree) moves away from Source (Jack)
    # Note: Trees are usually heavy, so maybe it moves less?
    target.position = (
        target.position[0] - nx * (push_strength * 0.5), 
        target.position[1] - ny * (push_strength * 0.5)
    )

    # 4. Stop their current movement (Reset targets)
    source.move_to(source.position)
    target.move_to(target.position)

# --- 3. THE COLLISION SYSTEM ---

class CollisionSystem(System):
    """Purely detects proximity and informs the engine via Events."""
    def update(self, game: Game, dt: float):
        # 1. Find the Jack
        jack = next((e for e in game.entity_map.entities.values() if e.asset == "lumberjack"), None)
        if not jack: return

        # 2. Check proximity to trees
        for eid, entity in game.entity_map.entities.items():
            if entity.asset == "tree":
                dist = math.sqrt(
                    (jack.position[0] - entity.position[0])**2 + 
                    (jack.position[1] - entity.position[1])**2
                )
                
                # If close enough, enqueue an event
                if dist < 0.7:
                    game.enqueue_event(EntityCollisionEvent(source_id=jack.id, target_id=eid))

# --- 4. THE CONCRETE GAME ---

class LumberjackGame(Game):
    @classmethod
    def setup(cls, width: int, height: int) -> "LumberjackGame":
        params = TerrainGenerationParams()
        terrain = BasicTerrain.generate(width, height, params)
        entities = EntityMap()
        
        instance = cls(terrain_map=terrain, entity_map=entities)
        
        # Register Handlers
        instance.command_processor.register_handler(MoveCommand, handle_move_command)
        instance.event_processor.register_handler(EntityCollisionEvent, handle_collision_event)
        
        # Add Systems
        instance.systems.append(MovementSystem())
        instance.systems.append(CollisionSystem()) # Logic for proximity
        instance.systems.append(InteractionSystem())
        
        return instance

# --- 5. EXECUTION ---

if __name__ == "__main__":
    app = Ursina()

    # Asset Library: Use distinct scales/colors to see the difference
    asset_library = {
        "grass": AssetModel(asset_id="grass", model="quad", texture="white_cube", is_static=True, layer=0),
        "lumberjack": AssetModel(asset_id="lumberjack", model="cube", texture="white_cube", scale=(0.5, 1, 0.5), layer=1),
        "tree": AssetModel(asset_id="tree", model="cube", texture="white_cube", scale=(0.8, 3, 0.8), layer=1)
    }

    game_instance = LumberjackGame.setup(width=10, height=10)

    # Add Entities
    jack = BaseEntity(position=(2.0, 2.0), asset="lumberjack", traits=[MovableTrait(speed=5.0)])
    game_instance.entity_map.add(jack)
    
    # Scatter some trees
    game_instance.entity_map.add(BaseEntity(position=(5, 5), asset="tree"))
    game_instance.entity_map.add(BaseEntity(position=(8, 2), asset="tree"))

    mapper = SceneMapper(asset_library)
    renderer = UrsinaRenderer()

    EditorCamera()

    def update():
        # Input -> Commands
        dx = held_keys['right arrow'] - held_keys['left arrow']
        dy = held_keys['up arrow'] - held_keys['down arrow']
        if dx != 0 or dy != 0:
            target = (jack.position[0] + dx, jack.position[1] + dy)
            game_instance.enqueue_command(MoveCommand(entity_id=jack.id, target_pos=target))

        # Simulation
        game_instance.tick(time.dt)
        
        # Bridge & Render
        proxies = mapper.map_to_proxies(game_instance)
        renderer.render(proxies)

    app.run()
