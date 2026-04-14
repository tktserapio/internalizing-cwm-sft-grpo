import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import itertools

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper functions
def parse_action(action_str: str) -> tuple[int, int]:
    """Converts the action string into a (row, col) pair."""
    row, col = map(int, action_str.split(','))
    return row, col

def get_row_col_from_cell(cell: str) -> tuple[int, int]:
    """Converts a cell identifier into a (row, col) pair."""
    if cell.isdigit():
        return int(cell) - 1, 0
    else:
        row, col = cell[1:].split('-')
        return int(row) - 1, int(col) - 1

def is_corner(cell: str) -> bool:
    """Checks if the given cell is a corner cell."""
    _, col = get_row_col_from_cell(cell)
    return col == 0

def get_corners(board_size: int) -> list[str]:
    """Returns the corners of the board."""
    return [f"{i}{board_size}" for i in range(1, board_size + 1)]

def get_edges(board_size: int) -> list[str]:
    """Returns the edges of the board excluding corners."""
    edges = []
    for i in range(1, board_size + 1):
        edges.append(f"{i}{i}")
        edges.append(f"{i}{board_size + 1 - i}")
    return edges

def get_all_cells(board_size: int) -> list[str]:
    """Returns all cells on the board."""
    return [str(i) for i in range(1, board_size * (board_size + 1) // 2 + 1)]

def get_board_state(board_size: int) -> State:
    """Returns the initial game state for a given board size."""
    board = {}
    for cell in get_all_cells(board_size):
        board[cell] = {'color': None}
    return board

def get_initial_state(board_size: int) -> State:
    """Returns the initial game state before any actions are taken."""
    return get_board_state(board_size)

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    row, col = parse_action(action)
    cell = f"{row + 1}{col + 1}"
    if cell in state:
        state[cell]['color'] = 'B' if state[cell]['color'] != 'W' else 'W'
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    black_stones = sum(1 for cell in state.values() if cell['color'] == 'B')
    white_stones = sum(1 for cell in state.values() if cell['color'] == 'W')
    if black_stones > white_stones:
        return 0
    elif white_stones > black_stones:
        return 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    black_stones = sum(1 for cell in state.values() if cell['color'] == 'B')
    white_stones = sum(1 for cell in state.values() if cell['color'] == 'W')
    return [black_stones, white_stones]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for cell in state.keys():
        if state[cell]['color'] is None:
            legal_actions.append(cell)
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = [{'board': state, 'legal_actions': get_legal_actions(state)} for _ in range(2)]
    return observations

# Example usage
if __name__ == "__main__":
    board_size = 4
    initial_state = get_initial_state(board_size)
    print("Initial State:", initial_state)
    
    # Apply some actions
    actions = ["0,0", "0,1", "1,0", "1,1", "2,0", "2,1"]
    for action in actions:
        initial_state = apply_action(initial_state, action)
        print(f"After action '{action}':")
        print(initial_state)
        
    # Get current player and rewards
    current_player = get_current_player(initial_state)
    print(f"Current Player: {get_player_name(current_player)}")
    print(f"Rewards: {get_rewards(initial_state)}")
    
    # Get legal actions
    legal_actions = get_legal_actions(initial_state)
    print(f"Legal Actions: {legal_actions}")
    
    # Get observations
    observations = get_observations(initial_state)
    print(f"Observations: {observations}")