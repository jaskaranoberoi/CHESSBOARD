def get_board_from_fen(fen):
    """
    Extract the board setup from the FEN string and expand digits representing
    empty squares to '1' (indicating empty squares).
    """
    board = fen.split()[0]  # Get the board part of the FEN
    expanded_board = ""

    # Expand digits in FEN notation into empty squares ('1')
    for char in board:
        if char.isdigit():
            expanded_board += '1' * int(char)  # Expand digits (e.g., '8' -> '11111111')
        else:
            expanded_board += char  # Keep piece characters (P, p, R, etc.)

    return expanded_board

def find_last_move(prev_fen, new_fen):
    """
    Find the last piece that moved between the previous and current FEN strings.
    
    Returns:
        - moved_piece: The piece that moved (e.g., 'P', 'r', etc.).
        - start_square: The starting square index (0-63, where 0 is 'a8' and 63 is 'h1').
        - end_square: The destination square index (0-63).
    """
    # Get the board positions from the FEN strings
    prev_board = get_board_from_fen(prev_fen)
    new_board = get_board_from_fen(new_fen)

    # Initialize variables to track the move
    start_square = None
    end_square = None
    moved_piece = None

    # Compare the board positions square by square (0-63 for 64 squares)
    for i in range(64):
        prev_square = prev_board[i]
        new_square = new_board[i]

        # If a square was occupied in the previous position but is now empty, that's the start square
        if prev_square != '1' and new_square == '1':
            start_square = i
            moved_piece = prev_square  # The piece that moved

        # If a square was empty before but is now occupied, that's the end square
        if prev_square == '1' and new_square != '1':
            end_square = i

        # Special case: A piece moves between two non-empty squares
        if prev_square != '1' and new_square != '1' and prev_square != new_square:
            start_square = i
            moved_piece = prev_square
            end_square = i

    return moved_piece, start_square, end_square

def square_index_to_coordinates(index):
    """
    Convert a square index (0-63) to chessboard coordinates (e.g., 'a1', 'h8').
    """
    row = 8 - (index // 8)  # Rows are reversed (row 8 is at index 0-7)
    col = chr((index % 8) + ord('a'))  # Columns go from 'a' to 'h'
    return f"{col}{row}"

# Example usage
prev_fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
new_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3"

moved_piece, start_square, end_square = find_last_move(prev_fen, new_fen)

# Convert square indices to coordinates
start_coord = square_index_to_coordinates(start_square) if start_square is not None else None
end_coord = square_index_to_coordinates(end_square) if end_square is not None else None

# Output the result
print(f"Piece moved: {moved_piece}, from: {start_coord}, to: {end_coord}")
