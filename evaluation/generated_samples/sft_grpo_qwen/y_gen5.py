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
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {
            'A1': None,
            'A2': None,
            'A3': None,
            'A4': None,
            'B1': None,
            'B2': None,
            'B3': None,
            'C1': None,
            'C2': None,
            'C3': None
        },
        'current_player': 0  # Black starts
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = new_state['current_player']
    
    # Convert action string to coordinates
    action_coords = action.split(',')
    row, col = int(action_coords[0]), int(action_coords[1])
    
    # Check if the cell is empty
    if new_state['board'][f'A{row + 1}'] is None:
        new_state['board'][f'A{row + 1}'] = player_id
    elif new_state['board'][f'B{row + 1}'] is None:
        new_state['board'][f'B{row + 1}'] = player_id
    elif new_state['board'][f'C{row + 1}'] is None:
        new_state['board'][f'C{row + 1}'] = player_id
    
    # Update current player
    new_state['current_player'] = (player_id + 1) % 2
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In a perfect information game like Y, there's no need to track running rewards
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []
    
    for row in range(1, 4):
        for col in range(1, 4):
            if board[f'A{row}'] is None and board[f'B{row}'] is None and board[f'C{row}'] is None:
                legal_actions.append(f'{row},{col}')
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = [
        {
            'board': board,
            'current_player': get_current_player(state),
            'legal_actions': get_legal_actions(state)
        },
        {
            'board': board,
            'current_player': get_current_player(state),
            'legal_actions': get_legal_actions(state)
        }
    ]
    return observations