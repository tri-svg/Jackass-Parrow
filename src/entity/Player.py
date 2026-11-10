import pygame
from pygame import Surface

from src.block.BlockGroup import BlockGroup
from src.entity.Bullet import LEFT, RIGHT, Bullet
from src.settings import display, resources
from src.settings import player as cfg
from src.system import assets
from src.system.Sound import Sound

GROUND_Y = display.HEIGHT  # bas de l'écran


class Player(pygame.sprite.Sprite):
    # /!\ physique "fait main" : valeurs (settings/player.py) et ordre des calculs volontairement inchangés
    BASE_SPEED = cfg.BASE_SPEED
    MAX_FALL_SPEED = cfg.MAX_FALL_SPEED
    JUMP_FORCE = cfg.JUMP_FORCE
    KNOCKBACK_FORCE = cfg.KNOCKBACK_FORCE
    GRAVITY_STEP = cfg.GRAVITY_STEP
    BULLET_DELAY = cfg.BULLET_DELAY

    def __init__(self, x=cfg.SPAWN_X, y=cfg.SPAWN_Y):
        super().__init__()
        self.shield = False
        self.evasive = False
        self.invinsibilyTime = 0
        self.sounds = Sound()

        # copies : ces surfaces sont modifiées en place (blit / set_alpha) par les animations
        self.walk1 = assets.image(*resources.PLAYER_TEXTURE)
        self.walk2 = assets.image(*resources.PLAYER_WALK_TEXTURE)
        self.shield_image = assets.image(*resources.PLAYER_SHIELD_TEXTURE)
        self.player_image = assets.image_copy(*resources.PLAYER_TEXTURE)
        self.firing_image = assets.image_copy(*resources.PLAYER_FIRING_TEXTURE)
        self.dead_image = assets.image_copy(*resources.PLAYER_DEAD_TEXTURE)
        self.rect = self.player_image.get_rect(y=y, x=x)
        self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        self.speed = 0
        self.direction = LEFT
        self.gravity = 0
        self.onGround = False
        self.knockback = 0
        self.health = cfg.HEALTH
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
            bullets.add(Bullet(self.rect.x, self.rect.y + cfg.BULLET_OFFSET_Y, LEFT if self.direction == RIGHT else RIGHT))
            self.knockback = self.KNOCKBACK_FORCE if self.direction == RIGHT else -self.KNOCKBACK_FORCE
            self.last_bullet_time = self.current_time
            self.sounds.son_tir.play()
            return

        if keys[pygame.K_i] and keys[pygame.K_o] and keys[pygame.K_p]:
            self.debug_shot(bullets)

    def debug_shot(self, bullets: pygame.sprite.Group):
        if self.current_time - self.last_bullet_time > cfg.DEBUG_SHOT_DELAY:
            for y in range(*cfg.DEBUG_SHOT_Y_RANGE):
                bullets.add(Bullet(cfg.DEBUG_SHOT_LEFT_X, y, RIGHT), Bullet(cfg.DEBUG_SHOT_RIGHT_X, y, LEFT))
            self.last_bullet_time = self.current_time

    # ------------------------------------------------------------------ état
    def addScore(self, score):
        self.score += score

    def touched(self, bullet=None) -> bool:
        """
        Encaisse un coup. Renvoie False (sans effet) si le joueur est déjà invincible, y compris
        quand il a été touché plus tôt dans la même frame : une seule source de dégâts à la fois.
        """
        if self.evasive:
            return False
        self.sounds.son_hurt.play()
        self.health -= 1
        self.invinsibilyTime = self.current_time
        self.evasive = True
        if bullet:
            bullet.kill()
        return True

    def _is_parried(self, bullet) -> bool:
        """
        Le bouclier pare tout ce qui arrive du côté où il est tourné : la moitié avant du joueur sur toute
        sa hauteur, y compris le bas (ex. une poule qui frôle les pieds quand il dépasse du bord d'une plateforme).
        """
        if not self.shield:
            return False
        if self.direction == LEFT:
            return bullet.rect.centerx <= self.rect.centerx
        return bullet.rect.centerx >= self.rect.centerx

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
            visible, hidden = cfg.BLINK_ALPHAS
            self.image.set_alpha(visible if self.current_time % cfg.BLINK_PERIOD <= cfg.BLINK_PERIOD // 2 else hidden)

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
                    and rect.bottom > block_rect.top + cfg.BLOCK_SIDE_TOLERANCE):
                if self.speed == -self.BASE_SPEED:
                    self.speed = 0
                if self.knockback < 0:
                    self.knockback = -self.knockback / 2
            elif (block_rect.collidepoint(rect.midright) and rect.right > block_rect.left
                    and rect.bottom > block_rect.top + cfg.BLOCK_SIDE_TOLERANCE):
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

        if self.health <= 0:
            # mort : on garde le sprite du joueur mort, sans clignotement
            self.evasive = False
            self.image = self.dead_image
            self.image.set_alpha(255)
            return

        # préparation de l'image de la frame suivante
        is_firing = self.current_time - self.last_bullet_time < cfg.FIRING_ANIMATION_TIME
        self.image = self.firing_image if is_firing else self.player_image

        if self.current_time - self.invinsibilyTime > cfg.INVINCIBILITY_TIME:
            self.evasive = False
            self.image.set_alpha(255)

            if self.speed in (self.BASE_SPEED, -self.BASE_SPEED) and self.onGround:
                walk_frame = self.walk1 if self.current_time % cfg.WALK_ANIMATION_PERIOD >= cfg.WALK_ANIMATION_PERIOD // 2 else self.walk2
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
        self.knockback *= cfg.KNOCKBACK_DAMPING
        if abs(self.knockback) < cfg.KNOCKBACK_MIN:
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
