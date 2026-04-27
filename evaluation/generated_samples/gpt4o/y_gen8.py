import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [[None for _ in range(4)] for _ in range(4)],  # 4x4 board for simplicity
        'current_player': 0,  # 0 for Black, 1 for White
        'winner': None  # None if the game is ongoing
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        'board': [row[:] for row in state['board']],
        'current_player': state['current_player'],
        'winner': state['winner']
    }
    
    # Parse the action
    row, col = map(int, action.split(','))
    
    # Place the stone
    if new_state['board'][row][col] is None:
        new_state['board'][row][col] = new_state['current_player']
    else:
        raise ValueError("Invalid action: Cell is already occupied.")
    
    # Check for a winner
    if check_winner(new_state['board'], new_state['current_player']):
        new_state['winner'] = new_state['current_player']
    
    # Switch player
    new_state['current_player'] = 1 - state['current_player']
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state['winner'] is not None:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state['winner'] is None:
        return [0.0, 0.0]
    return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None:
        return []
    
    legal_actions = []
    for row in range(4):
        for col in range(4):
            if state['board'][row][col] is None:
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [{'board': state['board'], 'current_player': state['current_player']}] * 2

def check_winner(board: List[List[int]], player: int) -> bool:
    """Check if the current player has won the game."""
    # This function should implement the logic to check if a player has connected all three sides.
    # For simplicity, this is a placeholder. Implement the actual connection-checking logic here.
    return False

# Note: The check_winner function needs to be implemented with the logic to check for a winning connection.