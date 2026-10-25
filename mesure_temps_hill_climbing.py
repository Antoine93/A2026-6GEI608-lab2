# lance le hill climbing sur les puzzles de data/input-sudoku, un processus par puzzle, sans limite de temps et écrit le temps de chaque puzzle dans results/hill_climbing_base_sans_plafond/

import glob
import os
import subprocess
import sys
import time

if sys.version_info < (3, 10):
    sys.exit(f"Python 3.10 ou plus est nécessaire")

# les messages s'affichent même si la console ne connaît pas un caractère
sys.stdout.reconfigure(errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "results", "hill_climbing_base_sans_plafond")

# intervalle (en secondes) entre deux messages de suivi
HEARTBEAT = 600

# ordre de la file d'attente choisie (lancement sans argument)
DEFAULT_PUZZLES = ["Sudoku-01-simple", "Sudoku-03-easy", "Sudoku-05-intermediate", "Sudoku-07-expert", "Sudoku-09-easy", "Sudoku-02-simple", "Sudoku-04-easy", "Sudoku-06-intermediate", "Sudoku-08-expert", "Sudoku-10-easy"]

# affiche un message à l'écran et l'ajoute à suivi.txt pour la tracabilité
def say(message):
    print(message, flush=True)
    with open(os.path.join(OUT, "suivi.txt"), "a", encoding="utf-8") as f:
        f.write(message + "\n")


# résout un puzzle avec le hill climbing de base sans plafond
def run_one(filename):
    
    # se placer à la racine du projet pour que les imports de src fonctionnent
    os.chdir(ROOT)
    sys.path.insert(0, ROOT)
    from src.sudoku.parser import parse_sudoku_file
    from src.sudoku.commun import conflicts
    from src.sudoku.hill_climbing import hill_climbing

    # mesurer seulement le temps de la recherche
    puzzle, solution = parse_sudoku_file(filename)
    print(f"début : {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    # temps d'horloge (perf_counter) et temps processeur (process_time) de la recherche seule
    start = time.perf_counter()
    cpu_start = time.process_time()
    result, iterations, costs, restart_count = hill_climbing(puzzle)
    elapsed = time.perf_counter() - start
    cpu = time.process_time() - cpu_start

    print(f"fin : {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    # les conflits restants sont recalculés sur la grille retournée (0 = sudoku résolu)
    print(f"conflits : {conflicts(result)} (0 = résolu)")
    print(f"itérations : {iterations}")
    print(f"redémarrages : {restart_count}")
    print(f"temps (horloge) : {elapsed:.1f} s")
    print(f"temps (processeur) : {cpu:.1f} s", flush=True)


# retourner  les 10 puzzles dans l'ordre de DEFAULT_PUZZLES, sinon les fichiers donnés en argument au début du script
def choose_files(args):
    all_files = sorted(glob.glob(os.path.join(ROOT, "data", "input-sudoku", "*.txt")))
    if not args or args == ["tous"]:
        by_name = {os.path.splitext(os.path.basename(f))[0]: f for f in all_files}
        if any(name not in by_name for name in DEFAULT_PUZZLES):
            sys.exit("Puzzles introuvables dans data/input-sudoku : vérifiez que le dossier data est bien copié.")
        return [by_name[name] for name in DEFAULT_PUZZLES]
    return [os.path.abspath(a) for a in args]


# écrire resume.txt pour garder la trace des temps de chaque puzzle, même si on arrête
def write_summary(lines):
    with open(os.path.join(OUT, "resume.txt"), "w", encoding="utf-8") as out:
        out.write("\n".join(lines) + "\n")


# démarre un processus par puzzle et en démarre un nouveau dès qu'un puzzle se termine
def launcher(args):
    os.makedirs(OUT, exist_ok=True)

    # option --max N pour un nombre maximal de processus en même temps (multithreading)
    max_parallel = max(1, (os.cpu_count() or 2) - 1)
    if "--max" in args:
        i = args.index("--max")
        max_parallel = max(1, int(args[i + 1]))
        args = args[:i] + args[i + 2:]
    files = choose_files(args)

    say(f"=== {time.strftime('%Y-%m-%d %H:%M:%S')} | Python {sys.version.split()[0]} | {os.cpu_count()} coeurs ===")
    say(f"{len(files)} puzzle(s) dans la file, sans limite de temps, {max_parallel} processus en parallèle")

    pending = list(files)       # puzzles pas encore démarrés
    running = []                # (processus, nom, heure de départ, fichier .log) des puzzles en cours
    lines = []                  # lignes de resume.txt
    last_report = time.perf_counter()   # heure du dernier message de suivi

    # sortie des processus en UTF-8 pour que les accents s'écrivent correctement dans les .log
    env = dict(os.environ, PYTHONIOENCODING="utf-8")

    try:
        # boucler jusqu'à ce que tous les puzzles soient terminés
        while pending or running:

            # tant qu'il reste de la place, démarre le puzzle suivant ; sa sortie va dans <puzzle>.log
            while pending and len(running) < max_parallel:
                f = pending.pop(0)
                name = os.path.splitext(os.path.basename(f))[0]
                log = open(os.path.join(OUT, name + ".log"), "w", encoding="utf-8")
                proc = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--un", f],
                                        stdout=log, stderr=subprocess.STDOUT, env=env)
                running.append((proc, name, time.perf_counter(), log))
                say(f"{time.strftime('%H:%M:%S')} lancé : {name}")

            # un puzzle terminé : note son temps total dans resume.txt et libère sa place pour le suivant
            for item in running[:]:
                proc, name, started, log = item
                if proc.poll() is not None:
                    log.close()
                    waited = time.perf_counter() - started
                    lines.append(f"{name} : terminé en {waited:.1f} s (voir {name}.log)")
                    write_summary(lines)
                    say(f"{time.strftime('%H:%M:%S')} terminé : {name} en {waited:.1f} s")
                    running.remove(item)

            # toutes les HEARTBEAT secondes : rappelle quels puzzles tournent encore
            if running and time.perf_counter() - last_report >= HEARTBEAT:
                last_report = time.perf_counter()
                for proc, name, started, log in running:
                    say(f"{time.strftime('%H:%M:%S')} en cours : {name} ({(last_report - started) / 60:.0f} min)")
            time.sleep(1)       # vérifier état des processus chaque seconde

    except KeyboardInterrupt:
        # Ctrl+C arrête les processus en cours et note le temps écoulé de chacun, les puzzles jamais démarrés sont notés aussi
        for proc, name, started, log in running:
            proc.kill()
            proc.wait()
            log.close()
            waited = time.perf_counter() - started
            lines.append(f"{name} : interrompu, non résolu après {waited / 60:.1f} min ({waited:.0f} s)")
        for f in pending:
            lines.append(f"{os.path.splitext(os.path.basename(f))[0]} : jamais lancé")
        write_summary(lines)
        say("Arrêt demandé.")

    # résumé final identique à resume.txt
    say("\n".join(lines))


# avec --un <puzzle> mesure ce seul puzzle
if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--un":
        run_one(sys.argv[2])
    else:
        launcher(sys.argv[1:])
