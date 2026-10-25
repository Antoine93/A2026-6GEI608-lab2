# A2026-6GEI608-lab2

Laboratoire 2 de 6GEI608, Intelligence artificielle et reconnaissance des formes (UQAC).

- Équipe : voir `EQUIPE.txt`
- Dépôt : https://github.com/Antoine93/A2026-6GEI608-lab2

> <mark>**Brouillon v2.**</mark> <mark>Les passages surlignés sont ajoutés ou modifiés par rapport au README existant.</mark> Partie 1 : texte du README existant, conservé et mis à jour seulement là où le code ou les résultats ont changé. Partie 2 : rédigée à partir du journal de laboratoire, contre-vérifiée sur la base de code du 25 octobre. Les passages `<mark>[À COMPLÉTER]</mark>` attendent les résultats des évaluations finales.

---

## Partie 1 : résolution du 8-puzzle avec l'algorithme A*

### Utilisation

Similaire au fonctionnement du lab 1, le programme (`python main.py`) demande le fichier d'entrée (ex. `data/input-Ex1/Ex1-1.txt`) puis l'algorithme : bfs, dfs, ids, <mark>a_star (distance de Manhattan), a_star_misplaced (tuiles mal placées) ou a_star_max (maximum des deux)</mark>.
Il vérifie d'abord que le puzzle est solvable (parité des inversions), puis exécute la recherche 10 fois.

Pour chaque exécution, un fichier est écrit dans `results/<algo>/<input>_runNN.txt` :
- à partir de la première ligne : numéro_itération ⇥ taille_de_frontière ; <mark>pour A*, une 3ᵉ colonne donne la taille de la liste des états explorés (numéro_itération ⇥ taille_de_frontière ⇥ taille_des_explorés)</mark> ;
- avant-dernière ligne : nombre total <mark>d'itérations (états dépilés)</mark> ;
- dernière ligne : temps d'exécution de la fonction de recherche.

## Algorithme A*

- **Fonction d'évaluation :** `f(n) = g(n) + h(n)`, où `g` est le coût pour arriver à n (chaque coup coûte 1 dans notre 8-puzzle) et `h` l'heuristique.
- **Heuristiques utilisées :** <mark>trois heuristiques, choisies par le paramètre `h` de `solve_puzzle_a_star(start, x, y, h=manhattan)` :</mark>
  - **distance de Manhattan** <mark>(`manhattan`, par défaut)</mark> : la somme, pour chaque tuile (case vide exclue), de la distance en lignes et en colonnes entre sa position et sa position cible ;
  - <mark>**tuiles mal placées** (`misplaced_tiles`) : le nombre de tuiles (case vide exclue) qui ne sont pas à leur position cible ;</mark>
  - <mark>**maximum des deux** (`max_heuristic`).</mark>

### Implémentation

Nous sommes partis de l'implémentation de référence de GeeksforGeeks et nous l'avons adaptée petit à petit au lieu de la réécrire, pour que A* s'intègre dans la structure du lab 1 sans modifier BFS, DFS et IDS.

La liste ouverte est une file de priorité (`heapq`) ordonnée par `f`. Avant chaque dépilement, nous enregistrons la taille de cette liste (la frontière) <mark>et celle de la liste fermée (les états explorés)</mark>. Une itération correspond à un état dépilé, comme pour BFS, DFS et IDS, ce qui rend les résultats comparables. La liste fermée est un ensemble des plateaux déjà développés.

De la référence (`src/solvers/a_star.py`), nous avons gardé la boucle A* (`heapq`, `closed_list`, `move_tile`, le dictionnaire `moves` et les tests de bord de la case vide), la représentation du plateau en liste plate de 9 cases avec `0` pour la case vide, et la fonction d'heuristique de Manhattan <mark>(renommée `manhattan` ; l'ancien nom `heuristic` reste disponible)</mark>. La référence est déjà correcte et connue : en la modifiant le moins possible, nous limitons le risque d'introduire des erreurs dans l'algorithme.

Du lab 1, nous avons réutilisé :
- `main.py` : le dictionnaire `SOLVERS` qui associe un nom d'algorithme à sa fonction, la question à l'utilisateur, la boucle de 10 exécutions et le calcul du temps moyen. A* y a été ajouté sous <mark>les noms `a_star`, `a_star_misplaced` et `a_star_max`</mark>, sans changer le reste.
- `parse_puzzle_file`, qui lit le fichier d'entrée et retourne la grille 3x3 (`None` pour la case vide) avec la position de la case vide.
- `is_solvable`, qui refuse les puzzles non solvables avant la recherche.
- `write_run_file` et `output_path`, qui écrivent un fichier par exécution dans le format demandé. <mark>`write_run_file` écrit en colonnes séparées par des tabulations les valeurs qui sont des paires (frontière, explorés), ce qui ne change rien pour BFS, DFS et IDS.</mark>

Ces composants ne dépendent pas de l'algorithme. Les réutiliser garantit que les fichiers de résultats de A* ont le même format que ceux de BFS, DFS et IDS, donc que la comparaison est équitable.

Nous avons apporté les modifications suivantes à la référence :
1. Suppression du code exécuté à l'import. La référence contenait un état initial codé en dur et une résolution à la fin du fichier. Comme `src/solvers/__init__.py` importe le module, ce code se serait exécuté à chaque lancement de `main.py`.
2. Même interface que les autres algorithmes. La fonction devient <mark>`solve_puzzle_a_star(start, x, y, h)`</mark> et retourne <mark>`(état final ou None, nombre d'itérations, tailles enregistrées)`</mark>. C'est ce que `main.py` attend de tous les solveurs, ce qui permet de les appeler de la même façon.
3. Ajout des compteurs. Avant chaque `heappop`, nous enregistrons la taille de la liste ouverte <mark>et celle de la liste fermée</mark>. Après, nous incrémentons les itérations. C'est le même emplacement que dans BFS, DFS et IDS.
4. Ajout de deux fonctions de conversion, `to_flat` et `to_matrix`. Le parser et les autres algorithmes utilisent une grille 3x3 avec `None`, alors que la référence utilise une liste plate avec `0`. Nous convertissons le plateau initial à l'entrée de la fonction et le plateau final à la sortie, ce qui évite de réécrire le code de la référence. La conversion se fait une seule fois par exécution, donc son coût devrait être négligeable.
5. Distance affichée avec `result.depth`. Dans `main.py`, `get_actions` du lab 1 reconstruit le chemin avec la position `x`, `y` et le parent de son propre `PuzzleState`. Celui de A* a une autre forme (il garde le coup et le coût `f`), donc nous lisons directement la profondeur, qui est égale au nombre de coups.
6. Correction de l'heuristique. Notre première version parcourait seulement 3 cases au lieu de 9, ce qui rendait l'heuristique inadmissible. Nous sommes revenus à la boucle sur 9 cases de la référence, et la distance obtenue est maintenant identique à celle de BFS.
7. <mark>Heuristique en paramètre. `solve_puzzle_a_star` reçoit l'heuristique `h` (Manhattan par défaut), ce qui permet de comparer les trois heuristiques sans dupliquer la boucle A*.</mark>

Les paramètres `x` et `y` ne servent pas à A*, qui retrouve la case vide avec `.index(0)`. Ils sont conservés pour garder la même signature que les autres solveurs. Les fonctions `print_board`, `print_solution` et `colored` de la référence sont restées dans le fichier mais ne sont pas utilisées par `main.py`.

### Pourquoi la distance de Manhattan comme heuristique <mark>principale</mark>

- **Admissible :** un coup déplace une seule tuile d'une seule case, donc il réduit la somme des distances d'au plus 1. L'heuristique ne surestime jamais le coût restant, et A* trouve donc un chemin optimal.
- **Cohérente :** le changement de `h` entre deux états voisins est d'au plus 1, ce qui est le coût d'un coup. Une fois un plateau développé, on ne trouvera pas de meilleur chemin vers lui.
- **Informative et peu coûteuse :** elle se calcule en une passe sur 9 cases et guide beaucoup mieux la recherche qu'une absence d'information (cas de BFS).
- **Référencée :** c'est l'heuristique de la référence GeeksforGeeks que nous avons trouvée durant la revue de l'état de l'art.
- <mark>**Dominante :** pour tout état, Manhattan ≥ nombre de tuiles mal placées (chaque tuile mal placée est à au moins une case de sa cible), vérifié aussi sur 20 000 états aléatoires. Les tuiles mal placées sont aussi admissibles (chaque tuile mal placée demande au moins un coup), et le maximum de deux heuristiques admissibles est admissible ; comme Manhattan domine, ce maximum est toujours égal à Manhattan.</mark>

## Comparaison des algorithmes

Résultats obtenus avec `main.py` (10 exécutions par cas)<mark>, toutes sur la même machine</mark>. Ex1-3 n'est pas solvable. <mark>Les itérations, frontières et explorés sont identiques d'une exécution à l'autre ; les temps sont indicatifs.</mark>

<mark>Tableau entièrement mis à jour : nouvelle exécution, colonne « Explorés », lignes des deux nouvelles heuristiques.</mark>

| Input | Algo | Distance | Itérations | Frontière max | Explorés (fin) | Temps moyen |
|---|---|---|---|---|---|---|
| Ex1-1 | BFS | 20 | 61 757 | 18 858 | — | 0,536 s |
| | DFS | 2 698 | 2 775 | 2 159 | — | 0,018 s |
| | IDS | 20 | 201 154 | 20 | — | 0,666 s |
| | **A\* Manhattan** | **20** | **274** | 170 | 270 | **0,0023 s** |
| | A\* tuiles mal placées | 20 | 3 811 | 2 215 | 3 653 | 0,0219 s |
| | A\* max | 20 | 274 | 170 | 270 | 0,0022 s |
| Ex1-2 | BFS | 17 | 12 717 | 7 344 | — | 0,098 s |
| | DFS | 65 971 | 96 880 | 42 890 | — | 1,266 s |
| | IDS | 17 | 51 436 | 17 | — | 0,170 s |
| | **A\* Manhattan** | **17** | **195** | 128 | 192 | **0,0017 s** |
| | A\* tuiles mal placées | 17 | 772 | 483 | 748 | 0,0043 s |
| | A\* max | 17 | 195 | 128 | 192 | 0,0019 s |
| Ex1-4 | BFS | 28 | 178 224 | 24 048 | — | 1,705 s |
| | DFS | 64 830 | 106 784 | 42 913 | — | 1,315 s |
| | IDS | 28 | 2 492 752 | 25 | — | 10,213 s |
| | **A\* Manhattan** | **28** | **611** | 314 | 607 | **0,0039 s** |
| | A\* tuiles mal placées | 28 | 68 222 | 25 864 | 61 097 | 0,549 s |
| | A\* max | 28 | 611 | 314 | 607 | 0,0072 s |

<mark>[À COMPLÉTER : écart-type, minimum et maximum du temps sur les 10 exécutions (valeurs statistiques demandées par la grille).]</mark>

### Optimalité

BFS, IDS et A* <mark>(les trois heuristiques)</mark> trouvent la même distance sur les trois inputs. DFS ne garantit pas l'optimalité : il retourne le premier chemin trouvé, qui compte de 2 698 à 65 971 coups alors que la solution optimale en compte 17 à 28.

### Itérations

A* <mark>(Manhattan)</mark> explore <mark>de 65 à 290 fois</mark> moins d'états que BFS (611 contre 178 224 sur Ex1-4) et <mark>de 260 à 4 080 fois</mark> moins qu'IDS (2,5 millions). L'heuristique oriente la recherche vers l'état but au lieu d'explorer tous les états par niveau. IDS est le plus coûteux, car il refait la recherche à chaque nouvelle limite de profondeur.

<mark>Pour A*, le nombre d'itérations dépasse légèrement celui des états explorés (274 contre 270 sur Ex1-1) : ce sont des doublons d'un état déjà développé, retirés de la frontière et ignorés. Avec une heuristique cohérente, un état développé n'est jamais revisité.</mark>

### <mark>Comparaison des heuristiques</mark>

<mark>Les trois heuristiques sont admissibles et trouvent la distance optimale, mais Manhattan explore de 4 à 110 fois moins d'états que les tuiles mal placées, et l'écart grandit avec la longueur de la solution (× 110 sur Ex1-4). C'est l'effet de la dominance vu en cours : une heuristique dominante explore moins d'états, avec une frontière plus petite et moins d'itérations (« jusqu'à 90 % » selon la séance 4). Le maximum des deux est identique à Manhattan, comme prévu.</mark>

### Temps d'exécution

A* <mark>(Manhattan)</mark> est de l'ordre de la milliseconde (<mark>0,0017 à 0,0039 s</mark>), contre <mark>0,1 à 1,7 s</mark> pour BFS et jusqu'à <mark>10 s</mark> pour IDS. Le temps suit le nombre d'itérations, mais chaque itération de A* coûte un peu plus cher (calcul de l'heuristique et file de priorité). DFS peut être rapide (<mark>0,018 s</mark> sur Ex1-1) mais son résultat n'est pas utilisable.

<mark>Comme vu en séance 4, on ne peut pas se fier entièrement au temps mesuré : il dépend de la machine et de sa charge. Nos premières mesures, prises sur une autre machine, étaient environ deux fois plus faibles. Les itérations et la taille des listes sont les mesures principales ; le temps est indicatif et n'est comparé qu'entre mesures prises sur la même machine.</mark>

### Frontière

BFS grossit jusqu'à 7 000 à 24 000 états, et DFS jusqu'à 2 000 à 43 000 selon l'input. La frontière de A* <mark>(Manhattan)</mark> reste entre <mark>128</mark> et 314 états. IDS a la plus petite frontière (17 à 25), car il ne garde que le chemin courant et ses voisins. <mark>Avec les tuiles mal placées sur Ex1-4, A* explore toujours moins d'états que BFS (68 222 contre 178 224), mais sa frontière (25 864) dépasse celle de BFS (24 048) : une heuristique faible fait perdre l'avantage mémoire de A*.</mark>

### Mémoire

La frontière donne un indice de la mémoire utilisée, mais elle ne la mesure pas entièrement, car chaque algorithme garde aussi un ensemble d'états visités ou fermés. BFS et DFS stockent tous les états rencontrés. IDS économise la frontière mais a un ensemble `visited` par limite de profondeur. A* garde la liste fermée, qui reste petite ici parce qu'il explore peu d'états<mark> : 192 à 607 états avec Manhattan, contre 748 à 61 097 avec les tuiles mal placées</mark>. Nous n'avons pas mesuré la mémoire en octets.

## Apprentissages et remarques <mark>(partie 1)</mark>

- A* donne la solution optimale de BFS pour une fraction du coût, sur les trois inputs testés. Sur ces puzzles, il est de loin le meilleur choix.
- DFS est rapide sur certains inputs, mais ses chemins de plusieurs dizaines de milliers de coups le rendent inutilisable si on veut une solution courte.
- IDS est optimal avec peu de mémoire, mais il refait beaucoup de travail. Sur Ex1-4, il fait 14 fois plus d'itérations que BFS.
- <mark>Le choix de l'heuristique compte autant que l'algorithme : avec les tuiles mal placées, A* explore jusqu'à 110 fois plus d'états qu'avec Manhattan, et sa frontière peut dépasser celle de BFS.</mark>
- Le point le plus délicat de A* était l'adaptation de la référence : la représentation du plateau (liste plate contre grille 3x3) et les compteurs d'itérations, de frontière <mark>et d'états explorés</mark>, pour que les résultats restent comparables aux autres algorithmes.
- Une erreur d'implémentation sur la boucle de l'heuristique (parcourir 3 cases au lieu de 9) a rendu l'heuristique inadmissible. Une comparaison de la distance avec celle de BFS permet de détecter ce genre d'erreur.
- Le 8-puzzle est petit. Le temps de A* est de l'ordre de la milliseconde, donc plus sensible au bruit de mesure <mark>et à la machine utilisée</mark>, et trois inputs ne suffisent pas pour des conclusions générales.

## Références utilisées <mark>(partie 1)</mark>

- https://www.geeksforgeeks.org/artificial-intelligence/8-puzzle-problem-in-ai/
- Jebbar, O. (2026). Intelligence artificielle et reconnaissance des formes (6GEI608, <mark>séances 3 et 4</mark> : recherche dans un graphe, A*<mark>, heuristiques</mark>). Université du Québec à Chicoutimi.

---

## Partie 2 : problème d'optimisation, plusieurs états objectifs (Sudoku)

<mark>**Toute la partie 2 est nouvelle** (le README existant n'avait que le titre de cette partie et deux références). Elle n'est pas surlignée ligne par ligne.</mark>

### Puzzles

Dix puzzles générés sur https://qqwing.com/generate.html (`data/input-sudoku/`), avec leurs métadonnées : ligne 1 = puzzle (81 caractères, `.` = vide), ligne 2 = solution, puis les ratings qqwing (difficulté, nombre de cases données, techniques nécessaires, nombre d'essais `Guesses`). La solution est lue par le parser mais n'est jamais utilisée par les algorithmes.

| Puzzle | Difficulté | Cases données | Guesses |
|---|---|---|---|
| 01, 02 | Simple | 24, 28 | 0 |
| 03, 04, 09, 10 | Easy | 25, 24, 25, 26 | 0 |
| 05, 06 | Intermediate | 24, 26 | 0 |
| 07, 08 | Expert | 26, 25 | 2, 5 |

### Utilisation

Chaque algorithme se lance directement :

```
uv run -m src.sudoku.<algo> [fichier de puzzle] [nombre d'exécutions]
```

où `<algo>` est `hill_climbing`, `genetic_tournament`, `genetic_truncation` ou `genetic_hc`. Sans fichier, les 10 puzzles de `data/input-sudoku/` sont lancés ; sans nombre, la constante `N_RUNS` du fichier s'applique. Exemple : `uv run -m src.sudoku.genetic_hc data/input-sudoku/Sudoku-07-expert.txt 10`.

Chaque lancement reçoit un identifiant (date et heure) et son propre dossier (`src/sudoku/runner.py`) :

```
results/sudoku/<algo>/<ID>/
    stats.txt                 récapitulatif du lancement (résolues, temps moyen, itérations moyennes par puzzle)
    <puzzle>/runNN.log        journal de l'exécution
    <puzzle>/runNN.txt        une ligne « génération⇥conflits du meilleur » par itération, puis itérations, temps (s), redémarrages
    <puzzle>/stats.txt        résolues, tableau par exécution, moyenne / écart-type / min / max (temps, itérations, redémarrages, conflits)
```

Le niveau de journalisation se règle par `LOG_LEVEL` en tête de chaque fichier : `INFO` donne la présentation des résultats (nom du puzzle, grille de départ, paramètres, redémarrages, résultat final, grille obtenue) ; `DEBUG` ajoute le détail de chaque itération.

### Modélisation

- **État :** une grille de 81 cases entièrement remplie, les cases données intactes. Chaque **ligne** contient toujours les chiffres 1 à 9 ; seuls les colonnes et les blocs peuvent être en conflit.
- **État initial :** `fill_rows` (`src/sudoku/commun.py`) remplit chaque ligne au hasard avec ses chiffres manquants.
- **Coût (fitness) :** `conflicts`, le nombre de **paires** de cases contenant le même chiffre dans une même colonne ou un même bloc (fonction des 8 reines vue en cours). Il vaut 0 seulement pour la solution ; il est à minimiser.
- **Voisin :** échange de deux cases **modifiables** d'une même ligne. Le cours définit un voisin comme le changement du contenu d'une case ; changer une seule case créerait forcément un doublon dans sa ligne. Un échange équivaut à deux changements de case coordonnés qui gardent les lignes valides ; c'est l'opérateur standard pour cette représentation, et il réduit l'espace de recherche.
- **Cases données :** jamais modifiées, ni par les voisins, ni par la mutation, ni par le crossover.

**Restriction aux chiffres permis (connaissance du domaine, déclarée).** Avec `USE_ALLOWED_DIGITS = True` (valeur utilisée), `fill_rows` ne place dans une case vide que des chiffres **absents des cases données de sa colonne et de son bloc** (`allowed_digits`, `place_row`). Un conflit avec une case donnée est certain et définitif (une case donnée ne bouge jamais) ; la solution n'est jamais exclue (vérifié sur les 10 puzzles avec la solution du fichier). Il s'agit d'une seule passe de filtrage, sans déduction en cascade. Effet : l'espace des grilles possibles passe d'environ 10²⁸ à 10¹⁴ selon le puzzle, et le nombre moyen de conflits au départ de 56,6 à 38,0 sur Sudoku-01. Les mutations et voisins peuvent ensuite replacer un chiffre interdit ; la fitness le pénalise. Tous les algorithmes utilisent le même `fill_rows`, la comparaison entre eux reste donc équitable. L'effet de cette restriction est mesuré plus bas.

### Hill climbing (`hill_climbing.py`)

Hill climbing à **montée la plus raide** (*steepest ascent*), adapté d'aima-python (`search.py`), avec **redémarrages aléatoires**.

**Déroulement.**
1. **État initial :** une grille `fill_rows` (lignes valides, chiffres permis par les cases données).
2. **À chaque itération :** on enregistre les conflits de l'état courant, puis on génère **tous** ses voisins avec `get_neighbors` : pour chaque ligne, tous les échanges de deux cases modifiables (de 140 à 160 voisins selon le puzzle). Chaque voisin est évalué par `value = -conflicts` (maximiser `value` revient à minimiser les conflits).
3. **Déplacement :** on choisit le meilleur voisin (`argmax_random_tie`, égalités départagées au hasard). S'il est **strictement** meilleur que l'état courant, il devient l'état courant.
4. **Optimum local :** si aucun voisin n'est strictement meilleur (optimum local ou plateau), on **redémarre** d'une nouvelle grille `fill_rows` et on compte un redémarrage. C'est la solution proposée en cours contre les optimums locaux : réexécuter avec plusieurs initialisations aléatoires (séance 4).
5. **Arrêt :** à la solution (0 conflit), ou après `MAX_ITERATIONS = 100 000` itérations, redémarrages compris (≈ 350 itérations par seconde, soit ≈ 5 min au plus). En cas d'échec, on retourne la **meilleure grille vue** sur toute l'exécution, et non la grille courante (qui peut être une grille aléatoire juste après un redémarrage).

**Sorties.** Le nombre d'itérations compte tous les pas, redémarrages compris ; le fichier de résultats donne les conflits de l'état courant à chaque itération (la courbe remonte à chaque redémarrage) et le nombre de redémarrages.

**Comportement observé.**
- Une montée depuis une grille aléatoire atteint un optimum local en une vingtaine de pas environ, puis l'algorithme redémarre ; les optimums locaux se situent le plus souvent entre 2 et 8 conflits.
- Le hill climbing trouve la solution, mais il peut lui falloir des milliers de redémarrages : les premières versions, sans limite, mettaient plusieurs heures sur certains puzzles. Chaque essai repart de zéro et ignore ce que les essais précédents ont trouvé.
- Avec un budget de 20 000 itérations, il a résolu 5 exécutions sur 9 (puzzles 01, 05, 07) avec la restriction aux chiffres permis, et 0 sur 9 sans elle.

**Propriétés.** Le hill climbing ne garde qu'une grille (mémoire minimale) et chaque pas coûte l'évaluation de ses 140 à 160 voisins. Il est **incomplet** : un optimum local à k > 0 conflits ne dit rien de la distance à la solution. Avec des redémarrages, il devient complet **en probabilité** seulement, à temps infini ; sous un budget fixe, on mesure un taux de succès.

<mark>[À COMPLÉTER : résultats de l'évaluation finale (10 puzzles × N exécutions) : taux de succès, temps, itérations et redémarrages moyens.]</mark>

### Algorithmes génétiques

Les trois versions partagent la représentation, la fitness (`conflicts`, à minimiser), le crossover et la mutation ; elles diffèrent par la sélection et par les mécanismes ajoutés. Toutes s'arrêtent à la solution ou après `MAX_GENERATIONS` générations, et retournent la meilleure grille vue sur toute l'exécution (pas seulement celle de la dernière génération).

- **Population initiale :** `POP_SIZE` grilles `fill_rows`.
- **Fitness :** nombre de paires en conflit, à minimiser. Les deux sélections ne font que comparer les scores : aucune transformation en valeur positive n'est nécessaire.
- **Crossover uniforme par lignes :** chaque ligne de l'enfant vient, au hasard, de l'un ou l'autre parent. Les lignes étant copiées entières, elles restent valides et les cases données sont conservées (le professeur recommandait de trancher par lignes ou par colonnes). Le crossover uniforme est une variante de la coupe par lignes : avec une coupe à un point, les lignes voisines d'un même côté de la coupe ne sont jamais séparées (8 enfants possibles au lieu de 2⁹ = 512).
- **Mutation :** avec la probabilité `MUTATION_RATE`, un ou plusieurs échanges de deux cases modifiables d'une même ligne (comme le voisin du hill climbing).
- **Remplacement :** toute la population est remplacée à chaque génération.

#### 1. Sélection par tournoi (`genetic_tournament.py`)

Version de base, adaptée du code du livre (AIMA, Figure 4.8). Pour choisir un parent, on tire `TOURNAMENT_K` candidats ; le meilleur gagne avec la probabilité `TOURNAMENT_P`, sinon le suivant avec la même probabilité, et ainsi de suite (tournoi probabiliste : avec `TOURNAMENT_P = 1.0`, le meilleur gagne toujours). Le tournoi a été préféré à la roulette : il n'exige pas de fitness positive et sa pression se règle avec un seul paramètre.

#### 2. Sélection par troncature uniforme (`genetic_truncation.py`)

Créée pour **préserver la diversité**. Avec le tournoi, la population descend rapidement d'un même individu (convergence prématurée) et se fige dans un faux minimum. La troncature dirige le groupe **en éliminant les pires** plutôt qu'en favorisant les meilleurs : seuls les individus dont le score est au plus le quantile `TRUNCATION_QUANTILE` de la génération peuvent être parents, et ils sont tirés **uniformément** (un individu à 5 conflits n'a pas plus de chances qu'un individu à 25). Le nombre d'échanges d'une mutation est une fraction des cases modifiables (`MUTATION_SWAP_RATE`). Les journaux DEBUG affichent la distance moyenne entre grilles et la proportion de cases figées, pour suivre la diversité.

#### 3. Génétique et hill climbing (`genetic_hc.py`)

Algorithme **mémétique** : la troncature uniforme, plus un hill climbing appliqué à une fraction des enfants (`HILL_CLIMBING_RATE`) pendant au plus `HILL_CLIMBING_STEPS` pas (même voisinage et même règle que `hill_climbing.py`, sans redémarrage interne). Si le meilleur score de l'essai en cours n'est pas battu pendant `RESTART_STAGNATION` générations, toute la population est recréée. Il réunit le meilleur des deux mondes : le génétique combine les lignes de bons optimums locaux et garde la mémoire des bons essais ; le hill climbing fait les derniers échanges précis que le génétique seul ne trouve pas. C'est un hybride, présenté comme tel.

#### Paramètres

| Paramètre | `genetic_tournament` | `genetic_truncation` | `genetic_hc` |
|---|---|---|---|
| `POP_SIZE` | 20 000 | 1 000 | 500 |
| Sélection | tournoi, k = 2, p = 0,8 | troncature, quantile 0,95 | troncature, quantile 0,5 |
| `MUTATION_RATE` | 0,3 | 0,01 | 0,1 |
| Échanges par mutation | 10 | taux 1,0 des cases modifiables | taux 0,2 des cases modifiables |
| `MAX_GENERATIONS` | 5 000 | 5 000 | 50 000 |
| Hill climbing | — | — | 10 % des enfants, 5 pas |
| Redémarrage | — | — | après 30 générations sans progrès |

<mark>[À VÉRIFIER : valeurs des paramètres au moment des évaluations finales.]</mark>

### Résultats

<mark>[À COMPLÉTER à partir de `results/sudoku/<algo>/<ID>/stats.txt` : pour chaque algorithme et chaque puzzle, exécutions résolues, temps moyen et écart-type, itérations moyennes, redémarrages moyens.]</mark>

| Puzzle | Hill climbing | Génétique (tournoi) | Génétique (troncature) | Génétique + hill climbing |
|---|---|---|---|---|
| 01 | | | 0/10 | 10/10, 27,6 s ± 16,0 |
| 02 | | | 0/10 | 10/10, 8,0 s ± 4,6 |
| 03 | | | 0/10 | |
| 04 | | | 0/10 | |
| 05 | | | 0/10 | |
| 06 … 10 | | | | |

<mark>(Résultats partiels au moment de la rédaction du brouillon.)</mark>

**Effet de la restriction aux chiffres permis** (budgets réduits : 20 000 itérations pour le hill climbing, 500 générations pour le génétique + hill climbing ; puzzles 01, 05, 07 ; 3 exécutions chacun) :

| Algorithme | Chiffres permis | Résolues | Temps moyen |
|---|---|---|---|
| Génétique + hill climbing | oui | 9/9 | ≈ 51 s |
| Génétique + hill climbing | non | 5/9 (4 échecs à 2 conflits) | ≈ 284 s |
| Hill climbing | oui | 5/9 | — |
| Hill climbing | non | 0/9 | — |

### Analyse

**Le génétique pur se coince lui aussi.** Le cours présente les génétiques comme un moyen de ne pas se coincer dans les optimums locaux. Nos mesures nuancent cette affirmation : le génétique pur (tournoi ou troncature) **réduit** le risque mais ne le supprime pas, et plafonne entre 2 et 6 conflits. Deux mécanismes l'expliquent :
- **convergence prématurée** : avec le tournoi, le meilleur individu envahit la population en quelques générations (environ ln N / ln k) ; croiser des grilles presque identiques ne crée plus rien ;
- **dérive génétique** : même sans aucun avantage aux meilleurs (troncature uniforme), une population finie perd sa diversité, plus vite si elle est petite, car certaines lignées disparaissent au hasard. La dérive fige les lignes présentes, pas celles de la solution.

Il faut **à la fois** de la diversité et une pression de sélection : sans pression, la population erre (troncature à 0,95 : moyenne stable vers 37 conflits avec 20 000 individus) ; avec trop de pression, elle converge vers un faux minimum.

**Un conflit n'est pas une case fausse.** Sur le Sudoku-03, 114 essais bloqués sur 116 du génétique + hill climbing l'étaient exactement à 2 conflits. Comparées à la solution, ces grilles à 2 conflits comptaient de 9 à 33 cases fausses sur 4 à 8 lignes. Les inversions forment une chaîne (par exemple un 5 et un 6 échangés dans deux lignes différentes) : chaque colonne garde un exemplaire de chaque chiffre, et les conflits n'apparaissent qu'aux bouts de la chaîne. Une grille à 2 conflits est presque une **autre** grille valide ; pour atteindre la solution, il faut changer plusieurs lignes à la fois, et chaque échange isolé ajoute des conflits. C'est un **faux minimum** : le nombre de conflits mesure la validité, pas la distance à la solution. Allonger le hill climbing n'aide pas, puisqu'il s'arrête dès qu'aucun échange n'améliore.

**Pourquoi le génétique + hill climbing fonctionne.** Le hill climbing seul repart toujours d'une grille aléatoire et oublie ses essais (il a trouvé des solutions, mais après plusieurs heures) ; le génétique seul s'approche de la solution mais ne sait pas la finir. Le mémétique part de combinaisons de bons optimums locaux et le hill climbing finit le travail ; les redémarrages sur stagnation remplacent la diversité perdue. Sa pression de sélection doit laisser les grilles améliorées se reproduire : avec la troncature à 0,5, il a résolu 9 exécutions sur 9 (puzzles 01, 05, 07) ; à 0,95, seulement 3 sur 9.

**Difficulté qqwing et difficulté pour la recherche.** La difficulté qqwing mesure les techniques de déduction humaines. Elle ne prédit pas la difficulté pour une recherche par échanges : le Sudoku-07 « expert » a été résolu en quelques secondes, alors que le Sudoku-03 « easy » a demandé jusqu'à 23 redémarrages (grand bassin de faux minima à 2 conflits).

**Connaissance du domaine.** Une seule passe de filtrage à partir des cases données a presque doublé le taux de réussite (génétique + hill climbing : 5/9 → 9/9 ; hill climbing : 0/9 → 5/9). La connaissance du problème a pesé plus lourd que le réglage des paramètres. Aller plus loin (propagation en cascade, comme Norvig) résoudrait la plupart des puzzles sans recherche : 8 de nos 10 puzzles ont `Guesses: 0`, c'est-à-dire qu'ils se résolvent par déduction pure. Nous ne l'avons pas fait, pour que ce soient bien le hill climbing et le génétique qui résolvent.

**Complétude.** Le hill climbing et le génétique sont des recherches **incomplètes** : 0 conflit prouve qu'on a la solution, mais un optimum à 2 conflits ne dit rien de la distance à la solution. Le hill climbing à redémarrages est complet seulement en probabilité, à temps infini. Une recherche complète (propagation de contraintes et recherche en profondeur, comme Norvig : 95 puzzles difficiles résolus en 0,04 s en moyenne) donne une garantie en temps borné.

### Autres mécanismes essayés (non retenus)

Pendant le développement, nous avons essayé : élitisme (les élites attirent la population vers leur optimum local), mutation adaptative (le taux monte quand la recherche stagne ; sans élitisme, la population devient aléatoire), modèle en îles (les migrations finissent par uniformiser les îles), refus des doublons et mutation ciblée sur les cases en conflit (gain faible), crossover guidé (gain faible, deux fois plus lent), sélection uniforme en fitness (FUSS) et sélection vers le milieu (diversité sans direction), quota d'exploration pour les mutants (la sélection filtre aussitôt la nouveauté). Tous retardaient la convergence sans la changer.

### Pistes

- **Recuit simulé** (séance 4) : accepter parfois un voisin pire permettrait de défaire une chaîne d'inversions comme celle du Sudoku-03.
- **Voisinage étendu** : des paires d'échanges dans deux lignes différentes (beaucoup plus coûteux).
- **Exécutions en parallèle** dans le runner, pour réduire la durée des évaluations.

---

## Ce que nous avons appris

- Le bon outil dépend du problème : A* est exact et optimal quand une heuristique admissible guide la recherche ; le hill climbing et le génétique sont adaptés à l'optimisation quand beaucoup de solutions sont acceptables, moins quand une seule solution exacte est attendue, comme au Sudoku.
- Une heuristique dominante réduit fortement le nombre d'états explorés (× 110 sur Ex1-4) sans perdre l'optimalité.
- Un algorithme génétique est fort pour s'approcher d'une solution, faible pour la finir ; la diversité sans pression de sélection ne converge pas, et la pression sans diversité se coince.
- Ajuster des paramètres sur un seul puzzle mène au surapprentissage : il faut mesurer sur plusieurs puzzles, et mesurer chaque mécanisme seul avant de conclure qu'il aide.
- Toute connaissance du problème ajoutée à un algorithme doit être déclarée et son effet mesuré.
- Un temps d'exécution n'est comparable que sur la même machine, dans les mêmes conditions.
- <mark>[À COMPLÉTER : défis rencontrés par l'équipe.]</mark>

## Références

- https://www.geeksforgeeks.org/artificial-intelligence/8-puzzle-problem-in-ai/
- Russell, S. et Norvig, P. *Artificial Intelligence: A Modern Approach* (Figure 4.8, algorithme génétique) ; https://github.com/aimacode/aima-python
- Norvig, P. *Solving Every Sudoku Puzzle*. https://www.norvig.com/sudoku.html
- *Solving Sudoku with genetic algorithms* (2010). https://fakeguido.blogspot.com/2010/05/solving-sudoku-with-genetic-algorithms.html
- Jebbar, O. (2026). Intelligence artificielle et reconnaissance des formes (6GEI608, séances 3 et 4). Université du Québec à Chicoutimi.
- https://www.geeksforgeeks.org/dsa/check-if-given-sudoku-board-configuration-is-valid-or-not/
