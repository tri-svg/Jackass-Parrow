from enum import Enum

# Résolution du jeu : tout est calculé et dessiné à cette taille, puis agrandi à la taille de la fenêtre
# (cf. system/Display.py). Ne pas la changer pour adapter le jeu à un écran : régler la fenêtre.
WIDTH = 1280
HEIGHT = 800
FPS = 60


class DisplayMode(Enum):
    WINDOWED = "fenetre"
    BORDERLESS = "sans_bordure"  # fenêtre sans bordure à la taille de l'écran


WINDOW_TITLE = "Jackass-Parrow"
# Tailles de fenêtre proposées (seules celles qui tiennent sur l'écran sont affichées) ; en 16:9 le jeu
# (16:10) a des bandes noires sur les côtés
WINDOW_SIZES = [(1280, 720), (1280, 800), (1366, 768), (1440, 900), (1600, 900), (1680, 1050), (1920, 1080),
                (1920, 1200), (2560, 1440), (3840, 2160)]
DEFAULT_DISPLAY_MODE = DisplayMode.WINDOWED
DEFAULT_WINDOW_SIZE = (WIDTH, HEIGHT)
MIN_WINDOW_SIZE = (640, 400)  # taille minimale de la fenêtre
# Rendu SDL sous Windows : Direct3D 9 (défaut de SDL) donne un écran noir quand la fenêtre est moins
# haute que le jeu ; "direct3d11" ou "opengl" fonctionnent (SDL en prend un autre s'il est indisponible)
WINDOWS_RENDER_DRIVER = "direct3d11"
SCALE_QUALITY = "linear"  # agrandissement de l'image : "linear" (lissé) ou "nearest" (pixels nets)

# Délai max pris en compte entre deux frames (secondes). Évite que le joueur / les tirs
# traversent les blocs après un ralentissement ponctuel. Sans effet au-dessus de 20 FPS.
MAX_DELTA_TIME = 1 / 20

# Temps écoulé donné à pygame_gui à chaque frame : volontairement énorme pour que
# les transitions du thème (survol des boutons) soient instantanées.
UI_TIME_DELTA = 60

# Couleurs
WHITE = (255, 255, 255)
TITLE_SHADOW_COLOR = (50, 50, 50)
INPUT_ACTIVE_COLOR = (0, 150, 0)
SAVE_BUTTON_COLOR = (0, 150, 0)
SAVE_BUTTON_HOVER_COLOR = (0, 200, 0)
OVERLAY_ALPHA = 150  # fond noir semi-transparent des écrans de fin / intro / victoire

# Polices (fichiers dans assets/fonts)
CAT_COMIC_FONT = "Cat Comic.ttf"
DIMBO_FONT = "Dimbo Regular.ttf"

HUD_FONT_SIZE = 36
HUD_LEVEL_FONT_SIZE = 24  # compteur de niveau
TITLE_FONT_SIZE = 80
BUTTON_FONT_SIZE = 50
BOSS_INTRO_FONT_SIZE = 52
BOSS_WIN_FONT_SIZE = 48
