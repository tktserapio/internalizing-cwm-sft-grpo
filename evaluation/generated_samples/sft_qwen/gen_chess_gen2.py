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

# Helper function to convert file and rank to algebraic notation
def file_rank_to_algebraic(file: str, rank: int) -> str:
    return f"{file}{rank}"

# Initialize the initial state of the game
def get_initial_state() -> State:
    # Initial board setup
    initial_board = {
        "r": file_rank_to_algebraic("a", 5),
        "n": file_rank_to_algebraic("b", 5),
        "b": file_rank_to_algebraic("c", 5),
        "q": file_rank_to_algebraic("d", 5),
        "k": file_rank_to_algebraic("e", 5),
        "p": "p_p_p_p_p",
        "R": file_rank_to_algebraic("a", 1),
        "N": file_rank_to_algebraic("b", 1),
        "B": file_rank_to_algebraic("c", 1),
        "Q": file_rank_to_algebraic("d", 1),
        "K": file_rank_to_algebraic("e", 1),
        "P": "P_P_P_P_P",
        "E": "e2_e4_e5_e6_e7_e8"
    }
    return initial_board

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    piece, from_square, to_square = action.split("_")
    
    # Handle pawn movement
    if piece == "P":
        if from_square == to_square:
            new_state[from_square] = "."
            new_state[to_square] = piece
        else:
            new_state[from_square] = "."
            new_state[to_square] = piece
            new_state[file_rank_to_algebraic(from_square[0], int(from_square[1]) + 1)] = "."
    
    # Handle piece movement
    elif piece in ["R", "N", "B", "Q", "K"]:
        new_state[from_square] = "."
        new_state[to_square] = piece
    
    # Handle promotion
    elif piece == "P" and to_square == "e5":
        new_state[to_square] = "P"
        new_state["e5_promotion"] = "Q"
    
    # Castling is not implemented in this version
    elif piece == "K":
        pass
    
    # En passant is not implemented in this version
    elif piece == "P" and to_square == "e3":
        new_state[to_square] = "P"
        new_state["e3_promotion"] = "Q"
    
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    if "E" in state:
        return 0 if state["E"].startswith("P") else 1
    return -4

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return "Player 0" if player_id == 0 else "Player 1"

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    if "E" in state:
        return [1.0, -1.0]
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    for piece in ["R", "N", "B", "Q", "K", "P"]:
        for from_square in state.keys():
            if state[from_square] == piece:
                if piece == "P":
                    # Pawn movement
                    if from_square in ["a2", "b2", "c2", "d2", "e2"]:
                        if from_square == "a2":
                            if "a3" in state and state["a3"] == ".":
                                legal_actions.append(f"P_{from_square}_a3")
                        if from_square == "e2":
                            if "e3" in state and state["e3"] == ".":
                                legal_actions.append(f"P_{from_square}_e3")
                        if "e4" in state and state["e4"] == ".":
                            legal_actions.append(f"P_{from_square}_e4")
                    if from_square in ["a1", "b1", "c1", "d1", "e1"]:
                        if from_square == "a1":
                            if "a2" in state and state["a2"] == ".":
                                legal_actions.append(f"P_{from_square}_a2")
                        if from_square == "e1":
                            if "e2" in state and state["e2"] == ".":
                                legal_actions.append(f"P_{from_square}_e2")
                        if "e4" in state and state["e4"] == ".":
                            legal_actions.append(f"P_{from_square}_e4")
                    if from_square in ["a2", "b2", "c2", "d2", "e2"]:
                        if "a3" in state and state["a3"] != ".":
                            legal_actions.append(f"P_{from_square}_a3")
                        if "e3" in state and state["e3"] != ".":
                            legal_actions.append(f"P_{from_square}_e3")
                        if "e4" in state and state["e4"] != ".":
                            legal_actions.append(f"P_{from_square}_e4")
                elif piece in ["R", "N", "B", "Q", "K"]:
                    # Piece movement
                    for to_square in state.keys():
                        if state[to_square] == ".":
                            legal_actions.append(f"{piece}_{from_square}_{to_square}")
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    player_0_obs = {}
    player_1_obs = {}
    
    # Player 0 sees the board from White's perspective
    for file in "abcde":
        for rank in "12345":
            square = file_rank_to_algebraic(file, rank)
            if square in state:
                player_0_obs[square] = state[square]
            else:
                player_0_obs[square] = "."
    
    # Player 1 sees the board from Black's perspective
    for file in "abcde":
        for rank in "12345":
            square = file_rank_to_algebraic(file, rank)
            if square in state:
                player_1_obs[square] = state[square]
            else:
                player_1_obs[square] = "."
    
    return [player_0_obs, player_1_obs]