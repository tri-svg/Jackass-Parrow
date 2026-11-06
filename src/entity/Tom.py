import random

from src.block.Block import Block
from src.block.BlockGroup import BlockGroup
from src.entity.Boss import Boss
from src.entity.Bullet import LEFT
from src.entity.EnemyBullet import EnemyBullet
from src.entity.Player import Player
from src.settings import bosses
from src.settings.bosses import BossDifficulty, BossId


class Tom(Boss):
    """
    Tom de l'Abbaye : lance des poules à hauteur du joueur et se protège derrière
    des boucliers qui changent à chaque coup encaissé. S'énerve quand il a peu de PV.
    """

    BOSS_ID = BossId.TOM

    def __init__(self, game_surface, enemy_bullets, difficulty: BossDifficulty = BossDifficulty.NORMAL,
                 background: tuple = None):
        super().__init__(game_surface, enemy_bullets, difficulty, background)
        self.index_hole = 0
        self.attackSpeed = bosses.TOM_ATTACK_SPEED
        self.angryAttackSpeed = bosses.TOM_ANGRY_ATTACK_SPEED
        self.timeLastBullet = 0
        self.bouclier = BlockGroup(self.game_surface)

    def setup_hard_mode(self):
        self.attackSpeed = bosses.TOM_HARD.get("attack_speed", self.attackSpeed)
        self.angryAttackSpeed = bosses.TOM_HARD.get("angry_attack_speed", self.angryAttackSpeed)

    def attack(self, player: Player, now: float):
        if now - self.timeLastBullet > self.attackSpeed / 1000.0:
            self.timeLastBullet = now
            self.bullets.add(EnemyBullet(self.rect.midleft[0] - bosses.TOM_BULLET_OFFSET_X, player.rect.y, LEFT))

    def on_hit(self):
        self.generateBouclier()
        if self.health <= bosses.TOM_ANGRY_HEALTH:  # colère
            self.attackSpeed = self.angryAttackSpeed

    def get_obstacles(self) -> list:
        return self.bouclier.sprites()

    def render_extra(self):
        self.bouclier.render()

    def generateBouclier(self):
        self.bouclier.empty()
        choice = list(range(bosses.TOM_SHIELD_COUNT))
        # évite de laisser 2 fois le même trou de bouclier d'affilée
        choice.remove(self.index_hole)
        self.index_hole = random.choice(choice)

        width, height = bosses.TOM_SHIELD_SIZE
        for bouclier_index in choice:
            row = bosses.TOM_SHIELD_BOTTOM_ROW - bouclier_index * bosses.TOM_SHIELD_SPACING
            self.bouclier.add(Block(bosses.TOM_SHIELD_COLUMN, row, width, height))
