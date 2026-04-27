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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {
            'A1': None,
            'A2': None,
            'A3': None,
            'A4': None,
            'B1': None,
            'B2': None,
            'B3': None,
            'C1': None,
            'C2': None,
            'C3': None
        },
        'current_player': 0  # Player 0 is Black
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    cell_id = action
    new_state['board'][cell_id] = new_state['current_player'] + 1  # 0 for Black, 1 for White
    new_state['current_player'] = (new_state['current_player'] + 1) % 2  # Switch player
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In a perfect information game like Y, there's no need to track running rewards.
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []
    
    for cell_id, value in board.items():
        if value is None:
            legal_actions.append(cell_id)
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    board = state['board']
    current_player = state['current_player']
    
    for cell_id, value in board.items():
        observation = {'cell_id': cell_id, 'value': value}
        observations.append(observation)
    
    return [observations, observations]

# Helper function to check if a move connects all three sides
def is_winner(state: State) -> bool:
    board = state['board']
    current_player = state['current_player']
    
    # Check if the current player can form a connection
    def is_connected(board, player_id, cell_id):
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        visited = set()
        
        def dfs(x, y):
            if (x, y) in visited:
                return False
            visited.add((x, y))
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(board) and 0 <= ny < len(board) and board.get(f'A{nx}{ny}') == player_id:
                    if dfs(nx, ny):
                        return True
            return False
        
        return dfs(cell_id[0], int(cell_id[1:]) - 1)
    
    # Check all corners
    if is_connected(board, current_player, 'A1') or is_connected(board, current_player, 'A3') or is_connected(board, current_player, 'C1'):
        return True
    
    # Check all sides
    if is_connected(board, current_player, 'A1') or is_connected(board, current_player, 'A3') or is_connected(board, current_player, 'C1'):
        return True
    
    return False

# Example usage
initial_state = get_initial_state()
print("Initial State:", initial_state)

# Apply a few moves
state_after_move1 = apply_action(initial_state, '4')
state_after_move2 = apply_action(state_after_move1, '1')
state_after_move3 = apply_action(state_after_move2, '7')
state_after_move4 = apply_action(state_after_move3, '5')
state_after_move5 = apply_action(state_after_move4, '3')
state_after_move6 = apply_action(state_after_move5, '8')

# Check if a player has won
winner = is_winner(state_after_move6)
print("Winner:", 'Black' if winner else 'No Winner')