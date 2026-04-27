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

# Helper function to generate a unique key for each cell
def get_cell_key(row: int, col: int) -> str:
    return f"{row},{col}"

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initialize the board as an empty dictionary
    return {get_cell_key(row, col): None for row in range(6) for col in range(6)}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action string to row and col
    row, col = map(int, action.split(","))
    # Check if the action is valid
    if state.get(get_cell_key(row, col)) is None:
        state[get_cell_key(row, col)] = "x"  # Player 'x' places 'x'
        return state
    elif state.get(get_cell_key(row, col)) == "x":
        state[get_cell_key(row, col)] = "o"  # Player 'o' places 'o'
        return state
    else:
        raise ValueError("Cell already occupied")

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Track the player's turn using a counter
    player_turn = 0
    for cell in state.values():
        if cell == "x":
            player_turn = 0
            break
        elif cell == "o":
            player_turn = 1
            break
    # If all cells are filled, it's a draw
    if len(state) == 36:
        return -4
    return player_turn

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return "Player x" if player_id == 0 else "Player o"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # Calculate the number of 'x' and 'o' marks
    x_count = sum(cell == "x" for cell in state.values())
    o_count = sum(cell == "o" for cell in state.values())
    # Determine the winner or draw condition
    if x_count > o_count:
        return [1.0, 0.0]
    elif o_count > x_count:
        return [0.0, 1.0]
    else:
        return [0.5, 0.5]  # Draw condition

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Generate all possible actions
    actions = []
    for row in range(6):
        for col in range(6):
            if state.get(get_cell_key(row, col)) is None:
                actions.append(get_cell_key(row, col))
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Create observations for each player
    player_0_obs = {}
    player_1_obs = {}
    for cell, mark in state.items():
        row, col = map(int, cell.split(","))
        if mark == "x":
            player_0_obs[cell] = 1
            player_1_obs[cell] = 0
        elif mark == "o":
            player_0_obs[cell] = 0
            player_1_obs[cell] = 1
    return [player_0_obs, player_1_obs]