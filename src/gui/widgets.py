import pygame_gui


class PassiveImage(pygame_gui.elements.UIImage):
    """Image qui ne capte pas la souris (laisse le survol et le clic au bouton placé dessous)."""

    def can_hover(self) -> bool:
        return False

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        return False
