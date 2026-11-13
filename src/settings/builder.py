"""Réglages de l'éditeur de tableaux (builder.py, à la racine) : outil de dev, pas utilisé par le jeu."""

from src.settings import resources

PANEL_WIDTH = 420  # px : panneau à droite du tableau (code Python + boutons)
# La fenêtre est réduite pour tenir sur l'écran : None = automatique, sinon échelle forcée (ex. 0.7)
WINDOW_SCALE = None
SCREEN_FILL = 0.9  # en automatique : part max de la largeur / hauteur de l'écran occupée par la fenêtre
FPS = 60
NEW_LEVEL_NAME = "LEVEL_NEW"  # nom de la variable dans le code affiché
DEFAULT_PLAYER_SPAWN = (12, 14)  # case (x, y) du joueur pour un tableau vide
BACKGROUNDS = [resources.BACKGROUND_GREEN, resources.BACKGROUND_BLUE, resources.BACKGROUND_RED]

# Affichage
FONT_NAME = "consolas"  # police système (monospace pour le code)
FONT_SIZE = 16
LINE_HEIGHT = 18
PANEL_PADDING = 12
PANEL_COLOR = (30, 30, 34)
TEXT_COLOR = (230, 230, 230)
HELP_COLOR = (150, 150, 160)
BUTTON_SIZE = (125, 34)
BUTTON_GAP = 8
BUTTON_COLOR = (90, 55, 20)
BUTTON_HOVER_COLOR = (140, 85, 30)
GRID_COLOR = (0, 0, 0, 40)  # RGBA des lignes de la grille
DRAG_COLOR = (255, 255, 255, 90)  # RGBA du bloc en cours de création
SPAWNABLE_TINT = (255, 225, 0, 90)  # RGBA posé sur les blocs spawnable
TRANSPARENT_COLOR = (80, 160, 255)  # contour des blocs transparents
TRANSPARENT_BORDER = 3
HOVER_BORDER_COLOR = (255, 255, 255)  # contour du bloc sous la souris
HOVER_BORDER = 2
MESSAGE_DURATION = 2.0  # secondes d'affichage d'un message ("copié", ...)
UNDO_LIMIT = 100
