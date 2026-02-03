from math import sqrt
from engine.builtins.events.entity_arrived import EntityArrivedEvent
from engine.builtins.traits import MovableTrait
from engine.core.system import EPSILON, System


class MovementSystem(System):
    def update(self, game: "Game", dt: float):
        for entity, movable in game.entities.yield_entities_with_trait(MovableTrait):
            if not movable.destination or not movable.is_moving:
                continue

            if not movable.path:
                movable.set_path([movable.destination])

            # Peek target
            target_pos = movable.path[-1]

            # --- COORDINATES (Pure 2D X/Z) ---
            current_x, _, current_z = entity.position  # Ignore Y completely!
            target_x, target_z = target_pos[0], target_pos[1]

            dx = target_x - current_x
            dz = target_z - current_z

            distance = sqrt(dx**2 + dz**2)
            move_distance = movable.speed * dt

            # CHECK ARRIVAL
            if distance <= move_distance + EPSILON:
                # 1. Snap Logic X/Z only (Let SnappingSystem handle Y later)
                # We keep the current Y for now, or set it to 0, it doesn't matter
                # because TerrainSnappingSystem runs next.
                entity.position = (target_x, entity.position[1], target_z)

                movable.path.pop()
                if not movable.path:
                    movable.stop_movement()
                    game.enqueue_event(EntityArrivedEvent(entity_id=entity.id))
            else:
                # MOVE
                ratio = move_distance / distance
                new_x = current_x + (dx * ratio)
                new_z = current_z + (dz * ratio)

                # Update Position (Preserve current Y)
                entity.position = (new_x, entity.position[1], new_z)
