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
def convert_position_to_string(position):
    """Converts a tuple (rank, file) to a string 'a1' format."""
    return f"{chr(position[1] + ord('a'))}{position[0]}"

def convert_string_to_position(position):
    """Converts a string 'a1' format to a tuple (rank, file)."""
    return (int(position[1]) - 1, ord(position[0]) - ord('a'))

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial board setup
    board = {
        "r": {"d1": "R", "d5": "r"},
        "n": {"b1": "N", "c1": "N"},
        "b": {"c1": "B", "f1": "B"},
        "q": {"d1": "Q"},
        "k": {"d1": "K"},
        "p": [
            {"e2": "P", "e5": "P"},
            {"d2": "P", "d5": "P"},
            {"c2": "P", "c5": "P"},
            {"a2": "P", "a5": "P"},
            {"b2": "P", "b5": "P"}
        ],
        "R": {"d5": "R"},
        "N": {"b5": "N"},
        "B": {"c5": "B"},
        "Q": {"d5": "Q"},
        "K": {"d5": "K"}
    }
    return board

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    piece, from_pos, to_pos = action.split("_")
    from_pos = convert_position_to_string(convert_string_to_position(from_pos))
    to_pos = convert_position_to_string(convert_string_to_position(to_pos))

    if piece == "P":
        # Pawn movement
        if from_pos[0] == "1" and piece == "P" and to_pos[0] == "2":
            # En passant
            captured_piece = state["p"][to_pos[0]][to_pos[1]]
            del new_state["p"][to_pos[0]][to_pos[1]]
            new_state["p"][to_pos[0] + "_e2"][to_pos[1]] = captured_piece
        else:
            del new_state["p"][from_pos]
            new_state["p"][to_pos] = new_state["p"].pop(from_pos)
    elif piece == "N":
        # Knight movement
        if new_state[piece][from_pos] != " ":
            del new_state[piece][from_pos]
            new_state[piece][to_pos] = new_state[piece].pop(from_pos)
    elif piece == "B":
        # Bishop movement
        new_state[piece][to_pos] = new_state[piece].pop(from_pos)
    elif piece == "R":
        # Rook movement
        new_state[piece][to_pos] = new_state[piece].pop(from_pos)
    elif piece == "Q":
        # Queen movement
        new_state[piece][to_pos] = new_state[piece].pop(from_pos)
    elif piece == "K":
        # King movement
        new_state[piece][to_pos] = new_state[piece].pop(from_pos)

    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Determine the current player based on whose turn it is
    for piece, positions in state.items():
        for pos, _ in positions.items():
            if pos[0] == "1":
                return 0 if piece == "w" else 1
    return -4

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return "White" if player_id == 0 else "Black"

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # Determine the winner based on the state
    for piece, positions in state.items():
        for pos, _ in positions.items():
            if pos[0] == "5":
                return [1.0, -1.0] if piece == "w" else [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for piece, positions in state.items():
        for from_pos, _ in positions.items():
            for to_pos in [(int(pos[0]) + 1, int(pos[1])) for pos in positions]:
                if to_pos[0] <= 5 and to_pos[1] >= 0:
                    legal_actions.append(f"{piece}_{from_pos}_{convert_position_to_string(to_pos)}")
            for to_pos in [(int(pos[0]) - 1, int(pos[1])) for pos in positions]:
                if to_pos[0] <= 5 and to_pos[1] >= 0:
                    legal_actions.append(f"{piece}_{from_pos}_{convert_position_to_string(to_pos)}")
            for to_pos in [(int(pos[0]), int(pos[1]) + 1) for pos in positions]:
                if to_pos[0] <= 5 and to_pos[1] >= 0:
                    legal_actions.append(f"{piece}_{from_pos}_{convert_position_to_string(to_pos)}")
            for to_pos in [(int(pos[0]), int(pos[1]) - 1) for pos in positions]:
                if to_pos[0] <= 5 and to_pos[1] >= 0:
                    legal_actions.append(f"{piece}_{from_pos}_{convert_position_to_string(to_pos)}")
            for to_pos in [(int(pos[0]) + 1, int(pos[1]) + 1) for pos in positions]:
                if to_pos[0] <= 5 and to_pos[1] >= 0:
                    legal_actions.append(f"{piece}_{from_pos}_{convert_position_to_string(to_pos)}")
            for to_pos in [(int(pos[0]) + 1, int(pos[1]) - 1) for pos in positions]:
                if to_pos[0] <= 5 and to_pos[1] >= 0:
                    legal_actions.append(f"{piece}_{from_pos}_{convert_position_to_string(to_pos)}")
            for to_pos in [(int(pos[0]) - 1, int(pos[1]) + 1) for pos in positions]:
                if to_pos[0] <= 5 and to_pos[1] >= 0:
                    legal_actions.append(f"{piece}_{from_pos}_{convert_position_to_string(to_pos)}")
            for to_pos in [(int(pos[0]) - 1, int(pos[1]) - 1) for pos in positions]:
                if to_pos[0] <= 5 and to_pos[1] >= 0:
                    legal_actions.append(f"{piece}_{from_pos}_{convert_position_to_string(to_pos)}")
            if piece == "P" and from_pos[0] == "2":
                for to_pos in [(int(pos[0]) + 1, int(pos[1])) for pos in positions]:
                    if to_pos[0] <= 5 and to_pos[1] >= 0:
                        legal_actions.append(f"P_{from_pos}_{convert_position_to_string(to_pos)}_e2")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Observations are the same for both players
    observations = []
    for piece, positions in state.items():
        observation = {}
        for pos, piece_type in positions.items():
            if piece_type != " ":
                observation[pos] = piece_type
        observations.append(observation)
    return observations