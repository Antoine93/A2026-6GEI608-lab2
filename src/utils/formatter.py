# Module qui écrit les résultats d'une exécution dans un fichier texte

import os

# écrit le fichier de sortie d'une exevution
# format du lab 1 : une ligne « itération \t valeur » par itération (séparateur « \t » écrit tel quel, comme dans l'énoncé),
# puis le nombre d'itérations, le temps, et (si fourni) les redémarrages
# une valeur peut être un tuple (ex. A* : frontière, explorés) : ses éléments sont séparés de la même façon
def write_run_file( output_file, frontier_sizes, explored, elapsed_time, restart_count=None):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for i, size in enumerate(frontier_sizes, start=1):
            values = size if isinstance(size, tuple) else (size,)
            f.write(f"{i} \\t " + " \\t ".join(str(v) for v in values) + "\n")

        f.write(f"{explored}\n")
        f.write(f"{elapsed_time}\n")
        if restart_count is not None:
            f.write(f"{restart_count}\n")

# construit le chemin complet du fichier de sortie
def output_path(base_path, algo, input_file, run):
    name = os.path.splitext(os.path.basename(input_file))[0]
    return os.path.join(base_path,algo, f"{name}_run{run:02d}.txt")