import chess
import numpy as np

def array_to_board(array):
    """Convert your 8x8 array into a python-chess Board."""
    piece_map = {
        "P": chess.PAWN, "N": chess.KNIGHT, "B": chess.BISHOP,
        "R": chess.ROOK, "Q": chess.QUEEN, "K": chess.KING,
        "p": chess.PAWN, "n": chess.KNIGHT, "b": chess.BISHOP,
        "r": chess.ROOK, "q": chess.QUEEN, "k": chess.KING,
        "*": None
    }
    board = chess.Board.empty()
    for row in range(8):
        for col in range(8):
            piece = array[row][col]
            if piece != "*" and piece in piece_map:
                color = chess.WHITE if piece.isupper() else chess.BLACK
                board.set_piece_at(chess.square(col, 7-row), chess.Piece(piece_map[piece], color))
    return board


def board_to_array(board):
    """Convert a python-chess Board back to your 8x8 array."""
    arr = []
    for row in range(7, -1, -1):  # rank 8 → 1
        row_arr = []
        for col in range(8):  # file a → h
            sq = chess.square(col, row)
            piece = board.piece_at(sq)
            if piece is None:
                row_arr.append("*")
            else:
                symbol = piece.symbol()
                row_arr.append(symbol if piece.color == chess.BLACK else symbol.upper())
        arr.append(row_arr)
    return arr


def generate_legal_boards(array, turn):
    """Generate all possible new board arrays given current array and side to move."""
    board = array_to_board(array)
    board.turn = chess.WHITE if turn == "white" else chess.BLACK
    
    new_boards = []
    for move in board.legal_moves:
        temp_board = board.copy()
        temp_board.push(move)
        new_boards.append(board_to_array(temp_board))
    
    return new_boards


# Example usage:
array = [
    ["r","n","b","q","k","b","n","r"],
    ["p","p","p","p","p","p","p","p"],
    ["*","*","*","*","*","*","*","*"],
    ["*","*","*","*","*","*","*","*"],
    ["*","*","*","*","p","*","*","*"],
    ["*","*","*","*","*","*","*","*"],
    ["P","P","P","P","*","P","P","P"],
    ["R","N","B","Q","K","B","N","R"]
]

turn = "black"
all_boards = generate_legal_boards(array, turn)

print(f"Total legal moves for {turn}: {len(all_boards)}")
for b in all_boards[::1]:  # print first 5 boards
    for row in b:
        print(row)
    print("------")
