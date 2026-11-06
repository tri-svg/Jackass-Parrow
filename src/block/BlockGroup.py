from random import randint, sample

import pygame

from src.entity.Enemy import Enemy, EnemyAngwy
from src.entity.EnemyKamikaze import EnemyKamikaze

ANGRY_DANGER_THRESHOLD = 5  # au-delà, les chevaliers normaux sont remplacés par des chevaliers énervés


class BlockGroup(pygame.sprite.Group):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene

    def get_spawnable(self) -> list:
        return [bloc for bloc in self.sprites() if bloc.spawnable]

    def spawn(self, danger_level: int, enemyGroup):
        """Fait apparaître `danger_level` ennemis (au plus un par bloc spawnable)."""
        spawnables = self.get_spawnable()
        angry = danger_level > ANGRY_DANGER_THRESHOLD
        nb_enemies = min(danger_level, len(spawnables))

        for bloc in sample(spawnables, nb_enemies):
            x = randint(bloc.rect.x, (bloc.rect.x + bloc.rect.width) - (Enemy.SIZE[0] // 2))
            y = bloc.rect.y - 90

            if randint(0, 3) == 0:
                new_enemy = EnemyKamikaze(x, bloc.rect.y - 70, bloc)
            elif angry:
                new_enemy = EnemyAngwy(x, y)
            else:
                new_enemy = Enemy(x, y)
            enemyGroup.add(new_enemy)

    def render(self):
        self.draw(self.scene)
