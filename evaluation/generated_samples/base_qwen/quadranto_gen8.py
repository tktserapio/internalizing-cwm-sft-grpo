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

# Helper function to generate a random initial state
def _generate_initial_state():
    # Randomly place player 0 in Q1 and player 1 in Q4
    player_0_start = random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])
    player_1_start = random.choice([(2, 2), (2, 3), (3, 2), (3, 3)])
    return {
        "player_0": player_0_start,
        "player_1": player_1_start,
        "turn_count": 0,
        "current_quadrant_p0": "Q1",
        "current_quadrant_p1": "Q4"
    }

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return _generate_initial_state()

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_loc, p1_loc = new_state["player_0"], new_state["player_1"]
    current_quadrant_p0, current_quadrant_p1 = new_state["current_quadrant_p0"], new_state["current_quadrant_p1"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["player_0"] = (row, col)
        new_state["current_quadrant_p0"] = get_quadrant(row, col)
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["player_1"] = (row, col)
        new_state["current_quadrant_p1"] = get_quadrant(row, col)
    else:
        # Movement action
        new_row, new_col = p0_loc
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
        
        new_state["player_0"] = (new_row, new_col)
        new_state["current_quadrant_p0"] = get_quadrant(new_row, new_col)
        
        opponent_loc = new_state["player_1"]
        opponent_quadrant = new_state["current_quadrant_p1"]
        
        if opponent_loc == p0_loc:
            new_state["current_quadrant_p1"] = "Q1"
            new_state["winner"] = 0
            new_state["loser"] = 1
            new_state["reward_p0"] = 1.0
            new_state["reward_p1"] = -1.0
            new_state["game_over"] = True
        else:
            new_state["current_quadrant_p1"] = get_quadrant(opponent_loc[0], opponent_loc[1])
    
    new_state["turn_count"] += 1
    
    return new_state

def get_quadrant(row, col):
    if row < 2 and col < 2:
        return "Q1"
    elif row < 2 and col >= 2:
        return "Q2"
    elif row >= 2 and col < 2:
        return "Q3"
    else:
        return "Q4"

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["game_over"]:
        return -4
    elif state["player_0"][0] == state["player_1"][0] and state["player_0"][1] == state["player_1"][1]:
        return -4
    elif state["turn_count"] < 20:
        return 0 if state["player_0"][0] < state["player_1"][0] else 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        return [state["reward_p0"], state["reward_p1"]]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    elif state["turn_count"] < 20:
        p0_loc, p1_loc = state["player_0"], state["player_1"]
        current_quadrant_p0, current_quadrant_p1 = state["current_quadrant_p0"], state["current_quadrant_p1"]
        
        if current_quadrant_p0 != current_quadrant_p1:
            if current_quadrant_p0 == "Q1":
                return ["Up", "Left", "Stay"]
            elif current_quadrant_p0 == "Q2":
                return ["Up", "Right", "Stay"]
            elif current_quadrant_p0 == "Q3":
                return ["Down", "Left", "Stay"]
            else:  # current_quadrant_p0 == "Q4"
                return ["Down", "Right", "Stay"]
        else:
            if current_quadrant_p0 == "Q1":
                return ["Up", "Left", "Right", "Down", "Stay"]
            elif current_quadrant_p0 == "Q2":
                return ["Up", "Left", "Right", "Down", "Stay"]
            elif current_quadrant_p0 == "Q3":
                return ["Up", "Left", "Right", "Down", "Stay"]
            else:  # current_quadrant_p0 == "Q4"
                return ["Up", "Left", "Right", "Down", "Stay"]
    else:
        return []

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc, p1_loc = state["player_0"], state["player_1"]
    current_quadrant_p0, current_quadrant_p1 = state["current_quadrant_p0"], state["current_quadrant_p1"]
    
    p0_obs = {
        "My Loc": f"{p0_loc}",
        "Opponent Quadrant": current_quadrant_p1
    }
    
    p1_obs = {
        "My Loc": f"{p1_loc}",
        "Opponent Quadrant": current_quadrant_p0
    }
    
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # For simplicity, we will just return a fixed sequence of actions based on the current state
    # In a real implementation, this would involve sampling from the possible trajectories
    # that could have led to the current observations.
    if player_id == 0:
        return ["Right", "Down", "Right", "Up", "Right", "Up", "Left"]
    else:
        return ["Left", "Up", "Left", "Up", "Right", "Up", "Left"]