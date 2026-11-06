from random import randint

import pygame

from src.entity.Bullet import LEFT, RIGHT
from src.entity.EnemyBullet import EnemyBullet
from src.system import assets
from src.system.Sound import Sound

DEAD_ALPHA = 150


class Enemy(pygame.sprite.Sprite):
    SIZE = (75, 90)
    TEXTURE = ("entity", "chevalier.png")
    DEAD_TEXTURE = ("entity", "chevalierMort.png")

    def __init__(self, x, y):
        super().__init__()
        self.sounds = Sound()
        self.direction = LEFT
        self.image = assets.image(*self.TEXTURE)
        self.rect = self.image.get_rect(x=x, y=y)
        # NB : ne pas nommer cet attribut "alive", ça écrase la méthode Sprite.alive() de pygame
        self.is_alive = True
        self.last_shot_time = 0
        self.angryCoef = 1
        self.score = 100

    def update(self, player, bullet_group, player_bullets):
        min_delay, max_delay = int(1600 * self.angryCoef), int(2200 * self.angryCoef)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > randint(min_delay, max_delay) and self.is_alive and player.health > 0:
            self.shoot(bullet_group, player)
            self.last_shot_time = current_time

        for bullet in player_bullets:
            if self.rect.colliderect(bullet.rect):
                self.killed()
                bullet.kill()
                player.addScore(self.score)

        if not self.is_alive:
            self.rect.y -= 5

    def shoot(self, bullet_group, player):
        direction = LEFT if self.rect.centerx > player.rect.centerx else RIGHT
        if self.direction != direction:
            self.image = pygame.transform.flip(self.image, True, False)
        self.direction = direction

        self.sounds.son_enemy_fire.play()
        bullet_group.add(EnemyBullet(self.rect.centerx, self.rect.centery, direction))

    def killed(self):
        self.sounds.son_knight_hurt.play()
        self.is_alive = False
        self.image = assets.image_with_alpha(DEAD_ALPHA, *self.DEAD_TEXTURE)


class EnemyAngwy(Enemy):
    TEXTURE = ("entity", "chevalier_angwy.png")

    def __init__(self, x, y):
        super().__init__(x, y)
        self.score = 150
        self.angryCoef = 0.7
