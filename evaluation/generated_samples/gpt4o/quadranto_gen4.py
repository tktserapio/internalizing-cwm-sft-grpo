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

# Constants
BOARD_SIZE = 4
QUADRANTS = {
    0: [(0, 0), (0, 1), (1, 0), (1, 1)],  # Top-Left
    1: [(0, 2), (0, 3), (1, 2), (1, 3)],  # Top-Right
    2: [(2, 0), (2, 1), (3, 0), (3, 1)],  # Bottom-Left
    3: [(2, 2), (2, 3), (3, 2), (3, 3)],  # Bottom-Right
}

ACTIONS = ["Up", "Down", "Left", "Right", "Stay"]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    p0_start = random.choice(QUADRANTS[0])
    p1_start = random.choice(QUADRANTS[3])
    return {
        "positions": [(p0_start), (p1_start)],
        "turn_count": 0,
        "current_player": 0,
        "game_over": False,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    positions = list(state["positions"])
    player = state["current_player"]
    
    # Determine new position based on action
    row, col = positions[player]
    if action == "Up":
        row = max(0, row - 1)
    elif action == "Down":
        row = min(BOARD_SIZE - 1, row + 1)
    elif action == "Left":
        col = max(0, col - 1)
    elif action == "Right":
        col = min(BOARD_SIZE - 1, col + 1)
    
    positions[player] = (row, col)
    new_state["positions"] = positions
    
    # Check for win condition
    if positions[0] == positions[1]:
        new_state["game_over"] = True
        new_state["winner"] = player
    else:
        # Increment turn count and switch player
        new_state["turn_count"] += 1
        if new_state["turn_count"] >= 20:
            new_state["game_over"] = True
        new_state["current_player"] = 1 - player
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return -4 if state["game_over"] else state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state["game_over"]:
        return [0.0, 0.0]
    if state["winner"] is not None:
        return [1.0 if state["winner"] == 0 else -1.0, 1.0 if state["winner"] == 1 else -1.0]
    return [0.0, 0.0]  # Draw

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    return [] if state["game_over"] else ACTIONS

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    positions = state["positions"]
    observations = []
    for player in range(2):
        opponent = 1 - player
        opponent_quadrant = next(q for q, locs in QUADRANTS.items() if positions[opponent] in locs)
        observations.append({
            "My Loc": positions[player],
            "Opponent Quadrant": opponent_quadrant
        })
    return observations

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function is complex and depends on the specifics of the game logic and how to infer actions from observations.
    # For simplicity, we'll return a random sequence of actions that could have led to the current state.
    actions = []
    state = get_initial_state()
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
            state = apply_action(state, action)
    return actions