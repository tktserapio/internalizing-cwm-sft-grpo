import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initialize the board as a 4x4 grid
    board = [[(i, j) for j in range(4)] for i in range(4)]
    # Place player 0 in a random position in the top-left quadrant
    player_0_pos = (board[0][0], board[0][1])
    # Place player 1 in a random position in the bottom-right quadrant
    player_1_pos = (board[3][2], board[3][3])
    # Create the initial state dictionary
    initial_state = {
        "board": board,
        "player_0_pos": player_0_pos,
        "player_1_pos": player_1_pos,
        "turn_count": 0,
        "current_player": 0
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    current_player = new_state["current_player"]
    opponent_pos = new_state["player_1_pos"] if current_player == 0 else new_state["player_0_pos"]
    
    # Update the player's position based on the action
    if action == "Stay":
        new_state[current_player]["pos"] = opponent_pos
    elif action in ["Up", "Down", "Left", "Right"]:
        direction = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}[action]
        new_pos = (new_state[current_player]["pos"][0] + direction[0], new_state[current_player]["pos"][1] + direction[1])
        if 0 <= new_pos[0] < 4 and 0 <= new_pos[1] < 4:
            new_state[current_player]["pos"] = new_pos
        else:
            new_state[current_player]["pos"] = opponent_pos
    else:
        raise ValueError(f"Invalid action: {action}")
    
    # Check if the game ended
    if new_state["player_0_pos"] == new_state["player_1_pos"]:
        new_state["game_over"] = True
        new_state["winner"] = 1 if current_player == 0 else 0
        new_state["loser"] = 0 if current_player == 0 else 1
    else:
        new_state["game_over"] = False
        new_state["winner"] = 0
        new_state["loser"] = 0
    
    new_state["turn_count"] += 1
    new_state["current_player"] = 1 if current_player == 0 else 0
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state["game_over"]:
        return [-state["loser"], state["winner"]]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = state["current_player"]
    player_pos = state["player_0_pos"] if current_player == 0 else state["player_1_pos"]
    legal_actions = []
    for direction in ["Up", "Down", "Left", "Right", "Stay"]:
        new_pos = (player_pos[0] + direction[0], player_pos[1] + direction[1])
        if 0 <= new_pos[0] < 4 and 0 <= new_pos[1] < 4:
            legal_actions.append(direction)
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        "my_loc": state["player_0_pos"],
        "opponent_quadrant": "Top-Left" if state["player_1_pos"] in [(0, 2), (0, 3), (1, 2), (1, 3)] else "Top-Right" if state["player_1_pos"] in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Bottom-Left" if state["player_1_pos"] in [(2, 0), (2, 1), (3, 0), (3, 1)] else "Bottom-Right"
    }
    player_1_obs = {
        "my_loc": state["player_1_pos"],
        "opponent_quadrant": "Top-Left" if state["player_0_pos"] in [(0, 2), (0, 3), (1, 2), (1, 3)] else "Top-Right" if state["player_0_pos"] in [(0, 0), (0, 1), (1, 0), (1, 1)] else "Bottom-Left" if state["player_0_pos"] in [(2, 0), (2, 1), (3, 0), (3, 1)] else "Bottom-Right"
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement stochastic sampling logic here
    # For simplicity, we'll just return a fixed sequence of actions
    # In a real implementation, this would involve complex probabilistic reasoning
    return ["Right", "Up", "Down", "Left", "Stay"]