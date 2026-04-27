import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to create a copy of the state
def copy_state(state):
    return copy.deepcopy(state)

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial board setup
    initial_board = {
        'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
        'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
        'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
        'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
    }
    return {'board': initial_board}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = copy_state(state)
    piece, from_square, to_square = action.split('_')
    from_square = from_square.lower()
    to_square = to_square.lower()

    # Get the current piece at the from_square
    current_piece = new_state['board'].get(from_square)
    
    # Check if the move is valid
    if current_piece is None:
        raise ValueError(f"Invalid move: No piece at {from_square}")
    
    if current_piece == 'p' and (to_square == 'e5' or to_square == 'e1'):
        # Promotion
        new_state['board'][to_square] = 'q'
    elif current_piece == 'p' and to_square == 'e4':
        # En passant
        captured_piece = new_state['board'].pop(to_square + '_e3')
        new_state['board'][to_square] = 'p'
    else:
        new_state['board'][to_square] = current_piece
        new_state['board'].pop(from_square)
    
    # Update the current player
    new_state['current_player'] = 1 - new_state['current_player']
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    return state.get('current_player', -4)

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return ['White', 'Black'][player_id]

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['current_player'] == -4:
        return [0.0, 0.0]
    else:
        return [0.0, 1.0] if state['current_player'] == 0 else [-1.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    current_player = state['current_player']
    board = state['board']

    for square, piece in board.items():
        if piece == '.':
            continue
        
        if piece == 'p' and current_player == 0:
            # Pawn moves and en passant capture
            if square == 'e2':
                legal_actions.append(f"P_{square}_e4")
            else:
                if square == 'e1':
                    legal_actions.append(f"P_{square}_e2")
                else:
                    legal_actions.append(f"P_{square}_e3")
                    legal_actions.append(f"P_{square}_e4")
        
        if piece != '.':
            # Regular piece moves
            if piece == 'r':
                for i in range(1, 5):
                    if board.get(square + f"{i}") == '.':
                        legal_actions.append(f"{piece}_{square}_{square + f'{i}'}")
                    else:
                        break
                for i in range(1, 5):
                    if board.get(square + f"-{i}") == '.':
                        legal_actions.append(f"{piece}_{square}_{square + f'-{i}'}")
                    else:
                        break
            elif piece == 'n':
                for move in [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]:
                    next_square = tuple(map(sum, zip(square, move)))
                    if board.get(next_square) == '.':
                        legal_actions.append(f"{piece}_{square}_{next_square}")
                    else:
                        break
            elif piece == 'b':
                for i in range(1, 5):
                    if board.get(square + f"{i}") == '.':
                        legal_actions.append(f"{piece}_{square}_{square + f'{i}'}")
                    else:
                        break
                for i in range(1, 5):
                    if board.get(square + f"-{i}") == '.':
                        legal_actions.append(f"{piece}_{square}_{square + f'-{i}'}")
                    else:
                        break
            elif piece == 'q':
                for i in range(1, 5):
                    if board.get(square + f"{i}") == '.':
                        legal_actions.append(f"{piece}_{square}_{square + f'{i}'}")
                    else:
                        break
                for i in range(1, 5):
                    if board.get(square + f"-{i}") == '.':
                        legal_actions.append(f"{piece}_{square}_{square + f'-{i}'}")
                    else:
                        break
            elif piece == 'k':
                for move in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    next_square = tuple(map(sum, zip(square, move)))
                    if board.get(next_square) == '.':
                        legal_actions.append(f"{piece}_{square}_{next_square}")
                    else:
                        break
            elif piece == 'p':
                if current_player == 1:
                    # Black's perspective
                    if square == 'e4':
                        legal_actions.append(f"P_{square}_e3")
                    else:
                        legal_actions.append(f"P_{square}_e5")
                else:
                    # White's perspective
                    if square == 'e3':
                        legal_actions.append(f"P_{square}_e4")
                    else:
                        legal_actions.append(f"P_{square}_e2")

    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    board = state['board']
    current_player = state['current_player']

    obs_0 = {}
    obs_1 = {}

    for square, piece in board.items():
        if piece == '.':
            continue
        if current_player == 0:
            obs_0[square] = piece
        else:
            obs_1[square] = piece

    observations.append(obs_0)
    observations.append(obs_1)

    return observations