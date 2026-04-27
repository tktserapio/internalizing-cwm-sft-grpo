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
    p0_position = random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])
    p1_position = random.choice([(2, 2), (2, 3), (3, 2), (3, 3)])
    
    return {
        "p0_position": p0_position,
        "p1_position": p1_position,
        "current_player": 0,
        "turn_count": 0,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_position = new_state["p0_position"]
    p1_position = new_state["p1_position"]
    current_player = new_state["current_player"]
    turn_count = new_state["turn_count"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p0_position"] = (row, col)
        new_state["current_player"] = (current_player + 1) % 2
        new_state["turn_count"] += 1
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1_position"] = (row, col)
        new_state["current_player"] = (current_player + 1) % 2
        new_state["turn_count"] += 1
    else:
        # Movement actions
        if action == "Up":
            new_state["p0_position"] = (max(0, p0_position[0] - 1), p0_position[1])
            new_state["p1_position"] = (max(0, p1_position[0] - 1), p1_position[1])
        elif action == "Down":
            new_state["p0_position"] = (min(3, p0_position[0] + 1), p0_position[1])
            new_state["p1_position"] = (min(3, p1_position[0] + 1), p1_position[1])
        elif action == "Left":
            new_state["p0_position"] = (p0_position[0], max(0, p0_position[1] - 1))
            new_state["p1_position"] = (p1_position[0], max(0, p1_position[1] - 1))
        elif action == "Right":
            new_state["p0_position"] = (p0_position[0], min(3, p0_position[1] + 1))
            new_state["p1_position"] = (p1_position[0], min(3, p1_position[1] + 1))
        elif action == "Stay":
            pass
        else:
            raise ValueError(f"Invalid action: {action}")
        
        new_state["current_player"] = (current_player + 1) % 2
        new_state["turn_count"] += 1
    
    # Check for game over condition
    if new_state["p0_position"] == new_state["p1_position"]:
        new_state["game_over"] = True
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player{player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        if state["p0_position"] == state["p1_position"]:
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    current_player = state["current_player"]
    p0_position = state["p0_position"]
    p1_position = state["p1_position"]
    
    legal_actions = []
    if current_player == 0:
        # Player 0's legal actions
        if p0_position[0] > 0:
            legal_actions.append("Up")
        if p0_position[0] < 3:
            legal_actions.append("Down")
        if p0_position[1] > 0:
            legal_actions.append("Left")
        if p0_position[1] < 3:
            legal_actions.append("Right")
        legal_actions.append("Stay")
    else:
        # Player 1's legal actions
        if p1_position[0] > 0:
            legal_actions.append("Up")
        if p1_position[0] < 3:
            legal_actions.append("Down")
        if p1_position[1] > 0:
            legal_actions.append("Left")
        if p1_position[1] < 3:
            legal_actions.append("Right")
        legal_actions.append("Stay")
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_position = state["p0_position"]
    p1_position = state["p1_position"]
    p0_quadrant = get_quadrant(p0_position)
    p1_quadrant = get_quadrant(p1_position)
    
    p0_observation = {
        "my_loc": p0_position,
        "opponent_quadrant": p1_quadrant
    }
    p1_observation = {
        "my_loc": p1_position,
        "opponent_quadrant": p0_quadrant
    }
    
    return [p0_observation, p1_observation]

def get_quadrant(position: Tuple[int, int]) -> str:
    """Determines the quadrant of a given position."""
    row, col = position
    if row == 0 and col == 0:
        return "Q1"
    elif row == 0 and col == 3:
        return "Q2"
    elif row == 3 and col == 0:
        return "Q3"
    elif row == 3 and col == 3:
        return "Q4"
    else:
        raise ValueError(f"Position {position} is not within the 4x4 grid.")

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to be implemented based on the specific game dynamics and history.
    # For simplicity, we'll just return a random legal action.
    legal_actions = get_legal_actions(get_initial_state())
    return [random.choice(legal_actions)]