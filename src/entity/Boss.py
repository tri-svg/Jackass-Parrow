import time

import pygame

from src.entity.Player import Player
from src.gui.MenuContext import MenuContext
from src.settings import resources
from src.settings.bosses import BOSSES, BossConfig, BossDifficulty, BossId
from src.system import assets


class Boss(pygame.sprite.Sprite):
    """
    Classe de base des boss.

    Comportement commun : affichage, PV, invulnérabilité + clignotement après un coup,
    mort puis outro. Les classes filles redéfinissent les "hooks" :
        attack(player, now)  -> attaques à chaque frame
        on_hit()             -> réaction quand le boss est touché
        get_obstacles()      -> blocs propres au boss qui arrêtent les tirs du joueur
        render_extra()       -> éléments affichés en plus du boss
        setup_hard_mode()    -> réglages spécifiques à la difficulté HARD
    Les réglages viennent de settings/bosses.py (BOSSES[BOSS_ID]) ; en HARD, les valeurs
    du dictionnaire `hard` de la config remplacent les valeurs normales.
    """

    BOSS_ID: BossId = None

    def __init__(self, game_surface, enemy_bullets, difficulty: BossDifficulty = BossDifficulty.NORMAL,
                 background: tuple = None):
        super().__init__()
        self.difficulty = difficulty
        self.config: BossConfig = BOSSES[self.BOSS_ID].for_difficulty(difficulty)
        # fond de l'arène : celui de la série précédente, ou celui du Mode Boss
        self.background = background or self.config.boss_mode_background
        self.start_timer = time.time()
        self.game_surface = game_surface

        self.TEXTURE = pygame.transform.scale(assets.image(*self.config.texture), self.config.size)
        self.TEXTURE_DAMAGE = pygame.transform.scale(assets.image(*self.config.damage_texture), self.config.size)
        self.image = self.TEXTURE.copy()  # surface de travail, redessinée à chaque frame
        self.rect = self.image.get_rect(topleft=self.config.position)

        self.health = self.config.health
        self.lastEvasiveTime = 0
        self.deathTime = 0
        self.outroFinished = False
        self.bullets = enemy_bullets

        assets.play_music(self.config.music)

    # ------------------------------------------------------------------ hooks
    def attack(self, player: Player, now: float):
        """Attaques du boss (aucune par défaut)."""

    def on_hit(self):
        """Appelé à chaque coup encaissé, après la perte du PV."""

    def get_obstacles(self) -> list:
        """Blocs propres au boss qui arrêtent les tirs du joueur."""
        return []

    def render_extra(self):
        """Éléments à dessiner en plus du boss."""

    def setup_hard_mode(self):
        """
        Ajustements propres au boss en difficulté HARD (rien par défaut).
        Appelé par create_boss() une fois le boss entièrement construit.
        """

    # ------------------------------------------------------------------ commun
    @property
    def name(self) -> str:
        return self.config.name

    @property
    def is_hard(self) -> bool:
        return self.difficulty == BossDifficulty.HARD

    def is_evasive(self) -> bool:
        return time.time() - self.lastEvasiveTime <= self.config.evasive_duration

    def _set_texture(self, texture: pygame.Surface):
        self.image.fill((0, 0, 0, 0))
        self.image.blit(texture, (0, 0))

    def render(self):
        self.game_surface.blit(self.image, self.rect)
        # préparation de l'image de la frame suivante
        if not self.is_evasive():
            self._set_texture(self.TEXTURE)
            self.image.set_alpha(255)
        else:
            self._set_texture(self.TEXTURE_DAMAGE)
            period = self.config.blink_period_ms
            bright, dim = self.config.blink_alphas
            self.image.set_alpha(bright if int(time.time() * 1000) % period <= period // 2 else dim)
        self.render_extra()

    def update(self, player_bullets, player: Player, menu_context: MenuContext):
        # appelée uniquement si aucun menu modal n'est actif
        now = time.time()

        if self.health <= 0:
            self._update_dead(now, menu_context)
            return

        self.attack(player, now)

        # collision avec les tirs du joueur (si pas en mode évasif)
        if not self.is_evasive():
            for bullet in player_bullets:
                if self.rect.colliderect(bullet.rect):
                    self.health -= 1
                    self.lastEvasiveTime = time.time()
                    bullet.kill()
                    self.on_hit()

    def _update_dead(self, now: float, menu_context: MenuContext):
        if self.deathTime == 0:
            self.bullets.empty()
            self.deathTime = now
        menu_context.set_active_modal(MenuContext.OUTRO_BOSS_MODAL)
        self._set_texture(self.TEXTURE_DAMAGE)

        # fin de l'outro (la musique n'est relancée qu'une fois)
        if not self.outroFinished and now - self.deathTime > self.config.outro_duration:
            self.outroFinished = True
            assets.play_music(resources.MUSIC_MAIN)
