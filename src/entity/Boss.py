import random
import time

import pygame

from src.block.Block import Block
from src.block.BlockGroup import BlockGroup
from src.entity.Bullet import LEFT
from src.entity.EnemyBullet import EnemyBullet
from src.entity.Player import Player
from src.gui.MenuContext import MenuContext
from src.system import assets


class Boss(pygame.sprite.Sprite):
    """Tom de l'Abbaye."""

    X = 900
    Y = 110
    SIZE = (144, 286)
    BOUCLIER_COLUMN = 15
    BOUCLIER_WIDTH = 1
    BOUCLIER_HEIGHT = 3
    EVASIVE_DURATION = 2  # secondes d'invulnérabilité après un coup
    OUTRO_DURATION = 5  # secondes entre la mort et la fin de l'outro
    ATTACK_SPEED = 1000  # ms entre deux tirs
    ANGRY_ATTACK_SPEED = 700
    ANGRY_HEALTH = 3

    def __init__(self, game_surface, enemy_bullets):
        super().__init__()

        self.start_timer = time.time()
        self.game_surface = game_surface

        size = (self.SIZE[0] * 2, self.SIZE[1] * 2)
        self.TEXTURE_TOM = pygame.transform.scale(assets.image("entity", "tom.png"), size)
        self.TEXTURE_TOM_DAMAGE = pygame.transform.scale(assets.image("entity", "tomDamage.png"), size)
        self.image = self.TEXTURE_TOM.copy()  # surface de travail, redessinée à chaque frame
        self.rect = self.image.get_rect(x=self.X, y=self.Y)

        self.health = 10

        self.lastEvasiveTime = 0
        self.deathTime = 0
        self.outroFinished = False

        self.index_hole = 0
        self.attackSpeed = self.ATTACK_SPEED
        self.bullets = enemy_bullets
        self.timeLastBullet = 0

        self.bouclier = BlockGroup(self.game_surface)
        assets.play_music(assets.BOSS_THEME_PATH)

    def is_evasive(self) -> bool:
        return time.time() - self.lastEvasiveTime <= self.EVASIVE_DURATION

    def generateBouclier(self):
        self.bouclier.empty()
        choice = [0, 1, 2]
        # évite de laisser 2 fois le même trou de bouclier d'affilée
        choice.remove(self.index_hole)
        self.index_hole = random.choice(choice)

        for bouclier_index in choice:
            self.bouclier.add(Block(self.BOUCLIER_COLUMN, 12 - (bouclier_index * 4),
                                    self.BOUCLIER_WIDTH, self.BOUCLIER_HEIGHT))

    def _set_texture(self, texture: pygame.Surface):
        self.image.fill((0, 0, 0, 0))
        self.image.blit(texture, (0, 0))

    def render(self):
        self.game_surface.blit(self.image, self.rect)
        # préparation de l'image de la frame suivante
        if not self.is_evasive():
            self._set_texture(self.TEXTURE_TOM)
            self.image.set_alpha(255)
        else:
            self._set_texture(self.TEXTURE_TOM_DAMAGE)
            self.image.set_alpha(200 if int(time.time() * 1000) % 200 <= 100 else 150)
        self.bouclier.render()

    def update(self, player_bullets, player: Player, menu_context: MenuContext):
        # la fonction update est appelée uniquement si aucun menu modal n'est actif
        now = time.time()

        if self.health <= 0:
            if self.deathTime == 0:
                self.bullets.empty()
                self.deathTime = now
            menu_context.set_active_modal(MenuContext.OUTRO_BOSS_MODAL)
            self._set_texture(self.TEXTURE_TOM_DAMAGE)

            # fin de l'outro (la musique n'est relancée qu'une fois)
            if not self.outroFinished and now - self.deathTime > self.OUTRO_DURATION:
                self.outroFinished = True
                assets.play_music(assets.MAIN_THEME_PATH)
            return

        # tirs
        if now - self.timeLastBullet > self.attackSpeed / 1000.0:
            self.timeLastBullet = now
            self.bullets.add(EnemyBullet(self.rect.midleft[0] - 100, player.rect.y, LEFT))

        # collision avec les tirs du joueur (si pas en mode évasif)
        if not self.is_evasive():
            for bullet in player_bullets:
                if self.rect.colliderect(bullet.rect):
                    self.generateBouclier()
                    self.health -= 1
                    self.lastEvasiveTime = time.time()
                    bullet.kill()
                    if self.health <= self.ANGRY_HEALTH:  # colère
                        self.attackSpeed = self.ANGRY_ATTACK_SPEED
