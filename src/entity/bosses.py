from src.entity.Balerino import Balerino
from src.entity.Boss import Boss
from src.entity.Paya import Paya
from src.entity.Tom import Tom
from src.settings.bosses import BossDifficulty, BossId

BOSS_CLASSES: dict[BossId, type[Boss]] = {
    BossId.TOM: Tom,
    BossId.PAYA: Paya,
    BossId.BALERINO: Balerino,
}


def create_boss(boss_id: BossId, game_surface, enemy_bullets,
                difficulty: BossDifficulty = BossDifficulty.NORMAL, background: tuple = None) -> Boss:
    """
    Crée un boss (toujours passer par ici pour que la difficulté soit appliquée).
    background : fond de l'arène (None = fond du Mode Boss défini dans settings/bosses.py).
    """
    boss = BOSS_CLASSES[boss_id](game_surface, enemy_bullets, difficulty, background)
    if boss.is_hard:
        boss.setup_hard_mode()
    return boss
