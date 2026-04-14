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

# Helper function to generate random coordinates within the 4x4 grid
def random_coordinates():
    return random.randint(0, 3), random.randint(0, 3)

# Required Functions
def get_initial_state() -> State:
    # Initial state setup
    p0_loc = random_coordinates()
    p1_loc = (3, 3)
    return {
        "p0_loc": p0_loc,
        "p1_loc": p1_loc,
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    # Apply the action to the state
    new_state = state.copy()
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p0_loc"] = (row, col)
        new_state["turn_count"] += 1
        new_state["current_player"] = 1
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1_loc"] = (row, col)
        new_state["turn_count"] += 1
        new_state["current_player"] = 0
    
    return new_state

def get_current_player(state: State) -> int:
    # Return the current player
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    # Return the name of the player
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    # Determine the rewards based on the game rules
    if state["game_over"]:
        if state["current_player"] == 0:
            return [-1.0, 1.0]
        else:
            return [1.0, -1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    # Get legal actions for the current state
    if state["game_over"]:
        return []
    else:
        current_player = state["current_player"]
        legal_actions = ["Up", "Down", "Left", "Right", "Stay"]
        if current_player == 0:
            # Player 0 can only move to its own quadrant
            if state["p0_loc"][0] == 0 and state["p0_loc"][1] == 0:
                legal_actions.remove("Up")
            if state["p0_loc"][0] == 0 and state["p0_loc"][1] == 3:
                legal_actions.remove("Down")
            if state["p0_loc"][0] == 3 and state["p0_loc"][1] == 0:
                legal_actions.remove("Left")
            if state["p0_loc"][0] == 3 and state["p0_loc"][1] == 3:
                legal_actions.remove("Right")
        else:
            # Player 1 can only move to its own quadrant
            if state["p1_loc"][0] == 0 and state["p1_loc"][1] == 0:
                legal_actions.remove("Up")
            if state["p1_loc"][0] == 0 and state["p1_loc"][1] == 3:
                legal_actions.remove("Down")
            if state["p1_loc"][0] == 3 and state["p1_loc"][1] == 0:
                legal_actions.remove("Left")
            if state["p1_loc"][0] == 3 and state["p1_loc"][1] == 3:
                legal_actions.remove("Right")
        return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    # Get the observations for each player
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    p0_quadrant = get_quadrant(p0_loc)
    p1_quadrant = get_quadrant(p1_loc)
    p0_obs = {"my_loc": p0_loc, "opponent_quadrant": p1_quadrant}
    p1_obs = {"my_loc": p1_loc, "opponent_quadrant": p0_quadrant}
    return [p0_obs, p1_obs]

def get_quadrant(loc: tuple[int, int]) -> str:
    # Determine the quadrant of a given location
    if loc[0] == 0 and loc[1] == 0:
        return "Q1"
    elif loc[0] == 0 and loc[1] == 3:
        return "Q2"
    elif loc[0] == 3 and loc[1] == 0:
        return "Q3"
    elif loc[0] == 3 and loc[1] == 3:
        return "Q4"

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # Resample a valid sequence of actions
    # This function would need to be implemented based on the specific game dynamics
    # For simplicity, we'll just return a fixed sequence of actions
    if player_id == 0:
        return ["place_p0:0,0", "place_p1:3,3", "Right", "Up", "Down", "Left", "Right", "Up"]
    else:
        return ["place_p1:3,3", "place_p0:0,0", "Right", "Up", "Down", "Left", "Right", "Up"]

# Example usage
initial_state = get_initial_state()
print("Initial State:", initial_state)

# Simulate a game run
obs_action_history = [("{'my_loc': (0, 0), 'opponent_quadrant': 'Bottom-Right'}", None),
                      ("{'my_loc': (0, 1), 'opponent_quadrant': 'Top-Left'}", "Right"),
                      ("{'my_loc': (0, 1), 'opponent_quadrant': 'Bottom-Right'}", "Down"),
                      ("{'my_loc': (1, 1), 'opponent_quadrant': 'Top-Left'}", "Left"),
                      ("{'my_loc': (1, 2), 'opponent_quadrant': 'Top-Right'}", "Up"),
                      ("{'my_loc': (1, 2), 'opponent_quadrant': 'Top-Right'}", "Up")]

resampled_actions = resample_history(obs_action_history, 1)
for action in resampled_actions:
    print(f"Resampled Action: {action}")