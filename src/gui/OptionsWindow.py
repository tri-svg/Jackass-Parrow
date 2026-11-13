from enum import Enum
from functools import lru_cache
from typing import Callable

import pygame
import pygame_gui

from src.block.BlockGroup import BlockGroup
from src.gui.widgets import PassiveImage
from src.settings import controls, display, levels, menu, resources, texts
from src.settings.display import DisplayMode
from src.system import Display, assets
from src.system.LevelCollection import LevelCollection, level_difficulty
from src.system.Options import OPTIONS


class OptionsTab(Enum):
    GENERAL = "general"
    KEYS = "keys"
    DEBUG = "debug"


TAB_TITLES = {
    OptionsTab.GENERAL: texts.OPTIONS_TAB_GENERAL,
    OptionsTab.KEYS: texts.OPTIONS_TAB_KEYS,
    OptionsTab.DEBUG: texts.OPTIONS_TAB_DEBUG,
}


@lru_cache(maxsize=None)
def level_thumbnail(level_id: int) -> pygame.Surface:
    """
    Miniature d'un tableau (fond menu.DEBUG_THUMBNAIL_BACKGROUND, blocs spawnable teintés),
    encadrée de la couleur de sa difficulté.
    """
    difficulty = level_difficulty(level_id)
    background = menu.DEBUG_THUMBNAIL_BACKGROUND
    scene = assets.image_copy(*background)
    blocks = BlockGroup(scene)
    LevelCollection(blocks).load(level_id, background)
    blocks.draw(scene)
    for block in blocks.get_spawnable():
        tint = pygame.Surface(block.rect.size, pygame.SRCALPHA)
        tint.fill(menu.DEBUG_SPAWNABLE_TINT)
        scene.blit(tint, block.rect)
    thumbnail = pygame.transform.smoothscale(scene, menu.DEBUG_THUMBNAIL_SIZE)
    color = menu.DEBUG_DIFFICULTY_COLORS.get(difficulty, menu.DEBUG_UNKNOWN_DIFFICULTY_COLOR)
    pygame.draw.rect(thumbnail, color, thumbnail.get_rect(), menu.DEBUG_THUMBNAIL_BORDER)
    return thumbnail


@lru_cache(maxsize=None)
def level_case(level_id: int, hovered: bool) -> pygame.Surface:
    """Case de la grille Debug : bois des boutons (clair au survol), miniature, nom du tableau."""
    wood = resources.GUI_BUTTON_HOVER if hovered else resources.GUI_BUTTON_NORMAL
    case = assets.image_scaled(menu.DEBUG_CASE_SIZE, *wood).copy()
    thumbnail = level_thumbnail(level_id)
    case.blit(thumbnail, thumbnail.get_rect(midtop=(case.get_width() // 2, menu.DEBUG_CASE_PADDING)))
    font = assets.font(display.CAT_COMIC_FONT, menu.DEBUG_CASE_FONT_SIZE)
    name = font.render(texts.DEBUG_LEVEL_NAME.format(level=level_id), True, display.WHITE)
    name_area_top = menu.DEBUG_CASE_PADDING + thumbnail.get_height()
    case.blit(name, name.get_rect(center=(case.get_width() // 2, (name_area_top + case.get_height()) // 2)))
    return case


class OptionsWindow:
    """
    Grande fenêtre modale du menu principal, avec des onglets :
    Général (volumes), Touches (persistantes, cf. system/Options.py), Debug (lance un tableau au choix).
    """

    def __init__(self, ui_manager, make_window: Callable, tab: OptionsTab, debug_page: int,
                 on_debug_level: Callable[[int], None], on_click: Callable[[], None]):
        self.ui_manager = ui_manager
        self.on_debug_level = on_debug_level
        self.on_click = on_click
        self.debug_page = debug_page
        self.waiting_binding = None  # (action, slot) en attente d'une touche
        self.closed = False

        size = menu.OPTIONS_WINDOW_SIZE
        rect = pygame.Rect(((display.WIDTH - size[0]) // 2, (display.HEIGHT - size[1]) // 2), size)
        self.window = make_window(rect)
        self.window.set_blocking(True)
        self.width = self.window.get_container().get_size()[0]

        # onglets
        tab_width, tab_height = menu.OPTIONS_TAB_SIZE
        tabs_width = len(OptionsTab) * tab_width + (len(OptionsTab) - 1) * menu.OPTIONS_TAB_SPACING
        self.tab_buttons = {}
        for index, options_tab in enumerate(OptionsTab):
            x = (self.width - tabs_width) // 2 + index * (tab_width + menu.OPTIONS_TAB_SPACING)
            self.tab_buttons[options_tab] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x, menu.OPTIONS_TABS_TOP), menu.OPTIONS_TAB_SIZE),
                text=TAB_TITLES[options_tab], manager=ui_manager, container=self.window, object_id='@tab')

        close_width, close_height = menu.WINDOW_BUTTON_SIZE
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(((self.width - close_width) // 2, size[1] - close_height - menu.WINDOW_PADDING),
                                      menu.WINDOW_BUTTON_SIZE),
            text=texts.BUTTON_CLOSE, manager=ui_manager, container=self.window, object_id='@menu_button')

        self.content_rect = pygame.Rect(0, menu.OPTIONS_CONTENT_TOP, self.width,
                                        size[1] - menu.OPTIONS_CONTENT_TOP - close_height - 2 * menu.WINDOW_PADDING)
        self.panels = {}
        self._build_general()
        self._build_keys()
        self._build_debug()
        self.tab = None
        self.select_tab(tab)

    # ------------------------------------------------------------------ outils
    def _panel(self) -> pygame_gui.elements.UIPanel:
        return pygame_gui.elements.UIPanel(relative_rect=self.content_rect, starting_height=1, manager=self.ui_manager,
                                           container=self.window, object_id='@options_panel')

    def _label(self, panel, rect: pygame.Rect, text: str) -> pygame_gui.elements.UILabel:
        return pygame_gui.elements.UILabel(relative_rect=rect, text=text, manager=self.ui_manager, container=panel,
                                           object_id='@options_label')

    def select_tab(self, options_tab: OptionsTab):
        self.tab = options_tab
        self._cancel_binding()
        for each_tab, button in self.tab_buttons.items():
            button.change_object_id('@tab_active' if each_tab == options_tab else '@tab')
        for each_tab, panel in self.panels.items():
            if each_tab == options_tab:
                panel.show()
            else:
                panel.hide()

    def close(self):
        self.window.kill()
        self.closed = True

    # ------------------------------------------------------------------ onglet Général
    def _build_general(self):
        panel = self._panel()
        self.panels[OptionsTab.GENERAL] = panel
        label_width, row_height = menu.OPTIONS_LABEL_WIDTH, menu.OPTIONS_ROW_HEIGHT
        slider_width = menu.OPTIONS_SLIDER_WIDTH
        value_width = menu.OPTIONS_VALUE_WIDTH
        left = (self.width - label_width - slider_width - value_width - 2 * menu.OPTIONS_GAP) // 2
        # affichage : mode et taille de fenêtre (menus déroulants)
        dropdown_width = slider_width
        self.mode_names = {texts.DISPLAY_MODE_NAMES[mode]: mode for mode in DisplayMode}
        self.size_names = {texts.WINDOW_SIZE_NAME.format(width=w, height=h): (w, h)
                           for w, h in Display.available_window_sizes()}
        current_size = texts.WINDOW_SIZE_NAME.format(width=OPTIONS.window_size[0], height=OPTIONS.window_size[1])
        if current_size not in self.size_names:  # taille enregistrée qui ne tient plus sur cet écran
            self.size_names[current_size] = OPTIONS.window_size
        y = menu.OPTIONS_GENERAL_TOP
        self._label(panel, pygame.Rect(left, y, label_width, row_height), texts.OPTIONS_DISPLAY_MODE)
        self.mode_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=list(self.mode_names), starting_option=texts.DISPLAY_MODE_NAMES[OPTIONS.display_mode],
            relative_rect=pygame.Rect(left + label_width + menu.OPTIONS_GAP, y, dropdown_width, row_height),
            manager=self.ui_manager, container=panel, object_id='@options_dropdown')
        y += row_height + menu.OPTIONS_GAP
        self._label(panel, pygame.Rect(left, y, label_width, row_height), texts.OPTIONS_WINDOW_SIZE)
        self.size_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=list(self.size_names), starting_option=current_size,
            relative_rect=pygame.Rect(left + label_width + menu.OPTIONS_GAP, y, dropdown_width, row_height),
            manager=self.ui_manager, container=panel, object_id='@options_dropdown')
        self._refresh_size_dropdown()

        self.sliders = {}
        self.slider_values = {}
        rows = [("music", texts.OPTIONS_MUSIC_VOLUME, OPTIONS.music_volume),
                ("sound", texts.OPTIONS_SOUND_VOLUME, OPTIONS.sound_volume)]
        for index, (name, title, value) in enumerate(rows):
            y = menu.OPTIONS_GENERAL_TOP + (index + 2) * (row_height + menu.OPTIONS_GAP)
            self._label(panel, pygame.Rect(left, y, label_width, row_height), title)
            slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(left + label_width + menu.OPTIONS_GAP, y, slider_width, row_height),
                start_value=value, value_range=(0, 100), click_increment=menu.OPTIONS_SLIDER_STEP,
                manager=self.ui_manager, container=panel, object_id='@volume_slider')
            self.sliders[slider] = name
            self.slider_values[name] = self._label(
                panel, pygame.Rect(left + label_width + slider_width + 2 * menu.OPTIONS_GAP, y, value_width, row_height),
                texts.OPTIONS_PERCENT.format(value=value))

    def _refresh_size_dropdown(self):
        """La taille ne compte qu'en mode fenêtré (sans bordure : taille de l'écran)."""
        if OPTIONS.display_mode == DisplayMode.WINDOWED:
            self.size_dropdown.enable()
        else:
            self.size_dropdown.disable()

    def _on_dropdown(self, dropdown, text: str):
        if dropdown == self.mode_dropdown:
            OPTIONS.set_display(self.mode_names[text], OPTIONS.window_size)
            self._refresh_size_dropdown()
        elif dropdown == self.size_dropdown:
            OPTIONS.set_display(OPTIONS.display_mode, self.size_names[text])

    def _on_slider(self, slider, value):
        name = self.sliders[slider]
        value = int(round(value))
        if name == "music":
            OPTIONS.set_music_volume(value)
        else:
            OPTIONS.set_sound_volume(value)
        self.slider_values[name].set_text(texts.OPTIONS_PERCENT.format(value=value))

    # ------------------------------------------------------------------ onglet Touches
    def _build_keys(self):
        panel = self._panel()
        self.panels[OptionsTab.KEYS] = panel
        label_width, row_height = menu.OPTIONS_LABEL_WIDTH, menu.OPTIONS_KEY_ROW_HEIGHT
        key_width = menu.OPTIONS_KEY_BUTTON_WIDTH
        gap = menu.OPTIONS_GAP
        left = (self.width - label_width - controls.BINDING_SLOTS * (key_width + gap)) // 2
        self.key_buttons = {}  # bouton -> (action, slot)
        y = menu.OPTIONS_KEYS_TOP
        for action in controls.ACTION_ORDER:
            self._label(panel, pygame.Rect(left, y, label_width, row_height), texts.ACTION_NAMES[action])
            for slot in range(controls.BINDING_SLOTS):
                x = left + label_width + gap + slot * (key_width + gap)
                button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(x, y, key_width, row_height), text="", manager=self.ui_manager,
                    container=panel, object_id='@key_button')
                self.key_buttons[button] = (action, slot)
            y += row_height + menu.OPTIONS_KEY_ROW_GAP
        self._label(panel, pygame.Rect(0, y, self.width, menu.OPTIONS_HINT_HEIGHT), texts.OPTIONS_KEYS_HINT)
        reset_width, reset_height = menu.OPTIONS_RESET_SIZE
        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.width - reset_width) // 2, y + menu.OPTIONS_HINT_HEIGHT, reset_width,
                                      reset_height),
            text=texts.OPTIONS_RESET_KEYS, manager=self.ui_manager, container=panel, object_id='@key_button')
        self._refresh_keys()

    def _refresh_keys(self):
        for button, (action, slot) in self.key_buttons.items():
            if self.waiting_binding == (action, slot):
                button.set_text(texts.OPTIONS_WAITING_KEY)
            else:
                button.set_text(OPTIONS.key_name(action, slot) or texts.OPTIONS_NO_KEY)

    def _cancel_binding(self):
        if self.waiting_binding is not None:
            self.waiting_binding = None
            self._refresh_keys()

    def _on_key(self, key: int):
        action, slot = self.waiting_binding
        self.waiting_binding = None
        if key == controls.CLEAR_BINDING_KEY:
            OPTIONS.bind(action, slot, None)
        elif key != controls.CANCEL_BINDING_KEY:
            OPTIONS.bind(action, slot, key)
        self._refresh_keys()

    # ------------------------------------------------------------------ onglet Debug
    def _level_ids(self) -> list:
        return list(range(1, len(levels.LEVELS) + 1))

    def _page_count(self) -> int:
        per_page = menu.DEBUG_GRID[0] * menu.DEBUG_GRID[1]
        return max(1, -(-len(self._level_ids()) // per_page))

    def _build_debug(self):
        old_panel = self.panels.get(OptionsTab.DEBUG)
        if old_panel is not None:
            old_panel.kill()
        panel = self._panel()
        self.panels[OptionsTab.DEBUG] = panel
        self.debug_page = max(0, min(self.debug_page, self._page_count() - 1))

        columns, rows = menu.DEBUG_GRID
        case_width, case_height = menu.DEBUG_CASE_SIZE
        gap_x, gap_y = menu.DEBUG_CASE_GAP
        grid_width = columns * case_width + (columns - 1) * gap_x
        left = (self.width - grid_width) // 2
        per_page = columns * rows
        page_ids = self._level_ids()[self.debug_page * per_page:(self.debug_page + 1) * per_page]
        self.level_buttons = {}  # bouton -> id du tableau
        self.level_images = {}  # bouton -> image de la case (changée au survol)
        for index, level_id in enumerate(page_ids):
            column, row = index % columns, index // columns
            case_rect = pygame.Rect(left + column * (case_width + gap_x), row * (case_height + gap_y),
                                    case_width, case_height)
            # bouton invisible pour le clic et le survol, image de la case par-dessus
            button = pygame_gui.elements.UIButton(
                relative_rect=case_rect, text="", manager=self.ui_manager, container=panel, object_id='@level_case')
            self.level_buttons[button] = level_id
            self.level_images[button] = PassiveImage(
                relative_rect=case_rect, image_surface=level_case(level_id, False), manager=self.ui_manager,
                container=panel)

        # flèches et numéro de page ; chaque flèche se clique aussi sur toute la bande à côté de la grille
        arrow_width, arrow_height = menu.DEBUG_ARROW_SIZE
        grid_height = rows * case_height + (rows - 1) * gap_y
        arrow_y = (grid_height - arrow_height) // 2
        margin = menu.DEBUG_ARROW_MARGIN
        zone_width = left - menu.DEBUG_ARROW_ZONE_GAP
        self.previous_zone = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, zone_width, grid_height), text="", manager=self.ui_manager,
            container=panel, object_id='@level_case')
        self.next_zone = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.width - zone_width, 0, zone_width, grid_height), text="",
            manager=self.ui_manager, container=panel, object_id='@level_case')
        self.previous_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(left - margin - arrow_width, arrow_y, arrow_width, arrow_height),
            text=texts.DEBUG_PREVIOUS, manager=self.ui_manager, container=panel, object_id='@key_button')
        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(left + grid_width + margin, arrow_y, arrow_width, arrow_height),
            text=texts.DEBUG_NEXT, manager=self.ui_manager, container=panel, object_id='@key_button')
        self._label(panel, pygame.Rect(left + grid_width + margin, arrow_y + arrow_height, arrow_width,
                                       menu.OPTIONS_HINT_HEIGHT),
                    texts.DEBUG_PAGE.format(page=self.debug_page + 1, count=self._page_count()))
        if self.debug_page == 0:
            self.previous_button.disable()
            self.previous_zone.disable()
        if self.debug_page >= self._page_count() - 1:
            self.next_button.disable()
            self.next_zone.disable()

    def _change_page(self, step: int):
        self.debug_page += step
        self._build_debug()
        self.select_tab(OptionsTab.DEBUG)

    # ------------------------------------------------------------------ événements
    def handle(self, event):
        """Traite un événement pygame / pygame_gui destiné à la fenêtre."""
        if self.waiting_binding is not None and event.type == pygame.KEYDOWN:
            self._on_key(event.key)
            return
        if event.type in (pygame_gui.UI_BUTTON_ON_HOVERED, pygame_gui.UI_BUTTON_ON_UNHOVERED):
            if event.ui_element in self.level_images:
                hovered = event.type == pygame_gui.UI_BUTTON_ON_HOVERED
                self.level_images[event.ui_element].set_image(level_case(self.level_buttons[event.ui_element], hovered))
            return
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element in (self.mode_dropdown,
                                                                                    self.size_dropdown):
            self._on_dropdown(event.ui_element, event.text)
            return
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and event.ui_element in self.sliders:
            self._on_slider(event.ui_element, event.value)
            return
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return
        element = event.ui_element
        if element == self.close_button:
            self.on_click()
            self.close()
        elif element in self.tab_buttons.values():
            self.on_click()
            self.select_tab(next(tab for tab, button in self.tab_buttons.items() if button == element))
        elif element in self.key_buttons:
            self.waiting_binding = self.key_buttons[element]
            self._refresh_keys()
        elif element == self.reset_button:
            self.on_click()
            OPTIONS.reset_bindings()
            self._cancel_binding()
            self._refresh_keys()
        elif element in (self.previous_button, self.previous_zone):
            self.on_click()
            self._change_page(-1)
        elif element in (self.next_button, self.next_zone):
            self.on_click()
            self._change_page(1)
        elif element in self.level_buttons:
            self.on_click()
            level_id = self.level_buttons[element]
            self.close()
            self.on_debug_level(level_id)
