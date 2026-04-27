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
    # Parse the action
    piece, from_square, to_square = action.split('_')
    from_square = from_square.lower()
    to_square = to_square.lower()

    # Create a copy of the state to avoid mutating the original state
    new_state = state.copy()

    # Apply the action
    if piece == 'p':
        # Pawn movement
        if from_square in ['a2', 'b2', 'c2', 'd2', 'e2']:
            new_state[from_square][to_square] = new_state.pop(from_square)
            new_state[to_square]['P'] = None
        else:
            new_state[from_square][to_square] = new_state.pop(from_square)
            new_state[to_square]['P'] = None
            if to_square == 'e4' and from_square in ['e2', 'e4']:
                new_state[to_square]['P'] = 'Q'
    elif piece == 'n':
        # Knight movement
        new_state[from_square][to_square] = new_state.pop(from_square)
    elif piece == 'b':
        # Bishop movement
        new_state[from_square][to_square] = new_state.pop(from_square)
    elif piece == 'r':
        # Rook movement
        new_state[from_square][to_square] = new_state.pop(from_square)
    elif piece == 'q':
        # Queen movement
        new_state[from_square][to_square] = new_state.pop(from_square)
    elif piece == 'k':
        # King movement
        new_state[from_square][to_square] = new_state.pop(from_square)

    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Determine the current player based on whose turn it is
    for rank in state.values():
        for piece in rank.values():
            if piece == 'P':
                return 0 if rank == state['p'] else 1
    return -4

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # Determine the winner based on the state
    white_king = state['k']['a5']
    black_king = state['k']['e5']

    if white_king and not black_king:
        return [1.0, 0.0]
    elif black_king and not white_king:
        return [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    for rank, pieces in state.items():
        for piece, square in pieces.items():
            if square:
                piece_type = piece
                from_square = square
                if piece_type == 'P':
                    # Pawn movement
                    if from_square == 'a2':
                        legal_actions.append(f"P_{from_square}_e4")
                    elif from_square == 'e2':
                        legal_actions.append(f"P_{from_square}_e4")
                    elif from_square == 'a4':
                        legal_actions.append(f"P_{from_square}_e5")
                    elif from_square == 'e4':
                        legal_actions.append(f"P_{from_square}_e5")
                    # En passant
                    if from_square == 'a4' and state['p']['e3']:
                        legal_actions.append(f"P_{from_square}_e3")
                    elif from_square == 'e4' and state['p']['e3']:
                        legal_actions.append(f"P_{from_square}_e3")
                elif piece_type == 'N':
                    # Knight movement
                    knight_moves = [
                        ('a2', 'b4'), ('a2', 'c3'), ('a2', 'd2'),
                        ('b2', 'a4'), ('b2', 'c4'), ('b2', 'd3'),
                        ('c2', 'a4'), ('c2', 'b3'), ('c2', 'd4'),
                        ('d2', 'a4'), ('d2', 'b3'), ('d2', 'c2'),
                        ('e2', 'd4'), ('e2', 'c3'), ('e2', 'b2')
                    ]
                    for move_from, move_to in knight_moves:
                        if state[move_to] is None:
                            legal_actions.append(f"N_{move_from}_{move_to}")
                elif piece_type == 'B':
                    # Bishop movement
                    bishop_moves = [
                        ('a2', 'c3'), ('a2', 'd4'), ('a2', 'e5'),
                        ('b2', 'a4'), ('b2', 'c3'), ('b2', 'd4'),
                        ('c2', 'a4'), ('c2', 'b3'), ('c2', 'd4'),
                        ('d2', 'a4'), ('d2', 'b3'), ('d2', 'c2'),
                        ('e2', 'd4'), ('e2', 'c3'), ('e2', 'b2')
                    ]
                    for move_from, move_to in bishop_moves:
                        if state[move_to] is None:
                            legal_actions.append(f"B_{move_from}_{move_to}")
                elif piece_type == 'R':
                    # Rook movement
                    rook_moves = [
                        ('a2', 'a4'), ('a2', 'a5'), ('a2', 'b3'),
                        ('a2', 'c2'), ('a2', 'd1'), ('a2', 'e5'),
                        ('b2', 'b4'), ('b2', 'b5'), ('b2', 'c3'),
                        ('b2', 'c2'), ('b2', 'd1'), ('b2', 'e4'),
                        ('c2', 'c4'), ('c2', 'c5'), ('c2', 'd3'),
                        ('c2', 'd2'), ('c2', 'e1'), ('c2', 'e4'),
                        ('d2', 'd4'), ('d2', 'd5'), ('d2', 'e3'),
                        ('d2', 'e1'), ('d2', 'e4'),
                        ('e2', 'e4'), ('e2', 'e5'), ('e2', 'd3'),
                        ('e2', 'c2'), ('e2', 'b1'), ('e2', 'a5')
                    ]
                    for move_from, move_to in rook_moves:
                        if state[move_to] is None:
                            legal_actions.append(f"R_{move_from}_{move_to}")
                elif piece_type == 'Q':
                    # Queen movement
                    queen_moves = bishop_moves + rook_moves
                    for move_from, move_to in queen_moves:
                        if state[move_to] is None:
                            legal_actions.append(f"Q_{move_from}_{move_to}")
                elif piece_type == 'K':
                    # King movement
                    king_moves = [
                        ('a2', 'a3'), ('a2', 'a4'), ('a2', 'b1'),
                        ('a2', 'b2'), ('a2', 'b3'), ('a2', 'c1'),
                        ('a2', 'c2'), ('a2', 'c3'), ('a2', 'd1'),
                        ('a2', 'd2'), ('a2', 'd3'), ('a2', 'e1'),
                        ('a2', 'e2'), ('a2', 'e3'), ('a2', 'f1'),
                        ('a2', 'f2'), ('a2', 'f3'), ('a2', 'g1'),
                        ('a2', 'g2'), ('a2', 'g3'), ('a2', 'h1'),
                        ('a2', 'h2'), ('a2', 'h3')
                    ]
                    for move_from, move_to in king_moves:
                        if state[move_to] is None:
                            legal_actions.append(f"K_{move_from}_{move_to}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Get the current player
    current_player = get_current_player(state)
    
    # Create observations
    player_0_obs = state.copy()
    player_1_obs = state.copy()
    
    # Hide the opponent's pieces for player 0
    for rank, pieces in player_1_obs.items():
        for piece, square in pieces.items():
            if square and square != 'P':
                player_0_obs[rank][square] = None
    
    # Hide the player's own pieces for player 1
    for rank, pieces in player_0_obs.items():
        for piece, square in pieces.items():
            if square and square != 'P':
                player_1_obs[rank][square] = None
    
    return [player_0_obs, player_1_obs]