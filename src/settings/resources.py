"""Fichiers utilisés par le jeu. Les images sont relatives à assets/img, les sons à assets/sounds."""

# Fonds
BACKGROUND_GREEN = ("background", "fondGameJam.png")
BACKGROUND_RED = ("background", "fondGameJamRed.png")
BACKGROUND_BLUE = ("background", "fondGameJamBlue.png")
MENU_WINDOW_BACKGROUND = ("background", "menu.png")
BOSS_MENU_BACKGROUND = ("placeholder", "placeHolder_menu.png")

# Blocs
BLOCK_TEXTURE = ("block", "block.png")
DIRT_TEXTURE = ("block", "dirt.png")

# Joueur
PLAYER_TEXTURE = ("player", "player.png")
PLAYER_WALK_TEXTURE = ("player", "playerWalk.png")
PLAYER_SHIELD_TEXTURE = ("player", "player_shield.png")
PLAYER_FIRING_TEXTURE = ("player", "player_firing.png")
PLAYER_DEAD_TEXTURE = ("player", "player_dead.png")
PLAYER_HD_TEXTURE = ("player", "playerHD.png")  # menu principal

# Ennemis et projectiles
BULLET_TEXTURE = ("entity", "bullet.png")
CHICKEN_TEXTURE = ("entity", "chicken.png")
KNIGHT_TEXTURE = ("entity", "chevalier.png")
KNIGHT_ANGRY_TEXTURE = ("entity", "chevalier_angwy.png")
KNIGHT_DEAD_TEXTURE = ("entity", "chevalierMort.png")
KAMIKAZE_WALK_TEXTURES = (("entity", "chicken_bomb.png"), ("entity", "chicken_bomb_walk.png"))
KAMIKAZE_EXPLOSION_TEXTURES = tuple(("entity", f"explosion_{i}.png") for i in range(1, 5))

# Boss
TOM_TEXTURE = ("entity", "tom.png")
TOM_DAMAGE_TEXTURE = ("entity", "tomDamage.png")
BOSS_PLACEHOLDER_TEXTURE = ("placeholder", "placeHolder_boss.png")

# Sons
SOUND_SHOT = "tir.wav"
SOUND_BUTTON = "button.wav"
SOUND_HURT = "hurt.wav"
SOUND_KNIGHT_HURT = "knight_hurt.wav"
SOUND_ENEMY_FIRE = "enemyFire.wav"
SOUND_PARRY = "parade.wav"

# Musiques
MUSIC_MAIN = "mainTheme.mp3"
MUSIC_BOSS = "bossTheme.mp3"
MUSIC_VOLUME = 0.15

# Thème pygame_gui (relatif à assets/) et fichier des scores (relatif à la racine du projet)
GUI_THEME = ("themes", "theme.json")
SCORES_FILE = "scores.json"
