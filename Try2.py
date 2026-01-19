import chess
import chess.pgn

def fen_to_pgn(prev_fen, new_fen):
    board = chess.Board(prev_fen)

    # Iterate through all legal moves in the position
    for move in board.legal_moves:
        # Get the SAN notation before applying the move
        move_san = board.san(move)

        # Push the move to update the board position
        board.push(move)

        # Check if the new FEN matches the current board's FEN
        if board.fen() == new_fen:
            return move_san  # Return the SAN of the move that led to this FEN
        
        # Restore the previous board state by popping the move
        board.pop()

    # If no valid move was found that leads to the new FEN, raise an error
    raise ValueError(f"Could not find a valid move leading to the new FEN: {new_fen}")

prev_fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
new_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"

fen1 = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
fen2 = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"


move_san = fen_to_pgn(fen1, fen2)
print(move_san)
