import chess
import chess.engine
import chess.pgn
import time
import numpy as np
from pathlib import Path
from chessboard_detector import get_chessboard
import requests
import sys
import json


Player_Color = 1

# Path to the Stockfish engine executable
engine_path = r"C:\Users\karan\OneDrive\Desktop\stockfish\stockfish.exe"

# Start the engine
engine = chess.engine.SimpleEngine.popen_uci(engine_path)

def fetch_chessboard():
    ChessBoard = get_chessboard()
    ChessBoard = [['' if piece == '*' else piece for piece in row] for row in ChessBoard]
    return ChessBoard

def array_to_fen(ChessBoard):
    board = chess.Board(None)
    piece_map = {
        'P': 'P', 'p': 'p',
        'R': 'R', 'r': 'r',
        'N': 'N', 'n': 'n',
        'B': 'B', 'b': 'b',
        'Q': 'Q', 'q': 'q',
        'K': 'K', 'k': 'k',
        '*': None
    }
    for row in range(8):
        for col in range(8):
            piece_symbol = ChessBoard[row][col]
            if piece_symbol:
                square = chess.square(col, 7 - row)
                board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))
    return board.fen()

def send_fen_to_javascript(fen, pgn=None, move_count=None):
    url = 'http://localhost:3000/update_fen'
    payload = {'fen': fen}
    
    if pgn:
        payload['pgn'] = pgn
    if move_count is not None:
        payload['move_count'] = move_count
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"FEN successfully sent to JavaScript: {fen}")
    except requests.RequestException as e:
        print(f"Error sending FEN to JavaScript: {e}")

def get_best_move(board):
    try:
        result = engine.play(board, chess.engine.Limit(time=2.0))
        move = result.move
        board.push(move)
        return move, board
    except Exception as e:
        print(f"Error getting best move: {e}")
        return None, board

def fen_to_pgn(prev_fen, new_fen):
    game = chess.pgn.Game()
    board = chess.Board(prev_fen)
    game.setup(board)
    
    # Create a new branch to explore moves leading to the new FEN
    node = game

    # Generate all possible moves and add them to the PGN game
    for move in board.legal_moves:
        board.push(move)
        if board.fen() == new_fen:
            # Add the move to the game
            node = node.add_variation(move)
            break
        board.pop()
    
    # Add moves to the PGN game until reaching the new FEN
    while board.fen() != new_fen:
        found_move = False
        for move in board.legal_moves:
            board.push(move)
            if board.fen() == new_fen:
                node = node.add_variation(move)
                found_move = True
                break
            board.pop()
        if not found_move:
            raise ValueError("Could not find a valid sequence of moves leading to the new FEN")
    
    return game.mainline_moves()

def update_fen_to_move(current_fen, move_side):
    parts = current_fen.split()
    if (move_side == 'white' and parts[1] == 'b') or (move_side == 'black' and parts[1] == 'w'):
        parts[1] = 'b' if move_side == 'black' else 'w'
        return ' '.join(parts)
    else:
        return current_fen  # Return current_fen if no update is needed

    
def add_castling_rights(fen, castling_rights):
    # Split the FEN string into its components
    parts = fen.split()
    
    # Ensure there are 6 parts in the FEN string
    if len(parts) != 6:
        raise ValueError("Invalid FEN string")

    # Replace the castling rights (4th part of the FEN string) with the new castling rights
    parts[2] = castling_rights

    # Reconstruct the FEN string with the updated castling rights
    updated_fen = ' '.join(parts)
    return updated_fen

def increment_fen_move_count(fen):
    parts = fen.split()
    
    # Ensure there are 6 parts in the FEN string
    if len(parts) != 6:
        raise ValueError("Invalid FEN string")

    # Extract the current move count and increment it
    move_count = int(parts[5])
    move_count += 1
    
    # Update the FEN string with the new move count
    parts[5] = str(move_count)
    
    # Reconstruct the FEN string
    updated_fen = ' '.join(parts)
    return updated_fen

# Initialize variables
move_count = 0
game_start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
previous_fen = game_start_fen
previous_white_fen = None
previous_black_fen = None
current_fen = game_start_fen
castling_rights = 'KQkq'  # Add this as the castling rights


try:
    while True:
        if Player_Color == 0:  # White's turn
            ChessBoard = fetch_chessboard()
            current_fen = array_to_fen(ChessBoard)

            if current_fen != previous_fen and previous_white_fen != current_fen:
                move_count += 1
                previous_white_fen = current_fen

                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = " ".join([move.uci() for move in pgn_moves])
                print(f"PGN from previous FEN to new FEN: {pgn}")
                #send_fen_to_javascript(current_fen, pgn, move_count)

                previous_fen = current_fen
                current_fen = update_fen_to_move(current_fen, 'black')
                
                time.sleep(10)
                board = chess.Board(current_fen)
                best_move, updated_board = get_best_move(board)
                current_fen = updated_board.fen()
                previous_black_fen = current_fen

                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = " ".join([move.uci() for move in pgn_moves])
                print(f"PGN from previous FEN to new FEN: {pgn}")

                #send_fen_to_javascript(current_fen, pgn, move_count)
                previous_fen = current_fen
                move_count += 1


        elif Player_Color == 1:  # Black's turn
            if move_count == 0:
                board = chess.Board(game_start_fen)
                best_move, updated_board = get_best_move(board)
                current_fen = updated_board.fen()
                previous_white_fen = current_fen

                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = " ".join([move.uci() for move in pgn_moves])
                print(f"In Player color1 move count 0 PGN from previous FEN to new FEN: {pgn}")
                move_count += 1
                #send_fen_to_javascript(current_fen, pgn, move_count)
                previous_fen = update_fen_to_move(previous_fen,'black')
                previous_fen = current_fen
                time.sleep(5)
            else:
                ChessBoard = fetch_chessboard()
                current_fen = array_to_fen(ChessBoard)

                if current_fen != previous_fen and previous_black_fen != current_fen:
                    move_count += 1
                    previous_black_fen = current_fen
                    print(previous_fen)
                    current_fen = add_castling_rights(current_fen, castling_rights)
                    current_fen = increment_fen_move_count(current_fen)
                    print(current_fen)

                    pgn_moves = fen_to_pgn(previous_fen, current_fen)
                    pgn = " ".join([move.uci() for move in pgn_moves])
                    print(f" We are here PGN from previous FEN to new FEN: {pgn}")
                    #send_fen_to_javascript(current_fen, pgn, move_count)
                    previous_fen = current_fen
                    previous_fen = update_fen_to_move(current_fen, 'white')
                    print(current_fen)

                    time.sleep(10)
                    board = chess.Board(current_fen)
                    best_move, updated_board = get_best_move(board)
                    current_fen = updated_board.fen()
                    print(current_fen)
                    print(previous_fen)
                    previous_white_fen = current_fen

                    pgn_moves = fen_to_pgn(previous_fen, current_fen)
                    pgn = " ".join([move.uci() for move in pgn_moves])
                    print(f" We are here 2 PGN from previous FEN to new FEN: {pgn}")

                    #send_fen_to_javascript(current_fen, pgn, move_count)
                    previous_fen = current_fen
                    move_count += 1

        time.sleep(5)

finally:
    engine.quit()
