import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to convert coordinates to action string
def coord_to_action(coord: tuple[int, int]) -> Action:
    return f"{coord[0]}, {coord[1]}"

# Required Functions
def get_initial_state() -> State:
    # Initial state with an empty board
    return {
        "board": {},
        "current_player": 0,
        "turn_count": 0,
        "size": 4,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    coords = action.split(',')
    x, y = int(coords[0]), int(coords[1])
    
    # Check if the action is valid
    if x < 0 or x >= state["size"] or y < 0 or y >= state["size"]:
        raise ValueError("Invalid action: coordinates out of bounds")
    
    # Get the current player
    player = state["current_player"]
    
    # Apply the action
    state["board"][f"{x},{y}"] = player
    
    # Update the current player
    state["current_player"] = 1 - player
    
    # Increment the turn count
    state["turn_count"] += 1
    
    # Check for winner
    if check_winner(state):
        state["winner"] = player
    
    return state

def check_winner(state: State) -> bool:
    # Check all possible winning conditions
    for side in ["A", "B", "C"]:
        for cell in state["board"].keys():
            if side in cell:
                # Find the other two cells of the same side
                other_cells = []
                for c in state["board"].keys():
                    if side in c and c != cell:
                        other_cells.append(c)
                
                # Check if all three cells are occupied
                if len(other_cells) == 2 and state["board"][cell] == state["board"][other_cells[0]] == state["board"][other_cells[1]]:
                    return True
    
    return False

def get_current_player(state: State) -> int:
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> list[float]:
    if state["winner"] is not None:
        return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    # Generate all possible actions
    legal_actions = []
    for x in range(state["size"]):
        for y in range(state["size"]):
            if f"{x},{y}" not in state["board"]:
                legal_actions.append(coord_to_action((x, y)))
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    # Observations are identical for both players
    observations = [
        {"board": state["board"], "current_player": state["current_player"], "turn_count": state["turn_count"], "size": state["size"], "winner": state["winner"]},
        {"board": state["board"], "current_player": state["current_player"], "turn_count": state["turn_count"], "size": state["size"], "winner": state["winner"]}
    ]
    return observations