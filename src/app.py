import json
import time

import pygame
import pygame_gui

from src.gui.Menu import Menu, load_scores
from src.gui.MenuContext import MenuContext
from src.system import assets
from src.system.GameConfig import APPConfig
from src.system.GameManager import GameManager
from src.system.Sound import Sound

HUD_COLOR = (255, 255, 255)
BOSS_INTRO_DURATION = 5  # secondes

# Délai max pris en compte entre deux frames. Sans ça, un ralentissement ponctuel
# (chargement, fenêtre déplacée...) produit un delta énorme et le joueur / les tirs
# traversent les blocs. N'a aucun effet tant que le jeu tourne au-dessus de 20 FPS.
MAX_DELTA_TIME = 1 / 20

# pygame_gui reçoit volontairement un "temps écoulé" fixe et énorme :
# les transitions du thème (survol des boutons) sont donc instantanées, comme à l'origine.
UI_TIME_DELTA = 60


class App:
    def __init__(self):
        # gestion du temps
        self.clock = pygame.time.Clock()
        self.delta_time = 1
        self._running = True

        # surface
        self.gameSurface = None
        self.size = APPConfig.WIDTH, APPConfig.HEIGHT

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
        pygame.mixer.music.set_volume(0.15)
        assets.play_music(assets.MAIN_THEME_PATH)
        self.sounds = Sound()
        self.gameSurface = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        self.HUDfont = assets.font(assets.CAT_COMIC_FONT, 36)
        self.game_manager = GameManager(self.gameSurface)
        self.ui_manager = pygame_gui.UIManager(self.size, str(assets.THEME_PATH))
        self.menu = Menu(self.ui_manager, self.gameSurface, self.menu_context)

    def handleEvent(self, event):
        self.ui_manager.process_events(event)
        if event.type == pygame.QUIT:
            self._running = False
        self.menu.handleMenu(event, self)

    def onLoop(self):
        """Calculs et détections de la frame courante."""
        self.ui_manager.update(UI_TIME_DELTA)
        if self.menu_context.get_active_menu() == MenuContext.INGAME_MENU:
            keys = pygame.key.get_pressed()
            self.game_manager.on_loop(self.delta_time, keys, self)

            # menu de fin de partie
            if self.game_manager.game_over and not self.game_manager.score_saved:
                self.menu_context.set_active_modal(MenuContext.END_GAME_MODAL)

    def restart(self):
        assets.play_music(assets.MAIN_THEME_PATH)
        self.menu_context.set_active_menu(MenuContext.START_MENU)
        self.menu_context.clear_active_modal()
        self.game_manager = GameManager(self.gameSurface)

    def _render_hud(self):
        player = self.game_manager.player
        self.gameSurface.blit(self.HUDfont.render(f"Score: {player.score}", True, HUD_COLOR), (10, 10))
        self.gameSurface.blit(self.HUDfont.render(f"Vie: {player.health}", True, HUD_COLOR), (10, 40))

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
            self.menu.show_boss_win()
        elif active_modal == MenuContext.END_GAME_MODAL:
            self.menu.show_end_screen(self)

        # pause du jeu pendant l'intro du boss
        boss = self.game_manager.boss
        if boss is not None:
            if time.time() - boss.start_timer <= BOSS_INTRO_DURATION:
                self.menu_context.set_active_modal(MenuContext.INTRO_BOSS_MODAL)
            else:
                self.menu_context.clear_active_modal()
                self.menu_context.set_active_menu(MenuContext.INGAME_MENU)

        self.ui_manager.draw_ui(self.gameSurface)

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
            self.delta_time = min(self.clock.tick(APPConfig.FPS) / 1000.0, MAX_DELTA_TIME)
        self.shutdown()

    def save_score(self):
        data = load_scores()
        data.append({"pseudo": self.menu.user_text, "score": self.game_manager.player.score})
        with open(assets.SCORES_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self.restart()
