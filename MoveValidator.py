import numpy as np

def fen_to_array(fen: str):
    """Convert FEN string to 8x8 numpy array (rank 8 -> rank 1)."""
    board = []
    rows = fen.split(" ")[0].split("/")
    for row in rows:
        row_arr = []
        for ch in row:
            if ch.isdigit():
                row_arr.extend(["*"] * int(ch))
            else:
                row_arr.append(ch)
        board.append(row_arr)
    return np.array(board, dtype=str)


def is_path_clear(board, start, end):
    """Check if straight/diagonal path between start and end is clear (exclude start & end)."""
    x1, y1 = start
    x2, y2 = end

    dx = int(np.sign(x2 - x1))
    dy = int(np.sign(y2 - y1))

    x, y = x1 + dx, y1 + dy
    while (x, y) != (x2, y2):
        if board[x, y] != '*':
            return False
        x += dx
        y += dy
    return True


def find_move_squares(board_before, board_after):
    """
    Given two 8x8 numpy arrays return (start, end).
    Only accepts exactly two changed squares (typical single move or capture or promotion).
    Returns (start, end) as tuples (row, col) or (None, None) if not a simple single-move diff.
    """
    # positions where pieces differ
    diff = np.argwhere(board_before != board_after)
    # strict: single legal move should change exactly two squares (origin & destination)
    if diff.shape[0] != 2:
        return None, None

    start = None
    end = None
    for sq in diff:
        r, c = int(sq[0]), int(sq[1])
        before = board_before[r, c]
        after = board_after[r, c]

        # origin square: had a piece before, is empty after
        if before != '*' and after == '*':
            start = (r, c)
        # destination square: was empty before, has a piece after
        elif before == '*' and after != '*':
            end = (r, c)
        # capture or promotion-like: different non-empty symbols -> treat as end
        elif before != '*' and after != '*' and before != after:
            # This means a piece moved to this square capturing (or promotion producing different symbol)
            end = (r, c)

    # both must be found
    if start is None or end is None:
        return None, None
    return start, end


def is_legal_move(fen_before: str, fen_after: str) -> bool:
    """
    Return True if a single *legal* piece move (ignoring castling & en-passant & check detection)
    transforms fen_before -> fen_after.

    Strict rules:
      - The board difference must be exactly two squares (start & end).
      - The moving piece must match the side-to-move in fen_before.
      - Basic piece movement rules are enforced (pawns, knights, bishops, rooks, queens, king).
      - Path clearance checked for sliding pieces.
    """
    board_before = fen_to_array(fen_before)
    board_after  = fen_to_array(fen_after)

    # find start and end squares (strictly 2 changed squares required)
    start, end = find_move_squares(board_before, board_after)
    if start is None or end is None:
        return False

    piece = board_before[start]
    dest_before = board_before[end]   # occupancy of destination before the move

    # sanity checks
    if piece == '*':
        return False
    if board_after[start] != '*':  # start must be empty after move
        return False

    # cannot capture own piece (destination before the move)
    if dest_before != '*' and (dest_before.isupper() == piece.isupper()):
        return False

    # turn validation (active color in fen_before)
    parts = fen_before.split()
    if len(parts) >= 2:
        active = parts[1]
        if active == 'w' and not piece.isupper():
            return False
        if active == 'b' and not piece.islower():
            return False

    # movement vector (row difference, col difference)
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    # Pawn rules (no en-passant)
    # Note: array indexing uses row0 = rank8, row7 = rank1, so white moves dx = -1
    if piece == 'P':
        # single forward (destination must have been empty)
        if dx == -1 and dy == 0 and dest_before == '*':
            return True
        # capture to diagonals (destination before must have opponent piece)
        if dx == -1 and abs(dy) == 1 and dest_before != '*' and dest_before.islower():
            return True
        # double from starting rank (white pawns start at row 6)
        if start[0] == 6 and dx == -2 and dy == 0 and dest_before == '*' and board_before[5, start[1]] == '*':
            return True
        return False

    if piece == 'p':
        # black pawn forward
        if dx == 1 and dy == 0 and dest_before == '*':
            return True
        # capture
        if dx == 1 and abs(dy) == 1 and dest_before != '*' and dest_before.isupper():
            return True
        # double from starting rank (black pawns start at row 1)
        if start[0] == 1 and dx == 2 and dy == 0 and dest_before == '*' and board_before[2, start[1]] == '*':
            return True
        return False

    # Rook
    if piece.lower() == 'r':
        if dx == 0 or dy == 0:
            return is_path_clear(board_before, start, end)
        return False

    # Bishop
    if piece.lower() == 'b':
        if abs(dx) == abs(dy):
            return is_path_clear(board_before, start, end)
        return False

    # Queen
    if piece.lower() == 'q':
        if dx == 0 or dy == 0 or abs(dx) == abs(dy):
            return is_path_clear(board_before, start, end)
        return False

    # Knight
    if piece.lower() == 'n':
        if (abs(dx), abs(dy)) in [(2,1), (1,2)]:
            return True
        return False

    # King (single step only; castling not supported)
    if piece.lower() == 'k':
        if abs(dx) <= 1 and abs(dy) <= 1:
            return True
        return False

    return False
