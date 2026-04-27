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

# Constants
BOARD_SIZE = 5
CENTER_SQUARE = (2, 2)
MAX_TURNS = 50

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        "positions": {
            0: [(0, 0), (0, 4)],  # Player 0 (Blue) starting positions
            1: [(4, 0), (4, 4)],  # Player 1 (Red) starting positions
        },
        "stunned": {0: [], 1: []},  # Stunned units for each player
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
        "board": [row[:] for row in state["board"]],
        "positions": {0: state["positions"][0][:], 1: state["positions"][1][:]},
        "stunned": {0: state["stunned"][0][:], 1: state["stunned"][1][:]},
        "current_player": state["current_player"],
        "turn_count": state["turn_count"],
        "winner": state["winner"]
    }
    
    if action.startswith("move"):
        _, from_pos, _, to_pos = action.split()
        from_pos = tuple(map(int, from_pos.strip("()").split(",")))
        to_pos = tuple(map(int, to_pos.strip("()").split(",")))
        
        player = new_state["current_player"]
        new_state["positions"][player].remove(from_pos)
        new_state["positions"][player].append(to_pos)
        
        # Check for victory
        if to_pos == CENTER_SQUARE:
            new_state["winner"] = player
        
        # Update stunned units
        opponent = 1 - player
        new_state["stunned"][opponent] = [
            pos for pos in new_state["positions"][opponent]
            if not is_adjacent(pos, to_pos)
        ]
    
    # Switch player
    new_state["current_player"] = 1 - new_state["current_player"]
    new_state["turn_count"] += 1
    
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
    actions = []
    
    for pos in state["positions"][player]:
        if pos in state["stunned"][player]:
            continue
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_pos = (pos[0] + dr, pos[1] + dc)
                if is_within_bounds(new_pos) and is_empty(state, new_pos):
                    actions.append(f"move {pos} to {new_pos}")
    
    if not actions:
        actions.append("pass")
    
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]

def is_within_bounds(pos: Tuple[int, int]) -> bool:
    """Check if a position is within the board bounds."""
    return 0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE

def is_empty(state: State, pos: Tuple[int, int]) -> bool:
    """Check if a position is empty."""
    return all(pos not in state["positions"][player] for player in [0, 1])

def is_adjacent(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """Check if two positions are adjacent."""
    return abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1