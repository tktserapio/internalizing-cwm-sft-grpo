import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
PLAYER_BLACK = 0
PLAYER_WHITE = 1
EMPTY_CELL = -1
BOARD_SIZE = 4  # Size of the board (4 cells per edge for a size-4 board)

# Helper function to convert action string to board coordinates
def action_to_coords(action: Action) -> Tuple[int, int]:
    return tuple(map(int, action.split(',')))

# Helper function to convert board coordinates to action string
def coords_to_action(row: int, col: int) -> Action:
    return f"{row},{col}"

# Initialize the game state
def get_initial_state() -> State:
    return {
        "board": [[EMPTY_CELL for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        "current_player": PLAYER_BLACK,
        "turn_count": 0,
        "winner": None
    }

# Apply an action to the state and return the new state
def apply_action(state: State, action: Action) -> State:
    new_state = {
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "turn_count": state["turn_count"] + 1,
        "winner": state["winner"]
    }
    
    row, col = action_to_coords(action)
    new_state["board"][row][col] = state["current_player"]
    
    # Check for a winner after the move
    if check_winner(new_state["board"], state["current_player"]):
        new_state["winner"] = state["current_player"]
    
    # Switch player
    new_state["current_player"] = 1 - state["current_player"]
    
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    if state["winner"] is not None:
        return -4  # Terminal state
    return state["current_player"]

# Get the player name
def get_player_name(player_id: int) -> str:
    return "Black" if player_id == PLAYER_BLACK else "White"

# Get rewards for the players
def get_rewards(state: State) -> List[float]:
    if state["winner"] is None:
        return [0.0, 0.0]
    elif state["winner"] == PLAYER_BLACK:
        return [1.0, 0.0]
    else:
        return [0.0, 1.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["winner"] is not None:
        return []  # No legal actions if the game is over
    
    legal_actions = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if state["board"][row][col] == EMPTY_CELL:
                legal_actions.append(coords_to_action(row, col))
    return legal_actions

# Get observations for the players
def get_observations(state: State) -> List[PlayerObservation]:
    return [state, state]  # Perfect information game

# Check if the current player has won
def check_winner(board: List[List[int]], player: int) -> bool:
    # Implement a connection check algorithm to see if the player has a path connecting all three sides
    # This is a complex task and requires a graph traversal algorithm like DFS or BFS
    # For simplicity, this function is a placeholder and should be implemented with proper logic
    return False  # Placeholder implementation

# Example usage
if __name__ == "__main__":
    state = get_initial_state()
    print("Initial State:", state)
    action = "0,0"
    state = apply_action(state, action)
    print("State after action:", state)