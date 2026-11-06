"""
Chargement centralisé des ressources (images, sons, polices).

Chaque ressource n'est lue sur le disque qu'une seule fois puis gardée en cache.

ATTENTION : les surfaces renvoyées par `image()` sont partagées.
Ne jamais les modifier en place (fill, blit, set_alpha...) : utiliser
`image_copy()` pour obtenir une surface modifiable.
"""

from functools import lru_cache
from pathlib import Path

import pygame

from src.settings import resources

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"
IMG_DIR = ASSETS_DIR / "img"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"
THEME_PATH = ASSETS_DIR.joinpath(*resources.GUI_THEME)
SCORES_FILE_PATH = PROJECT_ROOT / resources.SCORES_FILE


@lru_cache(maxsize=None)
def image(*parts: str) -> pygame.Surface:
    """Image partagée (lecture seule) : assets/img/<parts...>"""
    return pygame.image.load(str(IMG_DIR.joinpath(*parts))).convert_alpha()


@lru_cache(maxsize=None)
def image_flipped(*parts: str) -> pygame.Surface:
    """Image partagée retournée horizontalement (lecture seule)."""
    return pygame.transform.flip(image(*parts), True, False)


@lru_cache(maxsize=None)
def image_with_alpha(alpha: int, *parts: str) -> pygame.Surface:
    """Copie partagée d'une image avec une transparence globale (lecture seule)."""
    surface = image(*parts).copy()
    surface.set_alpha(alpha)
    return surface


@lru_cache(maxsize=None)
def image_scaled(size: tuple, *parts: str) -> pygame.Surface:
    """Image partagée redimensionnée (lecture seule)."""
    return pygame.transform.scale(image(*parts), size)


def image_copy(*parts: str) -> pygame.Surface:
    """Copie modifiable d'une image."""
    return image(*parts).copy()


@lru_cache(maxsize=None)
def sound(name: str) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / name))


@lru_cache(maxsize=None)
def font(name: str, size: int) -> pygame.font.Font:
    return pygame.font.Font(str(FONTS_DIR / name), size)


def play_music(name: str) -> None:
    pygame.mixer.music.load(str(SOUNDS_DIR / name))
    pygame.mixer.music.play(-1)
