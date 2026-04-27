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

# Helper function to initialize the state
def _initialize_state():
    # Initial setup based on the rules provided
    state = {
        'board': [
            ['R', 'N', 'B', 'Q', 'K'],
            ['P', 'P', 'P', 'P', 'P'],
            ['.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K']
        ],
        'turn': 0,
        'winner': None,
        'current_player': 0,
        'legal_actions': [],
        'rewards': [0.0, 0.0],
        'observation': {
            'player_0': {'board': copy.deepcopy(state['board']), 'turn': state['turn']},
            'player_1': {'board': copy.deepcopy(state['board']), 'turn': state['turn']}
        }
    }
    return state

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return _initialize_state()

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy.deepcopy(state)
    new_state['board'] = state['board']
    new_state['current_player'] = (state['current_player'] + 1) % 2
    
    # Update the board based on the action
    if action.startswith('P'):
        piece, from_square, to_square = action.split('_')
        new_state['board'][int(from_square[1])][ord(from_square[0]) - ord('a')] = '.'
        new_state['board'][int(to_square[1])][ord(to_square[0]) - ord('a')] = piece
    elif action.startswith('N'):
        piece, from_square, to_square = action.split('_')
        new_state['board'][int(from_square[1])][ord(from_square[0]) - ord('a')] = '.'
        new_state['board'][int(to_square[1])][ord(to_square[0]) - ord('a')] = piece
    elif action.startswith('B'):
        piece, from_square, to_square = action.split('_')
        new_state['board'][int(from_square[1])][ord(from_square[0]) - ord('a')] = '.'
        new_state['board'][int(to_square[1])][ord(to_square[0]) - ord('a')] = piece
    elif action.startswith('R'):
        piece, from_square, to_square = action.split('_')
        new_state['board'][int(from_square[1])][ord(from_square[0]) - ord('a')] = '.'
        new_state['board'][int(to_square[1])][ord(to_square[0]) - ord('a')] = piece
    elif action.startswith('Q'):
        piece, from_square, to_square = action.split('_')
        new_state['board'][int(from_square[1])][ord(from_square[0]) - ord('a')] = '.'
        new_state['board'][int(to_square[1])][ord(to_square[0]) - ord('a')] = piece
    elif action.startswith('K'):
        piece, from_square, to_square = action.split('_')
        new_state['board'][int(from_square[1])][ord(from_square[0]) - ord('a')] = '.'
        new_state['board'][int(to_square[1])][ord(to_square[0]) - ord('a')] = piece
    else:
        raise ValueError("Invalid action format")
    
    # Determine the winner if applicable
    if check_checkmate(new_state):
        new_state['winner'] = new_state['current_player']
        new_state['rewards'] = [1.0, -1.0] if new_state['winner'] == 0 else [-1.0, 1.0]
        new_state['legal_actions'] = []
    
    return new_state

def check_checkmate(state: State) -> bool:
    king_position = None
    for row in state['board']:
        for piece in row:
            if piece == 'K':
                king_position = (row.index(piece), state['board'].index(row))
                break
        if king_position:
            break
    
    if not king_position:
        return False
    
    king_row, king_col = king_position
    
    # Check all possible moves for the opponent
    for opponent in [1, 0]:  # 1 is black, 0 is white
        for piece in ['Q', 'R', 'B', 'N', 'P']:
            for move in get_possible_moves(state, opponent, piece):
                if move == f'{piece}_{king_row}_{king_col}':
                    return False
    return True

def get_possible_moves(state: State, player: int, piece: str) -> list[str]:
    moves = []
    if piece == 'P':
        for i in range(1, 6):
            if player == 0:
                if state['board'][i][state['board'][i].index('.')] == '.':
                    moves.append(f'P_{chr(ord("a") + state["board"][i].index("."))}_{chr(ord("a") + i)}')
                if i < 5 and state['board'][i + 1][state['board'][i + 1].index('.')] == 'P' and state['board'][i + 2][state['board'][i + 2].index('.')] == '.':
                    moves.append(f'P_{chr(ord("a") + state["board"][i].index("."))}_{chr(ord("a") + i + 2)}')
            else:
                if state['board'][i][state['board'][i].index('.')] == '.':
                    moves.append(f'P_{chr(ord("e") - i + 1)}_{chr(ord("e") - i + 1)}')
                if i > 1 and state['board'][i - 1][state['board'][i - 1].index('.')] == 'P' and state['board'][i - 2][state['board'][i - 2].index('.')] == '.':
                    moves.append(f'P_{chr(ord("e") - i + 1)}_{chr(ord("e") - i + 3)}')
    elif piece == 'N':
        for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            if 0 <= king_row + dx < 5 and 0 <= king_col + dy < 5:
                if state['board'][king_row + dx][king_col + dy] == '.':
                    moves.append(f'N_{chr(ord("a") + king_col + dy)}_{chr(ord("a") + king_row + dx)}')
    elif piece == 'B':
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            x, y = king_row, king_col
            while 0 <= x + dx < 5 and 0 <= y + dy < 5:
                if state['board'][x + dx][y + dy] == '.':
                    moves.append(f'B_{chr(ord("a") + y + dy)}_{chr(ord("a") + x + dx)}')
                elif state['board'][x + dx][y + dy] != '.':
                    moves.append(f'B_{chr(ord("a") + y + dy)}_{chr(ord("a") + x + dx)}')
                    break
                x += dx
                y += dy
    elif piece == 'R':
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x, y = king_row, king_col
            while 0 <= x + dx < 5 and 0 <= y + dy < 5:
                if state['board'][x + dx][y + dy] == '.':
                    moves.append(f'R_{chr(ord("a") + y + dy)}_{chr(ord("a") + x + dx)}')
                elif state['board'][x + dx][y + dy] != '.':
                    moves.append(f'R_{chr(ord("a") + y + dy)}_{chr(ord("a") + x + dx)}')
                    break
                x += dx
                y += dy
    elif piece == 'Q':
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            x, y = king_row, king_col
            while 0 <= x + dx < 5 and 0 <= y + dy < 5:
                if state['board'][x + dx][y + dy] == '.':
                    moves.append(f'Q_{chr(ord("a") + y + dy)}_{chr(ord("a") + x + dx)}')
                elif state['board'][x + dx][y + dy] != '.':
                    moves.append(f'Q_{chr(ord("a") + y + dy)}_{chr(ord("a") + x + dx)}')
                    break
                x += dx
                y += dy
    elif piece == 'K':
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            if 0 <= king_row + dx < 5 and 0 <= king_col + dy < 5:
                if state['board'][king_row + dx][king_col + dy] == '.':
                    moves.append(f'K_{chr(ord("a") + king_col + dy)}_{chr(ord("a") + king_row + dx)}')
    return moves

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return {0: 'Player 0', 1: 'Player 1'}[player_id]

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return state['rewards']

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    return state['legal_actions']

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state['observation']['player_0'], state['observation']['player_1']]