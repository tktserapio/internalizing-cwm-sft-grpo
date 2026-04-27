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

# Helper function to generate a random initial state
def _generate_initial_state():
    # Possible locations for Player 0 and Player 1
    possible_locations = [
        [(0, 0), (0, 1), (1, 0), (1, 1)],  # Q1
        [(0, 2), (0, 3), (1, 2), (1, 3)],  # Q2
        [(2, 0), (2, 1), (3, 0), (3, 1)],  # Q3
        [(2, 2), (2, 3), (3, 2), (3, 3)]   # Q4
    ]
    
    # Randomly place Player 0 in Q1, Q2, or Q3
    player_0_location = random.choice(possible_locations)
    player_1_location = random.choice([loc for loc in possible_locations if loc != player_0_location])
    
    return {
        "player_0": {"location": random.choice(player_0_location), "quadrant": "Q1" if player_0_location == [(0, 0), (0, 1), (1, 0), (1, 1)] else "Q2" if player_0_location == [(0, 2), (0, 3), (1, 2), (1, 3)] else "Q3" if player_0_location == [(2, 0), (2, 1), (3, 0), (3, 1)] else "Q4"},
        "player_1": {"location": random.choice(player_1_location), "quadrant": "Q4" if player_1_location == [(2, 2), (2, 3), (3, 2), (3, 3)] else "Q1" if player_1_location == [(0, 0), (0, 1), (1, 0), (1, 1)] else "Q2" if player_1_location == [(0, 2), (0, 3), (1, 2), (1, 3)] else "Q3"},
        "turn_count": 0,
        "game_over": False
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
    player_id = get_current_player(new_state)
    player = new_state[f"player_{player_id}"]
    opponent_quadrant = new_state["player_1"]["quadrant"] if player_id == 0 else new_state["player_0"]["quadrant"]
    
    # Update player's location based on the action
    if action == "Stay":
        new_state[f"player_{player_id}"]["location"] = player["location"]
    elif action in ["Up", "Down", "Left", "Right"]:
        row, col = player["location"]
        if action == "Up":
            new_state[f"player_{player_id}"]["location"] = (row - 1, col)
        elif action == "Down":
            new_state[f"player_{player_id}"]["location"] = (row + 1, col)
        elif action == "Left":
            new_state[f"player_{player_id}"]["location"] = (row, col - 1)
        elif action == "Right":
            new_state[f"player_{player_id}"]["location"] = (row, col + 1)
    
    # Check if the game is over
    if new_state[f"player_{player_id}"]["location"] == new_state["player_1"]["location"]:
        new_state["game_over"] = True
        new_state[f"player_{player_id}"]["quadrant"] = opponent_quadrant
        new_state["player_1"]["quadrant"] = "Bottom-Right" if opponent_quadrant == "Top-Left" else "Top-Left"
        new_state[f"player_{player_id}"]["points"] = 1.0
        new_state["player_1"]["points"] = -1.0
    elif new_state["turn_count"] >= 20:
        new_state["game_over"] = True
        new_state[f"player_{player_id}"]["points"] = 0.0
        new_state["player_1"]["points"] = 0.0
    
    new_state["turn_count"] += 1
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["game_over"]:
        return -4
    return 0 if state["player_0"]["quadrant"] == "Bottom-Right" else 1

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        return [state["player_0"]["points"], state["player_1"]["points"]]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    return ["Stay", "Up", "Down", "Left", "Right"]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        "My Loc": state["player_0"]["location"],
        "Opponent Quadrant": state["player_1"]["quadrant"]
    }
    player_1_obs = {
        "My Loc": state["player_1"]["location"],
        "Opponent Quadrant": state["player_0"]["quadrant"]
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: list[Tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # For simplicity, we will just return a fixed sequence of actions that lead to the current state
    # This is a placeholder function as the actual implementation would require more complex logic
    return obs_action_history[-1][1:] if obs_action_history else ["Stay"] * 20