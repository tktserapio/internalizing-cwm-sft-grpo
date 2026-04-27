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
        'current_player': 0  # Black starts first
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = new_state['current_player']
    
    # Convert action string to coordinates
    action_parts = action.split(',')
    row = int(action_parts[0])
    col = int(action_parts[1])
    
    # Update the board with the new stone
    new_state['board'][f'A{col}'] = player_id
    
    # Determine the new current player
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
    # In a perfect information game like Y, there's no need for rewards tracking
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    board = state['board']
    legal_actions = []
    
    for row in range(1, 4):
        for col in range(1, 4):
            if board[f'A{col}'] is None:
                legal_actions.append(f'{row},{col}')
                
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    
    # Player 0 (Black) observation
    black_observation = {
        'board': {cell: board[cell] for cell in board if cell.startswith('A')},
        'current_player': get_current_player(state)
    }
    observations.append(black_observation)
    
    # Player 1 (White) observation
    white_observation = {
        'board': {cell: board[cell] for cell in board if cell.startswith('B') or cell.startswith('C')},
        'current_player': get_current_player(state)
    }
    observations.append(white_observation)
    
    return observations