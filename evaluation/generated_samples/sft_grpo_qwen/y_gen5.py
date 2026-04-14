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
    """
    Returns the initial game state before any actions are taken.
    The initial state should be an empty dictionary.
    """
    return {}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action string to coordinates
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if row < 0 or row >= 4 or col < 0 or col >= 5:
        raise ValueError("Invalid action")

    # Create a deep copy of the state to avoid mutating the original state
    new_state = state.copy()

    # Update the state with the new action
    new_state[f"{row},{col}"] = "stone"

    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Count the number of 'stone' keys in the state
    num_stones = sum(1 for value in state.values() if value == "stone")
    
    # Determine the current player based on the number of stones
    if num_stones % 2 == 0:
        return 0  # White's turn
    else:
        return 1  # Black's turn

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return "White" if player_id == 0 else "Black"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # In a perfect information game like Y, there are no running rewards until the game ends.
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Legal actions are all empty cells on the board
    legal_actions = []
    for row in range(4):
        for col in range(5):
            if f"{row},{col}" not in state:
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Observations are the same for both players in a perfect info game
    observation = {"board": state}
    return [observation, observation]