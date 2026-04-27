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
    # Extracting the board state
    board = state['board']
    # Checking each side for a winning connection
    for side in ['A', 'B', 'C']:
        for i in range(1, len(board) + 1):
            if f"{side}{i}" in board and (
                (f"{side}{i-1}" in board and f"{side}{i+1}" in board) or
                (f"{side}{i-2}" in board and f"{side}{i+2}" in board)
            ):
                return True
    return False

# Required Functions
def get_initial_state() -> State:
    # Initial state with an empty board
    return {
        'board': {},
        'turn': 0,
        'winner': -4,
        'running_reward': [0.0, 0.0]
    }

def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    row, col = map(int, action.split(','))
    # Update the board state
    state['board'][action] = state['turn'] + 1
    # Switch turn
    state['turn'] = 1 - state['turn']
    # Check if the move leads to a win
    if is_winner(state, state['turn']):
        state['winner'] = state['turn']
        state['running_reward'][state['turn']] += 1.0
    # Check if the board is full
    if len(state['board']) == len(state['board'].keys()):
        state['winner'] = -4
    return state

def get_current_player(state: State) -> int:
    return state['turn']

def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> list[float]:
    return state['running_reward']

def get_legal_actions(state: State) -> list[Action]:
    # Get all possible moves
    all_moves = set(itertools.product(range(1, len(state['board']) + 1), repeat=2))
    # Remove moves that are already taken
    taken_moves = set(state['board'].keys())
    legal_moves = all_moves - taken_moves
    # Return only valid moves
    return [f"{row},{col}" for row, col in legal_moves]

def get_observations(state: State) -> list[PlayerObservation]:
    # Observations are identical for both players in this game
    return [
        {
            'board': state['board'],
            'turn': state['turn'],
            'winner': state['winner'],
            'running_reward': state['running_reward']
        },
        {
            'board': state['board'],
            'turn': state['turn'],
            'winner': state['winner'],
            'running_reward': state['running_reward']
        }
    ]