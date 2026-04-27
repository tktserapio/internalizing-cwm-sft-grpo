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

# Helper function to initialize the state
def get_initial_state() -> State:
    # Initialize the board as a dictionary with coordinates as keys and None as values
    # Each side of the board is represented as a set of coordinates
    board = {
        'A1': None, 'A2': None, 'A3': None, 'A4': None,
        'B1': None, 'B2': None, 'B3': None, 'B4': None,
        'C1': None, 'C2': None, 'C3': None, 'C4': None,
        'A6': None, 'B6': None, 'C6': None, 'A9': None, 'B9': None, 'C9': None,
        'A7': None, 'B7': None, 'C7': None, 'A8': None, 'B8': None, 'C8': None, 'A5': None,
        'A6': None, 'B6': None, 'C6': None, 'A9': None, 'B9': None, 'C9': None
    }
    return {'board': board}

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert the action string to a tuple of coordinates
    row, col = map(int, action.split(','))
    # Get the current state
    board = state['board']
    # Check if the action is valid
    if board.get(f'A{col}') is None and board.get(f'B{col}') is None and board.get(f'C{col}') is None:
        # Place the stone on the board
        board[f'A{col}'] = 'B'
        board[f'B{col}'] = 'W'
        board[f'C{col}'] = 'B'
        return {'board': board}
    else:
        raise ValueError("Invalid move")

# Function to get the current player
def get_current_player(state: State) -> int:
    # Count the number of 'B' and 'W' stones on the board
    black_stones = sum(1 for value in state['board'].values() if value == 'B')
    white_stones = sum(1 for value in state['board'].values() if value == 'W')
    # Determine the current player based on the count
    if black_stones > white_stones:
        return 0  # Black's turn
    elif white_stones > black_stones:
        return 1  # White's turn
    else:
        return -4  # Terminal state

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    # Player 0 is Black, Player 1 is White
    return ['Black', 'White'][player_id]

# Function to get the rewards for the given state
def get_rewards(state: State) -> List[float]:
    # In a perfect information game, there should be no rewards until the game ends
    return [0.0, 0.0]

# Function to get the legal actions for the given state
def get_legal_actions(state: State) -> List[Action]:
    # Get the current player
    current_player = get_current_player(state)
    # Get the board state
    board = state['board']
    # Generate legal moves
    legal_moves = []
    for key, value in board.items():
        if value is None:
            # Check if the move can connect all three sides
            if check_connection(key, board):
                legal_moves.append(key)
    # Return the legal moves for the current player
    if current_player == 0:
        return legal_moves
    else:
        return []

# Function to check if a move can connect all three sides
def check_connection(cell: str, board: Dict[str, Any]) -> bool:
    # Implement the logic to check if the move can connect all three sides
    # This is a placeholder implementation
    return False

# Function to get the observations for the given state
def get_observations(state: State) -> List[PlayerObservation]:
    # Since it's a perfect information game, both players see the same state
    return [{'board': state['board']}]

# Test the implementation
initial_state = get_initial_state()
print("Initial State:", initial_state)
black_move = apply_action(initial_state, "0,0")
print("After Black's move:", black_move)
white_move = apply_action(black_move, "0,1")
print("After White's move:", white_move)
current_player = get_current_player(white_move)
print("Current Player:", get_player_name(current_player))