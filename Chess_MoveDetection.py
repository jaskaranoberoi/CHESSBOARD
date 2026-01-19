import numpy as np
from ChessBoard_Creation import ChessBoard_Creation
from Fen_To_Array import fen_to_array

def Chess_MoveDetection(new_arr, old_arr):
    Sq = np.empty((2, 2), dtype=int)  # Simplified to 2x2 for start and end positions
    count = 0
    piece_moved = ''
    piece_captured = ''
    castling = ''
    no_of_rooks=0
    
    for i in range(8):
        for j in range(8):
            if new_arr[i][j]=="r" or new_arr[i][j]=="R":
                no_of_rooks += 1 
            if new_arr[i][j] != old_arr[i][j]:
                if count == 0:
                    # Record start position of the move
                    Sq[count][0] = i
                    Sq[count][1] = j
                    count += 1
                elif count == 1:
                    # Record end position of the move
                    Sq[count][0] = i
                    Sq[count][1] = j
                    count += 1
                
                # Detect castling
                if j == 2 and ((i == 0 and old_arr[i][0] == 'R' and new_arr[i][3] == 'R') or (i == 7 and old_arr[i][0] == 'r' and new_arr[i][3] == 'r')):  # Queenside castling
                    castling = 'O-O-O' if i == 0 else 'o-o-o'
                elif j == 6 and ((i == 0 and old_arr[i][7] == 'R' and new_arr[i][5] == 'R') or (i == 7 and old_arr[i][7] == 'r' and new_arr[i][5] == 'r')):  # Kingside castling
                    castling = 'O-O' if i == 0 else 'o-o'
                
                # Detect piece movement
                if old_arr[i][j] == '*':
                    piece_moved = new_arr[i][j]
                elif old_arr[i][j] != '*' and new_arr[i][j] != "*":
                    piece_moved = new_arr[i][j]
                    piece_captured = 'x' 

    return Sq, piece_moved, piece_captured, castling,no_of_rooks

# # Example usage
# ChessArr = fen_to_array("rnbqkbnr/ppp1pppp/8/3P4/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2")
# ChessArr1 = fen_to_array("rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 3")

# print("Old Board:")
# print(ChessArr)
# print("New Board:")
# print(ChessArr1)

# Sq, Piece_Moved, piece_captured, castling,noofrooks = Chess_MoveDetection(ChessArr1, ChessArr)
# print("Move Coordinates (start and end):")
# print(Sq)
# print("Piece Moved:")
# print(Piece_Moved)
# print("Piece Captured:")
# print(piece_captured)
# print("Castling:")
# print(castling)
