import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the board state
def _init_board(size: int) -> State:
    board = {}
    for i in range(1, size * (size + 1) // 2 + 1):
        board[f"{chr(ord('A') + (i - 1) // (size + 1))}{(i - 1) % (size + 1) + 1}"] = {'color': None, 'type': 'empty'}
    return board

# Function to convert coordinates to a single string representation
def _coord_to_str(coord: Tuple[int, int]) -> Action:
    return f"{ord(coord[0]) - ord('A')},{coord[1] - 1}"

# Function to convert a single string representation back to coordinates
def _str_to_coord(action: Action) -> Tuple[int, int]:
    coord = action.split(',')
    return (ord(coord[0].upper()) - ord('A'), int(coord[1]))

# Function to get the initial state of the game
def get_initial_state() -> State:
    # Size of the board is 4 for simplicity
    size = 4
    return _init_board(size)

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action to coordinates
    x, y = _str_to_coord(action)
    # Check if the action is valid
    if state.get(_coord_to_str((x, y)), {}).get('type') == 'empty':
        state[_coord_to_str((x, y))] = {'color': 1 if state['A'].get('color', 0) else 0, 'type': 'occupied'}
        return state
    else:
        raise ValueError("Invalid move")

# Function to get the current player
def get_current_player(state: State) -> int:
    # Determine the current player based on the first cell's color
    for key in state.keys():
        if state[key]['type'] == 'occupied':
            return state[key]['color']
    return -4  # Terminal state

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 1 else 'White'

# Function to get the rewards per player
def get_rewards(state: State) -> List[float]:
    # In a perfect information game, there should be no meaningful rewards until the game ends
    return [0.0, 0.0]

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    # Get the current player's color
    current_color = get_current_player(state)
    # Get the coordinates of the current player's last move
    last_move = next(key for key in state.keys() if state[key]['color'] == current_color and state[key]['type'] == 'occupied')
    # Get the coordinates of the corners
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    # Generate legal moves
    legal_moves = []
    for corner in corners:
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            x, y = corner
            while 0 <= x + dx < 4 and 0 <= y + dy < 4 and state.get(f"{chr(ord('A') + x + dx)},{y + dy}", {}).get('type') == 'empty':
                x += dx
                y += dy
                legal_moves.append(_coord_to_str((x, y)))
    return legal_moves

# Function to get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    # Since it's a perfect information game, both players see the same state
    return [{}, {}]