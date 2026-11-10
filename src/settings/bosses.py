from dataclasses import dataclass, field, replace
from enum import Enum

from src.settings import levels, resources


class BossId(Enum):
    TOM = "tom"
    PAYA = "paya"
    BALERINO = "balerino"


class BossDifficulty(Enum):
    NORMAL = "normal"
    HARD = "hard"  # à partir de la 2e rencontre en partie normale (cf. settings/progression.py)


@dataclass(frozen=True)
class BossConfig:
    name: str  # nom affiché dans le menu de sélection
    intro_title: str  # dernière ligne de l'écran d'intro
    victory_title: str  # nom affiché sur l'écran de victoire
    texture: tuple
    damage_texture: tuple  # affichée pendant l'invulnérabilité qui suit un coup
    menu_texture: tuple  # portrait dans le menu de sélection
    size: tuple  # taille d'affichage en px
    boss_spawn: tuple  # case (x, y) du coin haut-gauche du boss, même grille que player_spawn (décimales acceptées)
    boss_mode_background: tuple  # fond en "Mode Boss" ; en partie normale c'est celui de la série précédente
    arena: list
    player_spawn: tuple  # case (x, y) où le joueur apparaît dans l'arène (grille de settings/levels.py)
    health: int  # PV du boss (coups à encaisser avant de mourir)
    music: str = resources.MUSIC_BOSS
    evasive_duration: float = 2  # secondes d'invulnérabilité après un coup
    outro_duration: float = 5  # secondes entre la mort et la fin du combat
    blink_period_ms: int = 200  # clignotement pendant l'invulnérabilité
    blink_alphas: tuple = (200, 150)
    # Valeurs remplacées en difficulté HARD, ex : {"health": 15, "evasive_duration": 1}
    hard: dict = field(default_factory=dict)

    def for_difficulty(self, difficulty: "BossDifficulty") -> "BossConfig":
        if difficulty == BossDifficulty.HARD and self.hard:
            return replace(self, **self.hard)
        return self


# Écran d'intro (le jeu est en pause pendant ce temps)
INTRO_DURATION = 5  # secondes

BOSSES = {
    BossId.TOM: BossConfig(
        name="Tom",
        intro_title="** TOM DE L'ABBAYE  **",
        victory_title="Tom de L'Abbaye !!",
        texture=resources.TOM_TEXTURE,
        damage_texture=resources.TOM_DAMAGE_TEXTURE,
        menu_texture=resources.TOM_TEXTURE,
        size=(144 * 2, 286 * 2),
        boss_spawn=(18, 2.2),
        boss_mode_background=resources.BACKGROUND_GREEN,
        arena=levels.ARENA_TOM,
        player_spawn=(1, 1),
        health=10,
        hard={},
    ),
    BossId.PAYA: BossConfig(
        name="Paya",
        intro_title="** PAYA **",
        victory_title="Paya !!",
        texture=resources.BOSS_PLACEHOLDER_TEXTURE,
        damage_texture=resources.BOSS_PLACEHOLDER_TEXTURE,
        menu_texture=resources.BOSS_PLACEHOLDER_TEXTURE,
        size=(288, 414),
        boss_spawn=(18, 5.36),
        boss_mode_background=resources.BACKGROUND_RED,
        arena=levels.ARENA_PAYA,
        player_spawn=(2, 14),
        health=10,
        hard={},
    ),
    BossId.BALERINO: BossConfig(
        name="Balerino",
        intro_title="** BALERINO **",
        victory_title="Balerino !!",
        texture=resources.BALERINO_TEXTURE,
        damage_texture=resources.BALERINO_DAMAGE_TEXTURE,
        menu_texture=resources.BALERINO_TEXTURE,
        size=(104, 150),  # taille des sprites ; assez petit pour que le joueur lui saute par-dessus pendant la danse
        boss_spawn=(11.76, 12.5),  # au centre, posé sur le sol
        boss_mode_background=resources.BACKGROUND_BLUE,
        arena=levels.ARENA_BALERINO,
        player_spawn=(2, 10),  # au-dessus de la plateforme de gauche
        health=6,
        hard={},
    ),
}

# Ordre des cases dans le menu "Mode Boss"
BOSS_MENU_ORDER = [BossId.TOM, BossId.PAYA, BossId.BALERINO]

# Réglages propres à Tom
TOM_ATTACK_SPEED = 1000  # ms entre deux tirs
TOM_ANGRY_ATTACK_SPEED = 700
TOM_ANGRY_HEALTH = 3  # passe en colère à partir de ce nombre de PV
TOM_BULLET_OFFSET_X = 100  # les poules partent à cette distance devant Tom
TOM_SHIELD_COLUMN = 15  # colonne (en cases) des boucliers
TOM_SHIELD_SIZE = (1, 3)  # largeur, hauteur en cases
TOM_SHIELD_BOTTOM_ROW = 12
TOM_SHIELD_SPACING = 4  # en cases, entre deux boucliers
TOM_SHIELD_COUNT = 3  # emplacements ; à chaque coup, l'un d'eux reste ouvert
# Tom en difficulté HARD (à remplir) : remplace les réglages ci-dessus pour la 2e rencontre
TOM_HARD = {
    # "attack_speed": 800,
    # "angry_attack_speed": 500,
}


# Réglages propres à Balerino (arène : settings/levels.py, BALERINO_PLATFORM_*)
class BalerinoAttack(Enum):
    DANCE = "danse"  # danse de gauche à droite entre les plateformes
    CHICKENS = "poules"  # au centre, tire une colonne de poules de chaque côté
    SPLIT = "grand_ecart"  # sort par le haut et retombe en grand écart sur les plateformes


# Routine : chaque attaque passe une fois, dans un ordre tiré au hasard, puis on remélange
BALERINO_ATTACKS = [BalerinoAttack.DANCE, BalerinoAttack.CHICKENS, BalerinoAttack.SPLIT]
BALERINO_PAUSE = 1.0  # secondes d'attente (pose de repos) entre deux attaques
BALERINO_CONTACT_DAMAGE = 1  # PV perdus au contact (le bouclier ne protège pas)
# px ignorés en haut de Balerino pour le contact : il fait la hauteur des plateformes, sans cette marge
# il touche les pieds d'un joueur qui dépasse du bord (posé dessus, le joueur s'enfonce d'1 px)
BALERINO_CONTACT_TOLERANCE = 10

# 1. Danse
BALERINO_DANCE_SPEED = 300  # px/s
BALERINO_DANCE_CROSSINGS = 4  # nombre de demi-tours (chaque arrivée contre une plateforme compte)
# Pendant la danse, il tourne sur lui-même en continu, de l'image "gauche" à l'image "droite" et inversement.
# Effet "papier" (à la Paper Mario) : le sprite s'aplatit jusqu'à être vu de profil puis s'élargit sur
# l'autre image. BALERINO_SPIN_DEPTH > 0 lui donne une tranche d'épaisseur (plus 3D, façon item Minecraft).
BALERINO_SPIN_HALF_TURN = 0.4  # secondes par demi-tour (image "gauche" -> image "droite")
BALERINO_SPIN_FRAMES = 16  # images calculées une fois pour toutes (plus = plus fluide)
BALERINO_SPIN_DEPTH = 0  # px : épaisseur de la tranche vue de profil (0 = feuille de papier)
BALERINO_SPIN_SIDE_SHADE = 110  # 0-255 : luminosité de la tranche, si BALERINO_SPIN_DEPTH > 0 (255 = pas assombrie)

# 2. Poules
BALERINO_WALK_SPEED = 400  # px/s pour rejoindre le centre avant de tirer
BALERINO_CHICKEN_EXTRA_ROWS = 2  # en cases : Balerino s'étire d'autant (pointe des pieds) et la colonne dépasse
                                 # d'autant le dessus des plateformes (le joueur posé dessus est touché)
BALERINO_STRETCH_SPEED = 300  # px/s pour s'étirer avant de tirer (et reprendre sa taille après)
BALERINO_CHICKEN_WINDUP = 1.0  # secondes au centre, étiré, avant la première salve
BALERINO_CHICKENS_PER_SIDE = 6  # réparties du sol jusqu'à BALERINO_CHICKEN_EXTRA_ROWS au-dessus des plateformes
BALERINO_CHICKEN_VOLLEYS = 2  # nombre de salves
BALERINO_CHICKEN_VOLLEY_DELAY = 1.2  # secondes entre deux salves (et après la dernière)
BALERINO_CHICKEN_OFFSET_X = 10  # px entre le bord de Balerino et les poules

# 3. Grand écart
BALERINO_SPLIT_HEIGHT = None  # px ; la largeur est celle de l'arène (entre les deux murs)
                              # None = hauteur suivant les proportions du sprite (pas de déformation)
BALERINO_SPLIT_RISE_SPEED = 900  # px/s pour sortir par le haut
BALERINO_SPLIT_FALL_SPEED = 700  # px/s pour retomber
BALERINO_SPLIT_OFFSCREEN_DELAY = 1.5  # secondes hors de l'écran avant de retomber en grand écart
BALERINO_SPLIT_DURATION = 2.0  # secondes posé sur les plateformes

# Balerino en difficulté HARD (à remplir) : clés = attributs de Balerino, ex. "dance_speed"
BALERINO_HARD = {
    # "dance_speed": 400,
    # "pause": 0.6,
}
