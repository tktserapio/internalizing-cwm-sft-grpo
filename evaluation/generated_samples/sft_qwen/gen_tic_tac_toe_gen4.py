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
    row, col = map(int, action.split(','))
    if row < 0 or row > 5 or col < 0 or col > 5 or state.get(f'{row},{col}') is not None:
        return False
    return True

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        f"{i},{j}": None for i in range(6) for j in range(6)
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    if not is_valid_action(action, state):
        raise ValueError("Invalid action")
    
    state[action] = 'x' if state[action] is None else 'o'
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    # Assuming 'x' starts the game
    if state.get('0,0', None) == 'x':
        return 0
    elif state.get('0,0', None) == 'o':
        return 1
    else:
        return -4  # Terminal state

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Player 1' if player_id == 0 else 'Player 2'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if get_current_player(state) == -4:
        return [0.0, 0.0]  # Game is over, no rewards
    else:
        return [0.0, 0.0]  # No rewards yet

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for row in range(6):
        for col in range(6):
            if state.get(f"{row},{col}", None) is None:
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {k: v for k, v in state.items() if v is None}
    player_1_obs = {k: v for k, v in state.items() if v is None}
    return [player_0_obs, player_1_obs]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    action = "0,0"
    new_state = apply_action(initial_state, action)
    print("After applying action:", action, "New State:", new_state)
    
    current_player = get_current_player(new_state)
    print("Current Player:", get_player_name(current_player))
    
    legal_actions = get_legal_actions(new_state)
    print("Legal Actions:", legal_actions)
    
    rewards = get_rewards(new_state)
    print("Rewards:", rewards)
    
    observations = get_observations(new_state)
    print("Observations:", observations)