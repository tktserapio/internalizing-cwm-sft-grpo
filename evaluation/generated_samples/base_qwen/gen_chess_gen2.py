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

# Function to get the initial state of the game
def get_initial_state() -> State:
    # Initial board setup
    board = {
        "r": (5, 0), "n": (5, 1), "b": (5, 2), "q": (5, 3), "k": (5, 4),
        "p": [(4, i) for i in range(5)],
        "R": (1, 0), "N": (1, 1), "B": (1, 2), "Q": (1, 3), "K": (1, 4),
        "p": [(2, i) for i in range(5)]
    }
    return {"board": board, "turn": 0}

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action to tuple
    piece, from_coord, to_coord = action.split("_")
    from_coord = tuple(map(int, from_coord))
    to_coord = tuple(map(int, to_coord))
    
    # Get the current player
    player = state["turn"]
    
    # Create a deep copy of the state to avoid mutating the original
    new_state = copy.deepcopy(state)
    
    # Update the board
    if piece == "p":
        # Pawn movement
        if to_coord[0] == from_coord[0] + 1:
            new_state["board"][piece][1] = to_coord[1]
        else:
            # Promotion
            new_state["board"][piece][1] = to_coord[1]
            new_state["board"][piece] = (to_coord[0], to_coord[1])
            new_state["board"][f"{piece}_Q"] = (to_coord[0], to_coord[1])
    elif piece == "k":
        # King movement
        new_state["board"][piece] = to_coord
    elif piece == "r":
        # Rook movement
        new_state["board"][piece] = to_coord
    elif piece == "n":
        # Knight movement
        new_state["board"][piece] = to_coord
    elif piece == "b":
        # Bishop movement
        new_state["board"][piece] = to_coord
    elif piece == "q":
        # Queen movement
        new_state["board"][piece] = to_coord
    
    # Update the turn
    new_state["turn"] = (player + 1) % 2
    
    return new_state

# Function to get the current player
def get_current_player(state: State) -> int:
    return state["turn"]

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return "Player 0" if player_id == 0 else "Player 1"

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    # In this simple implementation, we assume a win/loss based on the final state
    # In a real game, you would need to evaluate the state to determine the winner
    if state["board"]["k"][0] == 1:
        return [1.0, -1.0]
    elif state["board"]["K"][0] == 5:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    # This is a simplified version. In a real game, you would need to generate all possible moves
    # and filter out illegal ones.
    player = state["turn"]
    legal_actions = []
    
    # Pawn moves
    for piece, pos in state["board"].items():
        if piece.startswith("p"):
            if pos[0] < 5 and state["board"][piece] != (pos[0] + 1, pos[1]):
                legal_actions.append(f"{piece}_{coord_to_str(pos)}_{coord_to_str((pos[0] + 1, pos[1]))}")
            if pos[0] == 1 and state["board"][piece] != (pos[0] + 2, pos[1]):
                legal_actions.append(f"{piece}_{coord_to_str(pos)}_{coord_to_str((pos[0] + 2, pos[1]))}")
    
    # Rook moves
    for piece, pos in state["board"].items():
        if piece.startswith("r"):
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                x, y = pos
                while 0 <= x + dx < 5 and 0 <= y + dy < 5:
                    if (x + dx, y + dy) in state["board"]:
                        break
                    legal_actions.append(f"{piece}_{coord_to_str(pos)}_{coord_to_str((x + dx, y + dy))}")
                    x += dx
                    y += dy
                    if (x + dx, y + dy) in state["board"]:
                        break
    
    # Knight moves
    for piece, pos in state["board"].items():
        if piece.startswith("n"):
            for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                x, y = pos
                if (x + dx, y + dy) in state["board"]:
                    legal_actions.append(f"{piece}_{coord_to_str(pos)}_{coord_to_str((x + dx, y + dy))}")
    
    # Bishop moves
    for piece, pos in state["board"].items():
        if piece.startswith("b"):
            for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                x, y = pos
                while 0 <= x + dx < 5 and 0 <= y + dy < 5:
                    if (x + dx, y + dy) in state["board"]:
                        break
                    legal_actions.append(f"{piece}_{coord_to_str(pos)}_{coord_to_str((x + dx, y + dy))}")
                    x += dx
                    y += dy
                    if (x + dx, y + dy) in state["board"]:
                        break
    
    # Queen moves
    for piece, pos in state["board"].items():
        if piece.startswith("q"):
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                x, y = pos
                while 0 <= x + dx < 5 and 0 <= y + dy < 5:
                    if (x + dx, y + dy) in state["board"]:
                        break
                    legal_actions.append(f"{piece}_{coord_to_str(pos)}_{coord_to_str((x + dx, y + dy))}")
                    x += dx
                    y += dy
                    if (x + dx, y + dy) in state["board"]:
                        break
    
    # King moves
    for piece, pos in state["board"].items():
        if piece.startswith("k"):
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                x, y = pos
                if (x + dx, y + dy) in state["board"]:
                    legal_actions.append(f"{piece}_{coord_to_str(pos)}_{coord_to_str((x + dx, y + dy))}")
    
    return legal_actions

# Function to get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    # Observations include the board state and the current player's turn
    observations = [
        {
            "board": {k: v for k, v in state["board"].items()},
            "turn": state["turn"]
        },
        {
            "board": {k: v for k, v in state["board"].items()},
            "turn": (state["turn"] + 1) % 2
        }
    ]
    return observations