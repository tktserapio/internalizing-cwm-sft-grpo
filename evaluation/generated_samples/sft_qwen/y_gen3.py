import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import itertools

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to initialize the board
def init_board(size: int) -> State:
    """Initialize the board state with given size."""
    board = {}
    for i in range(1, size + 1):
        for j in range(i):
            board[f"{i},{j}"] = " "
    return board

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    size = 4
    board = init_board(size)
    return board

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_state[action] = "B" if action[0] == '0' else "W"
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    # Assuming Black starts first, we can track the turn count to determine the current player
    turn_count = sum(cell.count("B") for cell in state.values())
    if turn_count % 2 == 0:
        return 1  # White's turn
    else:
        return 0  # Black's turn

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    # In this simple implementation, we don't track rewards, so we return [0.0, 0.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    # Legal actions are all empty cells
    return [cell for cell in state.keys() if state[cell] == " "]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    # Observations are the same for both players
    observation = {"board": state}
    return [observation, observation]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Apply some actions
    actions = ["0,0", "0,1", "1,0", "1,1", "2,0", "2,1", "2,2"]
    for action in actions:
        initial_state = apply_action(initial_state, action)
        print(f"After applying action {action}:")
        print(initial_state)
        print(f"Current Player: {get_player_name(get_current_player(initial_state))}")
        print(f"Legal Actions: {get_legal_actions(initial_state)}")
        print(f"Rewards: {get_rewards(initial_state)}")
        print(f"Observations: {get_observations(initial_state)}")
        print("\n")