from random import randint, sample

import pygame

from src.entity.Enemy import Enemy, EnemyAngwy
from src.entity.EnemyKamikaze import EnemyKamikaze
from src.settings import enemies


class BlockGroup(pygame.sprite.Group):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene

    def get_spawnable(self) -> list:
        return [bloc for bloc in self.sprites() if bloc.spawnable]

    def spawn(self, danger_level: int, enemyGroup):
        """Fait apparaître `danger_level` ennemis (au plus un par bloc spawnable)."""
        spawnables = self.get_spawnable()
        angry = danger_level > enemies.ANGRY_DANGER_THRESHOLD
        nb_enemies = min(danger_level, len(spawnables))

        for bloc in sample(spawnables, nb_enemies):
            x = randint(bloc.rect.x, (bloc.rect.x + bloc.rect.width) - (enemies.KNIGHT_SIZE[0] // 2))

            if randint(0, enemies.KAMIKAZE_CHANCE - 1) == 0:
                new_enemy = EnemyKamikaze(x, bloc.rect.y - enemies.KAMIKAZE_SPAWN_OFFSET_Y, bloc)
            elif angry:
                new_enemy = EnemyAngwy(x, bloc.rect.y - enemies.KNIGHT_SPAWN_OFFSET_Y)
            else:
                new_enemy = Enemy(x, bloc.rect.y - enemies.KNIGHT_SPAWN_OFFSET_Y)
            enemyGroup.add(new_enemy)

    def render(self):
        self.draw(self.scene)
