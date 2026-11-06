from src.settings import resources
from src.system import assets


class Sound:
    """
    Accès aux effets sonores.

    Les sons sont chargés une seule fois (cache dans `assets`) : instancier
    `Sound()` ne coûte rien.
    """

    def __init__(self):
        self.son_tir = assets.sound(resources.SOUND_SHOT)
        self.son_button = assets.sound(resources.SOUND_BUTTON)
        self.son_hurt = assets.sound(resources.SOUND_HURT)
        self.son_knight_hurt = assets.sound(resources.SOUND_KNIGHT_HURT)
        self.son_enemy_fire = assets.sound(resources.SOUND_ENEMY_FIRE)
        self.son_parade = assets.sound(resources.SOUND_PARRY)
