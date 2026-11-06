import json
from typing import TYPE_CHECKING

import pygame
import pygame_gui

from src.gui.MenuContext import MenuContext
from src.system import assets
from src.system.GameConfig import APPConfig

if TYPE_CHECKING:
    from src.app import App

WIDTH, HEIGHT = APPConfig.WIDTH, APPConfig.HEIGHT
WHITE = (255, 255, 255)

LORE_TEXT = """
            Quand il était jeune, Jackass-Parrow n'était pas le pirate le plus agile du navire.
            C'est pour cela que ses parents lui ont greffé un canon scié sur l'arrière-train en guise de cadeau d'anniversaire.
            Malheureusement, celui-ci fut exclu de sa fratrie lorsqu'il tira accidentellement dans la tête de son père en voulant s'étirer.
            Jackass-Parrow passa donc le reste de son enfance dans une jungle, élevé par une tribu indigène.

            Aujourd'hui, menacé par Tom de l'Abbaye et ses chevaliers, Jackass-Parrow est prêt à tout pour défendre ceux qui l'ont recueilli.
            """

BOSS_INTRO_TEXT = [
    "Le combat final approche",
    "Préparez-vous à combattre le grand...",
    "** TOM DE L'ABBAYE  **",
]

BOSS_WIN_TEXT = [
    "Victoire !",
    "Vous avez vaincu l'abominable",
    "",
    "Tom de L'Abbaye !!",
    "",
    "Merci d'avoir joué!",
]


def load_scores() -> list:
    try:
        with open(assets.SCORES_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _scale_to_menu_height(image: pygame.Surface) -> pygame.Surface:
    return pygame.transform.scale(image, (image.get_width() * HEIGHT // 1.4 // image.get_height(), HEIGHT // 1.4))


def _text_panel(lines: list, font: pygame.font.Font, padding: int, alpha: int = 150) -> pygame.Surface:
    """Bloc de texte centré sur fond noir semi-transparent."""
    text_surfaces = [font.render(line, True, WHITE) for line in lines]
    max_width = max(surface.get_width() for surface in text_surfaces)
    total_height = sum(surface.get_height() for surface in text_surfaces)

    panel = pygame.Surface((max_width + 2 * padding, total_height + 2 * padding), pygame.SRCALPHA)
    panel.fill((0, 0, 0, alpha))

    y_offset = padding
    for surface in text_surfaces:
        panel.blit(surface, ((panel.get_width() - surface.get_width()) // 2, y_offset))
        y_offset += surface.get_height()
    return panel


class Menu:
    BUTTON_WIDTH = 220
    BUTTON_HEIGHT = 80

    def __init__(self, ui_manager, game_surface: pygame.Surface, menu_context: MenuContext):
        self.ui_manager = ui_manager
        self.game_surface = game_surface
        self.menu_context = menu_context
        self.menu_font = assets.font(assets.CAT_COMIC_FONT, 80)
        self.lore_font = assets.font(assets.DIMBO_FONT, 38)
        self.button_font = assets.font(assets.CAT_COMIC_FONT, 50)
        self.leaderboard_font = assets.font(assets.CAT_COMIC_FONT, 40)

        self.start_button = None
        self.boss_button = None
        self.lore_button = None
        self.leaderboard_button = None

        # fenêtres et leurs boutons de fermeture
        self.lore_window = None
        self.leaderboard_window = None
        self.lore_close_button = None
        self.leaderboard_close_button = None

        # menu de fin de partie (enregistrement du score)
        self.save_button_rect = None
        self.input_box_color = WHITE
        self.user_text = ''
        self.active = False
        self.input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 1.6, 200, 50)

        # surfaces pré-calculées (avant : rechargées / recalculées à chaque frame)
        self._background = assets.image("background", "fondGameJam.png")
        self._tom_image = _scale_to_menu_height(assets.image("entity", "tom.png"))
        self._tom_rect = self._tom_image.get_rect(center=(self._tom_image.get_width() // 2 + 50, HEIGHT // 2))
        self._perso_image = _scale_to_menu_height(assets.image("player", "playerHD.png"))
        self._perso_rect = self._perso_image.get_rect(center=(self._perso_image.get_width() // 0.45, HEIGHT // 2))
        self._title_shadow = self.menu_font.render("Jackass-Parrow", True, (50, 50, 50))
        self._title = self.menu_font.render("Jackass-Parrow", True, WHITE)
        self._game_over_text = self.menu_font.render("Game Over", True, WHITE)
        self._save_text = self.button_font.render("Enregistrer", True, WHITE)
        self._end_frame = pygame.Surface((WIDTH // 1.3, HEIGHT // 1.3), pygame.SRCALPHA)
        self._end_frame.fill((0, 0, 0, 150))
        self._boss_intro_panel = None
        self._boss_win_panel = None

        self.setup_start_menu()

    # ------------------------------------------------------------------ menu principal
    def _menu_button(self, text: str, index: int) -> pygame_gui.elements.UIButton:
        x_pos = WIDTH // 2 - self.BUTTON_WIDTH // 2
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_pos, HEIGHT // 2 + 70 * index), (self.BUTTON_WIDTH, self.BUTTON_HEIGHT)),
            text=text,
            manager=self.ui_manager,
            object_id='@menu_button',
        )

    def _start_menu_buttons(self) -> tuple:
        return self.start_button, self.boss_button, self.lore_button, self.leaderboard_button

    def setup_start_menu(self):
        self.game_surface.blit(self._background, (0, 0))
        self.start_button = self._menu_button('Lancer', 0)
        self.boss_button = self._menu_button('Mode Boss', 1)
        self.lore_button = self._menu_button('Histoire', 2)
        self.leaderboard_button = self._menu_button('Classement', 3)

    def show_start_screen(self, app: "App"):
        self.menu_context.set_active_menu(MenuContext.START_MENU)
        self.game_surface.blit(self._background, (0, 0))
        for button in self._start_menu_buttons():
            button.show()

        self.game_surface.blit(self._tom_image, self._tom_rect)
        self.game_surface.blit(self._perso_image, self._perso_rect)
        self.game_surface.blit(self._title_shadow, self._title_shadow.get_rect(center=(WIDTH // 2 + 5, HEIGHT // 3 + 5)))
        self.game_surface.blit(self._title, self._title.get_rect(center=(WIDTH // 2, HEIGHT // 3)))

    def hide_start_menu(self):
        for button in self._start_menu_buttons():
            button.hide()

    # ------------------------------------------------------------------ événements
    def handleMenu(self, event, app: "App"):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button(event.ui_element, app)

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if self.lore_window and event.ui_element == self.lore_window:
                self.close_lore_window()
            if self.leaderboard_window and event.ui_element == self.leaderboard_window:
                self.close_leaderboard_window()

        if app.game_manager.game_over:
            self._handle_end_screen(event, app)

    def _handle_button(self, element, app: "App"):
        if element == self.start_button:
            app.game_manager.start_game()
            app.sounds.son_button.play()
            self.menu_context.set_active_menu(MenuContext.INGAME_MENU)
            self.hide_start_menu()
        elif element == self.boss_button:
            app.game_manager.boss_mode = True
            app.sounds.son_button.play()
            app.game_manager.start_boss_mode()
            self.menu_context.set_active_menu(MenuContext.INGAME_MENU)
            self.hide_start_menu()
        elif element == self.lore_button:
            app.sounds.son_button.play()
            self.show_lore_window()
        elif element == self.leaderboard_button:
            app.sounds.son_button.play()
            self.show_leaderboard_window()
        elif self.lore_close_button and element == self.lore_close_button:
            self.close_lore_window()
        elif self.leaderboard_close_button and element == self.leaderboard_close_button:
            self.close_leaderboard_window()

    def _handle_end_screen(self, event, app: "App"):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.input_box.collidepoint(event.pos) and not self.active
            if self.save_button_rect is not None and self.save_button_rect.collidepoint(event.pos):
                app.save_score()
            self.input_box_color = (0, 150, 0) if self.active else WHITE
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                app.save_score()
            elif event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            else:
                self.user_text += event.unicode

    # ------------------------------------------------------------------ fenêtres
    def _text_window(self, html_text: str):
        """Crée une fenêtre (fond + texte + bouton Fermer). Renvoie (fenêtre, bouton)."""
        window_rect = pygame.Rect((WIDTH // 4, HEIGHT // 6), (WIDTH // 2, HEIGHT // 1.5))
        button_width, button_height, padding = 180, 70, 20
        text_box_height = window_rect.height - button_height - padding * 2

        window = pygame_gui.elements.UIWindow(
            rect=window_rect,
            manager=self.ui_manager,
            window_display_title='',
            object_id='@window',
            resizable=False,
            draggable=False,
        )
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((0, 0), window.get_container().get_size()),
            image_surface=assets.image_copy("background", "menu.png"),
            manager=self.ui_manager,
            container=window,
        )
        text_box = pygame_gui.elements.UITextBox(
            html_text=html_text,
            relative_rect=pygame.Rect(padding, padding, window_rect.width - padding * 2, text_box_height),
            manager=self.ui_manager,
            container=window,
            object_id='@text_box_in_window',
        )
        close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(((window_rect.width - button_width) // 2, text_box.get_relative_rect().bottom + padding),
                                      (button_width, button_height)),
            text='Fermer',
            manager=self.ui_manager,
            container=window,
            object_id='@menu_button',
        )
        return window, close_button

    def show_lore_window(self):
        if self.lore_window is None:
            self.lore_window, self.lore_close_button = self._text_window(LORE_TEXT)

    def close_lore_window(self):
        self.lore_window.kill()
        self.lore_window = None
        self.lore_close_button = None

    def show_leaderboard_window(self):
        if self.leaderboard_window is None:
            scores = sorted(load_scores(), key=lambda x: x["score"], reverse=True)
            leaderboard_text = "".join(f"{i + 1}. {score['pseudo']} - {score['score']}<br>"
                                       for i, score in enumerate(scores[:10]))
            self.leaderboard_window, self.leaderboard_close_button = self._text_window(leaderboard_text)

    def close_leaderboard_window(self):
        self.leaderboard_window.kill()
        self.leaderboard_window = None
        self.leaderboard_close_button = None

    # ------------------------------------------------------------------ modales
    def _blit_centered(self, surface: pygame.Surface):
        x = (self.game_surface.get_width() - surface.get_width()) // 2
        y = (self.game_surface.get_height() - surface.get_height()) // 2
        self.game_surface.blit(surface, (x, y))

    def show_boss_intro(self, app: "App"):
        if self._boss_intro_panel is None:
            self._boss_intro_panel = _text_panel(BOSS_INTRO_TEXT, assets.font(assets.DIMBO_FONT, 52), padding=60)
        self._blit_centered(self._boss_intro_panel)

    def show_boss_win(self):
        if self._boss_win_panel is None:
            self._boss_win_panel = _text_panel(BOSS_WIN_TEXT, assets.font(assets.DIMBO_FONT, 48), padding=20)
        self._blit_centered(self._boss_win_panel)

    def show_end_screen(self, app: "App"):
        self.menu_context.set_active_modal(MenuContext.END_GAME_MODAL)
        self.game_surface.blit(self._end_frame, self._end_frame.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        self.game_surface.blit(self._game_over_text,
                               self._game_over_text.get_rect(center=(WIDTH // 2 + 5, HEIGHT // 3 + 5)))
        score_text = self.menu_font.render(f"Score : {app.game_manager.player.score}", True, WHITE)
        self.game_surface.blit(score_text, score_text.get_rect(center=(WIDTH // 2 + 5, HEIGHT // 2 + 5)))

        # zone de saisie du pseudo
        pygame.draw.rect(self.game_surface, self.input_box_color, self.input_box, 2)
        input_text = self.button_font.render(self.user_text, True, WHITE)
        self.game_surface.blit(input_text, (self.input_box.x + 5, self.input_box.y + 5))

        # bouton enregistrer (plus clair au survol)
        self.save_button_rect = self._save_text.get_rect(center=(WIDTH // 2, HEIGHT // 1.3))
        hovered = self.save_button_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.game_surface, (0, 200, 0) if hovered else (0, 150, 0), self.save_button_rect, border_radius=10)
        self.game_surface.blit(self._save_text, self.save_button_rect)
