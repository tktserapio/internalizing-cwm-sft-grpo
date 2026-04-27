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

# Function to get the initial state of the game
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
    # Get the current board state
    board = state['board']
    
    # Parse the action
    piece, from_square, to_square = action.split('_')
    from_square = algebraic_to_coordinates(from_square)
    to_square = algebraic_to_coordinates(to_square)
    
    # Check if the action is valid
    if from_square not in board or to_square not in board:
        raise ValueError("Invalid action: Invalid square coordinates.")
    
    # Perform the move
    board[to_square] = board[from_square]
    board[from_square] = '.'
    
    # Handle promotions
    if piece == 'P' and abs(int(from_square[1]) - int(to_square[1])) == 2:
        board[to_square] = 'P' + to_square[-1]
    
    # Handle castling
    if piece == 'K':
        # Castling logic here (not implemented for simplicity)
        pass
    
    # Handle en passant
    if piece == 'P' and abs(int(from_square[1]) - int(to_square[1])) == 1 and from_square[0] == to_square[0]:
        captured_piece = board.pop(f'{to_square[0]}{int(to_square[1]) - 1}')
        board[to_square] = 'P' + to_square[-1]
    
    return {'board': board}

# Function to get the current player
def get_current_player(state: State) -> int:
    # Determine the current player based on whose turn it is
    # In this simplified version, we assume the first player is always white
    return 0 if state['board']['a1'] != '.' else 1

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Player 0' if player_id == 0 else 'Player 1'

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    # Determine the winner based on the final board configuration
    winner = None
    for square in state['board'].values():
        if square == 'K':
            winner = 0 if 'a1' in square else 1
            break
    
    if winner is None:
        return [0.0, 0.0]  # Game is still ongoing
    elif winner == 0:
        return [1.0, -1.0]  # Player 0 wins
    else:
        return [-1.0, 1.0]  # Player 1 wins

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    # Generate all possible moves and promotions
    legal_actions = []
    for square, piece in state['board'].items():
        if piece != '.':
            # Generate all possible moves for the given piece
            for target_square in state['board']:
                if target_square != square and state['board'][target_square] == '.':
                    # Generate the move action
                    legal_actions.append(f"{piece}_{square}_{target_square}")
                    # Handle promotions if applicable
                    if piece == 'P' and abs(int(square[1]) - int(target_square[1])) == 2:
                        for promotion_piece in ['Q', 'R', 'B', 'N']:
                            legal_actions.append(f"{piece}_{square}_{target_square}_{promotion_piece}")
    
    return legal_actions

# Function to get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    # Each player sees the same board state
    return [{'board': state['board']}]

# Example usage
if __name__ == "__main__":
    # Initialize the game
    state = get_initial_state()
    
    # Simulate a few turns
    print("Initial state:")
    print(state)
    
    # Player 0's turn
    action = 'P_a2_a3'
    state = apply_action(state, action)
    print("\nAfter Player 0's turn:")
    print(state)
    
    # Player 1's turn
    action = 'P_a4_a5'
    state = apply_action(state, action)
    print("\nAfter Player 1's turn:")
    print(state)
    
    # Get the current player
    print("\nCurrent player:", get_current_player(state))
    
    # Get the rewards
    print("\nRewards:", get_rewards(state))
    
    # Get the legal actions
    print("\nLegal actions:", get_legal_actions(state))
    
    # Get the observations
    print("\nObservations:", get_observations(state))