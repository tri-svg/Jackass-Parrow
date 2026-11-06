from typing import TYPE_CHECKING

import pygame
from pygame.key import ScancodeWrapper
from pygame.surface import Surface

from src.block.BlockGroup import BlockGroup
from src.entity.Boss import Boss
from src.entity.EnemyGroup import EnemyGroup
from src.entity.Player import Player
from src.system import assets
from src.system.GameConfig import APPConfig, DIFFICULTY, WorldType
from src.system.LevelCollection import LevelCollection
from src.system.WorldManager import WorldManager

if TYPE_CHECKING:
    from src.app import App

GAME_DIFFICULTY = DIFFICULTY.OLD


class GameManager:
    """
    Classe principale gérant le déroulement du jeu.

    Cette classe centralise le cycle de vie des parties :
    chargement des niveaux, gestion du joueur, des ennemis,
    des boss, et affichage des éléments graphiques.

    Attributes:
        level_collection (LevelCollection): Gestionnaire des niveaux.
        game_surface (Surface): Surface Pygame où le jeu est rendu.
        backgrounds (dict[WorldType, Surface]): Image de fond de chaque monde.
        world_manager (WorldManager): Gestionnaire des mondes
        game_over (bool): Indique si la partie est terminée.
        game_over_time (int): Temps écoulé depuis la fin de partie.
        fight_boss (bool): Indique si un combat de boss est en cours.
        boss_mode (bool): Indique si le jeu est en mode Boss.
        score_saved (bool): Indique si le score a été sauvegardé.
        player (Player): Le joueur contrôlé.
        bullets (pygame.sprite.Group): Projectiles du joueur.
        enemy_group (EnemyGroup): Groupe d'ennemis.
        enemy_bullets (pygame.sprite.Group): Projectiles ennemis.
        blocks (BlockGroup): Groupe de blocs responsable de l'apparition des ennemis.
        boss (Boss): Instance de boss actuel.
    """

    def __init__(self, game_surface: Surface):
        """
        Args:
            game_surface (Surface): Surface sur laquelle le jeu est affiché.
        """
        # système
        self.level_collection: LevelCollection = None
        self.game_surface = game_surface
        normal_background = assets.image("background", "fondGameJam.png")
        self.backgrounds = {
            WorldType.MONDE_FORET: normal_background,
            WorldType.MONDE_JUNGLE: normal_background,
            WorldType.MONDE_VOLCAN: assets.image("background", "fondGameJamRed.png"),
        }
        self.world_manager: WorldManager = None

        # état de la partie
        self.game_over: bool = False
        self.game_over_time: int = 0
        self.fight_boss: bool = False
        self.boss_mode: bool = False
        self.score_saved: bool = False

        # entités
        self.player: Player = None
        self.boss: Boss = None

        # groupes
        self.bullets: pygame.sprite.Group = None
        self.enemy_group: EnemyGroup = None
        self.enemy_bullets: pygame.sprite.Group = None
        self.blocks: BlockGroup = None

    # ------------------------------------------------------------------ chargement
    def _new_game(self):
        """Réinitialise les entités et le gestionnaire de mondes."""
        self.bullets = pygame.sprite.Group()
        self.enemy_group = EnemyGroup(self.game_surface)
        self.enemy_bullets = pygame.sprite.Group()
        self.player = Player()
        self.blocks = BlockGroup(self.game_surface)
        self.level_collection = LevelCollection(self.blocks)
        self.world_manager = WorldManager(GAME_DIFFICULTY, self.level_collection)

    def load_tableau(self):
        """Charge un niveau normal (non boss) et fait apparaître les ennemis."""
        self.level_collection.load(self.world_manager.get_next_level_id())
        self.enemy_bullets.empty()
        self.player.rect.x, self.player.rect.y = self.level_collection.playerSpawn
        self.blocks.spawn(self.world_manager.get_danger_level(), self.enemy_group)

    def load_tableau_boss(self):
        """Charge un niveau de boss (uniquement Tom pour l'instant)."""
        self.enemy_bullets.empty()
        self.level_collection.load_boss(self.world_manager.get_current_world_type())
        self.player.rect.x, self.player.rect.y = self.level_collection.playerSpawn

    def start_game(self):
        """Initialise une nouvelle partie en mode normal."""
        self.boss_mode = False
        self.fight_boss = False
        self.game_over = False
        self.game_over_time = 0

        if self.boss is not None:
            self.boss.kill()
            self.boss = None

        self._new_game()
        self.load_tableau()

    def start_boss_mode(self):
        """Initialise une partie en mode boss."""
        self.boss_mode = True
        self.fight_boss = True
        self._new_game()
        self.boss = Boss(self.game_surface, self.enemy_bullets)
        self.load_tableau_boss()

    def _start_boss_fight(self):
        self.load_tableau_boss()
        self.player.speed = 0
        self.player.knockback = 0
        self.boss = Boss(self.game_surface, self.enemy_bullets)
        self.fight_boss = True

    def _end_boss_fight(self, app: "App"):
        """Tom est vaincu : on passe au monde suivant (tableaux HARD)."""
        self.fight_boss = False
        self.blocks.empty()
        self.world_manager.next_world()
        self.load_tableau()
        self.boss = None
        app.menu_context.clear_active_modal()

    # ------------------------------------------------------------------ rendu
    def render_game_background(self):
        world_type = self.world_manager.get_current_world_type()
        if world_type not in self.backgrounds:
            raise NotImplementedError(f"Le monde {WorldType(world_type).name} n'a pas de fond de jeu défini.")
        self.game_surface.blit(self.backgrounds[world_type], (0, 0))

    def render_game(self, app: "App", delta_time: float):
        """Dessine l'ensemble des éléments du jeu sur l'écran."""
        self.render_game_background()

        self.player.render(self.game_surface)
        self.blocks.draw(self.game_surface)
        self.bullets.draw(self.game_surface)
        self.enemy_group.draw(self.game_surface)
        self.enemy_bullets.draw(self.game_surface)
        if self.fight_boss:
            self.boss.render()

        if self.game_over:
            app.menu.show_end_screen(app)

    # ------------------------------------------------------------------ logique
    def on_loop(self, delta_time: float, keys: ScancodeWrapper, app: "App"):
        """
        Met à jour la logique du jeu pour un cycle.

        Args:
            delta_time (float): Temps écoulé depuis la dernière frame.
            keys (ScancodeWrapper): État des touches clavier.
            app (App): Instance principale de l'application.
        """
        # arrêt du jeu pendant l'affichage d'un menu modal
        if app.menu_context.get_active_modal() is None:
            self.player.update(self.game_surface, self.blocks, self.enemy_bullets, delta_time)
            if self.fight_boss:
                self.boss.update(self.bullets, self.player, app.menu_context)

            self.player.handleMove(keys, self.bullets, delta_time)
            self.enemy_group.update(self.player, self.enemy_bullets, self.bullets)
            self.enemy_bullets.update(APPConfig.WIDTH, self.blocks, delta_time)

            # pendant le combat contre Tom, ses boucliers arrêtent aussi les tirs du joueur
            if self.fight_boss and self.world_manager.get_current_world_type() == WorldType.MONDE_JUNGLE:
                self.bullets.update(APPConfig.WIDTH, self.blocks.sprites() + self.boss.bouclier.sprites(), delta_time)
            else:
                self.bullets.update(APPConfig.WIDTH, self.blocks, delta_time)

        # joueur mort
        if self.player.health <= 0 and not self.game_over:
            self.game_over = True
            self.game_over_time = pygame.time.get_ticks()

        # boss mort (après l'outro)
        if self.fight_boss and self.boss.health <= 0 and self.boss.outroFinished:
            if self.boss_mode:
                app.restart()
                self.boss.outroFinished = False
            else:
                self._end_boss_fight(app)

        # tous les ennemis sont morts : tableau suivant (ou boss en fin de monde)
        if self.enemy_group.nbAlive() == 0 and self.boss is None and not self.boss_mode:
            self.enemy_group.empty()
            self.blocks.empty()
            world = self.world_manager
            if world.is_endless() or world.get_current_level() < world.get_world_max_level():
                self.load_tableau()
            elif world.get_current_level() == world.get_world_max_level():
                self._start_boss_fight()
            else:
                raise ValueError("le niveau actuel ne peut pas être supérieur au niveau max du monde")
