import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Constants for the game
BOARD_SIZE = 4
MAX_TURNS = 20
PLAYER_0 = 0
PLAYER_1 = 1
TERMINAL_STATE = -4

# Helper function to determine the quadrant of a given position
def get_quadrant(row: int, col: int) -> str:
    if row < 2 and col < 2:
        return "Top-Left"
    elif row < 2 and col >= 2:
        return "Top-Right"
    elif row >= 2 and col < 2:
        return "Bottom-Left"
    else:
        return "Bottom-Right"

# Initialize the game state
def get_initial_state() -> State:
    state = {
        "player_positions": [(0, 0), (3, 3)],  # Initial positions for player 0 and player 1
        "turn_count": 0,
        "current_player": PLAYER_0,
        "game_over": False,
        "winner": None,
    }
    return state

# Apply an action to the current state and return the new state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    player = new_state["current_player"]
    row, col = new_state["player_positions"][player]

    # Determine new position based on action
    if action == "Up":
        row = max(0, row - 1)
    elif action == "Down":
        row = min(BOARD_SIZE - 1, row + 1)
    elif action == "Left":
        col = max(0, col - 1)
    elif action == "Right":
        col = min(BOARD_SIZE - 1, col + 1)

    # Update player position
    new_state["player_positions"][player] = (row, col)

    # Check for win condition
    if new_state["player_positions"][PLAYER_0] == new_state["player_positions"][PLAYER_1]:
        new_state["game_over"] = True
        new_state["winner"] = player
    else:
        # Increment turn count and switch player
        new_state["turn_count"] += 1
        if new_state["turn_count"] >= MAX_TURNS:
            new_state["game_over"] = True
        else:
            new_state["current_player"] = 1 - player

    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    if state["game_over"]:
        return TERMINAL_STATE
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards for each player
def get_rewards(state: State) -> List[float]:
    if state["game_over"]:
        if state["winner"] is not None:
            return [1.0 if state["winner"] == PLAYER_0 else -1.0, 
                    1.0 if state["winner"] == PLAYER_1 else -1.0]
        else:
            return [0.0, 0.0]  # Draw
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state["game_over"]:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_pos = state["player_positions"][PLAYER_0]
    player_1_pos = state["player_positions"][PLAYER_1]
    return [
        {
            "My Loc": player_0_pos,
            "Opponent Quadrant": get_quadrant(*player_1_pos)
        },
        {
            "My Loc": player_1_pos,
            "Opponent Quadrant": get_quadrant(*player_0_pos)
        }
    ]

# Resample history based on observations
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # This function would typically involve some stochastic process to generate a plausible action history
    # For simplicity, we'll return a random sequence of actions that could have led to the current observations
    actions = []
    state = get_initial_state()
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
            state = apply_action(state, action)
        else:
            # Generate a random valid action
            legal_actions = get_legal_actions(state)
            if legal_actions:
                random_action = random.choice(legal_actions)
                actions.append(random_action)
                state = apply_action(state, random_action)
    return actions