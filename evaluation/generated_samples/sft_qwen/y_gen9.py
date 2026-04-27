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

# Helper function to convert coordinates to action string
def coord_to_action(coord: Tuple[int, int]) -> Action:
    return f"{coord[0]},{coord[1]}"

# Initial state of the game
def get_initial_state() -> State:
    # Initialize the board as a dictionary with coordinates as keys
    board = {
        'A1': {'color': None},
        'A2': {'color': None},
        'A3': {'color': None},
        'A4': {'color': None},
        'B1': {'color': None},
        'B2': {'color': None},
        'B3': {'color': None},
        'C1': {'color': None},
        'C2': {'color': None},
        'C3': {'color': None}
    }
    return board

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert the action string to coordinates
    coords = action.split(',')
    x, y = int(coords[0]), int(coords[1])
    
    # Check if the action is valid
    if state.get(f"A{x + 1}") is None or state.get(f"B{x + 1}") is None or state.get(f"C{x + 1}") is None:
        raise ValueError("Invalid action: out of bounds")
    
    # Place the stone on the board
    state[f"A{x + 1}']['color'] = 'Black'
    state[f"B{x + 1}']['color'] = 'White'
    state[f"C{x + 1}']['color'] = 'Black'
    
    return state

# Get the current player
def get_current_player(state: State) -> int:
    black_stones = sum(1 for _, color in state.items() if color == 'Black')
    white_stones = sum(1 for _, color in state.items() if color == 'White')
    
    if black_stones > white_stones:
        return 0  # Black's turn
    elif white_stones > black_stones:
        return 1  # White's turn
    else:
        return -4  # Terminal state

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Get rewards for the given state
def get_rewards(state: State) -> List[float]:
    black_stones = sum(1 for _, color in state.items() if color == 'Black')
    white_stones = sum(1 for _, color in state.items() if color == 'White')
    
    if black_stones > white_stones:
        return [1.0, 0.0]
    elif white_stones > black_stones:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    # Legal moves are all empty cells
    legal_moves = []
    for key in state.keys():
        if state[key]['color'] is None:
            legal_moves.append(coord_to_action(key))
    return legal_moves

# Get observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    # Observations are identical for both players
    observation = {
        'board': state,
        'current_player': get_current_player(state),
        'player_name': get_player_name(get_current_player(state))
    }
    return [observation, observation]