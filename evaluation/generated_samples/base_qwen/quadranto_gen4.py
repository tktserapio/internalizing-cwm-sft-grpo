import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to generate random initial positions
def get_random_position():
    return random.choice([(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 0), (2, 1), (3, 0), (3, 1), (2, 2), (2, 3), (3, 2), (3, 3)])

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Place player 0 in Q1 and player 1 in Q4
    p0_pos = get_random_position()
    p1_pos = get_random_position()
    while p0_pos == p1_pos:
        p1_pos = get_random_position()
    
    return {
        "p0": p0_pos,
        "p1": p1_pos,
        "turn_count": 0,
        "current_quadrant_p0": "Q1",
        "current_quadrant_p1": "Q4"
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    p0_loc, p1_loc = new_state["p0"], new_state["p1"]
    current_quadrant_p0, current_quadrant_p1 = new_state["current_quadrant_p0"], new_state["current_quadrant_p1"]
    turn_count = new_state["turn_count"]
    
    if action == "place_p0:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p0"] = (row, col)
        new_state["current_quadrant_p0"] = get_quadrant(row, col)
    elif action == "place_p1:<row>,<col>":
        row, col = map(int, action.split(":")[1].split(","))
        new_state["p1"] = (row, col)
        new_state["current_quadrant_p1"] = get_quadrant(row, col)
    else:
        new_state["p0"] = move_player(p0_loc, action)
        new_state["p1"] = move_player(p1_loc, action)
        new_state["current_quadrant_p0"] = get_quadrant(new_state["p0"][0], new_state["p0"][1])
        new_state["current_quadrant_p1"] = get_quadrant(new_state["p1"][0], new_state["p1"][1])
    
    new_state["turn_count"] += 1
    
    return new_state

def move_player(loc: tuple[int, int], action: Action) -> tuple[int, int]:
    """
    Moves the player based on the given action.
    """
    row, col = loc
    if action == "Up":
        return (max(0, row - 1), col)
    elif action == "Down":
        return (min(3, row + 1), col)
    elif action == "Left":
        return (row, max(0, col - 1))
    elif action == "Right":
        return (row, min(3, col + 1))
    elif action == "Stay":
        return (row, col)
    else:
        raise ValueError(f"Invalid action: {action}")

def get_quadrant(row: int, col: int) -> str:
    """
    Determines the quadrant based on the row and column coordinates.
    """
    if row < 2 and col < 2:
        return "Q1"
    elif row < 2 and col >= 2:
        return "Q2"
    elif row >= 2 and col < 2:
        return "Q3"
    else:
        return "Q4"

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if state["turn_count"] < 20:
        return 0 if state["p0"] == state["p1"] else -4
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["turn_count"] < 20:
        return [-1.0, 1.0] if state["p0"] == state["p1"] else [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["turn_count"] < 20:
        p0_loc, p1_loc = state["p0"], state["p1"]
        current_quadrant_p0, current_quadrant_p1 = state["current_quadrant_p0"], state["current_quadrant_p1"]
        
        p0_legal_moves = ["Up", "Down", "Left", "Right", "Stay"]
        p1_legal_moves = ["Up", "Down", "Left", "Right", "Stay"]
        
        if current_quadrant_p0 != current_quadrant_p1:
            p0_legal_moves.remove("Stay")
            p1_legal_moves.remove("Stay")
        
        if current_quadrant_p0 == "Q1":
            p0_legal_moves.remove("Up")
            p0_legal_moves.remove("Left")
        if current_quadrant_p0 == "Q2":
            p0_legal_moves.remove("Up")
            p0_legal_moves.remove("Right")
        if current_quadrant_p0 == "Q3":
            p0_legal_moves.remove("Down")
            p0_legal_moves.remove("Left")
        if current_quadrant_p0 == "Q4":
            p0_legal_moves.remove("Down")
            p0_legal_moves.remove("Right")
        
        if current_quadrant_p1 == "Q1":
            p1_legal_moves.remove("Up")
            p1_legal_moves.remove("Left")
        if current_quadrant_p1 == "Q2":
            p1_legal_moves.remove("Up")
            p1_legal_moves.remove("Right")
        if current_quadrant_p1 == "Q3":
            p1_legal_moves.remove("Down")
            p1_legal_moves.remove("Left")
        if current_quadrant_p1 == "Q4":
            p1_legal_moves.remove("Down")
            p1_legal_moves.remove("Right")
        
        return p0_legal_moves + p1_legal_moves
    else:
        return []

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_loc, p1_loc = state["p0"], state["p1"]
    current_quadrant_p0, current_quadrant_p1 = state["current_quadrant_p0"], state["current_quadrant_p1"]
    
    p0_obs = {
        "My Loc": f"{p0_loc}",
        "Opponent Quadrant": current_quadrant_p1
    }
    p1_obs = {
        "My Loc": f"{p1_loc}",
        "Opponent Quadrant": current_quadrant_p0
    }
    
    return [p0_obs, p1_obs]

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to be implemented to sample actions based on the history and current state.
    # For simplicity, we'll just return a fixed sequence here.
    # In a real implementation, this would involve sampling actions that lead to the observed state.
    # Here, we're returning a fixed sequence of actions that could potentially explain the observed state.
    # Note: This is a placeholder implementation.
    return [
        "place_p0:0,0",  # Player 0 starts in Q1
        "place_p1:3,3",  # Player 1 starts in Q4
        "Right",        # Player 0 moves Right
        "Up",           # Player 1 moves Up
        "Down",         # Player 0 moves Down
        "Left",         # Player 1 moves Left
        "Right",        # Player 0 moves Right
        "Up"            # Player 1 moves Up
    ]