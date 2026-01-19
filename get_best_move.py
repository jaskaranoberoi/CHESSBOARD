import sys
import chess  # type: ignore
import chess.engine # type: ignore

# Path to the Stockfish engine executable
engine_path = "stockfish\stockfish.exe"

# Start the engine
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

def get_best_move(board):
    try:
        result = engine.play(board, chess.engine.Limit(time=2.0))
        move = result.move
        board.push(move)
        return move, board
    except Exception as e:
        print(f"Error getting best move: {e}")
        return None, board
    finally:
        engine.quit()

if __name__ == "__main__":
    current_fen = sys.argv[1]  # Get the FEN string passed from the server

    # Call function to get the best move
    board = chess.Board(current_fen)
    best_move, updated_board = get_best_move(board)
    new_fen = updated_board.fen()

    if best_move:
        # Send both the best move and the FEN string back to the server, separated by a semicolon
        print(f"{best_move};{new_fen}")
    else:
        print("Error;Error", file=sys.stderr)  # Indicate an error
