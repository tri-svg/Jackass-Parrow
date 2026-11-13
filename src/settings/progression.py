"""
Déroulement d'une partie :

    série PREMIERE -> boss 1 -> série DEUXIEME -> boss 2 -> série TROISIEME -> boss 3
    -> série BONUS -> boss 1 -> série BONUS -> boss 2 -> série BONUS -> boss 3 -> ... (sans fin)

- Le fond d'un combat de boss est celui de la série qui le précède.
- À partir de la 2e rencontre, un boss est en difficulté HARD (cf. settings/bosses.py).
- Level (affiché dans le HUD) : chaque tableau, boss ou tableau spécial compte pour un level,
  celui en cours compris. Le nombre d'ennemis d'un tableau vaut level + ENEMY_COUNT_OFFSET,
  limité par le nombre de blocs "spawnable".
"""

from enum import Enum

from src.settings import levels, resources
from src.settings.bosses import BossId
from src.settings.enemies import EnemyType


class SeriesType(Enum):
    PREMIERE = "premiere"
    DEUXIEME = "deuxieme"
    TROISIEME = "troisieme"
    BONUS = "bonus"


# Ordre des séries ; une fois la liste épuisée, toutes les séries suivantes sont BONUS
SERIES_ORDER = [SeriesType.PREMIERE, SeriesType.DEUXIEME, SeriesType.TROISIEME]

SERIES = {
    SeriesType.PREMIERE: {
        "level_count": 4,  # nombre de tableaux de la série
        "level_ids": levels.NORMAL_LEVEL_IDS,  # tableaux tirés au hasard (bornes incluses)
        "background": resources.BACKGROUND_BLUE,  # fond des tableaux ET du boss qui suit
        # ennemis qui peuvent apparaître, avec leurs chances relatives (ici 3 chevaliers pour 1 poule) ;
        # un type absent n'apparaît pas dans la série
        "enemies": {EnemyType.KNIGHT: 3, EnemyType.KAMIKAZE: 1},
        # au-delà de ce level, les chevaliers tirés deviennent énervés ; None = jamais
        "angry_above_level": None,
    },
    SeriesType.DEUXIEME: {
        "level_count": 6,
        "level_ids": levels.NORMAL_LEVEL_IDS,
        "background": resources.BACKGROUND_GREEN,
        "enemies": {EnemyType.KNIGHT: 3, EnemyType.KAMIKAZE: 1},
        "angry_above_level": None,  # pas de chevalier énervé dans la 2e série
    },
    SeriesType.TROISIEME: {
        "level_count": 5,
        "level_ids": levels.HARD_LEVEL_IDS,
        "background": resources.BACKGROUND_RED,
        "enemies": {EnemyType.KNIGHT: 3, EnemyType.KAMIKAZE: 1},
        "angry_above_level": 5,
    },
    SeriesType.BONUS: {
        "level_count": 5,
        "level_ids": levels.NORMAL_LEVEL_IDS,
        "background": resources.BACKGROUND_RED,
        "enemies": {EnemyType.KNIGHT: 3, EnemyType.KAMIKAZE: 1},
        "angry_above_level": 5,
    },
}

BOSS_CYCLE = [BossId.BALERINO, BossId.TOM, BossId.PAYA]

ENEMY_COUNT_OFFSET = 0  # ennemis d'un tableau = level + ce décalage (négatif : moins d'ennemis)

# Tableau spécial (settings/special_level.py) : une seule fois par partie, après le premier combat
# contre ce boss ; None pour le désactiver
SPECIAL_LEVEL_AFTER_BOSS = BossId.TOM

# Nombre de rencontres avec un même boss avant qu'il passe en difficulté HARD
BOSS_HARD_FROM_ENCOUNTER = 2
