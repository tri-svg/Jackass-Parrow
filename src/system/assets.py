"""
Chargement centralisé des ressources (images, sons, polices).

Chaque ressource n'est lue sur le disque qu'une seule fois puis gardée en cache.
Avant, chaque ennemi / projectile / bloc rechargeait ses images et ses sons
(un `Sound()` = 6 fichiers .wav décodés par ennemi), ce qui provoquait des
micro-freezes à chaque changement de tableau et à chaque tir.

ATTENTION : les surfaces renvoyées par `image()` sont partagées.
Ne jamais les modifier en place (fill, blit, set_alpha...) : utiliser
`image_copy()` pour obtenir une surface modifiable.
"""

from functools import lru_cache
from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"
IMG_DIR = ASSETS_DIR / "img"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"
THEME_PATH = ASSETS_DIR / "themes" / "theme.json"
SCORES_FILE_PATH = PROJECT_ROOT / "scores.json"

MAIN_THEME_PATH = SOUNDS_DIR / "mainTheme.mp3"
BOSS_THEME_PATH = SOUNDS_DIR / "bossTheme.mp3"

CAT_COMIC_FONT = "Cat Comic.ttf"
DIMBO_FONT = "Dimbo Regular.ttf"


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


def image_copy(*parts: str) -> pygame.Surface:
    """Copie modifiable d'une image."""
    return image(*parts).copy()


@lru_cache(maxsize=None)
def sound(name: str) -> pygame.mixer.Sound:
    return pygame.mixer.Sound(str(SOUNDS_DIR / name))


@lru_cache(maxsize=None)
def font(name: str, size: int) -> pygame.font.Font:
    return pygame.font.Font(str(FONTS_DIR / name), size)


def play_music(path: Path) -> None:
    pygame.mixer.music.load(str(path))
    pygame.mixer.music.play(-1)
