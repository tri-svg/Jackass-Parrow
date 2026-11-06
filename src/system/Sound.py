from src.system import assets


class Sound:
    """
    Accès aux effets sonores.

    Les sons sont chargés une seule fois (cache dans `assets`) : instancier
    `Sound()` est donc gratuit, contrairement à avant où chaque ennemi
    rechargeait les 6 fichiers .wav.
    """

    def __init__(self):
        self.son_tir = assets.sound("tir.wav")
        self.son_button = assets.sound("button.wav")
        self.son_hurt = assets.sound("hurt.wav")
        self.son_knight_hurt = assets.sound("knight_hurt.wav")
        self.son_enemy_fire = assets.sound("enemyFire.wav")
        self.son_parade = assets.sound("parade.wav")
