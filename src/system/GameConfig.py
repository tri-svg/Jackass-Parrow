from enum import Enum, IntEnum


class APPConfig(IntEnum):
    WIDTH = 1280
    HEIGHT = 800
    FPS = 60


class WorldType(Enum):
    MONDE_FORET = 0
    MONDE_JUNGLE = 1
    MONDE_VOLCAN = 2
    FIN_DE_PARTIE = 3


class DIFFICULTY(Enum):
    FACILE = 0
    NORMAL = 1
    DIFFICILE = 2
    OLD = 3
    TEST_DEBUG = 4


# Tableaux tirés au hasard pour chaque type de monde (id de LevelCollection.LEVELS, bornes incluses)
# 1-5 : tableaux normaux, 6-10 : tableaux "HARD"
LEVEL_POOLS = {
    WorldType.MONDE_FORET: (1, 5),
    WorldType.MONDE_JUNGLE: (1, 5),
    WorldType.MONDE_VOLCAN: (5, 10),
}

# Les mondes augmentent leur niveau de danger de 1 à chaque tableau.
# Un monde peut avoir un niveau de danger par défaut paramétré ("danger").
# Chaque boss est associé à un type de monde, chaque monde a un boss spécifique.
# Les niveaux de difficulté sont définis par une série de mondes paramétrés.
# Un monde avec "nb_level": None est infini : pas de boss, les tableaux s'enchaînent sans fin.
# Une difficulté sans monde infini boucle sur sa liste de mondes ;
# quand elle boucle, le niveau de danger par défaut de ses mondes augmente de 3.
worlds_config = {
    DIFFICULTY.FACILE: [
        {"monde": WorldType.MONDE_FORET, "nb_level": 10},
        {"monde": WorldType.MONDE_JUNGLE, "nb_level": 10},
    ],
    DIFFICULTY.NORMAL: [
        {"monde": WorldType.MONDE_FORET, "nb_level": 6},
        {"monde": WorldType.MONDE_JUNGLE, "nb_level": 7, "danger": 2},
        {"monde": WorldType.MONDE_VOLCAN, "nb_level": 7, "danger": 3},
    ],
    DIFFICULTY.DIFFICILE: [
        {"monde": WorldType.MONDE_JUNGLE, "nb_level": 6, "danger": 2},
        {"monde": WorldType.MONDE_VOLCAN, "nb_level": 7, "danger": 4},
        {"monde": WorldType.MONDE_FORET, "nb_level": 7, "danger": 4},
    ],
    # Déroulement de la version GameJam : 7 tableaux, Tom, puis tableaux HARD
    # (fond rouge) à l'infini avec un danger qui continue de monter.
    DIFFICULTY.OLD: [
        {"monde": WorldType.MONDE_JUNGLE, "nb_level": 7},
        {"monde": WorldType.MONDE_VOLCAN, "nb_level": None, "danger": 8},
    ],
    DIFFICULTY.TEST_DEBUG: [
        {"monde": WorldType.MONDE_JUNGLE, "nb_level": 2},
        {"monde": WorldType.MONDE_VOLCAN, "nb_level": None},
    ],
}
