"""Fichiers utilisés par le jeu. Les images sont relatives à assets/img, les sons à assets/sounds."""

# Fonds
BACKGROUND_GREEN = ("background", "fondGameJam.png")
BACKGROUND_RED = ("background", "fondGameJamRed.png")
BACKGROUND_BLUE = ("background", "fondGameJamBlue.png")
MENU_WINDOW_BACKGROUND = ("background", "menu.png")
BOSS_MENU_BACKGROUND = ("placeholder", "placeHolder_menu.png")
DIALOGUE_BACKGROUND = ("placeholder", "placeHolder_dialogue.png")  # boîte de dialogue (cadre gardé, intérieur en mosaïque : menu.DIALOGUE_FRAME)

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

# Tableau spécial (cf. settings/special_level.py)
CUISTOT_LEG_TEXTURE = ("entity", "cuistot_leg.png")  # bas de Cuistot Bongo
CUISTOT_BONGO_TEXTURE = ("entity", "cuistot_bongo.png")  # empilé sur la jambe
OVEN_TEXTURE = ("entity", "oven.png")

# Balerino : À COMPLÉTER, en attendant les sprites manquants utilisent la pose de repos
BALERINO_TEXTURE = ("entity", "balerino.png")  # pose de repos (pause entre deux attaques, portrait du menu)
BALERINO_DAMAGE_TEXTURE = BALERINO_TEXTURE  # TODO : affichée pendant l'invulnérabilité après un coup
# danse : une image par sens de déplacement ; la pirouette entre les deux est calculée (cf. BALERINO_SPIN_*)
BALERINO_DANCE_LEFT_TEXTURE = ("entity", "balerino_left.png")  # va vers la gauche
BALERINO_DANCE_RIGHT_TEXTURE = ("entity", "balerino_right.png")  # va vers la droite
BALERINO_STRETCH_TEXTURE = BALERINO_TEXTURE  # TODO : étiré sur la pointe des pieds avant de tirer les poules
BALERINO_STRETCH_DAMAGE_TEXTURE = BALERINO_TEXTURE  # TODO : étiré et touché
BALERINO_SPLIT_TEXTURE = ("entity", "balerino_stomp.png")  # grand écart (mis à la largeur de l'arène)
BALERINO_SPLIT_DAMAGE_TEXTURE = BALERINO_SPLIT_TEXTURE  # TODO : grand écart touché

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
