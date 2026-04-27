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
def is_win(state: State, player: int) -> bool:
    # Extracting the board state
    board = state['board']
    # Checking all possible winning moves
    for side in ['A', 'B', 'C']:
        for cell in board[side]:
            if board[side][cell]['color'] == player:
                # Check if the cell can form a win
                if check_win(board, cell, player):
                    return True
    return False

# Function to check if a move forms a win
def check_win(board: Dict[str, Dict[int, dict]], cell: int, player: int) -> bool:
    # Directions for checking connections
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]
    for dx, dy in directions:
        x, y = cell // 3, cell % 3
        while 0 <= x < 3 and 0 <= y < 3:
            if board[f'A'][x * 3 + y]['color'] == player:
                break
            x += dx
            y += dy
        else:
            continue
        # Check if the path connects to another side
        for ddx, ddy in directions:
            if ddx == 0 and ddy == 0:
                continue
            nx, ny = x + ddx, y + ddy
            if 0 <= nx < 3 and 0 <= ny < 3 and board[f'{chr(65 + nx)}'][nx * 3 + ny]['color'] == player:
                return True
    return False

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    board = {
        'A': {0: {'color': None}, 1: {'color': None}, 2: {'color': None}},
        'B': {3: {'color': None}, 4: {'color': None}, 5: {'color': None}},
        'C': {6: {'color': None}, 7: {'color': None}, 8: {'color': None}, 9: {'color': None}}
    }
    return {
        'board': board,
        'current_player': 0,
        'turn': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    player = state['current_player']
    new_state['board'][action]['color'] = player
    new_state['turn'] += 1
    new_state['current_player'] = 1 - player
    if is_win(new_state, player):
        new_state['winner'] = player
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['winner'] is not None:
        return [1.0, -1.0] if state['winner'] == 0 else [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None:
        return []
    board = state['board']
    legal_actions = []
    for side in ['A', 'B', 'C']:
        for cell in board[side]:
            if board[side][cell]['color'] is None:
                legal_actions.append(cell)
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    board = state['board']
    for side in ['A', 'B', 'C']:
        for cell in board[side]:
            if board[side][cell]['color'] is None:
                observations.append({
                    'board': board,
                    'legal_actions': get_legal_actions(state),
                    'current_player': state['current_player'],
                    'turn': state['turn'],
                    'winner': state['winner']
                })
            else:
                observations.append({
                    'board': board,
                    'legal_actions': [],
                    'current_player': state['current_player'],
                    'turn': state['turn'],
                    'winner': state['winner']
                })
    return observations