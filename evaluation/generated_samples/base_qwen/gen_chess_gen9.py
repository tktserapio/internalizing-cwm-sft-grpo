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

# Helper function to create a new state based on the given action
def apply_action_helper(state: State, action: Action) -> State:
    # Extract the piece, from square, to square from the action string
    piece, from_square, to_square = action.split('_')
    from_square = tuple(map(int, from_square))
    to_square = tuple(map(int, to_square))

    # Create a deep copy of the current state to avoid mutating the original state
    new_state = copy.deepcopy(state)

    # Apply the action to the new state
    if piece == 'P':
        # Pawn movement
        if from_square[0] == 4 and to_square[0] == 3:
            # Promotion
            new_state['board'][to_square] = 'Q' if 'Q' not in new_state['board'][to_square] else 'R' if 'R' not in new_state['board'][to_square] else 'B' if 'B' not in new_state['board'][to_square] else 'N'
        else:
            new_state['board'][to_square] = new_state['board'][from_square]
            new_state['board'][from_square] = '.'
    elif piece == 'N':
        # Knight movement
        if abs(from_square[0] - to_square[0]) + abs(from_square[1] - to_square[1]) != 3:
            raise ValueError("Invalid knight move")
        new_state['board'][to_square] = new_state['board'][from_square]
        new_state['board'][from_square] = '.'
    elif piece == 'B':
        # Bishop movement
        if abs(from_square[0] - to_square[0]) != abs(from_square[1] - to_square[1]):
            raise ValueError("Invalid bishop move")
        new_state['board'][to_square] = new_state['board'][from_square]
        new_state['board'][from_square] = '.'
    elif piece == 'R':
        # Rook movement
        if abs(from_square[0] - to_square[0]) != abs(from_square[1] - to_square[1]):
            raise ValueError("Invalid rook move")
        new_state['board'][to_square] = new_state['board'][from_square]
        new_state['board'][from_square] = '.'
    elif piece == 'Q':
        # Queen movement
        if abs(from_square[0] - to_square[0]) != abs(from_square[1] - to_square[1]) and abs(from_square[0] - to_square[0]) + abs(from_square[1] - to_square[1]) != 3:
            raise ValueError("Invalid queen move")
        new_state['board'][to_square] = new_state['board'][from_square]
        new_state['board'][from_square] = '.'
    elif piece == 'K':
        # King movement
        if abs(from_square[0] - to_square[0]) + abs(from_square[1] - to_square[1]) != 1:
            raise ValueError("Invalid king move")
        new_state['board'][to_square] = new_state['board'][from_square]
        new_state['board'][from_square] = '.'
    
    # Update the current player
    new_state['current_player'] = 1 - new_state['current_player']

    return new_state

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    board = {
        'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
        'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
        'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
        'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
    }
    current_player = 0
    return {'board': board, 'current_player': current_player}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    return apply_action_helper(state, action)

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return {0: 'White', 1: 'Black'}[player_id]

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    winner = state['winner']
    if winner == -4:
        return [0.0, 0.0]
    elif winner == 0:
        return [1.0, -1.0]
    elif winner == 1:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    current_player = state['current_player']
    board = state['board']
    current_player_pieces = [piece for piece, square in board.items() if square == f'{current_player}K' or square.startswith(f'{current_player}')]

    for piece in current_player_pieces:
        for from_square in board.keys():
            if board[from_square] == piece:
                for to_square in board.keys():
                    if board[to_square] == '.':
                        if piece == 'P':
                            if to_square[0] == 'e' and (to_square[1] == '3' or to_square[1] == '4'):
                                legal_actions.append(f"{piece}_{from_square}_{to_square}_Q")  # Promotion
                            elif abs(ord(to_square[0]) - ord(from_square[0])) == 1 and abs(int(to_square[1]) - int(from_square[1])) == 1:
                                legal_actions.append(f"{piece}_{from_square}_{to_square}")
                        elif piece == 'N':
                            if abs(ord(to_square[0]) - ord(from_square[0])) + abs(int(to_square[1]) - int(from_square[1])) == 3:
                                legal_actions.append(f"{piece}_{from_square}_{to_square}")
                        elif piece == 'B':
                            if abs(ord(to_square[0]) - ord(from_square[0])) == abs(int(to_square[1]) - int(from_square[1])):
                                legal_actions.append(f"{piece}_{from_square}_{to_square}")
                        elif piece == 'R':
                            if abs(ord(to_square[0]) - ord(from_square[0])) == abs(int(to_square[1]) - int(from_square[1])):
                                legal_actions.append(f"{piece}_{from_square}_{to_square}")
                        elif piece == 'Q':
                            if abs(ord(to_square[0]) - ord(from_square[0])) == abs(int(to_square[1]) - int(from_square[1])) or abs(ord(to_square[0]) - ord(from_square[0])) + abs(int(to_square[1]) - int(from_square[1])) == 3:
                                legal_actions.append(f"{piece}_{from_square}_{to_square}")
                        elif piece == 'K':
                            if abs(ord(to_square[0]) - ord(from_square[0])) + abs(int(to_square[1]) - int(from_square[1])) == 1:
                                legal_actions.append(f"{piece}_{from_square}_{to_square}")
                        if piece == 'P' and to_square[0] == 'e' and (to_square[1] == '3' or to_square[1] == '4'):
                            legal_actions.append(f"{piece}_{from_square}_{to_square}_Q")

    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    board = state['board']
    observations = [
        {
            'board': board,
            'current_player': state['current_player'],
            'winner': state['winner']
        },
        {
            'board': board,
            'current_player': 1 - state['current_player'],
            'winner': state['winner']
        }
    ]
    return observations