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

# Helper function to convert coordinates to action strings
def coord_to_action(coord: Tuple[int, int]) -> Action:
    return f"{coord[0]},{coord[1]}"

# Initial state of the game
def get_initial_state() -> State:
    # Initialize the board as a dictionary with coordinates as keys and None as values
    board_size = 4
    initial_board = {(x, y): None for x in range(board_size + 1) for y in range(board_size - x)}
    return {
        "board": initial_board,
        "current_player": 0,  # Player 0 starts
        "winner": None,
        "turn": 0
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    x, y = map(int, action.split(","))
    # Update the board state
    state["board"][(x, y)] = state["current_player"]
    # Switch the current player
    state["current_player"] = (state["current_player"] + 1) % 2
    # Increment the turn counter
    state["turn"] += 1
    return state

# Get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return "Black" if player_id == 0 else "White"

# Get rewards
def get_rewards(state: State) -> List[float]:
    # Check if the game is over
    if state["winner"]:
        return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    # Get the current player's stones' positions
    current_player_stones = [(x, y) for x, y in state["board"].items() if y == state["current_player"]]
    # Generate possible moves
    legal_moves = []
    for stone in current_player_stones:
        # Check horizontal moves
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_x, next_y = stone[0] + dx, stone[1] + dy
            if (next_x, next_y) in state["board"] and state["board"][next_x, next_y] is None:
                legal_moves.append(coord_to_action((next_x, next_y)))
        # Check diagonal moves
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            next_x, next_y = stone[0] + dx, stone[1] + dy
            if (next_x, next_y) in state["board"] and state["board"][next_x, next_y] is None:
                legal_moves.append(coord_to_action((next_x, next_y)))
    return legal_moves

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    # Observations are the same for both players in a perfect information game
    board_representation = [[None for _ in range(4)] for _ in range(4)]
    for coord, value in state["board"].items():
        board_representation[coord[0]][coord[1]] = value
    return [
        {
            "board": board_representation,
            "legal_actions": get_legal_actions(state),
            "current_player": get_current_player(state),
            "player_name": get_player_name(state["current_player"])
        }
    ]

# Example usage
initial_state = get_initial_state()
print("Initial State:", initial_state)

# Simulate a few moves
state = apply_action(initial_state, "0,0")  # Black plays cell 0
state = apply_action(state, "1,0")  # White plays cell 1
state = apply_action(state, "2,0")  # Black plays cell 2
state = apply_action(state, "3,0")  # White plays cell 3
state = apply_action(state, "3,1")  # Black plays cell 3 (corner)
state = apply_action(state, "3,2")  # White plays cell 4 (corner)

# Print the final state
print("Final State:", state)

# Get rewards
rewards = get_rewards(state)
print("Rewards:", rewards)