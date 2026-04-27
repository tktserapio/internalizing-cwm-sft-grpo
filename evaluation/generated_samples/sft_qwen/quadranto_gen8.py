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

# Helper functions
def place_p0(row: int, col: int) -> Action:
    """Place player 0 at the given row and column."""
    return f"place_p0:{row},{col}"

def place_p1(row: int, col: int) -> Action:
    """Place player 1 at the given row and column."""
    return f"place_p1:{row},{col}"

def get_quadrant(row: int, col: int) -> str:
    """Return the quadrant of the given row and column."""
    if row == 0 and col < 2:
        return "Q1"
    elif row == 0 and col >= 2:
        return "Q2"
    elif row == 2 and col < 2:
        return "Q3"
    else:
        return "Q4"

def get_random_location() -> Tuple[int, int]:
    """Return a random location within the 4x4 grid."""
    return random.randint(0, 3), random.randint(0, 3)

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    p0_row, p0_col = get_random_location()
    p1_row, p1_col = get_random_location()
    while p0_row == p1_row and abs(p0_col - p1_col) == 1:
        p1_row, p1_col = get_random_location()
    return {
        "p0": {"row": p0_row, "col": p0_col, "quadrant": get_quadrant(p0_row, p0_col)},
        "p1": {"row": p1_row, "col": p1_col, "quadrant": get_quadrant(p1_row, p1_col)}
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if action.startswith("place_p0"):
        p0_row, p0_col = map(int, action.split(":")[1].split(","))
        state["p0"]["row"], state["p0"]["col"] = p0_row, p0_col
        state["p0"]["quadrant"] = get_quadrant(p0_row, p0_col)
    elif action.startswith("place_p1"):
        p1_row, p1_col = map(int, action.split(":")[1].split(","))
        state["p1"]["row"], state["p1"]["col"] = p1_row, p1_col
        state["p1"]["quadrant"] = get_quadrant(p1_row, p1_col)
    else:
        # Movement action
        p0 = state["p0"]
        p1 = state["p1"]
        if action == "Up":
            p0["row"] = max(0, p0["row"] - 1)
            p1["row"] = max(0, p1["row"] - 1)
        elif action == "Down":
            p0["row"] = min(3, p0["row"] + 1)
            p1["row"] = min(3, p1["row"] + 1)
        elif action == "Left":
            p0["col"] = max(0, p0["col"] - 1)
            p1["col"] = max(0, p1["col"] - 1)
        elif action == "Right":
            p0["col"] = min(3, p0["col"] + 1)
            p1["col"] = min(3, p1["col"] + 1)
        elif action == "Stay":
            pass
        else:
            raise ValueError(f"Invalid action: {action}")
    return state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    p0 = state["p0"]
    p1 = state["p1"]
    if p0["row"] == p1["row"] and p0["col"] == p1["col"]:
        return -4  # Game over
    elif p0["quadrant"] == state["p1"]["quadrant"]:
        return 1  # Player 1 wins
    elif p1["quadrant"] == state["p0"]["quadrant"]:
        return 0  # Player 0 wins
    else:
        return 0 if p0["row"] < p1["row"] else 1  # Player 0's turn

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    winner = get_current_player(state)
    return [-1.0 if winner == 0 else 1.0, 1.0 if winner == 1 else -1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    p0 = state["p0"]
    p1 = state["p1"]
    if p0["row"] == p1["row"] and p0["col"] == p1["col"]:
        return []  # Game over
    elif p0["quadrant"] == p1["quadrant"]:
        return ["Stay"]
    else:
        return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0 = state["p0"]
    p1 = state["p1"]
    p0_obs = {
        "My Loc": f"({p0['row']}, {p0['col']})",
        "Opponent Quadrant": p1["quadrant"]
    }
    p1_obs = {
        "My Loc": f"({p1['row']}, {p1['col']})",
        "Opponent Quadrant": p0["quadrant"]
    }
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations."""
    # This function would need to implement the logic to resample actions based on the observations.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this would involve sampling from the possible actions based on the observations.
    if player_id == 0:
        return ["Right", "Down", "Right", "Up", "Right", "Up", "Left"]
    else:
        return ["Up", "Left", "Up", "Left", "Up", "Down", "Left"]