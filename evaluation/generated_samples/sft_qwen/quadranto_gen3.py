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

# Helper functions
def get_random_location():
    """Generates a random location within the 4x4 grid."""
    return (random.randint(0, 3), random.randint(0, 3))

def get_quadrant(location):
    """Determines the quadrant based on the row and column of the location."""
    row, col = location
    if row < 2 and col < 2:
        return "Q1"
    elif row < 2 and col >= 2:
        return "Q2"
    elif row >= 2 and col < 2:
        return "Q3"
    else:
        return "Q4"

def get_opponent_quadrant(current_quadrant):
    """Determines the opponent's quadrant based on the current player's quadrant."""
    if current_quadrant == "Q1":
        return "Q4"
    elif current_quadrant == "Q2":
        return "Q1"
    elif current_quadrant == "Q3":
        return "Q2"
    else:
        return "Q3"

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial locations for players
    p0_loc = get_random_location()
    p1_loc = get_random_location()
    
    # Determine quadrants
    p0_quadrant = get_quadrant(p0_loc)
    p1_quadrant = get_opponent_quadrant(p0_quadrant)
    
    return {
        "p0_loc": p0_loc,
        "p1_loc": p1_loc,
        "p0_quadrant": p0_quadrant,
        "p1_quadrant": p1_quadrant,
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    p0_loc = new_state["p0_loc"]
    p1_loc = new_state["p1_loc"]
    p0_quadrant = new_state["p0_quadrant"]
    p1_quadrant = new_state["p1_quadrant"]
    current_player = new_state["current_player"]
    turn_count = new_state["turn_count"]
    
    if action == "place_p0:<row>,<col>":
        new_loc = eval(action.split(":")[1])
        new_state["p0_loc"] = new_loc
        new_state["p0_quadrant"] = get_quadrant(new_loc)
        new_state["p1_loc"] = get_random_location()
        new_state["p1_quadrant"] = get_opponent_quadrant(new_state["p0_quadrant"])
        new_state["turn_count"] += 1
        new_state["current_player"] = 1
    elif action == "place_p1:<row>,<col>":
        new_state["p1_loc"] = eval(action.split(":")[1])
        new_state["p1_quadrant"] = get_quadrant(new_state["p1_loc"])
        new_state["p0_loc"] = get_random_location()
        new_state["p0_quadrant"] = get_opponent_quadrant(new_state["p1_quadrant"])
        new_state["turn_count"] += 1
        new_state["current_player"] = 0
    elif action in ["Up", "Down", "Left", "Right", "Stay"]:
        if action == "Up":
            new_loc = (max(p0_loc[0] - 1, 0), p0_loc[1])
        elif action == "Down":
            new_loc = (min(p0_loc[0] + 1, 3), p0_loc[1])
        elif action == "Left":
            new_loc = (p0_loc[0], max(p0_loc[1] - 1, 0))
        elif action == "Right":
            new_loc = (p0_loc[0], min(p0_loc[1] + 1, 3))
        elif action == "Stay":
            new_loc = p0_loc
        
        if new_loc == p1_loc:
            new_state["game_over"] = True
            new_state["winner"] = 0
            new_state["loser"] = 1
        else:
            new_state["p0_loc"] = new_loc
            new_state["p0_quadrant"] = get_quadrant(new_loc)
            new_state["p1_loc"] = get_random_location()
            new_state["p1_quadrant"] = get_opponent_quadrant(new_state["p0_quadrant"])
            new_state["turn_count"] += 1
            new_state["current_player"] = 1
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        winner = state["winner"]
        loser = state["loser"]
        return [1.0 if winner == 0 else -1.0, 1.0 if winner == 1 else -1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    current_player = state["current_player"]
    if current_player == 0:
        return ["place_p0:<row>,<col>", "Up", "Down", "Left", "Right", "Stay"]
    else:
        return ["place_p1:<row>,<col>", "Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
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
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented based on the specific logic of the game and the observations.
    # For simplicity, we'll just return a random action for demonstration purposes.
    return [random.choice(["Up", "Down", "Left", "Right", "Stay"]) for _ in range(len(obs_action_history))]