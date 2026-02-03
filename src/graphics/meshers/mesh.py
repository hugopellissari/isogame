from dataclasses import dataclass, field


@dataclass
class MeshData:
    """
    Raw geometric data.
    """
    vertices: list[tuple[float, float, float]] = field(default_factory=list)
    triangles: list[int] = field(default_factory=list) # Indices
    uvs: list[tuple[float, float]] = field(default_factory=list)
    # Colors stored as generic (r, g, b, a) tuples, 0.0 to 1.0
    colors: list[tuple[float, float, float, float]] = field(default_factory=list) 

    def clear(self):
        self.vertices.clear()
        self.triangles.clear()
        self.uvs.clear()
        self.colors.clear()
