from enum import Enum


class EnemyType(Enum):
    """Types d'ennemis des tableaux ; leur apparition se règle par série dans settings/progression.py."""
    KNIGHT = "chevalier"
    ANGRY_KNIGHT = "chevalier_angwy"
    KAMIKAZE = "poule_kamikaze"


BULLET_SPEED = 600  # px/s (tirs du joueur et poules lancées par les ennemis)

# Chevalier
KNIGHT_SIZE = (75, 90)
KNIGHT_SCORE = 100
KNIGHT_SHOT_DELAY = (1600, 2200)  # ms, tiré au hasard entre ces deux valeurs
KNIGHT_DEAD_ALPHA = 150
KNIGHT_DEAD_RISE_SPEED = 5  # px/frame : le chevalier mort s'envole

# Chevalier énervé (apparition : "enemies" et "angry_above_level" des séries, settings/progression.py)
ANGRY_KNIGHT_SCORE = 150
ANGRY_KNIGHT_SHOT_COEF = 0.7  # multiplie le délai entre deux tirs

# Poule kamikaze
KAMIKAZE_SCORE = 100
KAMIKAZE_SPEED = 5  # px/frame
KAMIKAZE_PLATFORM_MARGIN = 15  # px avant le bord de la plateforme pour faire demi-tour
KAMIKAZE_WALK_DELAY = 100  # ms entre deux images de marche
KAMIKAZE_EXPLOSION_DELAY = 50  # ms entre deux images d'explosion

# Apparition (décalage vertical par rapport au haut du bloc)
KNIGHT_SPAWN_OFFSET_Y = 90
KAMIKAZE_SPAWN_OFFSET_Y = 70
