from src.settings import resources
from src.settings.display import CAT_COMIC_FONT, DIMBO_FONT, HEIGHT, WIDTH

# Boutons du menu principal
BUTTON_SIZE = (220, 80)
BUTTONS_TOP = HEIGHT // 2
BUTTONS_SPACING = 70
ILLUSTRATION_BUTTON_GAP = 10  # px entre une illustration et le bouton placé dessous (Classement, Quitter)

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

# Fenêtre Options (onglets Général / Touches / Debug)
OPTIONS_WINDOW_SIZE = (1000, 690)
OPTIONS_TAB_SIZE = (220, 70)
OPTIONS_TABS_TOP = 20
OPTIONS_TAB_SPACING = 20
OPTIONS_CONTENT_TOP = 105  # haut de la zone sous les onglets
OPTIONS_GAP = 20
OPTIONS_LABEL_WIDTH = 260
OPTIONS_ROW_HEIGHT = 50
OPTIONS_HINT_HEIGHT = 40
# Général
OPTIONS_GENERAL_TOP = 30
OPTIONS_SLIDER_WIDTH = 400
OPTIONS_SLIDER_STEP = 5  # % par clic sur les flèches de la barre
OPTIONS_VALUE_WIDTH = 90
# Touches
OPTIONS_KEYS_TOP = 10
OPTIONS_KEY_ROW_HEIGHT = 54
OPTIONS_KEY_ROW_GAP = 8
OPTIONS_KEY_BUTTON_WIDTH = 200
OPTIONS_RESET_SIZE = (200, 60)  # boutons bois : garder ~ les proportions de l'image (923 x 276)
# Debug : grille de miniatures des tableaux
DEBUG_GRID = (3, 3)  # colonnes, lignes
DEBUG_CASE_SIZE = (200, 150)
DEBUG_CASE_GAP = (24, 8)
DEBUG_CASE_PADDING = 8  # entre le haut de la case et la miniature
DEBUG_CASE_FONT_SIZE = 24  # nom du tableau sous la miniature
DEBUG_THUMBNAIL_SIZE = (176, 110)
DEBUG_THUMBNAIL_BORDER = 5  # px du cadre de couleur
DEBUG_DIFFICULTY_COLORS = {"normal": (40, 200, 60), "mid": (240, 210, 40), "hard": (220, 40, 40)}
DEBUG_UNKNOWN_DIFFICULTY_COLOR = (150, 150, 150)
DEBUG_ARROW_SIZE = (150, 50)
DEBUG_ARROW_MARGIN = 12  # px entre la grille et les flèches
DEBUG_ARROW_ZONE_GAP = 4  # px entre la grille et la zone cliquable de chaque flèche (toute la bande sur le côté)
DEBUG_THUMBNAIL_BACKGROUND = resources.BACKGROUND_GREEN  # fond de toutes les miniatures
DEBUG_SPAWNABLE_TINT = (255, 225, 0, 70)  # RGBA posé sur les blocs spawnable des miniatures
