import json

import pygame

from src.settings import controls
from src.settings.controls import Action
from src.system import assets


class Options:
    """
    Options du joueur (volumes, touches), lues au lancement et enregistrées à chaque changement
    dans resources.OPTIONS_FILE. Une seule instance : OPTIONS.
    """

    def __init__(self):
        self.music_volume = controls.DEFAULT_MUSIC_VOLUME
        self.sound_volume = controls.DEFAULT_SOUND_VOLUME
        self.bindings = {action: list(keys) for action, keys in controls.DEFAULT_BINDINGS.items()}
        self.load()

    # ------------------------------------------------------------------ fichier
    def load(self):
        try:
            with open(assets.OPTIONS_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return
        self.music_volume = data.get("music_volume", self.music_volume)
        self.sound_volume = data.get("sound_volume", self.sound_volume)
        for action in Action:
            keys = data.get("bindings", {}).get(action.name)
            if isinstance(keys, list) and len(keys) == controls.BINDING_SLOTS:
                self.bindings[action] = keys

    def save(self):
        data = {
            "music_volume": self.music_volume,
            "sound_volume": self.sound_volume,
            "bindings": {action.name: keys for action, keys in self.bindings.items()},
        }
        with open(assets.OPTIONS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------------------ volumes
    def apply_volumes(self):
        """Applique les volumes à la musique et aux effets sonores (mixer initialisé)."""
        pygame.mixer.music.set_volume(controls.MUSIC_VOLUME_MAX * self.music_volume / 100)
        assets.set_sound_volume(controls.SOUND_VOLUME_MAX * self.sound_volume / 100)

    def set_music_volume(self, percent: int):
        self.music_volume = percent
        self.apply_volumes()
        self.save()

    def set_sound_volume(self, percent: int):
        self.sound_volume = percent
        self.apply_volumes()
        self.save()

    # ------------------------------------------------------------------ touches
    def pressed(self, keys, action: Action) -> bool:
        """Une des touches de l'action est-elle enfoncée ?"""
        return any(keys[key] for key in self.bindings[action] if key is not None)

    def primary_pressed(self, keys, action: Action) -> bool:
        """Seulement la touche principale (Player garde ce comportement d'origine à certains endroits)."""
        key = self.bindings[action][0]
        return key is not None and keys[key]

    def key_name(self, action: Action, slot: int = 0) -> str:
        key = self.bindings[action][slot]
        return pygame.key.name(key).upper() if key is not None else ""

    def bind(self, action: Action, slot: int, key):
        """Assigne `key` (None : vide) ; la touche est retirée des autres cases qui l'utilisaient."""
        if key is not None:
            for keys in self.bindings.values():
                for index, bound in enumerate(keys):
                    if bound == key:
                        keys[index] = None
        self.bindings[action][slot] = key
        self.save()

    def reset_bindings(self):
        self.bindings = {action: list(keys) for action, keys in controls.DEFAULT_BINDINGS.items()}
        self.save()


OPTIONS = Options()
