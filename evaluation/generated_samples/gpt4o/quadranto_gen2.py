import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants for the game
BOARD_SIZE = 4
MAX_TURNS = 20
QUADRANTS = {
    (0, 0): "Top-Left",
    (0, 1): "Top-Left",
    (1, 0): "Top-Left",
    (1, 1): "Top-Left",
    (0, 2): "Top-Right",
    (0, 3): "Top-Right",
    (1, 2): "Top-Right",
    (1, 3): "Top-Right",
    (2, 0): "Bottom-Left",
    (2, 1): "Bottom-Left",
    (3, 0): "Bottom-Left",
    (3, 1): "Bottom-Left",
    (2, 2): "Bottom-Right",
    (2, 3): "Bottom-Right",
    (3, 2): "Bottom-Right",
    (3, 3): "Bottom-Right",
}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Randomly place players in their respective quadrants
    p0_start = random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])
    p1_start = random.choice([(2, 2), (2, 3), (3, 2), (3, 3)])
    
    return {
        "player_positions": {0: p0_start, 1: p1_start},
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if state["game_over"]:
        return state

    new_state = state.copy()
    new_positions = new_state["player_positions"].copy()
    current_player = new_state["current_player"]
    current_position = new_positions[current_player]

    # Calculate new position based on action
    if action == "Up":
        new_position = (max(0, current_position[0] - 1), current_position[1])
    elif action == "Down":
        new_position = (min(BOARD_SIZE - 1, current_position[0] + 1), current_position[1])
    elif action == "Left":
        new_position = (current_position[0], max(0, current_position[1] - 1))
    elif action == "Right":
        new_position = (current_position[0], min(BOARD_SIZE - 1, current_position[1] + 1))
    elif action == "Stay":
        new_position = current_position
    else:
        raise ValueError("Invalid action")

    # Update position
    new_positions[current_player] = new_position
    new_state["player_positions"] = new_positions

    # Check for win condition
    if new_positions[0] == new_positions[1]:
        new_state["game_over"] = True
    else:
        # Update turn count and switch player
        new_state["turn_count"] += 1
        if new_state["turn_count"] >= MAX_TURNS:
            new_state["game_over"] = True
        else:
            new_state["current_player"] = 1 - current_player

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -1 for terminal state."""
    return -1 if state["game_over"] else state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state["game_over"]:
        return [0.0, 0.0]
    
    p0_pos = state["player_positions"][0]
    p1_pos = state["player_positions"][1]
    
    if p0_pos == p1_pos:
        # Player who just moved won
        winner = 1 - state["current_player"]
        return [1.0 if winner == 0 else -1.0, 1.0 if winner == 1 else -1.0]
    else:
        # Draw
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_pos = state["player_positions"][0]
    p1_pos = state["player_positions"][1]
    
    return [
        {"My Loc": p0_pos, "Opponent Quadrant": QUADRANTS[p1_pos]},
        {"My Loc": p1_pos, "Opponent Quadrant": QUADRANTS[p0_pos]}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function is complex and requires a detailed understanding of the game dynamics.
    # For simplicity, we will assume a random valid sequence of actions.
    state = get_initial_state()
    actions = []
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
            state = apply_action(state, action)
        else:
            # Generate a random valid action
            legal_actions = get_legal_actions(state)
            random_action = random.choice(legal_actions)
            actions.append(random_action)
            state = apply_action(state, random_action)
    return actions