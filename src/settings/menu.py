from src.settings.display import CAT_COMIC_FONT, DIMBO_FONT, HEIGHT, WIDTH

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
HUD_LEVEL_MARGIN = (10, 10)  # px depuis le coin haut-droit (compteur de niveau, sans fond)
HUD_HEALTH_POS = (10, 40)

# Boîte de dialogue (style RPG Maker, en bas de l'écran ; textes : settings/texts.py)
DIALOGUE_HEIGHT = 160  # px (posée sur la bande du bas du tableau spécial)
DIALOGUE_MARGIN = 20  # px entre la boîte et les bords de l'écran
DIALOGUE_PADDING = 16  # px entre le cadre et le contenu
DIALOGUE_FRAME = 4  # px : épaisseur du cadre dans l'image de fond (gardé tel quel, l'intérieur est répété)
DIALOGUE_PORTRAIT_SIZE = 128  # px, portrait carré à gauche
DIALOGUE_NAME_FONT = CAT_COMIC_FONT
DIALOGUE_NAME_FONT_SIZE = 34
DIALOGUE_NAME_COLOR = (255, 210, 80)
DIALOGUE_NAME_GAP = 4  # px entre le nom et le texte
DIALOGUE_TEXT_FONT = DIMBO_FONT  # Cat Comic n'a pas les lettres accentuées
DIALOGUE_TEXT_FONT_SIZE = 32
DIALOGUE_HINT_FONT = CAT_COMIC_FONT  # sans accents, comme le nom
DIALOGUE_HINT_FONT_SIZE = 22
DIALOGUE_AUTO_ADVANCE = 10  # secondes avant de passer seul à la page suivante
