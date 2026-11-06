import pygame

from src.entity.Enemy import Enemy
from src.system import assets

WALK_TEXTURES = (("entity", "chicken_bomb.png"), ("entity", "chicken_bomb_walk.png"))
EXPLOSION_TEXTURES = tuple(("entity", f"explosion_{i}.png") for i in range(1, 5))


class EnemyKamikaze(Enemy):
    """Poule-bombe qui fait des allers-retours sur sa plateforme et explose au contact."""

    TEXTURE = WALK_TEXTURES[0]

    def __init__(self, x, y, platform):
        super().__init__(x, y)
        self.walk_frames = [assets.image(*texture) for texture in WALK_TEXTURES]
        self.walk_frames_flipped = [assets.image_flipped(*texture) for texture in WALK_TEXTURES]
        self.walk_index = 0
        self.image = self.walk_frames[self.walk_index]
        self.rect = self.image.get_rect(x=x, y=y)
        self.platform = platform
        self.speed = 5
        self.direction = 1
        self.animation_timer = 0
        self.animation_delay = 100

        # explosion
        self.explosion_frames = [assets.image(*texture) for texture in EXPLOSION_TEXTURES]
        self.explosion_index = 0
        self.explosion_timer = 0
        self.explosion_delay = 50
        self.is_exploding = False

    def update(self, player, bullet_group, player_bullets):
        current_time = pygame.time.get_ticks()

        if self.is_alive:
            self.rect.x += self.speed * self.direction

            if self.rect.right > self.platform.rect.right - 15:
                self.direction = -1
            elif self.rect.left < self.platform.rect.left + 15:
                self.direction = 1
            if self.rect.colliderect(player.rect):
                self.touch(player)

            if current_time - self.animation_timer > self.animation_delay:
                self.animation_timer = current_time
                self.walk_index = (self.walk_index + 1) % len(self.walk_frames)
                frames = self.walk_frames_flipped if self.direction == 1 else self.walk_frames
                self.image = frames[self.walk_index]

            for bullet in player_bullets:
                if self.rect.colliderect(bullet.rect):
                    self.killed()
                    bullet.kill()
                    player.addScore(self.score)

        if self.is_exploding and current_time - self.explosion_timer > self.explosion_delay:
            self.explosion_timer = current_time
            self.explosion_index += 1
            if self.explosion_index < len(self.explosion_frames):
                self.image = self.explosion_frames[self.explosion_index]
            else:
                self.is_exploding = False
                self.kill()

    def shoot(self, bullet_group, player):
        pass

    def killed(self):
        self.is_alive = False
        self.is_exploding = True
        self.explosion_index = 0
        self.explosion_timer = pygame.time.get_ticks()
        self.image = self.explosion_frames[self.explosion_index]

    def touch(self, player):
        player.touched()
        self.killed()
