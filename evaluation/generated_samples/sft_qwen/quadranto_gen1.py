import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    # Initial state setup
    player_0_location = random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])
    player_1_location = random.choice([(2, 2), (2, 3), (3, 2), (3, 3)])
    return {
        "player_0": player_0_location,
        "player_1": player_1_location,
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Apply an action to the current state and return the new state.
    Ensure the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = new_state["current_player"]
    opponent_id = 1 - player_id
    
    if action == "Stay":
        new_state["player_" + str(player_id)] = new_state["player_" + str(player_id)]
    elif action in ["Up", "Down", "Left", "Right"]:
        row, col = new_state["player_" + str(player_id)]
        if action == "Up":
            new_state["player_" + str(player_id)] = (max(0, row - 1), col)
        elif action == "Down":
            new_state["player_" + str(player_id)] = (min(3, row + 1), col)
        elif action == "Left":
            new_state["player_" + str(player_id)] = (row, max(0, col - 1))
        elif action == "Right":
            new_state["player_" + str(player_id)] = (row, min(3, col + 1))
    
    # Check if the game is over
    if new_state["player_0"] == new_state["player_1"]:
        new_state["game_over"] = True
        new_state["current_player"] = -4
    else:
        new_state["turn_count"] += 1
        new_state["current_player"] = 1 - player_id
    
    return new_state

def get_current_player(state: State) -> int:
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    return "Player " + str(player_id)

def get_rewards(state: State) -> List[float]:
    if state["game_over"]:
        if state["player_0"] == state["player_1"]:
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    player_id = state["current_player"]
    player_loc = state["player_" + str(player_id)]
    legal_moves = ["Stay"]
    if player_loc[0] > 0:
        legal_moves.append("Up")
    if player_loc[0] < 3:
        legal_moves.append("Down")
    if player_loc[1] > 0:
        legal_moves.append("Left")
    if player_loc[1] < 3:
        legal_moves.append("Right")
    return legal_moves

def get_observations(state: State) -> List[PlayerObservation]:
    player_0_loc = state["player_0"]
    player_1_loc = state["player_1"]
    player_0_quadrant = get_quadrant(player_0_loc)
    player_1_quadrant = get_quadrant(player_1_loc)
    return [
        {"loc": player_0_loc, "opponent_quadrant": player_1_quadrant},
        {"loc": player_1_loc, "opponent_quadrant": player_0_quadrant}
    ]

def get_quadrant(loc: Tuple[int, int]) -> str:
    row, col = loc
    if row == 0 and col == 0:
        return "Q1"
    elif row == 0 and col == 1:
        return "Q1"
    elif row == 1 and col == 0:
        return "Q1"
    elif row == 1 and col == 1:
        return "Q1"
    elif row == 2 and col == 2:
        return "Q2"
    elif row == 2 and col == 3:
        return "Q2"
    elif row == 3 and col == 2:
        return "Q2"
    elif row == 3 and col == 3:
        return "Q2"
    elif row == 0 and col == 2:
        return "Q3"
    elif row == 0 and col == 3:
        return "Q3"
    elif row == 1 and col == 2:
        return "Q3"
    elif row == 1 and col == 3:
        return "Q3"
    elif row == 2 and col == 0:
        return "Q4"
    elif row == 2 and col == 1:
        return "Q4"
    elif row == 3 and col == 0:
        return "Q4"
    elif row == 3 and col == 1:
        return "Q4"

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return the last observed action
    if obs_action_history:
        return [obs_action_history[-1][1]]
    else:
        return []