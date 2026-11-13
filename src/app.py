import json
import time

import pygame
import pygame_gui

from src.gui.Menu import Menu, load_scores
from src.gui.MenuContext import MenuContext
from src.settings import display, menu, resources, texts
from src.settings import player as player_cfg
from src.settings.bosses import INTRO_DURATION
from src.system import Display, assets
from src.system.GameManager import GameManager
from src.system.Options import OPTIONS
from src.system.Sound import Sound


class App:
    def __init__(self):
        # gestion du temps
        self.clock = pygame.time.Clock()
        self.delta_time = 1
        self._running = True

        # surface
        self.gameSurface = None
        self.size = display.WIDTH, display.HEIGHT

        # menu
        self.menu_context = MenuContext(MenuContext.START_MENU)
        self.HUDfont = None
        self.menu: Menu = None
        self.ui_manager = None

        # son
        self.sounds = None

        # jeu
        self.game_manager: GameManager = None

    def start(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        OPTIONS.apply_volumes()
        assets.play_music(resources.MUSIC_MAIN)
        self.sounds = Sound()
        self.gameSurface = Display.create_window(OPTIONS.display_mode, OPTIONS.window_size)
        self._running = True

        self.HUDfont = assets.font(display.CAT_COMIC_FONT, display.HUD_FONT_SIZE)
        self.HUD_level_font = assets.font(display.CAT_COMIC_FONT, display.HUD_LEVEL_FONT_SIZE)
        self.game_manager = GameManager(self.gameSurface)
        self.ui_manager = pygame_gui.UIManager(self.size, str(assets.THEME_PATH))
        self.menu = Menu(self.ui_manager, self.gameSurface, self.menu_context)

    def handleEvent(self, event):
        self.ui_manager.process_events(event)
        if event.type == pygame.QUIT:
            self.quit()
        self.menu.handleMenu(event, self)

    def onLoop(self):
        """Calculs et détections de la frame courante."""
        self.ui_manager.update(display.UI_TIME_DELTA)
        if self.menu_context.get_active_menu() == MenuContext.INGAME_MENU:
            keys = pygame.key.get_pressed()
            self.game_manager.on_loop(self.delta_time, keys, self)

            # menu de fin de partie
            if self.game_manager.game_over and not self.game_manager.score_saved:
                self.menu_context.set_active_modal(MenuContext.END_GAME_MODAL)

    def restart(self):
        assets.play_music(resources.MUSIC_MAIN)
        self.menu_context.set_active_menu(MenuContext.START_MENU)
        self.menu_context.clear_active_modal()
        self.game_manager = GameManager(self.gameSurface)

    def return_to_debug_menu(self):
        """Fin d'un tableau lancé depuis Options > Debug : retour au menu principal, sur cet onglet."""
        from src.gui.OptionsWindow import OptionsTab
        self.restart()
        self.menu.show_options_window(self, OptionsTab.DEBUG)

    def _render_hud(self):
        player = self.game_manager.player
        score_text = self.HUDfont.render(texts.HUD_SCORE.format(score=player.score), True, display.WHITE)
        health_text = self.HUDfont.render(texts.HUD_HEALTH.format(health=max(player.health, 0), max_health=player_cfg.MAX_HEALTH), True, display.WHITE)
        self.gameSurface.blit(score_text, menu.HUD_SCORE_POS)
        self.gameSurface.blit(health_text, menu.HUD_HEALTH_POS)

        level_text = self.HUD_level_font.render(texts.HUD_LEVEL.format(level=self.game_manager.progression.level),
                                                True, display.WHITE)
        margin_x, margin_y = menu.HUD_LEVEL_MARGIN
        self.gameSurface.blit(level_text, (display.WIDTH - margin_x - level_text.get_width(), margin_y))

    def render(self) -> None:
        """Rendu de la frame courante."""
        active_menu = self.menu_context.get_active_menu()

        if active_menu == MenuContext.START_MENU:
            self.menu.show_start_screen(self)

        if active_menu == MenuContext.INGAME_MENU:
            self.game_manager.render_game(self, self.delta_time)
            self._render_hud()

        active_modal = self.menu_context.get_active_modal()
        if active_modal == MenuContext.INTRO_BOSS_MODAL:
            self.menu.show_boss_intro(self)
        elif active_modal == MenuContext.OUTRO_BOSS_MODAL:
            self.menu.show_boss_win(self)
        elif active_modal == MenuContext.END_GAME_MODAL:
            self.menu.show_end_screen(self)

        # pause du jeu pendant l'intro du boss
        boss = self.game_manager.boss
        if boss is not None:
            if time.time() - boss.start_timer <= INTRO_DURATION:
                self.menu_context.set_active_modal(MenuContext.INTRO_BOSS_MODAL)
            else:
                self.menu_context.clear_active_modal()
                self.menu_context.set_active_menu(MenuContext.INGAME_MENU)

        self.ui_manager.draw_ui(self.gameSurface)

    def quit(self) -> None:
        """Arrête la boucle principale (la fenêtre se ferme à la fin de la frame)."""
        self._running = False

    def shutdown(self) -> None:
        pygame.quit()

    def execute(self) -> None:
        """Boucle principale : handleEvent, onLoop & render."""
        self._running = True
        while self._running:
            for event in pygame.event.get():
                self.handleEvent(event)
            self.onLoop()
            self.render()
            pygame.display.flip()
            self.delta_time = min(self.clock.tick(display.FPS) / 1000.0, display.MAX_DELTA_TIME)
        self.shutdown()

    def save_score(self):
        data = load_scores()
        data.append({"pseudo": self.menu.user_text, "score": self.game_manager.player.score})
        with open(assets.SCORES_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self.restart()
