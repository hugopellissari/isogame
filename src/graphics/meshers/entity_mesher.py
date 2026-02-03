import math
from graphics.meshers.mesh import MeshData


class PrimitiveMesher:
    @staticmethod
    def create_cube(size: float = 1.0, color: tuple = (1, 1, 1, 1)) -> MeshData:
        data = MeshData()
        r = size / 2.0

        # We need 6 faces. Each face has 4 corners.
        # Order: Bottom-Left, Top-Left, Top-Right, Bottom-Right (relative to face direction)
        faces = [
            # Front (Z-)
            [(-r, -r, -r), (-r, r, -r), (r, r, -r), (r, -r, -r)],
            # Back (Z+)
            [(r, -r, r), (r, r, r), (-r, r, r), (-r, -r, r)],
            # Right (X+)
            [(r, -r, -r), (r, r, -r), (r, r, r), (r, -r, r)],
            # Left (X-)
            [(-r, -r, r), (-r, r, r), (-r, r, -r), (-r, -r, -r)],
            # Top (Y+)
            [(-r, r, -r), (-r, r, r), (r, r, r), (r, r, -r)],
            # Bottom (Y-)
            [(-r, -r, r), (-r, -r, -r), (r, -r, -r), (r, -r, r)],
        ]

        cursor = 0
        for face_verts in faces:
            # 1. Add Vertices
            data.vertices.extend(face_verts)

            # 2. Add Triangles (0-1-2, 0-2-3 relative to this face)
            # This creates the two triangles that make up the square face
            data.triangles.extend(
                [cursor, cursor + 1, cursor + 2, cursor, cursor + 2, cursor + 3]
            )

            # 3. Add Colors & UVs
            data.colors.extend([color] * 4)
            data.uvs.extend([(0, 0), (0, 1), (1, 1), (1, 0)])

            cursor += 4

        return data

    @staticmethod
    def create_pyramid(
        size: float = 1.0, height: float = 1.0, color: tuple = (1, 1, 1, 1)
    ) -> MeshData:
        data = MeshData()
        r = size / 2.0

        # 1. Base (Square, facing down)
        # We manually add the 4 corners of the base
        base_verts = [(-r, 0, r), (-r, 0, -r), (r, 0, -r), (r, 0, r)]
        data.vertices.extend(base_verts)
        data.colors.extend([color] * 4)
        data.uvs.extend([(0, 0), (0, 1), (1, 1), (1, 0)])

        # Base Triangles (indices 0,1,2,3)
        data.triangles.extend([0, 1, 2, 0, 2, 3])

        # 2. Sides (4 Triangles meeting at the tip)
        top_point = (0, height, 0)

        # The base corners again (for the sides)
        corners = [(-r, 0, -r), (r, 0, -r), (r, 0, r), (-r, 0, r)]

        cursor = 4  # Start after the base vertices

        for i in range(4):
            # Triangle is: Left Corner -> Tip -> Right Corner
            p1 = corners[i]
            p2 = top_point
            p3 = corners[(i + 1) % 4]  # Wrap around to start for the last side

            data.vertices.extend([p1, p2, p3])
            data.colors.extend([color] * 3)
            data.uvs.extend([(0, 0), (0.5, 1), (1, 0)])  # Simple triangular UV mapping

            # Add 1 triangle (0-1-2)
            data.triangles.extend([cursor, cursor + 1, cursor + 2])
            cursor += 3

        return data

    @staticmethod
    def create_quad(
        width: float = 1.0, height: float = 1.0, color: tuple = (1, 1, 1, 1)
    ) -> MeshData:
        """
        A single flat rectangle facing up (useful for water or floors).
        """
        data = MeshData()
        w, h = width / 2.0, height / 2.0

        # 4 corners (Facing Up, Y+)
        data.vertices = [(-w, 0, h), (-w, 0, -h), (w, 0, -h), (w, 0, h)]
        data.triangles = [0, 1, 2, 0, 2, 3]
        data.colors = [color] * 4
        data.uvs = [(0, 0), (0, 1), (1, 1), (1, 0)]
        return data

    @staticmethod
    def create_cylinder(
        radius: float = 0.5,
        height: float = 1.0,
        segments: int = 8,
        color: tuple = (1, 1, 1, 1),
    ) -> MeshData:
        """
        A vertical cylinder. Increase 'segments' for roundness.
        """
        data = MeshData()

        # 1. Generate Circle Points (Top and Bottom rings)
        top_verts = []
        bot_verts = []
        angle_step = (math.pi * 2) / segments

        for i in range(segments):
            angle = i * angle_step
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius

            top_verts.append((x, height, z))
            bot_verts.append((x, 0, z))

        # 2. Build Sides (Quads connecting top and bottom)
        cursor = 0
        for i in range(segments):
            # A side is a quad made of 4 vertices:
            # Bottom-Left, Top-Left, Top-Right, Bottom-Right
            next_i = (i + 1) % segments

            v_bl = bot_verts[i]
            v_tl = top_verts[i]
            v_tr = top_verts[next_i]
            v_br = bot_verts[next_i]

            data.vertices.extend([v_bl, v_tl, v_tr, v_br])
            data.colors.extend([color] * 4)
            # UVs map around the cylinder
            u_start = i / segments
            u_end = (i + 1) / segments
            data.uvs.extend([(u_start, 0), (u_start, 1), (u_end, 1), (u_end, 0)])

            data.triangles.extend(
                [cursor, cursor + 1, cursor + 2, cursor, cursor + 2, cursor + 3]
            )
            cursor += 4

        # 3. Build Caps (Top and Bottom disks) - Optional but recommended
        # (This usually involves a "fan" of triangles connecting to a center point)
        # ... logic for caps ...

        return data


class MeshBuilder:
    def __init__(self):
        self._parts: list[MeshData] = []

    def _apply_transform(self, mesh: MeshData, position: tuple, size: tuple | float):
        """Helper to avoid repeating scale/translate code for every shape."""
        # 1. Scale
        sx, sy, sz = size if isinstance(size, tuple) else (size, size, size)

        # Only loop if we are actually scaling (optimization)
        if sx != 1.0 or sy != 1.0 or sz != 1.0:
            mesh.vertices = [(v[0] * sx, v[1] * sy, v[2] * sz) for v in mesh.vertices]

        # 2. Translate
        tx, ty, tz = position
        if tx != 0.0 or ty != 0.0 or tz != 0.0:
            mesh.vertices = [(v[0] + tx, v[1] + ty, v[2] + tz) for v in mesh.vertices]

    def add_cube(self, position=(0, 0, 0), size=1.0, color=(1, 1, 1, 1)):
        # We pass size=1.0 to the primitive so our manual scaling handles everything
        cube = PrimitiveMesher.create_cube(size=1.0, color=color)
        self._apply_transform(cube, position, size)
        self._parts.append(cube)
        return self

    def add_pyramid(self, position=(0, 0, 0), size=1.0, height=1.0, color=(1, 1, 1, 1)):
        # Note: height is handled by the primitive, but width/depth by our scalar
        pyr = PrimitiveMesher.create_pyramid(size=1.0, height=height, color=color)
        self._apply_transform(pyr, position, size)
        self._parts.append(pyr)
        return self

    def add_quad(self, position=(0, 0, 0), size=1.0, color=(1, 1, 1, 1)):
        # Quads are 2D, but we might stretch them
        quad = PrimitiveMesher.create_quad(width=1.0, height=1.0, color=color)
        self._apply_transform(quad, position, size)
        self._parts.append(quad)
        return self

    def add_cylinder(
        self, position=(0, 0, 0), radius=0.5, height=1.0, segments=8, color=(1, 1, 1, 1)
    ):
        # Cylinders are tricky to scale uniformly, so we usually rely on the primitive params
        # But we still allow position offset
        cyl = PrimitiveMesher.create_cylinder(
            radius=radius, height=height, segments=segments, color=color
        )
        self._apply_transform(cyl, position, size=1.0)  # We assume radius handles size
        self._parts.append(cyl)
        return self

    def build(self) -> MeshData:
        final_mesh = MeshData()
        cursor = 0

        for part in self._parts:
            final_mesh.vertices.extend(part.vertices)
            final_mesh.colors.extend(part.colors)
            final_mesh.uvs.extend(part.uvs)

            # Shift triangles
            shifted_tris = [t + cursor for t in part.triangles]
            final_mesh.triangles.extend(shifted_tris)

            cursor += len(part.vertices)

        return final_mesh
