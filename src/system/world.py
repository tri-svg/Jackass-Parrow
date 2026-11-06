from enum import Enum
from random import randint

from src.system.GameConfig import LEVEL_POOLS, WorldType


class BossType(Enum):
    BALERINO = 1
    TOM = 2
    PAYA = 3


class World:
    def __init__(self, level_collection, world_index: WorldType, nb_levels: int | None, danger_level=0):
        self.world_type_index = world_index
        self.level_collection = level_collection
        self.nb_levels = nb_levels
        self.current_level = 0
        self.danger_level = danger_level

    @property
    def is_endless(self) -> bool:
        return self.nb_levels is None

    def get_next_level_id(self, last_level_id: int) -> int:
        """Tire un tableau au hasard dans le pool du monde, différent du précédent."""
        if self.world_type_index not in LEVEL_POOLS:
            # avant : boucle infinie (= freeze) si le monde n'avait pas de tableaux
            raise NotImplementedError(f"Le monde {self.world_type_index.name} n'a pas de tableaux définis.")
        low, high = LEVEL_POOLS[self.world_type_index]
        level_id = randint(low, high)
        while level_id == last_level_id:
            level_id = randint(low, high)
        self.current_level += 1
        self.danger_level += 1
        return level_id
