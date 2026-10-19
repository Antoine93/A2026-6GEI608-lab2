# Vérification de doublons dans les lignes, colonnes et sous-matrices 3x3 d'une grille de Sudoku (pris de la référence geekforgeeks)

# vérifie les doublons dans la ligne actuelle
def rowValid(mat, row):

    # tableau pour suivre les occurrences des chiffres
    visited = [0] * 10
    
    for i in range(9):

        # si la case n'est pas vide
        if mat[row][i] != 0:
            val = mat[row][i]

            # si un doublon est trouvé
            if visited[val] != 0:
                return False

            # marquer le chiffre comme visité
            visited[val] += 1
    return True

# vérifie les doublons dans la colonne actuelle
def colValid(mat, col):

    visited = [0] * 10
    
    for i in range(9):

        if mat[i][col] != 0:
            val = mat[i][col]

            if visited[val] != 0:
                return False

            visited[val] += 1
    return True

# vérifie les doublons dans la sous-matrice 3x3 actuelle
def subMatValid(mat, startRow, startCol):

    visited = [0] * 10
    
    for row in range(3):
        for col in range(3):

            curr = mat[row + startRow][col + startCol]

            if curr != 0:

                if visited[curr] != 0:
                    return False

                visited[curr] += 1
    return True

# valide la grille entière en vérifiant toutes les lignes, colonnes et sous-matrices 3x3
def isValid(mat):
    for i in range(9):
        for j in range(9):

            if not rowValid(mat, i) or not colValid(mat, j) or \
               not subMatValid(mat, i - i % 3, j - j % 3):
                return False
    return True 