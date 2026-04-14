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
    return {
        'board': [
            ['r', 'n', 'b', 'q', 'k'],
            ['p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K']
        ],
        'turn': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse the action
    piece, from_square, to_square = action.split('_')
    from_file, from_rank = from_square[0], from_square[1]
    to_file, to_rank = to_square[0], to_square[1]

    # Convert file and rank to index
    from_index = 4 * (ord(from_file) - ord('a')) + int(from_rank) - 1
    to_index = 4 * (ord(to_file) - ord('a')) + int(to_rank) - 1

    # Get the current player
    current_player = state['turn']

    # Update the board
    board = state['board']
    board[from_index][int(from_rank) - 1], board[to_index][int(to_rank) - 1] = board[to_index][int(to_rank) - 1], board[from_index][int(from_rank) - 1]

    # Handle pawn promotion
    if piece == 'P' and abs(int(from_rank) - int(to_rank)) == 2:
        board[to_index][int(to_rank) - 1] = 'Q'

    # Handle castling
    if piece == 'R' and from_rank == to_rank and abs(ord(from_file) - ord(to_file)) == 2:
        board[to_index][int(to_rank) - 1] = board[to_index][int(from_rank) - 1]
        board[to_index][int(from_rank) - 1] = '.'

    # Handle en passant
    if piece == 'P' and abs(int(from_rank) - int(to_rank)) == 2:
        captured_piece = board[to_index + 1][int(to_rank) - 1]
        if captured_piece == 'P':
            board[to_index + 1][int(to_rank) - 1] = '.'

    # Update the turn
    state['turn'] = 1 - current_player

    # Determine the winner
    if checkmate(state):
        state['winner'] = current_player
    else:
        state['winner'] = None

    return state

def checkmate(state: State) -> bool:
    """
    Checks if the current player is in checkmate.
    """
    board = state['board']
    king_position = None
    for i in range(5):
        for j in range(5):
            if board[i][j] == 'K':
                king_position = (i, j)
                break
        if king_position is not None:
            break

    if king_position is None:
        return False

    king_row, king_col = king_position

    # Check all pieces for possible attacks
    for row in range(5):
        for col in range(5):
            piece = board[row][col]
            if piece != '.':
                if piece == 'P' and (row == king_row - 1 and col == king_col):
                    continue
                if piece == 'P' and (row == king_row + 1 and col == king_col):
                    continue
                if piece == 'N':
                    if (abs(row - king_row) == 2 and abs(col - king_col) == 1) or (abs(row - king_row) == 1 and abs(col - king_col) == 2):
                        continue
                if piece == 'B':
                    if abs(row - king_row) == abs(col - king_col):
                        continue
                if piece == 'R':
                    if row == king_row or col == king_col:
                        continue
                if piece == 'Q':
                    if abs(row - king_row) == abs(col - king_col):
                        continue
                    if row == king_row or col == king_col:
                        continue
                if piece == 'K':
                    continue

                # Check if the piece can move to the king's position
                if piece == 'P' and (row == king_row - 1 and col == king_col):
                    continue
                if piece == 'P' and (row == king_row + 1 and col == king_col):
                    continue
                if piece == 'N':
                    if (abs(row - king_row) == 2 and abs(col - king_col) == 1) or (abs(row - king_row) == 1 and abs(col - king_col) == 2):
                        continue
                if piece == 'B':
                    if abs(row - king_row) == abs(col - king_col):
                        continue
                if piece == 'R':
                    if row == king_row or col == king_col:
                        continue
                if piece == 'Q':
                    if abs(row - king_row) == abs(col - king_col):
                        continue
                    if row == king_row or col == king_col:
                        continue
                if piece == 'K':
                    continue

                return True

    return False

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['turn']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['winner'] is not None:
        return [1.0, -1.0] if state['winner'] == 0 else [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    board = state['board']
    current_player = state['turn']
    legal_actions = []

    for row in range(5):
        for col in range(5):
            piece = board[row][col]
            if piece != '.':
                if piece == 'P':
                    if current_player == 0:
                        if row == 1:
                            legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                        elif row == 2:
                            legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                    else:
                        if row == 4:
                            legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                elif piece == 'N':
                    if current_player == 0:
                        if row == 0:
                            legal_actions.append(f"N_{chr(ord('a') + col)}_{chr(ord('a') + col + 2)}")
                        elif row == 1:
                            legal_actions.append(f"N_{chr(ord('a') + col)}_{chr(ord('a') + col + 2)}")
                    else:
                        if row == 3:
                            legal_actions.append(f"N_{chr(ord('a') + col)}_{chr(ord('a') + col + 2)}")
                elif piece == 'B':
                    if current_player == 0:
                        if row == 0:
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                        elif row == 1:
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                        elif row == 2:
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                        elif row == 3:
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                    else:
                        if row == 3:
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                        elif row == 2:
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                        elif row == 1:
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                        elif row == 0:
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                elif piece == 'R':
                    if current_player == 0:
                        if row == 0:
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 1:
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 2:
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 3:
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                    else:
                        if row == 3:
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 2:
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 1:
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 0:
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                elif piece == 'Q':
                    if current_player == 0:
                        if row == 0:
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 1:
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 2:
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 3:
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                    else:
                        if row == 3:
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 2:
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 1:
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 0:
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                elif piece == 'K':
                    if current_player == 0:
                        if row == 0:
                            legal_actions.append(f"K_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 1:
                            legal_actions.append(f"K_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                    else:
                        if row == 3:
                            legal_actions.append(f"K_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 2:
                            legal_actions.append(f"K_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 1:
                            legal_actions.append(f"K_{chr(ord('a') + col)}_{chr(ord('a') + col)}")
                        elif row == 0:
                            legal_actions.append(f"K_{chr(ord('a') + col)}_{chr(ord('a') + col)}")

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    player_0_obs = {
        'board': board,
        'turn': state['turn'],
        'winner': state['winner']
    }
    player_1_obs = {
        'board': board,
        'turn': state['turn'],
        'winner': state['winner']
    }
    return [player_0_obs, player_1_obs]