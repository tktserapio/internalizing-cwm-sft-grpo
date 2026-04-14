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
        'current_player': 0  # Black starts
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    cell_id = action
    new_state['board'][cell_id] = new_state['current_player'] + 1  # Player's color
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
    # In a perfect information game like Y, there are no running rewards until the game ends.
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    legal_actions = []
    for cell_id, value in board.items():
        if value is None:
            legal_actions.append(cell_id)
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    board = state['board']
    for cell_id, value in board.items():
        observation = {'cell': cell_id, 'color': value}
        observations.append(observation)
    return [observations, observations]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Apply some actions
    actions = ["A1", "A2", "B1", "C1", "A3", "B2"]
    for action in actions:
        new_state = apply_action(initial_state, action)
        print(f"After applying action {action}:")
        print(new_state)
        
    # Get current player
    current_player = get_current_player(new_state)
    print(f"Current Player: {get_player_name(current_player)}")
    
    # Get legal actions
    legal_actions = get_legal_actions(new_state)
    print(f"Legal Actions: {legal_actions}")
    
    # Get observations
    observations = get_observations(new_state)
    print(f"Observations: {observations}")