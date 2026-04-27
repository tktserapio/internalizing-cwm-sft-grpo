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
MAX_TURNS = 50

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None]
        ],
        "positions": {
            0: [(0, 0), (0, 4)],  # Player 0 (Blue)
            1: [(4, 0), (4, 4)]   # Player 1 (Red)
        },
        "stunned": {
            0: [False, False],
            1: [False, False]
        },
        "current_player": 0,
        "turn_count": 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = {
        "board": [row[:] for row in state["board"]],
        "positions": {k: v[:] for k, v in state["positions"].items()},
        "stunned": {k: v[:] for k, v in state["stunned"].items()},
        "current_player": state["current_player"],
        "turn_count": state["turn_count"]
    }
    
    if action.startswith("move"):
        _, from_pos, _, to_pos = action.split()
        from_pos = tuple(map(int, from_pos.strip("()").split(",")))
        to_pos = tuple(map(int, to_pos.strip("()").split(",")))
        
        player = new_state["current_player"]
        unit_index = new_state["positions"][player].index(from_pos)
        
        # Move the unit
        new_state["positions"][player][unit_index] = to_pos
        
        # Clear the stun status for the opponent
        opponent = 1 - player
        new_state["stunned"][opponent] = [False, False]
        
        # Check for new stuns
        for i, pos in enumerate(new_state["positions"][opponent]):
            if is_adjacent(to_pos, pos):
                new_state["stunned"][opponent][i] = True
    
    # Update the current player and turn count
    new_state["current_player"] = 1 - new_state["current_player"]
    new_state["turn_count"] += 1
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    if is_terminal(state):
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Blue" if player_id == 0 else "Red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if is_terminal(state):
        if state["positions"][0].count(CENTER_SQUARE) > 0:
            return [1.0, 0.0]
        elif state["positions"][1].count(CENTER_SQUARE) > 0:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]  # Draw
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if is_terminal(state):
        return []
    
    player = state["current_player"]
    legal_actions = []
    
    for i, pos in enumerate(state["positions"][player]):
        if state["stunned"][player][i]:
            continue  # Skip stunned units
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip no movement
                
                new_pos = (pos[0] + dr, pos[1] + dc)
                if is_within_bounds(new_pos) and is_empty(state, new_pos):
                    legal_actions.append(f"move {pos} to {new_pos}")
    
    if not legal_actions:
        legal_actions.append("pass")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

# Helper functions
def is_within_bounds(pos: Tuple[int, int]) -> bool:
    """Checks if a position is within the board bounds."""
    return 0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE

def is_empty(state: State, pos: Tuple[int, int]) -> bool:
    """Checks if a position is empty."""
    for positions in state["positions"].values():
        if pos in positions:
            return False
    return True

def is_adjacent(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """Checks if two positions are adjacent."""
    return abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1

def is_terminal(state: State) -> bool:
    """Checks if the game is in a terminal state."""
    if state["positions"][0].count(CENTER_SQUARE) > 0 or state["positions"][1].count(CENTER_SQUARE) > 0:
        return True
    if state["turn_count"] >= MAX_TURNS:
        return True
    return False