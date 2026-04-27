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

# Helper function to generate the initial state
def get_initial_state() -> State:
    # Initial state dictionary
    return {
        'board': ['E'] * 10,  # 'E' represents empty cells
        'current_player': 0,  # Player 0 is Black
        'turn': 0,            # Turn counter starts from 0
        'winner': None         # No winner yet
    }

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action to coordinates
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if state['board'][10 + row + col] != 'E':
        raise ValueError("Cell is already occupied")

    # Update the board
    state['board'][10 + row + col] = 'B' if state['current_player'] == 0 else 'W'
    state['turn'] += 1

    # Determine the next player
    state['current_player'] = 1 if state['current_player'] == 0 else 0

    # Check for win condition
    check_win(state)
    return state

# Function to check if there's a winner
def check_win(state: State):
    board = state['board']
    current_player = state['current_player']

    # Define the sides of the board
    side_a_b = [0, 2, 4]
    side_a_c = [1, 5, 9]
    side_b_c = [2, 5, 8, 9]

    # Check each player's possible winning groups
    def find_winning_group(side):
        for i in side:
            if board[i] == 'B' and all(board[j] == 'B' for j in side if j != i):
                return True
            elif board[i] == 'W' and all(board[j] == 'W' for j in side if j != i):
                return True
        return False

    if find_winning_group(side_a_b) or find_winning_group(side_a_c) or find_winning_group(side_b_c):
        state['winner'] = current_player
    else:
        if state['turn'] == 10:  # If all cells are filled and no winner, it's a draw
            state['winner'] = None

# Function to get the current player
def get_current_player(state: State) -> int:
    return state['current_player']

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Function to get rewards
def get_rewards(state: State) -> List[float]:
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Function to get legal actions
def get_legal_actions(state: State) -> List[Action]:
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    for i in range(10):
        if board[i] == 'E':
            legal_actions.append(f"{i}")

    return legal_actions

# Function to get observations
def get_observations(state: State) -> List[PlayerObservation]:
    board = state['board']
    current_player = state['current_player']
    observations = []

    for i in range(10):
        observation = {'cell': f"{i}", 'occupied': board[i] == 'B' if current_player == 0 else board[i] == 'W'}
        observations.append(observation)

    return observations

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)

    # Apply some actions
    actions = ["0", "2", "4", "1", "5", "8"]
    for action in actions:
        initial_state = apply_action(initial_state, action)
        print(f"After action {action}:")
        print(initial_state)