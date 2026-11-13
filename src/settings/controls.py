"""
Touches du joueur et options par défaut. Les choix du joueur (fenêtre Options du menu principal)
sont enregistrés dans resources.OPTIONS_FILE et remplacent ces valeurs au lancement suivant.
"""

from enum import Enum

import pygame


class Action(Enum):
    JUMP = "saut"
    DOWN = "bouclier"  # au sol : bouclier ; en l'air : descente rapide
    LEFT = "gauche"
    RIGHT = "droite"
    SHOOT = "tir"  # fait aussi passer les boîtes de dialogue


# Ordre des lignes dans l'onglet "Touches"
ACTION_ORDER = [Action.JUMP, Action.LEFT, Action.RIGHT, Action.DOWN, Action.SHOOT]

# Deux touches par action : [principale, secondaire] (None = aucune)
DEFAULT_BINDINGS = {
    Action.JUMP: [pygame.K_z, pygame.K_UP],
    Action.DOWN: [pygame.K_s, pygame.K_DOWN],
    Action.LEFT: [pygame.K_q, pygame.K_LEFT],
    Action.RIGHT: [pygame.K_d, pygame.K_RIGHT],
    Action.SHOOT: [pygame.K_SPACE, None],
}
BINDING_SLOTS = 2
CANCEL_BINDING_KEY = pygame.K_ESCAPE  # pendant l'attente d'une touche : annule
CLEAR_BINDING_KEY = pygame.K_BACKSPACE  # pendant l'attente d'une touche : vide la case

# Volumes par défaut, en % de la barre (0-100)
DEFAULT_MUSIC_VOLUME = 50
DEFAULT_SOUND_VOLUME = 100
MUSIC_VOLUME_MAX = 0.3  # volume pygame de la musique quand la barre est à 100 %
SOUND_VOLUME_MAX = 1.0  # volume pygame des effets quand la barre est à 100 %
