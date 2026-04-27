import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import itertools

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to check if a move connects all three sides
def is_winner(state: State, player: int) -> bool:
    # Extract the board from the state
    board = state['board']
    # Check all possible winning combinations
    for side in ['A', 'B', 'C']:
        for i in range(1, len(board) + 1):
            if f'{side}{i}' in board and f'{side}{i+1}' in board and f'{side}{i+2}' in board:
                return True
    return False

# Required Functions
def get_initial_state() -> State:
    # Initial state with an empty board
    return {'board': {}, 'turn': 0}

def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    row, col = map(int, action.split(','))
    # Create a new state based on the action
    new_state = state.copy()
    new_board = new_state['board'].copy()
    new_turn = (new_state['turn'] + 1) % 2  # Switch to next player
    
    # Apply the action to the board
    if action in new_board:
        raise ValueError(f"Cell {action} is already occupied.")
    new_board[action] = new_turn + 1  # Player ID + 1 (0 for black, 1 for white)
    
    new_state['board'] = new_board
    new_state['turn'] = new_turn
    return new_state

def get_current_player(state: State) -> int:
    return state['turn']

def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> list[float]:
    # Determine the winner
    winner = is_winner(state, state['turn'])
    if winner:
        return [1.0, 0.0] if state['turn'] == 0 else [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    # Get the current player's turn
    player = state['turn']
    # Get the board state
    board = state['board']
    # Generate all possible moves
    moves = []
    for cell in board.keys():
        moves.append(cell)
    return moves

def get_observations(state: State) -> list[PlayerObservation]:
    # Get the current player's turn
    player = state['turn']
    # Get the board state
    board = state['board']
    # Create observations for each player
    obs = [{'board': board, 'turn': player}]
    return obs