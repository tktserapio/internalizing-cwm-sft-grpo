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

# Helper function to create an initial state
def get_initial_state() -> State:
    # Initial state with an empty board
    return {
        'board': {},
        'current_player': 0,
        'turn': 0,
        'winner': None
    }

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if row < 0 or row >= 4 or col < 0 or col >= 4:
        raise ValueError("Invalid action")

    # Update the board with the new action
    state['board'][f'{row},{col}'] = state['current_player']
    state['turn'] += 1

    # Switch the current player
    state['current_player'] = (state['current_player'] + 1) % 2

    # Check if the game is over
    if check_winner(state):
        state['winner'] = state['current_player']
    else:
        state['winner'] = None

    return state

# Function to check if there's a winner
def check_winner(state: State) -> bool:
    # Define the sides of the board
    sides = [
        [(0, 0), (0, 1), (0, 2)],  # Side A-B
        [(0, 0), (1, 0), (2, 0)],  # Side A-C
        [(0, 2), (1, 2), (2, 2)]   # Side B-C
    ]

    # Get the current player's stones
    player_stones = state['board'].values()

    # Check each side for a complete connection
    for side in sides:
        for stone in player_stones:
            if stone == state['current_player']:
                # Check horizontally
                if (stone, stone + 1) in player_stones and (stone + 1, stone + 2) in player_stones:
                    return True
                # Check vertically
                if (stone, stone + 3) in player_stones and (stone + 3, stone + 6) in player_stones:
                    return True
                # Check diagonally
                if (stone, stone + 4) in player_stones and (stone + 4, stone + 8) in player_stones:
                    return True
                # Check anti-diagonally
                if (stone, stone + 2) in player_stones and (stone + 2, stone + 6) in player_stones:
                    return True

    return False

# Function to get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}' if player_id in [0, 1] else 'Unknown'

# Function to get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    # Get the current player's stones
    player_stones = [key for key, value in state['board'].items() if value == state['current_player']]
    # Generate possible moves
    moves = []
    for stone in player_stones:
        row, col = map(int, stone.split(','))
        # Check horizontal moves
        if col > 0 and f'{row},{col-1}' not in state['board']:
            moves.append(f'{row},{col-1}')
        if col < 3 and f'{row},{col+1}' not in state['board']:
            moves.append(f'{row},{col+1}')
        # Check vertical moves
        if row > 0 and f'{row-1},{col}' not in state['board']:
            moves.append(f'{row-1},{col}')
        if row < 3 and f'{row+1},{col}' not in state['board']:
            moves.append(f'{row+1},{col}')
        # Check diagonal moves
        if row > 0 and col > 0 and f'{row-1},{col-1}' not in state['board']:
            moves.append(f'{row-1},{col-1}')
        if row > 0 and col < 3 and f'{row-1},{col+1}' not in state['board']:
            moves.append(f'{row-1},{col+1}')
        if row < 3 and col > 0 and f'{row+1},{col-1}' not in state['board']:
            moves.append(f'{row+1},{col-1}')
        if row < 3 and col < 3 and f'{row+1},{col+1}' not in state['board']:
            moves.append(f'{row+1},{col+1}')
    return moves

# Function to get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    # Observations are the same for both players
    observation = {
        'board': state['board'],
        'current_player': state['current_player'],
        'turn': state['turn'],
        'winner': state['winner']
    }
    return [observation, observation]