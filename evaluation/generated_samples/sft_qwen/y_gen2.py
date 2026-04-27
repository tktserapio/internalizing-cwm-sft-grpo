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
    return f"{coord[0]},{coord[1]}"

# Initial state of the game
def get_initial_state() -> State:
    # Initialize the board with empty cells
    board = {
        "A1": None,
        "A2": None,
        "A3": None,
        "A4": None,
        "B1": None,
        "B2": None,
        "B3": None,
        "C1": None,
        "C2": None,
        "C3": None
    }
    # Set the starting player to Black (0)
    return {"board": board, "current_player": 0}

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    x, y = map(int, action.split(","))
    # Get the current player
    current_player = state["current_player"]
    # Check if the action is valid
    if state["board"].get(f"A{x}") == current_player or state["board"].get(f"B{x}") == current_player or state["board"].get(f"C{x}") == current_player:
        # Place the stone on the board
        state["board"][f"A{x}"] = current_player
        # Switch the current player
        state["current_player"] = 1 if current_player == 0 else 0
        # Return the new state
        return state
    else:
        raise ValueError("Invalid move")

# Get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return "Black" if player_id == 0 else "White"

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    # In this simple implementation, we assume the game ends when the board is full
    # and the last player to place a stone wins.
    if len(state["board"]) == 10:
        return [1.0, 0.0] if state["current_player"] == 0 else [0.0, 1.0]
    else:
        return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    # Legal actions are all cells that are empty and belong to the current player
    board = state["board"]
    current_player = state["current_player"]
    legal_actions = []
    for cell in board.keys():
        if board[cell] is None and (cell.startswith("A") or cell.startswith("B")):
            legal_actions.append(coord_to_action((int(cell[1]), int(cell[2]))))
    return legal_actions

# Get the observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    # Observations are the same for both players in a perfect information game
    board = state["board"]
    current_player = state["current_player"]
    observation = {}
    for cell in board.keys():
        if board[cell] is not None:
            observation[cell] = board[cell]
    return [observation, observation]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Simulate a few moves
    state = apply_action(initial_state, "0,0")
    print("After Move 1:", state)
    
    state = apply_action(state, "1,0")
    print("After Move 2:", state)
    
    state = apply_action(state, "2,0")
    print("After Move 3:", state)
    
    state = apply_action(state, "3,0")
    print("After Move 4:", state)
    
    state = apply_action(state, "4,0")
    print("After Move 5:", state)
    
    state = apply_action(state, "5,0")
    print("After Move 6:", state)
    
    state = apply_action(state, "6,0")
    print("After Move 7:", state)
    
    print("Final State Rewards:", get_rewards(state))
    print("Legal Actions:", get_legal_actions(state))
    print("Observations:", get_observations(state))