import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to generate random coordinates within the quadrant
def random_quadrant_coordinates():
    row = random.randint(0, 3)
    col = random.randint(0, 3)
    while (row, col) not in [(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 0), (2, 1), (3, 0), (3, 1), (2, 2), (2, 3), (3, 2), (3, 3)]:
        row = random.randint(0, 3)
        col = random.randint(0, 3)
    return row, col

# Required Functions
def get_initial_state() -> State:
    # Initial state setup
    p0_row, p0_col = random_quadrant_coordinates()
    p1_row, p1_col = random_quadrant_coordinates()
    return {
        "p0_loc": (p0_row, p0_col),
        "p1_loc": (p1_row, p1_col),
        "p0_quadrant": get_quadrant(p0_row, p0_col),
        "p1_quadrant": get_quadrant(p1_row, p1_col),
        "turn_count": 0,
        "p0_points": 0,
        "p1_points": 0
    }

def get_quadrant(row, col):
    if row == 0 and col < 2:
        return "Q1"
    elif row == 0 and col >= 2:
        return "Q2"
    elif row == 1 and col < 2:
        return "Q3"
    else:
        return "Q4"

def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    p0_loc = new_state["p0_loc"]
    p1_loc = new_state["p1_loc"]
    
    if action == "place_p0:<row>,<col>":
        new_state["p0_loc"] = eval(action.split(":")[1])
        new_state["p0_quadrant"] = get_quadrant(new_state["p0_loc"][0], new_state["p0_loc"][1])
    elif action == "place_p1:<row>,<col>":
        new_state["p1_loc"] = eval(action.split(":")[1])
        new_state["p1_quadrant"] = get_quadrant(new_state["p1_loc"][0], new_state["p1_loc"][1])
    else:
        if action == "Up":
            new_state["p0_loc"] = (p0_loc[0] - 1, p0_loc[1])
            new_state["p1_loc"] = (p1_loc[0] - 1, p1_loc[1])
        elif action == "Down":
            new_state["p0_loc"] = (p0_loc[0] + 1, p0_loc[1])
            new_state["p1_loc"] = (p1_loc[0] + 1, p1_loc[1])
        elif action == "Left":
            new_state["p0_loc"] = (p0_loc[0], p0_loc[1] - 1)
            new_state["p1_loc"] = (p1_loc[0], p1_loc[1] - 1)
        elif action == "Right":
            new_state["p0_loc"] = (p0_loc[0], p0_loc[1] + 1)
            new_state["p1_loc"] = (p1_loc[0], p1_loc[1] + 1)
        elif action == "Stay":
            pass
    
    new_state["turn_count"] += 1
    return new_state

def get_current_player(state: State) -> int:
    if state["p0_loc"] == state["p1_loc"]:
        return -4  # Game over
    else:
        return 0 if state["p0_loc"] != state["p1_loc"] else -1

def get_player_name(player_id: int) -> str:
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> list[float]:
    if state["turn_count"] > 20:
        return [0.0, 0.0]  # Draw
    elif state["p0_loc"] == state["p1_loc"]:
        return [-1.0, 1.0]  # Player 0 loses, Player 1 wins
    else:
        return [0.0, 0.0]  # Not a terminal state yet

def get_legal_actions(state: State) -> list[Action]:
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    p0_quadrant = state["p0_quadrant"]
    p1_quadrant = state["p1_quadrant"]
    
    if state["turn_count"] <= 20:
        if p0_loc == p1_loc:
            return []
        else:
            legal_actions = ["Up", "Down", "Left", "Right", "Stay"]
            if p0_quadrant == "Q1":
                legal_actions.remove("Up")
            if p0_quadrant == "Q2":
                legal_actions.remove("Left")
            if p0_quadrant == "Q3":
                legal_actions.remove("Down")
            if p0_quadrant == "Q4":
                legal_actions.remove("Right")
            if p1_quadrant == "Q1":
                legal_actions.remove("Down")
            if p1_quadrant == "Q2":
                legal_actions.remove("Right")
            if p1_quadrant == "Q3":
                legal_actions.remove("Up")
            if p1_quadrant == "Q4":
                legal_actions.remove("Left")
            return legal_actions
    else:
        return []

def get_observations(state: State) -> list[PlayerObservation]:
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    p0_quadrant = state["p0_quadrant"]
    p1_quadrant = state["p1_quadrant"]
    
    p0_obs = {
        "My Loc": p0_loc,
        "Opponent Quadrant": p1_quadrant
    }
    p1_obs = {
        "My Loc": p1_loc,
        "Opponent Quadrant": p0_quadrant
    }
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to be implemented based on the specific rules of the game.
    # For simplicity, we'll just return a random action from the legal actions.
    legal_actions = get_legal_actions(resample_history.get_initial_state())
    return [random.choice(legal_actions)]