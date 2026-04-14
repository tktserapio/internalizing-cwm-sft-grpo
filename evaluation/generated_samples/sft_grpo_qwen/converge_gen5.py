import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def parse_coordinates(action: Action) -> Tuple[int, int]:
    """Parses the source and destination coordinates from the action string."""
    parts = action.split(" to ")
    src = tuple(map(int, parts[0].split("(")[1].split(",")[::-1]))
    dest = tuple(map(int, parts[1].split(",")[::-1]))
    return src, dest

def is_adjacent(src: Tuple[int, int], dest: Tuple[int, int]) -> bool:
    """Checks if the source and destination are adjacent."""
    return abs(src[0] - dest[0]) <= 1 and abs(src[1] - dest[1]) <= 1

def is_center_square(src: Tuple[int, int]) -> bool:
    """Checks if the source coordinate is the center square."""
    return src == (2, 2)

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "state": {
            "board": [
                [None, None, None, None, None],
                [None, None, None, None, None],
                [None, None, None, None, None],
                [None, None, None, None, None],
                [None, None, None, None, None]
            ],
            "turn": 0,
            "stunned_units": [],
            "winner": None
        },
        "players": {
            "blue": {"units": [(0, 0), (0, 4)]},
            "red": {"units": [(4, 0), (4, 4)]}
        }
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    src, dest = parse_coordinates(action)
    if new_state["state"]["board"][src[0]][src[1]] is None:
        raise ValueError(f"Source square {src} is empty.")
    
    # Apply movement
    new_state["state"]["board"][dest[0]][dest[1]] = new_state["state"]["board"][src[0]][src[1]]
    new_state["state"]["board"][src[0]][src[1]] = None
    
    # Check for stun
    for unit in new_state["players"]["blue"]["units"]:
        if is_adjacent(unit, dest):
            new_state["stunned_units"].append(unit)
            break
    for unit in new_state["players"]["red"]["units"]:
        if is_adjacent(unit, dest):
            new_state["stunned_units"].append(unit)
            break
    
    # Update turn
    new_state["state"]["turn"] += 1
    
    # Check for winner
    if is_center_square(dest):
        new_state["winner"] = "blue" if dest in new_state["players"]["blue"]["units"] else "red"
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["winner"] is not None:
        return -4
    return state["state"]["turn"] % 2

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "blue" if player_id == 0 else "red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] is not None:
        return [1.0, 0.0] if state["winner"] == "blue" else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for player in ["blue", "red"]:
        for unit in state["players"][player]["units"]:
            for i in range(5):
                for j in range(5):
                    if state["state"]["board"][i][j] is None:
                        src = (i, j)
                        dest = (unit[0], unit[1])
                        if is_adjacent(src, dest):
                            legal_actions.append(f"move ({i},{j}) to ({unit[0]},{unit[1]})")
                        elif is_center_square((i, j)):
                            legal_actions.append(f"move ({i},{j}) to ({unit[0]},{unit[1]})")
                        else:
                            legal_actions.append(f"move ({i},{j}) to ({unit[0]},{unit[1]})")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    blue_obs = {
        "board": state["state"]["board"],
        "turn": state["state"]["turn"],
        "stunned_units": state["stunned_units"],
        "winner": state["winner"]
    }
    red_obs = {
        "board": state["state"]["board"],
        "turn": state["state"]["turn"],
        "stunned_units": state["stunned_units"],
        "winner": state["winner"]
    }
    return [blue_obs, red_obs]