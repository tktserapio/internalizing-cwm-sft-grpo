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

# Helper function to generate a unique ID for each cell
def generate_cell_id(row: int, col: int) -> str:
    return f"{chr(65 + col)}{row + 1}"

# Initial state generation
def get_initial_state() -> State:
    # Size-4 board example
    board_size = 4
    board = {}
    for row in range(board_size):
        for col in range(row + 1):
            cell_id = generate_cell_id(row, col)
            board[cell_id] = {'color': None, 'is_corner': False}
    
    # Mark corners
    board['A1'] = {'color': None, 'is_corner': True}
    board['A2'] = {'color': None, 'is_corner': True}
    board['C1'] = {'color': None, 'is_corner': True}
    board['C2'] = {'color': None, 'is_corner': True}
    
    return board

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    row, col = map(int, action.split(','))
    cell_id = generate_cell_id(row, col)
    
    if cell_id in new_state:
        new_state[cell_id]['color'] = 'B' if new_state[cell_id]['color'] == 'W' else 'W'
        new_state[cell_id]['is_corner'] = False  # Corners can only be played once
    
    return new_state

# Get current player
def get_current_player(state: State) -> int:
    black_stones = sum(1 for cell in state.values() if cell['color'] == 'B')
    white_stones = sum(1 for cell in state.values() if cell['color'] == 'W')
    
    if black_stones > white_stones:
        return 0  # Black's turn
    elif white_stones > black_stones:
        return 1  # White's turn
    else:
        return -4  # Terminal state

# Get player name
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Get rewards
def get_rewards(state: State) -> List[float]:
    black_stones = sum(1 for cell in state.values() if cell['color'] == 'B')
    white_stones = sum(1 for cell in state.values() if cell['color'] == 'W')
    
    if black_stones >= 3:
        return [1.0, 0.0]
    elif white_stones >= 3:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    for cell_id, cell_info in state.items():
        if cell_info['color'] is None:
            legal_actions.append(cell_id)
    return legal_actions

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    observations = []
    for cell_id, cell_info in state.items():
        observation = {
            'cell_id': cell_id,
            'color': cell_info['color'],
            'is_corner': cell_info['is_corner']
        }
        observations.append(observation)
    return observations

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Apply actions
    actions = ["0,0", "0,1", "1,0", "1,1", "2,0", "2,1"]
    for action in actions:
        initial_state = apply_action(initial_state, action)
        print(f"After {action}:")
        print(initial_state)
    
    # Get current player
    current_player = get_current_player(initial_state)
    print(f"Current Player: {get_player_name(current_player)}")
    
    # Get rewards
    rewards = get_rewards(initial_state)
    print(f"Rewards: {rewards}")
    
    # Get legal actions
    legal_actions = get_legal_actions(initial_state)
    print(f"Legal Actions: {legal_actions}")
    
    # Get observations
    observations = get_observations(initial_state)
    print(f"Observations: {observations}")