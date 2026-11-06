from src.entity.Boss import Boss
from src.settings.bosses import BossId


class Balerino(Boss):
    """Balerino : pour l'instant immobile, il encaisse les coups jusqu'à mourir."""

    BOSS_ID = BossId.BALERINO

    def setup_hard_mode(self):
        # difficulté HARD (2e rencontre) : rien de spécial pour l'instant
        pass
