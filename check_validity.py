import sys
import chess

def check_validity(last_fen, curr_fen):
    # Create chess boards from the FEN strings
    board = chess.Board(fen=last_fen)

    try:
        # Set the new board position from the current FEN
        new_board = chess.Board(fen=curr_fen)

        # Check if both FENs are valid
        if board.is_valid() and new_board.is_valid():
            # Generate all legal moves from the last position
            legal_moves = list(board.legal_moves)

            # Check if the transition from last_fen to curr_fen is valid
            # Create a move that corresponds to the change from last_fen to curr_fen
            for move in legal_moves:
                # Create a temporary board to apply the legal move
                temp_board = board.copy()
                temp_board.push(move)
                
                # Check if the resulting board matches curr_fen
                if temp_board.fen() == curr_fen:
                    print("valid")
                    return

            print("invalid")
        else:
            print("invalid")
    except Exception as e:
        print("invalid", str(e))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 check_validity.py <last_fen> <curr_fen>")
        sys.exit(1)

    last_fen = sys.argv[1]
    curr_fen = sys.argv[2]
    
    check_validity(last_fen, curr_fen)

