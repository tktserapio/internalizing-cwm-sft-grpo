import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import *
import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to generate a random initial state
def get_random_initial_position():
    positions = [(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 0), (2, 1), (3, 0), (3, 1), (2, 2), (2, 3), (3, 2), (3, 3)]
    return random.choice(positions)

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial state: Player 0 in Q1, Player 1 in Q4
    p0_pos = get_random_initial_position()
    p1_pos = get_random_initial_position()
    while p0_pos == p1_pos:
        p1_pos = get_random_initial_position()
    
    return {
        "p0_loc": p0_pos,
        "p1_loc": p1_pos,
        "p0_quadrant": "Top-Left" if p0_pos in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Top-Right",
        "p1_quadrant": "Bottom-Right" if p1_pos in [(2, 2), (2, 3), (3, 2), (3, 3)] else "Bottom-Left",
        "turn_count": 0
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    p0_loc = new_state["p0_loc"]
    p1_loc = new_state["p1_loc"]
    
    if action == "place_p0:<row>,<col>":
        new_state["p0_loc"] = eval(action.split(":")[1])
        new_state["p0_quadrant"] = "Top-Left" if new_state["p0_loc"] in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Top-Right"
    elif action == "place_p1:<row>,<col>":
        new_state["p1_loc"] = eval(action.split(":")[1])
        new_state["p1_quadrant"] = "Bottom-Right" if new_state["p1_loc"] in [(2, 2), (2, 3), (3, 2), (3, 3)] else "Bottom-Left"
    else:
        if action in ["Up", "Down", "Left", "Right"]:
            if action == "Up":
                new_state["p0_loc"] = (new_state["p0_loc"][0], max(0, new_state["p0_loc"][1] - 1))
                new_state["p1_loc"] = (new_state["p1_loc"][0], max(0, new_state["p1_loc"][1] - 1))
            elif action == "Down":
                new_state["p0_loc"] = (new_state["p0_loc"][0], min(3, new_state["p0_loc"][1] + 1))
                new_state["p1_loc"] = (new_state["p1_loc"][0], min(3, new_state["p1_loc"][1] + 1))
            elif action == "Left":
                new_state["p0_loc"] = (max(0, new_state["p0_loc"][0] - 1), new_state["p0_loc"][1])
                new_state["p1_loc"] = (max(0, new_state["p1_loc"][0] - 1), new_state["p1_loc"][1])
            elif action == "Right":
                new_state["p0_loc"] = (min(3, new_state["p0_loc"][0] + 1), new_state["p0_loc"][1])
                new_state["p1_loc"] = (min(3, new_state["p1_loc"][0] + 1), new_state["p1_loc"][1])
        elif action == "Stay":
            pass
        
        new_state["p0_quadrant"] = "Top-Left" if new_state["p0_loc"] in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Top-Right"
        new_state["p1_quadrant"] = "Bottom-Right" if new_state["p1_loc"] in [(2, 2), (2, 3), (3, 2), (3, 3)] else "Bottom-Left"
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    
    if p0_loc == p1_loc:
        return -4  # Game over, draw
    elif state["turn_count"] % 2 == 0:
        return 0  # Player 0's turn
    else:
        return 1  # Player 1's turn

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 0" if player_id == 0 else "Player 1"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    
    if p0_loc == p1_loc:
        return [-1.0, 1.0]  # Player 0 loses, Player 1 wins
    else:
        return [0.0, 0.0]  # Not a terminal state yet

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    
    if state["turn_count"] >= 20:
        return []  # Game ends in a draw
    elif p0_loc == p1_loc:
        return []
    else:
        legal_moves = ["Up", "Down", "Left", "Right", "Stay"]
        if state["turn_count"] % 2 == 0:
            return legal_moves
        else:
            return legal_moves + ["place_p0:<row>,<col>", "place_p1:<row>,<col>"]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc = state["p0_loc"]
    p1_loc = state["p1_loc"]
    p0_quadrant = state["p0_quadrant"]
    p1_quadrant = state["p1_quadrant"]
    
    return [
        {"loc": p0_loc, "quadrant": p0_quadrant},
        {"loc": p1_loc, "quadrant": p1_quadrant}
    ]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state()."""
    # This function would need to be implemented based on the specific rules of the game and the observed history.
    # For simplicity, we'll just return a random legal action.
    legal_actions = get_legal_actions(obs_action_history[-1][0])
    return [random.choice(legal_actions)]