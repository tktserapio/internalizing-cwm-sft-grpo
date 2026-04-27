import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants for the game
BOARD_SIZE = 4
QUADRANTS = {
    0: [(0, 0), (0, 1), (1, 0), (1, 1)],  # Top-Left
    1: [(0, 2), (0, 3), (1, 2), (1, 3)],  # Top-Right
    2: [(2, 0), (2, 1), (3, 0), (3, 1)],  # Bottom-Left
    3: [(2, 2), (2, 3), (3, 2), (3, 3)]   # Bottom-Right
}
ACTIONS = ["Up", "Down", "Left", "Right", "Stay"]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    p0_start = random.choice(QUADRANTS[0])
    p1_start = random.choice(QUADRANTS[3])
    return {
        "positions": {0: p0_start, 1: p1_start},
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_positions = new_state["positions"].copy()
    current_player = new_state["current_player"]

    # Get current position
    current_pos = new_positions[current_player]

    # Calculate new position based on action
    if action == "Up":
        new_pos = (max(0, current_pos[0] - 1), current_pos[1])
    elif action == "Down":
        new_pos = (min(BOARD_SIZE - 1, current_pos[0] + 1), current_pos[1])
    elif action == "Left":
        new_pos = (current_pos[0], max(0, current_pos[1] - 1))
    elif action == "Right":
        new_pos = (current_pos[0], min(BOARD_SIZE - 1, current_pos[1] + 1))
    else:  # "Stay"
        new_pos = current_pos

    # Update position
    new_positions[current_player] = new_pos
    new_state["positions"] = new_positions

    # Check for game over condition
    if new_positions[0] == new_positions[1]:
        new_state["game_over"] = True

    # Increment turn count
    new_state["turn_count"] += 1

    # Check for draw condition
    if new_state["turn_count"] >= 20:
        new_state["game_over"] = True

    # Switch player
    new_state["current_player"] = 1 - current_player

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -1 for terminal state."""
    if state["game_over"]:
        return -1
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state["game_over"]:
        return [0.0, 0.0]
    positions = state["positions"]
    if positions[0] == positions[1]:
        # Determine winner
        winner = 1 - state["current_player"]
        return [1.0 if winner == 0 else -1.0, 1.0 if winner == 1 else -1.0]
    return [0.0, 0.0]  # Draw

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    return ACTIONS

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    positions = state["positions"]
    p0_quadrant = get_quadrant(positions[1])
    p1_quadrant = get_quadrant(positions[0])
    return [
        {"My Loc": positions[0], "Opponent Quadrant": p0_quadrant},
        {"My Loc": positions[1], "Opponent Quadrant": p1_quadrant}
    ]

def get_quadrant(position: Tuple[int, int]) -> str:
    """Helper function to determine the quadrant of a position."""
    for quadrant, positions in QUADRANTS.items():
        if position in positions:
            return ["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"][quadrant]
    return "Unknown"

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This is a complex function that would require a detailed implementation based on the game's stochastic nature.
    # For simplicity, we'll return a random sequence of actions that could have led to the observations.
    actions = []
    state = get_initial_state()
    for obs, _ in obs_action_history:
        legal_actions = get_legal_actions(state)
        action = random.choice(legal_actions)
        actions.append(action)
        state = apply_action(state, action)
    return actions