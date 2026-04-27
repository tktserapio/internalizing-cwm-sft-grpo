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

# Helper functions
def convert_to_algebraic(square: tuple[int, int]) -> str:
    """Converts a (rank, file) tuple to algebraic notation."""
    return f"{chr(ord('a') + square[1])}{5 - square[0]}"

def convert_to_tuple(algebraic: str) -> tuple[int, int]:
    """Converts algebraic notation to a (rank, file) tuple."""
    return (5 - ord(algebraic[1]), ord(algebraic[0]) - ord('a'))

def is_valid_move(state: State, action: Action) -> bool:
    """Checks if the given action is valid in the current state."""
    # Implement validation logic here
    pass

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    initial_board = {
        'r': (1, 4), 'n': (2, 4), 'b': (3, 4), 'q': (4, 4), 'k': (5, 4),
        'p': [(1, i) for i in range(5)], 
        'R': (1, 1), 'N': (2, 1), 'B': (3, 1), 'Q': (4, 1), 'K': (5, 1)
    }
    return {
        'board': initial_board,
        'turn': 0,
        'castling_rights': {'wK': True, 'wQ': True, 'bK': False, 'bQ': False},
        'en_passant_target': None,
        'halfmove_clock': 0,
        'fullmove_number': 1,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = copy.deepcopy(state)
    piece, from_square, to_square = action.split('_')
    from_square = convert_to_tuple(from_square)
    to_square = convert_to_tuple(to_square)
    
    # Handle pawn movement
    if piece == 'p':
        if state['board'][piece][0] == 1:  # White pawn
            if to_square[0] == from_square[0] - 1 and to_square[1] == from_square[1]:
                new_state['board'][piece].remove(from_square)
                new_state['board'][piece].append(to_square)
                new_state['halfmove_clock'] += 1
                if to_square[0] == 0:
                    new_state['board'][piece].append((0, to_square[1]))
                    new_state['halfmove_clock'] += 1
            elif to_square[0] == from_square[0] - 1 and to_square[1] == from_square[1] + 1:
                new_state['board'][piece].remove(from_square)
                new_state['board'][piece].append(to_square)
                new_state['halfmove_clock'] += 1
                if to_square[0] == 0:
                    new_state['board'][piece].append((0, to_square[1]))
                    new_state['halfmove_clock'] += 1
        else:  # Black pawn
            if to_square[0] == from_square[0] + 1 and to_square[1] == from_square[1]:
                new_state['board'][piece].remove(from_square)
                new_state['board'][piece].append(to_square)
                new_state['halfmove_clock'] += 1
                if to_square[0] == 4:
                    new_state['board'][piece].append((4, to_square[1]))
                    new_state['halfmove_clock'] += 1
            elif to_square[0] == from_square[0] + 1 and to_square[1] == from_square[1] + 1:
                new_state['board'][piece].remove(from_square)
                new_state['board'][piece].append(to_square)
                new_state['halfmove_clock'] += 1
                if to_square[0] == 4:
                    new_state['board'][piece].append((4, to_square[1]))
                    new_state['halfmove_clock'] += 1
    
    # Handle piece movement
    else:
        if piece == 'R':
            new_state['board'][piece].remove(from_square)
            new_state['board'][piece].append(to_square)
        elif piece == 'N':
            if abs(to_square[0] - from_square[0]) == 1 and abs(to_square[1] - from_square[1]) == 2 or \
               abs(to_square[0] - from_square[0]) == 2 and abs(to_square[1] - from_square[1]) == 1:
                new_state['board'][piece].remove(from_square)
                new_state['board'][piece].append(to_square)
        elif piece == 'B':
            if abs(to_square[0] - from_square[0]) == abs(to_square[1] - from_square[1]):
                new_state['board'][piece].remove(from_square)
                new_state['board'][piece].append(to_square)
        elif piece == 'Q':
            if abs(to_square[0] - from_square[0]) == abs(to_square[1] - from_square[1]) or \
               to_square[0] == from_square[0] or to_square[1] == from_square[1]:
                new_state['board'][piece].remove(from_square)
                new_state['board'][piece].append(to_square)
        elif piece == 'K':
            if abs(to_square[0] - from_square[0]) <= 1 and abs(to_square[1] - from_square[1]) <= 1:
                new_state['board'][piece].remove(from_square)
                new_state['board'][piece].append(to_square)
        elif piece == 'p':
            if to_square[0] == 0 and piece == 'P' and from_square[0] == 1:
                new_state['board']['Q'].append(to_square)
            elif to_square[0] == 4 and piece == 'P' and from_square[0] == 3:
                new_state['board']['Q'].append(to_square)
    
    # Update castling rights
    if piece == 'K':
        if from_square[0] == 5 and to_square[0] == 7 and state['board']['R'][0] == (5, 1):
            state['castling_rights']['wK'] = False
        elif from_square[0] == 5 and to_square[0] == 3 and state['board']['R'][0] == (5, 1):
            state['castling_rights']['wQ'] = False
        elif from_square[0] == 1 and to_square[0] == 3 and state['board']['R'][0] == (1, 1):
            state['castling_rights']['bK'] = False
        elif from_square[0] == 1 and to_square[0] == 7 and state['board']['R'][0] == (1, 1):
            state['castling_rights']['bQ'] = False
    
    # Update en passant target
    if piece == 'p' and (to_square[0] == 4 or to_square[0] == 0):
        new_state['en_passant_target'] = to_square
    
    # Update halfmove clock
    if piece != 'p':
        new_state['halfmove_clock'] += 1
    
    # Check for stalemate
    if len(new_state['board']['p']) == 0 and len(new_state['board']['P']) == 0:
        new_state['winner'] = 0 if new_state['turn'] == 0 else 1
        return new_state
    
    # Check for checkmate
    if is_in_check(new_state, new_state['turn']):
        new_state['winner'] = 0 if new_state['turn'] == 0 else 1
        return new_state
    
    # Check for draw conditions
    if is_draw(new_state):
        new_state['winner'] = 0 if new_state['turn'] == 0 else 1
        return new_state
    
    return new_state

def is_in_check(state: State, player: int) -> bool:
    """Checks if the given player is in check."""
    # Implement check logic here
    pass

def is_draw(state: State) -> bool:
    """Checks if the game is in a draw condition."""
    # Implement draw logic here
    pass

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['turn']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return ['Player 0', 'Player 1'][player_id]

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return [state['winner']] * 2

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    # Implement legal action generation logic here
    pass

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    # Implement observation logic here
    pass