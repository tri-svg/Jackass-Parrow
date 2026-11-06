import pygame
from pygame import Surface

from src.block.BlockGroup import BlockGroup
from src.entity.Bullet import LEFT, RIGHT, Bullet
from src.system import assets
from src.system.GameConfig import APPConfig
from src.system.Sound import Sound

GROUND_Y = APPConfig.HEIGHT  # bas de l'écran


class Player(pygame.sprite.Sprite):
    # /!\ physique "fait main" : valeurs et ordre des calculs volontairement inchangés
    BASE_SPEED = 400
    MAX_FALL_SPEED = 1000
    JUMP_FORCE = 1250
    KNOCKBACK_FORCE = 1500
    GRAVITY_STEP = 60  # ajouté à chaque frame tant que le joueur est en l'air
    BULLET_DELAY = 1000  # délai entre les tirs en millisecondes
    FIRING_ANIMATION_TIME = 200
    INVINCIBILITY_TIME = 600

    def __init__(self, x=200, y=200):
        super().__init__()
        self.shield = False
        self.evasive = False
        self.invinsibilyTime = 0
        self.sounds = Sound()

        # copies : ces surfaces sont modifiées en place (blit / set_alpha) par les animations
        self.walk1 = assets.image("player", "player.png")
        self.walk2 = assets.image("player", "playerWalk.png")
        self.shield_image = assets.image("player", "player_shield.png")
        self.player_image = assets.image_copy("player", "player.png")
        self.firing_image = assets.image_copy("player", "player_firing.png")
        self.dead_image = assets.image_copy("player", "player_dead.png")
        self.rect = self.player_image.get_rect(y=y, x=x)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        self.speed = 0
        self.direction = LEFT
        self.gravity = 0
        self.onGround = False
        self.knockback = 0
        self.health = 3
        self.score = 0

        self.current_time = 150
        self.last_bullet_time = 0

    # ------------------------------------------------------------------ input
    def handleMove(self, keys, bullets, delta_time: float):
        if self.health <= 0:
            return

        if not keys[pygame.K_s]:
            self.shield = False
        if keys[pygame.K_z] or keys[pygame.K_UP]:
            if self.onGround:
                self.gravity = -self.JUMP_FORCE
                # premier décollage pour placer le joueur en état de saut
                self.rect.y += self.gravity * delta_time
                self.onGround = False
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if not self.onGround:
                if self.gravity < self.MAX_FALL_SPEED:
                    self.gravity = self.MAX_FALL_SPEED
            else:
                self.shield = True
                self.speed = 0
                self.image.fill((0, 0, 0, 0))
                self.image.blit(self.shield_image, (0, 0))
        elif (keys[pygame.K_q] or keys[pygame.K_LEFT]) and not self.shield:
            self.speed = -self.BASE_SPEED
            self.direction = LEFT
        elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and not self.shield:
            self.speed = self.BASE_SPEED
            self.direction = RIGHT
        elif (not keys[pygame.K_q] and not keys[pygame.K_d]) or (keys[pygame.K_d] and keys[pygame.K_q]):
            self.speed = 0

        if keys[pygame.K_SPACE] and self.current_time - self.last_bullet_time > self.BULLET_DELAY:
            # le canon est à l'arrière : on tire dans le dos
            bullets.add(Bullet(self.rect.x, self.rect.y + 50, LEFT if self.direction == RIGHT else RIGHT))
            self.knockback = self.KNOCKBACK_FORCE if self.direction == RIGHT else -self.KNOCKBACK_FORCE
            self.last_bullet_time = self.current_time
            self.sounds.son_tir.play()
            return

        if keys[pygame.K_i] and keys[pygame.K_o] and keys[pygame.K_p]:
            self.debug_shot(bullets)

    def debug_shot(self, bullets: pygame.sprite.Group):
        if self.current_time - self.last_bullet_time > (self.BULLET_DELAY // 4):
            for i in range(10, 1200, 20):
                bullets.add(Bullet(10, i, RIGHT), Bullet(1250, i, LEFT))
        self.last_bullet_time = self.current_time

    # ------------------------------------------------------------------ état
    def addScore(self, score):
        self.score += score

    def touched(self, bullet=None):
        self.sounds.son_hurt.play()
        self.health -= 1
        self.invinsibilyTime = self.current_time
        self.evasive = True
        if bullet:
            bullet.kill()

    def _is_parried(self, bullet) -> bool:
        if not self.shield:
            return False
        if self.direction == LEFT:
            return bullet.rect.collidepoint(self.rect.midleft) or bullet.rect.collidepoint(self.rect.topleft)
        return bullet.rect.collidepoint(self.rect.midright) or bullet.rect.collidepoint(self.rect.topright)

    def check_bullets(self, enemy_bullets):
        # collisions avec les projectiles
        if not self.evasive:
            for bullet in enemy_bullets:
                if self.rect.colliderect(bullet.rect):
                    if self._is_parried(bullet):
                        self.sounds.son_parade.play()
                        bullet.kill()
                    else:
                        self.touched(bullet)
        else:
            # clignotement pendant l'invincibilité
            self.image.set_alpha(100 if self.current_time % 20 <= 10 else 0)

        if self.health <= 0:
            self.image = self.dead_image
            self.rect = self.image.get_rect(x=self.rect.x, y=self.rect.y)
            self.speed = 0

    def check_blocks(self, Blocs: BlockGroup):
        rect = self.rect
        for testBlock in Blocs.sprites():
            block_rect = testBlock.rect
            # atterrissage sur un bloc
            if (self.gravity >= 0 and block_rect.colliderect(rect)
                    and rect.bottom + self.gravity > block_rect.top > rect.centery):
                rect.bottom = block_rect.top + 1
                self.gravity = 0
                self.onGround = True
            # saut en dessous d'un bloc
            elif self.gravity < 0 and block_rect.colliderect(rect) and rect.top > block_rect.centery:
                self.gravity = 1

            # gauche / droite
            if (block_rect.collidepoint(rect.midleft) and rect.left < block_rect.right
                    and rect.bottom > block_rect.top + 2):
                if self.speed == -self.BASE_SPEED:
                    self.speed = 0
                if self.knockback < 0:
                    self.knockback = -self.knockback / 2
            elif (block_rect.collidepoint(rect.midright) and rect.right > block_rect.left
                    and rect.bottom > block_rect.top + 2):
                if self.speed == self.BASE_SPEED:
                    self.speed = 0
                if self.knockback > 0:
                    self.knockback = -self.knockback / 2

    # ------------------------------------------------------------------ rendu
    def render(self, scene: Surface):
        self.current_time = pygame.time.get_ticks()
        if self.direction == LEFT:
            scene.blit(self.image, self.rect)
        else:
            scene.blit(pygame.transform.flip(self.image, True, False), self.rect)

        # préparation de l'image de la frame suivante
        is_firing = self.current_time - self.last_bullet_time < self.FIRING_ANIMATION_TIME
        self.image = self.firing_image if is_firing else self.player_image

        if self.current_time - self.invinsibilyTime > self.INVINCIBILITY_TIME:
            self.evasive = False
            self.image.set_alpha(255)

            if self.speed in (self.BASE_SPEED, -self.BASE_SPEED) and self.onGround:
                walk_frame = self.walk1 if self.current_time % 300 >= 150 else self.walk2
                self.image.fill((0, 0, 0, 0))
                self.image.blit(walk_frame, (0, 0))
            elif is_firing:
                self.image = self.firing_image
            else:
                self.image.fill((0, 0, 0, 0))
                self.image.blit(self.walk1, (0, 0))

    # ------------------------------------------------------------------ physique
    def update(self, scene: Surface, Blocs: BlockGroup, enemy_bullets, delta_time: float):
        self.check_bullets(enemy_bullets)

        # amortissement du knockback
        self.knockback *= 0.85
        if abs(self.knockback) < 0.1:
            self.knockback = 0

        # saut et chute
        self.onGround = False
        if self.rect.bottom >= GROUND_Y and self.gravity > 0:
            self.gravity = 0
            self.onGround = True
        # évite de clip dans le sol en cas d'excès de vitesse
        elif self.rect.bottom + (self.gravity * delta_time) > GROUND_Y:
            self.rect.bottom = GROUND_Y

        self.check_blocks(Blocs)

        if not self.onGround:
            self.gravity += self.GRAVITY_STEP

        self.rect.y += int(self.gravity * delta_time)
        self.rect.x += int((self.speed + self.knockback) * delta_time)
