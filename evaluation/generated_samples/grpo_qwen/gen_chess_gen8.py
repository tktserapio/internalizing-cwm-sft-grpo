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
    # Initialize the board with the given positions
    board = {
        'r': {'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K'},
        'n': {'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K'},
        'b': {'c1': 'B', 'd1': 'Q', 'e1': 'K'},
        'q': {'d1': 'Q', 'e1': 'K'},
        'k': {'e1': 'K'},
        'p': {'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P'},
        'r': {'a5': 'R', 'b5': 'N', 'c5': 'B', 'd5': 'Q', 'e5': 'K'},
        'n': {'b5': 'N', 'c5': 'B', 'd5': 'Q', 'e5': 'K'},
        'b': {'c5': 'B', 'd5': 'Q', 'e5': 'K'},
        'q': {'d5': 'Q', 'e5': 'K'},
        'k': {'e5': 'K'}
    }
    return {
        'board': board,
        'turn': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    piece, from_square, to_square = action.split('_')
    from_square = tuple(from_square)
    to_square = tuple(to_square)
    
    # Get the piece and the piece's owner
    piece_owner = new_state['board'][piece][from_square]
    piece_type = piece_owner[0]
    
    # Check if the move is valid
    if piece_type == 'p' and abs(int(from_square[1]) - int(to_square[1])) == 2:
        # En passant
        en_passant_square = from_square[0] + str(int(from_square[1]) + int(to_square[1]) // 2)
        captured_piece = new_state['board'][piece][en_passant_square]
        del new_state['board'][piece][en_passant_square]
        new_state['board'][piece][to_square] = piece_owner
        new_state['board'][captured_piece]['a'] = ''
    else:
        new_state['board'][piece][to_square] = piece_owner
        del new_state['board'][piece][from_square]
    
    # Update the turn
    new_state['turn'] = 1 - new_state['turn']
    
    # Check for checkmate
    winner = check_for_checkmate(new_state)
    if winner:
        new_state['winner'] = winner
    
    return new_state

def check_for_checkmate(state: State) -> int:
    """
    Checks if the game is in a checkmate state.
    """
    king_square = None
    for piece, squares in state['board'].items():
        if 'K' in squares.values():
            king_square = next(iter(squares))
            break
    
    if not king_square:
        return None
    
    king_row, king_col = ord(king_square[0]) - ord('a'), int(king_square[1]) - 1
    
    # Check for check
    for piece, squares in state['board'].items():
        if piece != 'K':
            for square in squares:
                if squares[square] == 'Q':
                    # Queen can move diagonally, vertically, and horizontally
                    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                        row, col = king_row + dr, king_col + dc
                        if 0 <= row < 5 and 0 <= col < 5:
                            if state['board'][piece][f'{chr(ord("a") + col)}{5 - row}'] != '':
                                return 1 - state['turn']
                elif squares[square] == 'R':
                    # Rook can move horizontally or vertically
                    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        row, col = king_row + dr, king_col + dc
                        while 0 <= row < 5 and 0 <= col < 5:
                            if state['board'][piece][f'{chr(ord("a") + col)}{5 - row}'] != '':
                                return 1 - state['turn']
                            row += dr
                            col += dc
                elif squares[square] == 'B':
                    # Bishop can move diagonally
                    for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        row, col = king_row + dr, king_col + dc
                        while 0 <= row < 5 and 0 <= col < 5:
                            if state['board'][piece][f'{chr(ord("a") + col)}{5 - row}'] != '':
                                return 1 - state['turn']
                            row += dr
                            col += dc
                elif squares[square] == 'N':
                    # Knight can move in an L-shape
                    for dr, dc in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
                        row, col = king_row + dr, king_col + dc
                        if 0 <= row < 5 and 0 <= col < 5:
                            if state['board'][piece][f'{chr(ord("a") + col)}{5 - row}'] != '':
                                return 1 - state['turn']
                elif squares[square] == 'K':
                    # King can move one square in any direction
                    for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                        row, col = king_row + dr, king_col + dc
                        if 0 <= row < 5 and 0 <= col < 5:
                            if state['board'][piece][f'{chr(ord("a") + col)}{5 - row}'] != '':
                                return 1 - state['turn']
                elif squares[square] == 'P':
                    # Pawn can move forward one or two squares
                    if piece == 'P' and int(king_square[1]) - int(king_square[1]) == 2:
                        # En passant
                        en_passant_square = from_square[0] + str(int(from_square[1]) + int(to_square[1]) // 2)
                        captured_piece = state['board'][piece][en_passant_square]
                        del state['board'][piece][en_passant_square]
                        state['board'][piece][to_square] = piece_owner
                        state['board'][captured_piece]['a'] = ''
                        return 1 - state['turn']
                    else:
                        # Normal move
                        if piece == 'P' and int(king_square[1]) - int(king_square[1]) == 1:
                            # Moving forward one square
                            if state['board'][piece][f'{king_square[0]}{int(king_square[1]) + 1}'] != '':
                                return 1 - state['turn']
                        else:
                            # Moving forward two squares
                            if state['board'][piece][f'{king_square[0]}{int(king_square[1]) + 2}'] != '':
                                return 1 - state['turn']
    
    return None

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['turn']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['winner']:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for piece, squares in state['board'].items():
        if piece == 'K':
            continue
        for from_square, to_square in squares.items():
            if to_square == '':
                continue
            to_square = to_square[1] + to_square[0]
            if piece == 'P' and int(from_square[1]) - int(to_square) == 2:
                # En passant
                en_passant_square = from_square[0] + str(int(from_square[1]) + int(to_square) // 2)
                if state['board']['P'][en_passant_square] != '':
                    legal_actions.append(f"P_{from_square}_{to_square}_Q")
            else:
                legal_actions.append(f"{piece}_{from_square}_{to_square}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {}
    player_1_obs = {}
    for piece, squares in state['board'].items():
        for from_square, to_square in squares.items():
            if to_square != '':
                to_square = to_square[1] + to_square[0]
                player_0_obs[f"{piece}_{from_square}_{to_square}"] = 1
            else:
                player_0_obs[f"{piece}_{from_square}"] = 1
    for piece, squares in state['board'].items():
        for from_square, to_square in squares.items():
            if to_square != '':
                to_square = to_square[1] + to_square[0]
                player_1_obs[f"{piece}_{from_square}_{to_square}"] = 1
            else:
                player_1_obs[f"{piece}_{from_square}"] = 1
    return [player_0_obs, player_1_obs]