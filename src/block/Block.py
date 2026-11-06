from functools import lru_cache

import pygame

from src.settings import levels, resources
from src.system import assets


@lru_cache(maxsize=None)
def _block_surface(width: int, height: int, dirt: bool, transparent: bool) -> pygame.Surface:
    """Surface d'un bloc (partagée entre tous les blocs de même taille, lecture seule)."""
    tile = levels.TILE_SIZE
    surface = pygame.Surface([width * tile, height * tile], pygame.SRCALPHA)
    if transparent:
        surface.fill((200, 0, 0, 0))
        return surface

    texture = assets.image(*(resources.DIRT_TEXTURE if dirt else resources.BLOCK_TEXTURE))
    for texture_y in range(height):
        for texture_x in range(width):
            surface.blit(texture, (texture_x * tile, texture_y * tile))
    return surface


class Block(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int, spawnable=False, transparent=False):
        super().__init__()
        self.spawnable = spawnable
        self.transparent = transparent
        self.image = _block_surface(width, height, y == levels.GROUND_ROW, transparent)
        offset_x, offset_y = levels.BLOCK_OFFSET
        self.rect = self.image.get_rect(x=x * levels.TILE_SIZE + offset_x, y=y * levels.TILE_SIZE + offset_y)
        self.size = width, height
