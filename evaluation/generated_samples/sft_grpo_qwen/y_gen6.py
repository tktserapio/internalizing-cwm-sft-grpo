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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state with an empty board
    return {
        'board': {},
        'current_player': 0,
        'turn': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_state['turn'] += 1
    new_state['current_player'] = (new_state['current_player'] + 1) % 2
    
    # Parse the action
    row, col = map(int, action.split(','))

    # Update the board state
    new_state['board'][f'{row},{col}'] = new_state['current_player']
    
    # Check for win condition
    check_win(new_state)
    
    return new_state

def check_win(state: State) -> None:
    """
    Checks if a player has won the game based on the current state.
    If a player has won, sets the 'winner' field in the state dictionary.
    """
    board = state['board']
    winner = None

    # Define the sides of the triangle
    side_a_b = [1, 3, 6]
    side_a_c = [2, 5, 9]
    side_b_c = [6, 7, 8, 9]

    # Check if the current player has formed a winning connection
    for side in [side_a_b, side_a_c, side_b_c]:
        if all(cell in board for cell in side):
            winner = state['current_player']
            break

    if winner is not None:
        state['winner'] = winner

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['winner'] is not None:
        return [1.0, -1.0] if state['winner'] == 0 else [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    legal_actions = []
    for row in range(10):
        for col in range(10):
            if f'{row},{col}' not in board:
                legal_actions.append(f'{row},{col}')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = [
        {'board': board, 'current_player': state['current_player']},
        {'board': board, 'current_player': state['current_player']}
    ]
    return observations