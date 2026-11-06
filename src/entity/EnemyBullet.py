from src.entity.Bullet import Bullet
from src.settings import resources


class EnemyBullet(Bullet):
    """Projectile ennemi : une poule lancée."""

    TEXTURE = resources.CHICKEN_TEXTURE
