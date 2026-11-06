from random import randint

import pygame

from src.entity.Bullet import LEFT, RIGHT
from src.entity.EnemyBullet import EnemyBullet
from src.settings import enemies, resources
from src.system import assets
from src.system.Sound import Sound


class Enemy(pygame.sprite.Sprite):
    SIZE = enemies.KNIGHT_SIZE
    TEXTURE = resources.KNIGHT_TEXTURE
    DEAD_TEXTURE = resources.KNIGHT_DEAD_TEXTURE

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
        self.score = enemies.KNIGHT_SCORE

    def update(self, player, bullet_group, player_bullets):
        if not self.is_alive:
            # le chevalier mort s'envole et ne bloque plus les tirs
            self.rect.y -= enemies.KNIGHT_DEAD_RISE_SPEED
            return

        min_delay, max_delay = (int(delay * self.angryCoef) for delay in enemies.KNIGHT_SHOT_DELAY)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > randint(min_delay, max_delay) and player.health > 0:
            self.shoot(bullet_group, player)
            self.last_shot_time = current_time

        for bullet in player_bullets:
            if self.rect.colliderect(bullet.rect):
                self.killed()
                bullet.kill()
                player.addScore(self.score)
                break

        if not self.is_alive:
            self.rect.y -= enemies.KNIGHT_DEAD_RISE_SPEED

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
        self.image = assets.image_with_alpha(enemies.KNIGHT_DEAD_ALPHA, *self.DEAD_TEXTURE)


class EnemyAngwy(Enemy):
    TEXTURE = resources.KNIGHT_ANGRY_TEXTURE

    def __init__(self, x, y):
        super().__init__(x, y)
        self.score = enemies.ANGRY_KNIGHT_SCORE
        self.angryCoef = enemies.ANGRY_KNIGHT_SHOT_COEF
