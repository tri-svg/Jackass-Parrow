from src.system.GameConfig import DIFFICULTY, WorldType, worlds_config
from src.system.world import World


class WorldManager:
    def __init__(self, difficulty: DIFFICULTY, level_collection):
        self.__difficulty = difficulty
        self.__current_world_index = 0
        self.level_collection = level_collection
        self.danger_offset = 0
        self.last_level_id = -1
        self.current_world: World = None

        self.set_current_world()

    def _worlds(self) -> list:
        return worlds_config[self.__difficulty]

    def set_current_world(self):
        config = self._worlds()[self.__current_world_index]
        self.current_world = World(
            self.level_collection,
            config["monde"],
            config["nb_level"],
            config.get("danger", 0) + self.danger_offset,
        )

    def get_current_world(self) -> World:
        return self.current_world

    def get_danger_level(self) -> int:
        return self.current_world.danger_level

    def get_current_level(self) -> int:
        return self.current_world.current_level

    def get_world_max_level(self) -> int | None:
        return self.current_world.nb_levels

    def get_current_world_type(self) -> WorldType:
        return self.current_world.world_type_index

    def is_endless(self) -> bool:
        return self.current_world.is_endless

    def next_world(self):
        # Si le monde actuel est le dernier, on recommence sur le premier monde de la difficulté
        if self.__current_world_index + 1 >= len(self._worlds()):
            self.__current_world_index = 0
            self.danger_offset += 3
        else:
            self.__current_world_index += 1
        self.set_current_world()

    def get_next_level_id(self) -> int:
        self.last_level_id = self.current_world.get_next_level_id(self.last_level_id)
        return self.last_level_id
