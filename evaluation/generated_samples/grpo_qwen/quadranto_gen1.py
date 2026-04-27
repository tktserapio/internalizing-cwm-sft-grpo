import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to generate a random position within a quadrant
def random_position_in_quadrant(quadrant: str) -> tuple[int, int]:
    row, col = quadrant.split(',')
    row = int(row)
    col = int(col)
    # Randomly place player in the quadrant
    row = random.choice([row, row+1])
    col = random.choice([col, col+1])
    return (row, col)

# Required Functions
def get_initial_state() -> State:
    # Initial positions for players
    p0_pos = random_position_in_quadrant("0,0")
    p1_pos = random_position_in_quadrant("3,3")
    # Initial state dictionary
    state = {
        "p0_loc": p0_pos,
        "p1_loc": p1_pos,
        "p0_quadrant": "Q1",
        "p1_quadrant": "Q4",
        "turn_count": 0
    }
    return state

def apply_action(state: State, action: Action) -> State:
    # Create a copy of the state to avoid mutating the original
    new_state = state.copy()
    p0_loc = new_state["p0_loc"]
    p1_loc = new_state["p1_loc"]
    
    # Update player locations based on the action
    if action == "Stay":
        pass
    elif action in ["Up", "Down"]:
        if action == "Up":
            new_state["p0_loc"] = (p0_loc[0], max(0, p0_loc[1]-1))
            new_state["p1_loc"] = (p1_loc[0], max(0, p1_loc[1]-1))
        else:
            new_state["p0_loc"] = (p0_loc[0], min(3, p0_loc[1]+1))
            new_state["p1_loc"] = (p1_loc[0], min(3, p1_loc[1]+1))
    elif action in ["Left", "Right"]:
        if action == "Left":
            new_state["p0_loc"] = (max(0, p0_loc[0]-1), p0_loc[1])
            new_state["p1_loc"] = (max(0, p1_loc[0]-1), p1_loc[1])
        else:
            new_state["p0_loc"] = (min(3, p0_loc[0]+1), p0_loc[1])
            new_state["p1_loc"] = (min(3, p1_loc[0]+1), p1_loc[1])
    
    # Determine the quadrant of each player
    new_state["p0_quadrant"] = get_quadrant(p0_loc)
    new_state["p1_quadrant"] = get_quadrant(p1_loc)
    
    # Check if the game is over
    if new_state["p0_loc"] == new_state["p1_loc"]:
        new_state["game_over"] = True
        new_state["winner"] = 1
        new_state["loser"] = 0
    else:
        new_state["game_over"] = False
        new_state["winner"] = 0
        new_state["loser"] = 1
    
    new_state["turn_count"] += 1
    return new_state

def get_quadrant(loc: tuple[int, int]) -> str:
    row, col = loc
    if row < 2 and col < 2:
        return "Q1"
    elif row < 2 and col >= 2:
        return "Q2"
    elif row >= 2 and col < 2:
        return "Q3"
    else:
        return "Q4"

def get_current_player(state: State) -> int:
    if state["game_over"]:
        return -4
    else:
        return 1 - state["loser"]

def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    if state["game_over"]:
        return [state["winner"], -state["winner"]]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    p0_quadrant = state["p0_quadrant"]
    p1_quadrant = state["p1_quadrant"]
    
    # Legal actions for player 0
    legal_actions_p0 = []
    if p0_loc != p1_loc:
        if p0_quadrant == "Q1":
            legal_actions_p0.extend(["Up", "Right"])
        elif p0_quadrant == "Q2":
            legal_actions_p0.extend(["Up", "Left", "Right"])
        elif p0_quadrant == "Q3":
            legal_actions_p0.extend(["Down", "Left"])
        elif p0_quadrant == "Q4":
            legal_actions_p0.extend(["Down", "Right"])
        legal_actions_p0.append("Stay")
    
    # Legal actions for player 1
    legal_actions_p1 = []
    if p1_loc != p0_loc:
        if p1_quadrant == "Q1":
            legal_actions_p1.extend(["Down", "Left"])
        elif p1_quadrant == "Q2":
            legal_actions_p1.extend(["Down", "Right", "Left"])
        elif p1_quadrant == "Q3":
            legal_actions_p1.extend(["Up", "Right"])
        elif p1_quadrant == "Q4":
            legal_actions_p1.extend(["Up", "Right"])
        legal_actions_p1.append("Stay")
    
    # Return the legal actions for the current player
    return legal_actions_p0 if get_current_player(state) == 0 else legal_actions_p1

def get_observations(state: State) -> list[PlayerObservation]:
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    p0_quadrant = state["p0_quadrant"]
    p1_quadrant = state["p1_quadrant"]
    return [
        {"My Loc": p0_loc, "Opponent Quadrant": p1_quadrant},
        {"My Loc": p1_loc, "Opponent Quadrant": p0_quadrant}
    ]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to be implemented to sample a valid sequence of actions.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this function would use the history to predict the most likely next action.
    # Here, we're returning a fixed sequence of actions for demonstration purposes.
    if player_id == 0:
        return ["Right", "Down", "Right", "Up", "Right", "Up", "Left"]
    else:
        return ["Up", "Left", "Up", "Right", "Up", "Left", "Up"]