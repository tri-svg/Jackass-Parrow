"""
Joueur. /!\\ Physique "fait main" : la gravité est ajoutée par frame alors que les
déplacements utilisent le delta time. C'est ce qui donne le côté goofy, on n'y touche pas.
"""

SPAWN_X = 200
SPAWN_Y = 200
HEALTH = 5  # PV au début de la partie
MAX_HEALTH = 5  # PV maximum (affiché dans le HUD ; les soins ne vont pas au-delà)

BASE_SPEED = 400  # px/s
JUMP_FORCE = 1250  # px/s vers le haut au décollage
GRAVITY_STEP = 60  # ajouté à la vitesse verticale à chaque frame passée en l'air
MAX_FALL_SPEED = 1000  # vitesse imposée par la descente rapide
KNOCKBACK_FORCE = 1500  # recul après un tir
KNOCKBACK_DAMPING = 0.85  # multiplicateur du recul à chaque frame
KNOCKBACK_MIN = 0.1  # en dessous, le recul est annulé
BLOCK_SIDE_TOLERANCE = 2  # px : marge pour ne pas se bloquer contre le bord supérieur d'un bloc

BULLET_DELAY = 1000  # ms entre deux tirs
BULLET_OFFSET_Y = 50  # hauteur de sortie du tir depuis le haut du sprite
FIRING_ANIMATION_TIME = 200  # ms
WALK_ANIMATION_PERIOD = 300  # ms pour un cycle complet de marche (2 images)
INVINCIBILITY_TIME = 600  # ms après avoir été touché
BLINK_PERIOD = 20  # ms (clignotement pendant l'invincibilité)
BLINK_ALPHAS = (100, 0)

# Tir de debug (I + O + P) : un mur de tirs des deux côtés de l'écran
DEBUG_SHOT_DELAY = BULLET_DELAY // 4
DEBUG_SHOT_Y_RANGE = (10, 1200, 20)  # range(début, fin, pas)
DEBUG_SHOT_LEFT_X = 10
DEBUG_SHOT_RIGHT_X = 1250
