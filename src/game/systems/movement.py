import math
import heapq
from game.systems.base import System
from game.world.terrain.tile import TerrainType

class MovementSystem(System):
    def update(self, world, dt: float):
        for unit in world.entity_map.units:
            if not hasattr(unit, "mover"):
                continue

            # 1. PATH REQUEST: If we have a destination but NO path yet, calculate it
            if unit.mover.destination and not unit.mover.path:
                unit.mover.path = self._calculate_a_star(
                    world.terrain_map, 
                    unit.position, 
                    unit.mover.destination
                )
                # If pathfinding failed (e.g. tree on island), clear destination
                if not unit.mover.path:
                    unit.mover.destination = None
                    continue

            # 2. PATH FOLLOWING: If we have a path, move toward the NEXT point in it
            if unit.mover.path:
                target_x, target_z = unit.mover.path[0]
                
                dx = target_x - unit.position[0]
                dz = target_z - unit.position[1]
                dist = math.sqrt(dx*dx + dz*dz)

                # Are we close enough to the current waypoint?
                if dist < 0.1:
                    unit.position = (target_x, target_z)
                    unit.mover.path.pop(0) # Remove reached waypoint
                    
                    # If that was the last point, we reached the final destination
                    if not unit.mover.path:
                        unit.mover.destination = None
                    continue

                # Move toward the waypoint
                move_x = (dx / dist) * unit.mover.speed * dt
                move_z = (dz / dist) * unit.mover.speed * dt
                
                unit.position = (
                    unit.position[0] + move_x,
                    unit.position[1] + move_z
                )

    def _calculate_a_star(self, terrain_map, start, goal):
        """A* Algorithm to find land-only paths."""
        start_node = (int(start[0]), int(start[1]))
        goal_node = (int(goal[0]), int(goal[1]))

        open_set = []
        heapq.heappush(open_set, (0, start_node))
        
        came_from = {}
        g_score = {start_node: 0}
        
        # Manhattan distance heuristic
        def h(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal_node:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1] # Path from start to goal

            for dx, dz in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dz)
                
                # Boundary check and WATER check
                tile = terrain_map.tile_at(neighbor[0], neighbor[1])
                if not tile or tile.terrain == TerrainType.water:
                    continue

                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + h(neighbor, goal_node)
                    heapq.heappush(open_set, (f_score, neighbor))

        return [] # Path not found
