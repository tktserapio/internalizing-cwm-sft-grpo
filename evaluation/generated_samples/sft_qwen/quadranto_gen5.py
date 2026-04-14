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
def place_unit(state: State, player_id: int, position: Tuple[int, int]) -> State:
    """
    Places a unit in the given position in the state.
    """
    state[f"player_{player_id}_loc"] = position
    return state

def update_quadrant(state: State, player_id: int, position: Tuple[int, int]) -> State:
    """
    Updates the quadrant of the given player based on their position.
    """
    row, col = position
    if row < 2 and col < 2:
        state[f"player_{player_id}_quadrant"] = "Q1"
    elif row < 2 and col >= 2:
        state[f"player_{player_id}_quadrant"] = "Q2"
    elif row >= 2 and col < 2:
        state[f"player_{player_id}_quadrant"] = "Q3"
    else:
        state[f"player_{player_id}_quadrant"] = "Q4"
    return state

def get_player_loc(state: State, player_id: int) -> Tuple[int, int]:
    """
    Returns the location of the given player.
    """
    return tuple(int(coord) for coord in state[f"player_{player_id}_loc"].split(','))

def get_opponent_loc(state: State, player_id: int) -> Tuple[int, int]:
    """
    Returns the opponent's location based on the current player's quadrant.
    """
    own_quadrant = state[f"player_{player_id}_quadrant"]
    opponent_quadrant = "Q1" if own_quadrant == "Q2" else "Q2" if own_quadrant == "Q1" else "Q3" if own_quadrant == "Q4" else "Q4"
    opponent_loc_str = next((coord for coord in state.keys() if coord.startswith(f"player_1_loc") and state[coord] == opponent_quadrant), None)
    return tuple(int(coord) for coord in opponent_loc_str.split(',')) if opponent_loc_str else (-1, -1)

def get_opponent_quadrant(state: State, player_id: int) -> str:
    """
    Returns the quadrant of the opponent based on the current player's quadrant.
    """
    own_quadrant = state[f"player_{player_id}_quadrant"]
    opponent_quadrant = "Q1" if own_quadrant == "Q2" else "Q2" if own_quadrant == "Q1" else "Q3" if own_quadrant == "Q4" else "Q4"
    return opponent_quadrant

def get_opponent_quadrant_observation(state: State, player_id: int) -> PlayerObservation:
    """
    Returns the opponent's quadrant observation.
    """
    opponent_quadrant = get_opponent_quadrant(state, player_id)
    return {"opponent_quadrant": opponent_quadrant}

def get_current_player(state: State) -> int:
    """
    Returns the current player (0 or 1).
    """
    return int(state["current_player"])

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards.
    """
    current_player = get_current_player(state)
    opponent_quadrant = get_opponent_quadrant(state, current_player)
    if opponent_quadrant == state[f"player_{current_player}_quadrant"]:
        return [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    current_player = get_current_player(state)
    player_loc = get_player_loc(state, current_player)
    opponent_loc = get_opponent_loc(state, current_player)
    legal_actions = []
    if player_loc != opponent_loc:
        if player_loc[0] > 0:
            legal_actions.append("Up")
        if player_loc[0] < 3:
            legal_actions.append("Down")
        if player_loc[1] > 0:
            legal_actions.append("Left")
        if player_loc[1] < 3:
            legal_actions.append("Right")
        legal_actions.append("Stay")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs].
    """
    player_0_loc = get_player_loc(state, 0)
    player_1_loc = get_opponent_loc(state, 0)
    player_0_quadrant = state[f"player_0_quadrant"]
    player_1_quadrant = state[f"player_1_quadrant"]
    player_0_obs = {
        "player_0_loc": ",".join(map(str, player_0_loc)),
        "player_0_quadrant": player_0_quadrant,
        "opponent_loc": ",".join(map(str, player_1_loc)),
        "opponent_quadrant": player_1_quadrant
    }
    player_1_obs = {
        "player_1_loc": ",".join(map(str, player_1_loc)),
        "player_1_quadrant": player_1_quadrant,
        "opponent_loc": ",".join(map(str, player_0_loc)),
        "opponent_quadrant": player_0_quadrant
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to be implemented to sample a valid sequence of actions.
    # For simplicity, we'll just return a fixed sequence here.
    # In a real implementation, this should be stochastic and based on the history.
    return ["Right", "Up", "Down", "Left", "Stay"]

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    state = {}
    state["current_player"] = 0
    state["player_0_loc"] = "0,0"
    state["player_1_loc"] = "3,3"
    state["player_0_quadrant"] = "Q1"
    state["player_1_quadrant"] = "Q4"
    state["board_size"] = 4
    state["turn_count"] = 0
    state["game_over"] = False
    state["obs_action_history"] = []
    state["reward_history"] = [0.0, 0.0]
    state["legal_actions"] = ["Right", "Up", "Down", "Left", "Stay"]
    state["observation"] = get_observations(state)
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    state_copy = state.copy()
    current_player = get_current_player(state_copy)
    player_loc = get_player_loc(state_copy, current_player)
    opponent_loc = get_opponent_loc(state_copy, current_player)
    opponent_quadrant = get_opponent_quadrant(state_copy, current_player)
    if action == "Right":
        new_loc = (player_loc[0], player_loc[1] + 1)
    elif action == "Left":
        new_loc = (player_loc[0], player_loc[1] - 1)
    elif action == "Up":
        new_loc = (player_loc[0] - 1, player_loc[1])
    elif action == "Down":
        new_loc = (player_loc[0] + 1, player_loc[1])
    elif action == "Stay":
        new_loc = player_loc
    else:
        raise ValueError(f"Invalid action: {action}")
    
    state_copy["player_0_loc"] = ",".join(map(str, new_loc))
    state_copy["player_1_loc"] = ",".join(map(str, opponent_loc))
    state_copy["player_0_quadrant"] = get_opponent_quadrant(state_copy, current_player)
    state_copy["player_1_quadrant"] = get_opponent_quadrant(state_copy, current_player)
    state_copy["turn_count"] += 1
    state_copy["obs_action_history"].append((state_copy["observation"], action))
    state_copy["observation"] = get_observations(state_copy)
    state_copy["legal_actions"] = get_legal_actions(state_copy)
    if new_loc == opponent_loc:
        state_copy["game_over"] = True
        state_copy["reward_history"][current_player] = 1.0
        state_copy["reward_history"][1 - current_player] = -1.0
    return state_copy