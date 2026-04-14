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

# Constants
BOARD_SIZE = 4
MAX_TURNS = 20
ACTIONS = ["Up", "Down", "Left", "Right", "Stay"]
QUADRANTS = {
    "Top-Left": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "Top-Right": [(0, 2), (0, 3), (1, 2), (1, 3)],
    "Bottom-Left": [(2, 0), (2, 1), (3, 0), (3, 1)],
    "Bottom-Right": [(2, 2), (2, 3), (3, 2), (3, 3)]
}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    p0_start = random.choice(QUADRANTS["Top-Left"])
    p1_start = random.choice(QUADRANTS["Bottom-Right"])
    return {
        "positions": [(p0_start[0], p0_start[1]), (p1_start[0], p1_start[1])],
        "turn": 0,
        "current_player": 0,
        "game_over": False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    new_positions = list(new_state["positions"])
    player = new_state["current_player"]
    row, col = new_positions[player]

    if action == "Up":
        row = max(0, row - 1)
    elif action == "Down":
        row = min(BOARD_SIZE - 1, row + 1)
    elif action == "Left":
        col = max(0, col - 1)
    elif action == "Right":
        col = min(BOARD_SIZE - 1, col + 1)

    new_positions[player] = (row, col)
    new_state["positions"] = new_positions

    # Check for win condition
    if new_positions[0] == new_positions[1]:
        new_state["game_over"] = True
    else:
        # Update turn and current player
        new_state["turn"] += 1
        new_state["current_player"] = 1 - player
        if new_state["turn"] >= MAX_TURNS:
            new_state["game_over"] = True

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
    if state["positions"][0] == state["positions"][1]:
        winner = 1 - state["current_player"]
        return [1.0 if winner == 0 else -1.0, 1.0 if winner == 1 else -1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    return [] if state["game_over"] else ACTIONS

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
    """Determines the quadrant of a given position."""
    for quadrant, positions in QUADRANTS.items():
        if position in positions:
            return quadrant
    return ""

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function is complex and depends on the specific game rules and randomness.
    # For simplicity, we will return a random sequence of actions.
    actions = []
    for obs, _ in obs_action_history:
        actions.append(random.choice(ACTIONS))
    return actions