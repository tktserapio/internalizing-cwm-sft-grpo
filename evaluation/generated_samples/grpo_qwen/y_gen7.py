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

# Required Functions
def get_initial_state() -> State:
    # Initial state with an empty board
    return {
        "board": {},
        "current_player": 0,
        "winner": -4,
        "turn": 0
    }

def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinates
    coords = action.split(',')
    x, y = int(coords[0]), int(coords[1])
    
    # Check if the action is valid
    if x < 0 or y < 0 or x >= 4 or y >= 4:
        raise ValueError("Invalid action")
    
    # Update the board state
    state["board"][f"A{x+1}"] = state["current_player"]
    state["board"][f"B{x+1}"] = state["current_player"]
    state["board"][f"C{x+1}"] = state["current_player"]
    
    # Switch the current player
    state["current_player"] = 1 - state["current_player"]
    state["turn"] += 1
    
    # Determine the winner
    if check_winner(state):
        state["winner"] = state["current_player"]
    
    return state

def check_winner(state: State) -> bool:
    # Check all possible winning conditions
    for side in ["A", "B", "C"]:
        for i in range(1, 5):
            if f"{side}{i}" in state["board"] and f"{side}{i+1}" in state["board"] and f"{side}{i+2}" in state["board"]:
                return True
    return False

def get_current_player(state: State) -> int:
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    return "Black" if player_id == 0 else "White"

def get_rewards(state: State) -> List[float]:
    if state["winner"] != -4:
        return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    for x in range(4):
        for y in range(4):
            if f"A{x+1}" not in state["board"] and f"B{x+1}" not in state["board"] and f"C{x+1}" not in state["board"]:
                legal_actions.append(coord_to_action((x, y)))
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    observations = []
    for player_id in [0, 1]:
        observation = {}
        for cell in state["board"]:
            if state["board"][cell] == player_id:
                observation[cell] = 1
            else:
                observation[cell] = 0
        observations.append(observation)
    return observations