import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the state
def get_initial_state() -> State:
    # Initialize the board state
    board = {
        'cells': [''] * 10,
        'turn': 0,  # 0 for Black, 1 for White
        'winner': None
    }
    return board

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action string to tuple
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if state['cells'][row*3 + col] != '':
        raise ValueError("Cell already occupied")

    # Update the board state
    state['cells'][row*3 + col] = 'B' if state['turn'] == 0 else 'W'
    state['turn'] = 1 - state['turn']

    # Check for win condition
    check_win(state)
    return state

# Check if there's a winner
def check_win(state: State):
    cells = state['cells']
    # Check rows, columns, and diagonals
    for i in range(3):
        if cells[i*3:i*3+3] == ['B', 'B', 'B'] or cells[i*3:i*3+3] == ['W', 'W', 'W']:
            state['winner'] = 0 if cells[i*3] == 'B' else 1
            return
        if cells[i::3] == ['B', 'B', 'B'] or cells[i::3] == ['W', 'W', 'W']:
            state['winner'] = 0 if cells[i] == 'B' else 1
            return
    if cells[0::4] == ['B', 'B', 'B'] or cells[0::4] == ['W', 'W', 'W']:
        state['winner'] = 0 if cells[0] == 'B' else 1
        return
    if cells[2:7:2] == ['B', 'B', 'B'] or cells[2:7:2] == ['W', 'W', 'W']:
        state['winner'] = 0 if cells[2] == 'B' else 1
        return
    if state['winner'] is None:
        if all(cell != '' for cell in cells):
            state['winner'] = None

# Get the current player
def get_current_player(state: State) -> int:
    return state['turn']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state['winner'] is None:
        return [0.0, 0.0]
    elif state['winner'] == 0:
        return [1.0, 0.0]
    else:
        return [0.0, 1.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state['winner'] is not None:
        return []
    return [f"{i},{j}" for i in range(3) for j in range(3) if state['cells'][i*3+j] == '']

# Get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    return [{'board': state['cells']}]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    print("Legal Actions:", get_legal_actions(initial_state))
    print("Player Name (Black):", get_player_name(0))
    print("Player Name (White):", get_player_name(1))
    print("Rewards (Initial State):", get_rewards(initial_state))