from src.block.Block import Block
from src.block.BlockGroup import BlockGroup
from src.settings import levels


class LevelCollection:
    """Construit les tableaux décrits dans settings/levels.py dans un BlockGroup."""

    def __init__(self, blockGroup: BlockGroup):
        self.blocks = blockGroup
        self.playerSpawn = (0, 0)

    def build_tableau(self, lstBloc: list, background: tuple = None):
        """`background` : fond affiché derrière le tableau, il donne sa couleur à l'herbe (levels.GRASS_COLORS)."""
        grass_color = levels.GRASS_COLORS.get(background)
        for x, y, width, height in levels.COMMON_BLOCKS:
            self.blocks.add(Block(x, y, width, height, grass_color=grass_color))

        for bloc in lstBloc:
            if len(bloc) == 2:
                self.playerSpawn = (bloc[0] * levels.TILE_SIZE, bloc[1] * levels.TILE_SIZE)
                continue
            x, y, width, height, *flags = bloc
            spawnable = flags[0] if len(flags) > 0 else False
            transparent = flags[1] if len(flags) > 1 else False
            self.blocks.add(Block(x, y, width, height, spawnable=spawnable, transparent=transparent,
                                  grass_color=grass_color))

    def load(self, levelId: int, background: tuple = None):
        """Charge un tableau par son id (à partir de 1)."""
        self.build_tableau(levels.LEVELS[levelId - 1], background)

    def load_arena(self, arena: list, player_spawn: tuple, background: tuple = None):
        """Charge l'arène d'un boss ; player_spawn est une case (x, y)."""
        self.build_tableau(arena, background)
        self.playerSpawn = (player_spawn[0] * levels.TILE_SIZE, player_spawn[1] * levels.TILE_SIZE)
