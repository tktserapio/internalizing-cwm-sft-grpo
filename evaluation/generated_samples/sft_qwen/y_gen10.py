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

# Helper function to check if a move connects all three sides
def is_winner(state: State, player: int) -> bool:
    # Extract the board from the state
    board = state['board']
    
    # Check if the player's stones form a connected path to all three sides
    def is_connected_to_all_sides(board, player_color):
        # Function to check if a given cell is connected to all sides
        def is_connected(cell, board, player_color):
            neighbors = [(cell[0]-1, cell[1]), (cell[0]+1, cell[1]), (cell[0], cell[1]-1), (cell[0], cell[1]+1)]
            for neighbor in neighbors:
                if neighbor in board and board[neighbor]['color'] == player_color:
                    return True
            return False
        
        # Check each side
        for side in ['A', 'B', 'C']:
            if side not in board:
                continue
            start_cell = board[side][0]
            if not is_connected(start_cell, board, player_color):
                return False
        return True
    
    # Check if the opponent's stones form a connected path to all three sides
    def is_opponent_winner(board, opponent_color):
        for side in ['A', 'B', 'C']:
            if side not in board:
                continue
            start_cell = board[side][0]
            if is_connected(start_cell, board, opponent_color):
                return True
        return False
    
    # Determine the player's color
    player_color = 'W' if player == 0 else 'B'
    
    # Check if the player's stones form a winner
    if is_connected_to_all_sides(board, player_color):
        return True
    
    # Check if the opponent's stones form a winner
    if is_opponent_winner(board, 'W' if player == 1 else 'B'):
        return True
    
    return False

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {},
        'turn': 0,
        'size': 4,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action string to coordinates
    row, col = map(int, action.split(','))
    
    # Update the board
    board = state['board']
    board[f'{row},{col}'] = {'color': 'W' if state['turn'] == 0 else 'B'}
    
    # Swap turn
    state['turn'] = 1 - state['turn']
    
    # Check if the move results in a win
    if is_winner(state, state['turn']):
        state['winner'] = state['turn']
    
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['turn']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'White' if player_id == 0 else 'Black'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None:
        return []
    
    board = state['board']
    legal_actions = []
    for row in range(state['size']):
        for col in range(state['size']):
            if f'{row},{col}' not in board:
                legal_actions.append(f'{row},{col}')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    for player_id in [0, 1]:
        obs = {}
        for cell in board:
            if board[cell]['color'] == 'W' if player_id == 0 else 'B':
                obs[cell] = board[cell]
        observations.append(obs)
    return observations