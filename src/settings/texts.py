GAME_TITLE = "Jackass-Parrow"

# Menu principal
BUTTON_START = "Lancer"
BUTTON_BOSS_MODE = "Mode Boss"
BUTTON_LORE = "Histoire"
BUTTON_LEADERBOARD = "Classement"
BUTTON_QUIT = "Quitter"
BUTTON_CLOSE = "Fermer"

LORE = """
            Quand il était jeune, Jackass-Parrow n'était pas le pirate le plus agile du navire.
            C'est pour cela que ses parents lui ont greffé un canon scié sur l'arrière-train en guise de cadeau d'anniversaire.
            Malheureusement, celui-ci fut exclu de sa fratrie lorsqu'il tira accidentellement dans la tête de son père en voulant s'étirer.
            Jackass-Parrow passa donc le reste de son enfance dans une jungle, élevé par une tribu indigène.

            Aujourd'hui, menacé par Tom de l'Abbaye et ses chevaliers, Jackass-Parrow est prêt à tout pour défendre ceux qui l'ont recueilli.
            """

LEADERBOARD_LINE = "{rank}. {pseudo} - {score}<br>"
LEADERBOARD_SIZE = 10

# HUD
HUD_SCORE = "Score: {score}"
HUD_HEALTH = "Vie: {health}/{max_health}"
HUD_LEVEL = "Level {level}"  # en haut à droite

# Boîtes de dialogue
DIALOGUE_NEXT_HINT = "Espace : suivant"
CUISTOT_NAME = "Cuistot Bongo"
CUISTOT_DIALOGUE = [  # une boîte par entrée ; les PV sont rendus à la page special_level.CUISTOT_HEAL_PAGE
    "Tu as terrassé Tom, mais ton combat contre les troupes de l'Abbaye n'est pas fini...",
    "Prends cette pizza avant de reprendre ta route, tu en auras grand besoin ! (+2 PV restaurés)",
]

# Fin de partie
GAME_OVER = "Game Over"
END_SCORE = "Score : {score}"
BUTTON_SAVE = "Enregistrer"

# Boss ({title} est remplacé par le titre du boss, cf. settings/bosses.py)
BOSS_INTRO = [
    "Le combat final approche",
    "Préparez-vous à combattre le grand...",
    "{title}",
]
BOSS_VICTORY = [
    "Victoire !",
    "Vous avez vaincu l'abominable",
    "",
    "{title}",
    "",
    "Merci d'avoir joué!",
]
