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
def parse_action(action_str: Action) -> tuple[int, int]:
    """Converts the action string into a (row, col) tuple."""
    if action_str.isdigit():
        return (int(action_str) - 1, 0)
    else:
        return (ord(action_str[0]) - ord('A'), int(action_str[1:]) - 1)

def reverse_action(action: Action) -> Action:
    """Reverses the action string for the opponent."""
    row, col = parse_action(action)
    return f"{col + 1},{6 - row}"

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Size-4 board
    board = {
        'A1': ' ', 'A2': ' ', 'A3': ' ', 'A4': ' ',
        'B1': ' ', 'B2': ' ', 'B3': ' ', 'B4': ' ',
        'C1': ' ', 'C2': ' ', 'C3': ' ', 'C4': ' '
    }
    return {'board': board}

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    board = state['board']
    player = 0 if action != reverse_action(action) else 1
    board[action] = 'B' if player == 0 else 'W'
    return {'board': board}

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    board = state['board']
    corners = ['A1', 'A4', 'C1', 'C4']
    for corner in corners:
        if board[corner] == 'B':
            return 0
        elif board[corner] == 'W':
            return 1
    return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    winner = get_current_player(state)
    if winner != -4:
        return [1.0, 0.0] if winner == 0 else [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    legal_actions = []
    for key, value in board.items():
        if value == ' ':
            legal_actions.append(key)
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    for player_id in range(2):
        observation = {}
        for key, value in board.items():
            if value == 'B':
                observation[key] = 1
            elif value == 'W':
                observation[key] = 2
            else:
                observation[key] = 0
        observations.append(observation)
    return observations

# Example usage
initial_state = get_initial_state()
print("Initial State:", initial_state)
print("Legal Actions:", get_legal_actions(initial_state))
print("Current Player:", get_current_player(initial_state))
print("Rewards:", get_rewards(initial_state))
print("Observations:", get_observations(initial_state))