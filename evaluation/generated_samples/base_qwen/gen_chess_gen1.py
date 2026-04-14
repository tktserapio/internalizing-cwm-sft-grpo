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
    file, rank = algebraic_notation[0], algebraic_notation[1]
    return f"{rank}{file}"

# Function to convert coordinates to algebraic notation
def coordinates_to_algebraic(rank, file):
    return f"{file}{rank}"

# Function to get the initial game state
def get_initial_state() -> State:
    # Initial board setup
    initial_board = {
        'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K',
        'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P',
        'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.',
        'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.',
        'a5': 'r', 'b5': 'n', 'c5': 'b', 'd5': 'q', 'e5': 'k'
    }
    return {'board': initial_board}

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    piece, from_square, to_square = action.split('_')
    
    # Convert algebraic notation to coordinates
    from_coords = algebraic_to_coordinates(from_square)
    to_coords = algebraic_to_coordinates(to_square)
    
    # Get the piece at the from_square
    from_piece = new_state['board'].pop(from_coords)
    
    # Place the piece at the to_square
    new_state['board'][to_coords] = from_piece
    
    # Update the board dictionary
    new_state['board'] = {k: v for k, v in new_state['board'].items()}
    
    # Check for pawn promotion
    if from_piece == 'P' and (to_coords[0] == 'e' or to_coords[0] == 'a'):
        new_state['board'][to_coords] += '_Q'
    
    return new_state

# Function to get the current player
def get_current_player(state: State) -> int:
    # Determine the current player based on whose turn it is
    if state['board']['e1'] != '.':
        return 0  # White's turn
    else:
        return 1  # Black's turn

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return ['White', 'Black'][player_id]

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    # Determine the winner based on the board state
    if state['board']['e1'] == '.':
        return [1.0, -1.0]  # White wins
    elif state['board']['e5'] == '.':
        return [-1.0, 1.0]  # Black wins
    else:
        return [0.0, 0.0]  # Game is not over yet

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    current_player = get_current_player(state)
    
    # Iterate through each square on the board
    for rank in range(1, 6):
        for file in 'abcde':
            coords = f"{rank}{file}"
            
            # Check if there's a piece on the current square
            if coords in state['board']:
                piece = state['board'][coords]
                
                # Pawn movement
                if piece == 'P':
                    # Check for double move
                    if coords == 'e2':
                        legal_actions.append(f"P_{coords}_e4")
                    elif coords == 'e1':
                        legal_actions.append(f"P_{coords}_e3")
                    else:
                        if coords[1] != 'e':
                            legal_actions.append(f"P_{coords}_e{chr(ord(coords[1]) + 1)}")
                        if coords[1] != 'a':
                            legal_actions.append(f"P_{coords}_e{chr(ord(coords[1]) - 1)}")
                
                # Knight movement
                if piece == 'N':
                    knight_moves = [
                        ('a1', 'b3'), ('a1', 'c3'), ('a1', 'd3'), ('a1', 'e3'),
                        ('b1', 'a3'), ('b1', 'c3'), ('b1', 'd3'), ('b1', 'e3'),
                        ('c1', 'a3'), ('c1', 'b3'), ('c1', 'd3'), ('c1', 'e3'),
                        ('d1', 'a3'), ('d1', 'b3'), ('d1', 'c3'), ('d1', 'e3'),
                        ('e1', 'a3'), ('e1', 'b3'), ('e1', 'c3'), ('e1', 'd3')
                    ]
                    for move in knight_moves:
                        if move[0] == coords:
                            legal_actions.append(f"N_{coords}_{move[1]}")
                
                # Bishop movement
                if piece == 'B':
                    bishop_moves = []
                    for i in range(1, 5):
                        if coords[0] + chr(ord(coords[1]) + i) in state['board']:
                            bishop_moves.append(coords[0] + chr(ord(coords[1]) + i))
                        if coords[0] + chr(ord(coords[1]) - i) in state['board']:
                            bishop_moves.append(coords[0] + chr(ord(coords[1]) - i))
                        if coords[1] + str(int(coords[0]) + i) in state['board']:
                            bishop_moves.append(chr(ord(coords[1]) + i) + coords[1])
                        if coords[1] + str(int(coords[0]) - i) in state['board']:
                            bishop_moves.append(chr(ord(coords[1]) - i) + coords[1])
                    for move in bishop_moves:
                        legal_actions.append(f"B_{coords}_{move}")
                
                # Rook movement
                if piece == 'R':
                    rook_moves = []
                    for i in range(1, 5):
                        if coords[0] + str(int(coords[1]) + i) in state['board']:
                            rook_moves.append(coords[0] + str(int(coords[1]) + i))
                        if coords[0] + str(int(coords[1]) - i) in state['board']:
                            rook_moves.append(coords[0] + str(int(coords[1]) - i))
                        if chr(ord(coords[1]) + i) + coords[1] in state['board']:
                            rook_moves.append(chr(ord(coords[1]) + i) + coords[1])
                        if chr(ord(coords[1]) - i) + coords[1] in state['board']:
                            rook_moves.append(chr(ord(coords[1]) - i) + coords[1])
                    for move in rook_moves:
                        legal_actions.append(f"R_{coords}_{move}")
                
                # Queen movement
                if piece == 'Q':
                    queen_moves = []
                    for i in range(1, 5):
                        if coords[0] + str(int(coords[1]) + i) in state['board']:
                            queen_moves.append(coords[0] + str(int(coords[1]) + i))
                        if coords[0] + str(int(coords[1]) - i) in state['board']:
                            queen_moves.append(coords[0] + str(int(coords[1]) - i))
                        if chr(ord(coords[1]) + i) + coords[1] in state['board']:
                            queen_moves.append(chr(ord(coords[1]) + i) + coords[1])
                        if chr(ord(coords[1]) - i) + coords[1] in state['board']:
                            queen_moves.append(chr(ord(coords[1]) - i) + coords[1])
                    for move in queen_moves:
                        legal_actions.append(f"Q_{coords}_{move}")
                
                # King movement
                if piece == 'K':
                    king_moves = [
                        ('a1', 'b1'), ('a1', 'c1'), ('a1', 'd1'), ('a1', 'e1'),
                        ('b1', 'a1'), ('b1', 'c1'), ('b1', 'd1'), ('b1', 'e1'),
                        ('c1', 'a1'), ('c1', 'b1'), ('c1', 'd1'), ('c1', 'e1'),
                        ('d1', 'a1'), ('d1', 'b1'), ('d1', 'c1'), ('d1', 'e1'),
                        ('e1', 'a1'), ('e1', 'b1'), ('e1', 'c1'), ('e1', 'd1'),
                        ('a1', 'a2'), ('a1', 'b2'), ('a1', 'c2'), ('a1', 'd2'), ('a1', 'e2'),
                        ('b1', 'a2'), ('b1', 'c2'), ('b1', 'd2'), ('b1', 'e2'),
                        ('c1', 'a2'), ('c1', 'b2'), ('c1', 'd2'), ('c1', 'e2'),
                        ('d1', 'a2'), ('d1', 'b2'), ('d1', 'c2'), ('d1', 'e2'),
                        ('e1', 'a2'), ('e1', 'b2'), ('e1', 'c2'), ('e1', 'd2'),
                        ('a1', 'a3'), ('a1', 'b3'), ('a1', 'c3'), ('a1', 'd3'), ('a1', 'e3'),
                        ('b1', 'a3'), ('b1', 'c3'), ('b1', 'd3'), ('b1', 'e3'),
                        ('c1', 'a3'), ('c1', 'b3'), ('c1', 'd3'), ('c1', 'e3'),
                        ('d1', 'a3'), ('d1', 'b3'), ('d1', 'c3'), ('d1', 'e3'),
                        ('e1', 'a3'), ('e1', 'b3'), ('e1', 'c3'), ('e1', 'd3'),
                        ('a1', 'a4'), ('a1', 'b4'), ('a1', 'c4'), ('a1', 'd4'), ('a1', 'e4'),
                        ('b1', 'a4'), ('b1', 'c4'), ('b1', 'd4'), ('b1', 'e4'),
                        ('c1', 'a4'), ('c1', 'b4'), ('c1', 'd4'), ('c1', 'e4'),
                        ('d1', 'a4'), ('d1', 'b4'), ('d1', 'c4'), ('d1', 'e4'),
                        ('e1', 'a4'), ('e1', 'b4'), ('e1', 'c4'), ('e1', 'd4'),
                        ('a1', 'a5'), ('a1', 'b5'), ('a1', 'c5'), ('a1', 'd5'), ('a1', 'e5'),
                        ('b1', 'a5'), ('b1', 'c5'), ('b1', 'd5'), ('b1', 'e5'),
                        ('c1', 'a5'), ('c1', 'b5'), ('c1', 'd5'), ('c1', 'e5'),
                        ('d1', 'a5'), ('d1', 'b5'), ('d1', 'c5'), ('d1', 'e5'),
                        ('e1', 'a5'), ('e1', 'b5'), ('e1', 'c5'), ('e1', 'd5')
                    ]
                    for move in king_moves:
                        if move[0] == coords:
                            legal_actions.append(f"K_{coords}_{move[1]}")
    
    return legal_actions

# Function to get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    white_observation = {}
    black_observation = {}
    
    # White sees the entire board
    for rank in range(1, 6):
        for file in 'abcde':
            coords = f"{rank}{file}"
            piece = state['board'].get(coords, '.')
            if piece != '.':
                white_observation[coords] = piece
    
    # Black only sees the side of the board where he is playing
    for rank in range(4, 6):
        for file in 'abcde':
            coords = f"{rank}{file}"
            piece = state['board'].get(coords, '.')
            if piece != '.':
                black_observation[coords] = piece
    
    return [white_observation, black_observation]