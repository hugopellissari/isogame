from ursina import Texture, color
from PIL import Image
import random

_texture_cache = {}

def get_color_texture(r: int, g: int, b: int) -> Texture:
    r, g, b = [max(0, min(255, int(c))) for c in (r, g, b)]
    key = (r, g, b)
    if key not in _texture_cache:
        img = Image.new('RGB', (1, 1), (r, g, b))
        _texture_cache[key] = Texture(img)
    return _texture_cache[key]

class ColorPalette:
    # 1. LIGHTER, WARMER GRASS (Like a lawn)
    # Less saturation, more yellow/brown undertone
    LAND_BASE = (110, 160, 60) 
    
    # 2. DARKER, COOLER TREES (Like a deep forest)
    # Much lower brightness helps them pop against light grass
    TREE_BASE = (30, 80, 40)
    
    WATER_BASE = (30, 144, 255)
    TRUNK = (90, 50, 20)

    @staticmethod
    def get_land_texture():
        r, g, b = ColorPalette.LAND_BASE
        # Low noise for ground so it doesn't distract
        noise = random.randint(-5, 5) 
        return get_color_texture(r + noise, g + noise, b + noise)

    @staticmethod
    def get_water_texture():
        r, g, b = ColorPalette.WATER_BASE
        noise = random.randint(-10, 10)
        return get_color_texture(r + noise, g + noise, b + noise)

    @staticmethod
    def random_leaf_color():
        # Generate variation based on the darker TREE_BASE
        r, g, b = ColorPalette.TREE_BASE
        # High variation creates distinct "light" and "dark" trees
        noise = random.randint(-20, 40)
        return (
            r + noise, 
            g + noise + 20, # Boost green slightly
            b + noise
        )
