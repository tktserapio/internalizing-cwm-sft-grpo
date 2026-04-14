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
    # Initial state dictionary
    initial_state = {
        'board': {
            'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
            'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
            'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
            'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
            'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
        },
        'turn': 0,
        'winner': None
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    piece, from_square, to_square = action.split('_')
    from_square = from_square.lower()
    to_square = to_square.lower()

    # Get the piece and its current position
    piece_type = state['board'][from_square]
    from_position = (int(from_square[1]) - 1, ord(from_square[0]) - ord('a'))

    # Update the board with the moved piece
    new_state['board'][from_square] = '.'
    new_state['board'][to_square] = piece_type

    # Handle special cases like pawn promotion
    if piece == 'p' and (from_position[0] == 0 or from_position[0] == 4):
        new_state['board'][to_square] = piece + '_Q' if piece == 'p' else piece + '_R' if piece == 'p' else piece + '_B' if piece == 'p' else piece + '_N'

    # Handle castling (not available in this variant)
    if piece == 'r':
        if from_position == (0, 0) and to_position == (0, 2):
            new_state['board']['c1'] = '.'
            new_state['board']['g1'] = 'r'
        elif from_position == (0, 2) and to_position == (0, 0):
            new_state['board']['g1'] = '.'
            new_state['board']['c1'] = 'r'
        elif from_position == (4, 0) and to_position == (4, 2):
            new_state['board']['c5'] = '.'
            new_state['board']['g5'] = 'r'
        elif from_position == (4, 2) and to_position == (4, 0):
            new_state['board']['g5'] = '.'
            new_state['board']['c5'] = 'r'

    # Handle en passant (not available in this variant)
    if piece == 'p' and abs(to_position[0] - from_position[0]) == 2:
        captured_piece = new_state['board'][to_position[0] * 5 + to_position[1]]
        if captured_piece == 'p':
            new_state['board'][to_position[0] * 5 + to_position[1]] = '.'
            new_state['board'][to_position[0] * 5 + to_position[1] + (1 if to_position[0] < from_position[0] else -1)] = '.'

    # Update the turn
    new_state['turn'] = (new_state['turn'] + 1) % 2

    # Check for checkmate
    if is_in_check(new_state, 0) and not is_legal_move(new_state, 0, (0, 0)):
        new_state['winner'] = 1
    elif is_in_check(new_state, 1) and not is_legal_move(new_state, 1, (4, 4)):
        new_state['winner'] = 0

    return new_state

def is_in_check(state: State, player_id: int) -> bool:
    """
    Checks if the given player is in check.
    """
    king_position = next((pos for pos, piece in state['board'].items() if piece == f'K{player_id}'), None)
    if not king_position:
        return False
    enemy_pieces = [piece for piece, pos in state['board'].items() if piece.startswith(f'{chr(ord("A") + (ord(pos[0]) - ord("a")) + 1)}') and piece != f'K{player_id}']
    for piece in enemy_pieces:
        if is_legal_move(state, player_id, (king_position[0], king_position[1]), (state['board'][king_position[0] * 5 + king_position[1]].split('_')[1][1:], king_position)):
            return True
    return False

def is_legal_move(state: State, player_id: int, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
    """
    Checks if the given move is legal.
    """
    piece = state['board'][f'{chr(ord("a") + from_pos[1])}{5 - from_pos[0]}']
    if piece == 'P':
        if player_id == 0 and to_pos[0] == 1 and state['board'][f'{chr(ord("a") + to_pos[1])}{5 - to_pos[0]}'] == '.':
            return True
        if player_id == 1 and to_pos[0] == 4 and state['board'][f'{chr(ord("a") + to_pos[1])}{5 - to_pos[0]}'] == '.':
            return True
        if player_id == 0 and to_pos[0] == from_pos[0] + 1 and state['board'][f'{chr(ord("a") + to_pos[1])}{5 - to_pos[0]}'] == '.':
            return True
        if player_id == 1 and to_pos[0] == from_pos[0] - 1 and state['board'][f'{chr(ord("a") + to_pos[1])}{5 - to_pos[0]}'] == '.':
            return True
        if player_id == 0 and to_pos[0] == from_pos[0] + 1 and state['board'][f'{chr(ord("a") + to_pos[1])}{5 - to_pos[0]}'].startswith('P'):
            return True
        if player_id == 1 and to_pos[0] == from_pos[0] - 1 and state['board'][f'{chr(ord("a") + to_pos[1])}{5 - to_pos[0]}'].startswith('P'):
            return True
    elif piece == 'N':
        if abs(to_pos[0] - from_pos[0]) == 2 and abs(to_pos[1] - from_pos[1]) == 1:
            return True
        if abs(to_pos[0] - from_pos[0]) == 1 and abs(to_pos[1] - from_pos[1]) == 2:
            return True
    elif piece == 'B':
        if abs(to_pos[0] - from_pos[0]) == abs(to_pos[1] - from_pos[1]):
            return True
    elif piece == 'R':
        if to_pos[0] == from_pos[0] or to_pos[1] == from_pos[1]:
            return True
    elif piece == 'Q':
        if abs(to_pos[0] - from_pos[0]) == abs(to_pos[1] - from_pos[1]) or to_pos[0] == from_pos[0] or to_pos[1] == from_pos[1]:
            return True
    elif piece == 'K':
        if abs(to_pos[0] - from_pos[0]) <= 1 and abs(to_pos[1] - from_pos[1]) <= 1:
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
    return {0: 'Player 0', 1: 'Player 1'}[player_id]

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['winner'] is None:
        return [0.0, 0.0]
    elif state['winner'] == 0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for piece, pos in state['board'].items():
        if piece != '.':
            for to_pos in [(pos[0] + dx, pos[1] + dy) for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)] if 0 <= pos[0] + dx < 5 and 0 <= pos[1] + dy < 5]:
                if state['board'][f'{chr(ord("a") + to_pos[1])}{5 - to_pos[0]}'] == '.':
                    legal_actions.append(f'{piece}_{pos}_{to_pos}')
                elif state['board'][f'{chr(ord("a") + to_pos[1])}{5 - to_pos[0]}'].startswith(piece):
                    legal_actions.append(f'{piece}_{pos}_{to_pos}')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {}
    player_1_obs = {}
    for pos, piece in state['board'].items():
        if piece != '.':
            player_0_obs[pos] = piece
            player_1_obs[pos] = piece
    return [player_0_obs, player_1_obs]