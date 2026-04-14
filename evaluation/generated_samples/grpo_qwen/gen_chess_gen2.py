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
    # Initialize the board
    board = {
        'r': {'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K'},
        'n': {'a2': ' ', 'b2': 'P', 'c2': ' ', 'd2': ' ', 'e2': 'P'},
        'b': {'a3': ' ', 'b3': ' ', 'c3': ' ', 'd3': ' ', 'e3': ' '},
        'q': {'a4': ' ', 'b4': ' ', 'c4': ' ', 'd4': ' ', 'e4': ' '},
        'k': {'a5': 'K', 'b5': ' ', 'c5': ' ', 'd5': ' ', 'e5': ' '},
        'p': {'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P'}
    }
    return {
        'board': board,
        'turn': 0,  # White starts
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
    
    # Get the piece and its current position
    piece_type = new_state['board'][piece][from_square]
    piece_position = new_state['board'][piece_type][from_square]
    
    # Update the board
    new_state['board'][piece_type][from_square] = '.'
    new_state['board'][piece_type][to_square] = piece_position
    
    # Handle pawn promotion
    if piece == 'p' and (to_square[0] == 'a' or to_square[0] == 'e'):
        new_state['board'][piece_type][to_square] += '_Q'  # Promotion to queen
    
    # Handle castling
    # Castling is not implemented in this 5x5 variant
    
    # Handle en passant
    # En passant is not implemented in this 5x5 variant
    
    # Determine the winner
    if piece == 'k' and piece_position == 'K':
        new_state['winner'] = 0 if new_state['turn'] == 0 else 1
    elif piece == 'K' and piece_position == 'k':
        new_state['winner'] = 1 if new_state['turn'] == 0 else 0
    
    # Switch turns
    new_state['turn'] = (new_state['turn'] + 1) % 2
    
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
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    if state['winner'] is not None:
        return [-1.0, 1.0] if state['winner'] == 0 else [1.0, -1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for piece, positions in state['board'].items():
        for from_square, piece_type in positions.items():
            if piece_type != '.':
                # Check pawn movement
                if piece == 'p':
                    if state['turn'] == 0 and from_square[0] == 'a':
                        legal_actions.append(f"P_{from_square}_{from_square[0]+str(int(from_square[1])+1)}")
                    elif state['turn'] == 1 and from_square[0] == 'e':
                        legal_actions.append(f"P_{from_square}_{from_square[0]+str(int(from_square[1])-1)}")
                    else:
                        if from_square[1] != '1':
                            legal_actions.append(f"P_{from_square}_{from_square[0]+str(int(from_square[1])+1)}")
                        if from_square[1] != '5':
                            legal_actions.append(f"P_{from_square}_{from_square[0]+str(int(from_square[1])-1)}")
                # Check other pieces
                else:
                    for to_square, _ in positions.items():
                        if piece_type != '.':
                            legal_actions.append(f"{piece}_{from_square}_{to_square}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    board_representation = []
    for rank in ['1', '2', '4', '5']:
        row = []
        for file in ['a', 'b', 'c', 'd', 'e']:
            square = f"{rank}{file}"
            if square in state['board']['p']:
                row.append('P' if state['turn'] == 0 else 'p')
            elif square in state['board']['n']:
                row.append('N' if state['turn'] == 0 else 'n')
            elif square in state['board']['b']:
                row.append('B' if state['turn'] == 0 else 'b')
            elif square in state['board']['q']:
                row.append('Q' if state['turn'] == 0 else 'q')
            elif square in state['board']['k']:
                row.append('K' if state['turn'] == 0 else 'k')
            else:
                row.append('.')
        board_representation.append(row)
    observations.append({
        'board': board_representation,
        'turn': state['turn'],
        'winner': state['winner']
    })
    observations.append(observations[0].copy())
    return observations