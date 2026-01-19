import numpy as np

import numpy as np

def calculate_layer(pos: str) -> int:
    layers = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    return layers.get(pos, -1)

def is_valid_pawn_move(start, end, board, piece, en_passant_target=None):
    x1, y1 = start
    x2, y2 = end
    if piece == 'P':  # White pawn
        if x2 == x1 - 1 and y1 == y2 and board[x2][y2] == '*':
            return True  # Forward move
        if x2 == x1 - 1 and abs(y2 - y1) == 1 and (board[x2][y2].islower() or (en_passant_target and (x2, y2) == en_passant_target)):
            return True  # Capture or en passant
        if x1 == 6 and x2 == 4 and y1 == y2 and board[5][y1] == '*' and board[4][y1] == '*':
            return True  # Initial two-step move
    elif piece == 'p':  # Black pawn
        if x2 == x1 + 1 and y1 == y2 and board[x2][y2] == '*':
            return True  # Forward move
        if x2 == x1 + 1 and abs(y2 - y1) == 1 and (board[x2][y2].isupper() or (en_passant_target and (x2, y2) == en_passant_target)):
            return True  # Capture or en passant
        if x1 == 1 and x2 == 3 and y1 == y2 and board[2][y1] == '*' and board[3][y1] == '*':
            return True  # Initial two-step move
    return False

def is_valid_rook_move(start, end, board):
    x1, y1 = start
    x2, y2 = end
    if x1 != x2 and y1 != y2:
        return False  # Rook moves straight only
    
    if x1 == x2:  # Horizontal move
        step = 1 if y2 > y1 else -1
        for y in range(y1 + step, y2, step):
            if board[x1][y] != '*':
                return False
    else:  # Vertical move
        step = 1 if x2 > x1 else -1
        for x in range(x1 + step, x2, step):
            if board[x][y1] != '*':
                return False
    return True

def is_valid_bishop_move(start, end, board):
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) != abs(y2 - y1):
        return False  # Bishop moves diagonally
    
    step_x = 1 if x2 > x1 else -1
    step_y = 1 if y2 > y1 else -1
    x, y = x1 + step_x, y1 + step_y
    while x != x2:
        if board[x][y] != '*':
            return False
        x += step_x
        y += step_y
    return True

def is_valid_knight_move(start, end):
    x1, y1 = start
    x2, y2 = end
    return (abs(x2 - x1), abs(y2 - y1)) in [(2, 1), (1, 2)]

def is_valid_queen_move(start, end, board):
    return is_valid_rook_move(start, end, board) or is_valid_bishop_move(start, end, board)

def is_valid_king_move(start, end, board, castling_rights):
    x1, y1 = start
    x2, y2 = end
    
    # Normal move
    if max(abs(x2 - x1), abs(y2 - y1)) == 1:
        return True
    
    # Castling move
    if (x1, y1) == (7, 4) and x2 == 7 and (y2 == 6 or y2 == 2):  # White king
        if castling_rights['K'] and y2 == 6 and board[7][5] == '*' and board[7][6] == '*':
            return True
        if castling_rights['Q'] and y2 == 2 and board[7][1] == '*' and board[7][2] == '*' and board[7][3] == '*':
            return True
    if (x1, y1) == (0, 4) and x2 == 0 and (y2 == 6 or y2 == 2):  # Black king
        if castling_rights['k'] and y2 == 6 and board[0][5] == '*' and board[0][6] == '*':
            return True
        if castling_rights['q'] and y2 == 2 and board[0][1] == '*' and board[0][2] == '*' and board[0][3] == '*':
            return True
    return False

def get_move_from_boards(start_board, end_board):
    start_pos, end_pos = None, None
    for i in range(8):
        for j in range(8):
            if start_board[i][j] != end_board[i][j]:
                if start_board[i][j] != '*':
                    start_pos = (i, j)
                if end_board[i][j] != '*':
                    end_pos = (i, j)
    return start_pos, end_pos

def move_validity(start_board, end_board, en_passant_target=None, castling_rights={'K': True, 'Q': True, 'k': True, 'q': True}) -> bool:
    result = np.array_equal(start_board, end_board)
    print(result)  # True
    if(result):
        return True
    
    start_pos, end_pos = get_move_from_boards(start_board, end_board)
    if not start_pos or not end_pos:
        return False  # No valid move detected
    
    piece = start_board[start_pos[0]][start_pos[1]]
    if piece == '*':
        return False  # No piece to move
    
    if piece.lower() == 'p':
        return is_valid_pawn_move(start_pos, end_pos, start_board, piece, en_passant_target)
    elif piece.lower() == 'r':
        return is_valid_rook_move(start_pos, end_pos, start_board)
    elif piece.lower() == 'b':
        return is_valid_bishop_move(start_pos, end_pos, start_board)
    elif piece.lower() == 'n':
        return is_valid_knight_move(start_pos, end_pos)
    elif piece.lower() == 'q':
        return is_valid_queen_move(start_pos, end_pos, start_board)
    elif piece.lower() == 'k':
        return is_valid_king_move(start_pos, end_pos, start_board, castling_rights)
    
    return False  # Invalid move if piece type is unknown

# Arr1 = np.full((8, 8), '*', dtype=str)
# print(Arr1)

# Arr2 = np.full((8,8), '*', dtype=str)
# print(Arr2)

# start_pos = np.array([
#     ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
#     ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
#     ['*', '*', '*', '*', '*', '*', '*', '*'],
#     ['*', '*', '*', '*', '*', '*', '*', '*'],
#     ['*', '*', '*', '*', 'P', '*', '*', '*'],
#     ['*', '*', '*', '*', '*', '*', '*', '*'],
#     ['P', 'P', 'P', 'P', '*', 'P', 'P', 'P'],
#     ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
# ])

# e4_pos = np.array([
#     ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
#     ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
#     ['*', '*', '*', '*', '*', '*', '*', '*'],
#     ['*', '*', '*', '*', '*', '*', '*', '*'],
#     ['*', '*', '*', '*', 'P', '*', '*', '*'],
#     ['*', '*', '*', '*', '*', '*', '*', '*'],
#     ['P', 'P', 'P', 'P', '*', 'P', 'P', 'P'],
#     ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
# ])

# if move_validity(start_pos, e4_pos):
#     print("Valid move")
# else:
#     print("Invalid move")