from functools import lru_cache

import pygame

from src.settings import display, menu, resources, texts
from src.system import assets


@lru_cache(maxsize=None)
def _box_background(size: tuple) -> pygame.Surface:
    """
    Fond de la boîte à partir du template resources.DIALOGUE_BACKGROUND, en 9-slice : les coins et
    le cadre (menu.DIALOGUE_FRAME px) sont conservés, l'intérieur est répété en mosaïque, sans étirement.
    """
    template = assets.image(*resources.DIALOGUE_BACKGROUND)
    frame = menu.DIALOGUE_FRAME
    template_width, template_height = template.get_size()
    template_inner_width, template_inner_height = template_width - 2 * frame, template_height - 2 * frame
    width, height = size
    inner_width, inner_height = width - 2 * frame, height - 2 * frame
    box = pygame.Surface(size, pygame.SRCALPHA)

    def part(x, y, w, h):
        return template.subsurface((x, y, w, h))

    # intérieur en mosaïque
    inner = part(frame, frame, template_inner_width, template_inner_height)
    box.set_clip((frame, frame, inner_width, inner_height))
    for y in range(frame, height - frame, template_inner_height):
        for x in range(frame, width - frame, template_inner_width):
            box.blit(inner, (x, y))
    box.set_clip(None)

    # bords étirés sur leur longueur
    box.blit(pygame.transform.scale(part(frame, 0, template_inner_width, frame), (inner_width, frame)), (frame, 0))
    box.blit(pygame.transform.scale(part(frame, template_height - frame, template_inner_width, frame),
                                    (inner_width, frame)), (frame, height - frame))
    box.blit(pygame.transform.scale(part(0, frame, frame, template_inner_height), (frame, inner_height)), (0, frame))
    box.blit(pygame.transform.scale(part(template_width - frame, frame, frame, template_inner_height),
                                    (frame, inner_height)), (width - frame, frame))
    # coins
    box.blit(part(0, 0, frame, frame), (0, 0))
    box.blit(part(template_width - frame, 0, frame, frame), (width - frame, 0))
    box.blit(part(0, template_height - frame, frame, frame), (0, height - frame))
    box.blit(part(template_width - frame, template_height - frame, frame, frame), (width - frame, height - frame))
    return box


def _wrap(text: str, font: pygame.font.Font, max_width: int) -> list:
    """Coupe le texte en lignes qui tiennent dans max_width (au mot près)."""
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}" if line else word
        if line and font.size(candidate)[0] > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


class DialogueBox:
    """
    Boîte de dialogue en bas de l'écran, façon RPG Maker : portrait, nom, texte.
    Espace passe à la page suivante ; sinon elle passe seule après menu.DIALOGUE_AUTO_ADVANCE secondes.
    """

    def __init__(self, speaker: str, pages: list, portrait: tuple = None):
        self.pages = pages
        self.page = 0
        self.page_start = pygame.time.get_ticks()
        self.finished = False
        # Espace considéré comme enfoncé à l'ouverture (ex. le joueur tirait) : il faut le relâcher avant de passer
        self.skip_was_down = True

        margin = menu.DIALOGUE_MARGIN
        self.rect = pygame.Rect(margin, display.HEIGHT - margin - menu.DIALOGUE_HEIGHT,
                                display.WIDTH - 2 * margin, menu.DIALOGUE_HEIGHT)
        self.background = _box_background(self.rect.size)
        name_font = assets.font(menu.DIALOGUE_NAME_FONT, menu.DIALOGUE_NAME_FONT_SIZE)
        text_font = assets.font(menu.DIALOGUE_TEXT_FONT, menu.DIALOGUE_TEXT_FONT_SIZE)
        hint_font = assets.font(menu.DIALOGUE_HINT_FONT, menu.DIALOGUE_HINT_FONT_SIZE)

        padding = menu.DIALOGUE_PADDING
        self.portrait = None
        self.text_left = padding
        if portrait is not None:
            size = menu.DIALOGUE_PORTRAIT_SIZE
            self.portrait = assets.image_scaled((size, size), *portrait)
            self.text_left += size + padding
        text_width = self.rect.width - self.text_left - padding

        self.name_surface = name_font.render(speaker, True, menu.DIALOGUE_NAME_COLOR)
        self.hint_surface = hint_font.render(texts.DIALOGUE_NEXT_HINT, True, display.WHITE)
        self.page_lines = [[text_font.render(line, True, display.WHITE) for line in _wrap(text, text_font, text_width)]
                           for text in pages]

    def update(self, keys):
        if self.finished:
            return
        skip_down = keys[pygame.K_SPACE]
        pressed = skip_down and not self.skip_was_down
        self.skip_was_down = skip_down
        timed_out = pygame.time.get_ticks() - self.page_start >= menu.DIALOGUE_AUTO_ADVANCE * 1000
        if pressed or timed_out:
            self.page += 1
            self.page_start = pygame.time.get_ticks()
            self.finished = self.page >= len(self.pages)

    def render(self, scene: pygame.Surface):
        if self.finished:
            return
        scene.blit(self.background, self.rect)
        padding = menu.DIALOGUE_PADDING
        if self.portrait is not None:
            scene.blit(self.portrait, (self.rect.x + padding, self.rect.centery - self.portrait.get_height() // 2))
        x, y = self.rect.x + self.text_left, self.rect.y + padding
        scene.blit(self.name_surface, (x, y))
        y += self.name_surface.get_height() + menu.DIALOGUE_NAME_GAP
        for line in self.page_lines[self.page]:
            scene.blit(line, (x, y))
            y += line.get_height()
        scene.blit(self.hint_surface, (self.rect.right - padding - self.hint_surface.get_width(),
                                       self.rect.bottom - padding - self.hint_surface.get_height()))
