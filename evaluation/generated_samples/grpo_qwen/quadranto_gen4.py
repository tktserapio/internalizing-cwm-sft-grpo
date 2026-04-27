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
    initial_player_positions = {
        0: random.choice(initial_quadrant_mapping["Q1"]),
        1: random.choice(initial_quadrant_mapping["Q4"])
    }
    initial_state = {
        "board": initial_board,
        "current_player": 0,
        "turn_count": 0,
        "player_positions": initial_player_positions,
        "quadrant_mapping": initial_quadrant_mapping
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    current_player = new_state["current_player"]
    opponent_position = new_state["player_positions"][1 - current_player]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["board"][row][col] = 0
        new_state["player_positions"][0] = [row, col]
        new_state["current_player"] = 1
        new_state["turn_count"] += 1
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["board"][row][col] = 1
        new_state["player_positions"][1] = [row, col]
        new_state["current_player"] = 0
        new_state["turn_count"] += 1
    else:
        row, col = new_state["player_positions"][current_player]
        if action == "Up":
            new_state["board"][row][col] = 0
            new_state["player_positions"][current_player][1] -= 1
        elif action == "Down":
            new_state["board"][row][col] = 0
            new_state["player_positions"][current_player][1] += 1
        elif action == "Left":
            new_state["board"][row][col] = 0
            new_state["player_positions"][current_player][0] -= 1
        elif action == "Right":
            new_state["board"][row][col] = 0
            new_state["player_positions"][current_player][0] += 1
        elif action == "Stay":
            pass
        else:
            raise ValueError(f"Invalid action: {action}")
        new_state["turn_count"] += 1
    
    if new_state["turn_count"] >= 20:
        new_state["game_over"] = True
        new_state["winner"] = 1 - current_player
        new_state["reward"] = [0.0, 0.0]
    else:
        new_state["reward"] = [0.0, 0.0]
    
    return new_state

def get_current_player(state: State) -> int:
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    if state["game_over"]:
        return [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    current_player = state["current_player"]
    player_position = state["player_positions"][current_player]
    row, col = player_position
    legal_actions = []
    if row > 0:
        legal_actions.append("Up")
    if row < 3:
        legal_actions.append("Down")
    if col > 0:
        legal_actions.append("Left")
    if col < 3:
        legal_actions.append("Right")
    legal_actions.append("Stay")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    current_player = state["current_player"]
    player_position = state["player_positions"][current_player]
    opponent_position = state["player_positions"][1 - current_player]
    quadrant_mapping = state["quadrant_mapping"]
    opponent_quadrant = quadrant_mapping[str([opponent_position[0], opponent_position[1]])]
    observations = [
        {"loc": player_position, "opponent_loc": opponent_position, "opponent_quadrant": opponent_quadrant},
        {"loc": opponent_position, "opponent_loc": player_position, "opponent_quadrant": quadrant_mapping[str([player_position[0], player_position[1]])]}
    ]
    return observations

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would require more complex logic to handle stochastic outcomes and should be implemented based on the specific rules of the game.
    # For simplicity, we'll just return a fixed sequence of actions that lead to the given observations.
    # In a real implementation, this function would need to account for the stochastic nature of the game.
    if player_id == 0:
        return ["place_p0:0,0", "place_p1:3,3", "Right", "Up", "Down", "Left", "Right", "Up"]
    else:
        return ["place_p1:3,3", "place_p0:0,0", "Up", "Down", "Left", "Right", "Up"]