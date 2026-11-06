import pygame


class EnemyGroup(pygame.sprite.Group):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene

    def nbAlive(self) -> int:
        return sum(1 for enemy in self.sprites() if enemy.is_alive)
