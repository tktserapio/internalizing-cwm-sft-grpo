import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    # Initial state setup
    player_0_location = (random.randint(0, 1), random.randint(0, 1))  # Randomly place player 0 in Q1
    player_1_location = (3 - player_0_location[0], 3 - player_0_location[1])  # Randomly place player 1 in Q4
    return {
        "player_0": player_0_location,
        "player_1": player_1_location,
        "turn_count": 0,
        "current_player": 0,
        "quadrant_player_0": "Q1" if player_0_location == (0, 0) else "Q2",
        "quadrant_player_1": "Q4" if player_1_location == (3, 3) else "Q3"
    }

def apply_action(state: State, action: Action) -> State:
    # Apply action to the state
    new_state = state.copy()
    player_id = new_state["current_player"]
    
    if action == "Stay":
        new_state[player_id + "_location"] = new_state[player_id + "_location"]
    elif action in ["Up", "Down", "Left", "Right"]:
        row, col = new_state[f"{player_id}_location"]
        if action == "Up":
            new_state[f"{player_id}_location"] = (row - 1, col)
        elif action == "Down":
            new_state[f"{player_id}_location"] = (row + 1, col)
        elif action == "Left":
            new_state[f"{player_id}_location"] = (row, col - 1)
        elif action == "Right":
            new_state[f"{player_id}_location"] = (row, col + 1)
    
    # Check if the game ended
    opponent_quadrant = new_state["quadrant_player_" + str(1 - player_id)]
    if opponent_quadrant == "Q1" and new_state[f"{player_id}_location"] == (0, 0):
        new_state["game_over"] = True
        new_state["winner"] = player_id
        new_state["loser"] = 1 - player_id
        new_state["reward"] = [1.0, -1.0]
    elif opponent_quadrant == "Q4" and new_state[f"{player_id}_location"] == (3, 3):
        new_state["game_over"] = True
        new_state["winner"] = player_id
        new_state["loser"] = 1 - player_id
        new_state["reward"] = [-1.0, 1.0]
    elif new_state["turn_count"] >= 20:
        new_state["game_over"] = True
        new_state["winner"] = -4
        new_state["loser"] = -4
        new_state["reward"] = [0.0, 0.0]
    
    new_state["turn_count"] += 1
    new_state["current_player"] = 1 - player_id
    
    return new_state

def get_current_player(state: State) -> int:
    # Return the current player
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    # Return the name of the player
    return "Player " + str(player_id)

def get_rewards(state: State) -> List[float]:
    # Return the rewards per player
    return state["reward"]

def get_legal_actions(state: State) -> List[Action]:
    # Return legal actions for current state
    player_id = state["current_player"]
    player_location = state[f"{player_id}_location"]
    quadrant_player_0 = state["quadrant_player_0"]
    quadrant_player_1 = state["quadrant_player_1"]
    
    legal_actions = []
    if quadrant_player_0 == "Q1":
        if player_location == (0, 0):
            legal_actions.append("Stay")
        elif player_location[0] > 0:
            legal_actions.append("Left")
        elif player_location[1] < 1:
            legal_actions.append("Up")
    elif quadrant_player_0 == "Q2":
        if player_location == (1, 1):
            legal_actions.append("Stay")
        elif player_location[0] < 1:
            legal_actions.append("Right")
        elif player_location[1] > 0:
            legal_actions.append("Down")
    
    if quadrant_player_1 == "Q4":
        if player_location == (3, 3):
            legal_actions.append("Stay")
        elif player_location[0] < 3:
            legal_actions.append("Left")
        elif player_location[1] > 2:
            legal_actions.append("Up")
    elif quadrant_player_1 == "Q3":
        if player_location == (2, 2):
            legal_actions.append("Stay")
        elif player_location[0] > 2:
            legal_actions.append("Right")
        elif player_location[1] < 3:
            legal_actions.append("Down")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    # Return observations for both players
    player_0_loc = state["player_0"]
    player_1_loc = state["player_1"]
    quadrant_player_0 = state["quadrant_player_0"]
    quadrant_player_1 = state["quadrant_player_1"]
    
    player_0_obs = {
        "Loc": player_0_loc,
        "OpponentQuadrant": quadrant_player_1
    }
    player_1_obs = {
        "Loc": player_1_loc,
        "OpponentQuadrant": quadrant_player_0
    }
    
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Stochastically sample a valid sequence of actions
    # This is a placeholder function as the exact implementation would require more complex logic
    # For simplicity, we'll just return a fixed sequence of actions
    actions = ["Right", "Up", "Down", "Left", "Stay"]
    sampled_actions = []
    for _ in range(len(obs_action_history)):
        sampled_actions.append(random.choice(actions))
    return sampled_actions