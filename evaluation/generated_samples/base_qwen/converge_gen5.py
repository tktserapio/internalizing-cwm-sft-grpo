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
def is_valid_move(action: Action, state: State) -> bool:
    """Check if the given action is valid based on the current state."""
    # Extract coordinates from the action string
    start, end = action.split(" to ")
    start_row, start_col = map(int, start.split(","))
    end_row, end_col = map(int, end.split(","))

    # Check if the move is within the board boundaries
    if not (0 <= start_row < 5 and 0 <= start_col < 5 and 0 <= end_row < 5 and 0 <= end_col < 5):
        return False

    # Check if the destination is empty
    if (end_row, end_col) in state['board']:
        return False

    return True

def apply_action(state: State, action: Action) -> State:
    """Apply the given action to the state and return the new state."""
    new_state = copy.deepcopy(state)
    # Extract coordinates from the action string
    start, end = action.split(" to ")
    start_row, start_col = map(int, start.split(","))
    end_row, end_col = map(int, end.split(","))

    # Update the board with the new position
    new_state['board'][end_row, end_col] = new_state['current_player']
    del new_state['board'][start_row, start_col]

    # Update the current player
    new_state['current_player'] = 1 - new_state['current_player']

    return new_state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    board = {(i, j): None for i in range(5) for j in range(5)}
    board[(0, 0)], board[(0, 4)] = 'B', 'B'
    board[(4, 0)], board[(4, 4)] = 'R', 'R'
    state = {
        'board': board,
        'current_player': 0,
        'turn_count': 0,
        'stunned_units': {}
    }
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['current_player'] == 0 and state['board'][2, 2] == 'B':
        return [1.0, 0.0]
    elif state['current_player'] == 1 and state['board'][2, 2] == 'R':
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    current_player = state['current_player']
    board = state['board']
    current_player_units = [(r, c) for r, c in board.items() if board[(r, c)] == chr(ord('B') + current_player)]
    opponent_units = [(r, c) for r, c in board.items() if board[(r, c)] != None and board[(r, c)] != chr(ord('B') + current_player)]

    for unit in current_player_units:
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            new_row, new_col = unit[0] + dr, unit[1] + dc
            if (new_row, new_col) in board and board[(new_row, new_col)] is None:
                legal_actions.append(f"move {unit} to ({new_row}, {new_col})")
            elif (new_row, new_col) in opponent_units:
                legal_actions.append(f"move {unit} to ({new_row}, {new_col})")

    if not legal_actions:
        return ["pass"]
    else:
        return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    for player_id in range(2):
        observation = {}
        for row in range(5):
            for col in range(5):
                if board[(row, col)] is not None and board[(row, col)] == chr(ord('B') + player_id):
                    observation[(row, col)] = 1
                else:
                    observation[(row, col)] = 0
        observations.append(observation)
    return observations

# Example usage
initial_state = get_initial_state()
print(get_observations(initial_state))
print(get_legal_actions(initial_state))