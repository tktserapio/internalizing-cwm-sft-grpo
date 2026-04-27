import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to convert coordinates to string representation
def coord_to_str(coord):
    file, rank = coord
    return f"{chr(file + ord('a'))}{rank}"

# Initialize the initial state
def get_initial_state() -> State:
    # Initial board setup
    board = {
        "r": coord_to_str((4, 1)), "n": coord_to_str((4, 2)), "b": coord_to_str((4, 3)), 
        "q": coord_to_str((4, 4)), "k": coord_to_str((4, 5)),
        "p": ["p_a1", "p_b1", "p_c1", "p_d1", "p_e1"],
        "R": coord_to_str((1, 1)), "N": coord_to_str((1, 2)), "B": coord_to_str((1, 3)), 
        "Q": coord_to_str((1, 4)), "K": coord_to_str((1, 5))
    }
    return {"board": board}

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    piece, from_coord, to_coord = action.split("_")
    from_coord = coord_to_str(tuple(map(int, from_coord[1:].split(','))))
    
    # Convert to file and rank
    file_from, rank_from = from_coord
    file_to, rank_to = to_coord
    
    # Handle pawn movement
    if piece == "P":
        if rank_from == "1" and rank_to == "2":
            new_state["board"][piece] = [f"{file_to}_{rank_to}"]
            new_state["board"]["p"].remove(f"{file_from}_{rank_from}")
        else:
            new_state["board"][piece] = [f"{file_to}_{rank_to}"]
            new_state["board"][piece] += [f"{file_from}_{rank_from}"]
            new_state["board"]["p"].remove(f"{file_from}_{rank_from}")
    
    # Handle other pieces
    elif piece in ["R", "N", "B", "Q", "K"]:
        new_state["board"][piece] = [f"{file_to}_{rank_to}"]
        new_state["board"][piece] += [f"{file_from}_{rank_from}"]
        del new_state["board"][piece][new_state["board"][piece].index(f"{file_from}_{rank_from}")]
    
    # Handle castling
    if piece == "K":
        new_state["board"][piece] = [f"{file_to}_{rank_to}"]
        new_state["board"][piece] += [f"{file_from}_{rank_from}"]
        del new_state["board"][piece][new_state["board"][piece].index(f"{file_from}_{rank_from}")]
    
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    board = state["board"]
    white_pieces = sum(1 for piece in board.values() if piece.startswith("R") or piece.startswith("N") or piece.startswith("B") or piece.startswith("Q") or piece.startswith("K"))
    black_pieces = sum(1 for piece in board.values() if piece.startswith("r") or piece.startswith("n") or piece.startswith("b") or piece.startswith("q") or piece.startswith("k"))
    return 0 if white_pieces > black_pieces else 1

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return "Player 0" if player_id == 0 else "Player 1"

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    board = state["board"]
    white_pieces = sum(1 for piece in board.values() if piece.startswith("R") or piece.startswith("N") or piece.startswith("B") or piece.startswith("Q") or piece.startswith("K"))
    black_pieces = sum(1 for piece in board.values() if piece.startswith("r") or piece.startswith("n") or piece.startswith("b") or piece.startswith("q") or piece.startswith("k"))
    if white_pieces == 0 or black_pieces == 0:
        return [1.0, -1.0]
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    board = state["board"]
    legal_actions = []
    for piece, coords in board.items():
        if piece.startswith("P"):
            for from_coord in coords:
                file_from, rank_from = from_coord[1:].split('_')
                rank_from = int(rank_from)
                if rank_from < 5:
                    to_coords = [f"{file_from}_{rank_from+1}", f"{file_from}_{rank_from+2}"] if rank_from == 1 else [f"{file_from}_{rank_from+1}"]
                    for to_coord in to_coords:
                        if to_coord not in board[piece] and to_coord not in board["p"]:
                            legal_actions.append(f"P_{from_coord}_{to_coord}")
        elif piece.startswith("R"):
            for from_coord in coords:
                file_from, rank_from = from_coord[1:].split('_')
                for delta_rank in range(-1, 2):
                    for delta_file in range(-1, 2):
                        if abs(delta_file) + abs(delta_rank) != 0:
                            to_file = chr(ord(file_from) + delta_file)
                            to_rank = str(int(rank_from) + delta_rank)
                            to_coord = f"{to_file}_{to_rank}"
                            if to_coord not in board[piece] and to_coord not in board["p"]:
                                legal_actions.append(f"{piece}_{from_coord}_{to_coord}")
        elif piece.startswith("N"):
            for from_coord in coords:
                file_from, rank_from = from_coord[1:].split('_')
                for delta_rank in [-2, -1, 1, 2]:
                    for delta_file in [-1, 1]:
                        to_file = chr(ord(file_from) + delta_file)
                        to_rank = str(int(rank_from) + delta_rank)
                        to_coord = f"{to_file}_{to_rank}"
                        if to_coord not in board[piece] and to_coord not in board["p"]:
                            legal_actions.append(f"N_{from_coord}_{to_coord}")
        elif piece.startswith("B"):
            for from_coord in coords:
                file_from, rank_from = from_coord[1:].split('_')
                for delta_rank in range(-1, 2):
                    for delta_file in range(-1, 2):
                        if abs(delta_file) + abs(delta_rank) != 0:
                            to_file = chr(ord(file_from) + delta_file)
                            to_rank = str(int(rank_from) + delta_rank)
                            to_coord = f"{to_file}_{to_rank}"
                            if to_coord not in board[piece] and to_coord not in board["p"]:
                                legal_actions.append(f"B_{from_coord}_{to_coord}")
        elif piece.startswith("Q"):
            for from_coord in coords:
                file_from, rank_from = from_coord[1:].split('_')
                for delta_rank in range(-1, 2):
                    for delta_file in range(-1, 2):
                        if abs(delta_file) + abs(delta_rank) != 0:
                            to_file = chr(ord(file_from) + delta_file)
                            to_rank = str(int(rank_from) + delta_rank)
                            to_coord = f"{to_file}_{to_rank}"
                            if to_coord not in board[piece] and to_coord not in board["p"]:
                                legal_actions.append(f"Q_{from_coord}_{to_coord}")
        elif piece.startswith("K"):
            for from_coord in coords:
                file_from, rank_from = from_coord[1:].split('_')
                for delta_rank in [-1, 0, 1]:
                    for delta_file in [-1, 0, 1]:
                        if abs(delta_file) + abs(delta_rank) != 0:
                            to_file = chr(ord(file_from) + delta_file)
                            to_rank = str(int(rank_from) + delta_rank)
                            to_coord = f"{to_file}_{to_rank}"
                            if to_coord not in board[piece] and to_coord not in board["p"]:
                                legal_actions.append(f"K_{from_coord}_{to_coord}")
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    board = state["board"]
    white_pieces = sum(1 for piece in board.values() if piece.startswith("R") or piece.startswith("N") or piece.startswith("B") or piece.startswith("Q") or piece.startswith("K"))
    black_pieces = sum(1 for piece in board.values() if piece.startswith("r") or piece.startswith("n") or piece.startswith("b") or piece.startswith("q") or piece.startswith("k"))
    white_obs = {coord: piece for piece, coords in board.items() for coord in coords if piece.startswith("R") or piece.startswith("N") or piece.startswith("B") or piece.startswith("Q") or piece.startswith("K")}
    black_obs = {coord: piece for piece, coords in board.items() for coord in coords if piece.startswith("r") or piece.startswith("n") or piece.startswith("b") or piece.startswith("q") or piece.startswith("k")}
    return [{"white": white_obs, "black": black_obs}]