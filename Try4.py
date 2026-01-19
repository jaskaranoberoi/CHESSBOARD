import sys
import chess # type: ignore
import chess.engine #type: ignore
import chess.pgn #type: ignore

# Path to the Stockfish engine executable
engine_path = r"C:\Users\karan\OneDrive\Desktop\stockfish\stockfish.exe"

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
    #current_fen = sys.argv[1]  # Get the FEN string passed from the server
    current_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    # Call function to get the best move
    board = chess.Board(current_fen)
    best_move, updated_board = get_best_move(board)
    new_fen = updated_board.fen()

    # Send both the best move and the FEN string back to the server, separated by a semicolon
    print(f"{best_move};{new_fen}")
