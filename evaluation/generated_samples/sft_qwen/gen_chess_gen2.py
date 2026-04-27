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

# Helper functions
def convert_position(position):
    """Converts algebraic notation to tuple coordinates for the 5x5 board."""
    file, rank = position
    file = 'a' if file == 'a' else 'b' if file == 'b' else 'c' if file == 'c' else 'd' if file == 'd' else 'e'
    rank = '1' if rank == '1' else '2' if rank == '2' else '3' if rank == '3' else '4' if rank == '4' else '5'
    return (rank, file)

def convert_coordinates(coordinates):
    """Converts tuple coordinates back to algebraic notation for the 5x5 board."""
    rank, file = coordinates
    file = 'a' if file == 'a' else 'b' if file == 'b' else 'c' if file == 'c' else 'd' if file == 'd' else 'e'
    rank = '1' if rank == '1' else '2' if rank == '2' else '3' if rank == '3' else '4' if rank == '4' else '5'
    return f"{rank}{file}"

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial board setup
    initial_board = {
        "r": (1, 'a'), "n": (1, 'b'), "b": (1, 'c'), "q": (1, 'd'), "k": (1, 'e'),
        "p": [(2, 'a'), (2, 'b'), (2, 'c'), (2, 'd'), (2, 'e')],
        "R": (5, 'a'), "N": (5, 'b'), "B": (5, 'c'), "Q": (5, 'd'), "K": (5, 'e')
    }
    return {"board": initial_board}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    piece, from_pos, to_pos = action.split('_')
    from_pos = convert_position(from_pos)
    to_pos = convert_position(to_pos)
    
    # Check if the move is valid
    if piece == "P":
        if from_pos[0] == '1':  # Pawn starting move
            new_state["board"][piece][0] += 2
        elif from_pos[0] == '5':  # Pawn ending move
            new_state["board"][piece][0] -= 2
        else:
            new_state["board"][piece][0] -= 1
    elif piece == "K":
        new_state["board"][piece][0] = to_pos[0]
        new_state["board"][piece][1] = to_pos[1]
    else:
        new_state["board"][piece][0] = to_pos[0]
        new_state["board"][piece][1] = to_pos[1]
    
    # Remove the moved piece from its original position
    del new_state["board"][piece][:]
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    white_pieces = sum(1 for _, pos in state["board"].values() if pos[0] == '1')
    black_pieces = sum(1 for _, pos in state["board"].values() if pos[0] == '5')
    if white_pieces > black_pieces:
        return 0
    elif black_pieces > white_pieces:
        return 1
    else:
        return -4  # Terminal state

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    white_pieces = sum(1 for _, pos in state["board"].values() if pos[0] == '1')
    black_pieces = sum(1 for _, pos in state["board"].values() if pos[0] == '5')
    if white_pieces > black_pieces:
        return [1.0, 0.0]
    elif black_pieces > white_pieces:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for piece, positions in state["board"].items():
        if piece in ["P", "K"]:
            for from_pos in positions:
                to_pos = (state["board"][piece][0], chr(ord(state["board"][piece][1]) + 1))
                if to_pos[0] != '5':
                    legal_actions.append(f"{piece}_{convert_coordinates(from_pos)}_{convert_coordinates(to_pos)}")
                if piece == "P" and from_pos[0] == '2':
                    to_pos = (state["board"][piece][0], chr(ord(state["board"][piece][1]) + 1))
                    if to_pos[0] != '5':
                        legal_actions.append(f"P_{convert_coordinates(from_pos)}_{convert_coordinates(to_pos)}")
        elif piece == "K":
            for from_pos in positions:
                for to_pos in [(int(state["board"][piece][0]) + i, ord(state["board"][piece][1]) + j) for i in range(-1, 2) for j in range(-1, 2) if -1 < i < 2 and -1 < j < 2]:
                    if to_pos[0] != '5':
                        legal_actions.append(f"{piece}_{convert_coordinates(from_pos)}_{convert_coordinates(to_pos)}")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {}
    player_1_obs = {}
    
    for piece, positions in state["board"].items():
        for pos in positions:
            if pos[0] == '1':
                player_0_obs[convert_coordinates(pos)] = piece
            elif pos[0] == '5':
                player_1_obs[convert_coordinates(pos)] = piece
    
    return [player_0_obs, player_1_obs]