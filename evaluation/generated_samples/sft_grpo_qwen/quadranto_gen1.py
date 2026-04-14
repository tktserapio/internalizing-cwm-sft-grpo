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

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions for players
    initial_positions = {
        "p0": {"row": random.randint(0, 1), "col": random.randint(0, 1)},
        "p1": {"row": random.randint(2, 3), "col": random.randint(2, 3)}
    }
    # Initial observations
    initial_observations = {
        "p0": {"loc": f"({initial_positions['p0']['row']},{initial_positions['p0']['col']}), {get_quadrant(initial_positions['p0'])}",
               "opp_quadrant": get_quadrant(initial_positions['p1'])},
        "p1": {"loc": f"({initial_positions['p1']['row']},{initial_positions['p1']['col']}), {get_quadrant(initial_positions['p1'])}",
               "opp_quadrant": get_quadrant(initial_positions['p0'])}
    }
    return {
        "state": initial_positions,
        "observations": initial_observations
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = get_current_player(new_state)
    player = new_state["state"][f"p{player_id}"]
    opponent_quadrant = new_state["observations"][f"p{1-player_id}"]["opp_quadrant"]
    
    if action == "Stay":
        new_state[f"state"][f"p{player_id}"] = player
    elif action in ["Up", "Down", "Left", "Right"]:
        row, col = player["row"], player["col"]
        if action == "Up":
            row -= 1
        elif action == "Down":
            row += 1
        elif action == "Left":
            col -= 1
        elif action == "Right":
            col += 1
        new_state[f"state"][f"p{player_id}"] = {"row": row, "col": col}
    
    new_state["observations"][f"p{player_id}"] = {"loc": f"({new_state[f'state'][f'p{player_id}']['row']}, {new_state[f'state'][f'p{player_id}']['col']}), {opponent_quadrant}"}
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return 0 if state["state"]["p0"]["row"] < 2 else 1

def get_quadrant(position: dict) -> str:
    """Determines the quadrant based on the position."""
    row, col = position["row"], position["col"]
    if row < 2 and col < 2:
        return "Q1"
    elif row < 2 and col >= 2:
        return "Q2"
    elif row >= 2 and col < 2:
        return "Q3"
    else:
        return "Q4"

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"p{player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    p0_position = state["state"]["p0"]
    p1_position = state["state"]["p1"]
    if p0_position == p1_position:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = get_current_player(state)
    player = state["state"][f"p{player_id}"]
    row, col = player["row"], player["col"]
    legal_actions = []
    if row > 0:
        legal_actions.append("Up")
    if row < 1:
        legal_actions.append("Down")
    if col > 0:
        legal_actions.append("Left")
    if col < 1:
        legal_actions.append("Right")
    legal_actions.append("Stay")
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    return [
        state["observations"][f"p0"],
        state["observations"][f"p1"]
    ]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # Placeholder for resampling logic
    # For simplicity, we'll just return a random sequence of actions
    actions = ["Up", "Down", "Left", "Right", "Stay"]
    sampled_actions = [random.choice(actions) for _ in range(len(obs_action_history))]
    return sampled_actions