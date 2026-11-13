"""
Disposition des tableaux, en cases de 50px (l'écran fait 24 x 16 cases).

    (x, y)                                                  point d'apparition du joueur
    (x, y, largeur, hauteur[, spawnable[, transparent]])    bloc
        spawnable   : un ennemi peut apparaître dessus
        transparent : invisible et laisse passer les tirs (mais pas le joueur)
"""

from src.settings import resources

TILE_SIZE = 50
BLOCK_OFFSET = (40, -25)  # décalage en px de la grille des blocs
GROUND_ROW = 16  # les blocs de cette ligne utilisent la texture de terre

# Couleur de l'herbe (le vert de la texture de terre) selon le fond ; fond absent = vert d'origine
GRASS_COLORS = {
    resources.BACKGROUND_BLUE: (28, 34, 92),  # bleu foncé (séries faciles)
    resources.BACKGROUND_GREEN: (22, 66, 12),  # vert foncé (série moyenne)
    resources.BACKGROUND_RED: (78, 18, 22),  # rouge foncé (séries hard)
}
GRASS_SOURCE_GREEN = (52, 165, 0)  # vert de l'herbe dans resources.DIRT_TEXTURE (prend la couleur ci-dessus)
GRASS_MIN_GREEN_LEAD = 5  # un pixel est de l'herbe si son vert dépasse son rouge et son bleu d'autant

# Blocs présents dans tous les tableaux : sol et murs
COMMON_BLOCKS = [
    (-1, 16, 26, 1),
    (-2, -8, 1, 28),
    (25, -8, 1, 28),
]

LEVEL1 = [
    (12, 14),
    (0, 5, 6, 2, True),
    (18, 5, 6, 2, True),
    (9, 9, 6, 2, True),
    (2, 13, 5, 3, True),
    (17, 13, 5, 3, True),
]
LEVEL2 = [
    (12, 14),
    (5, 2, 3, 2),
    (11, 2, 3, 4),
    (17, 2, 3, 2),
    (5, 12, 3, 1, True),
    (11, 10, 3, 3, True),
    (17, 8, 3, 1, True),
]
LEVEL3 = [
    (2, 14),
    # platform
    (6, 13, 6, 1, True),
    (1, 9, 4, 1, True),
    (5, 5, 4, 1, True),
    (12, 5, 5, 1, True),
    # autre
    (20, 9, 4, 1, True),
    (18, 13, 6, 1, True),
]
LEVEL4 = [
    (15, 14),
    #(-1, 4, 3, 2),
    (-1, -3, 3, 19),
    (2, 5, 2, 12),

    #(2, 11, 3, 5),
    #(4, 9, 1, 2),
    (4, 9, 3, 7),
    (7, 13, 3, 3),
    (17, 5, 4, 2, True),
    (17, 9, 4, 2, True),
    (17, 13, 4, 3, True),
]
LEVEL5 = [
    (0, 10),
    (-1, 12, 4, 4),
    (3, 14, 2, 2),
    # (6, 13, 11, 3),
    (6, 8, 10, 2),
    (9, 6, 5, 3),
    (10, 3, 3, 3),
    (20, 3, 4, 2, True),
    (20, 8, 4, 2, True),
    (20, 14, 4, 2, True),
]

LEVEL1MID = [
    (1, 1),
    (3, 9, 3, 3),
    (6, 11, 4, 1, True),
    (10, 7, 8, 2, True),
    (0, 4, 2, 1),
    (20, 5, 4, 7, True),
    (0, 15, 2, 1, True),
    (13, 15, 2, 1, True),
]
LEVEL1HARD = [
    (12, 14),
    (0, 5, 6, 1, True),
    (18, 6, 6, 1, True),
    (10, 4, 5, 1, True),
    (9, 9, 6, 2, True),
    (3, 13, 4, 3, True),
    (17, 13, 4, 3, True),
    (0, 11, 3, 5, True),
    (21, 11, 3, 5, True),
]
LEVEL2HARD = [
    (12, 14),
    (5, 1, 3, 3),
    (11, 1, 3, 5),
    (17, 1, 3, 3),
    (5, 12, 3, 1, True),
    (11, 10, 3, 3, True),
    (0, 10, 3, 6, True),
    (17, 8, 3, 1, True),
    (0, 6, 3, 1, True),
    (20, 14, 3, 1, True),
]
LEVEL3HARD = [
    (2, 14),
    # platform
    (5, 4, 4, 1, True),
    (12, 5, 5, 1, True),
    (0, 9, 3, 1, True),
    (20, 8, 4, 1, True),
    (6, 13, 6, 1, True),
    (18, 12, 6, 1, True),
]
LEVEL4HARD = [
    (15, 14),
    (-1, -3, 3, 19),
    (-1, 4, 3, 2),
    (2, 6, 2, 7, True),
    (4, 10, 3, 1, True),
    (2, 11, 3, 5),
    (7, 14, 3, 2, True),
    (17, 4, 4, 2, True),
    (17, 9, 4, 2, True),
    (17, 14, 4, 2, True),
]
LEVEL5HARD = [
    (0, 10),
    (10, 4, 3, 3, True),
    (9, 7, 5, 3),
    (6, 8, 3, 2, True),
    (-1, 12, 4, 4),
    (3, 14, 2, 2, True),
    (21, 3, 4, 2, True),
    (21, 8, 4, 2, True),
    (21, 14, 4, 2, True),
]
LEVELS = [
    LEVEL1,
    LEVEL2,
    LEVEL3,
    LEVEL4,
    LEVEL5,
    LEVEL1HARD,
    LEVEL2HARD,
    LEVEL3HARD,
    LEVEL4HARD,
    LEVEL5HARD,
]

# ids (à partir de 1) utilisés par la progression : 1-5 normaux, 6-10 HARD
NORMAL_LEVEL_IDS = (1, 5)
MID_LEVEL_IDS = None  # aucun pour l'instant ; ex. (11, 15)
HARD_LEVEL_IDS = (6, 10)
# fond des tableaux lancés depuis Options > Debug (et de leur miniature), selon leur difficulté
LEVEL_DIFFICULTY_BACKGROUNDS = {
    "normal": resources.BACKGROUND_BLUE,
    "mid": resources.BACKGROUND_GREEN,
    "hard": resources.BACKGROUND_RED,
}

# Tableau spécial (cf. settings/special_level.py) : une bande de blocs en bas et une en haut,
# sur toute la largeur
SPECIAL_BAND_HEIGHT = 3  # en cases
SPECIAL_TOP_BAND_ROW = 0  # ligne du haut de la bande du haut
SPECIAL_BOTTOM_BAND_ROW = GROUND_ROW - SPECIAL_BAND_HEIGHT  # ligne du haut de la bande du bas (posée sur le sol)
SPECIAL_FIRST_COLUMN = -1  # les bandes vont d'un bord à l'autre de l'écran
SPECIAL_BAND_WIDTH = 26
SPECIAL_LEVEL = [
    (1, 10),  # joueur, à gauche sur la bande du bas
    (SPECIAL_FIRST_COLUMN, SPECIAL_TOP_BAND_ROW, SPECIAL_BAND_WIDTH, SPECIAL_BAND_HEIGHT),
    (SPECIAL_FIRST_COLUMN, SPECIAL_BOTTOM_BAND_ROW, SPECIAL_BAND_WIDTH, SPECIAL_BAND_HEIGHT),
]

# Arènes de boss (sans point d'apparition : il est dans la config du boss, settings/bosses.py)
ARENA_TOM = [
    (-1, 3, 2, 1, False),
    (-1, 7, 4, 1, False),
    (-1, 11, 6, 1, False),
    (-1, 15, 8, 1, False),
    (17, 14, 6, 2, False),
    (17, 0, 6, 3),
    (17, 3, 1, 11, False, True),
]
# Murs visibles de chaque côté, sur toute la hauteur ; l'arène jouable va de ARENA_FIRST_COLUMN
# à ARENA_LAST_COLUMN (incluses)
ARENA_WALL_LEFT_COLUMN = -1
ARENA_WALL_RIGHT_COLUMN = 24
ARENA_FIRST_COLUMN = ARENA_WALL_LEFT_COLUMN + 1
ARENA_LAST_COLUMN = ARENA_WALL_RIGHT_COLUMN - 1
ARENA_WALL_TOP_ROW = -1
ARENA_WALLS = [
    (ARENA_WALL_LEFT_COLUMN, ARENA_WALL_TOP_ROW, 1, GROUND_ROW - ARENA_WALL_TOP_ROW),
    (ARENA_WALL_RIGHT_COLUMN, ARENA_WALL_TOP_ROW, 1, GROUND_ROW - ARENA_WALL_TOP_ROW),
]

# Paya (provisoire) : sol plat entre les deux murs
ARENA_PAYA = list(ARENA_WALLS)

# Balerino : une plateforme contre chaque mur
BALERINO_PLATFORM_WIDTH = 4  # en cases
BALERINO_PLATFORM_HEIGHT = 3  # en cases, du sol jusqu'au dessus de la plateforme
BALERINO_PLATFORM_FLOATING = False  # False : pilier plein jusqu'au sol ; True : plateforme flottante
BALERINO_PLATFORM_THICKNESS = 1  # en cases, épaisseur d'une plateforme flottante
BALERINO_PLATFORM_TOP_ROW = GROUND_ROW - BALERINO_PLATFORM_HEIGHT
_balerino_platform_rows = BALERINO_PLATFORM_THICKNESS if BALERINO_PLATFORM_FLOATING else BALERINO_PLATFORM_HEIGHT
ARENA_BALERINO = ARENA_WALLS + [
    (ARENA_FIRST_COLUMN, BALERINO_PLATFORM_TOP_ROW, BALERINO_PLATFORM_WIDTH, _balerino_platform_rows),
    (ARENA_LAST_COLUMN - BALERINO_PLATFORM_WIDTH + 1, BALERINO_PLATFORM_TOP_ROW,
     BALERINO_PLATFORM_WIDTH, _balerino_platform_rows),
]
