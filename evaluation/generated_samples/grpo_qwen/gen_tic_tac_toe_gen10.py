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
        "game_over": False
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
        raise ValueError("Cell already occupied")
    
    # Update the board
    state["board"][row][col] = "x" if state["current_player"] == 0 else "o"
    
    # Switch the current player
    state["current_player"] = 1 if state["current_player"] == 0 else 0
    
    # Check for win condition
    check_winner(state)
    
    # Check for draw condition
    if all(all(cell != "." for cell in row) for row in state["board"]):
        state["game_over"] = True
        state["winner"] = None
    
    return state

def check_winner(state: State) -> None:
    """
    Checks if a player has won the game.
    Checks for horizontal, vertical, and diagonal lines of four.
    """
    for direction in [(0, 0), (0, 1), (1, 0), (1, 1), (1, -1)]:
        for i in range(6):
            for j in range(6):
                if state["board"][i][j] == ".":
                    continue
                count = 1
                for dx, dy in direction:
                    x, y = i + dx, j + dy
                    while 0 <= x < 6 and 0 <= y < 6 and state["board"][x][y] == state["board"][i][j]:
                        count += 1
                        x += dx
                        y += dy
                    if count >= 4:
                        state["winner"] = state["current_player"]
                        return

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["winner"] is not None:
        return [1.0, 0.0] if state["winner"] == 0 else [0.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["game_over"]:
        return []
    return [f"{i},{j}" for i in range(6) for j in range(6) if state["board"][i][j] == "."]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for i in range(6):
        for j in range(6):
            if state["board"][i][j] == ".":
                observations.append({
                    "board": [[cell if (i, j) == (r, c) else "." for c in range(6)] for r in range(6)],
                    "current_player": state["current_player"],
                    "winner": state["winner"]
                })
    return observations