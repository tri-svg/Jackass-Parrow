"""
Tableau spécial : joué une seule fois par partie, après le premier combat contre le boss
progression.SPECIAL_LEVEL_AFTER_BOSS.
Disposition des blocs : settings/levels.py (SPECIAL_LEVEL) ; textures : settings/resources.py.
Le joueur va toucher le cuistot : dialogue (texts.CUISTOT_DIALOGUE), soin, puis série suivante.
"""

from src.settings import display, resources

BACKGROUND = resources.BACKGROUND_GREEN  # fond du tableau (et couleur de l'herbe) ; None = fond de la série qui suit
CUISTOT_HEAL = 2  # PV rendus par le cuistot (sans dépasser settings/player.py MAX_HEALTH)
CUISTOT_HEAL_PAGE = 1  # page du dialogue (texts.CUISTOT_DIALOGUE, à partir de 0) où les PV sont rendus
CUISTOT_PORTRAIT = resources.CUISTOT_BONGO_TEXTURE  # portrait dans la boîte de dialogue

# Cuistot Bongo : la jambe en bas, le bongo empilé dessus, posé sur la bande du bas
CUISTOT_CENTER_X = display.WIDTH // 2  # px, centre horizontal du cuistot
CUISTOT_STACK_OVERLAP = 0  # px de recouvrement entre la jambe et le bongo (> 0 : le bongo s'enfonce)

# Four posé par terre à côté du cuistot
OVEN_SIDE = 1  # 1 : à droite du cuistot ; -1 : à gauche
OVEN_GAP = 10  # px entre le cuistot et le four
