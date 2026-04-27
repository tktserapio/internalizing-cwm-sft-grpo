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

# Helper function to initialize the game state
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initialize the board with pieces in their starting positions
    board = {
        'r': (1, 1),  # Rook
        'n': (1, 2),  # Knight
        'b': (1, 3),  # Bishop
        'q': (1, 4),  # Queen
        'k': (1, 5),  # King
        'p': [(2, i) for i in range(1, 6)],  # Pawns
        'R': (5, 1),
        'N': (5, 2),
        'B': (5, 3),
        'Q': (5, 4),
        'K': (5, 5),
        'P': [(4, i) for i in range(1, 6)]
    }
    return {'board': board, 'turn': 0}

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    piece, from_square, to_square = action.split('_')
    from_row, from_col = from_square[0], int(from_square[1]) - 1
    to_row, to_col = to_square[0], int(to_square[1]) - 1
    
    # Get the piece and its current position
    piece_position = new_state['board'].get(piece)
    if piece_position is None:
        raise ValueError(f"Invalid piece: {piece}")
    
    # Check if the move is valid
    if piece == 'P' and (from_row == 4 and from_col == 1):
        # Promotion
        new_state['board'][piece] = (to_row, to_col)
        new_state['board'][f'{piece}_promotion'] = (to_row, to_col)
        del new_state['board'][piece]
    elif piece == 'P' and (from_row == 4 and from_col == 2):
        # Promotion
        new_state['board'][piece] = (to_row, to_col)
        new_state['board'][f'{piece}_promotion'] = (to_row, to_col)
        del new_state['board'][piece]
    else:
        new_state['board'][piece] = (to_row, to_col)
        del new_state['board'][piece_position]
    
    # Update the turn
    new_state['turn'] = 1 - new_state['turn']
    return new_state

# Determine the current player
def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['turn']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return f"Player {player_id}"

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # Assuming a simple scoring system where the winner gets +1.0 and the loser gets -1.0
    if state['turn'] == 0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    board = state['board']
    turn = state['turn']
    
    # Iterate over each piece and its possible moves
    for piece, position in board.items():
        row, col = position
        if piece == 'P':
            # Pawn moves and promotions
            if turn == 0:
                if row == 4 and col == 1:
                    legal_actions.append(f"P_{row}_{col}_Q")
                elif row == 4 and col == 2:
                    legal_actions.append(f"P_{row}_{col}_Q")
                else:
                    if row > 1:
                        if board.get(f"P_{row-1}_{col}") is None:
                            legal_actions.append(f"P_{row}_{col}_{row-1}_{col}")
                    if col > 0:
                        if board.get(f"P_{row}_{col-1}") is None:
                            legal_actions.append(f"P_{row}_{col}_{row}_{col-1}")
                    if col < 5:
                        if board.get(f"P_{row}_{col+1}") is None:
                            legal_actions.append(f"P_{row}_{col}_{row}_{col+1}")
            else:
                if row == 1 and col == 1:
                    legal_actions.append(f"P_{row}_{col}_Q")
                elif row == 1 and col == 2:
                    legal_actions.append(f"P_{row}_{col}_Q")
                else:
                    if row < 4:
                        if board.get(f"P_{row+1}_{col}") is None:
                            legal_actions.append(f"P_{row}_{col}_{row+1}_{col}")
                    if col > 0:
                        if board.get(f"P_{row}_{col-1}") is None:
                            legal_actions.append(f"P_{row}_{col}_{row}_{col-1}")
                    if col < 5:
                        if board.get(f"P_{row}_{col+1}") is None:
                            legal_actions.append(f"P_{row}_{col}_{row}_{col+1}")
        else:
            # Other pieces
            if piece == 'R':
                for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    row, col = position
                    while 0 <= row + dr < 5 and 0 <= col + dc < 5:
                        next_row, next_col = row + dr, col + dc
                        if board.get(f"{piece}_{next_row}_{next_col}") is not None:
                            break
                        legal_actions.append(f"{piece}_{row}_{next_row}")
                        row, col = next_row, next_col
            elif piece == 'N':
                for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                    row, col = position
                    next_row, next_col = row + dr, col + dc
                    if 0 <= next_row < 5 and 0 <= next_col < 5:
                        if board.get(f"{piece}_{next_row}_{next_col}") is not None:
                            break
                        legal_actions.append(f"{piece}_{row}_{next_row}")
            elif piece == 'B':
                for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    row, col = position
                    while 0 <= row + dr < 5 and 0 <= col + dc < 5:
                        next_row, next_col = row + dr, col + dc
                        if board.get(f"{piece}_{next_row}_{next_col}") is not None:
                            break
                        legal_actions.append(f"{piece}_{row}_{next_row}")
                        row, col = next_row, next_col
            elif piece == 'Q':
                for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    row, col = position
                    while 0 <= row + dr < 5 and 0 <= col + dc < 5:
                        next_row, next_col = row + dr, col + dc
                        if board.get(f"{piece}_{next_row}_{next_col}") is not None:
                            break
                        legal_actions.append(f"{piece}_{row}_{next_row}")
                        row, col = next_row, next_col
                for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    row, col = position
                    while 0 <= row + dr < 5 and 0 <= col + dc < 5:
                        next_row, next_col = row + dr, col + dc
                        if board.get(f"{piece}_{next_row}_{next_col}") is not None:
                            break
                        legal_actions.append(f"{piece}_{row}_{next_row}")
                        row, col = next_row, next_col
            elif piece == 'K':
                for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    row, col = position
                    next_row, next_col = row + dr, col + dc
                    if 0 <= next_row < 5 and 0 <= next_col < 5:
                        if board.get(f"{piece}_{next_row}_{next_col}") is not None:
                            break
                        legal_actions.append(f"{piece}_{row}_{next_row}")
    return legal_actions

# Get observations for the players
def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    player_0_obs = {k: v for k, v in board.items() if v[0] < 3}
    player_1_obs = {k: v for k, v in board.items() if v[0] > 2}
    return [player_0_obs, player_1_obs]