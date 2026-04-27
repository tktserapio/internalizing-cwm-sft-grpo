import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to generate a board representation
def generate_board(size: int) -> State:
    board = {}
    for i in range(1, size + 1):
        for j in range(1, size + 1):
            if i == j:
                board[f"{chr(64 + i)}{j}"] = {"color": None, "type": "corner"}
            elif i + j == size + 1:
                board[f"{chr(64 + i)}{j}"] = {"color": None, "type": "corner"}
            else:
                board[f"{chr(64 + i)}{j}"] = {"color": None, "type": "empty"}
    return board

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    size = 4
    board = generate_board(size)
    return {
        "board": board,
        "current_player": 0,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    row, col = map(int, action.split(","))
    cell_id = f"{chr(64 + row + 1)}{col + 1}"
    
    # Check if the cell is empty
    if new_state["board"][cell_id]["color"] is not None:
        raise ValueError("Cell is already occupied.")
    
    # Update the board with the new action
    new_state["board"][cell_id]["color"] = new_state["current_player"]
    
    # Determine the winner
    if check_winner(new_state):
        new_state["winner"] = new_state["current_player"]
    
    # Switch the current player
    new_state["current_player"] = 1 - new_state["current_player"]
    
    return new_state

def check_winner(state: State) -> bool:
    """
    Checks if there's a winner based on the current state of the board.
    """
    board = state["board"]
    colors = ["B", "W"]
    
    for color in colors:
        for side in ["A", "B", "C"]:
            for cell in board.keys():
                if board[cell]["color"] == color:
                    if all(board[cell1]["color"] == color for cell1 in board[cell]["connections"]):
                        return True
    return False

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] is None:
        return [0.0, 0.0]
    elif state["current_player"] == 0:
        return [1.0, 0.0]
    else:
        return [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state["board"]
    current_player = state["current_player"]
    legal_actions = []
    
    for cell_id, cell_info in board.items():
        if cell_info["color"] is None:
            legal_actions.append(cell_id)
    
    if len(legal_actions) > 0:
        return legal_actions
    else:
        return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state["board"]
    observations = []
    
    for player_id in [0, 1]:
        player_observations = {}
        for cell_id, cell_info in board.items():
            if cell_info["color"] is None:
                continue
            if cell_info["color"] == "B":
                player = "Black"
            else:
                player = "White"
            if player_id == 0:
                player = "Black"
            else:
                player = "White"
            
            if player not in player_observations:
                player_observations[player] = []
            
            player_observations[player].append(cell_id)
        
        observations.append(player_observations)
    
    return observations