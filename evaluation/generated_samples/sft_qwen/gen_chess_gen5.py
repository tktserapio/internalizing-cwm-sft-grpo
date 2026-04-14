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

# Helper function to convert board coordinates to algebraic notation
def coord_to_algebraic(coord):
    file, rank = coord
    return f"{chr(ord('a') + int(file))}{int(rank) + 1}"

# Initialize the game state
def get_initial_state() -> State:
    # Initial board setup
    initial_board = {
        'r': (0, 0), 'n': (0, 1), 'b': (0, 2), 'q': (0, 3), 'k': (0, 4),
        'p': [(1, i) for i in range(5)],
        'R': (4, 0), 'N': (4, 1), 'B': (4, 2), 'Q': (4, 3), 'K': (4, 4),
        'p': [(3, i) for i in range(5)]
    }
    return {
        'board': initial_board,
        'turn': 0,
        'castling_rights': {'w_k': True, 'w_q': True, 'b_k': False, 'b_q': False},
        'en_passant_target': None,
        'halfmove_clock': 0,
        'fullmove_number': 1,
        'check': False,
        'checkmate': False,
        'stalemate': False,
        'insufficient_material': False,
        'winner': None
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    piece, from_coord, to_coord = action.split('_')
    from_coord = coord_to_algebraic(from_coord)
    to_coord = coord_to_algebraic(to_coord)
    
    # Handle pawn movement
    if piece == 'p':
        if state['board'][piece][0] == 1:  # White pawn
            if to_coord[1] == '5':  # Promotion
                new_state['board'][piece].append((5, int(to_coord[1])))
                new_state['board'][piece].remove((1, int(from_coord[1])))
                new_state['board'][piece][0] = 5
            else:
                new_state['board'][piece].remove((1, int(from_coord[1])))
                new_state['board'][piece].append((1, int(to_coord[1])))
        else:  # Black pawn
            if to_coord[1] == '1':  # Promotion
                new_state['board'][piece].append((1, int(to_coord[1])))
                new_state['board'][piece].remove((5, int(from_coord[1])))
                new_state['board'][piece][0] = 1
            else:
                new_state['board'][piece].remove((5, int(from_coord[1])))
                new_state['board'][piece].append((5, int(to_coord[1])))
    
    # Handle other pieces
    elif piece in ['r', 'n', 'b', 'q', 'k']:
        if piece == 'p' and abs(int(from_coord[1]) - int(to_coord[1])) == 2:
            new_state['en_passant_target'] = (int(from_coord[1]), int(to_coord[1]))
        else:
            new_state['board'][piece].remove((int(from_coord[1]), int(from_coord[2])))
            new_state['board'][piece].append((int(to_coord[1]), int(to_coord[2])))
    
    # Update castling rights
    if piece == 'K':
        new_state['castling_rights']['w_k'] = False
        new_state['castling_rights']['w_q'] = False
        new_state['castling_rights']['b_k'] = False
        new_state['castling_rights']['b_q'] = False
    
    # Update en passant target
    if new_state['en_passant_target']:
        new_state['board']['p'].remove(new_state['en_passant_target'])
        new_state['en_passant_target'] = None
    
    # Update halfmove clock
    if new_state['board'][piece][0] == 1:
        new_state['halfmove_clock'] += 1
    else:
        new_state['halfmove_clock'] = 0
    
    # Update fullmove number
    new_state['fullmove_number'] += 1
    
    # Check for checkmate
    if new_state['board']['K'][0] == 1:
        new_state['checkmate'] = True
        new_state['winner'] = 1
    elif new_state['board']['K'][0] == 5:
        new_state['checkmate'] = True
        new_state['winner'] = 0
    
    return new_state

# Get current player
def get_current_player(state: State) -> int:
    return state['turn']

# Get player name
def get_player_name(player_id: int) -> str:
    return 'Player 0' if player_id == 0 else 'Player 1'

# Get rewards
def get_rewards(state: State) -> list[float]:
    if state['winner'] is not None:
        return [-1.0, 1.0] if state['winner'] == 0 else [1.0, -1.0]
    return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    for piece, coords in state['board'].items():
        if piece == 'p':
            if state['board'][piece][0] == 1:
                # White pawn
                for i in range(5):
                    if i != int(state['board'][piece][1]):
                        legal_actions.append(f'p_{coord_to_algebraic((1, i))}_{coord_to_algebraic((1, i + 1))}')
                        if i == 1:
                            legal_actions.append(f'p_{coord_to_algebraic((1, i))}_{coord_to_algebraic((1, i + 2))}')
            else:
                # Black pawn
                for i in range(5):
                    if i != int(state['board'][piece][1]):
                        legal_actions.append(f'p_{coord_to_algebraic((5, i))}_{coord_to_algebraic((5, i + 1))}')
                        if i == 1:
                            legal_actions.append(f'p_{coord_to_algebraic((5, i))}_{coord_to_algebraic((5, i + 2))}')
        elif piece in ['r', 'n', 'b', 'q', 'k']:
            for from_coord in coords:
                if piece == 'p' and state['board'][piece][0] == 1:
                    for to_coord in [(from_coord[0], from_coord[1] + 1), (from_coord[0], from_coord[1] - 1)]:
                        if to_coord[1] in ['1', '5']:
                            legal_actions.append(f'{piece}_{coord_to_algebraic(from_coord)}_{coord_to_algebraic(to_coord)}')
                else:
                    for to_coord in [(from_coord[0] + 1, from_coord[1]), (from_coord[0] - 1, from_coord[1]),
                                     (from_coord[0] + 1, from_coord[1] + 1), (from_coord[0] - 1, from_coord[1] - 1)]:
                        if 0 <= to_coord[0] < 5 and 0 <= to_coord[1] < 5:
                            legal_actions.append(f'{piece}_{coord_to_algebraic(from_coord)}_{coord_to_algebraic(to_coord)}')
    return legal_actions

# Get observations
def get_observations(state: State) -> list[PlayerObservation]:
    observations = []
    for player_id in [0, 1]:
        obs = {}
        obs['board'] = {key: [] for key in state['board']}
        obs['board']['K'] = [state['board']['K'][0]]
        obs['board']['p'] = [coord for coord in state['board']['p'] if coord[0] == player_id]
        obs['board']['r'] = [coord for coord in state['board']['r'] if coord[0] == player_id]
        obs['board']['n'] = [coord for coord in state['board']['n'] if coord[0] == player_id]
        obs['board']['b'] = [coord for coord in state['board']['b'] if coord[0] == player_id]
        obs['board']['q'] = [coord for coord in state['board']['q'] if coord[0] == player_id]
        obs['board']['k'] = [coord for coord in state['board']['k'] if coord[0] == player_id]
        obs['turn'] = state['turn']
        obs['castling_rights'] = state['castling_rights']
        obs['en_passant_target'] = state['en_passant_target']
        obs['halfmove_clock'] = state['halfmove_clock']
        obs['fullmove_number'] = state['fullmove_number']
        obs['check'] = state['check']
        obs['checkmate'] = state['checkmate']
        obs['stalemate'] = state['stalemate']
        obs['insufficient_material'] = state['insufficient_material']
        obs['winner'] = state['winner']
        observations.append(obs)
    return observations