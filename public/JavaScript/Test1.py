import chess
import chess.svg

# Function to display chess board from FEN
def display_board_from_fen(fen):
    # Create a board object from the FEN string
    board = chess.Board(fen)

    # Print the board in a readable format
    print(board)

# Example FEN string (starting position)
fen = "1rb1kb2/p1ppppp1/1p2q1np/1rn4P/4P3/2NB1Q2/PPPPNPP1/R1KB2R1 w KQkq - 0 1"

# Call the function to display the board
display_board_from_fen(fen)
