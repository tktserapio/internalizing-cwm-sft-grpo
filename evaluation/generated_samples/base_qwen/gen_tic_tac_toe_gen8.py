import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import numpy as np

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Initialize the game board
def initialize_board():
    return np.zeros((6, 6), dtype=int)

# Function to get the initial state of the game
def get_initial_state() -> State:
    # Initial state is an empty board
    return {
        "board": initialize_board(),
        "current_player": 0,
        "winner": None,
        "game_over": False
    }

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Parse the action into row and column
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if state["board"][row][col] != 0:
        raise ValueError("Invalid action: Cell already occupied")

    # Update the board
    state["board"][row][col] = state["current_player"] + 1

    # Switch the current player
    state["current_player"] = 1 - state["current_player"]

    # Check for win condition
    check_winner(state)

    # Check for draw condition
    if np.all(state["board"]):
        state["winner"] = None
        state["game_over"] = True

    return state

# Function to check for a win condition
def check_winner(state: State):
    board = state["board"]
    n = 6

    # Check horizontal lines
    for i in range(n):
        for j in range(n - 3):
            if board[i][j] == board[i][j+1] == board[i][j+2] == board[i][j+3] != 0:
                state["winner"] = state["current_player"] + 1
                state["game_over"] = True

    # Check vertical lines
    for j in range(n):
        for i in range(n - 3):
            if board[i][j] == board[i+1][j] == board[i+2][j] == board[i+3][j] != 0:
                state["winner"] = state["current_player"] + 1
                state["game_over"] = True

    # Check diagonal lines
    for i in range(n - 3):
        for j in range(n - 3):
            if board[i][j] == board[i+1][j+1] == board[i+2][j+2] == board[i+3][j+3] != 0:
                state["winner"] = state["current_player"] + 1
                state["game_over"] = True
            if board[i][j+3] == board[i+1][j+2] == board[i+2][j+1] == board[i+3][j] != 0:
                state["winner"] = state["current_player"] + 1
                state["game_over"] = True

# Function to get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return "Player {}".format(player_id + 1)

# Function to get the rewards per player
def get_rewards(state: State) -> list[float]:
    if state["game_over"]:
        if state["winner"] is None:
            return [0.0, 0.0]  # Draw
        elif state["winner"] == 1:
            return [1.0, 0.0]  # Player 1 wins
        else:
            return [0.0, 1.0]  # Player 2 wins
    else:
        return [0.0, 0.0]  # Not a terminal state yet

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    board = state["board"]
    n = 6
    legal_actions = []

    for i in range(n):
        for j in range(n):
            if board[i][j] == 0:
                legal_actions.append("{},".format(i) + "{}".format(j))
    return legal_actions

# Function to get the observations for each player
def get_observations(state: State) -> list[PlayerObservation]:
    board = state["board"]
    n = 6

    player_0_obs = {}
    player_1_obs = {}

    for i in range(n):
        for j in range(n):
            if board[i][j] == 1:
                player_0_obs[(i, j)] = 1
            elif board[i][j] == 2:
                player_1_obs[(i, j)] = 1

    return [player_0_obs, player_1_obs]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)

    # Simulate a few moves
    state = apply_action(initial_state, "0,0")
    state = apply_action(state, "1,1")
    state = apply_action(state, "2,2")
    state = apply_action(state, "3,3")
    state = apply_action(state, "4,4")
    state = apply_action(state, "5,5")

    print("After Moves:", state)

    # Get current player and rewards
    current_player = get_current_player(state)
    print("Current Player:", get_player_name(current_player))
    print("Rewards:", get_rewards(state))

    # Get legal actions
    legal_actions = get_legal_actions(state)
    print("Legal Actions:", legal_actions)

    # Get observations
    observations = get_observations(state)
    print("Observations:", observations)