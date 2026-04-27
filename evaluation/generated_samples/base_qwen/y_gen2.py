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

# Helper function to check if a given action is valid
def is_valid_action(action: Action, state: State) -> bool:
    row, col = map(int, action.split(','))  # Convert action string to row and col
    if row < 0 or row >= 10 or col < 0 or col >= 10:
        return False  # Out of bounds
    if state.get(f'{row},{col}') == 'B' or state.get(f'{row},{col}') == 'W':
        return False  # Cell already occupied
    return True

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {
            '1': ' ', '2': ' ', '3': ' ', '4': ' ', '5': ' ', '6': ' ', '7': ' ', '8': ' ', '9': ' ',
            'A': ' ', 'B': ' ', 'C': ' '
        },
        'turn': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    if not is_valid_action(action, state['board']):
        raise ValueError("Invalid action")
    
    row, col = map(int, action.split(','))
    state['board'][f'{row},{col}'] = 'B' if state['turn'] == 0 else 'W'
    state['turn'] = 1 - state['turn']
    state['winner'] = None
    
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['turn']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['winner'] is not None:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    legal_actions = []
    for row in range(10):
        for col in range(10):
            if board.get(f'{row},{col}') == ' ':
                legal_actions.append(f'{row},{col}')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    observations = []
    for player_id in [0, 1]:
        observation = {}
        for key, value in board.items():
            if value == 'B' and player_id == 0:
                observation[key] = 'Black'
            elif value == 'W' and player_id == 1:
                observation[key] = 'White'
            else:
                observation[key] = 'Empty'
        observations.append(observation)
    return observations

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Apply some actions
    state_after_action1 = apply_action(initial_state, "4,4")
    print("After Action 1 (Black):", state_after_action1)
    
    state_after_action2 = apply_action(state_after_action1, "1,1")
    print("After Action 2 (White):", state_after_action2)
    
    # Get current player
    current_player = get_current_player(state_after_action2)
    print("Current Player:", 'Black' if current_player == 0 else 'White')
    
    # Get rewards
    rewards = get_rewards(state_after_action2)
    print("Rewards:", rewards)
    
    # Get legal actions
    legal_actions = get_legal_actions(state_after_action2)
    print("Legal Actions:", legal_actions)
    
    # Get observations
    observations = get_observations(state_after_action2)
    print("Observations:", observations)