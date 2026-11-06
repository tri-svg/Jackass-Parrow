from functools import lru_cache

import pygame

from src.system import assets

TILE_SIZE = 50
GROUND_ROW = 16  # les blocs posés sur cette ligne utilisent la texture de terre


@lru_cache(maxsize=None)
def _block_surface(width: int, height: int, dirt: bool, transparent: bool) -> pygame.Surface:
    """Surface d'un bloc (partagée entre tous les blocs de même taille, lecture seule)."""
    surface = pygame.Surface([width * TILE_SIZE, height * TILE_SIZE], pygame.SRCALPHA)
    if transparent:
        surface.fill((200, 0, 0, 0))
        return surface

    texture = assets.image("block", "dirt.png" if dirt else "block.png")
    for texture_y in range(height):
        for texture_x in range(width):
            surface.blit(texture, (texture_x * TILE_SIZE, texture_y * TILE_SIZE))
    return surface


class Block(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, width: int, height: int, spawnable=False, transparent=False):
        super().__init__()
        self.spawnable = spawnable
        self.transparent = transparent
        self.image = _block_surface(width, height, y == GROUND_ROW, transparent)
        self.rect = self.image.get_rect(x=(x * TILE_SIZE) + 40, y=y * TILE_SIZE - 25)
        self.size = width, height
