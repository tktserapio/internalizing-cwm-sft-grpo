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

# Helper function to convert file and rank to algebraic notation
def file_rank_to_algebraic(file: str, rank: int) -> str:
    return f"{file}{rank}"

# Function to convert algebraic notation back to file and rank
def algebraic_to_file_rank(algebraic: str) -> tuple[str, int]:
    file = algebraic[0]
    rank = int(algebraic[1])
    return file, rank

# Required Functions
def get_initial_state() -> State:
    # Initial state of the game
    initial_state = {
        'board': [
            ['r', 'n', 'b', 'q', 'k'],
            ['p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K']
        ],
        'turn': 0,
        'winner': None,
        'running_reward': [0.0, 0.0],
        'legal_actions': []
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    # Apply the action to the state and return the new state
    new_state = copy.deepcopy(state)
    piece, from_square, to_square = action.split('_')
    from_file, from_rank = algebraic_to_file_rank(from_square)
    to_file, to_rank = algebraic_to_file_rank(to_square)
    
    # Convert from and to squares to board indices
    from_index = 4 * (int(from_rank) - 1) + ord(from_file) - ord('a')
    to_index = 4 * (int(to_rank) - 1) + ord(to_file) - ord('a')
    
    # Get the piece at the from index
    piece_at_from = new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')]
    
    # Update the board
    new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
    new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
    
    # Handle pawn movement
    if piece == 'P':
        if int(from_rank) == 2 and int(to_rank) == 4:
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = 'Q'
        elif int(from_rank) == 1 and int(to_rank) == 3:
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = 'Q'
    
    # Handle promotion
    if piece == 'P' and (int(from_rank) == 1 or int(from_rank) == 2):
        new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = 'Q'
    
    # Handle castling
    if piece == 'R' and (int(from_rank) == 1 and ord(from_file) == ord('a')) and new_state['board'][0][0] == '.' and new_state['board'][0][1] == '.':
        new_state['board'][0][1] = 'R'
        new_state['board'][0][0] = '.'
        new_state['board'][0][2] = '.'
        new_state['board'][0][3] = '.'
        new_state['board'][0][4] = '.'
    
    # Handle en passant
    if piece == 'P' and int(from_rank) == 3 and int(to_rank) == 4 and new_state['board'][4][ord(to_file) - ord('a')] == 'P':
        new_state['board'][4][ord(to_file) - ord('a')] = '.'
    
    # Handle other pieces
    if piece == 'N':
        if abs(ord(from_file) - ord(to_file)) == 1 and abs(int(from_rank) - int(to_rank)) == 2:
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
            new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
        else:
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
            new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
    
    if piece == 'B':
        if abs(ord(from_file) - ord(to_file)) == abs(int(from_rank) - int(to_rank)):
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
            new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
        else:
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
            new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
    
    if piece == 'Q':
        if abs(ord(from_file) - ord(to_file)) == abs(int(from_rank) - int(to_rank)):
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
            new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
        else:
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
            new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
    
    if piece == 'K':
        if abs(ord(from_file) - ord(to_file)) <= 1 and abs(int(from_rank) - int(to_rank)) <= 1:
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
            new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
        else:
            new_state['board'][int(to_rank) - 1][ord(to_file) - ord('a')] = piece_at_from
            new_state['board'][int(from_rank) - 1][ord(from_file) - ord('a')] = '.'
    
    # Determine the winner based on the new state
    winner = determine_winner(new_state)
    if winner:
        new_state['winner'] = winner
        new_state['running_reward'] = [1.0, -1.0] if winner == 0 else [-1.0, 1.0]
    
    # Determine legal actions
    new_state['legal_actions'] = get_legal_actions(new_state)
    
    return new_state

def determine_winner(state: State) -> int:
    # Check for checkmate
    for row in state['board']:
        if 'K' in row:
            for col in range(5):
                if state['board'][col][4] == 'K':
                    return 0 if state['turn'] == 0 else 1
    return None

def get_current_player(state: State) -> int:
    return state['turn']

def get_player_name(player_id: int) -> str:
    return 'Player 0' if player_id == 0 else 'Player 1'

def get_rewards(state: State) -> list[float]:
    return state['running_reward']

def get_legal_actions(state: State) -> list[Action]:
    legal_actions = []
    for row in range(5):
        for col in range(5):
            piece = state['board'][row][col]
            if piece != '.':
                # Pawn movement
                if piece == 'P':
                    if state['turn'] == 0 and row == 1:
                        legal_actions.append(f"P_{file_rank_to_algebraic('a', row)}_{file_rank_to_algebraic('a', row + 2)}")
                    if state['turn'] == 1 and row == 4:
                        legal_actions.append(f"P_{file_rank_to_algebraic('a', row)}_{file_rank_to_algebraic('a', row + 2)}")
                    if state['turn'] == 0 and row == 2:
                        legal_actions.append(f"P_{file_rank_to_algebraic('a', row)}_{file_rank_to_algebraic('a', row + 1)}")
                    if state['turn'] == 1 and row == 3:
                        legal_actions.append(f"P_{file_rank_to_algebraic('a', row)}_{file_rank_to_algebraic('a', row + 1)}")
                # Other pieces
                if piece in ('N', 'B', 'Q', 'R', 'K'):
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            if dr == 0 and dc == 0:
                                continue
                            next_row = row + dr
                            next_col = col + dc
                            if 0 <= next_row < 5 and 0 <= next_col < 5 and state['board'][next_row][next_col] == '.':
                                legal_actions.append(f"{piece}_{file_rank_to_algebraic(chr(col + ord('a')), row)}_{file_rank_to_algebraic(chr(next_col + ord('a')), next_row)}")
                            if piece == 'P' and (state['turn'] == 0 and row == 1 or state['turn'] == 1 and row == 4):
                                next_row = row + dr
                                next_col = col + dc
                                if 0 <= next_row < 5 and 0 <= next_col < 5 and state['board'][next_row][next_col] == '.':
                                    legal_actions.append(f"{piece}_{file_rank_to_algebraic(chr(col + ord('a')), row)}_{file_rank_to_algebraic(chr(next_col + ord('a')), next_row)}_Q")
                # Promotion
                if piece == 'P' and (state['turn'] == 0 and row == 1 or state['turn'] == 1 and row == 4):
                    legal_actions.append(f"P_{file_rank_to_algebraic('a', row)}_{file_rank_to_algebraic('a', row + 1)}_Q")
                # Castling
                if piece == 'R' and (state['turn'] == 0 and row == 1 and col == 0) and state['board'][0][1] == '.' and state['board'][0][2] == '.':
                    legal_actions.append(f"R_{file_rank_to_algebraic('a', 1)}_{file_rank_to_algebraic('c', 1)}")
                if piece == 'R' and (state['turn'] == 0 and row == 1 and col == 4) and state['board'][0][3] == '.' and state['board'][0][2] == '.':
                    legal_actions.append(f"R_{file_rank_to_algebraic('d', 1)}_{file_rank_to_algebraic('c', 1)}")
                if piece == 'R' and (state['turn'] == 1 and row == 4 and col == 0) and state['board'][4][1] == '.' and state['board'][4][2] == '.':
                    legal_actions.append(f"R_{file_rank_to_algebraic('a', 4)}_{file_rank_to_algebraic('c', 4)}")
                if piece == 'R' and (state['turn'] == 1 and row == 4 and col == 4) and state['board'][4][3] == '.' and state['board'][4][2] == '.':
                    legal_actions.append(f"R_{file_rank_to_algebraic('d', 4)}_{file_rank_to_algebraic('c', 4)}")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    # Observations are the same for both players
    observation = {
        'board': state['board'],
        'turn': state['turn'],
        'winner': state['winner'],
        'legal_actions': state['legal_actions']
    }
    return [observation, observation]