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

# Helper function to convert algebraic notation to coordinates
def algebraic_to_coordinates(algebraic_notation):
    file = algebraic_notation[0]
    rank = 6 - int(algebraic_notation[1])  # Inverting ranks for easier indexing
    return file, rank

# Initialize the initial state
def get_initial_state() -> State:
    # Initial board setup
    board = {
        'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
        'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
        'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
        'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
    }
    return {'board': board}

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert algebraic notation to coordinates
    from_file, from_rank = algebraic_to_coordinates(action[:2])
    to_file, to_rank = algebraic_to_coordinates(action[2:4])
    
    # Create a deep copy of the state to avoid mutating the original state
    new_state = copy.deepcopy(state)
    
    # Get the piece from the old position
    piece = new_state['board'][f'{from_file}{from_rank}']
    
    # Update the board with the new position
    new_state['board'][f'{to_file}{to_rank}'] = piece
    new_state['board'][f'{from_file}{from_rank}'] = '.'
    
    # Handle special cases like pawn promotion
    if piece == 'P' and (to_rank == 1 or to_rank == 5):
        new_state['board'][f'{to_file}{to_rank}'] = action[4]
    
    # Handle castling
    if piece == 'K':
        # Castling logic would go here, but it's not implemented in this version
    
    return new_state

# Determine the current player
def get_current_player(state: State) -> int:
    # White starts first
    return 0 if state['board']['e1'] == 'R' else 1

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Get rewards per player
def get_rewards(state: State) -> list[float]:
    # Check for checkmate/stalemate/draw conditions
    if 'K' in state['board']['e5']:
        return [-1.0, 1.0]  # Black wins
    elif 'K' in state['board']['e1']:
        return [1.0, -1.0]  # White wins
    elif len(get_legal_actions(state)) == 0:
        return [0.5, 0.5]  # Draw by stalemate
    else:
        return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    for file in 'abcde':
        for rank in range(1, 6):
            position = f'{file}{rank}'
            piece = state['board'][position]
            
            if piece != '.':
                # Pawn movement
                if piece == 'P':
                    if rank == 2 or rank == 5:
                        # Two-step move
                        if rank == 2:
                            legal_actions.append(f'P_{position}_e{rank + 1}')
                        else:
                            legal_actions.append(f'P_{position}_e{rank - 1}')
                    # One-step move
                    if rank < 5:
                        legal_actions.append(f'P_{position}_e{rank + 1}')
                
                # Other pieces
                elif piece in 'RNQB':
                    # Rook
                    if piece == 'R':
                        for next_rank in range(rank + 1, 6):
                            if state['board'][f'{file}{next_rank}'] == '.':
                                legal_actions.append(f'R_{position}_e{next_rank}')
                            else:
                                break
                        for prev_rank in range(rank - 1, 0, -1):
                            if state['board'][f'{file}{prev_rank}'] == '.':
                                legal_actions.append(f'R_{position}_e{prev_rank}')
                            else:
                                break
                    # Knight
                    elif piece == 'N':
                        for delta_rank, delta_file in [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                                                      (1, -2), (1, 2), (2, -1), (2, 1)]:
                            next_rank, next_file = rank + delta_rank, file + delta_file
                            if 1 <= next_rank <= 5 and 'a' <= next_file <= 'e':
                                if state['board'][f'{next_file}{next_rank}'] == '.':
                                    legal_actions.append(f'N_{position}_{next_file}{next_rank}')
                                else:
                                    break
                    # Bishop
                    elif piece == 'B':
                        for next_rank, next_file in [(rank + 1, rank + 1), (rank + 1, rank - 1),
                                                     (rank - 1, rank + 1), (rank - 1, rank - 1)]:
                            if 1 <= next_rank <= 5 and 'a' <= next_file <= 'e':
                                if state['board'][f'{next_file}{next_rank}'] == '.':
                                    legal_actions.append(f'B_{position}_{next_file}{next_rank}')
                                else:
                                    break
                    # Queen
                    elif piece == 'Q':
                        for next_rank in range(rank + 1, 6):
                            if state['board'][f'{file}{next_rank}'] == '.':
                                legal_actions.append(f'Q_{position}_e{next_rank}')
                            else:
                                break
                        for prev_rank in range(rank - 1, 0, -1):
                            if state['board'][f'{file}{prev_rank}'] == '.':
                                legal_actions.append(f'Q_{position}_e{prev_rank}')
                            else:
                                break
                        for next_file in range(file + 1, 'e'):
                            if state['board'][f'{next_file}{rank}'] == '.':
                                legal_actions.append(f'Q_{position}_{next_file}{rank}')
                            else:
                                break
                        for prev_file in range('a', file):
                            if state['board'][f'{prev_file}{rank}'] == '.':
                                legal_actions.append(f'Q_{position}_{prev_file}{rank}')
                            else:
                                break
                    # King
                    elif piece == 'K':
                        for next_rank, next_file in [(-1, 0), (1, 0), (0, -1), (0, 1),
                                                     (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                            next_rank, next_file = rank + next_rank, file + next_file
                            if 1 <= next_rank <= 5 and 'a' <= next_file <= 'e':
                                if state['board'][f'{next_file}{next_rank}'] == '.':
                                    legal_actions.append(f'K_{position}_{next_file}{next_rank}')
                                else:
                                    break
                
                # Promotion
                if piece == 'P' and (rank == 2 or rank == 5):
                    for next_rank in range(6):
                        if state['board'][f'{file}{next_rank}'] == '.':
                            legal_actions.append(f'P_{position}_e{next_rank}_Q')
                            legal_actions.append(f'P_{position}_e{next_rank}_R')
                            legal_actions.append(f'P_{position}_e{next_rank}_B')
                            legal_actions.append(f'P_{position}_e{next_rank}_N')
    
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    # Observations include the board state and the current player
    return [{'board': state['board'], 'current_player': get_current_player(state)}]