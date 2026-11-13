from typing import TYPE_CHECKING

import pygame
from pygame.key import ScancodeWrapper
from pygame.surface import Surface

from src.block.BlockGroup import BlockGroup
from src.entity.Boss import Boss
from src.entity.bosses import create_boss
from src.entity.Cuistot import Cuistot, Oven
from src.entity.EnemyGroup import EnemyGroup
from src.entity.Player import Player
from src.gui.DialogueBox import DialogueBox
from src.settings import display, levels, texts
from src.settings import special_level
from src.settings import player as player_cfg
from src.settings import progression as progression_cfg
from src.settings.bosses import BossDifficulty, BossId
from src.system import assets
from src.system.LevelCollection import LevelCollection, level_difficulty
from src.system.Progression import Progression

if TYPE_CHECKING:
    from src.app import App


class GameManager:
    """
    Classe principale gérant le déroulement du jeu.

    Cette classe centralise le cycle de vie des parties :
    chargement des tableaux, gestion du joueur, des ennemis,
    des boss, et affichage des éléments graphiques.

    Attributes:
        level_collection (LevelCollection): Construit les tableaux.
        game_surface (Surface): Surface Pygame où le jeu est rendu.
        progression (Progression): Avancement de la partie (tableaux / boss).
        game_over (bool): Indique si la partie est terminée.
        game_over_time (int): Moment de la fin de partie (ms).
        fight_boss (bool): Indique si un combat de boss est en cours.
        boss_mode (bool): Indique si le jeu est en mode Boss (un seul combat choisi dans le menu).
        score_saved (bool): Indique si le score a été sauvegardé.
        player (Player): Le joueur contrôlé.
        bullets (pygame.sprite.Group): Projectiles du joueur.
        enemy_group (EnemyGroup): Groupe d'ennemis.
        enemy_bullets (pygame.sprite.Group): Projectiles ennemis.
        blocks (BlockGroup): Blocs du tableau, responsables de l'apparition des ennemis.
        boss (Boss): Boss actuel.
    """

    def __init__(self, game_surface: Surface):
        # système
        self.level_collection: LevelCollection = None
        self.game_surface = game_surface
        self.progression: Progression = None

        # état de la partie
        self.game_over: bool = False
        self.game_over_time: int = 0
        self.fight_boss: bool = False
        self.boss_mode: bool = False
        self.score_saved: bool = False
        self.special_level: bool = False  # tableau spécial en cours (cf. settings/special_level.py)
        self.debug_level: bool = False  # tableau lancé depuis Options > Debug
        self.debug_background: tuple = None

        # entités
        self.player: Player = None
        self.boss: Boss = None
        self.cuistot: Cuistot = None
        self.dialogue: DialogueBox = None  # boîte de dialogue affichée (le jeu est figé pendant ce temps)
        self.cuistot_healed: bool = False

        # groupes
        self.bullets: pygame.sprite.Group = None
        self.enemy_group: EnemyGroup = None
        self.enemy_bullets: pygame.sprite.Group = None
        self.blocks: BlockGroup = None
        self.special_sprites: pygame.sprite.Group = None  # cuistot et four du tableau spécial

    # ------------------------------------------------------------------ chargement
    def _new_game(self):
        """Réinitialise les entités et la progression."""
        self.bullets = pygame.sprite.Group()
        self.enemy_group = EnemyGroup(self.game_surface)
        self.enemy_bullets = pygame.sprite.Group()
        self.player = Player()
        self.blocks = BlockGroup(self.game_surface)
        self.level_collection = LevelCollection(self.blocks)
        self.progression = Progression()
        self.special_level = False
        self.cuistot = None
        self.dialogue = None
        self.special_sprites = pygame.sprite.Group()

    def load_tableau(self):
        """Charge le tableau suivant de la série et fait apparaître les ennemis."""
        self.progression.enter_level()
        self.level_collection.load(self.progression.next_level_id(), self.progression.background())
        self.enemy_bullets.empty()
        self.player.rect.x, self.player.rect.y = self.level_collection.playerSpawn
        self.blocks.spawn(self.progression.enemy_count(), self.enemy_group, self.progression.enemy_weights(),
                          self.progression.level, self.progression.angry_above_level())

    def load_tableau_boss(self, boss_id: BossId, difficulty: BossDifficulty = BossDifficulty.NORMAL,
                          background: tuple = None):
        """Charge l'arène d'un boss et l'y fait apparaître."""
        self.progression.enter_level()
        self.enemy_bullets.empty()
        self.boss = create_boss(boss_id, self.game_surface, self.enemy_bullets, difficulty, background)
        self.level_collection.load_arena(self.boss.config.arena, self.boss.config.player_spawn, self.boss.background)
        self.player.rect.x, self.player.rect.y = self.level_collection.playerSpawn
        self.fight_boss = True

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

    def start_debug_level(self, level_id: int):
        """Options > Debug : un tableau précis, un ennemi sur chaque bloc spawnable ; fin au dernier ennemi tué."""
        self.boss_mode = False
        self.fight_boss = False
        self.game_over = False
        self._new_game()
        self.debug_level = True
        difficulty = level_difficulty(level_id)
        self.debug_background = levels.LEVEL_DIFFICULTY_BACKGROUNDS.get(difficulty, self.progression.background())
        self.progression.enter_level()
        self.level_collection.load(level_id, self.debug_background)
        self.player.rect.x, self.player.rect.y = self.level_collection.playerSpawn
        debug = progression_cfg.DEBUG_LEVEL
        self.blocks.spawn(len(self.blocks.get_spawnable()), self.enemy_group, debug["enemies"],
                          self.progression.level, debug["angry_above_level"])

    def start_boss_mode(self, boss_id: BossId):
        """Initialise une partie en mode boss contre le boss choisi."""
        self.boss_mode = True
        self._new_game()
        self.load_tableau_boss(boss_id)

    def _start_boss_fight(self):
        """Fin de série : combat contre le boss suivant du cycle."""
        self.progression.next_stage()
        self.player.speed = 0
        self.player.knockback = 0
        # fond = celui de la série qui vient de se terminer ; HARD à partir de la 2e rencontre
        self.load_tableau_boss(self.progression.current_boss(),
                               self.progression.current_boss_difficulty(),
                               self.progression.background())

    def _end_boss_fight(self, app: "App"):
        """Boss vaincu : série de tableaux suivante (précédée du tableau spécial si c'est le moment)."""
        self.fight_boss = False
        self.blocks.empty()
        special = self.progression.special_level_due()
        self.progression.next_stage()
        if special:
            self._load_special_level()
        else:
            self.load_tableau()
        self.boss = None
        app.menu_context.clear_active_modal()

    def _load_special_level(self):
        """Tableau spécial : pas d'ennemis, il suffit d'aller toucher Cuistot Bongo."""
        self.progression.enter_level()
        self.progression.special_level_done = True
        self.enemy_bullets.empty()
        self.level_collection.build_tableau(levels.SPECIAL_LEVEL, special_level.BACKGROUND or self.progression.background())
        self.player.rect.x, self.player.rect.y = self.level_collection.playerSpawn
        self.player.speed = 0
        self.player.knockback = 0
        self.cuistot = Cuistot()
        self.special_sprites.add(self.cuistot, Oven(self.cuistot))
        self.special_level = True
        self.cuistot_healed = False

    def _start_cuistot_dialogue(self):
        """Cuistot Bongo touché : le joueur s'arrête et le cuistot parle."""
        self.player.speed = 0
        self.player.knockback = 0
        self.dialogue = DialogueBox(texts.CUISTOT_NAME, texts.CUISTOT_DIALOGUE, special_level.CUISTOT_PORTRAIT)

    def _update_cuistot_dialogue(self, keys):
        self.dialogue.update(keys)
        if not self.cuistot_healed and self.dialogue.page >= special_level.CUISTOT_HEAL_PAGE:
            self.cuistot_healed = True
            self.player.health = min(self.player.health + special_level.CUISTOT_HEAL, player_cfg.MAX_HEALTH)
        if self.dialogue.finished:
            self.dialogue = None
            self._end_special_level()

    def _end_special_level(self):
        """Fin du dialogue avec Cuistot Bongo : on enchaîne sur la série de tableaux suivante."""
        self.special_level = False
        self.special_sprites.empty()
        self.cuistot = None
        self.blocks.empty()
        self.bullets.empty()
        self.load_tableau()

    # ------------------------------------------------------------------ rendu
    def render_game_background(self):
        if self.fight_boss and self.boss is not None:
            background = self.boss.background
        elif self.debug_level:
            background = self.debug_background
        elif self.special_level and special_level.BACKGROUND is not None:
            background = special_level.BACKGROUND
        else:
            background = self.progression.background()
        self.game_surface.blit(assets.image(*background), (0, 0))

    def render_game(self, app: "App", delta_time: float):
        """Dessine l'ensemble des éléments du jeu sur l'écran."""
        self.render_game_background()

        self.player.render(self.game_surface)
        self.blocks.draw(self.game_surface)
        self.special_sprites.draw(self.game_surface)
        self.bullets.draw(self.game_surface)
        self.enemy_group.draw(self.game_surface)
        self.enemy_bullets.draw(self.game_surface)
        if self.fight_boss:
            self.boss.render()

        if self.dialogue is not None:
            self.dialogue.render(self.game_surface)

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
        # dialogue : le jeu est figé, seule la boîte avance
        if self.dialogue is not None:
            if app.menu_context.get_active_modal() is None:
                self._update_cuistot_dialogue(keys)
            return

        # arrêt du jeu pendant l'affichage d'un menu modal
        if app.menu_context.get_active_modal() is None:
            self.player.update(self.game_surface, self.blocks, self.enemy_bullets, delta_time)
            if self.fight_boss:
                self.boss.update(self.bullets, self.player, app.menu_context)

            self.player.handleMove(keys, self.bullets, delta_time)
            self.enemy_group.update(self.player, self.enemy_bullets, self.bullets)
            self.enemy_bullets.update(display.WIDTH, self.blocks, delta_time)

            # pendant un combat de boss, ses éventuels blocs (boucliers de Tom) arrêtent aussi les tirs
            if self.fight_boss:
                self.bullets.update(display.WIDTH, self.blocks.sprites() + self.boss.get_obstacles(), delta_time)
            else:
                self.bullets.update(display.WIDTH, self.blocks, delta_time)

        # tableau de debug : tous les ennemis tués (ou joueur mort) -> retour à Options > Debug
        if self.debug_level:
            if self.enemy_group.nbAlive() == 0 or self.player.health <= 0:
                app.return_to_debug_menu()
            return

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

        # tableau spécial : il suffit d'aller voir Cuistot Bongo
        if self.special_level:
            if self.player.health > 0 and self.player.rect.colliderect(self.cuistot.rect):
                self._start_cuistot_dialogue()
            return

        # tous les ennemis sont morts : tableau suivant, ou boss en fin de série
        if self.enemy_group.nbAlive() == 0 and self.boss is None and not self.boss_mode:
            self.enemy_group.empty()
            self.blocks.empty()
            if self.progression.has_next_level():
                self.load_tableau()
            else:
                self._start_boss_fight()
