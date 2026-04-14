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

def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    return {
        'board': {
            (0, 0): {'color': 'B', 'stunned': False},
            (0, 4): {'color': 'B', 'stunned': False},
            (4, 0): {'color': 'R', 'stunned': False},
            (4, 4): {'color': 'R', 'stunned': False}
        },
        'current_player': 0,
        'turn_count': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    source_square = tuple(map(int, action.split(' ')[1].split(',')))
    target_square = tuple(map(int, action.split(' ')[3].split(',')))

    # Check if the action is a valid move
    if source_square not in new_state['board'] or target_square not in new_state['board']:
        raise ValueError("Invalid move")

    # Get the source and target squares
    source_square_owner = new_state['board'][source_square]['color']
    target_square_owner = new_state['board'][target_square]['color']

    # Apply the move
    new_state['board'][source_square]['color'] = ' '
    new_state['board'][target_square]['color'] = source_square_owner

    # Check for stun
    if source_square_owner == 'B' and target_square_owner == 'R':
        new_state['board'][target_square]['stunned'] = True
    elif source_square_owner == 'R' and target_square_owner == 'B':
        new_state['board'][target_square]['stunned'] = True

    # Update current player
    new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0

    # Increment turn count
    new_state['turn_count'] += 1

    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['board'][state['board'].keys()[-1]]['color'] == 'B':
        return [1.0, 0.0]
    elif state['board'][state['board'].keys()[-1]]['color'] == 'R':
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    for square, piece in board.items():
        if piece['color'] == 'B':
            for move in [(square[0]+i, square[1]+j) for i in range(-1, 2) for j in range(-1, 2) if i != 0 or j != 0]:
                if move in board and board[move]['color'] == ' ':
                    legal_actions.append(f"move {square} to {move}")
        elif piece['color'] == 'R':
            for move in [(square[0]+i, square[1]+j) for i in range(-1, 2) for j in range(-1, 2) if i != 0 or j != 0]:
                if move in board and board[move]['color'] == ' ':
                    legal_actions.append(f"move {square} to {move}")

    if not legal_actions and state['turn_count'] < 50:
        return ['pass']
    else:
        return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    board = state['board']
    current_player = state['current_player']

    for square, piece in board.items():
        observation = {
            'position': square,
            'color': piece['color'],
            'stunned': piece['stunned']
        }
        if piece['color'] == 'B':
            observation['is_my_piece'] = True
        else:
            observation['is_my_piece'] = False
        observations.append(observation)

    return [observations, observations]