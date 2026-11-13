from functools import lru_cache

import pygame

from src.settings import levels, resources
from src.system import assets


@lru_cache(maxsize=None)
def _dirt_texture(grass_color: tuple = None) -> pygame.Surface:
    """
    Texture de terre dont l'herbe prend la couleur `grass_color` (None : vert d'origine).
    Les nuances sont conservées : chaque pixel d'herbe garde sa luminosité par rapport à GRASS_SOURCE_GREEN.
    """
    texture = assets.image(*resources.DIRT_TEXTURE)
    if grass_color is None:
        return texture
    texture = texture.copy()
    source_green = levels.GRASS_SOURCE_GREEN[1]
    for y in range(texture.get_height()):
        for x in range(texture.get_width()):
            r, g, b, a = texture.get_at((x, y))
            if g - max(r, b) < levels.GRASS_MIN_GREEN_LEAD:
                continue
            shade = g / source_green
            texture.set_at((x, y), [min(255, round(channel * shade)) for channel in grass_color] + [a])
    return texture


@lru_cache(maxsize=None)
def _block_surface(width: int, height: int, dirt: bool, transparent: bool, grass_color: tuple = None) -> pygame.Surface:
    """Surface d'un bloc (partagée entre tous les blocs de même taille, lecture seule)."""
    tile = levels.TILE_SIZE
    surface = pygame.Surface([width * tile, height * tile], pygame.SRCALPHA)
    if transparent:
        surface.fill((200, 0, 0, 0))
        return surface

    texture = _dirt_texture(grass_color) if dirt else assets.image(*resources.BLOCK_TEXTURE)
    for texture_y in range(height):
        for texture_x in range(width):
            surface.blit(texture, (texture_x * tile, texture_y * tile))
    return surface


class Block(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int, spawnable=False, transparent=False,
                 grass_color: tuple = None):
        super().__init__()
        self.spawnable = spawnable
        self.transparent = transparent
        self.image = _block_surface(width, height, y == levels.GROUND_ROW, transparent, grass_color)
        offset_x, offset_y = levels.BLOCK_OFFSET
        self.rect = self.image.get_rect(x=x * levels.TILE_SIZE + offset_x, y=y * levels.TILE_SIZE + offset_y)
        self.size = width, height
