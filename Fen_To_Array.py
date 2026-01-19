import numpy as np

def fen_to_array(fen):
    # Initialize an empty 8x8 board with '*'
    board = np.full((8, 8), '*', dtype=str)
    
    # Split FEN string into rows
    rows = fen.split(' ')[0].split('/')
    
    # Map pieces to their initials
    piece_map = {
        'r': 'r', 'n': 'n', 'b': 'b', 'q': 'q', 'k': 'k', 'p': 'p',
        'R': 'R', 'N': 'N', 'B': 'B', 'Q': 'Q', 'K': 'K', 'P': 'P'
    }
    
    # Fill the board
    for i, row in enumerate(rows):
        j = 0
        for char in row:
            if char.isdigit():
                j += int(char)  # Skip empty squares
            else:
                board[i, j] = piece_map.get(char, '*')  # Place the piece or '*'
                j += 1
    
    return board

# Example usage
# fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
# board = fen_to_array(fen)

# print(board)
