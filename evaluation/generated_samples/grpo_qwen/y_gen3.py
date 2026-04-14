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

# Helper function to check if a move connects all three sides
def is_winner(state: State, player: int) -> bool:
    # Extract the board from the state
    board = state['board']
    # Check each side for a connected path
    for side in ['A', 'B', 'C']:
        for start in board[side]:
            if not explore_side(board, start, side, player):
                return False
    return True

# Helper function to explore a side for a connected path
def explore_side(board: Dict[str, List[int]], start: int, side: str, player: int) -> bool:
    if start in board[side]:
        board[side].remove(start)
        for neighbor in board[side]:
            if neighbor not in board[side]:
                continue
            if explore_side(board, neighbor, side, player):
                return True
        board[side].append(start)
    return False

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {
            'A': [1, 3, 6],
            'B': [2, 5, 9],
            'C': [6, 7, 8, 9]
        },
        'current_player': 0,
        'winner': -4
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    player = state['current_player']
    board = state['board']
    new_board = board.copy()
    
    # Convert action string to tuple
    action_tuple = tuple(map(int, action.split(',')))
    cell = action_tuple[0]
    
    # Place the stone
    if cell in board[f'{player + 1}']:
        new_board[f'{player + 1}'].remove(cell)
        new_board[f'{player + 1}'].append(cell)
    else:
        raise ValueError(f"Invalid action: Cell {cell} is not empty.")
    
    # Update the current player
    new_state = state.copy()
    new_state['board'] = new_board
    new_state['current_player'] = 1 - player
    
    # Check if there's a winner
    if is_winner(new_state, player):
        new_state['winner'] = player
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['winner'] == -4:
        return [0.0, 0.0]
    elif state['winner'] == 0:
        return [1.0, -1.0]
    elif state['winner'] == 1:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []
    for side in ['A', 'B', 'C']:
        for cell in board[side]:
            if cell not in board[f'{current_player + 1}']:
                legal_actions.append(f"{cell}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    for player in [0, 1]:
        observation = {}
        for side in ['A', 'B', 'C']:
            observation[side] = board[side]
        observation['current_player'] = player
        observation['board_size'] = len(board)
        observation['winner'] = state['winner']
        observations.append(observation)
    return observations