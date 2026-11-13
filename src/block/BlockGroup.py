from random import choices, randint, sample

import pygame

from src.entity.Enemy import Enemy, EnemyAngwy
from src.entity.EnemyKamikaze import EnemyKamikaze
from src.settings import enemies
from src.settings.enemies import EnemyType


class BlockGroup(pygame.sprite.Group):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene

    def get_spawnable(self) -> list:
        return [bloc for bloc in self.sprites() if bloc.spawnable]

    def spawn(self, enemy_count: int, enemyGroup, enemy_weights: dict, level: int, angry_above_level=None):
        """
        Fait apparaître `enemy_count` ennemis (au plus un par bloc spawnable).
        enemy_weights : EnemyType -> chances relatives (cf. "enemies" des séries, settings/progression.py) ;
        si `level` dépasse `angry_above_level` (None : jamais), un chevalier tiré devient énervé.
        """
        spawnables = self.get_spawnable()
        nb_enemies = min(enemy_count, len(spawnables))
        types = [enemy_type for enemy_type, weight in enemy_weights.items() if weight > 0]
        if not types:
            return
        weights = [enemy_weights[enemy_type] for enemy_type in types]
        angry = angry_above_level is not None and level > angry_above_level

        for bloc in sample(spawnables, nb_enemies):
            x = randint(bloc.rect.x, (bloc.rect.x + bloc.rect.width) - (enemies.KNIGHT_SIZE[0] // 2))
            enemy_type = choices(types, weights)[0]
            if enemy_type == EnemyType.KNIGHT and angry:
                enemy_type = EnemyType.ANGRY_KNIGHT

            if enemy_type == EnemyType.KAMIKAZE:
                new_enemy = EnemyKamikaze(x, bloc.rect.y - enemies.KAMIKAZE_SPAWN_OFFSET_Y, bloc)
            elif enemy_type == EnemyType.ANGRY_KNIGHT:
                new_enemy = EnemyAngwy(x, bloc.rect.y - enemies.KNIGHT_SPAWN_OFFSET_Y)
            else:
                new_enemy = Enemy(x, bloc.rect.y - enemies.KNIGHT_SPAWN_OFFSET_Y)
            enemyGroup.add(new_enemy)

    def render(self):
        self.draw(self.scene)
