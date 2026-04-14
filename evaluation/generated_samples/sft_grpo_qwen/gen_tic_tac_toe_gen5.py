import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": [["." for _ in range(6)] for _ in range(6)],
        "current_player": 0,
        "winner": None,
        "turn_count": 0
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Parse the action
    row, col = map(int, action.split(","))
    
    # Check if the action is valid
    if state["board"][row][col] != ".":
        raise ValueError("Cell is already occupied.")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = (state["current_player"] + 1) % 2
    
    # Increment the turn count
    state["turn_count"] += 1
    
    # Check for win condition
    check_winner(state)
    
    # Check for draw condition
    if state["turn_count"] == 36:
        state["winner"] = "draw"
    
    return state

def check_winner(state: State):
    """
    Checks if a player has won the game based on the current state.
    """
    # Check horizontal lines
    for row in state["board"]:
        if len(set(row)) == 1 and row[0] != ".":
            state["winner"] = "x" if row[0] == "x" else "o"
            return
    
    # Check vertical lines
    for col in range(6):
        if len(set([state["board"][row][col] for row in range(6)])) == 1 and state["board"][0][col] != ".":
            state["winner"] = "x" if state["board"][0][col] == "x" else "o"
            return
    
    # Check diagonal lines
    for i in range(6):
        if len(set([state["board"][i][i], state["board"][i][5-i], state["board"][5-i][i], state["board"][5-i][5-i]])) == 1 and state["board"][i][i] != ".":
            state["winner"] = "x" if state["board"][i][i] == "x" else "o"
            return
    
    # No winner yet
    if state["winner"] is None:
        state["winner"] = "none"

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] == "x":
        return [1.0, 0.0]
    elif state["winner"] == "o":
        return [0.0, 1.0]
    elif state["winner"] == "draw":
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["winner"] is not None:
        return []
    return ["{},{}".format(row, col) for row in range(6) for col in range(6) if state["board"][row][col] == "."]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board_observation = state["board"]
    return [
        {"board": board_observation, "legal_actions": get_legal_actions(state)},
        {"board": board_observation, "legal_actions": get_legal_actions(state)}
    ]