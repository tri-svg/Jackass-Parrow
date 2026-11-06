"""
Déroulement d'une partie :

    série PREMIERE -> boss 1 -> série DEUXIEME -> boss 2 -> série TROISIEME -> boss 3
    -> série BONUS -> boss 1 -> série BONUS -> boss 2 -> série BONUS -> boss 3 -> ... (sans fin)

- Le fond d'un combat de boss est celui de la série qui le précède.
- À partir de la 2e rencontre, un boss est en difficulté HARD (cf. settings/bosses.py).
- Le niveau de danger (= nombre d'ennemis, limité par le nombre de blocs "spawnable")
  augmente de 1 à chaque tableau et ne redescend jamais.
"""

from enum import Enum

from src.settings import levels, resources
from src.settings.bosses import BossId


class SeriesType(Enum):
    PREMIERE = "premiere"
    DEUXIEME = "deuxieme"
    TROISIEME = "troisieme"
    BONUS = "bonus"


# Ordre des séries ; une fois la liste épuisée, toutes les séries suivantes sont BONUS
SERIES_ORDER = [SeriesType.PREMIERE, SeriesType.DEUXIEME, SeriesType.TROISIEME]

SERIES = {
    SeriesType.PREMIERE: {
        "level_count": 3,  # nombre de tableaux de la série
        "level_ids": levels.NORMAL_LEVEL_IDS,  # tableaux tirés au hasard (bornes incluses)
        "background": resources.BACKGROUND_BLUE,  # fond des tableaux ET du boss qui suit
    },
    SeriesType.DEUXIEME: {
        "level_count": 5,
        "level_ids": levels.NORMAL_LEVEL_IDS,
        "background": resources.BACKGROUND_GREEN,
    },
    SeriesType.TROISIEME: {
        "level_count": 5,
        "level_ids": levels.NORMAL_LEVEL_IDS,
        "background": resources.BACKGROUND_RED,
    },
    SeriesType.BONUS: {
        "level_count": 5,
        "level_ids": levels.NORMAL_LEVEL_IDS,
        "background": resources.BACKGROUND_RED,
    },
}

BOSS_CYCLE = [BossId.BALERINO, BossId.TOM, BossId.PAYA]

DANGER_START = 0  # le premier tableau aura DANGER_START + 1
DANGER_BONUS_AFTER_BOSS = 0  # danger ajouté après chaque boss vaincu

# Nombre de rencontres avec un même boss avant qu'il passe en difficulté HARD
BOSS_HARD_FROM_ENCOUNTER = 2
