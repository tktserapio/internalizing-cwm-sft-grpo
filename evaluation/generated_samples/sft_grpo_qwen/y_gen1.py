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

# Helper function to convert coordinates to action string
def coord_to_action(coord: Tuple[int, int]) -> Action:
    row, col = coord
    return f"{row},{col}"

# Initial state of the game
def get_initial_state() -> State:
    # Initialize the board as an empty dictionary
    return {}

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert the action string to coordinates
    row, col = map(int, action.split(","))
    # Add the action to the state
    state[action] = {"color": "Black"} if row % 2 == 0 else {"color": "White"}
    return state

# Get the current player
def get_current_player(state: State) -> int:
    # Check if the state is terminal
    if len(state) == 0:
        return -4
    # Determine the current player based on the last action
    last_action = max(state.keys())
    if int(last_action.split(",")[0]) % 2 == 0:
        return 0  # Black's turn
    else:
        return 1  # White's turn

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return "Black" if player_id == 0 else "White"

# Get rewards per player
def get_rewards(state: State) -> List[float]:
    # Since this is a perfect information game, there are no meaningful rewards yet
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    # Legal actions are all the keys in the state dictionary
    return list(state.keys())

# Get observations for both players
def get_observations(state: State) -> List[PlayerObservation]:
    # Each player sees the same state
    return [{}, {}]

# Example usage
if __name__ == "__main__":
    # Initialize the game state
    state = get_initial_state()
    
    # Apply some actions
    state = apply_action(state, "0,0")
    state = apply_action(state, "1,1")
    state = apply_action(state, "2,2")
    state = apply_action(state, "3,3")
    state = apply_action(state, "4,4")
    state = apply_action(state, "5,5")
    state = apply_action(state, "6,6")
    state = apply_action(state, "7,7")
    state = apply_action(state, "8,8")
    state = apply_action(state, "9,9")
    
    # Get the current player
    print(f"Current Player: {get_player_name(get_current_player(state))}")
    
    # Get legal actions
    print(f"Legal Actions: {get_legal_actions(state)}")
    
    # Get rewards
    print(f"Rewards: {get_rewards(state)}")
    
    # Get observations
    print(f"Observations: {get_observations(state)}")