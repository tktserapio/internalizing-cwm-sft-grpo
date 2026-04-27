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
    # Initial board setup
    initial_board = {
        'r': {'a1': None, 'b1': None, 'c1': None, 'd1': None, 'e1': None},
        'n': {'a2': None, 'b2': None, 'c2': None, 'd2': None, 'e2': None},
        'b': {'a3': None, 'b3': None, 'c3': None, 'd3': None, 'e3': None},
        'q': {'a4': None, 'b4': None, 'c4': None, 'd4': None, 'e4': None},
        'k': {'a5': None, 'b5': None, 'c5': None, 'd5': None, 'e5': None},
        'p': {'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P'},
        'r': {'a5': 'R', 'b5': 'R', 'c5': 'R', 'd5': 'R', 'e5': 'R'}
    }
    return initial_board

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    def move_piece(piece: str, from_square: str, to_square: str, state: State) -> State:
        if piece == 'P':
            if to_square == 'e5' and state[piece][from_square] == 'P':
                state[piece][to_square] = 'Q'
            elif to_square == 'e4' and state[piece][from_square] == 'P':
                state[piece][to_square] = 'Q'
            else:
                state[piece][to_square] = state[piece][from_square]
                state[piece][from_square] = None
        elif piece == 'N':
            if abs(ord(to_square[0]) - ord(from_square[0])) == 2 and abs(int(to_square[1]) - int(from_square[1])) == 1:
                state[piece][to_square] = state[piece][from_square]
                state[piece][from_square] = None
            else:
                raise ValueError("Invalid knight move")
        elif piece == 'B':
            x1, y1 = ord(from_square[0]) - ord('a'), int(from_square[1]) - 1
            x2, y2 = ord(to_square[0]) - ord('a'), int(to_square[1]) - 1
            if x1 == x2 or y1 == y2:
                state[piece][to_square] = state[piece][from_square]
                state[piece][from_square] = None
            else:
                raise ValueError("Invalid bishop move")
        elif piece == 'R':
            if from_square[0] == to_square[0] or from_square[1] == to_square[1]:
                state[piece][to_square] = state[piece][from_square]
                state[piece][from_square] = None
            else:
                raise ValueError("Invalid rook move")
        elif piece == 'Q':
            if from_square[0] == to_square[0] or from_square[1] == to_square[1]:
                state[piece][to_square] = state[piece][from_square]
                state[piece][from_square] = None
            else:
                raise ValueError("Invalid queen move")
        elif piece == 'K':
            if abs(ord(to_square[0]) - ord(from_square[0])) <= 1 and abs(int(to_square[1]) - int(from_square[1])) <= 1:
                state[piece][to_square] = state[piece][from_square]
                state[piece][from_square] = None
            else:
                raise ValueError("Invalid king move")
        elif piece == 'p':
            if to_square == 'e1' and state[piece][from_square] == 'P':
                state[piece][to_square] = 'P'
            elif to_square == 'e2' and state[piece][from_square] == 'P':
                state[piece][to_square] = 'P'
            else:
                state[piece][to_square] = state[piece][from_square]
                state[piece][from_square] = None
        else:
            raise ValueError("Unknown piece type")
    
    def promote_pawn(pawn: str, to_square: str, promo: str, state: State) -> State:
        state[pawn][to_square] = promo
        return state
    
    def castle_rook(rook: str, from_square: str, to_square: str, state: State) -> State:
        if rook == 'R':
            if from_square == 'a1' and to_square == 'c1':
                state['r']['a1'] = None
                state['r']['c1'] = 'R'
            elif from_square == 'e1' and to_square == 'c1':
                state['r']['e1'] = None
                state['r']['c1'] = 'R'
            else:
                raise ValueError("Invalid castling move")
        elif rook == 'r':
            if from_square == 'a5' and to_square == 'c5':
                state['r']['a5'] = None
                state['r']['c5'] = 'R'
            elif from_square == 'e5' and to_square == 'c5':
                state['r']['e5'] = None
                state['r']['c5'] = 'R'
            else:
                raise ValueError("Invalid castling move")
        else:
            raise ValueError("Unknown rook type")
        
        return state
    
    def handle_promotion(action: Action, state: State) -> State:
        piece, from_square, to_square, promo = action.split('_')
        if promo != '':
            return promote_pawn(piece, to_square, promo, state)
        else:
            return move_piece(piece, from_square, to_square, state)
    
    def handle_castle(action: Action, state: State) -> State:
        piece, from_square, to_square = action.split('_')
        if piece == 'R':
            return castle_rook(piece, from_square, to_square, state)
        elif piece == 'r':
            return castle_rook(piece, from_square, to_square, state)
        else:
            raise ValueError("Unknown rook type")
    
    def handle_move(action: Action, state: State) -> State:
        piece, from_square, to_square = action.split('_')
        return move_piece(piece, from_square, to_square, state)
    
    def handle_castle_or_promotion(action: Action, state: State) -> State:
        if action.startswith('P'):
            return handle_promotion(action, state)
        elif action.startswith('R') or action.startswith('r'):
            return handle_castle(action, state)
        else:
            return handle_move(action, state)
    
    # Parse the action
    try:
        parsed_action = action.split('_')
        if len(parsed_action) == 3:
            return handle_move(action, state)
        elif len(parsed_action) == 4:
            return handle_promotion(action, state)
        elif len(parsed_action) == 5:
            return handle_castle_or_promotion(action, state)
        else:
            raise ValueError("Invalid action format")
    except Exception as e:
        print(f"Error applying action: {e}")
        return state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    white_pieces = sum(1 for piece in state.values() if piece == 'R' or piece == 'N' or piece == 'B' or piece == 'Q' or piece == 'K' or piece == 'P')
    black_pieces = sum(1 for piece in state.values() if piece == 'r' or piece == 'n' or piece == 'b' or piece == 'q' or piece == 'k' or piece == 'p')
    if white_pieces > black_pieces:
        return 0
    elif black_pieces > white_pieces:
        return 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    if player_id == 0:
        return "White"
    elif player_id == 1:
        return "Black"
    else:
        return "Unknown"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    white_pieces = sum(1 for piece in state.values() if piece == 'R' or piece == 'N' or piece == 'B' or piece == 'Q' or piece == 'K' or piece == 'P')
    black_pieces = sum(1 for piece in state.values() if piece == 'r' or piece == 'n' or piece == 'b' or piece == 'q' or piece == 'k' or piece == 'p')
    if white_pieces > black_pieces:
        return [1.0, 0.0]
    elif black_pieces > white_pieces:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for piece, positions in state.items():
        if positions:
            for from_square, _ in positions.items():
                for to_square in positions[from_square].keys():
                    if piece == 'P' and to_square == 'e5' and positions[from_square] == 'P':
                        legal_actions.append(f"P_{from_square}_{to_square}_Q")
                    elif piece == 'P' and to_square == 'e4' and positions[from_square] == 'P':
                        legal_actions.append(f"P_{from_square}_{to_square}_Q")
                    elif piece == 'P':
                        legal_actions.append(f"P_{from_square}_{to_square}")
                    elif piece == 'N':
                        if abs(ord(to_square[0]) - ord(from_square[0])) == 2 and abs(int(to_square[1]) - int(from_square[1])) == 1:
                            legal_actions.append(f"N_{from_square}_{to_square}")
                    elif piece == 'B':
                        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                            next_x, next_y = ord(from_square[0]) + dx, int(from_square[1]) + dy
                            if 65 <= next_x <= 90 and 1 <= next_y <= 5:
                                if positions.get(f"{chr(next_x)}{next_y}") is None:
                                    legal_actions.append(f"B_{from_square}_{chr(next_x)}{next_y}")
                    elif piece == 'R':
                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            next_x, next_y = ord(from_square[0]) + dx, int(from_square[1]) + dy
                            if 65 <= next_x <= 90 and 1 <= next_y <= 5:
                                if positions.get(f"{chr(next_x)}{next_y}") is None:
                                    legal_actions.append(f"R_{from_square}_{chr(next_x)}{next_y}")
                    elif piece == 'Q':
                        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                            next_x, next_y = ord(from_square[0]) + dx, int(from_square[1]) + dy
                            if 65 <= next_x <= 90 and 1 <= next_y <= 5:
                                if positions.get(f"{chr(next_x)}{next_y}") is None:
                                    legal_actions.append(f"Q_{from_square}_{chr(next_x)}{next_y}")
                    elif piece == 'K':
                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                            next_x, next_y = ord(from_square[0]) + dx, int(from_square[1]) + dy
                            if 65 <= next_x <= 90 and 1 <= next_y <= 5:
                                if positions.get(f"{chr(next_x)}{next_y}") is None:
                                    legal_actions.append(f"K_{from_square}_{chr(next_x)}{next_y}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    player_0_obs = {}
    player_1_obs = {}
    for piece, positions in state.items():
        if positions:
            for from_square, to_square in positions.items():
                if to_square:
                    if piece == 'P':
                        if to_square == 'e5':
                            player_0_obs[f"P_{from_square}_e5"] = True
                        elif to_square == 'e4':
                            player_0_obs[f"P_{from_square}_e4"] = True
                    elif piece == 'N':
                        player_0_obs[f"N_{from_square}_{to_square}"] = True
                    elif piece == 'B':
                        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                            next_x, next_y = ord(from_square[0]) + dx, int(from_square[1]) + dy
                            if 65 <= next_x <= 90 and 1 <= next_y <= 5:
                                player_0_obs[f"B_{from_square}_{chr(next_x)}{next_y}"] = True
                    elif piece == 'R':
                        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                            next_x, next_y = ord(from_square[0]) + dx, int(from_square[1]) + dy
                            if 65 <= next_x <= 90 and 1 <= next_y <= 5:
                                player_0_obs[f"R_{from_square}_{chr(next_x)}{next_y}"] = True
                    elif piece == 'Q':
                        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                            next_x, next_y = ord(from_square[0]) + dx, int(from_square[1]) + dy
                            if 65 <= next_x <= 90 and 1 <= next_y <= 5:
                                player_0_obs[f"Q_{from_square}_{chr(next_x)}{next_y}"] = True
                    elif piece == 'K':
                        player_0_obs[f"K_{from_square}_{to_square}"] = True
    return [player_0_obs, player_0_obs]