from src.entity.Boss import Boss
from src.settings.bosses import BossId


class Paya(Boss):
    """Paya : pour l'instant immobile, il encaisse les coups jusqu'à mourir."""

    BOSS_ID = BossId.PAYA

    def setup_hard_mode(self):
        # difficulté HARD (2e rencontre) : rien de spécial pour l'instant
        pass
