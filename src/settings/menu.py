from src.settings.display import HEIGHT, WIDTH

# Boutons du menu principal
BUTTON_SIZE = (220, 80)
BUTTONS_TOP = HEIGHT // 2
BUTTONS_SPACING = 70

# Illustrations du menu principal (Tom à gauche, le héros à droite)
ILLUSTRATION_HEIGHT_RATIO = 1.4  # hauteur = HEIGHT / ratio
TOM_ILLUSTRATION_MARGIN = 50
HERO_ILLUSTRATION_X_RATIO = 0.45  # centre x = largeur / ratio
TITLE_Y = HEIGHT // 3
TITLE_SHADOW_OFFSET = 5

# Fenêtres Histoire / Classement
TEXT_WINDOW_RECT = ((WIDTH // 4, HEIGHT // 6), (WIDTH // 2, HEIGHT // 1.5))
WINDOW_BUTTON_SIZE = (180, 70)
WINDOW_PADDING = 20

# Fenêtre "Mode Boss"
BOSS_WINDOW_SIZE = (760, 480)
BOSS_CASE_SIZE = (200, 300)
BOSS_CASES_TOP = 40
BOSS_PORTRAIT_PADDING = 12
BOSS_NAME_HEIGHT = 50  # espace réservé au nom en bas de chaque case

# Écran de fin de partie
END_FRAME_RATIO = 1.3  # taille du cadre = écran / ratio
INPUT_BOX_SIZE = (200, 50)
INPUT_BOX_Y_RATIO = 1.6  # y = HEIGHT / ratio
INPUT_TEXT_PADDING = 5
INPUT_BORDER_WIDTH = 2
SAVE_BUTTON_Y_RATIO = 1.3
SAVE_BUTTON_RADIUS = 10

# Écrans d'intro / de victoire des boss
BOSS_INTRO_PADDING = 60
BOSS_VICTORY_PADDING = 20

# HUD
HUD_SCORE_POS = (10, 10)
HUD_HEALTH_POS = (10, 40)
