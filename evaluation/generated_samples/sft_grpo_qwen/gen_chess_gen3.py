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
    # Initialize the board state
    board = {
        'r': {'a1': None, 'b1': None, 'c1': None, 'd1': None, 'e1': None},
        'n': {'a2': None, 'b2': None, 'c2': None, 'd2': None, 'e2': None},
        'b': {'a3': None, 'b3': None, 'c3': None, 'd3': None, 'e3': None},
        'q': {'a4': None, 'b4': None, 'c4': None, 'd4': None, 'e4': None},
        'k': {'a5': None, 'b5': None, 'c5': None, 'd5': None, 'e5': None},
        'p': {
            'a2': {'color': 'w', 'rank': 2, 'file': 'a'},
            'b2': {'color': 'w', 'rank': 2, 'file': 'b'},
            'c2': {'color': 'w', 'rank': 2, 'file': 'c'},
            'd2': {'color': 'w', 'rank': 2, 'file': 'd'},
            'e2': {'color': 'w', 'rank': 2, 'file': 'e'}
        }
    }
    return {
        'board': board,
        'turn': 0,
        'winner': -4
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    piece, from_square, to_square = action.split('_')
    from_square = f"{from_square[0]}{from_square[1]}"
    to_square = f"{to_square[0]}{to_square[1]}"
    
    # Get the piece and its color
    piece_color = state['board'][piece][from_square]['color']
    piece_type = piece
    
    # Determine the piece movement logic based on the piece type
    if piece == 'p':
        # Pawn movement
        if piece_color == 'w' and int(to_square[1]) == 1:
            # Promotion
            new_state = promote_pawn(new_state, from_square, to_square, piece_type)
        elif piece_color == 'w' and int(to_square[1]) == 2:
            # Move forward one square
            new_state = move_pawn(new_state, from_square, to_square)
        elif piece_color == 'b' and int(to_square[1]) == 5:
            # Promotion
            new_state = promote_pawn(new_state, from_square, to_square, piece_type)
        elif piece_color == 'b' and int(to_square[1]) == 4:
            # Move forward one square
            new_state = move_pawn(new_state, from_square, to_square)
        else:
            # Regular move
            new_state = move_pawn(new_state, from_square, to_square)
    elif piece == 'n':
        # Knight movement
        new_state = move_knight(new_state, from_square, to_square)
    elif piece == 'b':
        # Bishop movement
        new_state = move_bishop(new_state, from_square, to_square)
    elif piece == 'r':
        # Rook movement
        new_state = move_rook(new_state, from_square, to_square)
    elif piece == 'q':
        # Queen movement
        new_state = move_queen(new_state, from_square, to_square)
    elif piece == 'k':
        # King movement
        new_state = move_king(new_state, from_square, to_square)
    
    # Update the turn
    new_state['turn'] = (new_state['turn'] + 1) % 2
    new_state['winner'] = get_winner(new_state)
    return new_state

def move_pawn(state: State, from_square: str, to_square: str) -> State:
    """
    Moves a pawn from `from_square` to `to_square`.
    """
    piece_color = state['board']['p'][from_square]['color']
    new_state = state.copy()
    new_state['board']['p'][from_square] = None
    new_state['board']['p'][to_square] = {'color': piece_color, 'rank': int(to_square[1]), 'file': to_square[0]}
    return new_state

def promote_pawn(state: State, from_square: str, to_square: str, piece_type: str) -> State:
    """
    Promotes a pawn to a new piece type.
    """
    piece_color = state['board']['p'][from_square]['color']
    new_state = state.copy()
    new_state['board']['p'][to_square] = {'color': piece_color, 'rank': int(to_square[1]), 'file': to_square[0], 'type': piece_type}
    return new_state

def move_knight(state: State, from_square: str, to_square: str) -> State:
    """
    Moves a knight from `from_square` to `to_square`.
    """
    piece_color = state['board']['n'][from_square]['color']
    new_state = state.copy()
    new_state['board']['n'][from_square] = None
    new_state['board']['n'][to_square] = {'color': piece_color, 'rank': int(to_square[1]), 'file': to_square[0]}
    return new_state

def move_bishop(state: State, from_square: str, to_square: str) -> State:
    """
    Moves a bishop from `from_square` to `to_square`.
    """
    piece_color = state['board']['b'][from_square]['color']
    new_state = state.copy()
    new_state['board']['b'][from_square] = None
    new_state['board']['b'][to_square] = {'color': piece_color, 'rank': int(to_square[1]), 'file': to_square[0]}
    return new_state

def move_rook(state: State, from_square: str, to_square: str) -> State:
    """
    Moves a rook from `from_square` to `to_square`.
    """
    piece_color = state['board']['r'][from_square]['color']
    new_state = state.copy()
    new_state['board']['r'][from_square] = None
    new_state['board']['r'][to_square] = {'color': piece_color, 'rank': int(to_square[1]), 'file': to_square[0]}
    return new_state

def move_queen(state: State, from_square: str, to_square: str) -> State:
    """
    Moves a queen from `from_square` to `to_square`.
    """
    piece_color = state['board']['q'][from_square]['color']
    new_state = state.copy()
    new_state['board']['q'][from_square] = None
    new_state['board']['q'][to_square] = {'color': piece_color, 'rank': int(to_square[1]), 'file': to_square[0]}
    return new_state

def move_king(state: State, from_square: str, to_square: str) -> State:
    """
    Moves a king from `from_square` to `to_square`.
    """
    piece_color = state['board']['k'][from_square]['color']
    new_state = state.copy()
    new_state['board']['k'][from_square] = None
    new_state['board']['k'][to_square] = {'color': piece_color, 'rank': int(to_square[1]), 'file': to_square[0]}
    return new_state

def get_winner(state: State) -> int:
    """
    Determines the winner based on the current state.
    """
    # Check for checkmate
    for piece, positions in state['board'].items():
        for position, piece_info in positions.items():
            if piece_info and piece_info['color'] != 'w' ^ state['turn']:
                # Check for checkmate
                if not get_legal_actions(state):
                    return piece_info['color']
    return -4

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for the current state.
    """
    legal_actions = []
    for piece, positions in state['board'].items():
        for position, piece_info in positions.items():
            if piece_info:
                if piece == 'p':
                    legal_actions.extend(get_legal_pawn_actions(state, position))
                elif piece == 'n':
                    legal_actions.extend(get_legal_knight_actions(state, position))
                elif piece == 'b':
                    legal_actions.extend(get_legal_bishop_actions(state, position))
                elif piece == 'r':
                    legal_actions.extend(get_legal_rook_actions(state, position))
                elif piece == 'q':
                    legal_actions.extend(get_legal_queen_actions(state, position))
                elif piece == 'k':
                    legal_actions.extend(get_legal_king_actions(state, position))
    return legal_actions

def get_legal_pawn_actions(state: State, position: str) -> List[Action]:
    """
    Returns legal pawn actions for a given position.
    """
    piece_color = state['board']['p'][position]['color']
    rank = int(position[1])
    file = position[0]
    legal_actions = []
    if piece_color == 'w':
        if rank == 2:
            legal_actions.append(f"P_{position}_e4")
        else:
            legal_actions.append(f"P_{position}_e4")
            legal_actions.append(f"P_{position}_e5")
    else:
        if rank == 5:
            legal_actions.append(f"P_{position}_e4")
        else:
            legal_actions.append(f"P_{position}_e4")
            legal_actions.append(f"P_{position}_e3")
    return legal_actions

def get_legal_knight_actions(state: State, position: str) -> List[Action]:
    """
    Returns legal knight actions for a given position.
    """
    piece_color = state['board']['n'][position]['color']
    rank = int(position[1])
    file = position[0]
    legal_actions = []
    for dx, dy in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
        nx, ny = rank + dx, file + dy
        if 1 <= nx <= 5 and 'a' <= ny <= 'e':
            target_position = f"{ny}{nx}"
            if state['board']['n'][target_position] is None:
                legal_actions.append(f"N_{position}_{target_position}")
            elif state['board']['n'][target_position]['color'] != piece_color:
                legal_actions.append(f"N_{position}_{target_position}")
    return legal_actions

def get_legal_bishop_actions(state: State, position: str) -> List[Action]:
    """
    Returns legal bishop actions for a given position.
    """
    piece_color = state['board']['b'][position]['color']
    rank = int(position[1])
    file = position[0]
    legal_actions = []
    for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        nx, ny = rank + dx, file + dy
        while 1 <= nx <= 5 and 'a' <= ny <= 'e':
            target_position = f"{ny}{nx}"
            if state['board']['b'][target_position] is None:
                legal_actions.append(f"B_{position}_{target_position}")
            elif state['board']['b'][target_position]['color'] != piece_color:
                legal_actions.append(f"B_{position}_{target_position}")
                break
            else:
                break
    return legal_actions

def get_legal_rook_actions(state: State, position: str) -> List[Action]:
    """
    Returns legal rook actions for a given position.
    """
    piece_color = state['board']['r'][position]['color']
    rank = int(position[1])
    file = position[0]
    legal_actions = []
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nx, ny = rank + dx, file + dy
        while 1 <= nx <= 5 and 'a' <= ny <= 'e':
            target_position = f"{ny}{nx}"
            if state['board']['r'][target_position] is None:
                legal_actions.append(f"R_{position}_{target_position}")
            elif state['board']['r'][target_position]['color'] != piece_color:
                legal_actions.append(f"R_{position}_{target_position}")
                break
            else:
                break
    return legal_actions

def get_legal_queen_actions(state: State, position: str) -> List[Action]:
    """
    Returns legal queen actions for a given position.
    """
    piece_color = state['board']['q'][position]['color']
    rank = int(position[1])
    file = position[0]
    legal_actions = []
    for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        nx, ny = rank + dx, file + dy
        while 1 <= nx <= 5 and 'a' <= ny <= 'e':
            target_position = f"{ny}{nx}"
            if state['board']['q'][target_position] is None:
                legal_actions.append(f"Q_{position}_{target_position}")
            elif state['board']['q'][target_position]['color'] != piece_color:
                legal_actions.append(f"Q_{position}_{target_position}")
                break
            else:
                break
    return legal_actions

def get_legal_king_actions(state: State, position: str) -> List[Action]:
    """
    Returns legal king actions for a given position.
    """
    piece_color = state['board']['k'][position]['color']
    rank = int(position[1])
    file = position[0]
    legal_actions = []
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        nx, ny = rank + dx, file + dy
        if 1 <= nx <= 5 and 'a' <= ny <= 'e':
            target_position = f"{ny}{nx}"
            if state['board']['k'][target_position] is None:
                legal_actions.append(f"K_{position}_{target_position}")
    return legal_actions

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    winner = get_winner(state)
    if winner != -4:
        return [1.0, -1.0] if winner == state['turn'] else [-1.0, 1.0]
    return [0.0, 0.0]

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = state['board'].copy()
    player_1_obs = state['board'].copy()
    return [player_0_obs, player_1_obs]