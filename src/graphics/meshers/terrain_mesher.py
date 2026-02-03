from engine.core.terrain import TerrainMap
from graphics.meshers.mesh import MeshData


class TerrainMesher:
    def __init__(self):
        pass

    def generate_mesh(self, terrain_map: TerrainMap) -> MeshData:
        data = MeshData()
        scale = terrain_map.tile_scale
        vertex_cursor = 0

        for x in range(terrain_map.width):
            for z in range(terrain_map.height):
                tile = terrain_map.tile_at(x, z)
                if not tile:
                    continue

                # --- 1. GET NEIGHBOR HEIGHTS ---
                h_bl = tile.height

                right_tile = terrain_map.tile_at(x + 1, z)
                h_br = right_tile.height if right_tile else h_bl

                top_tile = terrain_map.tile_at(x, z + 1)
                h_tl = top_tile.height if top_tile else h_bl

                diag_tile = terrain_map.tile_at(x + 1, z + 1)
                h_tr = diag_tile.height if diag_tile else h_bl

                # --- 2. CALCULATE POSITIONS ---
                x0, z0 = x * scale, z * scale
                x1, z1 = (x + 1) * scale, (z + 1) * scale

                # Order: 0:BL, 1:TL, 2:TR, 3:BR
                v_bl = (x0, h_bl, z0)
                v_tl = (x0, h_tl, z1)
                v_tr = (x1, h_tr, z1)
                v_br = (x1, h_br, z0)

                data.vertices.extend([v_bl, v_tl, v_tr, v_br])

                # --- 3. TRIANGLES (FIXED) ---
                base = vertex_cursor

                # We swapped the order to be Counter-Clockwise (CCW).
                # Triangle 1: Top-Right -> Top-Left -> Bottom-Left
                # Triangle 2: Bottom-Left -> Bottom-Right -> Top-Right
                data.triangles.extend(
                    [base + 2, base + 1, base, base, base + 3, base + 2]
                )

                vertex_cursor += 4

                data.uvs.extend([(0, 0), (0, 1), (1, 1), (1, 0)])
                data.colors.extend([(1, 1, 1, 1)] * 4)

        return data
