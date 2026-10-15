# fichier qui contient les fonctions communes, genre de convention
from .parser import BLANK

# indices (0 à 80) des cases de chaque ligne, colonne et bloc 3x3
ROWS = [[9 * r + c for c in range(9)] for r in range(9)]
COLS = [[9 * r + c for r in range(9)] for c in range(9)]
BOXES = [[9 * (3 * br + r) + 3 * bc + c for r in range(3) for c in range(3)] for br in range(3) for bc in range(3)]

#  0   1   2 |  3   4   5 |  6   7   8 
#  9  10  11 | 12  13  14 | 15  16  17 
# 18  19  20 | 21  22  23 | 24  25  26 
#--------------------------------------
# 27  28  29 | 30  31  32 | 33  34  35 
# 36  37  38 | 39  40  41 | 42  43  44 
# 45  46  47 | 48  49  50 | 51  52  53 
#--------------------------------------
# 54  55  56 | 57  58  59 | 60  61  62 
# 63  64  65 | 66  67  68 | 69  70  71
# 72  73  74 | 75  76  77 | 78  79  80 




# retourne pour chaque case si elle a été donnée par l'énoncé?
def get_fixed(puzzle: list[str]) -> list[bool]:
    return [val != BLANK for val in puzzle]

#puzzle :  ['.', '.', '.', '.', '5', '.', '9', '.', '.', ...]
#fixed  :  [False, False, False, False, True, False, True, False, False, ...]
