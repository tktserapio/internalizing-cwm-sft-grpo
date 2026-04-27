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
    # Initial state with player positions and center square
    return {
        'board': [
            [(0, 0), (0, 4)],  # Player 0 units
            [(4, 0), (4, 4)],  # Player 1 units
            [(2, 2)]           # Center square
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
    player_id = new_state['current_player']
    board = new_state['board']
    turn_count = new_state['turn_count']

    # Parse the action
    parts = action.split(' ')
    if len(parts) != 3:
        raise ValueError("Invalid action string")

    src_row, src_col = map(int, parts[1][1:-1].split(','))
    dest_row, dest_col = map(int, parts[2][1:-1].split(','))

    # Check if the source and destination are valid
    if (src_row, src_col) not in board[player_id] or (dest_row, dest_col) in board[player_id]:
        raise ValueError("Invalid move")

    # Apply the move
    board[player_id].remove((src_row, src_col))
    board[player_id].append((dest_row, dest_col))

    # Update the current player
    new_state['current_player'] = 1 if player_id == 0 else 0

    # Update the turn count
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
    # In this simple implementation, there are no rewards until the game ends
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    player_id = get_current_player(state)
    board = state['board']
    current_player_units = board[player_id]
    current_player_stunned = False

    # Check if the player has any units
    if not current_player_units:
        return []

    # Get the current player's units
    current_player_units = board[player_id]

    # Check for legal moves
    legal_moves = []
    for unit in current_player_units:
        row, col = unit
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5 and (new_row, new_col) not in board[player_id]:
                legal_moves.append(f'move ({row},{col}) to ({new_row},{new_col})')

    # Check for stun conditions
    for unit in current_player_units:
        row, col = unit
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5 and (new_row, new_col) in board[1 - player_id]:
                current_player_stunned = True

    # If the player has no legal moves, they must pass
    if not legal_moves and not current_player_stunned:
        return ['pass']
    else:
        return legal_moves

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    player_0_obs = {
        'units': board[0],
        'stunned': False
    }
    player_1_obs = {
        'units': board[1],
        'stunned': False
    }

    # Check for stun conditions
    for unit in board[0]:
        row, col = unit
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5 and (new_row, new_col) in board[1]:
                player_0_obs['stunned'] = True
                break

    for unit in board[1]:
        row, col = unit
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5 and (new_row, new_col) in board[0]:
                player_1_obs['stunned'] = True
                break

    return [player_0_obs, player_1_obs]