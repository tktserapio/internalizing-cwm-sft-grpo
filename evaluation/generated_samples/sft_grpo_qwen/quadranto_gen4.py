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
PlayerObservation = Dict[str, Union[str, List[str], List[List[str]]]]

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
    
    # Randomly place player 0 in Q1 and player 1 in Q4
    player_0_loc = random.choice(initial_quadrant_mapping["Q1"])
    player_1_loc = random.choice(initial_quadrant_mapping["Q4"])
    
    return {
        "board": initial_board,
        "player_0_loc": player_0_loc,
        "player_1_loc": player_1_loc,
        "current_player": 0,
        "turn_count": 0,
        "quadrant_mapping": initial_quadrant_mapping
    }

def apply_action(state: State, action: Action) -> State:
    # Apply the action to the state
    new_state = state.copy()
    current_player = new_state["current_player"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["board"][row][col] = 0
        new_state["player_0_loc"] = [row, col]
        new_state["quadrant_mapping"]["Q1"].remove([row, col])
        new_state["quadrant_mapping"]["Q2"].remove([row, col])
        new_state["quadrant_mapping"]["Q3"].remove([row, col])
        new_state["quadrant_mapping"]["Q4"].remove([row, col])
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["board"][row][col] = 1
        new_state["player_1_loc"] = [row, col]
        new_state["quadrant_mapping"]["Q1"].remove([row, col])
        new_state["quadrant_mapping"]["Q2"].remove([row, col])
        new_state["quadrant_mapping"]["Q3"].remove([row, col])
        new_state["quadrant_mapping"]["Q4"].remove([row, col])
    else:
        new_row, new_col = new_state["player_0_loc"]
        if action == "Up":
            new_row -= 1
        elif action == "Down":
            new_row += 1
        elif action == "Left":
            new_col -= 1
        elif action == "Right":
            new_col += 1
        elif action == "Stay":
            pass
        else:
            raise ValueError(f"Invalid action: {action}")
        
        new_state["board"][new_row][new_col] = 0
        new_state["player_0_loc"] = [new_row, new_col]
        new_state["quadrant_mapping"][get_quadrant(new_state["player_0_loc"])] = [
            [new_row, new_col]
        ]
        
        opponent_row, opponent_col = new_state["player_1_loc"]
        if opponent_row == new_row and opponent_col == new_col:
            new_state["winner"] = 0
        elif opponent_row == new_row and opponent_col == new_col:
            new_state["winner"] = 1
        else:
            new_state["winner"] = -4
        
    new_state["turn_count"] += 1
    new_state["current_player"] = (new_state["current_player"] + 1) % 2
    
    return new_state

def get_current_player(state: State) -> int:
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    if state["winner"] != -4:
        return [0.0, 0.0]
    elif state["winner"] == 0:
        return [-1.0, 1.0]
    else:
        return [1.0, -1.0]

def get_legal_actions(state: State) -> List[Action]:
    current_player = state["current_player"]
    player_loc = state["player_0_loc"] if current_player == 0 else state["player_1_loc"]
    quadrant = get_quadrant(player_loc)
    legal_moves = []
    
    if current_player == 0:
        legal_moves.append("place_p0:<row>,<col>")
        for move in ["Up", "Down", "Left", "Right", "Stay"]:
            if move in ["Up", "Down", "Left", "Right"] and is_valid_move(state, move):
                legal_moves.append(move)
    else:
        legal_moves.append("place_p1:<row>,<col>")
        for move in ["Up", "Down", "Left", "Right", "Stay"]:
            if move in ["Up", "Down", "Left", "Right"] and is_valid_move(state, move):
                legal_moves.append(move)
    
    return legal_moves

def is_valid_move(state: State, move: str) -> bool:
    player_loc = state["player_0_loc"] if state["current_player"] == 0 else state["player_1_loc"]
    new_loc = get_new_location(player_loc, move)
    return 0 <= new_loc[0] < 4 and 0 <= new_loc[1] < 4 and state["board"][new_loc[0]][new_loc[1]] == 0

def get_new_location(loc: List[int], move: str) -> List[int]:
    new_loc = loc.copy()
    if move == "Up":
        new_loc[0] -= 1
    elif move == "Down":
        new_loc[0] += 1
    elif move == "Left":
        new_loc[1] -= 1
    elif move == "Right":
        new_loc[1] += 1
    return new_loc

def get_quadrant(loc: List[int]) -> str:
    if loc[0] < 2 and loc[1] < 2:
        return "Q1"
    elif loc[0] < 2 and loc[1] >= 2:
        return "Q2"
    elif loc[0] >= 2 and loc[1] < 2:
        return "Q3"
    else:
        return "Q4"

def get_observations(state: State) -> List[PlayerObservation]:
    player_0_loc = state["player_0_loc"]
    player_1_loc = state["player_1_loc"]
    quadrant_mapping = state["quadrant_mapping"]
    
    player_0_obs = {
        "My Loc": [player_0_loc[0], player_0_loc[1]],
        "Opponent Quadrant": get_quadrant(player_1_loc),
        "Opponent Loc": [player_1_loc[0], player_1_loc[1]]
    }
    
    player_1_obs = {
        "My Loc": [player_1_loc[0], player_1_loc[1]],
        "Opponent Quadrant": get_quadrant(player_0_loc),
        "Opponent Loc": [player_0_loc[0], player_0_loc[1]]
    }
    
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would need to be implemented based on the specific rules of the game and the history of observations/actions.
    # For simplicity, we will just return a random legal action.
    legal_actions = get_legal_actions(resample_history.get_initial_state())
    return [random.choice(legal_actions)]