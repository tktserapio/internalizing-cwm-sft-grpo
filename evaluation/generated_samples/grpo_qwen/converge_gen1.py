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
            [None, None, 'C', None, None],
            [None, None, None, None, None],
            ['B', None, None, None, 'R']
        ],
        'current_player': 0,
        'turn_count': 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    board = new_state['board']
    current_player = new_state['current_player']
    turn_count = new_state['turn_count']

    # Parse the action
    parts = action.split(' to ')
    start_pos = tuple(map(int, parts[0].split(',')))
    end_pos = tuple(map(int, parts[1].split(',')))

    # Check if the action is valid
    if not is_valid_move(board, start_pos, end_pos):
        raise ValueError("Invalid move")

    # Apply the move
    board[start_pos[0]][start_pos[1]] = None
    board[end_pos[0]][end_pos[1]] = 'B' if current_player == 0 else 'R'

    # Check for stun
    for i in range(max(0, start_pos[0] - 1), min(5, start_pos[0] + 2)):
        for j in range(max(0, start_pos[1] - 1), min(5, start_pos[1] + 2)):
            if board[i][j] != None and abs(i - start_pos[0]) + abs(j - start_pos[1]) == 1:
                board[i][j] = 'S' if current_player == 0 else 'S'
                break

    # Update the current player
    new_state['current_player'] = 1 if current_player == 0 else 0
    new_state['turn_count'] += 1

    return new_state

def is_valid_move(board: List[List[str]], start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> bool:
    """
    Checks if a move is valid based on the rules of the game.
    """
    row, col = start_pos
    if not (0 <= row < 5 and 0 <= col < 5):
        return False
    if board[row][col] == None:
        return False
    if abs(row - end_pos[0]) + abs(col - end_pos[1]) != 1:
        return False
    return True

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['current_player'] == -4:
        return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    for row in range(5):
        for col in range(5):
            if board[row][col] == 'B' if current_player == 0 else 'R':
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, 0), (-1, -1), (0, -1)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < 5 and 0 <= new_col < 5 and board[new_row][new_col] == None:
                        legal_actions.append(f'move ({row},{col}) to ({new_row},{new_col})')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    for player_id in [0, 1]:
        obs = {'board': [[cell if cell == 'B' if player_id == 0 else 'R' else None for cell in row] for row in board], 'current_player': player_id}
        observations.append(obs)
    return observations