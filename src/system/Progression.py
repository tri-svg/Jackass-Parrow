from collections import Counter
from random import randint

from src.settings import progression
from src.settings.bosses import BossDifficulty, BossId
from src.settings.progression import SeriesType


class Progression:
    """
    Suit l'avancement d'une partie (cf. settings/progression.py).

    Les étapes paires sont des séries de tableaux, les impaires des boss :
        étape 0 : série PREMIERE      étape 1 : boss BOSS_CYCLE[0]
        étape 2 : série DEUXIEME      étape 3 : boss BOSS_CYCLE[1]
        étape 4 : série TROISIEME     étape 5 : boss BOSS_CYCLE[2]
        étape 6 : série BONUS         étape 7 : boss BOSS_CYCLE[0] (HARD) ...
    """

    def __init__(self):
        self.stage = 0
        self.levels_done = 0  # tableaux joués dans la série en cours
        self.danger_level = progression.DANGER_START
        self.last_level_id = -1
        self.boss_encounters = Counter()  # BossId -> nombre de rencontres (combat en cours inclus)

    # ------------------------------------------------------------------ séries
    @property
    def is_boss_stage(self) -> bool:
        return self.stage % 2 == 1

    def series_type(self) -> SeriesType:
        """Série en cours, ou série qui précède le boss en cours."""
        series_index = self.stage // 2
        if series_index < len(progression.SERIES_ORDER):
            return progression.SERIES_ORDER[series_index]
        return SeriesType.BONUS

    def _series(self) -> dict:
        return progression.SERIES[self.series_type()]

    def series_length(self) -> int:
        return self._series()["level_count"]

    def background(self) -> tuple:
        """Fond de la série en cours (ou de la série précédente pendant un boss)."""
        return self._series()["background"]

    def has_next_level(self) -> bool:
        """Reste-t-il des tableaux dans la série en cours ?"""
        return not self.is_boss_stage and self.levels_done < self.series_length()

    # ------------------------------------------------------------------ boss
    def current_boss(self) -> BossId:
        boss_index = self.stage // 2
        return progression.BOSS_CYCLE[boss_index % len(progression.BOSS_CYCLE)]

    def current_boss_difficulty(self) -> BossDifficulty:
        if self.boss_encounters[self.current_boss()] >= progression.BOSS_HARD_FROM_ENCOUNTER:
            return BossDifficulty.HARD
        return BossDifficulty.NORMAL

    # ------------------------------------------------------------------ avancement
    def next_level_id(self) -> int:
        """Tire le prochain tableau (différent du précédent) et augmente le danger."""
        low, high = self._series()["level_ids"]
        level_id = randint(low, high)
        while level_id == self.last_level_id and low != high:
            level_id = randint(low, high)
        self.last_level_id = level_id
        self.levels_done += 1
        self.danger_level += 1
        return level_id

    def next_stage(self):
        if self.is_boss_stage:
            self.danger_level += progression.DANGER_BONUS_AFTER_BOSS
        self.stage += 1
        self.levels_done = 0
        if self.is_boss_stage:
            self.boss_encounters[self.current_boss()] += 1
