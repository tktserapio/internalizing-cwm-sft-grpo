import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to create the initial board setup
def create_initial_board() -> List[List[str]]:
    return [
        ['r', 'n', 'b', 'q', 'k'],  # Rank 5 (Black)
        ['p', 'p', 'p', 'p', 'p'],  # Rank 4
        ['.', '.', '.', '.', '.'],  # Rank 3
        ['P', 'P', 'P', 'P', 'P'],  # Rank 2
        ['R', 'N', 'B', 'Q', 'K']   # Rank 1 (White)
    ]

# Function to get the initial state of the game
def get_initial_state() -> State:
    return {
        'board': create_initial_board(),
        'current_player': 0,  # 0 for White, 1 for Black
        'move_count': 0,
        'last_pawn_move_or_capture': 0,  # For 50-move rule
        'is_terminal': False,
        'winner': None
    }

# Function to apply an action to the current state and return the new state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        'board': [row[:] for row in state['board']],  # Deep copy of the board
        'current_player': 1 - state['current_player'],  # Switch player
        'move_count': state['move_count'] + 1,
        'last_pawn_move_or_capture': state['last_pawn_move_or_capture'],
        'is_terminal': False,
        'winner': None
    }

    # Parse the action
    parts = action.split('_')
    piece, from_square, to_square = parts[0], parts[1], parts[2]
    promotion = parts[3] if len(parts) == 4 else None

    # Convert algebraic notation to board indices
    from_rank, from_file = 5 - int(from_square[1]), ord(from_square[0]) - ord('a')
    to_rank, to_file = 5 - int(to_square[1]), ord(to_square[0]) - ord('a')

    # Move the piece on the board
    new_state['board'][to_rank][to_file] = new_state['board'][from_rank][from_file]
    new_state['board'][from_rank][from_file] = '.'

    # Handle pawn promotion
    if promotion:
        new_state['board'][to_rank][to_file] = promotion

    # Update last pawn move or capture
    if piece == 'P' or state['board'][to_rank][to_file] != '.':
        new_state['last_pawn_move_or_capture'] = new_state['move_count']

    # Check for terminal state (checkmate, stalemate, etc.)
    # This is a placeholder; actual implementation would require more logic
    # new_state['is_terminal'], new_state['winner'] = check_terminal_state(new_state)

    return new_state

# Function to get the current player
def get_current_player(state: State) -> int:
    return -4 if state['is_terminal'] else state['current_player']

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return "White" if player_id == 0 else "Black"

# Function to get the rewards for each player
def get_rewards(state: State) -> List[float]:
    if state['is_terminal']:
        if state['winner'] == 0:
            return [1.0, -1.0]
        elif state['winner'] == 1:
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]  # Draw
    return [0.0, 0.0]

# Function to get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state['is_terminal']:
        return []

    # Placeholder for generating legal moves
    # This would involve checking each piece for legal moves according to chess rules
    legal_actions = []

    # Example: Add all possible pawn moves for demonstration
    # This should be replaced with actual move generation logic
    for rank in range(5):
        for file in range(5):
            piece = state['board'][rank][file]
            if piece == 'P' and state['current_player'] == 0:
                # Example pawn move
                if rank > 0 and state['board'][rank - 1][file] == '.':
                    from_square = f"{chr(file + ord('a'))}{5 - rank}"
                    to_square = f"{chr(file + ord('a'))}{5 - (rank - 1)}"
                    legal_actions.append(f"P_{from_square}_{to_square}")

    return legal_actions

# Function to get observations for both players
def get_observations(state: State) -> List[PlayerObservation]:
    observation = {
        'board': state['board'],
        'current_player': state['current_player'],
        'move_count': state['move_count']
    }
    return [observation, observation]

# Note: The implementation of move generation, check/checkmate detection, and other chess rules is complex and requires detailed logic not covered in this basic setup.