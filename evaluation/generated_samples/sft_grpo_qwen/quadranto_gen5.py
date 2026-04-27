import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Union
import random

# Type definitions
Action = str
State = Dict[str, Union[int, List[int], List[List[int]]]]
PlayerObservation = Dict[str, Union[str, List[int], List[List[int]]]]

def get_initial_state() -> State:
    # Initial state setup
    initial_board = [[0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0],
                     [0, 0, 0, 0]]
    initial_quadrant_mapping = {
        "Q1": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "Q2": [(0, 2), (0, 3), (1, 2), (1, 3)],
        "Q3": [(2, 0), (2, 1), (3, 0), (3, 1)],
        "Q4": [(2, 2), (2, 3), (3, 2), (3, 3)]
    }
    initial_player_positions = {"P0": random.choice(initial_quadrant_mapping["Q1"]),
                                "P1": random.choice(initial_quadrant_mapping["Q4"])}
    return {
        "board": initial_board,
        "current_player": 0,
        "turn_count": 0,
        "player_positions": initial_player_positions,
        "quadrant_mapping": initial_quadrant_mapping
    }

def apply_action(state: State, action: Action) -> State:
    # Apply action to the state
    new_state = state.copy()
    current_player = new_state["current_player"]
    opponent_position = new_state["player_positions"][f"P{1 - current_player}"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["board"][row][col] = 0
        new_state["player_positions"]["P0"] = [row, col]
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["board"][row][col] = 1
        new_state["player_positions"]["P1"] = [row, col]
    else:
        direction = action
        current_row, current_col = new_state["player_positions"][f"P{current_player}"]
        
        if direction == "Up":
            new_row, new_col = max(0, current_row - 1), current_col
        elif direction == "Down":
            new_row, new_col = min(3, current_row + 1), current_col
        elif direction == "Left":
            new_row, new_col = current_row, max(0, current_col - 1)
        elif direction == "Right":
            new_row, new_col = current_row, min(3, current_col + 1)
        elif direction == "Stay":
            new_row, new_col = current_row, current_col
        
        new_state["board"][new_row][new_col] = current_player
        new_state["player_positions"][f"P{current_player}"] = [new_row, new_col]
    
    new_state["turn_count"] += 1
    new_state["current_player"] = 1 - current_player
    
    return new_state

def get_current_player(state: State) -> int:
    # Return the current player
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    # Return the name of the player
    return f"P{player_id}"

def get_rewards(state: State) -> List[float]:
    # Determine rewards based on the game rules
    if state["turn_count"] >= 20:
        return [0.0, 0.0]
    elif state["player_positions"]["P0"] == state["player_positions"]["P1"]:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    # Get legal actions for the current player
    current_player = state["current_player"]
    current_position = state["player_positions"][f"P{current_player}"]
    legal_actions = []
    
    if current_position[0] > 0:
        legal_actions.append("Up")
    if current_position[0] < 3:
        legal_actions.append("Down")
    if current_position[1] > 0:
        legal_actions.append("Left")
    if current_position[1] < 3:
        legal_actions.append("Right")
    legal_actions.append("Stay")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    # Get observations for both players
    player_0_obs = {
        "My Loc": state["player_positions"]["P0"],
        "Opponent Quadrant": state["quadrant_mapping"][get_opponent_quadrant(state)]
    }
    player_1_obs = {
        "My Loc": state["player_positions"]["P1"],
        "Opponent Quadrant": state["quadrant_mapping"][get_opponent_quadrant(state)]
    }
    return [player_0_obs, player_1_obs]

def get_opponent_quadrant(state: State) -> str:
    # Determine the quadrant of the opponent
    current_player_position = state["player_positions"][f"P{get_current_player(state)}"]
    opponent_position = state["player_positions"][f"P{1 - get_current_player(state)}"]
    return get_quadrant(opponent_position)

def get_quadrant(position: List[int]) -> str:
    # Map position to quadrant
    if position[0] == 0 and position[1] <= 1:
        return "Q1"
    elif position[0] == 0 and position[1] >= 2:
        return "Q2"
    elif position[0] == 3 and position[1] <= 1:
        return "Q3"
    else:
        return "Q4"

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Sample a valid sequence of actions
    history = obs_action_history.copy()
    sampled_actions = []
    while True:
        action = random.choice(history[-1][0]["My Loc"])
        sampled_actions.append(action)
        history = history[:-1]
        if len(history) == 0 or history[-1][1] is not None:
            break
    return sampled_actions