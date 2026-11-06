import pygame

from src.system import assets

# Directions utilisées par les projectiles, le joueur et les ennemis
LEFT = "gauche"
RIGHT = "Valerie chevalariass"


class Bullet(pygame.sprite.Sprite):
    TEXTURE = ("entity", "bullet.png")
    SPEED = 600

    def __init__(self, x, y, direction):
        super().__init__()
        self.direction = direction
        self.speed = self.SPEED
        # l'image (partagée) est retournée quand le projectile part vers la droite
        if direction == RIGHT:
            self.image = assets.image_flipped(*self.TEXTURE)
        else:
            self.image = assets.image(*self.TEXTURE)
        self.rect = self.image.get_rect(x=x, y=y)

    def update(self, scene_width, blocs, delta_time: float):
        if self.direction == LEFT:
            self.rect.x -= self.speed * delta_time
        else:
            self.rect.x += self.speed * delta_time

        rect = self.rect
        for bloc in blocs:
            if not bloc.transparent and rect.colliderect(bloc.rect):
                self.kill()
                return

        if rect.left > scene_width or rect.right < 0:
            self.kill()
