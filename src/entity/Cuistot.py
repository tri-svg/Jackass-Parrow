import pygame

from src.settings import levels, resources
from src.settings import special_level as cfg
from src.system import assets


def special_level_ground_y() -> int:
    """Haut de la bande du bas du tableau spécial, en px."""
    return levels.SPECIAL_BOTTOM_BAND_ROW * levels.TILE_SIZE + levels.BLOCK_OFFSET[1]


class Cuistot(pygame.sprite.Sprite):
    """Cuistot Bongo, le personnage du tableau spécial : la jambe en bas, le bongo empilé dessus."""

    def __init__(self):
        super().__init__()
        leg = assets.image(*resources.CUISTOT_LEG_TEXTURE)
        bongo = assets.image(*resources.CUISTOT_BONGO_TEXTURE)
        width = max(leg.get_width(), bongo.get_width())
        bongo_y = 0
        leg_y = bongo.get_height() - cfg.CUISTOT_STACK_OVERLAP
        self.image = pygame.Surface((width, leg_y + leg.get_height()), pygame.SRCALPHA)
        self.image.blit(leg, ((width - leg.get_width()) // 2, leg_y))
        self.image.blit(bongo, ((width - bongo.get_width()) // 2, bongo_y))
        self.rect = self.image.get_rect(centerx=cfg.CUISTOT_CENTER_X, bottom=special_level_ground_y())


class Oven(pygame.sprite.Sprite):
    """Four posé à côté du cuistot (décor)."""

    def __init__(self, cuistot: Cuistot):
        super().__init__()
        self.image = assets.image(*resources.OVEN_TEXTURE)
        self.rect = self.image.get_rect(bottom=special_level_ground_y())
        if cfg.OVEN_SIDE > 0:
            self.rect.left = cuistot.rect.right + cfg.OVEN_GAP
        else:
            self.rect.right = cuistot.rect.left - cfg.OVEN_GAP
