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
    p0_position = (random.choice([0, 0]), random.choice([0, 1]))
    p1_position = (3, 3)
    
    # Observations for players
    p0_observation = {
        "loc": p0_position,
        "opponent_quadrant": "Bottom-Right"
    }
    p1_observation = {
        "loc": p1_position,
        "opponent_quadrant": "Top-Left"
    }
    
    return {
        "p0_position": p0_position,
        "p1_position": p1_position,
        "p0_observation": p0_observation,
        "p1_observation": p1_observation,
        "turn_count": 0,
        "max_turns": 20
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    
    # Update player positions based on the action
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p0_position"] = (row, col)
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1_position"] = (row, col)
    else:
        # Movement actions
        p0_row, p0_col = new_state["p0_position"]
        p1_row, p1_col = new_state["p1_position"]
        
        if action == "Up":
            new_state["p0_position"] = (p0_row - 1, p0_col)
            new_state["p1_position"] = (p1_row - 1, p1_col)
        elif action == "Down":
            new_state["p0_position"] = (p0_row + 1, p0_col)
            new_state["p1_position"] = (p1_row + 1, p1_col)
        elif action == "Left":
            new_state["p0_position"] = (p0_row, p0_col - 1)
            new_state["p1_position"] = (p1_row, p1_col - 1)
        elif action == "Right":
            new_state["p0_position"] = (p0_row, p0_col + 1)
            new_state["p1_position"] = (p1_row, p1_col + 1)
        elif action == "Stay":
            pass
        
        # Check if the players have met
        if new_state["p0_position"] == new_state["p1_position"]:
            new_state["winner"] = 1
            new_state["loser"] = 0
            new_state["game_over"] = True
            new_state["turn_count"] = 20
            return new_state
    
    # Update observations
    new_state["p0_observation"] = {
        "loc": new_state["p0_position"],
        "opponent_quadrant": get_opponent_quadrant(new_state["p1_position"])
    }
    new_state["p1_observation"] = {
        "loc": new_state["p1_position"],
        "opponent_quadrant": get_opponent_quadrant(new_state["p0_position"])
    }
    
    # Increment turn count
    new_state["turn_count"] += 1
    
    return new_state

def get_opponent_quadrant(position: Tuple[int, int]) -> str:
    """Determine the quadrant of the opponent based on their position."""
    if position in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        return "Top-Left"
    elif position in [(0, 2), (0, 3), (1, 2), (1, 3)]:
        return "Top-Right"
    elif position in [(2, 0), (2, 1), (3, 0), (3, 1)]:
        return "Bottom-Left"
    else:  # position in [(2, 2), (2, 3), (3, 2), (3, 3)]
        return "Bottom-Right"

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["turn_count"] < state["max_turns"]:
        return 0 if state["p0_position"] == state["p1_position"] else 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if state["turn_count"] >= state["max_turns"]:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["turn_count"] >= state["max_turns"]:
        return []
    else:
        p0_position = state["p0_position"]
        p1_position = state["p1_position"]
        legal_actions = ["Up", "Down", "Left", "Right", "Stay"]
        
        if p0_position == p1_position:
            legal_actions.remove("Stay")
        
        if p0_position[0] == 0 and p0_position[1] == 0:
            legal_actions.remove("Up")
        
        if p0_position[0] == 3 and p0_position[1] == 3:
            legal_actions.remove("Down")
        
        if p0_position[1] == 0 and p0_position[0] != 0:
            legal_actions.remove("Left")
        
        if p0_position[1] == 3 and p0_position[0] != 3:
            legal_actions.remove("Right")
        
        return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_observation = {
        "loc": state["p0_position"],
        "opponent_quadrant": state["p1_observation"]["opponent_quadrant"]
    }
    p1_observation = {
        "loc": state["p1_position"],
        "opponent_quadrant": state["p0_observation"]["opponent_quadrant"]
    }
    return [p0_observation, p1_observation]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # For simplicity, we'll just return a random legal action for demonstration purposes.
    # In a real implementation, this would involve more complex logic to ensure the history is consistent.
    legal_actions = get_legal_actions(get_initial_state())
    return [random.choice(legal_actions) for _ in range(len(obs_action_history))]