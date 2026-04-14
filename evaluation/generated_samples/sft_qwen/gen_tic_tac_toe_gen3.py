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
    # Parse the action
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if state['board'][row][col] != ' ':
        raise ValueError("Invalid action: Cell already occupied")

    # Update the board
    state['board'][row][col] = 'x' if state['current_player'] == 0 else 'o'

    # Switch the current player
    state['current_player'] = 1 - state['current_player']

    # Check for win condition
    check_win(state)

    # Check for draw condition
    if all(all(cell != ' ' for cell in row) for row in state['board']):
        state['winner'] = None
        state['game_over'] = True

    return state

def check_win(state: State):
    """
    Checks for a win condition and updates the state accordingly.
    """
    # Check rows and columns
    for i in range(6):
        if all(state['board'][i][j] == 'x' for j in range(6)) or \
           all(state['board'][i][j] == 'o' for j in range(6)):
            state['winner'] = 0 if state['current_player'] == 0 else 1
            state['game_over'] = True
            return

        if all(state['board'][j][i] == 'x' for j in range(6)) or \
           all(state['board'][j][i] == 'o' for j in range(6)):
            state['winner'] = 0 if state['current_player'] == 0 else 1
            state['game_over'] = True
            return

    # Check diagonals
    if all(state['board'][i][i] == 'x' for i in range(6)) or \
       all(state['board'][i][i] == 'o' for i in range(6)):
        state['winner'] = 0 if state['current_player'] == 0 else 1
        state['game_over'] = True
        return

    if all(state['board'][i][5-i] == 'x' for i in range(6)) or \
       all(state['board'][i][5-i] == 'o' for i in range(6)):
        state['winner'] = 0 if state['current_player'] == 0 else 1
        state['game_over'] = True
        return

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player 1' if player_id == 0 else 'Player 2'

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['game_over']:
        if state['winner'] is None:
            return [0.0, 0.0]
        elif state['winner'] == 0:
            return [1.0, -1.0]
        else:
            return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []
    else:
        return ['{},{}'.format(row, col) for row in range(6) for col in range(6) if state['board'][row][col] == ' ']

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for i, player in enumerate(['x', 'o']):
        observation = {}
        for row in range(6):
            for col in range(6):
                observation[f'{row},{col}'] = state['board'][row][col] == player
        observations.append(observation)
    return observations