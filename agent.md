# Jackass-Parrow — consignes pour l'agent

Jeu de plateforme 2D en Python (pygame-ce + pygame_gui), fait à la main pour une GameJam.
Lancement : `python main.py` depuis la racine (le thème pygame_gui utilise des chemins relatifs).
Projet sous Windows : fins de ligne CRLF dans le dossier de travail, LF dans git (autocrlf).

## Règles à respecter (sauf demande explicite)

- **Ne pas toucher à la physique** (`entity/Player.py`, `settings/player.py`). La gravité est
  ajoutée par frame alors que le déplacement utilise le delta time : c'est voulu, c'est ce qui
  rend le jeu goofy. Ne pas changer les valeurs, ni l'ordre des calculs.
- **Ne rien changer visuellement** sans qu'on le demande. Tester une refacto en comparant le rendu
  au pixel près avec la version précédente (voir « Tests »).
- **Direction artistique :** utiliser des textures (placeholder si besoin) plutôt que des fonds
  transparents, des bordures arrondies ou des styles « UI générique ». Les placeholders sont dans
  `assets/img/placeholder/`. Je les remplace moi-même plus tard, donc pas besoin de respecter
  leurs dimensions.
- **Pas de nombres ni de chaînes magiques :** toute valeur réglable va dans `src/settings/`.
- **Équilibrage :** je modifie moi-même `src/settings/` en dehors des prompts pour équilibrer le
  jeu. Des changements inattendus dans ces fichiers sont donc normaux : ne pas les annuler, ne
  pas les « corriger », et les garder dans les commits.
- **Ressources :** toujours passer par `src/system/assets.py` (cache). Ne jamais charger une
  image ou un son dans une boucle ou par instance. Les surfaces de `assets.image()` sont
  partagées : ne jamais les modifier en place, utiliser `assets.image_copy()`.
- **Bugs volontaires :** ne pas corriger un comportement bizarre qui fait partie du gameplay sans
  le signaler. Le lister plutôt et me demander.
- **Commits :** un message court sur une ligne, par exemple `dev: ...`, `fix: ...`, `refactor: ...`.

## Structure

```
main.py                 point d'entrée
src/app.py              boucle principale (handleEvent / onLoop / render), HUD
src/settings/           TOUS les réglages : display, resources (noms de fichiers), player,
                        enemies, bosses, levels (tableaux + arènes), progression, menu, texts
src/system/
  assets.py             cache images/sons/polices
  GameManager.py        cycle d'une partie (tableaux, boss, fin de partie)
  Progression.py        enchaînement des séries et des boss, level, difficulté
  LevelCollection.py    construit les tableaux de settings/levels.py
  Options.py            OPTIONS : volumes et touches du joueur (options.json), défauts dans settings/controls.py
  Sound.py              accès aux effets sonores
src/entity/
  Player.py             joueur (physique fait main)
  Enemy.py              chevaliers (+ EnemyAngwy), EnemyKamikaze.py (poules-bombes)
  Bullet.py / EnemyBullet.py   tirs ; directions LEFT / RIGHT
  Boss.py               classe de base des boss ; Tom.py, Paya.py, Balerino.py
  bosses.py             create_boss() : toujours créer un boss par là
src/block/              Block (cases de 50px), BlockGroup (apparition des ennemis)
src/gui/Menu.py         menus, fenêtres (Histoire, Classement, Mode Boss), écrans de fin
src/gui/MenuContext.py  menu actif + fenêtre modale active (une modale met le jeu en pause)
src/gui/OptionsWindow.py  fenêtre Options : onglets Général (volumes), Touches, Debug (lance un tableau)
src/gui/DialogueBox.py  boîte de dialogue style RPG Maker (tableau spécial)
assets/themes/theme.json  style pygame_gui (@menu_button, @boss_case, @window...)
```

## Fonctionnement à connaître

- **Progression** (`settings/progression.py`) : série PREMIERE → Balerino → DEUXIEME → Tom →
  TROISIEME → Paya → BONUS → boss suivant... sans fin. Chaque série règle son nombre de
  tableaux, son pool de tableaux et son fond. Le fond d'un boss est celui de la série qui le
  précède. Le level (HUD) compte les tableaux, boss et tableau spécial ; un tableau a
  level + `ENEMY_COUNT_OFFSET` ennemis (limité par ses blocs spawnable).
- **Boss** : la classe de base gère l'affichage, les PV, l'invulnérabilité après un coup, la mort
  et l'outro. Les classes filles redéfinissent `attack`, `on_hit`, `get_obstacles`,
  `render_extra` et `setup_hard_mode`. À partir de la 2e rencontre, un boss passe en HARD : le
  dictionnaire `hard` de sa config remplace ses valeurs normales. C'est prévu mais encore vide.
- **Ajouter un boss** : `BossId` + entrée dans `BOSSES` (`settings/bosses.py`), une classe fille
  dans `entity/`, une ligne dans `entity/bosses.py`, et éventuellement `BOSS_CYCLE` et
  `BOSS_MENU_ORDER`.
- **Mode Boss** : fenêtre bloquante avec une case par boss. Le portrait est une `PassiveImage`
  (elle ne capte pas la souris, pour que le survol reste sur le bouton). Fond : `boss_mode_background`.
- `pygame_gui` reçoit `UI_TIME_DELTA = 60` : volontaire, les transitions de survol sont instantanées.
- La gestion des modales est fragile : `App.render()` remet la modale d'intro ou l'efface à chaque
  frame tant qu'un boss existe, et l'écran Game Over est dessiné deux fois. Ne pas la
  « simplifier » sans vérifier le rendu.

## Tests

- Il n'y a pas de tests unitaires. On vérifie en headless (`SDL_VIDEODRIVER=dummy`,
  `SDL_AUDIODRIVER=dummy`), avec une horloge simulée (`pygame.time.get_ticks`, `time.time`,
  `Clock.tick`), `random.seed`, et des touches scriptées via `pygame.key.get_pressed`.
- Pour une refacto : comparer le md5 de chaque frame entre l'ancienne et la nouvelle version.
- Tir debug : I + O + P (un mur de tirs) permet d'avancer vite dans les tableaux et les boss.

## Économiser des tokens

- Lire ce fichier et la structure ci-dessus avant d'explorer : ne pas relire tout le projet.
- Les réglages sont dans `src/settings/` : commencer par là pour toute demande d'équilibrage ou
  de texte.
- `doc/*.svg` sont gros (> 150 Ko) et obsolètes : ne pas les lire.
- Ignorer `.venv/`, `__pycache__/`, `uv.lock`, `assets/sounds/`.
- Réponses courtes, en français ; pas de récapitulatif détaillé de chaque fichier modifié.
