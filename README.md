# A2026-6GEI608-lab2

Laboratoire 2 de 6GEI608, Intelligence artificielle et reconnaissance des formes (UQAC).

- Équipe : voir `EQUIPE.txt`
- Dépôt : https://github.com/Antoine93/A2026-6GEI608-lab2

---

## Partie 1 : résolution du 8-puzzle avec l'algorithme A*

### Utilisation

Similaire au fonctionnement du lab 1, le programme (python main.py) demande le fichier d'entrée (ex. data/input-Ex1/Ex1-1.txt) puis l'algorithme : bfs, dfs, ids, a_star (distance de Manhattan), a_star_misplaced (tuiles mal placées) ou a_star_max (maximum des deux).
Il vérifie d'abord que le puzzle est solvable (parité des inversions), puis exécute la recherche 10 fois.

Pour chaque exécution, un fichier est écrit dans `results/<algo>/<input>_runNN.txt` :
- à partir de la première ligne (résultat lab 1) : numéro_itération \t taille_de_frontière SAUF pour A* (lab 2), une 3ᵉ colonne donne la taille de la liste des états explorés (numéro_itération \t taille_de_frontière \t taille_des_explorés) ;
- avant-dernière ligne : nombre total d'itérations (états dépilés) ;
- dernière ligne : temps d'exécution de la fonction de recherche.

## Algorithme A*

- **Fonction d'évaluation :** f(n) = g(n) + h(n), où g est le coût pour arriver à n (chaque coup coûte 1 dans notre 8-puzzle) et h l'heuristique.
- **Heuristiques utilisées :** trois heuristiques que nous avons expérimentées, choisies par le paramètre h de solve_puzzle_a_star(start, x, y, h) :
  - **distance de Manhattan** (manhattan, par défaut) : la somme, pour chaque tuile (case vide exclue), de la distance en lignes et en colonnes entre sa position et sa position cible
  - **tuiles mal placées** (misplaced_tiles) : le nombre de tuiles (case vide exclue) qui ne sont pas à leur position cible
  - **maximum des deux** (`max_heuristic`) : pour chaque état, on calcule les deux valeurs précédentes et on garde la plus grande, `h(n) = max(Manhattan(n), tuiles mal placées(n))`. Nous l'avons ajouté pour vérifier une propriété du cours : le maximum de deux heuristiques admissibles est admissible et au moins aussi informatif que chacune. Ici Manhattan est toujours supérieur ou égal aux tuiles mal placées, donc le maximum redonne exactement Manhattan. Les résultats identiques de `a_star` et `a_star_max` le confirment ; le maximum n'apporte rien de plus sur le 8-puzzle et coûte un peu plus de calcul.

### Implémentation

Nous sommes partis de l'implémentation de référence de GeeksforGeeks et nous l'avons adaptée petit à petit au lieu de la réécrire, pour que A* s'intègre dans la structure du lab 1 sans modifier BFS, DFS et IDS.

La liste ouverte est une file de priorité (heapq) ordonnée par f. Avant chaque dépilement, nous enregistrons la taille de cette liste (la frontière) et celle de la liste fermée (les états explorés). Une itération correspond à un état dépilé, comme pour BFS, DFS et IDS, ce qui rend les résultats comparables. La liste fermée est un ensemble des plateaux déjà développés.

De la référence (src/solvers/a_star.py), nous avons gardé la boucle A* (heapq, closed_list, move_tile, le dictionnaire moves et les tests de bord de la case vide), la représentation du plateau en liste plate de 9 cases avec 0 pour la case vide, et la fonction d'heuristique de Manhattan (renommée manhattan ; l'ancien nom heuristic reste disponible). La référence est déjà correcte et connue : en la modifiant le moins possible, nous limitons le risque d'introduire des erreurs dans l'algorithme.

Du lab 1, nous avons réutilisé :
- `main.py` : le dictionnaire `SOLVERS` qui associe un nom d'algorithme à sa fonction, la question à l'utilisateur, la boucle de 10 exécutions et le calcul du temps moyen. A* y a été ajouté sous les noms `a_star`, `a_star_misplaced` et `a_star_max`, sans changer le reste.
- `parse_puzzle_file`, qui lit le fichier d'entrée et retourne la grille 3x3 (`None` pour la case vide) avec la position de la case vide.
- `is_solvable`, qui refuse les puzzles non solvables avant la recherche.
- `write_run_file` et `output_path`, qui écrivent un fichier par exécution dans le format demandé. `write_run_file` écrit en colonnes séparées par des tabulations les valeurs qui sont des paires (frontière, explorés), ce qui ne change rien pour BFS, DFS et IDS.

Ces composants ne dépendent pas de l'algorithme. Les réutiliser garantit que les fichiers de résultats de A* ont le même format que ceux de BFS, DFS et IDS, donc que la comparaison est équitable.

Nous avons apporté les modifications suivantes à la référence :
1. Suppression du code exécuté à l'import. La référence contenait un état initial codé en dur et une résolution à la fin du fichier. Comme `src/solvers/__init__.py` importe le module, ce code se serait exécuté à chaque lancement de `main.py`.
2. Même interface que les autres algorithmes. La fonction devient `solve_puzzle_a_star(start, x, y, h)` et retourne `(état final ou None, nombre d'itérations, tailles enregistrées)`. C'est ce que `main.py` attend de tous les solveurs, ce qui permet de les appeler de la même façon.
3. Ajout des compteurs. Avant chaque `heappop`, nous enregistrons la taille de la liste ouverte et celle de la liste fermée. Après, nous incrémentons les itérations. C'est le même emplacement que dans BFS, DFS et IDS.
4. Ajout de deux fonctions de conversion, `to_flat` et `to_matrix`. Le parser et les autres algorithmes utilisent une grille 3x3 avec `None`, alors que la référence utilise une liste plate avec `0`. Nous convertissons le plateau initial à l'entrée de la fonction et le plateau final à la sortie, ce qui évite de réécrire le code de la référence. La conversion se fait une seule fois par exécution, donc son coût devrait être négligeable.
5. Distance affichée avec `result.depth`. Dans `main.py`, `get_actions` du lab 1 reconstruit le chemin avec la position `x`, `y` et le parent de son propre `PuzzleState`. Celui de A* a une autre forme (il garde le coup et le coût `f`), donc nous lisons directement la profondeur, qui est égale au nombre de coups.
6. Correction de l'heuristique. Notre première version parcourait seulement 3 cases au lieu de 9, ce qui rendait l'heuristique inadmissible. Nous sommes revenus à la boucle sur 9 cases de la référence, et la distance obtenue est maintenant identique à celle de BFS.
7. Heuristique en paramètre. `solve_puzzle_a_star` reçoit l'heuristique `h` (Manhattan par défaut), ce qui permet de comparer les trois heuristiques sans dupliquer la boucle A*.

Les paramètres `x` et `y` ne servent pas à A*, qui retrouve la case vide avec `.index(0)`. Ils sont conservés pour garder la même signature que les autres solveurs. Les fonctions `print_board`, `print_solution` et `colored` de la référence sont restées dans le fichier mais ne sont pas utilisées par `main.py`.

### Pourquoi la distance de Manhattan comme heuristique principale

- **Admissible** (elle ne surestime jamais le coût réel restant jusqu'au but) **:** un coup déplace une seule tuile d'une seule case, donc il réduit la somme des distances d'au plus 1. L'heuristique ne surestime jamais le coût restant, et A* trouve donc un chemin optimal.
- **Cohérente** (pour deux états voisins n et n', `h(n) ≤ 1 + h(n')`, le 1 étant le coût d'un coup) **:** le changement de `h` entre deux états voisins est d'au plus 1, ce qui est le coût d'un coup. Une fois un plateau développé, on ne trouvera pas de meilleur chemin vers lui.
- **Informative et peu coûteuse :** elle se calcule en une passe sur 9 cases et guide beaucoup mieux la recherche qu'une absence d'information (cas de BFS).
- **Référencée :** c'est l'heuristique de la référence GeeksforGeeks que nous avons trouvée durant la revue de l'état de l'art.
- **Dominante :** pour tout état, Manhattan ≥ nombre de tuiles mal placées (chaque tuile mal placée est à au moins une case de sa cible), vérifié aussi sur 20 000 états aléatoires. Les tuiles mal placées sont aussi admissibles (chaque tuile mal placée demande au moins un coup), et le maximum de deux heuristiques admissibles est admissible ; comme Manhattan domine, ce maximum est toujours égal à Manhattan.

## Comparaison des algorithmes

Résultats obtenus avec `main.py` (10 exécutions par cas), toutes sur la même machine. Ex1-3 n'est pas solvable. Les itérations, frontières et explorés sont identiques d'une exécution à l'autre ; les temps sont indicatifs.

Tableau entièrement mis à jour : nouvelle exécution, colonne « Explorés », lignes des deux nouvelles heuristiques.

| Input | Algo | Distance | Itérations | Frontière max | Explorés (fin) | Temps moyen |
|---|---|---|---|---|---|---|
| Ex1-1 | BFS | 20 | 61 757 | 18 858 | - | 0,536 s |
| | DFS | 2 698 | 2 775 | 2 159 | - | 0,018 s |
| | IDS | 20 | 201 154 | 20 | - | 0,666 s |
| | **A\* Manhattan** | **20** | **274** | 170 | 270 | **0,0023 s** |
| | A\* tuiles mal placées | 20 | 3 811 | 2 215 | 3 653 | 0,0219 s |
| | A\* max | 20 | 274 | 170 | 270 | 0,0022 s |
| Ex1-2 | BFS | 17 | 12 717 | 7 344 | - | 0,098 s |
| | DFS | 65 971 | 96 880 | 42 890 | - | 1,266 s |
| | IDS | 17 | 51 436 | 17 | - | 0,170 s |
| | **A\* Manhattan** | **17** | **195** | 128 | 192 | **0,0017 s** |
| | A\* tuiles mal placées | 17 | 772 | 483 | 748 | 0,0043 s |
| | A\* max | 17 | 195 | 128 | 192 | 0,0019 s |
| Ex1-4 | BFS | 28 | 178 224 | 24 048 | - | 1,705 s |
| | DFS | 64 830 | 106 784 | 42 913 | - | 1,315 s |
| | IDS | 28 | 2 492 752 | 25 | - | 10,213 s |
| | **A\* Manhattan** | **28** | **611** | 314 | 607 | **0,0039 s** |
| | A\* tuiles mal placées | 28 | 68 222 | 25 864 | 61 097 | 0,549 s |
| | A\* max | 28 | 611 | 314 | 607 | 0,0072 s |

Les temps ci-dessus sont des moyennes sur 10 exécutions ; le temps de chaque exécution est dans la dernière ligne de `results/<algo>/<input>_runNN.txt`.

### Optimalité

BFS, IDS et A* (les trois heuristiques) trouvent la même distance sur les trois inputs. DFS ne garantit pas l'optimalité : il retourne le premier chemin trouvé, qui compte de 2 698 à 65 971 coups alors que la solution optimale en compte 17 à 28.

### Itérations

A* (Manhattan) explore de 65 à 290 fois moins d'états que BFS (611 contre 178 224 sur Ex1-4) et de 260 à 4 080 fois moins qu'IDS (2,5 millions). L'heuristique oriente la recherche vers l'état but au lieu d'explorer tous les états par niveau. IDS est le plus coûteux, car il refait la recherche à chaque nouvelle limite de profondeur.

Pour A*, le nombre d'itérations dépasse légèrement celui des états explorés (274 contre 270 sur Ex1-1) : ce sont des doublons d'un état déjà développé, retirés de la frontière et ignorés. Avec une heuristique cohérente, un état développé n'est jamais revisité.

### Comparaison des heuristiques

Les trois heuristiques sont admissibles et trouvent la distance optimale, mais Manhattan explore de 4 à 110 fois moins d'états que les tuiles mal placées, et l'écart grandit avec la longueur de la solution (× 110 sur Ex1-4). C'est l'effet de la dominance vu en cours : une heuristique dominante explore moins d'états, avec une frontière plus petite et moins d'itérations (jusqu'à 90 % selon le cours). Le maximum des deux est identique à Manhattan, comme prévu.

### Temps d'exécution

A* (Manhattan) est de l'ordre de la milliseconde (0,0017 à 0,0039 s), contre 0,1 à 1,7 s pour BFS et jusqu'à 10 s pour IDS. Le temps suit le nombre d'itérations, mais chaque itération de A* coûte un peu plus cher (calcul de l'heuristique et file de priorité). DFS peut être rapide (0,018 s sur Ex1-1) mais son résultat n'est pas utilisable.

Comme vu en cours, on ne peut pas se fier entièrement au temps mesuré : il dépend de la machine et de sa charge. Nos premières mesures, prises sur une autre machine, étaient environ deux fois plus faibles. Les itérations et la taille des listes sont les mesures principales ; le temps est indicatif et n'est comparé qu'entre mesures prises sur la même machine.

### Frontière

BFS grossit jusqu'à 7 000 à 24 000 états, et DFS jusqu'à 2 000 à 43 000 selon l'input. La frontière de A* (Manhattan) reste entre 128 et 314 états. IDS a la plus petite frontière (17 à 25), car il ne garde que le chemin courant et ses voisins. Avec les tuiles mal placées sur Ex1-4, A* explore toujours moins d'états que BFS (68 222 contre 178 224), mais sa frontière (25 864) dépasse celle de BFS (24 048) : une heuristique faible fait perdre l'avantage mémoire de A*.

### Mémoire

La frontière donne un indice de la mémoire utilisée, mais elle ne la mesure pas entièrement, car chaque algorithme garde aussi un ensemble d'états visités ou fermés. BFS et DFS stockent tous les états rencontrés. IDS économise la frontière mais a un ensemble `visited` par limite de profondeur. A* garde la liste fermée, qui reste petite ici parce qu'il explore peu d'états : 192 à 607 états avec Manhattan, contre 748 à 61 097 avec les tuiles mal placées. Nous n'avons pas mesuré la mémoire en octets.

## Apprentissages et remarques A* avec les autres algorithmes de recherche (partie 1)

- A* donne la solution optimale de BFS pour une fraction du coût, sur les trois inputs testés. Sur ces puzzles, il est de loin le meilleur choix.
- DFS est rapide sur certains inputs, mais ses chemins de plusieurs dizaines de milliers de coups le rendent inutilisable si on veut une solution courte.
- IDS est optimal avec peu de mémoire, mais il refait beaucoup de travail. Sur Ex1-4, il fait 14 fois plus d'itérations que BFS.
- Le choix de l'heuristique compte autant que l'algorithme : avec les tuiles mal placées, A* explore jusqu'à 110 fois plus d'états qu'avec Manhattan, et sa frontière peut dépasser celle de BFS.
- Le point le plus délicat de A* était l'adaptation de la référence : la représentation du plateau (liste plate contre grille 3x3) et les compteurs d'itérations, de frontière et d'états explorés, pour que les résultats restent comparables aux autres algorithmes.
- Une erreur d'implémentation sur la boucle de l'heuristique (parcourir 3 cases au lieu de 9) a rendu l'heuristique inadmissible. Une comparaison de la distance avec celle de BFS permet de détecter ce genre d'erreur.
- Le 8-puzzle est petit. Le temps de A* est de l'ordre de la milliseconde, donc plus sensible au bruit de mesure et à la machine utilisée, et trois inputs ne suffisent pas pour des conclusions générales.

## Références utilisées (partie 1)

- https://www.geeksforgeeks.org/artificial-intelligence/8-puzzle-problem-in-ai/
- Jebbar, O. (2026). Intelligence artificielle et reconnaissance des formes (6GEI608, séances 3 et 4 : recherche dans un graphe, A*, heuristiques). Université du Québec à Chicoutimi.

---

## Partie 2 : problème d'optimisation, plusieurs états objectifs (Sudoku)

### Puzzles

Nous avons générés dix puzzles sur https://qqwing.com/generate.html (données disponibles dans `data/input-sudoku/`), avec leurs métadonnées :
- ligne 1 = puzzle (81 caractères, `.` = vide)
- ligne 2 = solution, puis les ratings qqwing (difficulté, nombre de cases données, techniques nécessaires, nombre d'essais `Guesses`). La solution est lue par le parser mais n'est jamais utilisée par les algorithmes.

Voici un tableau récapitulatif de nos données de 10 inputs pour le sudoku:

| Puzzle | Difficulté | Cases données | Guesses |
|---|---|---|---|
| 01, 02 | Simple | 24, 28 | 0 |
| 03, 04, 09, 10 | Easy | 25, 24, 25, 26 | 0 |
| 05, 06 | Intermediate | 24, 26 | 0 |
| 07, 08 | Expert | 26, 25 | 2, 5 |

### Utilisation

Chaque algorithme se lance directement dans le terminal comme ci :

```
uv run -m src.sudoku.<algo> [fichier de puzzle] [nombre d'exécutions]
```

où `<algo>` est `hill_climbing`, `genetic_tournament`, `genetic_truncation` ou `genetic_hc`.
Il est à préciser que sans fichier, les 10 puzzles de `data/input-sudoku/` sont lancés ; sans nombre, la constante `N_RUNS` du fichier s'applique.

Voici un exemple de lancement : `uv run -m src.sudoku.genetic_hc data/input-sudoku/Sudoku-07-expert.txt 10`.

Chaque lancement reçoit un identifiant (date et heure) et son propre dossier (`src/sudoku/runner.py`) :

```
results/sudoku/<algo>/<ID>/
    stats.txt                 récapitulatif du lancement (résolues, temps moyen, itérations moyennes par puzzle)
    <puzzle>/runNN.log        journal de l'exécution
    <puzzle>/runNN.txt        une ligne « génération⇥conflits du meilleur » par itération, puis itérations, temps (s), redémarrages
    <puzzle>/stats.txt        résolues, tableau par exécution, moyenne / écart-type / min / max (temps, itérations, redémarrages, conflits)
```

Le niveau de journalisation se règle par `LOG_LEVEL` en tête de chaque fichier : `INFO` donne la présentation des résultats (nom du puzzle, grille de départ, paramètres, redémarrages, résultat final, grille obtenue) ; `DEBUG` ajoute le détail de chaque itération.

### Formulation du problème / Modélisation

- **État :** une grille de 81 cases entièrement remplie, les cases données intactes. Chaque **ligne** contient toujours les chiffres 1 à 9 ; seuls les colonnes et les blocs peuvent être en conflit.
- **État initial :** `fill_rows` (`src/sudoku/commun.py`) remplit chaque ligne au hasard avec ses chiffres manquants.
- **Coût (fitness) :** `conflicts`, le nombre de **paires** de cases contenant le même chiffre dans une même colonne ou un même bloc (fonction des 8 reines vue en cours). Il vaut 0 seulement pour la solution ; il est à minimiser.
- **Voisin :** échange de deux cases modifiables d'une même ligne. Le cours définit un voisin comme le changement du contenu d'une case ; changer une seule case créerait forcément un doublon dans sa ligne. Un échange équivaut à deux changements de case coordonnés qui gardent les lignes valides ; c'est l'opérateur standard pour cette représentation, et il réduit l'espace de recherche.
- **Cases données :** jamais modifiées, ni par les voisins, ni par la mutation, ni par le crossover.

**Restriction aux chiffres permis (connaissance du domaine, déclarée).**

Idée : quand on remplit au hasard les cases vides d'une ligne, certains chiffres sont déjà impossibles. Si le 5 est une case donnée dans la colonne d'une case vide, ou dans son bloc, y placer un 5 créerait à coup sûr un conflit, et ce conflit ne pourrait jamais disparaître, puisqu'une case donnée ne bouge pas. On évite donc ces chiffres au départ.

Fonctionnement, avec `USE_ALLOWED_DIGITS = True` (valeur utilisée) : pour chaque case vide, `allowed_digits` liste les chiffres qui ne sont pas déjà donnés dans sa colonne ni dans son bloc. `fill_rows` remplit ensuite chaque ligne avec ses chiffres manquants, placés au hasard mais seulement dans des cases où ils sont permis ; `place_row` y parvient par un petit retour arrière (case la plus contrainte d'abord). Chaque ligne reste une permutation de 1 à 9.

Limites : c'est une seule passe de filtrage, sans déduction en cascade (on ne déduit pas un chiffre à partir d'un autre qu'on vient de déduire), et la solution n'est jamais exclue. Les mutations et les voisins peuvent replacer un chiffre interdit ensuite ; la fonction de coût le pénalise alors.

Effet : l'espace des grilles de départ passe d'environ 10^28 à 10^14 selon le puzzle, et le nombre moyen de conflits au départ de 56,6 à 38,0 sur Sudoku-01. Tous les algorithmes utilisent le même `fill_rows`, la comparaison entre eux reste donc équitable. L'effet sur les résultats est mesuré plus bas.

### Hill climbing (`hill_climbing.py`)

Hill climbing, adapté d'aima-python (`search.py`), avec **redémarrages aléatoires**.

**Déroulement.**
1. **État initial :** une grille `fill_rows` (lignes valides, chiffres permis par les cases données).
2. **À chaque itération :** on enregistre les conflits de l'état courant, puis on génère **tous** ses voisins avec `get_neighbors` : pour chaque ligne, tous les échanges de deux cases modifiables (de 140 à 160 voisins selon le puzzle). Chaque voisin est évalué par `value = -conflicts` (maximiser `value` revient à minimiser les conflits).
3. **Déplacement :** on choisit le meilleur voisin (`argmax_random_tie`, égalités départagées au hasard). S'il est **strictement** meilleur que l'état courant, il devient l'état courant.
4. **Optimum local :** si aucun voisin n'est strictement meilleur (optimum local ou plateau), on **redémarre** d'une nouvelle grille `fill_rows` et on compte un redémarrage. C'est la solution proposée en cours contre les optimums locaux : réexécuter avec plusieurs initialisations aléatoires.
5. **Arrêt :** à la solution (0 conflit), ou après `MAX_ITERATIONS = 100 000` itérations, redémarrages compris. Ce plafond est un budget de temps (environ 350 itérations par seconde, soit à peu près 5 min au plus par exécution), choisi par l'équipe pour que les évaluations restent réalisables et nous sommes conscients que ce n'est pas une valeur optimale (voir "Hill climbing de base, sans plafond" plus bas). En cas d'échec, on retourne la **meilleure grille vue** sur toute l'exécution, et non la grille courante (qui peut être une grille aléatoire juste après un redémarrage).

Il est important d'ajouter une précision qu'**une itération** est l'évaluation de tout le voisinage de l'état courant, suivie d'un déplacement vers le meilleur voisin ou d'un redémarrage. Le nombre d'itérations compte donc aussi les redémarrages (sur 20 000 itérations, environ 1 000 sont des redémarrages). Le fichier de résultats donne les conflits de l'état courant à chaque itération et le nombre de redémarrages.

**Comportement observé.**
- Une montée depuis une grille aléatoire atteint un optimum local en une vingtaine de pas environ, puis l'algorithme redémarre, les optimums locaux se situent le plus souvent entre 2 et 8 conflits.
- Le hill climbing trouve la solution, mais il peut lui falloir des milliers, voire des centaines de milliers de redémarrages : la version de base, sans limite, a demandé de 5,5 à 22,8 heures sur 6 puzzles (section suivante). Chaque essai repart de zéro et ignore ce que les essais précédents ont trouvé.
- Pendant le développement, avec un budget de 20 000 itérations, il a résolu 5 exécutions sur 9 (puzzles 01, 05, 07) avec la restriction aux chiffres permis.

**Propriétés.** Le hill climbing ne garde qu'une grille (mémoire minimale) et chaque pas coûte l'évaluation de ses 140 à 160 voisins. Il est incomplet : un optimum local à k > 0 conflits ne dit rien de la distance à la solution. Avec des redémarrages, il devient complet **en probabilité** seulement, à temps infini ; sous un budget fixe, on mesure un taux de succès.

#### Hill climbing de base, sans plafond

Au début du laboratoire, nous avons lancé la version de base du hill climbing sur les 10 puzzles, sans aucune limite de temps, pour savoir ce que coûte l'algorithme tel quel. Cette version est celle du commit `f63f579` : remplissage uniforme des lignes (sans restriction aux chiffres permis), `conflicts` avec `Counter`, aucun `MAX_ITERATIONS`, aucun journal. L'algorithme (voisinage, règle de déplacement, redémarrage sur optimum local) est le même qu'aujourd'hui. Ce qui a changé depuis : le plafond `MAX_ITERATIONS`, le remplissage par chiffres permis, un calcul de `conflicts` plus rapide et la journalisation.

Lancement : `mesure_temps_hill_climbing.py`, un processus par puzzle (10 en parallèle réalisé sur un PC à 32 coeurs), du 2026-10-24 08:03 jusqu'à l'arrêt manuel (Ctrl+C) le 2026-10-25, après 1 678,9 min (≈ 28 h). Résultats complets dans `results/hill_climbing_base_sans_plafond/` (`resume.txt`, `suivi.txt` et un `.log` par puzzle).

Voici un tableau récapitulatif des résultats :

| Puzzle | Résultat | Temps (horloge) | Itérations | Redémarrages |
|---|---|---|---|---|
| Sudoku-02-simple | résolu | 19 800 s (5,5 h) | 3 598 135 | 201 672 |
| Sudoku-04-easy | résolu | 24 911 s (6,9 h) | 3 660 817 | 194 620 |
| Sudoku-10-easy | résolu | 34 156 s (9,5 h) | 5 375 882 | 292 555 |
| Sudoku-08-expert | résolu | 56 580 s (15,7 h) | 9 122 880 | 492 376 |
| Sudoku-07-expert | résolu | 59 140 s (16,4 h) | 10 256 538 | 561 221 |
| Sudoku-06-intermediate | résolu | 82 193 s (22,8 h) | 13 012 598 | 709 485 |
| Sudoku-01, 03, 05, 09 | non résolus | > 100 734 s (28 h) | - | - |

Remarques :
- Un seul essai par puzzle : la durée suit une loi proche de l'exponentielle (chaque redémarrage a une très faible probabilité de réussir), donc l'ordre des puzzles dans ce tableau ne dit rien de leur difficulté réelle.
- Une montée dure en moyenne environ 18 itérations avant le redémarrage (3 598 135 / 201 672), donc un plafond de 100 000 itérations correspond à peu près 5 500 redémarrages. C'est très inférieur aux 200 000 à 700 000 redémarrages du tableau : avec le remplissage de base et ce plafond, l'algorithme échouerait presque TOUJOURS.


Les résultats du hill climbing avec la version du code actuel (plafond de 100 000 itérations) sont dans le tableau « Résultats » plus bas.

### Algorithmes génétiques

Les trois versions partagent la représentation, la fitness (`conflicts`, à minimiser), le crossover et la mutation ; elles diffèrent par la sélection et par les mécanismes ajoutés. Toutes s'arrêtent à la solution ou après `MAX_GENERATIONS` générations, et retournent la meilleure grille vue sur toute l'exécution (pas seulement celle de la dernière génération).

Une itération correspond à une génération : la création de `POP_SIZE` enfants (sélection, crossover, mutation, et hill climbing pour une partie des enfants dans `genetic_hc`) qui remplacent la population. Une génération coûte donc beaucoup plus cher qu'une itération du hill climbing : les nombres d'itérations ne se comparent pas d'un algorithme à l'autre, seuls les temps et les taux de succès le permettent.

- **Population initiale :** `POP_SIZE` grilles `fill_rows`.
- **Fitness :** nombre de paires en conflit, à minimiser. Les deux sélections ne font que comparer les scores : aucune transformation en valeur positive n'est nécessaire.
- **Crossover uniforme par lignes :** chaque ligne de l'enfant vient, au hasard, de l'un ou l'autre parent. Les lignes étant copiées entières, elles restent valides et les cases données sont conservées (couper par lignes ou par colonnes garantit de ne jamais modifier le puzzle de départ). Le crossover uniforme est une variante de la coupe par lignes : avec une coupe à un point, les lignes voisines d'un même côté de la coupe ne sont jamais séparées (8 enfants possibles au lieu de 2⁹ = 512).
- **Mutation :** avec la probabilité `MUTATION_RATE`, un ou plusieurs échanges de deux cases modifiables d'une même ligne (comme le voisin du hill climbing).
- **Remplacement :** toute la population est remplacée à chaque génération.

#### 1. Sélection par tournoi (`genetic_tournament.py`)

Version de base, adaptée du code du livre (AIMA, Figure 4.8). Pour choisir un parent, on tire `TOURNAMENT_K` candidats ; le meilleur gagne avec la probabilité `TOURNAMENT_P`, sinon le suivant avec la même probabilité, et ainsi de suite (tournoi probabiliste : avec `TOURNAMENT_P = 1.0`, le meilleur gagne toujours). Le tournoi a été préféré à la roulette : il n'exige pas de fitness positive et sa pression se règle avec un seul paramètre.

#### 2. Sélection par troncature uniforme (`genetic_truncation.py`)

Créée pour préserver la diversité. Avec le tournoi, la population descend rapidement d'un même individu (convergence prématurée) et se fige dans un faux minimum. La troncature dirige le groupe **en éliminant les pires** plutôt qu'en favorisant les meilleurs : seuls les individus dont le score est au plus le quantile `TRUNCATION_QUANTILE` de la génération peuvent être parents, et ils sont tirés uniformément (un individu à 5 conflits n'a pas plus de chances qu'un individu à 25). Le nombre d'échanges d'une mutation est une fraction des cases modifiables (`MUTATION_SWAP_RATE`). Les journaux DEBUG affichent la distance moyenne entre grilles et la proportion de cases figées, pour suivre la diversité.

#### 3. Génétique et hill climbing (`genetic_hc.py`)

Algorithme mémétique : la troncature uniforme, plus un hill climbing appliqué à une fraction des enfants (`HILL_CLIMBING_RATE`) pendant au plus `HILL_CLIMBING_STEPS` pas (même voisinage et même règle que `hill_climbing.py`, sans redémarrage interne). Si le meilleur score de l'essai en cours n'est pas battu pendant `RESTART_STAGNATION` générations, toute la population est recréée. Il réunit le meilleur des deux mondes : le génétique combine les lignes de bons optimums locaux et garde la mémoire des bons essais ; le hill climbing fait les derniers échanges précis que le génétique seul ne trouve pas. C'est un hybride, présenté comme tel.

#### Paramètres

| Paramètre | `genetic_tournament` | `genetic_truncation` | `genetic_hc` |
|---|---|---|---|
| `POP_SIZE` | 1 000 | 1 000 | 1 000 |
| Sélection | tournoi, k = 2, p = 0,8 | troncature, quantile 0,95 | troncature, quantile 0,5 |
| `MUTATION_RATE` | 0,3 | 0,01 | 0,1 |
| Échanges par mutation | 10 | taux 1,0 des cases modifiables | taux 0,2 des cases modifiables |
| `MAX_GENERATIONS` | 5 000 | 5 000 | 1 000 |
| Hill climbing | - | - | 10 % des enfants, 5 pas |
| Redémarrage | - | - | après 30 générations sans progrès |


### Résultats globaux

Chaque valeur vient d'un fichier `stats.txt` conservé dans `results/sudoku/<algo>/<ID>/`. Format : exécutions résolues, temps moyen par exécution.

| Puzzle | Hill climbing | Génétique (tournoi) | Génétique (troncature) | Génétique + hill climbing |
|---|---|---|---|---|
| 01 | 5/10, 236,9 s | 0/10, 154,4 s | 0/10, 100,6 s | 10/10, 40,6 s |
| 02 | 10/10, 16,3 s | 0/10, 153,9 s | 0/10, 102,1 s | 10/10, 11,8 s |
| 03 | 2/10, 230,9 s | 0/10, 157,7 s | 0/10, 102,0 s | 9/10, 388,2 s |
| 04 | 0/10, 282,1 s | 0/10, 150,0 s | 0/10, 103,4 s | 0/10, 1 041,1 s |
| 05 | 6/10, 206,3 s | 0/10, 153,0 s | 0/10, 134,9 s | 10/10, 50,3 s |
| 06 | 4/10, 192,3 s | 0/10, 150,7 s | 0/10, 103,0 s | 10/10, 16,2 s |
| 07 | 10/10, 27,4 s | 0/10, 154,5 s | 0/10, 105,3 s | 10/10, 31,0 s |
| 08 | 0/10, 277,2 s | 0/10, 153,8 s | 0/10, 103,3 s | 0/10, 1 015,6 s |
| 09 | 4/10, 206,0 s | 0/10, 151,2 s | 0/10, 105,2 s | 10/10, 25,8 s |
| 10 | 6/10, 155,9 s | 0/10, 151,5 s | 0/10, 104,5 s | 10/10, 15,7 s |
| **Total** | **47/100** | **0/100** | **0/100** | **79/100** |

Sources :
- `results/sudoku/hill_climbing/20261025-113114/stats.txt` (10 exécutions par puzzle, plafond de 100 000 itérations)
- `results/sudoku/genetic_tournament/20261025-131905/stats.txt` (5 000 générations par exécution)
- `results/sudoku/genetic_truncation/20261025-101920/stats.txt` (5 000 générations par exécution)
- `results/sudoku/genetic_hc/20261025-141610/stats.txt` (10 exécutions par puzzle, plafond de 1 000 générations)

Le temps moyen compte aussi les exécutions échouées, qui durent jusqu'au plafond (environ 280 s pour le hill climbing). Pour le génétique + hill climbing, une exécution échouée dure environ 1 000 s (plafond de 1 000 générations, environ 24 redémarrages).

**Lecture du hill climbing :** 47 exécutions sur 100 sont résolues dans les paramètres fixés. Les puzzles 02 et 07 le sont 10 fois sur 10 en 16 s et 27 s, alors que 04 et 08 ne le sont jamais : le plafond de 100 000 itérations (à peu près 5 500 redémarrages) est trop court pour eux, comme le laissaient prévoir nos mesures sans plafond. Les deux génétiques purs (tournoi et troncature) ne résolvent aucune exécution sur 200, ce qui confirme l'analyse plus bas.

**Lecture du génétique + hill climbing :** 79 exécutions sur 100 sont résolues. Sept puzzles sur dix le sont 10 fois sur 10, en 12 à 50 s en moyenne et avec au plus un redémarrage en moyenne ; le Sudoku-07 « expert » est résolu en 31 s en moyenne. Le Sudoku-03 l'est 9 fois sur 10, mais en 388 s en moyenne et avec jusqu'à 24 redémarrages (bassin de faux minima à 2 conflits, voir l'analyse). Les Sudoku-04 et 08 ne sont jamais résolus dans le plafond de 1 000 générations : ce sont aussi les deux puzzles que le hill climbing ne résout jamais. C'est le seul des quatre algorithmes qui résout la majorité des exécutions.


### Analyse

**Le génétique pur se coince lui aussi.** Le cours présente l'algorithme génétique comme un moyen de ne pas se coincer dans les optimums locaux mais il ne le garantit pas. Nos mesures nuancent cette affirmation : le génétique pur (tournoi ou troncature) réduit le risque mais ne le supprime pas, et plafonne entre 2 et 6 conflits. Deux mécanismes l'expliquent :
- **convergence prématurée** : avec le tournoi, le meilleur individu envahit la population en quelques générations (environ ln N / ln k) ; croiser des grilles presque identiques ne crée plus rien ;
- **dérive génétique** : même sans aucun avantage aux meilleurs (troncature uniforme), une population finie perd sa diversité, plus vite si elle est petite, car certaines lignées disparaissent au hasard. La dérive fige les lignes présentes, pas celles de la solution.

Il faut à la fois de la diversité et une pression de sélection : sans pression, la population erre (troncature à 0,95 : moyenne stable vers 37 conflits avec 20 000 individus) ; avec trop de pression, elle converge vers un faux minimum.

**Un conflit n'est pas une case fausse.** Sur le Sudoku-03 (lancement `20261025-141610`), les 88 essais bloqués du génétique + hill climbing l'étaient tous exactement à 2 conflits. La grille finale de l'exécution 8, elle aussi à 2 conflits, comptait 24 cases fausses sur 7 lignes par rapport à la solution. Les inversions forment une chaîne (par exemple un 5 et un 6 échangés dans deux lignes différentes) : chaque colonne garde un exemplaire de chaque chiffre, et les conflits n'apparaissent qu'aux bouts de la chaîne. Une grille à 2 conflits est presque une autre grille valide ; pour atteindre la solution, il faut changer plusieurs lignes à la fois, et chaque échange isolé ajoute des conflits. C'est un faux minimum : le nombre de conflits mesure la validité, pas la distance à la solution. Allonger le hill climbing n'aide pas, puisqu'il s'arrête dès qu'aucun échange n'améliore.

**Pourquoi le génétique + hill climbing fonctionne.** Le hill climbing seul repart toujours d'une grille aléatoire et oublie ses essais (il a trouvé des solutions, mais après plusieurs heures) ; le génétique seul s'approche de la solution mais ne sait pas la finir. Le mémétique part de combinaisons de bons optimums locaux et le hill climbing finit le travail ; les redémarrages sur stagnation remplacent la diversité perdue. Sa pression de sélection doit laisser les grilles améliorées se reproduire : avec la troncature à 0,5, il a résolu 9 exécutions sur 9 (puzzles 01, 05, 07) ; à 0,95, seulement 3 sur 9.

**Difficulté qqwing et difficulté pour la recherche.** La difficulté qqwing mesure les techniques de déduction humaines. Elle ne prédit pas la difficulté pour une recherche par échanges : le Sudoku-07 "expert" a été résolu en quelques secondes, alors que le Sudoku-03 "easy" a demandé jusqu'à 24 redémarrages (grand bassin de faux minima à 2 conflits).

**Connaissance du domaine.** Une seule passe de filtrage à partir des cases données a presque doublé le taux de réussite (génétique + hill climbing : 5/9 à 9/9 ; hill climbing : 0/9 à 5/9). La connaissance du problème a pesé plus lourd que le réglage des paramètres.

**Complétude.** Le hill climbing et le génétique sont des recherches **incomplètes** : 0 conflit prouve qu'on a la solution, mais un optimum à 2 conflits ne dit rien de la distance à la solution. Le hill climbing à redémarrages est complet seulement en probabilité, à temps infini. Une recherche complète (propagation de contraintes et recherche en profondeur, comme Norvig : 95 puzzles difficiles résolus en 0,04 s en moyenne) donne une garantie en temps borné.

### Pistes de solutions

- **Recuit simulé** (vu en cours) : accepter parfois un voisin pire permettrait de défaire une chaîne d'inversions comme celle du Sudoku-04 et Sudoku-08.
- **Voisinage étendu** : des paires d'échanges dans deux lignes différentes (beaucoup plus coûteux).
- **Exécutions en parallèle** dans le runner, pour réduire la durée des évaluations.

---

## Ce que nous avons appris

- Le bon outil dépend du problème : A* est exact et optimal quand une heuristique **ADMISSIBLE** guide la recherche. Le hill climbing et le génétique sont adaptés à l'optimisation quand beaucoup de solutions sont acceptables, moins quand une seule solution exacte est attendue comme au Sudoku.
- Une heuristique dominante réduit fortement le nombre d'états explorés (* 110 sur Ex1-4) sans perdre l'optimalité.
- Un algorithme génétique est fort pour s'approcher d'une solution, faible pour la finir, la diversité sans pression de sélection ne converge pas, et la pression sans diversité se coince.
- Ajuster des paramètres sur un seul puzzle mène au surapprentissage : il faut mesurer sur plusieurs puzzles, et mesurer chaque mécanisme seul avant de conclure qu'il aide.
- Toute connaissance du problème ajoutée à un algorithme doit être déclarée et son effet mesuré.
- Un temps d'exécution n'est comparable que sur la même machine, dans les mêmes conditions.
- Un algorithme sans plafond peut prendre des heures : les 6 puzzles résolus par la version de base ont demandé de 5,5 à 22,8 h, et 4 n'étaient pas résolus après 28 h. Mesurer un temps demande un lancement en parallèle et une trace écrite (`suivi.txt`, `.log`).
- Défis rencontrés : adapter le code de référence (GeeksforGeeks, AIMA) sans le réécrire, garder le format de résultats du lab 1, et rendre mesurables des algorithmes stochastiques (plusieurs exécutions, plafond, statistiques).

## Références

- https://www.geeksforgeeks.org/artificial-intelligence/8-puzzle-problem-in-ai/
- Russell, S. et Norvig, P. *Artificial Intelligence: A Modern Approach* (Figure 4.8, algorithme génétique) ; https://github.com/aimacode/aima-python
- Norvig, P. *Solving Every Sudoku Puzzle*. https://www.norvig.com/sudoku.html
- *Solving Sudoku with genetic algorithms* (2010). https://fakeguido.blogspot.com/2010/05/solving-sudoku-with-genetic-algorithms.html
- Jebbar, O. (2026). Intelligence artificielle et reconnaissance des formes (6GEI608, séances 3 et 4). Université du Québec à Chicoutimi.
- https://www.geeksforgeeks.org/dsa/check-if-given-sudoku-board-configuration-is-valid-or-not/
