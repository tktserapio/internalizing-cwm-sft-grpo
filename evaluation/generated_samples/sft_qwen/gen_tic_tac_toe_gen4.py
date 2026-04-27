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
    """
    Returns the initial game state before any actions are taken.
    """
    return {
        'board': [[' ' for _ in range(6)] for _ in range(6)],
        'current_player': 0,
        'winner': None,
        'turn_count': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse the action string
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if row < 0 or row > 5 or col < 0 or col > 5 or state['board'][row][col] != ' ':
        raise ValueError("Invalid action")

    # Update the board
    state['board'][row][col] = 'x' if state['current_player'] == 0 else 'o'

    # Switch the current player
    state['current_player'] = (state['current_player'] + 1) % 2

    # Increment the turn count
    state['turn_count'] += 1

    # Check for a win condition
    check_winner(state)

    return state

def check_winner(state: State):
    """
    Checks for a win condition and updates the state accordingly.
    """
    # Check horizontal lines
    for row in state['board']:
        if len(set(row)) == 1 and row[0] != ' ':
            state['winner'] = state['current_player']
            return

    # Check vertical lines
    for col in range(6):
        if len(set([state['board'][r][col] for r in range(6)])) == 1 and state['board'][0][col] != ' ':
            state['winner'] = state['current_player']
            return

    # Check diagonal lines
    for i in range(3):
        if state['board'][i][i] == state['board'][i+1][i+1] == state['board'][i+2][i+2] == state['board'][i+3][i+3] != ' ':
            state['winner'] = state['current_player']
            return
        if state['board'][i][5-i] == state['board'][i+1][4-i] == state['board'][i+2][3-i] == state['board'][i+3][2-i] != ' ':
            state['winner'] = state['current_player']
            return

    # Check for a draw
    if state['turn_count'] == 36:
        state['winner'] = None

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['winner'] if state['winner'] is not None else state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player x' if player_id == 0 else 'Player o'

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['winner'] is not None:
        return [-1.0, 1.0] if state['winner'] == 0 else [1.0, -1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    if state['winner'] is not None:
        return []
    return ['{},{}'.format(r, c) for r in range(6) for c in range(6) if state['board'][r][c] == ' ']

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    for i, player in enumerate(['x', 'o']):
        obs = {'board': copy.deepcopy(state['board']), 'legal_actions': get_legal_actions(state)}
        obs['player'] = player
        obs['turn_count'] = state['turn_count']
        obs['winner'] = state['winner']
        obs['current_player'] = state['current_player']
        observations.append(obs)
    return observations