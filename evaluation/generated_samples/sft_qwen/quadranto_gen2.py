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

# Helper functions
def place_player_in_quadrant(player_id: int, quadrant: str) -> Tuple[int, int]:
    """Randomly place a player in a quadrant."""
    quadrants = {
        "Q1": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "Q2": [(0, 2), (0, 3), (1, 2), (1, 3)],
        "Q3": [(2, 0), (2, 1), (3, 0), (3, 1)],
        "Q4": [(2, 2), (2, 3), (3, 2), (3, 3)]
    }
    quadrant_coords = quadrants[quadrant]
    row, col = random.choice(quadrant_coords)
    return player_id, (row, col)

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    state = {
        "player_0_loc": None,
        "player_1_loc": None,
        "turn_count": 0,
        "current_player": 0,
        "game_over": False,
        "player_0_quadrant": None,
        "player_1_quadrant": None
    }
    # Place players in quadrants
    player_0_id, player_0_loc = place_player_in_quadrant(0, "Q1")
    player_1_id, player_1_loc = place_player_in_quadrant(1, "Q4")
    state["player_0_loc"] = player_0_loc
    state["player_1_loc"] = player_1_loc
    state["player_0_quadrant"] = "Q1"
    state["player_1_quadrant"] = "Q4"
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    player_id = state["current_player"]
    opponent_id = 1 - player_id
    
    if action == "place_p0:<row>,<col>":
        new_state["player_0_loc"] = eval(action.split(":")[1])
        new_state["player_0_quadrant"] = get_quadrant(new_state["player_0_loc"])
        new_state["current_player"] = 0
    elif action == "place_p1:<row>,<col>":
        new_state["player_1_loc"] = eval(action.split(":")[1])
        new_state["player_1_quadrant"] = get_quadrant(new_state["player_1_loc"])
        new_state["current_player"] = 1
    else:
        new_state["player_0_loc"], new_state["player_1_loc"] = move_player(new_state["player_0_loc"], new_state["player_1_loc"], action, player_id)
    
    if new_state["player_0_loc"] == new_state["player_1_loc"]:
        new_state["game_over"] = True
        new_state["winner"] = player_id
        new_state["loser"] = 1 - player_id
        new_state["turn_count"] = 20  # Game ends in a draw after 20 moves
    elif new_state["game_over"] is False:
        new_state["turn_count"] += 1
        new_state["current_player"] = 1 - player_id
    
    return new_state

def get_quadrant(loc: Tuple[int, int]) -> str:
    """Determine the quadrant of a given location."""
    if loc[0] < 2 and loc[1] < 2:
        return "Q1"
    elif loc[0] < 2 and loc[1] >= 2:
        return "Q2"
    elif loc[0] >= 2 and loc[1] < 2:
        return "Q3"
    else:
        return "Q4"

def move_player(player_0_loc: Tuple[int, int], player_1_loc: Tuple[int, int], action: Action, player_id: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Move a player based on the action."""
    if player_id == 0:
        if action == "Up":
            new_loc = (player_0_loc[0] - 1, player_0_loc[1])
        elif action == "Down":
            new_loc = (player_0_loc[0] + 1, player_0_loc[1])
        elif action == "Left":
            new_loc = (player_0_loc[0], player_0_loc[1] - 1)
        elif action == "Right":
            new_loc = (player_0_loc[0], player_0_loc[1] + 1)
        elif action == "Stay":
            new_loc = player_0_loc
        else:
            raise ValueError(f"Invalid action: {action}")
    else:
        if action == "Up":
            new_loc = (player_1_loc[0] - 1, player_1_loc[1])
        elif action == "Down":
            new_loc = (player_1_loc[0] + 1, player_1_loc[1])
        elif action == "Left":
            new_loc = (player_1_loc[0], player_1_loc[1] - 1)
        elif action == "Right":
            new_loc = (player_1_loc[0], player_1_loc[1] + 1)
        elif action == "Stay":
            new_loc = player_1_loc
        else:
            raise ValueError(f"Invalid action: {action}")
    
    return new_loc, player_1_loc

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["game_over"]:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        return [state["loser"], state["winner"]]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    current_player = state["current_player"]
    if current_player == 0:
        return ["place_p0:<row>,<col>", "Up", "Down", "Left", "Right", "Stay"]
    else:
        return ["place_p1:<row>,<col>", "Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_loc = state["player_0_loc"]
    player_1_loc = state["player_1_loc"]
    player_0_quadrant = state["player_0_quadrant"]
    player_1_quadrant = state["player_1_quadrant"]
    player_0_obs = {
        "My Loc": player_0_loc,
        "Opponent Quadrant": player_1_quadrant
    }
    player_1_obs = {
        "My Loc": player_1_loc,
        "Opponent Quadrant": player_0_quadrant
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to be implemented to generate a plausible sequence of actions.
    # For simplicity, we'll just return a fixed sequence here.
    if player_id == 0:
        return ["place_p0:0,0", "Up", "Down", "Left", "Right", "Stay"]
    else:
        return ["place_p1:3,3", "Up", "Down", "Left", "Right", "Stay"]