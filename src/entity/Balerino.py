import math
import random
from enum import Enum, auto
from functools import lru_cache

import pygame

from src.entity.Boss import Boss
from src.entity.Bullet import LEFT, RIGHT
from src.entity.EnemyBullet import EnemyBullet
from src.entity.Player import Player
from src.settings import bosses, display, levels, resources
from src.settings.bosses import BalerinoAttack, BossDifficulty, BossId
from src.system import assets


def _column_x(column: int) -> int:
    """Bord gauche d'une colonne de la grille des blocs, en px."""
    return column * levels.TILE_SIZE + levels.BLOCK_OFFSET[0]


def _row_y(row: int) -> int:
    """Bord haut d'une ligne de la grille des blocs, en px."""
    return row * levels.TILE_SIZE + levels.BLOCK_OFFSET[1]


def _shaded(surface: pygame.Surface, shade: int) -> pygame.Surface:
    """Copie assombrie d'une image (transparence conservée)."""
    copy = surface.copy()
    copy.fill((shade, shade, shade, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return copy


@lru_cache(maxsize=None)
def _spin_frames(from_texture: tuple, to_texture: tuple, size: tuple, frame_count: int, depth: int,
                 shade: int) -> tuple:
    """
    Pirouette semi-3D de from_texture vers to_texture (images partagées, lecture seule).

    Rotation d'un demi-tour autour de l'axe vertical : l'image s'aplatit (cos de l'angle) tandis
    qu'une tranche assombrie d'épaisseur `depth` apparaît (sin de l'angle), comme un item Minecraft
    vu de profil. Passé le profil, c'est to_texture qui s'élargit, sa tranche de l'autre côté.
    """
    width, height = size
    faces = (assets.image_scaled(size, *from_texture), assets.image_scaled(size, *to_texture))
    sides = tuple(_shaded(face, shade) for face in faces)
    frames = []
    for index in range(frame_count):
        # milieu de chaque tranche de temps : ni 0 (image d'origine) ni pi (image d'arrivée)
        angle = math.pi * (index + 0.5) / frame_count
        second_half = angle > math.pi / 2
        face, side = (faces[1], sides[1]) if second_half else (faces[0], sides[0])

        thickness = round(depth * abs(math.sin(angle)))
        face_width = max(1, min(round(width * abs(math.cos(angle))), width - thickness))
        face = pygame.transform.scale(face, (face_width, height))
        side = pygame.transform.scale(side, (face_width, height))

        # face + tranche centrées ; la tranche dépasse à droite puis, après le profil, à gauche
        left = (width - face_width - thickness) // 2
        face_x, layer_step = (left + thickness, -1) if second_half else (left, 1)
        frame = pygame.Surface(size, pygame.SRCALPHA)
        for layer in range(thickness, 0, -1):
            frame.blit(side, (face_x + layer * layer_step, 0))
        frame.blit(face, (face_x, 0))
        frames.append(frame)
    return tuple(frames)


# Géométrie de l'arène en px, déduite de settings/levels.py
ARENA_LEFT = _column_x(levels.ARENA_FIRST_COLUMN)
ARENA_RIGHT = _column_x(levels.ARENA_LAST_COLUMN + 1)
ARENA_CENTER_X = (ARENA_LEFT + ARENA_RIGHT) / 2
GROUND_TOP = _row_y(levels.GROUND_ROW)
PLATFORM_TOP = _row_y(levels.BALERINO_PLATFORM_TOP_ROW)
CHICKEN_RISE = bosses.BALERINO_CHICKEN_EXTRA_ROWS * levels.TILE_SIZE  # px
DANCE_LEFT = _column_x(levels.ARENA_FIRST_COLUMN + levels.BALERINO_PLATFORM_WIDTH)
DANCE_RIGHT = _column_x(levels.ARENA_LAST_COLUMN - levels.BALERINO_PLATFORM_WIDTH + 1)


class _Step(Enum):
    PAUSE = auto()  # pose de repos entre deux attaques
    DANCE = auto()  # 1. danse entre les plateformes
    WALK_TO_CENTER = auto()  # 2. et 3. rejoint le centre (en tournant)...
    STRETCH = auto()  # ... s'étire sur la pointe des pieds...
    WINDUP = auto()  # ... attend avant de tirer...
    FIRE = auto()  # ... tire ses salves de poules...
    UNSTRETCH = auto()  # ... et reprend sa taille
    RISE = auto()  # 3. ... sort par le haut...
    SPLIT_WAIT = auto()  # ... attend hors de l'écran...
    SPLIT_FALL = auto()  # ... retombe en grand écart...
    SPLIT_HOLD = auto()  # ... reste posé sur les plateformes...
    SPLIT_RISE = auto()  # ... repart par le haut...
    LAND = auto()  # ... et retombe au centre


class Balerino(Boss):
    """
    Balerino : enchaîne 3 attaques dans un ordre mélangé (cf. BALERINO_ATTACKS), avec une pause
    entre chacune. Son contact fait mal (le bouclier n'y peut rien).
        1. danse de gauche à droite entre les plateformes : il faut monter dessus ou lui sauter par-dessus
        2. au centre, s'étire sur la pointe des pieds et tire une colonne de poules de chaque côté, du sol jusqu'au-dessus
           des plateformes (le joueur posé dessus est touché)
        3. sort par le haut et retombe en grand écart, étiré sur toute la largeur, les pieds sur les
           plateformes : il faut rester au sol au milieu, sous lui
    """

    BOSS_ID = BossId.BALERINO

    def __init__(self, game_surface, enemy_bullets, difficulty: BossDifficulty = BossDifficulty.NORMAL,
                 background: tuple = None):
        super().__init__(game_surface, enemy_bullets, difficulty, background)

        # réglages (les noms sont ceux utilisés par BALERINO_HARD)
        self.pause = bosses.BALERINO_PAUSE
        self.contact_damage = bosses.BALERINO_CONTACT_DAMAGE
        self.contact_tolerance = bosses.BALERINO_CONTACT_TOLERANCE
        self.dance_speed = bosses.BALERINO_DANCE_SPEED
        self.dance_crossings = bosses.BALERINO_DANCE_CROSSINGS
        self.spin_half_turn = bosses.BALERINO_SPIN_HALF_TURN
        self.walk_speed = bosses.BALERINO_WALK_SPEED
        self.stretch_speed = bosses.BALERINO_STRETCH_SPEED
        self.chicken_windup = bosses.BALERINO_CHICKEN_WINDUP
        self.chickens_per_side = bosses.BALERINO_CHICKENS_PER_SIDE
        self.chicken_volleys = bosses.BALERINO_CHICKEN_VOLLEYS
        self.chicken_volley_delay = bosses.BALERINO_CHICKEN_VOLLEY_DELAY
        self.split_rise_speed = bosses.BALERINO_SPLIT_RISE_SPEED
        self.split_fall_speed = bosses.BALERINO_SPLIT_FALL_SPEED
        self.split_duration = bosses.BALERINO_SPLIT_DURATION
        self.split_offscreen_delay = bosses.BALERINO_SPLIT_OFFSCREEN_DELAY

        # textures (partagées, lecture seule)
        self.rest_texture = self.TEXTURE
        self.rest_damage_texture = self.TEXTURE_DAMAGE
        left, right = resources.BALERINO_DANCE_LEFT_TEXTURE, resources.BALERINO_DANCE_RIGHT_TEXTURE
        spin = (self.config.size, bosses.BALERINO_SPIN_FRAMES, bosses.BALERINO_SPIN_DEPTH,
                bosses.BALERINO_SPIN_SIDE_SHADE)
        # un tour complet : image "gauche" -> profil -> image "droite" -> profil -> image "gauche"
        self.spin_cycle = _spin_frames(left, right, *spin) + _spin_frames(right, left, *spin)
        split_width = ARENA_RIGHT - ARENA_LEFT
        split_height = bosses.BALERINO_SPLIT_HEIGHT
        if split_height is None:  # garde les proportions du sprite
            source_width, source_height = assets.image(*resources.BALERINO_SPLIT_TEXTURE).get_size()
            split_height = round(split_width * source_height / source_width)
        split_size = (split_width, split_height)
        self.split_texture = assets.image_scaled(split_size, *resources.BALERINO_SPLIT_TEXTURE)
        self.split_damage_texture = assets.image_scaled(split_size, *resources.BALERINO_SPLIT_DAMAGE_TEXTURE)
        # étirement : redimensionnées à la hauteur courante pendant l'attaque des poules
        self.stretch_source = assets.image(*resources.BALERINO_STRETCH_TEXTURE)
        self.stretch_damage_source = assets.image(*resources.BALERINO_STRETCH_DAMAGE_TEXTURE)
        self.stretch_height = float(self.config.size[1])
        # surfaces de travail (redessinées à chaque frame par Boss.render)
        self.normal_image = self.image
        self.split_image = pygame.Surface(split_size, pygame.SRCALPHA)
        self.chicken_size = assets.image(*resources.CHICKEN_TEXTURE).get_size()

        # position en flottants pour des déplacements fluides (self.rect suit)
        self.x, self.y = float(self.rect.x), float(self.rect.y)
        self.last_update = None

        # routine
        self.routine: list[BalerinoAttack] = []
        self.step: _Step = None
        self.step_start = 0.0
        self.dance_direction = 1
        self.crossings_left = 0
        self.volleys_fired = 0
        self.after_walk = _Step.STRETCH  # étape qui suit WALK_TO_CENTER

    def setup_hard_mode(self):
        for name, value in bosses.BALERINO_HARD.items():
            if not hasattr(self, name):
                raise AttributeError(f"BALERINO_HARD : réglage inconnu '{name}'")
            setattr(self, name, value)

    # ------------------------------------------------------------------ boucle
    def attack(self, player: Player, now: float):
        # pas de delta time fourni aux boss : on le mesure (limité, ex. après la pause de l'intro)
        delta_time = 0 if self.last_update is None else min(now - self.last_update, display.MAX_DELTA_TIME)
        self.last_update = now
        if self.step is None:
            self._set_step(_Step.PAUSE, now)

        {
            _Step.PAUSE: self._pause,
            _Step.DANCE: self._dance,
            _Step.WALK_TO_CENTER: self._walk_to_center,
            _Step.STRETCH: self._stretch,
            _Step.WINDUP: self._windup,
            _Step.FIRE: self._fire,
            _Step.UNSTRETCH: self._unstretch,
            _Step.RISE: self._rise,
            _Step.SPLIT_WAIT: self._split_wait,
            _Step.SPLIT_FALL: self._split_fall,
            _Step.SPLIT_HOLD: self._split_hold,
            _Step.SPLIT_RISE: self._split_rise,
            _Step.LAND: self._land,
        }[self.step](now, delta_time)

        self.rect.topleft = (round(self.x), round(self.y))
        self._check_contact(player)

    def _swap_image(self, image: pygame.Surface):
        """
        Change de surface de travail en y dessinant tout de suite la texture courante :
        Boss.render affiche self.image avant de la redessiner, une surface neuve serait vide (invisible).
        """
        self.image = image
        self._set_texture(self.TEXTURE_DAMAGE if self.is_evasive() else self.TEXTURE)

    def _set_step(self, step: _Step, now: float):
        self.step = step
        self.step_start = now

    def _check_contact(self, player: Player):
        """Le contact fait mal ; pas de parade possible."""
        tolerance = self.contact_tolerance
        hitbox = pygame.Rect(self.rect.x, self.rect.y + tolerance, self.rect.width, self.rect.height - tolerance)
        if player.health > 0 and hitbox.colliderect(player.rect) and player.touched():
            player.health -= self.contact_damage - 1  # touched() retire déjà 1 PV

    # ------------------------------------------------------------------ routine
    def _next_attack(self, now: float):
        """Attaque suivante : chacune passe une fois dans un ordre mélangé, puis on remélange."""
        if not self.routine:
            self.routine = list(bosses.BALERINO_ATTACKS)
            random.shuffle(self.routine)
        attack = self.routine.pop(0)

        if attack == BalerinoAttack.DANCE:
            self.crossings_left = self.dance_crossings
            # part vers le côté le plus éloigné
            self.dance_direction = 1 if self.rect.centerx < ARENA_CENTER_X else -1
            self._set_step(_Step.DANCE, now)
        elif attack == BalerinoAttack.CHICKENS:
            self.after_walk = _Step.STRETCH
            self._set_step(_Step.WALK_TO_CENTER, now)
        elif attack == BalerinoAttack.SPLIT:
            # décolle du centre : sur place, il traverserait un joueur qui dépasse du bord d'une plateforme
            self.after_walk = _Step.RISE
            self._set_step(_Step.WALK_TO_CENTER, now)

    def _show_rest(self):
        self.TEXTURE = self.rest_texture
        self.TEXTURE_DAMAGE = self.rest_damage_texture

    def _pause(self, now: float, delta_time: float):
        self._show_rest()
        if now - self.step_start >= self.pause:
            self._next_attack(now)

    # ------------------------------------------------------------------ 1. danse
    def _spin(self, now: float):
        """
        Tourne sur lui-même depuis le début de l'étape (demi-tour de l'image "gauche" à "droite" et inversement).
        Même image quand il est touché : il continue de tourner en clignotant.
        """
        half_turns = (now - self.step_start) / self.spin_half_turn
        frames_per_half_turn = len(self.spin_cycle) // 2
        self.TEXTURE = self.spin_cycle[int(half_turns * frames_per_half_turn) % len(self.spin_cycle)]
        self.TEXTURE_DAMAGE = self.TEXTURE

    def _dance(self, now: float, delta_time: float):
        self._spin(now)
        self.x += self.dance_speed * delta_time * self.dance_direction

        width = self.rect.width
        if self.dance_direction > 0 and self.x + width >= DANCE_RIGHT:
            self.x = DANCE_RIGHT - width
            self.dance_direction = -1
            self.crossings_left -= 1
        elif self.dance_direction < 0 and self.x <= DANCE_LEFT:
            self.x = DANCE_LEFT
            self.dance_direction = 1
            self.crossings_left -= 1

        if self.crossings_left <= 0:
            self._set_step(_Step.PAUSE, now)

    # ------------------------------------------------------------------ 2. poules
    def _walk_to_center(self, now: float, delta_time: float):
        target_x = ARENA_CENTER_X - self.rect.width / 2
        self._spin(now)
        step = self.walk_speed * delta_time
        if abs(target_x - self.x) <= step:
            self.x = target_x
            self.stretch_height = float(self.rect.height)
            self._set_step(self.after_walk, now)
        else:
            self.x += step if target_x > self.x else -step

    def _set_height(self, height: int):
        """Étire Balerino à `height` px, les pieds restant au sol (taille normale : _set_normal_size)."""
        if height == self.rect.height:
            return
        size = (self.rect.width, height)
        self.TEXTURE = pygame.transform.scale(self.stretch_source, size)
        self.TEXTURE_DAMAGE = pygame.transform.scale(self.stretch_damage_source, size)
        self._swap_image(pygame.Surface(size, pygame.SRCALPHA))
        self.rect = self.image.get_rect(x=self.rect.x)
        self.y = GROUND_TOP - height

    def _set_normal_size(self):
        self.TEXTURE = self.rest_texture
        self.TEXTURE_DAMAGE = self.rest_damage_texture
        self._swap_image(self.normal_image)
        self.rect = self.image.get_rect(x=self.rect.x)
        self.y = GROUND_TOP - self.rect.height

    def _stretch(self, now: float, delta_time: float):
        target = self.config.size[1] + CHICKEN_RISE
        self.stretch_height = min(self.stretch_height + self.stretch_speed * delta_time, target)
        self._set_height(round(self.stretch_height))
        if self.stretch_height >= target:
            self._set_step(_Step.WINDUP, now)

    def _windup(self, now: float, delta_time: float):
        if now - self.step_start >= self.chicken_windup:
            self.volleys_fired = 0
            self._set_step(_Step.FIRE, now)

    def _unstretch(self, now: float, delta_time: float):
        normal = self.config.size[1]
        self.stretch_height = max(self.stretch_height - self.stretch_speed * delta_time, normal)
        if self.stretch_height <= normal:
            self._set_normal_size()
            self._set_step(_Step.PAUSE, now)
        else:
            self._set_height(round(self.stretch_height))

    def _fire(self, now: float, delta_time: float):
        if self.volleys_fired > 0 and now - self.step_start < self.chicken_volley_delay:
            return
        if self.volleys_fired >= self.chicken_volleys:
            self._set_step(_Step.UNSTRETCH, now)
            return
        self._fire_chickens()
        self.volleys_fired += 1
        self.step_start = now

    def _fire_chickens(self):
        """Une colonne de poules de chaque côté, du sol jusqu'à CHICKEN_RISE au-dessus des plateformes."""
        chicken_width, chicken_height = self.chicken_size
        lowest = GROUND_TOP - chicken_height
        highest = PLATFORM_TOP - CHICKEN_RISE
        count = self.chickens_per_side
        left_x = self.rect.left - bosses.BALERINO_CHICKEN_OFFSET_X - chicken_width
        right_x = self.rect.right + bosses.BALERINO_CHICKEN_OFFSET_X
        for index in range(count):
            y = lowest + (highest - lowest) * index / (count - 1) if count > 1 else lowest
            self.bullets.add(EnemyBullet(left_x, y, LEFT), EnemyBullet(right_x, y, RIGHT))

    # ------------------------------------------------------------------ 3. grand écart
    def _set_split(self, split: bool):
        """Passe de la taille normale au grand écart (étiré sur toute l'arène), ou l'inverse."""
        self.TEXTURE = self.split_texture if split else self.rest_texture
        self.TEXTURE_DAMAGE = self.split_damage_texture if split else self.rest_damage_texture
        self._swap_image(self.split_image if split else self.normal_image)
        self.rect = self.image.get_rect()

    def _rise(self, now: float, delta_time: float):
        self._show_rest()
        self.y -= self.split_rise_speed * delta_time
        if self.y + self.rect.height < 0:
            self._set_split(True)
            self.x, self.y = ARENA_LEFT, -self.rect.height
            self._set_step(_Step.SPLIT_WAIT, now)

    def _split_wait(self, now: float, delta_time: float):
        if now - self.step_start >= self.split_offscreen_delay:
            self._set_step(_Step.SPLIT_FALL, now)

    def _split_fall(self, now: float, delta_time: float):
        self.y += self.split_fall_speed * delta_time
        # les pieds se posent sur le dessus des plateformes
        if self.y + self.rect.height >= PLATFORM_TOP:
            self.y = PLATFORM_TOP - self.rect.height
            self._set_step(_Step.SPLIT_HOLD, now)

    def _split_hold(self, now: float, delta_time: float):
        if now - self.step_start >= self.split_duration:
            self._set_step(_Step.SPLIT_RISE, now)

    def _split_rise(self, now: float, delta_time: float):
        self.y -= self.split_rise_speed * delta_time
        if self.y + self.rect.height < 0:
            self._set_split(False)
            self.x, self.y = ARENA_CENTER_X - self.rect.width / 2, -self.rect.height
            self._set_step(_Step.LAND, now)

    def _land(self, now: float, delta_time: float):
        self._show_rest()
        self.y += self.split_fall_speed * delta_time
        if self.y + self.rect.height >= GROUND_TOP:
            self.y = GROUND_TOP - self.rect.height
            self._set_step(_Step.PAUSE, now)
