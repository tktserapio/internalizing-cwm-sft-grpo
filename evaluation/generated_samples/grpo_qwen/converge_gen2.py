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
    # Initial state with player positions and center square as unoccupied
    return {
        'board': [
            ['-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-'],
            ['-', '-', 'B', 'R', '-'],
            ['-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-']
        ],
        'current_player': 0,
        'turn_count': 0,
        'center_occupied': False
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
    src = tuple(map(int, action.split(' ')[1].split(',')))
    dest = tuple(map(int, action.split(' ')[3].split(',')))
    
    # Check if the action is valid
    if not is_valid_move(board, src, dest):
        raise ValueError("Invalid move")
    
    # Apply the move
    board[src[0]][src[1]], board[dest[0]][dest[1]] = board[dest[0]][dest[1]], board[src[0]][src[1]]
    
    # Update the current player
    current_player = 1 if current_player == 0 else 0
    
    # Check for stun
    if is_adjacent_to_stunned(board, src):
        board[src[0]][src[1]] = '-'
    
    # Update the turn count
    turn_count += 1
    
    # Check if the center square is occupied
    center_square = (2, 2)
    if board[center_square[0]][center_square[1]] == 'B':
        state['center_occupied'] = True
    elif board[center_square[0]][center_square[1]] == 'R':
        state['center_occupied'] = True
    
    # Determine the winner
    if state['center_occupied']:
        state['winner'] = current_player
    elif turn_count >= 50:
        state['winner'] = -4  # Draw
    
    return state

def is_valid_move(board, src, dest):
    """
    Checks if the move from src to dest is valid.
    """
    row, col = src
    newRow, newCol = dest
    if newRow < 0 or newRow > 4 or newCol < 0 or newCol > 4:
        return False
    if board[newRow][newCol] != '-':
        return False
    return True

def is_adjacent_to_stunned(board, position):
    """
    Checks if the given position is adjacent to a stunned unit.
    """
    row, col = position
    for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        newRow, newCol = row + dr, col + dc
        if 0 <= newRow <= 4 and 0 <= newCol <= 4 and board[newRow][newCol] == 'S':
            return True
    return False

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Blue' if player_id == 0 else 'Red'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state['winner'] == 0:
        return [1.0, 0.0]
    elif state['winner'] == 1:
        return [0.0, 1.0]
    elif state['winner'] == -4:
        return [0.5, 0.5]  # Draw
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []
    
    for i in range(5):
        for j in range(5):
            if board[i][j] == 'B' and current_player == 0:
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < 5 and 0 <= nj < 5 and board[ni][nj] == '-':
                        legal_actions.append(f'move ({i},{j}) to ({ni},{nj})')
            elif board[i][j] == 'R' and current_player == 1:
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < 5 and 0 <= nj < 5 and board[ni][nj] == '-':
                        legal_actions.append(f'move ({i},{j}) to ({ni},{nj})')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    for i in range(5):
        for j in range(5):
            if board[i][j] == 'B':
                observations.append({'position': (i, j)})
            elif board[i][j] == 'R':
                observations.append({'position': (i, j)})
    return observations