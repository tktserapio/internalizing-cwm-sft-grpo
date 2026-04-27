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

# Helper function to check if a position is within the board boundaries
def is_within_bounds(pos):
    return 0 <= pos[0] <= 4 and 0 <= pos[1] <= 4

# Initial state setup
def get_initial_state() -> State:
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

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    # Extract the source and destination positions from the action string
    src_pos = tuple(map(int, action.split(' to ')[0].split(',')))
    dst_pos = tuple(map(int, action.split(' to ')[1].split(',')))

    # Check if the action is valid
    if not is_within_bounds(src_pos) or not is_within_bounds(dst_pos):
        raise ValueError("Invalid move")

    # Get the piece to move
    piece_to_move = new_state['board'][src_pos[0]][src_pos[1]]
    if piece_to_move is None:
        raise ValueError("Source position is empty")

    # Update the board
    new_state['board'][src_pos[0]][src_pos[1]] = None
    new_state['board'][dst_pos[0]][dst_pos[1]] = piece_to_move

    # Update the current player
    new_state['current_player'] = 1 if new_state['current_player'] == 0 else 0

    # Increment the turn count
    new_state['turn_count'] += 1

    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Blue' if player_id == 0 else 'Red'

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state['current_player'] == 0 and state['board'][2][2] == 'B':
        return [1.0, 0.0]
    elif state['current_player'] == 1 and state['board'][2][2] == 'R':
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    current_player = state['current_player']
    board = state['board']
    turn_count = state['turn_count']

    for row in range(5):
        for col in range(5):
            piece = board[row][col]
            if piece is not None and piece == 'B' and turn_count % 2 == 0:
                # Player 0's turn
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (-1, 0), (0, -1)]:
                    dest_row, dest_col = row + dr, col + dc
                    if is_within_bounds((dest_row, dest_col)) and board[dest_row][dest_col] is None:
                        legal_actions.append(f'move ({row},{col}) to ({dest_row},{dest_col})')
            elif piece is not None and piece == 'R' and turn_count % 2 != 0:
                # Player 1's turn
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (-1, 0), (0, -1)]:
                    dest_row, dest_col = row + dr, col + dc
                    if is_within_bounds((dest_row, dest_col)) and board[dest_row][dest_col] is None:
                        legal_actions.append(f'move ({row},{col}) to ({dest_row},{dest_col})')

    return legal_actions

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    board = state['board']
    obs_0 = {'board': board, 'stunned': []}
    obs_1 = {'board': board, 'stunned': []}

    # Identify stunned pieces
    for row in range(5):
        for col in range(5):
            if board[row][col] is not None:
                stunned = False
                for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1), (-1, 0), (0, -1)]:
                    dest_row, dest_col = row + dr, col + dc
                    if is_within_bounds((dest_row, dest_col)) and board[dest_row][dest_col] is not None:
                        stunned = True
                        break
                if stunned:
                    obs_0['stunned'].append((row, col))
                    obs_1['stunned'].append((row, col))

    return [obs_0, obs_1]