"""
Fenêtre du jeu. Le jeu est toujours calculé et dessiné en display.WIDTH x display.HEIGHT (surface
renvoyée par create_window) : SDL agrandit l'image à la taille de la fenêtre (pygame.SCALED), avec des
bandes noires si les proportions diffèrent, et convertit la souris. La physique, les collisions et
pygame_gui ne voient donc jamais la vraie taille de la fenêtre : aucune différence de comportement.
"""

import os
import sys
import warnings

import pygame

from src.settings import display
from src.settings.display import DisplayMode


def desktop_size() -> tuple:
    sizes = pygame.display.get_desktop_sizes()
    return sizes[0] if sizes else (display.WIDTH, display.HEIGHT)


def available_window_sizes() -> list:
    """
    Tailles de display.WINDOW_SIZES qui tiennent sur l'écran avec la barre de titre (au moins la plus petite).
    La taille exacte de l'écran, c'est le mode sans bordure.
    """
    desktop_width, desktop_height = desktop_size()
    sizes = [size for size in display.WINDOW_SIZES if size[0] <= desktop_width and size[1] < desktop_height]
    return sizes or [min(display.WINDOW_SIZES)]


def _window() -> "pygame.Window":
    with warnings.catch_warnings():  # pygame-ce signale l'ancienne API display, qu'on garde pour le reste du jeu
        warnings.simplefilter("ignore")
        return pygame.Window.from_display_module()


def create_window(mode: DisplayMode, window_size: tuple) -> pygame.Surface:
    """Ouvre la fenêtre et renvoie la surface de jeu (toujours display.WIDTH x display.HEIGHT)."""
    os.environ.setdefault("SDL_RENDER_SCALE_QUALITY", display.SCALE_QUALITY)
    if sys.platform == "win32":
        # le rendu par défaut (Direct3D 9) affiche un écran noir dans une fenêtre moins haute que le jeu
        os.environ.setdefault("SDL_RENDER_DRIVER", display.WINDOWS_RENDER_DRIVER)
    surface = pygame.display.set_mode((display.WIDTH, display.HEIGHT), pygame.SCALED)
    pygame.display.set_caption(display.WINDOW_TITLE)
    apply(mode, window_size)
    return surface


def apply(mode: DisplayMode, window_size: tuple):
    """Change le mode d'affichage / la taille de la fenêtre sans toucher à la surface de jeu."""
    window = _window()
    window.minimum_size = display.MIN_WINDOW_SIZE  # SCALED l'impose sinon à WIDTH x HEIGHT (trop grand pour 1280 x 720)
    if mode == DisplayMode.BORDERLESS:
        window.borderless = True
        window.size = desktop_size()
        window.position = (0, 0)
    else:
        window.borderless = False
        window.size = window_size
        window.position = pygame.WINDOWPOS_CENTERED
