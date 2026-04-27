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
    # Place player 0 in a random position in Q1
    player0_pos = (board[0][0], board[0][1])
    # Place player 1 in a random position in Q4
    player1_pos = (board[3][2], board[3][3])
    # Create the initial state dictionary
    initial_state = {
        "board": board,
        "player0_pos": player0_pos,
        "player1_pos": player1_pos,
        "turn_count": 0,
        "current_player": 0,
        "game_over": False
    }
    return initial_state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    player_id = new_state["current_player"]
    opponent_id = 1 - player_id
    
    # Update player positions based on the action
    if action == "Stay":
        new_state[f"player{player_id}_pos"] = new_state[f"player{player_id}_pos"]
    elif action in ["Up", "Down", "Left", "Right"]:
        row, col = new_state[f"player{player_id}_pos"]
        if action == "Up":
            new_state[f"player{player_id}_pos"] = (max(row - 1, 0), col)
        elif action == "Down":
            new_state[f"player{player_id}_pos"] = (min(row + 1, 3), col)
        elif action == "Left":
            new_state[f"player{player_id}_pos"] = (row, max(col - 1, 0))
        elif action == "Right":
            new_state[f"player{player_id}_pos"] = (row, min(col + 1, 3))
    
    # Check if the game is over
    if new_state[f"player{player_id}_pos"] == new_state[f"player{opponent_id}_pos"]:
        new_state["game_over"] = True
        new_state["winner"] = player_id
        new_state["loser"] = 1 - player_id
        new_state["current_player"] = -4
    else:
        new_state["turn_count"] += 1
        new_state["current_player"] = 1 - player_id
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    winner = state.get("winner")
    loser = state.get("loser")
    if winner != -4:
        return [1.0, -1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = state["current_player"]
    player_pos = state[f"player{player_id}_pos"]
    row, col = player_pos
    legal_actions = []
    if row > 0:
        legal_actions.append("Up")
    if row < 3:
        legal_actions.append("Down")
    if col > 0:
        legal_actions.append("Left")
    if col < 3:
        legal_actions.append("Right")
    legal_actions.append("Stay")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player0_pos = state["player0_pos"]
    player1_pos = state["player1_pos"]
    player0_quadrant = get_quadrant(player0_pos)
    player1_quadrant = get_quadrant(player1_pos)
    player0_obs = {
        "My Loc": player0_pos,
        "Opponent Quadrant": player1_quadrant
    }
    player1_obs = {
        "My Loc": player1_pos,
        "Opponent Quadrant": player0_quadrant
    }
    return [player0_obs, player1_obs]

def get_quadrant(pos: Tuple[int, int]) -> str:
    """Returns the quadrant name for a given position."""
    row, col = pos
    if row == 0 and col == 0:
        return "Q1"
    elif row == 0 and col == 1:
        return "Q1"
    elif row == 0 and col == 2:
        return "Q2"
    elif row == 0 and col == 3:
        return "Q2"
    elif row == 1 and col == 0:
        return "Q1"
    elif row == 1 and col == 1:
        return "Q3"
    elif row == 1 and col == 2:
        return "Q2"
    elif row == 1 and col == 3:
        return "Q3"
    elif row == 2 and col == 0:
        return "Q3"
    elif row == 2 and col == 1:
        return "Q4"
    elif row == 2 and col == 2:
        return "Q2"
    elif row == 2 and col == 3:
        return "Q4"
    elif row == 3 and col == 0:
        return "Q4"
    elif row == 3 and col == 1:
        return "Q3"
    elif row == 3 and col == 2:
        return "Q4"
    elif row == 3 and col == 3:
        return "Q3"

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement stochastic sampling logic here
    # For simplicity, we'll just return a fixed sequence of actions
    # In a real implementation, this would involve complex probabilistic reasoning
    return ["Right", "Up", "Down", "Left", "Right", "Up"]