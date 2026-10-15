import heapq
def colored(text, _color):
    """Return text unchanged when optional terminal coloring is unavailable."""
    return text


# Définition de l'état du puzzle
class PuzzleState:
    def __init__(self, board, parent, move, depth, cost):
        self.board = board
        self.parent = parent
        self.move = move
        self.depth = depth
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost


# Afficher un puzzle board
def print_board(board):
    print("+---+---+---+")
    for row in range(0, 9, 3):
        row_visual = "|"
        for tile in board[row:row + 3]:
            if tile == 0:  
                row_visual += f" {colored(' ', 'cyan')} |"
            else:
                row_visual += f" {colored(str(tile), 'yellow')} |"
        print(row_visual)
        print("+---+---+---+")


# heuristique de Manhattan pour l'algorithme A*
def heuristic(board : list[int | None]) -> int:
    distance = 0
    for i in range(9):
        if board[i] != 0:
            x1, y1 = divmod(i, 3)
            x2, y2 = divmod(board[i] - 1, 3)
            distance += abs(x1 - x2) + abs(y1 - y2)
    return distance

# Génération de nouveaux états
def move_tile(board, move, blank_pos):
    new_board = board[:]
    new_blank_pos = blank_pos + moves[move]
    new_board[blank_pos], new_board[new_blank_pos] = new_board[new_blank_pos], new_board[blank_pos]
    return new_board

# grille 3 par 3 (None = vide) -> liste plate (0 = vide)
def to_flat(board):
    return [0 if v is None else v for r in board for v in r]

# liste plate (0 = vide) -> grille 3 par 3 (None = vide)
def to_matrix(board):
    return [[None if v == 0 else v for v in board[i:i + 3]] for i in range(0, 9, 3)]

# Implémentation de l'algorithme A*
def solve_puzzle_a_star(start,x,y):
    start_state = to_flat(start)
    open_list = []
    closed_list = set()
    heapq.heappush(open_list, PuzzleState(start_state, None, None, 0, heuristic(start_state)))

    iterations = 0
    frontier_sizes = []

    while open_list:
        # Ajouter la taille de la frontière à chaque itération
        frontier_sizes.append(len(open_list))

        current_state = heapq.heappop(open_list)

        # état est exploré au moment du pop
        iterations += 1

        # pour éviter de revisiter les états déjà explorés
        if tuple(current_state.board) in closed_list:
            continue

        if current_state.board == goal_state:
            current_state.board = to_matrix(current_state.board)
            return current_state, iterations, frontier_sizes

        closed_list.add(tuple(current_state.board))

        blank_pos = current_state.board.index(0)

        for move in moves:
            if move == 'U' and blank_pos < 3:  
                continue
            if move == 'D' and blank_pos > 5:  
                continue
            if move == 'L' and blank_pos % 3 == 0:  
                continue
            if move == 'R' and blank_pos % 3 == 2:  
                continue

            new_board = move_tile(current_state.board, move, blank_pos)

            if tuple(new_board) in closed_list:
                continue

            new_state = PuzzleState(new_board, current_state, move, current_state.depth + 1, current_state.depth + 1 + heuristic(new_board))
            heapq.heappush(open_list, new_state)

    return None, iterations, frontier_sizes

# Affichage des chemins parcourus et du puzzle board à chaque itération
def print_solution(solution):
    path = []
    current = solution
    while current:
        path.append(current)
        current = current.parent
    path.reverse()

    for step in path:
        print(f"Move: {step.move}")
        print_board(step.board)

goal_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]

moves = {
    'U': -3,  
    'D': 3,   
    'L': -1,  
    'R': 1   
}