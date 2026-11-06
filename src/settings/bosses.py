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
    position: tuple  # coin haut-gauche en px
    boss_mode_background: tuple  # fond en "Mode Boss" ; en partie normale c'est celui de la série précédente
    arena: list
    health: int = 10
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
        position=(900, 110),
        boss_mode_background=resources.BACKGROUND_GREEN,
        arena=levels.ARENA_TOM,
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
        position=(900, 268),
        boss_mode_background=resources.BACKGROUND_RED,
        arena=levels.ARENA_PAYA,
        hard={},
    ),
    BossId.BALERINO: BossConfig(
        name="Balerino",
        intro_title="** BALERINO **",
        victory_title="Balerino !!",
        texture=resources.BOSS_PLACEHOLDER_TEXTURE,
        damage_texture=resources.BOSS_PLACEHOLDER_TEXTURE,
        menu_texture=resources.BOSS_PLACEHOLDER_TEXTURE,
        size=(288, 414),
        position=(900, 268),
        boss_mode_background=resources.BACKGROUND_BLUE,
        arena=levels.ARENA_BALERINO,
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
