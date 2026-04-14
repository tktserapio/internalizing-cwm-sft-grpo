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

# Helper function to generate the initial state
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
    # Copy the state to avoid mutating the original state
    new_state = copy.deepcopy(state)
    piece, from_square, to_square = action.split('_')
    
    # Update the board
    new_state['board'][to_square] = new_state['board'].pop(from_square)
    
    # Handle promotions
    if piece == 'P' and to_square in ['e1', 'e8']:
        new_state['board'][to_square] = 'Q'
    
    return new_state

# Function to determine the current player
def get_current_player(state: State) -> int:
    # Determine the current player based on whose turn it is
    if state['board']['e1'] in ['r', 'n', 'b', 'q', 'k']:
        return 0  # White's turn
    elif state['board']['e8'] in ['R', 'N', 'B', 'Q', 'K']:
        return 1  # Black's turn
    else:
        return -4  # Terminal state

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    if player_id == 0:
        return 'White'
    elif player_id == 1:
        return 'Black'
    else:
        raise ValueError("Invalid player ID")

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    # Determine the winner based on the final state
    if state['board']['e1'] in ['r', 'n', 'b', 'q', 'k']:
        return [1.0, 0.0]  # White wins
    elif state['board']['e8'] in ['R', 'N', 'B', 'Q', 'K']:
        return [0.0, 1.0]  # Black wins
    else:
        return [0.0, 0.0]  # Game continues

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    # Get the current player
    current_player = get_current_player(state)
    
    # Generate legal actions for the current player
    legal_actions = []
    for square, piece in state['board'].items():
        if piece != '.':
            # Pawn moves
            if piece == 'P':
                if current_player == 0 and square in ['e2', 'e1']:
                    legal_actions.append(f"P_{square}_e4")
                elif current_player == 1 and square in ['e4', 'e8']:
                    legal_actions.append(f"P_{square}_e3")
            # Other pieces
            else:
                if piece == 'R':
                    for i in range(1, 5):
                        if state['board'].get(f"{square}{i}") == '.':
                            legal_actions.append(f"{piece}_{square}_{square}{i}")
                        elif state['board'].get(f"{square}{i}") == '.' and state['board'].get(f"{square}{i+1}") != '.':
                            legal_actions.append(f"{piece}_{square}_{square}{i+1}")
                elif piece == 'N':
                    for i in [-2, -1, 1, 2]:
                        for j in [-2, -1, 1, 2]:
                            if abs(i) + abs(j) != 0 and state['board'].get(f"{square}{i}{j}") == '.':
                                legal_actions.append(f"{piece}_{square}_{square}{i}{j}")
                elif piece == 'B':
                    for i in range(1, 5):
                        if state['board'].get(f"{square}{i}") == '.':
                            legal_actions.append(f"{piece}_{square}_{square}{i}")
                        elif state['board'].get(f"{square}{i}") != '.' and state['board'].get(f"{square}{i+1}") == '.':
                            legal_actions.append(f"{piece}_{square}_{square}{i+1}")
                elif piece == 'Q':
                    for i in range(1, 5):
                        if state['board'].get(f"{square}{i}") == '.':
                            legal_actions.append(f"{piece}_{square}_{square}{i}")
                        elif state['board'].get(f"{square}{i}") != '.' and state['board'].get(f"{square}{i+1}") == '.':
                            legal_actions.append(f"{piece}_{square}_{square}{i+1}")
                elif piece == 'K':
                    for i in [-1, 0, 1]:
                        for j in [-1, 0, 1]:
                            if abs(i) + abs(j) != 0 and state['board'].get(f"{square}{i}{j}") == '.':
                                legal_actions.append(f"{piece}_{square}_{square}{i}{j}")
    
    return legal_actions

# Function to get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    # Get the current player
    current_player = get_current_player(state)
    
    # Generate observations for each player
    observations = []
    for player_id in [0, 1]:
        observation = {}
        for square, piece in state['board'].items():
            if piece != '.':
                if player_id == 0 and square in ['a1', 'b1', 'c1', 'd1', 'e1']:
                    observation[f"{piece}_{square}"] = 1
                elif player_id == 1 and square in ['a5', 'b5', 'c5', 'd5', 'e5']:
                    observation[f"{piece}_{square}"] = 1
        observations.append(observation)
    
    return observations