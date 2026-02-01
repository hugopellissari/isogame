import math
from game.systems.base import System


class MovementSystem(System):
    def update(self, world, dt: float):
        """
        Iterates over ALL entities with a 'Mover' trait.
        If they have a destination, it moves them towards it.
        """
        for unit in world.entity_map.units:
            # Safety Check
            if not hasattr(unit, "mover"):
                continue
                
            # If no place to go, skip
            if unit.mover.destination is None:
                continue

            # 1. Calculate Distance to Destination
            dest_x, dest_z = unit.mover.destination
            dx = dest_x - unit.position[0]
            dz = dest_z - unit.position[1]
            dist = math.sqrt(dx*dx + dz*dz)

            # 2. Check Arrival
            # If we are super close, snap to target and stop
            if dist < 0.1:
                unit.position = (dest_x, dest_z)
                unit.mover.destination = None # We arrived!
                continue

            # 3. Move!
            # Normalize vector * speed * time
            move_x = (dx / dist) * unit.mover.speed * dt
            move_z = (dz / dist) * unit.mover.speed * dt
            
            unit.position = (
                unit.position[0] + move_x,
                unit.position[1] + move_z
            )
