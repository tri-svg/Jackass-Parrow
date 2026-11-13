"""
Éditeur de tableaux (outil de dev, pas utilisé par le jeu) : python builder.py

Le code du tableau s'affiche à droite, à copier-coller dans src/settings/levels.py.

Souris (sur le tableau)
    clic gauche + glisser   crée un bloc (simple clic dans le vide : bloc d'une case)
    clic gauche sur un bloc spawnable oui / non (teinté en jaune)
    clic droit sur un bloc  supprime le bloc
    clic molette            place le joueur
Clavier
    T                       bloc sous la souris transparent oui / non (contour bleu)
    J                       place le joueur sous la souris
    Ctrl+Z / Ctrl+C         annuler / copier le code
    F5                      tester (comme Options > Debug) ; Échap arrête l'essai
Réglages : src/settings/builder.py
"""

import math
import os

import pygame

from src.app import App
from src.block.BlockGroup import BlockGroup
from src.gui.MenuContext import MenuContext
from src.settings import builder as cfg
from src.settings import display, levels, resources
from src.system import assets
from src.system.GameManager import GameManager
from src.system.LevelCollection import LevelCollection
from src.system.Options import OPTIONS

TILE = levels.TILE_SIZE
OFFSET_X, OFFSET_Y = levels.BLOCK_OFFSET
HELP = [  # aide courte en bas du panneau (détail : docstring ci-dessus)
    "glisser          : créer un bloc",
    "clic             : bloc 1 case / spawnable",
    "clic droit       : supprimer un bloc",
    "molette ou J     : placer le joueur",
    "T                : bloc transparent",
    "Ctrl+Z / Ctrl+C  : annuler / copier",
    "F5 / Échap       : tester / arrêter l'essai",
]
WIDTH, HEIGHT = display.WIDTH, display.HEIGHT


def block_tile_at(pos: tuple) -> tuple:
    """Case de la grille des blocs (décalée de BLOCK_OFFSET) sous un point en px."""
    return math.floor((pos[0] - OFFSET_X) / TILE), math.floor((pos[1] - OFFSET_Y) / TILE)


def spawn_tile_at(pos: tuple) -> tuple:
    """Case du point d'apparition du joueur (grille sans décalage) sous un point en px."""
    return pos[0] // TILE, pos[1] // TILE


def block_rect(block: list) -> pygame.Rect:
    x, y, width, height = block[:4]
    return pygame.Rect(x * TILE + OFFSET_X, y * TILE + OFFSET_Y, width * TILE, height * TILE)


class Button:
    def __init__(self, label: str, rect: pygame.Rect, action):
        self.label, self.rect, self.action = label, rect, action


class Builder:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:  # pas de carte son : on continue sans
            os.environ["SDL_AUDIODRIVER"] = "dummy"
            pygame.mixer.init()
        # tout est dessiné en pleine résolution sur self.screen, puis réduit dans la fenêtre (cf. WINDOW_SCALE)
        full_size = (WIDTH + cfg.PANEL_WIDTH, HEIGHT)
        self.scale = cfg.WINDOW_SCALE or self._auto_scale(full_size)
        self.window = pygame.display.set_mode((round(full_size[0] * self.scale), round(full_size[1] * self.scale)))
        self.screen = pygame.Surface(full_size).convert()
        pygame.display.set_caption("Jackass-Parrow - builder")
        self.game_surface = self.screen.subsurface((0, 0, WIDTH, HEIGHT))
        OPTIONS.apply_volumes()
        self.font = pygame.font.SysFont(cfg.FONT_NAME, cfg.FONT_SIZE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.blocks: list = []  # [x, y, largeur, hauteur, spawnable, transparent]
        self.spawn = cfg.DEFAULT_PLAYER_SPAWN
        self.background_index = 0
        self.loaded_level = 0  # 0 = nouveau tableau, sinon id du tableau de settings/levels.py chargé
        self.undo_stack: list = []
        self.drag_start = None
        self.drag_moved = False
        self.message = ""
        self.message_time = 0.0
        self.player_image = assets.image(*resources.PLAYER_TEXTURE)
        self.buttons = self._make_buttons()

    # ------------------------------------------------------------------ fenêtre réduite
    @staticmethod
    def _auto_scale(full_size: tuple) -> float:
        """Échelle pour que la fenêtre tienne sur l'écran (jamais agrandie)."""
        info = pygame.display.Info()
        if info.current_w <= 0 or info.current_h <= 0:
            return 1.0
        return min(1.0, info.current_w * cfg.SCREEN_FILL / full_size[0], info.current_h * cfg.SCREEN_FILL / full_size[1])

    def to_full(self, pos: tuple) -> tuple:
        """Position dans la fenêtre réduite -> position en pleine résolution."""
        return int(pos[0] / self.scale), int(pos[1] / self.scale)

    def mouse(self) -> tuple:
        return self.to_full(pygame.mouse.get_pos())

    def present(self):
        """Affiche self.screen réduit à la taille de la fenêtre."""
        if self.scale == 1:
            self.window.blit(self.screen, (0, 0))
        else:
            pygame.transform.smoothscale(self.screen, self.window.get_size(), self.window)
        pygame.display.flip()

    # ------------------------------------------------------------------ données
    @property
    def background(self) -> tuple:
        return cfg.BACKGROUNDS[self.background_index]

    def layout(self) -> list:
        """Le tableau au format de settings/levels.py."""
        result = [tuple(self.spawn)]
        for x, y, width, height, spawnable, transparent in self.blocks:
            if transparent:
                result.append((x, y, width, height, spawnable, True))
            elif spawnable:
                result.append((x, y, width, height, True))
            else:
                result.append((x, y, width, height))
        return result

    def code(self) -> str:
        lines = [f"{cfg.NEW_LEVEL_NAME} = ["]
        lines += [f"    {entry}," for entry in self.layout()]
        lines.append("]")
        return "\n".join(lines)

    def _save_undo(self):
        self.undo_stack.append(([list(block) for block in self.blocks], self.spawn))
        del self.undo_stack[:-cfg.UNDO_LIMIT]

    def undo(self):
        if self.undo_stack:
            self.blocks, self.spawn = self.undo_stack.pop()
            self.say("annulé")

    def clear(self):
        self._save_undo()
        self.blocks = []
        self.say("tableau vidé")

    def load_level(self, level_id: int):
        """Charge un tableau existant (0 = tableau vide)."""
        self._save_undo()
        self.loaded_level = level_id
        self.blocks = []
        self.spawn = cfg.DEFAULT_PLAYER_SPAWN
        if level_id == 0:
            self.say("nouveau tableau")
            return
        for entry in levels.LEVELS[level_id - 1]:
            if len(entry) == 2:
                self.spawn = tuple(entry)
                continue
            x, y, width, height, *flags = entry
            spawnable = bool(flags[0]) if len(flags) > 0 else False
            transparent = bool(flags[1]) if len(flags) > 1 else False
            self.blocks.append([x, y, width, height, spawnable, transparent])
        self.say(f"tableau {level_id} chargé")

    def change_level(self, step: int):
        self.load_level((self.loaded_level + step) % (len(levels.LEVELS) + 1))

    def next_background(self):
        self.background_index = (self.background_index + 1) % len(cfg.BACKGROUNDS)

    def copy(self):
        text = self.code()
        print(text)
        try:
            pygame.scrap.put_text(text)
            self.say("code copié (et affiché dans la console)")
        except (pygame.error, AttributeError, NotImplementedError):
            self.say("code affiché dans la console")

    def say(self, message: str):
        self.message = message
        self.message_time = pygame.time.get_ticks() / 1000

    def block_at(self, pos: tuple):
        """Bloc du tableau sous la souris (le dernier créé en premier), ou None."""
        for block in reversed(self.blocks):
            if block_rect(block).collidepoint(pos):
                return block
        return None

    # ------------------------------------------------------------------ événements
    def _make_buttons(self) -> list:
        actions = [
            ("Tester (F5)", self.test), ("Copier", self.copy),
            ("Annuler", self.undo), ("Tout effacer", self.clear),
            ("< Tableau", lambda: self.change_level(-1)), ("Tableau >", lambda: self.change_level(1)),
            ("Fond", self.next_background),
        ]
        width, height = cfg.BUTTON_SIZE
        buttons = []
        for index, (label, action) in enumerate(actions):
            column, row = index % 3, index // 3
            x = WIDTH + cfg.PANEL_PADDING + column * (width + cfg.BUTTON_GAP)
            y = cfg.PANEL_PADDING + row * (height + cfg.BUTTON_GAP)
            buttons.append(Button(label, pygame.Rect(x, y, width, height), action))
        return buttons

    def handle_event(self, event):
        if hasattr(event, "pos"):  # souris : on repasse en coordonnées pleine résolution
            attributes = dict(event.dict, pos=self.to_full(event.pos))
            event = pygame.event.Event(event.type, attributes)
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_down(event)
        elif event.type == pygame.MOUSEMOTION and self.drag_start is not None:
            if block_tile_at(event.pos) != self.drag_start:
                self.drag_moved = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.drag_start is not None:
            self._mouse_up(event)
        elif event.type == pygame.KEYDOWN:
            self._key_down(event)

    def _mouse_down(self, event):
        if event.pos[0] >= WIDTH:
            if event.button == 1:
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos):
                        button.action()
            return
        if event.button == 1:
            self.drag_start = block_tile_at(event.pos)
            self.drag_moved = False
        elif event.button == 3:
            block = self.block_at(event.pos)
            if block is not None:
                self._save_undo()
                self.blocks.remove(block)
        elif event.button == 2:
            self._save_undo()
            self.spawn = spawn_tile_at(event.pos)

    def _mouse_up(self, event):
        start, end = self.drag_start, block_tile_at((min(event.pos[0], WIDTH - 1), event.pos[1]))
        self.drag_start = None
        if self.drag_moved:
            self._save_undo()
            x, y = min(start[0], end[0]), min(start[1], end[1])
            self.blocks.append([x, y, abs(end[0] - start[0]) + 1, abs(end[1] - start[1]) + 1, False, False])
        else:
            block = self.block_at(event.pos)
            if block is not None:
                self._save_undo()
                block[4] = not block[4]
            else:  # simple clic dans le vide : bloc d'une case
                self._save_undo()
                self.blocks.append([start[0], start[1], 1, 1, False, False])

    def _key_down(self, event):
        mouse = self.mouse()
        ctrl = event.mod & pygame.KMOD_CTRL
        if event.key == pygame.K_z and ctrl:
            self.undo()
        elif event.key == pygame.K_c and ctrl:
            self.copy()
        elif event.key == pygame.K_F5:
            self.test()
        elif event.key == pygame.K_t:
            block = self.block_at(mouse)
            if block is not None:
                self._save_undo()
                block[5] = not block[5]
        elif event.key == pygame.K_j and mouse[0] < WIDTH:
            self._save_undo()
            self.spawn = spawn_tile_at(mouse)

    # ------------------------------------------------------------------ rendu
    def draw(self):
        scene = self.game_surface
        scene.blit(assets.image(*self.background), (0, 0))
        group = BlockGroup(scene)
        LevelCollection(group).build_tableau(self.layout(), self.background)
        group.draw(scene)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x in range(OFFSET_X % TILE, WIDTH, TILE):
            pygame.draw.line(overlay, cfg.GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(OFFSET_Y % TILE, HEIGHT, TILE):
            pygame.draw.line(overlay, cfg.GRID_COLOR, (0, y), (WIDTH, y))
        for block in self.blocks:
            if block[4]:
                overlay.fill(cfg.SPAWNABLE_TINT, block_rect(block))
            if block[5]:
                pygame.draw.rect(overlay, cfg.TRANSPARENT_COLOR, block_rect(block), cfg.TRANSPARENT_BORDER)
        mouse = self.mouse()
        if self.drag_start is not None and self.drag_moved:
            end = block_tile_at(mouse)
            x, y = min(self.drag_start[0], end[0]), min(self.drag_start[1], end[1])
            rect = block_rect([x, y, abs(end[0] - self.drag_start[0]) + 1, abs(end[1] - self.drag_start[1]) + 1])
            overlay.fill(cfg.DRAG_COLOR, rect)
        elif mouse[0] < WIDTH:
            hovered = self.block_at(mouse)
            if hovered is not None:
                pygame.draw.rect(overlay, cfg.HOVER_BORDER_COLOR, block_rect(hovered), cfg.HOVER_BORDER)
        scene.blit(overlay, (0, 0))
        scene.blit(self.player_image, (self.spawn[0] * TILE, self.spawn[1] * TILE))
        self._draw_panel()

    def _text(self, text: str, pos: tuple, color=cfg.TEXT_COLOR):
        self.screen.blit(self.font.render(text, True, color), pos)

    def _draw_panel(self, status: str = None):
        panel = pygame.Rect(WIDTH, 0, cfg.PANEL_WIDTH, HEIGHT)
        self.screen.fill(cfg.PANEL_COLOR, panel)
        mouse = self.mouse()
        for button in self.buttons:
            color = cfg.BUTTON_HOVER_COLOR if button.rect.collidepoint(mouse) else cfg.BUTTON_COLOR
            self.screen.fill(color, button.rect)
            label = self.font.render(button.label, True, cfg.TEXT_COLOR)
            self.screen.blit(label, label.get_rect(center=button.rect.center))

        x = WIDTH + cfg.PANEL_PADDING
        y = self.buttons[-1].rect.bottom + cfg.PANEL_PADDING
        source = f"tableau {self.loaded_level}" if self.loaded_level else "nouveau tableau"
        info = f"{source} | case {block_tile_at(mouse)}" if mouse[0] < WIDTH else source
        for line in [status or info, self._message(), ""] + self.code().split("\n"):
            self._text(line, (x, y), cfg.HELP_COLOR if line in (info, status) else cfg.TEXT_COLOR)
            y += cfg.LINE_HEIGHT
        help_lines = HELP
        y = HEIGHT - cfg.PANEL_PADDING - len(help_lines) * cfg.LINE_HEIGHT
        for line in help_lines:
            self._text(line, (x, y), cfg.HELP_COLOR)
            y += cfg.LINE_HEIGHT

    def _message(self) -> str:
        if pygame.time.get_ticks() / 1000 - self.message_time < cfg.MESSAGE_DURATION:
            return self.message
        return ""

    # ------------------------------------------------------------------ essai
    def test(self):
        """Joue le tableau comme Options > Debug : un ennemi par bloc spawnable, fin au dernier tué."""
        if not any(block[4] for block in self.blocks):
            self.say("il faut au moins un bloc spawnable pour tester")
            return
        app = App()  # seulement ce que GameManager et le HUD utilisent
        app.gameSurface = self.game_surface
        app.HUDfont = assets.font(display.CAT_COMIC_FONT, display.HUD_FONT_SIZE)
        app.HUD_level_font = assets.font(display.CAT_COMIC_FONT, display.HUD_LEVEL_FONT_SIZE)
        app.menu_context.set_active_menu(MenuContext.INGAME_MENU)
        app.game_manager = GameManager(self.game_surface)
        finished = []
        app.game_manager.start_test_level(self.layout(), self.background, lambda: finished.append(True))
        delta_time = 1 / cfg.FPS
        while not finished and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    finished.append(True)
            app.game_manager.on_loop(delta_time, pygame.key.get_pressed(), app)
            app.game_manager.render_game(app, delta_time)
            app._render_hud()
            self._draw_panel("essai en cours : Échap pour arrêter")
            self.present()
            delta_time = min(self.clock.tick(cfg.FPS) / 1000, display.MAX_DELTA_TIME)
        self.say("fin de l'essai")

    # ------------------------------------------------------------------ boucle
    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            self.present()
            self.clock.tick(cfg.FPS)
        pygame.quit()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # chemins relatifs des ressources
    Builder().run()
