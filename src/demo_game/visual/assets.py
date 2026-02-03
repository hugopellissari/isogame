# Build other objects
from graphics.meshers.entity_mesher import MeshBuilder

player_asset = (
    MeshBuilder()
    .add_cube(
        position=(0, 0.45, 0),  # Center is half height (0.45)
        size=(0.6, 0.9, 0.4),
        color=(0.8, 0.2, 0.2, 1),
    )
    .add_cube(
        position=(0, 1.1, 0),  # 0.9 (Body Top) + 0.2 (Head Half-Height)
        size=0.4,
        color=(0.9, 0.7, 0.6, 1),
    )
    .build()
)
