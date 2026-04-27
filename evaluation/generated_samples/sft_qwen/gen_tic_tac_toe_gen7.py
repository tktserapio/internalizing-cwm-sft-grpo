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

# Helper function to check if a player has won
def check_win(board, player):
    # Check rows
    for row in range(6):
        if all(board[row][col] == player for col in range(6)):
            return True
    # Check columns
    for col in range(6):
        if all(board[row][col] == player for row in range(6)):
            return True
    # Check diagonals
    for i in range(3):  # Only need to check up to 3 because we're looking for 4 in a row
        if all(board[i + j][j] == player for j in range(4)) or \
           all(board[i + 5 - j][j] == player for j in range(4)):
            return True
    return False

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [[' ' for _ in range(6)] for _ in range(6)],
        'current_player': 0,
        'winner': None,
        'game_over': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    row, col = map(int, action.split(','))
    if state['board'][row][col] != ' ':
        raise ValueError("Cell already occupied")
    new_state['board'][row][col] = 'x' if state['current_player'] == 0 else 'o'
    new_state['current_player'] = (state['current_player'] + 1) % 2
    new_state['game_over'] = check_win(new_state['board'], 'x') or check_win(new_state['board'], 'o')
    new_state['winner'] = 'x' if check_win(new_state['board'], 'x') else ('o' if check_win(new_state['board'], 'o') else None)
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player 1' if player_id == 0 else 'Player 2'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['winner'] == 'x':
        return [1.0, 0.0]
    elif state['winner'] == 'o':
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []
    return [f"{row},{col}" for row in range(6) for col in range(6) if state['board'][row][col] == ' ']

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{'board': state['board'], 'legal_actions': get_legal_actions(state)} for _ in range(2)]