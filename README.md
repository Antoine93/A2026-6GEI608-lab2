# A2026-6GEI608-lab2

Laboratoire 2 de 6GEI608 (UQAC).

## Partie 1 : résolution du 8-puzzle avec l'algorithme A*

### Utilisation

Similaire au fonctionnement du lab 1, le programme demande le fichier d'entrée (ex. `data/input-Ex1/Ex1-1.txt`) puis l'algorithme (bfs, dfs, ids ou a_star).
Il vérifie d'abord que le puzzle est solvable (parité des inversions), puis exécute la recherche 10 fois.

Pour chaque exécution, un fichier est écrit dans `results/<algo>/<input>_runNN.txt` :
- à partir de la première ligne : numéro_itération \t taille_de_frontière
- avant-dernière ligne : nombre total d'états explorés
- dernière ligne : temps d'exécution de la fonction de recherche

## Algorithme A*

- **Fonction d'évaluation :** `f(n) = g(n) + h(n)`, où `g` est le cout pour arriver à n (chaque coup coûte 1 dans notre 8puzzle) et `h` l'heuristique.
- **Heuristique utilisé:** distance de Manhattan, soit la somme, pour chaque tuile (case vide exclue), de la distance en lignes et en colonnes entre sa position et sa position cible.

### Implémentation

Nous sommes partis de l'implémentation de référence de GeeksforGeeks et nous l'avons adaptée petit à petit au lieu de la réécrire, pour que A* s'intègre dans la structure du lab 1 sans modifier BFS, DFS et IDS.

La liste ouverte est une file de priorité (`heapq`) ordonnée par `f`. La taille de la frontière enregistrée à chaque itération est la taille de cette liste avant le dépilement. Une itération correspond à un état dépilé, comme pour BFS, DFS et IDS, ce qui rend les résultats comparables. La liste fermée est un ensemble des plateaux déjà développés.

De la référence (`src/solvers/a_star.py`), nous avons gardé la boucle A* (`heapq`, `closed_list`, `move_tile`, le dictionnaire `moves` et les tests de bord de la case vide), la représentation du plateau en liste plate de 9 cases avec `0` pour la case vide, et la fonction `heuristic`. La référence est déjà correcte et connue : en la modifiant le moins possible, nous limitons le risque d'introduire des erreurs dans l'algorithme.

Du lab 1, nous avons réutilisé :
- `main.py` : le dictionnaire `SOLVERS` qui associe un nom d'algorithme à sa fonction, la question à l'utilisateur, la boucle de 10 exécutions et le calcul du temps moyen. A* y a été ajouté sous le nom `a_star`, sans changer le reste.
- `parse_puzzle_file`, qui lit le fichier d'entrée et retourne la grille 3x3 (`None` pour la case vide) avec la position de la case vide.
- `is_solvable`, qui refuse les puzzles non solvables avant la recherche.
- `write_run_file` et `output_path`, qui écrivent un fichier par exécution dans le format demandé.

Ces composants ne dépendent pas de l'algorithme. Les réutiliser garantit que les fichiers de résultats de A* ont le même format que ceux de BFS, DFS et IDS, donc que la comparaison est équitable.

Nous avons apporté les modifications suivantes à la référence :
1. Suppression du code exécuté à l'import. La référence contenait un état initial codé en dur et une résolution à la fin du fichier. Comme `src/solvers/__init__.py` importe le module, ce code se serait exécuté à chaque lancement de `main.py`.
2. Même interface que les autres algorithmes. La fonction devient `solve_puzzle_a_star(start, x, y)` et retourne `(état final ou None, nombre d'itérations, tailles de frontière)`. C'est ce que `main.py` attend de tous les solveurs, ce qui permet de les appeler de la même façon.
3. Ajout des compteurs. Avant chaque `heappop`, nous enregistrons la taille de la liste ouverte. Après, nous incrémentons les itérations. C'est le même emplacement que dans BFS, DFS et IDS.
4. Ajout de deux fonctions de conversion, `to_flat` et `to_matrix`. Le parser et les autres algorithmes utilisent une grille 3x3 avec `None`, alors que la référence utilise une liste plate avec `0`. Nous convertissons le plateau initial à l'entrée de la fonction et le plateau final à la sortie, ce qui évite de réécrire le code de la référence. La conversion se fait une seule fois par exécution, donc son coût devrait être négligeable.
5. Distance affichée avec `result.depth`. Dans `main.py`, `get_actions` du lab 1 reconstruit le chemin avec la position `x`, `y` et le parent de son propre `PuzzleState`. Celui de A* a une autre forme (il garde le coup et le coût `f`), donc nous lisons directement la profondeur, qui est égale au nombre de coups.
6. Correction de l'heuristique. Notre première version parcourait seulement 3 cases au lieu de 9, ce qui rendait l'heuristique inadmissible. Nous sommes revenus à la boucle sur 9 cases de la référence, et la distance obtenue est maintenant identique à celle de BFS.

Les paramètres `x` et `y` ne servent pas à A*, qui retrouve la case vide avec `.index(0)`. Ils sont conservés pour garder la même signature que les autres solveurs. Les fonctions `print_board`, `print_solution` et `colored` de la référence sont restées dans le fichier mais ne sont pas utilisées par `main.py`.

### Pourquoi avons nous choisi la distance de Manhattan comme heuristique

- **Admissible :** un coup déplace une seule tuile d'une seule case, donc il réduit la somme des distances d'au plus 1. L'heuristique ne surestime jamais le coût restant, et A* trouve donc un chemin optimal.
- **Cohérente :** le changement de `h` entre deux états voisins est d'au plus 1, ce qui est le coût d'un coup. Une fois un plateau développé, on ne trouvera pas de meilleur chemin vers lui.
- **Informative et peu coûteuse :** elle se calcule en une passe sur 9 cases et guide beaucoup mieux la recherche qu'une absence d'information (cas de BFS).
- **Référencée :** c'est l'heuristique de la référence GeeksforGeeks que nous avons trouvée durant la revue de l'état de l'art.

Nous n'avons pas comparé avec d'autres heuristiques (par exemple le nombre de tuiles mal placées), donc nous ne mesurons pas ici le gain de Manhattan par rapport à elles.

## Comparaison des algorithmes

Résultats obtenus avec `main.py` (10 exécutions par cas). Ex1-3 n'est pas solvable.

| Input | Algo | Distance | Itérations | Frontière max | Temps moyen |
|---    |---   |---       |---         |---            |---          |
| Ex1-1 | BFS  | 20       | 61 757     | 18 858        | 0,243 s     |
|       | DFS  | 2 698    | 2 775      | 2 159         | 0,009 s     |
|       | IDS  | 20       | 201 154    | 20            | 0,350 s     |
|       | **A\*** | **20**| **286**    | 178           | **0,0008 s**|
| Ex1-2 | BFS  | 17       | 12 717     | 7 344         | 0,041 s     |
|       | DFS  | 65 971   | 96 880     | 42 890        | 0,706 s     |
|       | IDS  | 17       | 51 436     | 17            | 0,086 s     |
|       | **A\*** | **17**| **195**    | 131           | **0,0006 s**|
| Ex1-4 | BFS  | 28       | 178 224    | 24 048        | 0,852 s     |
|       | DFS  | 64 830   | 106 784    | 42 913        | 0,704 s     |
|       | IDS  | 28       | 2 492 752  | 25            | 5,325 s     |
|       | **A\*** | **28**| **611**    | 314           | **0,0018 s**|

### Optimalité

BFS, IDS et A* trouvent la même distance sur les trois inputs. DFS ne garantit pas l'optimalité : il retourne le premier chemin trouvé, qui compte de 2 698 à 65 971 coups alors que la solution optimale en compte 17 à 28.

### Itérations

A* explore de 100 à 4 000 fois moins d'états que BFS (611 contre 178 224 sur Ex1-4) et jusqu'à 4 000 fois moins qu'IDS (2,5 millions). L'heuristique oriente la recherche vers l'état but au lieu d'explorer tous les états par niveau. IDS est le plus coûteux, car il refait la recherche à chaque nouvelle limite de profondeur.

### Temps d'exécution

A* est de l'ordre de milliseconde (0,0006 à 0,0018 s), contre 0,04 à 0,85 s pour BFS et jusqu'à 5,3 s pour IDS. Le temps suit le nombre d'itérations, mais chaque itération de A* coûte un peu plus cher (calcul de l'heuristique et file de priorité). DFS peut être rapide (0,009 s sur Ex1-1) mais son résultat n'est pas utilisable.

### Frontière

BFS grossit jusqu'à 7 000 à 24 000 états, et DFS jusqu'à 2 000 à 43 000 selon l'input. La frontière de A* reste entre 131 et 314 états. IDS a la plus petite frontière (17 à 25), car il ne garde que le chemin courant et ses voisins.

### Mémoire

La frontière donne un indice de la mémoire utilisée, mais elle ne la mesure pas entièrement, car chaque algorithme garde aussi un ensemble d'états visités ou fermés. BFS et DFS stockent tous les états rencontrés. IDS économise la frontière mais a un ensemble `visited` par limite de profondeur. A* garde la liste fermée, qui reste petite ici parce qu'il explore peu d'états. Nous n'avons pas mesuré la mémoire en octets.

## Apprentissages et remarques

- A* donne la solution optimale de BFS pour une fraction du coût, sur les trois inputs testés. Sur ces puzzles, il est de loin le meilleur choix.
- DFS est rapide sur certains inputs, mais ses chemins de plusieurs dizaines de milliers de coups le rendent inutilisable si on veut une solution courte.
- IDS est optimal avec peu de mémoire, mais il refait beaucoup de travail. Sur Ex1-4, il fait 14 fois plus d'itérations que BFS.
- Le point le plus délicat de A* était l'adaptation de la référence : la représentation du plateau (liste plate contre grille 3x3) et les compteurs d'itérations et de frontière, pour que les résultats restent comparables aux autres algorithmes.
- Une erreur d'implémentation sur la boucle de l'heuristique (parcourir 3 cases au lieu de 9) a rendu l'heuristique inadmissible. Une comparaison de la distance avec celle de BFS permet de détecter ce genre d'erreur.
- Le 8-puzzle est petit. Le temps de A* est de l'ordre de la milliseconde, donc plus sensible au bruit de mesure, et trois inputs ne suffisent pas pour des conclusions générales.

## Références utilisées

- https://www.geeksforgeeks.org/artificial-intelligence/8-puzzle-problem-in-ai/
- Jebbar, O. (2026). Intelligence artificielle et reconnaissance des formes (6GEI608, séance 3, recherche dans un graphe, A*). Université du Québec à Chicoutimi.
