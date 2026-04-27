import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

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
            0: [(0, 0), (0, 4)],  # Player 0 (Blue) positions
            1: [(4, 0), (4, 4)]   # Player 1 (Red) positions
        },
        "stunned": {
            0: [False, False],  # Stun status for Player 0's units
            1: [False, False]   # Stun status for Player 1's units
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
        # Parse the action string
        _, from_pos, _, to_pos = action.split()
        from_r, from_c = map(int, from_pos.strip("()").split(","))
        to_r, to_c = map(int, to_pos.strip("()").split(","))
        
        # Determine which unit is moving
        player = state["current_player"]
        unit_index = new_state["positions"][player].index((from_r, from_c))
        
        # Move the unit
        new_state["positions"][player][unit_index] = (to_r, to_c)
        
        # Update stun status for opponent's units
        opponent = 1 - player
        for i, (op_r, op_c) in enumerate(new_state["positions"][opponent]):
            if abs(op_r - to_r) <= 1 and abs(op_c - to_c) <= 1:
                new_state["stunned"][opponent][i] = True
        
        # Clear current player's stun status
        new_state["stunned"][player] = [False, False]
        
        # Check for victory
        if (to_r, to_c) == (2, 2):
            new_state["current_player"] = -4  # Terminal state
            return new_state
    
    # Increment turn count and switch player
    new_state["turn_count"] += 1
    new_state["current_player"] = 1 - state["current_player"]
    
    # Check for draw
    if new_state["turn_count"] >= 50:
        new_state["current_player"] = -4  # Terminal state
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Blue" if player_id == 0 else "Red"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if state["current_player"] == -4:
        # Check who won
        for player, positions in state["positions"].items():
            if (2, 2) in positions:
                return [1.0, 0.0] if player == 0 else [0.0, 1.0]
        # If no one won, it's a draw
        return [0.5, 0.5]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["current_player"] == -4:
        return []
    
    player = state["current_player"]
    legal_actions = []
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    for i, (r, c) in enumerate(state["positions"][player]):
        if state["stunned"][player][i]:
            continue  # Skip stunned units
        
        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 5 and 0 <= new_c < 5 and (new_r, new_c) not in state["positions"][0] and (new_r, new_c) not in state["positions"][1]:
                legal_actions.append(f"move ({r},{c}) to ({new_r},{new_c})")
    
    if not legal_actions:
        legal_actions.append("pass")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    return [state, state]