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
    return {
        'board': [
            ['B', None, None, None, 'R'],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            ['R', None, None, None, 'B']
        ],
        'current_player': 0,
        'turn_count': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    board = state['board']
    current_player = state['current_player']
    turn_count = state['turn_count']

    # Parse the action
    source, target = parse_action(action)
    
    # Check if the action is valid
    if not is_valid_move(board, source, target):
        raise ValueError("Invalid move")
    
    # Apply the move
    board[source[0]][source[1]], board[target[0]][target[1]] = board[target[0]][target[1]], board[source[0]][source[1]]
    
    # Update the current player
    current_player = 1 if current_player == 0 else 0
    
    # Update the turn count
    turn_count += 1
    
    # Check for stun
    if is_adjacent_to_stunned(board, source):
        board[source[0]][source[1]] = None
    
    # Check for win condition
    if is_in_center(board, target):
        return {
            'board': board,
            'current_player': -4,
            'turn_count': turn_count
        }
    
    # Check for draw condition
    if turn_count >= 50:
        return {
            'board': board,
            'current_player': -4,
            'turn_count': turn_count
        }
    
    return {
        'board': board,
        'current_player': current_player,
        'turn_count': turn_count
    }

def parse_action(action: Action) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Parses the action string into source and target coordinates."""
    parts = action.split(' to ')
    source_parts = parts[0].split('(')[1].split(',')
    target_parts = parts[1].split(')')[0].split(',')
    return (int(source_parts[0]), int(source_parts[1])), (int(target_parts[0]), int(target_parts[1]))

def is_valid_move(board: List[List[str]], source: Tuple[int, int], target: Tuple[int, int]) -> bool:
    """Checks if the move is valid based on the rules."""
    row, col = source
    if not (0 <= row < 5 and 0 <= col < 5):
        return False
    if board[row][col] != 'B' and board[row][col] != 'R':
        return False
    if board[target[0]][target[1]] in ('B', 'R'):
        return False
    return True

def is_adjacent_to_stunned(board: List[List[str]], source: Tuple[int, int]) -> bool:
    """Checks if the source is adjacent to a stunned unit."""
    row, col = source
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
        neighbor_row, neighbor_col = row + dr, col + dc
        if 0 <= neighbor_row < 5 and 0 <= neighbor_col < 5 and board[neighbor_row][neighbor_col] == 'S':
            return True
    return False

def is_in_center(board: List[List[str]], target: Tuple[int, int]) -> bool:
    """Checks if the target is in the center square."""
    row, col = target
    return row == 2 and col == 2

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['current_player'] == -4:
        return [1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []
    
    for row in range(5):
        for col in range(5):
            if board[row][col] in ('B', 'R'):
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    neighbor_row, neighbor_col = row + dr, col + dc
                    if 0 <= neighbor_row < 5 and 0 <= neighbor_col < 5 and board[neighbor_row][neighbor_col] is None:
                        action = f'move ({row},{col}) to ({neighbor_row},{neighbor_col})'
                        legal_actions.append(action)
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    for player_id in [0, 1]:
        obs = {}
        for row in range(5):
            for col in range(5):
                if board[row][col] == 'B' and player_id == 0:
                    obs[(row, col)] = 'B'
                elif board[row][col] == 'R' and player_id == 1:
                    obs[(row, col)] = 'R'
                elif board[row][col] == 'S':
                    obs[(row, col)] = 'S'
        observations.append(obs)
    return observations