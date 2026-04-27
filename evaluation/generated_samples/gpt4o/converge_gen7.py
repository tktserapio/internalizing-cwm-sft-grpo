import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants for the game
BOARD_SIZE = 5
CENTER_SQUARE = (2, 2)
PLAYER_0_START = [(0, 0), (0, 4)]
PLAYER_1_START = [(4, 0), (4, 4)]
MAX_TURNS = 50

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        "positions": {0: PLAYER_0_START.copy(), 1: PLAYER_1_START.copy()},
        "stunned": {0: [False, False], 1: [False, False]},
        "current_player": 0,
        "turn_count": 0,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board": [row.copy() for row in state["board"]],
        "positions": {0: state["positions"][0][:], 1: state["positions"][1][:]},
        "stunned": {0: state["stunned"][0][:], 1: state["stunned"][1][:]},
        "current_player": state["current_player"],
        "turn_count": state["turn_count"],
        "winner": state["winner"]
    }

    if action.startswith("move"):
        _, from_pos, _, to_pos = action.split()
        from_r, from_c = map(int, from_pos.strip("()").split(","))
        to_r, to_c = map(int, to_pos.strip("()").split(","))

        player = new_state["current_player"]
        unit_index = new_state["positions"][player].index((from_r, from_c))
        new_state["positions"][player][unit_index] = (to_r, to_c)

        if (to_r, to_c) == CENTER_SQUARE:
            new_state["winner"] = player

        # Update stun status
        opponent = 1 - player
        for i, (opp_r, opp_c) in enumerate(new_state["positions"][opponent]):
            if abs(opp_r - to_r) <= 1 and abs(opp_c - to_c) <= 1:
                new_state["stunned"][opponent][i] = True

    new_state["current_player"] = 1 - new_state["current_player"]
    new_state["turn_count"] += 1

    # Clear stun status for the player who just moved
    for i in range(2):
        new_state["stunned"][new_state["current_player"]][i] = False

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["winner"] is not None or state["turn_count"] >= MAX_TURNS:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Blue" if player_id == 0 else "Red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["winner"] is not None:
        return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]
    if state["turn_count"] >= MAX_TURNS:
        return [0.5, 0.5]  # Draw
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if get_current_player(state) == -4:
        return []

    player = state["current_player"]
    legal_actions = []

    for i, (r, c) in enumerate(state["positions"][player]):
        if state["stunned"][player][i]:
            continue

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_r, new_c = r + dr, c + dc
                if 0 <= new_r < BOARD_SIZE and 0 <= new_c < BOARD_SIZE:
                    if (new_r, new_c) not in state["positions"][0] and (new_r, new_c) not in state["positions"][1]:
                        legal_actions.append(f"move ({r},{c}) to ({new_r},{new_c})")

    if not legal_actions:
        legal_actions.append("pass")

    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]