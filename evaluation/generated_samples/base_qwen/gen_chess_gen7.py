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

# Helper functions
def parse_algebraic_notation(square: str) -> Tuple[int, int]:
    """Converts algebraic notation to (file, rank) tuple."""
    file = ord(square[0]) - ord('a')
    rank = int(square[1]) - 1
    return file, rank

def convert_square_to_string(file: int, rank: int) -> str:
    """Converts (file, rank) tuple to algebraic notation."""
    return f"{chr(file + ord('a'))}{rank + 1}"

def convert_state_to_string(state: State) -> State:
    """Converts internal state representation to human-readable string."""
    board = state['board']
    result = {convert_square_to_string(i, j): board[i][j] for i in range(5) for j in range(5)}
    return result

def convert_string_to_state(board_str: str) -> State:
    """Converts human-readable string to internal state representation."""
    board = [[None for _ in range(5)] for _ in range(5)]
    for square, piece in board_str.items():
        file, rank = parse_algebraic_notation(square)
        board[rank][file] = piece
    return {'board': board}

# Core functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial board setup
    board = [
        ['R', 'N', 'B', 'Q', 'K'],
        ['P', 'P', 'P', 'P', 'P'],
        ['.', '.', '.', '.', '.'],
        ['P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K']
    ]
    return convert_string_to_state(convert_state_to_string({'board': board}))

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    # Parse the action
    piece, from_square, to_square = action.split('_')
    from_file, from_rank = parse_algebraic_notation(from_square)
    to_file, to_rank = parse_algebraic_notation(to_square)
    
    # Convert to internal state
    board = state['board']
    
    # Capture piece if applicable
    captured_piece = None
    if board[to_rank][to_file] != '.':
        captured_piece = board[to_rank][to_file]
        board[to_rank][to_file] = '.'
    
    # Apply move
    board[from_rank][from_file], board[to_rank][to_file] = '.', piece
    
    # Update state
    new_state = convert_string_to_state(convert_state_to_string({'board': board}))
    
    # Handle promotions
    if piece == 'P' and (from_rank == 1 or from_rank == 4):
        new_state['promotion'] = True
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    board = state['board']
    white_pawns = sum(row.count('P') for row in board[:2])
    black_pawns = sum(row.count('P') for row in board[3:])
    if white_pawns > black_pawns:
        return 0
    elif black_pawns > white_pawns:
        return 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if get_current_player(state) == -4:
        return [1.0, -1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = get_current_player(state)
    legal_actions = []
    
    def is_valid_move(piece, from_square, to_square):
        from_file, from_rank = parse_algebraic_notation(from_square)
        to_file, to_rank = parse_algebraic_notation(to_square)
        
        if piece == 'P':
            if board[to_rank][to_file] == '.':
                if (from_rank == 1 and to_rank == 2) or (from_rank == 4 and to_rank == 3):
                    return True
                if abs(to_file - from_file) == 1 and board[to_rank][to_file] == '.':
                    return True
            return False
        elif piece == 'R':
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                row, col = from_rank + dr, from_file + dc
                while 0 <= row < 5 and 0 <= col < 5:
                    if board[row][col] != '.':
                        break
                    row += dr
                    col += dc
                if board[row][col] == '.':
                    continue
                if (row, col) == (to_rank, to_file):
                    return True
                if board[row][col] != '.' and board[row][col] != piece:
                    return True
            return False
        elif piece == 'N':
            if abs(to_file - from_file) == 1 and abs(to_rank - from_rank) == 1:
                return True
            return False
        elif piece == 'B':
            for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                row, col = from_rank + dr, from_file + dc
                while 0 <= row < 5 and 0 <= col < 5:
                    if board[row][col] != '.':
                        break
                    row += dr
                    col += dc
                if board[row][col] == '.':
                    continue
                if (row, col) == (to_rank, to_file):
                    return True
                if board[row][col] != '.' and board[row][col] != piece:
                    return True
            return False
        elif piece == 'Q':
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                row, col = from_rank + dr, from_file + dc
                while 0 <= row < 5 and 0 <= col < 5:
                    if board[row][col] != '.':
                        break
                    row += dr
                    col += dc
                if board[row][col] == '.':
                    continue
                if (row, col) == (to_rank, to_file):
                    return True
                if board[row][col] != '.' and board[row][col] != piece:
                    return True
            return False
        elif piece == 'K':
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                row, col = from_rank + dr, from_file + dc
                if 0 <= row < 5 and 0 <= col < 5 and board[row][col] == '.':
                    continue
                if board[row][col] != '.' and board[row][col] != piece:
                    return True
            return False
        elif piece == 'P' and (from_rank == 1 or from_rank == 4):
            if board[to_rank][to_file] == '.':
                return True
            if board[to_rank][to_file] != '.' and board[to_rank][to_file] != current_player:
                return True
        return False
    
    for rank in range(5):
        for file in range(5):
            piece = board[rank][file]
            if piece != '.':
                if piece == 'P' and (from_rank == 1 or from_rank == 4):
                    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        row, col = rank + dr, file + dc
                        if 0 <= row < 5 and 0 <= col < 5 and board[row][col] == '.':
                            legal_actions.append(f"P_{convert_square_to_string(file, rank)}_{convert_square_to_string(col, row)}")
                elif is_valid_move(piece, convert_square_to_string(file, rank), convert_square_to_string(file, rank)):
                    legal_actions.append(f"{piece}_{convert_square_to_string(file, rank)}_{convert_square_to_string(file, rank)}")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]