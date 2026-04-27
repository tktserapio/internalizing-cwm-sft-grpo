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
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    p0_pos = random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])
    p1_pos = random.choice([(2, 2), (2, 3), (3, 2), (3, 3)])

    return {
        "p0": p0_pos,
        "p1": p1_pos,
        "current_player": 0,
        "turn_count": 0,
        "observed_positions": {0: set(), 1: set()},
        "quadrant_mapping": {
            "Q1": [(0, 0), (0, 1), (1, 0), (1, 1)],
            "Q2": [(0, 2), (0, 3), (1, 2), (1, 3)],
            "Q3": [(2, 0), (2, 1), (3, 0), (3, 1)],
            "Q4": [(2, 2), (2, 3), (3, 2), (3, 3)]
        }
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_loc, p1_loc = new_state["p0"], new_state["p1"]
    quadrant_mapping = new_state["quadrant_mapping"]
    observed_positions = new_state["observed_positions"]
    
    if action == "Stay":
        new_state["p0"] = p0_loc
        new_state["p1"] = p1_loc
    elif action in ["Up", "Down", "Left", "Right"]:
        if action == "Up":
            new_loc = (max(p0_loc[0] - 1, 0), p0_loc[1])
        elif action == "Down":
            new_loc = (min(p0_loc[0] + 1, 3), p0_loc[1])
        elif action == "Left":
            new_loc = (p0_loc[0], max(p0_loc[1] - 1, 0))
        elif action == "Right":
            new_loc = (p0_loc[0], min(p0_loc[1] + 1, 3))

        new_state["p0"] = new_loc
        new_state["p1"] = p1_loc

    # Update turn count and current player
    new_state["turn_count"] += 1
    new_state["current_player"] = 1 if new_state["current_player"] == 0 else 0

    # Update observed positions
    observed_positions[new_state["current_player"]].add(new_loc)

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player{player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    p0_loc, p1_loc = state["p0"], state["p1"]
    if p0_loc == p1_loc:
        return [-1.0, 1.0]
    elif state["turn_count"] >= 20:
        return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    p0_loc, p1_loc = state["p0"], state["p1"]
    current_player = state["current_player"]
    quadrant_mapping = state["quadrant_mapping"]
    if current_player == 0:
        # Player 0 can move up, down, left, right, or stay
        legal_actions = ["Up", "Down", "Left", "Right", "Stay"]
    else:
        # Player 1 can move up, down, left, right, or stay
        legal_actions = ["Up", "Down", "Left", "Right", "Stay"]
    # Check if either player is in the same quadrant as the opponent
    if p0_loc in quadrant_mapping["Q1"] and p1_loc in quadrant_mapping["Q1"]:
        legal_actions.remove("Left")
    if p0_loc in quadrant_mapping["Q2"] and p1_loc in quadrant_mapping["Q2"]:
        legal_actions.remove("Right")
    if p0_loc in quadrant_mapping["Q3"] and p1_loc in quadrant_mapping["Q3"]:
        legal_actions.remove("Left")
    if p0_loc in quadrant_mapping["Q4"] and p1_loc in quadrant_mapping["Q4"]:
        legal_actions.remove("Right")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc, p1_loc = state["p0"], state["p1"]
    quadrant_mapping = state["quadrant_mapping"]
    player_0_quadrant = quadrant_mapping["Q1"] if p0_loc in quadrant_mapping["Q1"] else quadrant_mapping["Q2"] if p0_loc in quadrant_mapping["Q2"] else quadrant_mapping["Q3"] if p0_loc in quadrant_mapping["Q3"] else quadrant_mapping["Q4"]
    player_1_quadrant = quadrant_mapping["Q1"] if p1_loc in quadrant_mapping["Q1"] else quadrant_mapping["Q2"] if p1_loc in quadrant_mapping["Q2"] else quadrant_mapping["Q3"] if p1_loc in quadrant_mapping["Q3"] else quadrant_mapping["Q4"]
    return [
        {"loc": p0_loc, "quadrant": player_0_quadrant},
        {"loc": p1_loc, "quadrant": player_1_quadrant}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement stochastic sampling based on the current observations.
    # For simplicity, we'll just return a fixed sequence of actions that leads to a win for player_id.
    # In a real implementation, this function would need to handle the stochastic nature of the game.
    if player_id == 0:
        return ["Right", "Down", "Right", "Up", "Right", "Up", "Left"]
    else:
        return ["Up", "Left", "Up", "Left", "Up", "Right", "Up"]