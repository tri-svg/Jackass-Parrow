import json
from typing import TYPE_CHECKING

import pygame
import pygame_gui

from src.gui.MenuContext import MenuContext
from src.gui.OptionsWindow import OptionsTab, OptionsWindow
from src.gui.widgets import PassiveImage
from src.settings import display, menu, resources, texts
from src.settings.bosses import BOSS_MENU_ORDER, BOSSES, BossConfig, BossId
from src.system import assets

if TYPE_CHECKING:
    from src.app import App

WIDTH, HEIGHT = display.WIDTH, display.HEIGHT
WHITE = display.WHITE


def load_scores() -> list:
    try:
        with open(assets.SCORES_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _scale_to_menu_height(image: pygame.Surface) -> pygame.Surface:
    ratio = menu.ILLUSTRATION_HEIGHT_RATIO
    return pygame.transform.scale(image, (image.get_width() * HEIGHT // ratio // image.get_height(), HEIGHT // ratio))


def _fit(image: pygame.Surface, max_size: tuple) -> pygame.Surface:
    """Redimensionne une image pour qu'elle tienne dans max_size en gardant ses proportions."""
    scale = min(max_size[0] / image.get_width(), max_size[1] / image.get_height())
    return pygame.transform.smoothscale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))


def _text_panel(lines: list, font: pygame.font.Font, padding: int, alpha: int = display.OVERLAY_ALPHA) -> pygame.Surface:
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
    def __init__(self, ui_manager, game_surface: pygame.Surface, menu_context: MenuContext):
        self.ui_manager = ui_manager
        self.game_surface = game_surface
        self.menu_context = menu_context
        self.menu_font = assets.font(display.CAT_COMIC_FONT, display.TITLE_FONT_SIZE)
        self.button_font = assets.font(display.CAT_COMIC_FONT, display.BUTTON_FONT_SIZE)

        self.start_button = None
        self.boss_button = None
        self.lore_button = None
        self.leaderboard_button = None
        self.options_button = None
        self.quit_button = None

        # fenêtres et leurs boutons de fermeture
        self.lore_window = None
        self.leaderboard_window = None
        self.boss_window = None
        self.lore_close_button = None
        self.leaderboard_close_button = None
        self.boss_close_button = None
        self.boss_case_buttons: dict = {}  # bouton -> BossId
        self.options_window: OptionsWindow = None
        self.debug_page = 0  # page de l'onglet Debug, gardée pour y revenir après un tableau de debug

        # menu de fin de partie (enregistrement du score)
        self.save_button_rect = None
        self.input_box_color = WHITE
        self.user_text = ''
        self.active = False
        self.input_box = pygame.Rect((WIDTH // 2 - menu.INPUT_BOX_SIZE[0] // 2, HEIGHT // menu.INPUT_BOX_Y_RATIO),
                                     menu.INPUT_BOX_SIZE)

        # surfaces pré-calculées
        self._background = assets.image(*resources.BACKGROUND_GREEN)
        self._tom_image = _scale_to_menu_height(assets.image(*resources.TOM_TEXTURE))
        self._tom_rect = self._tom_image.get_rect(
            center=(self._tom_image.get_width() // 2 + menu.TOM_ILLUSTRATION_MARGIN, HEIGHT // 2))
        self._perso_image = _scale_to_menu_height(assets.image(*resources.PLAYER_HD_TEXTURE))
        self._perso_rect = self._perso_image.get_rect(
            center=(self._perso_image.get_width() // menu.HERO_ILLUSTRATION_X_RATIO, HEIGHT // 2))
        self._title_shadow = self.menu_font.render(texts.GAME_TITLE, True, display.TITLE_SHADOW_COLOR)
        self._title = self.menu_font.render(texts.GAME_TITLE, True, WHITE)
        self._game_over_text = self.menu_font.render(texts.GAME_OVER, True, WHITE)
        self._save_text = self.button_font.render(texts.BUTTON_SAVE, True, WHITE)
        self._end_frame = pygame.Surface((WIDTH // menu.END_FRAME_RATIO, HEIGHT // menu.END_FRAME_RATIO), pygame.SRCALPHA)
        self._end_frame.fill((0, 0, 0, display.OVERLAY_ALPHA))
        self._boss_intro_panels: dict = {}
        self._boss_victory_panels: dict = {}

        self.setup_start_menu()

    # ------------------------------------------------------------------ menu principal
    def _menu_button(self, text: str, index: int) -> pygame_gui.elements.UIButton:
        x_pos = WIDTH // 2 - menu.BUTTON_SIZE[0] // 2
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((x_pos, menu.BUTTONS_TOP + menu.BUTTONS_SPACING * index), menu.BUTTON_SIZE),
            text=text,
            manager=self.ui_manager,
            object_id='@menu_button',
        )

    def _button_under(self, text: str, image_rect: pygame.Rect) -> pygame_gui.elements.UIButton:
        """Bouton du menu principal centré sous une illustration (Tom, le héros)."""
        rect = pygame.Rect((0, 0), menu.BUTTON_SIZE)
        rect.midtop = (image_rect.centerx, image_rect.bottom + menu.ILLUSTRATION_BUTTON_GAP)
        return pygame_gui.elements.UIButton(relative_rect=rect, text=text, manager=self.ui_manager,
                                            object_id='@menu_button')

    def _start_menu_buttons(self) -> tuple:
        return (self.start_button, self.boss_button, self.lore_button, self.leaderboard_button,
                self.options_button, self.quit_button)

    def setup_start_menu(self):
        self.game_surface.blit(self._background, (0, 0))
        self.start_button = self._menu_button(texts.BUTTON_START, 0)
        self.boss_button = self._menu_button(texts.BUTTON_BOSS_MODE, 1)
        self.lore_button = self._menu_button(texts.BUTTON_LORE, 2)
        self.options_button = self._menu_button(texts.BUTTON_OPTIONS, 3)
        self.leaderboard_button = self._button_under(texts.BUTTON_LEADERBOARD, self._tom_rect)
        self.quit_button = self._button_under(texts.BUTTON_QUIT, self._perso_rect)

    def show_start_screen(self, app: "App"):
        self.menu_context.set_active_menu(MenuContext.START_MENU)
        self.game_surface.blit(self._background, (0, 0))
        # la grande fenêtre Options recouvre les boutons du bas (Classement, Quitter) : on les cache
        for button in self._start_menu_buttons():
            if self.options_window is None:
                button.show()
            else:
                button.hide()

        self.game_surface.blit(self._tom_image, self._tom_rect)
        self.game_surface.blit(self._perso_image, self._perso_rect)
        shadow = menu.TITLE_SHADOW_OFFSET
        self.game_surface.blit(self._title_shadow,
                               self._title_shadow.get_rect(center=(WIDTH // 2 + shadow, menu.TITLE_Y + shadow)))
        self.game_surface.blit(self._title, self._title.get_rect(center=(WIDTH // 2, menu.TITLE_Y)))

    def hide_start_menu(self):
        for button in self._start_menu_buttons():
            button.hide()

    # ------------------------------------------------------------------ événements
    def handleMenu(self, event, app: "App"):
        if self.options_window is not None:
            self.options_window.handle(event)
            if self.options_window is not None and self.options_window.closed:
                self.options_window = None
            return

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button(event.ui_element, app)

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if self.lore_window and event.ui_element == self.lore_window:
                self.close_lore_window()
            if self.leaderboard_window and event.ui_element == self.leaderboard_window:
                self.close_leaderboard_window()
            if self.boss_window and event.ui_element == self.boss_window:
                self.close_boss_window()

        if app.game_manager.game_over:
            self._handle_end_screen(event, app)

    def _handle_button(self, element, app: "App"):
        if element == self.start_button:
            app.game_manager.start_game()
            app.sounds.son_button.play()
            self.menu_context.set_active_menu(MenuContext.INGAME_MENU)
            self.hide_start_menu()
        elif element == self.boss_button:
            app.sounds.son_button.play()
            self.show_boss_window()
        elif element in self.boss_case_buttons:
            boss_id = self.boss_case_buttons[element]
            app.sounds.son_button.play()
            self.close_boss_window()
            self.start_boss_fight(app, boss_id)
        elif element == self.lore_button:
            app.sounds.son_button.play()
            self.show_lore_window()
        elif element == self.leaderboard_button:
            app.sounds.son_button.play()
            self.show_leaderboard_window()
        elif element == self.options_button:
            app.sounds.son_button.play()
            self.show_options_window(app)
        elif element == self.quit_button:
            app.quit()
        elif self.lore_close_button and element == self.lore_close_button:
            self.close_lore_window()
        elif self.leaderboard_close_button and element == self.leaderboard_close_button:
            self.close_leaderboard_window()
        elif self.boss_close_button and element == self.boss_close_button:
            self.close_boss_window()

    def show_options_window(self, app: "App", tab: OptionsTab = OptionsTab.GENERAL):
        if self.options_window is not None:
            return

        def start_debug_level(level_id: int):
            self.debug_page = self.options_window.debug_page
            self.options_window = None
            app.game_manager.start_debug_level(level_id, app.return_to_debug_menu)
            self.menu_context.set_active_menu(MenuContext.INGAME_MENU)
            self.hide_start_menu()

        self.hide_start_menu()  # tout de suite : sinon pygame_gui les affiche encore une frame
        self.options_window = OptionsWindow(
            self.ui_manager, lambda rect: self._window(rect, resources.OPTIONS_WINDOW_BACKGROUND), tab,
            self.debug_page, start_debug_level, app.sounds.son_button.play)

    def start_boss_fight(self, app: "App", boss_id: BossId):
        app.game_manager.start_boss_mode(boss_id)
        self.menu_context.set_active_menu(MenuContext.INGAME_MENU)
        self.hide_start_menu()

    def _handle_end_screen(self, event, app: "App"):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.input_box.collidepoint(event.pos) and not self.active
            if self.save_button_rect is not None and self.save_button_rect.collidepoint(event.pos):
                app.save_score()
            self.input_box_color = display.INPUT_ACTIVE_COLOR if self.active else WHITE
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                app.save_score()
            elif event.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            else:
                self.user_text += event.unicode

    # ------------------------------------------------------------------ fenêtres
    def _window(self, rect: pygame.Rect, background: tuple) -> pygame_gui.elements.UIWindow:
        window = pygame_gui.elements.UIWindow(
            rect=rect,
            manager=self.ui_manager,
            window_display_title='',
            object_id='@window',
            resizable=False,
            draggable=False,
        )
        pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((0, 0), window.get_container().get_size()),
            image_surface=assets.image_copy(*background),
            manager=self.ui_manager,
            container=window,
        )
        return window

    def _close_button(self, window, center_x: int, top: int) -> pygame_gui.elements.UIButton:
        width, height = menu.WINDOW_BUTTON_SIZE
        return pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x - width // 2, top), (width, height)),
            text=texts.BUTTON_CLOSE,
            manager=self.ui_manager,
            container=window,
            object_id='@menu_button',
        )

    def _text_window(self, html_text: str):
        """Fenêtre avec fond, texte et bouton Fermer. Renvoie (fenêtre, bouton)."""
        window_rect = pygame.Rect(*menu.TEXT_WINDOW_RECT)
        padding = menu.WINDOW_PADDING
        text_box_height = window_rect.height - menu.WINDOW_BUTTON_SIZE[1] - padding * 2

        window = self._window(window_rect, resources.MENU_WINDOW_BACKGROUND)
        text_box = pygame_gui.elements.UITextBox(
            html_text=html_text,
            relative_rect=pygame.Rect(padding, padding, window_rect.width - padding * 2, text_box_height),
            manager=self.ui_manager,
            container=window,
            object_id='@text_box_in_window',
        )
        close_button = self._close_button(window, window_rect.width // 2, text_box.get_relative_rect().bottom + padding)
        return window, close_button

    def show_lore_window(self):
        if self.lore_window is None:
            self.lore_window, self.lore_close_button = self._text_window(texts.LORE)

    def close_lore_window(self):
        self.lore_window.kill()
        self.lore_window = None
        self.lore_close_button = None

    def show_leaderboard_window(self):
        if self.leaderboard_window is None:
            scores = sorted(load_scores(), key=lambda x: x["score"], reverse=True)
            leaderboard_text = "".join(texts.LEADERBOARD_LINE.format(rank=i + 1, pseudo=score['pseudo'], score=score['score'])
                                       for i, score in enumerate(scores[:texts.LEADERBOARD_SIZE]))
            self.leaderboard_window, self.leaderboard_close_button = self._text_window(leaderboard_text)

    def close_leaderboard_window(self):
        self.leaderboard_window.kill()
        self.leaderboard_window = None
        self.leaderboard_close_button = None

    def show_boss_window(self):
        """Fenêtre modale "Mode Boss" : une case cliquable par boss."""
        if self.boss_window is not None:
            return
        window_size = menu.BOSS_WINDOW_SIZE
        window_rect = pygame.Rect(((WIDTH - window_size[0]) // 2, (HEIGHT - window_size[1]) // 2), window_size)
        self.boss_window = self._window(window_rect, resources.BOSS_MENU_BACKGROUND)
        self.boss_window.set_blocking(True)  # bloque les clics sur le menu principal

        case_width, case_height = menu.BOSS_CASE_SIZE
        container_width = self.boss_window.get_container().get_size()[0]
        gap = (container_width - case_width * len(BOSS_MENU_ORDER)) // (len(BOSS_MENU_ORDER) + 1)
        self.boss_case_buttons = {}
        for index, boss_id in enumerate(BOSS_MENU_ORDER):
            case_rect = pygame.Rect((gap + index * (case_width + gap), menu.BOSS_CASES_TOP), menu.BOSS_CASE_SIZE)
            self._boss_case(BOSSES[boss_id], boss_id, case_rect)

        self.boss_close_button = self._close_button(self.boss_window, container_width // 2,
                                                    menu.BOSS_CASES_TOP + case_height + menu.WINDOW_PADDING)

    def _boss_case(self, config: BossConfig, boss_id: BossId, case_rect: pygame.Rect):
        # bouton (texture des boutons du menu) qui couvre toute la case, puis portrait par-dessus
        button = pygame_gui.elements.UIButton(
            relative_rect=case_rect,
            text=config.name,
            manager=self.ui_manager,
            container=self.boss_window,
            object_id='@boss_case',
        )
        self.boss_case_buttons[button] = boss_id

        padding = menu.BOSS_PORTRAIT_PADDING
        portrait_area = (case_rect.width - 2 * padding, case_rect.height - menu.BOSS_NAME_HEIGHT - padding)
        portrait = _fit(assets.image(*config.menu_texture), portrait_area)
        portrait_rect = portrait.get_rect(midtop=(case_rect.centerx, case_rect.top + padding))
        PassiveImage(
            relative_rect=portrait_rect,
            image_surface=portrait,
            manager=self.ui_manager,
            container=self.boss_window,
        )

    def close_boss_window(self):
        self.boss_window.kill()
        self.boss_window = None
        self.boss_close_button = None
        self.boss_case_buttons = {}

    # ------------------------------------------------------------------ modales
    def _blit_centered(self, surface: pygame.Surface):
        x = (self.game_surface.get_width() - surface.get_width()) // 2
        y = (self.game_surface.get_height() - surface.get_height()) // 2
        self.game_surface.blit(surface, (x, y))

    def show_boss_intro(self, app: "App"):
        config = app.game_manager.boss.config
        if config.name not in self._boss_intro_panels:
            lines = [line.format(title=config.intro_title) for line in texts.BOSS_INTRO]
            font = assets.font(display.DIMBO_FONT, display.BOSS_INTRO_FONT_SIZE)
            self._boss_intro_panels[config.name] = _text_panel(lines, font, padding=menu.BOSS_INTRO_PADDING)
        self._blit_centered(self._boss_intro_panels[config.name])

    def show_boss_win(self, app: "App"):
        config = app.game_manager.boss.config
        if config.name not in self._boss_victory_panels:
            lines = [line.format(title=config.victory_title) for line in texts.BOSS_VICTORY]
            font = assets.font(display.DIMBO_FONT, display.BOSS_WIN_FONT_SIZE)
            self._boss_victory_panels[config.name] = _text_panel(lines, font, padding=menu.BOSS_VICTORY_PADDING)
        self._blit_centered(self._boss_victory_panels[config.name])

    def show_end_screen(self, app: "App"):
        self.menu_context.set_active_modal(MenuContext.END_GAME_MODAL)
        self.game_surface.blit(self._end_frame, self._end_frame.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        shadow = menu.TITLE_SHADOW_OFFSET
        self.game_surface.blit(self._game_over_text,
                               self._game_over_text.get_rect(center=(WIDTH // 2 + shadow, HEIGHT // 3 + shadow)))
        score_text = self.menu_font.render(texts.END_SCORE.format(score=app.game_manager.player.score), True, WHITE)
        self.game_surface.blit(score_text, score_text.get_rect(center=(WIDTH // 2 + shadow, HEIGHT // 2 + shadow)))

        # zone de saisie du pseudo
        pygame.draw.rect(self.game_surface, self.input_box_color, self.input_box, menu.INPUT_BORDER_WIDTH)
        input_text = self.button_font.render(self.user_text, True, WHITE)
        self.game_surface.blit(input_text, (self.input_box.x + menu.INPUT_TEXT_PADDING,
                                            self.input_box.y + menu.INPUT_TEXT_PADDING))

        # bouton enregistrer (plus clair au survol)
        self.save_button_rect = self._save_text.get_rect(center=(WIDTH // 2, HEIGHT // menu.SAVE_BUTTON_Y_RATIO))
        hovered = self.save_button_rect.collidepoint(pygame.mouse.get_pos())
        color = display.SAVE_BUTTON_HOVER_COLOR if hovered else display.SAVE_BUTTON_COLOR
        pygame.draw.rect(self.game_surface, color, self.save_button_rect, border_radius=menu.SAVE_BUTTON_RADIUS)
        self.game_surface.blit(self._save_text, self.save_button_rect)
