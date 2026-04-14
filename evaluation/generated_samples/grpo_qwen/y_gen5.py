import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to generate the board structure
def generate_board(size: int) -> Dict[int, Tuple[int, int]]:
    board = {}
    for i in range(1, size + 1):
        for j in range(i):
            board[i * (i + 1) // 2 + j] = (i, j)
    return board

# Initial state function
def get_initial_state() -> State:
    # Size-4 board for simplicity
    size = 4
    board = generate_board(size)
    state = {
        'board': board,
        'current_player': 0,  # Black starts
        'winner': -4,  # -4 indicates no winner yet
        'turn': 0,  # Turn counter
        'size': size
    }
    return state

# Apply action function
def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    action_coords = tuple(map(int, action.split(',')))
    if len(action_coords) != 2:
        raise ValueError("Invalid action format")
    
    # Get the current player's color
    player_color = 'B' if state['current_player'] == 0 else 'W'
    
    # Check if the action is valid
    if action_coords not in state['board']:
        raise ValueError("Invalid move: cell is already occupied")
    
    # Update the board with the player's color
    state['board'][action_coords] = player_color
    
    # Determine the winner based on the new board configuration
    winner = determine_winner(state)
    if winner != -4:
        return {'state': state, 'winner': winner}
    
    # Switch to the next player
    state['current_player'] = 1 - state['current_player']
    state['turn'] += 1
    
    return {'state': state, 'winner': -4}

# Determine winner function
def determine_winner(state: State) -> int:
    board = state['board']
    size = state['size']
    corners = [(0, 0), (size * (size + 1) // 2 - 1, 0), (size * (size + 1) // 2 - 1, size - 1)]
    
    # Check each side for a connected path
    def check_side(side: List[Tuple[int, int]], player_color: str) -> bool:
        for start in side:
            queue = [start]
            visited = set([start])
            while queue:
                current = queue.pop(0)
                if current in corners:
                    return True
                for neighbor in [(current[0] + 1, current[1]), (current[0] - 1, current[1]), (current[0], current[1] + 1), (current[0], current[1] - 1)]:
                    if neighbor in board and board[neighbor] == player_color and neighbor not in visited:
                        queue.append(neighbor)
                        visited.add(neighbor)
        return False
    
    # Check all three sides
    if check_side([(0, 0), (0, 1), (0, 2)], 'B') and check_side([(size * (size + 1) // 2 - 1, size - 1), (size * (size + 1) // 2 - 2, size - 1), (size * (size + 1) // 2 - 3, size - 1)], 'B') and check_side([(size * (size + 1) // 2 - 1, 0), (size * (size + 1) // 2 - 1, 1), (size * (size + 1) // 2 - 1, 2)], 'B'):
        return 0  # Black wins
    elif check_side([(0, 0), (0, 1), (0, 2)], 'W') and check_side([(size * (size + 1) // 2 - 1, size - 1), (size * (size + 1) // 2 - 2, size - 1), (size * (size + 1) // 2 - 3, size - 1)], 'W') and check_side([(size * (size + 1) // 2 - 1, 0), (size * (size + 1) // 2 - 1, 1), (size * (size + 1) // 2 - 1, 2)], 'W'):
        return 1  # White wins
    else:
        return -4  # No winner yet

# Get current player function
def get_current_player(state: State) -> int:
    return state['current_player']

# Get player name function
def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

# Get rewards function
def get_rewards(state: State) -> List[float]:
    if state['winner'] != -4:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get legal actions function
def get_legal_actions(state: State) -> List[Action]:
    board = state['board']
    size = state['size']
    legal_actions = []
    for cell in board:
        if board[cell] == '':
            legal_actions.append(str(cell))
    return legal_actions

# Get observations function
def get_observations(state: State) -> List[PlayerObservation]:
    board = state['board']
    size = state['size']
    observations = []
    for player_id in [0, 1]:
        observation = {}
        for cell in board:
            if board[cell] == '':
                observation[cell] = ''
            elif board[cell] == 'B':
                observation[cell] = 'Black'
            else:
                observation[cell] = 'White'
        observations.append(observation)
    return observations