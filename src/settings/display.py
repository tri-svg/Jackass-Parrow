WIDTH = 1280
HEIGHT = 800
FPS = 60

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
TITLE_FONT_SIZE = 80
BUTTON_FONT_SIZE = 50
BOSS_INTRO_FONT_SIZE = 52
BOSS_WIN_FONT_SIZE = 48
