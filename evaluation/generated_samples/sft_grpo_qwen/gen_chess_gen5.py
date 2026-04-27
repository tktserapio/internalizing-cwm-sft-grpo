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
    new_state = state.copy()
    piece, from_square, to_square = action.split('_')
    from_row, from_col = ord(from_square[0]) - ord('a'), int(from_square[1]) - 1
    to_row, to_col = ord(to_square[0]) - ord('a'), int(to_square[1]) - 1
    
    # Update the board
    new_state['board'][from_row][from_col] = '.'
    new_state['board'][to_row][to_col] = piece
    
    # Handle special cases like castling, en passant, etc.
    if piece == 'P' and abs(to_row - from_row) == 2:
        # En passant
        captured_piece = new_state['board'][to_row + (1 - to_row % 2)][to_col]
        new_state['board'][to_row + (1 - to_row % 2)][to_col] = '.'
        new_state['board'][to_row + (1 - to_row % 2) + 1][to_col] = captured_piece
    elif piece == 'P' and to_row == 0 or to_row == 4:
        # Promotion
        promoted_piece = action.split('_')[-1]
        new_state['board'][to_row][to_col] = promoted_piece
    
    # Update turn
    new_state['turn'] = (new_state['turn'] + 1) % 2
    
    # Determine winner
    if new_state['board'][2][2] == 'k' and new_state['board'][2][3] == 'q':
        new_state['winner'] = 1
    elif new_state['board'][3][2] == 'K' and new_state['board'][3][3] == 'K':
        new_state['winner'] = 0
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state['turn']

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return {0: 'White', 1: 'Black'}[player_id]

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['winner'] is not None:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    
    # Get current player
    player = get_current_player(state)
    
    # Iterate over all pieces
    for row in range(5):
        for col in range(5):
            piece = state['board'][row][col]
            
            # Pawn movement
            if piece == 'P':
                if state['board'][row][col + 1] == '.':
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}")
                if row == 1 and state['board'][row + 1][col + 1] == '.':
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}_Q")
                if row == 4 and state['board'][row - 1][col + 1] == '.':
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}_Q")
                if state['board'][row + 1][col] == 'P' and state['board'][row + 1][col].islower():
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}_Q")
                if state['board'][row - 1][col] == 'P' and state['board'][row - 1][col].isupper():
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 1)}_Q")
                
                if state['board'][row][col + 2] == '.':
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 2)}")
                if row == 1 and state['board'][row + 2][col + 2] == '.':
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 2)}_Q")
                if row == 4 and state['board'][row - 2][col + 2] == '.':
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 2)}_Q")
                if state['board'][row + 2][col + 2] == 'P' and state['board'][row + 2][col + 2].islower():
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 2)}_Q")
                if state['board'][row - 2][col + 2] == 'P' and state['board'][row - 2][col + 2].isupper():
                    legal_actions.append(f"P_{chr(ord('a') + col)}_{chr(ord('a') + col + 2)}_Q")
            
            # Knight movement
            if piece == 'N':
                for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
                    nx, ny = col + dx, row + dy
                    if 0 <= nx < 5 and 0 <= ny < 5 and state['board'][ny][nx] != '.':
                        legal_actions.append(f"N_{chr(ord('a') + col)}_{chr(ord('a') + nx)}")
            
            # Rook movement
            if piece == 'R':
                for dx in range(-4, 5):
                    for dy in range(-4, 5):
                        if abs(dx) + abs(dy) > 1:
                            continue
                        nx, ny = col + dx, row + dy
                        while 0 <= nx < 5 and 0 <= ny < 5 and state['board'][ny][nx] == '.':
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + nx)}")
                            nx += dx
                            ny += dy
                        if 0 <= nx < 5 and 0 <= ny < 5 and state['board'][ny][nx] != '.':
                            legal_actions.append(f"R_{chr(ord('a') + col)}_{chr(ord('a') + nx)}")
            
            # Bishop movement
            if piece == 'B':
                for dx in range(-4, 5):
                    for dy in range(-4, 5):
                        if abs(dx) + abs(dy) > 1:
                            continue
                        nx, ny = col + dx, row + dy
                        while 0 <= nx < 5 and 0 <= ny < 5 and state['board'][ny][nx] == '.':
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + nx)}")
                            nx += dx
                            ny += dy
                        if 0 <= nx < 5 and 0 <= ny < 5 and state['board'][ny][nx] != '.':
                            legal_actions.append(f"B_{chr(ord('a') + col)}_{chr(ord('a') + nx)}")
            
            # Queen movement
            if piece == 'Q':
                for dx in range(-4, 5):
                    for dy in range(-4, 5):
                        if abs(dx) + abs(dy) > 1:
                            continue
                        nx, ny = col + dx, row + dy
                        while 0 <= nx < 5 and 0 <= ny < 5 and state['board'][ny][nx] == '.':
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + nx)}")
                            nx += dx
                            ny += dy
                        if 0 <= nx < 5 and 0 <= ny < 5 and state['board'][ny][nx] != '.':
                            legal_actions.append(f"Q_{chr(ord('a') + col)}_{chr(ord('a') + nx)}")
            
            # King movement
            if piece == 'K':
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if abs(dx) + abs(dy) > 0:
                            continue
                        nx, ny = col + dx, row + dy
                        if 0 <= nx < 5 and 0 <= ny < 5 and state['board'][ny][nx] == '.':
                            legal_actions.append(f"K_{chr(ord('a') + col)}_{chr(ord('a') + nx)}")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {
        'board': state['board'],
        'turn': get_current_player(state),
        'winner': state['winner']
    }
    player_1_obs = {
        'board': state['board'],
        'turn': get_current_player(state),
        'winner': state['winner']
    }
    return [player_0_obs, player_1_obs]