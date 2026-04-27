import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to convert action string to board indices
def action_to_indices(action: Action) -> Tuple[int, int]:
    row, col = map(int, action.split(','))
    return row, col

# Initialize the game state
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board_size': 4,  # Size of the board (4x4 triangular grid)
        'board': [[None for _ in range(i + 1)] for i in range(4)],  # Triangular board
        'current_player': 0,  # 0 for Black, 1 for White
        'winner': None  # No winner initially
    }

# Apply an action to the game state
def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        'board_size': state['board_size'],
        'board': [row[:] for row in state['board']],  # Deep copy of the board
        'current_player': state['current_player'],
        'winner': state['winner']
    }
    
    row, col = action_to_indices(action)
    new_state['board'][row][col] = new_state['current_player']
    
    # Check for a winner
    if check_winner(new_state, row, col):
        new_state['winner'] = new_state['current_player']
    
    # Switch player
    new_state['current_player'] = 1 - new_state['current_player']
    
    return new_state

# Determine the current player
def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['winner'] is not None:
        return -4
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

# Get the rewards for the players
def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['winner'] is None:
        return [0.0, 0.0]
    return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None:
        return []
    
    legal_actions = []
    for row in range(state['board_size']):
        for col in range(row + 1):
            if state['board'][row][col] is None:
                legal_actions.append(f"{row},{col}")
    return legal_actions

# Get observations for the players
def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

# Helper function to check if the current player has won
def check_winner(state: State, row: int, col: int) -> bool:
    """Check if the current player has formed a winning connection."""
    player = state['current_player']
    board = state['board']
    size = state['board_size']
    
    # Directions for hexagonal adjacency
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
    
    # Perform a depth-first search (DFS) to check connectivity
    def dfs(r: int, c: int, visited: set) -> set:
        if (r, c) in visited or board[r][c] != player:
            return visited
        visited.add((r, c))
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc <= nr:
                dfs(nr, nc, visited)
        return visited
    
    # Check if the player's stones connect all three sides
    visited = dfs(row, col, set())
    sides_touched = set()
    for r, c in visited:
        if r == 0:
            sides_touched.add('A')
        if c == 0:
            sides_touched.add('B')
        if r == size - 1:
            sides_touched.add('C')
    
    return len(sides_touched) == 3