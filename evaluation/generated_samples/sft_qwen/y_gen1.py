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

# Helper function to initialize the board
def _init_board(size: int) -> State:
    board = {}
    for i in range(1, size + 1):
        for j in range(i):
            key = f"{chr(ord('A') + j)}{i}" if i < size else str(i)
            board[key] = {'color': None, 'occupied': False}
    return board

# Initialize the game state
def get_initial_state() -> State:
    # Size 4 board for simplicity
    size = 4
    board = _init_board(size)
    return {'board': board, 'current_player': 0}

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    row, col = map(int, action.split(','))
    # Get the current player
    player = state['current_player']
    
    # Check if the action is valid
    if row < 0 or col < 0 or row >= len(state['board']) or col >= len(state['board'][0]):
        raise ValueError("Invalid action")
    
    # Update the board
    board = state['board']
    board_key = f"{chr(ord('A') + col)}{row + 1}" if row < len(board) - 1 else str(row + 1)
    board[board_key]['color'] = player
    board[board_key]['occupied'] = True
    
    # Switch to the other player
    next_player = 1 if player == 0 else 0
    return {'board': board, 'current_player': next_player}

# Get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Get the rewards per player
def get_rewards(state: State) -> list[float]:
    # In this simple implementation, we assume the game ends when the board is full
    if len(state['board']) == 10:
        return [1.0, 0.0] if state['current_player'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    board = state['board']
    current_player = state['current_player']
    legal_actions = []
    for key, value in board.items():
        if not value['occupied']:
            legal_actions.append(key)
    return legal_actions

# Get observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    board = state['board']
    observations = []
    for key, value in board.items():
        if value['color'] == 0:
            observations.append({'color': 'Black', 'position': key})
        elif value['color'] == 1:
            observations.append({'color': 'White', 'position': key})
    return observations

# Example usage
if __name__ == "__main__":
    state = get_initial_state()
    print("Initial State:", state)
    
    # Simulate a few moves
    for move in ["0,0", "0,1", "0,2", "1,2", "2,2", "2,1"]:
        state = apply_action(state, move)
        print(f"After move {move}: Current Player {get_player_name(get_current_player(state))}, State:", state)
    
    # Get rewards
    print("Rewards:", get_rewards(state))
    
    # Get legal actions
    print("Legal Actions:", get_legal_actions(state))
    
    # Get observations
    print("Observations:", get_observations(state))