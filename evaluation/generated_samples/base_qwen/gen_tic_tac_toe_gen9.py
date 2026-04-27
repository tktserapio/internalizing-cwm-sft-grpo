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

# Helper functions
def create_board():
    """Create a 6x6 board initialized with None values."""
    return {f"{i},{j}": None for i in range(6) for j in range(6)}

def is_valid_action(action):
    """Check if the given action is valid for the current state."""
    row, col = map(int, action.split(","))
    return 0 <= row < 6 and 0 <= col < 6 and board[action] is None

def check_win(board, player):
    """Check if the player has won the game."""
    # Check rows and columns
    for i in range(6):
        if all(board[f"{i},{j}"] == player for j in range(6)) or \
           all(board[f"{j},{i}"] == player for j in range(6)):
            return True
    # Check diagonals
    for i in range(3):  # Only need to check up to 3 since we're looking for 4 in a row
        if all(board[f"{i+j},{i+j}"] == player for j in range(4)) or \
           all(board[f"{i+3-j},{i+j}"] == player for j in range(4)):
            return True
    return False

def get_initial_state():
    """Returns the initial game state before any actions are taken."""
    return {"board": create_board(), "current_player": 0}

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if not is_valid_action(action):
        raise ValueError("Invalid action")
    
    board = state["board"]
    current_player = state["current_player"]
    next_player = 1 - current_player
    
    board[action] = f"X" if current_player == 0 else f"O"
    
    if check_win(board, f"X") or check_win(board, f"O"):
        reward = [1.0, 0.0] if current_player == 0 else [0.0, 1.0]
    elif all(board[cell] is not None for cell in board.keys()):
        reward = [0.5, 0.5]  # Draw condition
    else:
        reward = [0.0, 0.0]
        
    return {
        "board": board,
        "current_player": next_player,
        "reward": reward
    }

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return "Player 1" if player_id == 0 else "Player 2"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    return state["reward"]

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state["board"]
    current_player = state["current_player"]
    legal_actions = []
    
    for action in board.keys():
        if board[action] is None:
            legal_actions.append(action)
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state["board"]
    observations = []
    
    for player in range(2):
        observation = {}
        for cell in board.keys():
            if board[cell] is None:
                observation[cell] = "None"
            elif board[cell] == f"X" if player == 0 else f"O":
                observation[cell] = "Occupied"
        observations.append(observation)
    
    return observations

# Main function to run the game
def main():
    state = get_initial_state()
    print(f"Initial state: {state}")
    
    while True:
        print(f"\nCurrent state: {state}")
        legal_actions = get_legal_actions(state)
        print(f"Legal actions: {legal_actions}")
        
        if not legal_actions:
            print("No legal actions left. It's a draw!")
            break
        
        action = input(f"Player {get_player_name(get_current_player(state))}, enter your move (row,col): ")
        state = apply_action(state, action)
        
        if get_rewards(state)[0] > 0 or get_rewards(state)[1] > 0:
            print(f"Player {get_player_name(get_current_player(state))} wins!")
            break

if __name__ == "__main__":
    main()