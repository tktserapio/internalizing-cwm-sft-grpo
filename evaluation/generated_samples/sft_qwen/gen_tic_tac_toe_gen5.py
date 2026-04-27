import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to check if a player has won
def check_win(board: List[List[int]], player: int, win_length: int) -> bool:
    # Check horizontal lines
    for row in board:
        if all(cell == player for cell in row[:win_length]):
            return True
    # Check vertical lines
    for col in range(len(board)):
        if all(board[row][col] == player for row in range(win_length)):
            return True
    # Check diagonal lines
    for i in range(len(board) - win_length + 1):
        if all(board[i + j][j] == player for j in range(win_length)):
            return True
        if all(board[i + j][len(board) - 1 - j] == player for j in range(win_length)):
            return True
    return False

# Initial state
def get_initial_state() -> State:
    return {
        "board": [[0 for _ in range(6)] for _ in range(6)],
        "current_player": 0,
        "winner": None,
        "draw": False
    }

# Apply action to the state
def apply_action(state: State, action: Action) -> State:
    row, col = map(int, action.split(","))
    if state["board"][row][col] != 0:
        raise ValueError("Cell is already occupied.")
    state["board"][row][col] = state["current_player"] + 1  # Marking as 1 for 'x', 2 for 'o'
    state["current_player"] = 1 - state["current_player"]
    if check_win(state["board"], state["current_player"] + 1, 4):
        state["winner"] = state["current_player"] + 1
        state["draw"] = False
    elif all(all(cell != 0 for cell in row) for row in state["board"]):
        state["draw"] = True
        state["winner"] = None
    return state

# Get current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get player name
def get_player_name(player_id: int) -> str:
    return "Player " + str(player_id + 1)

# Get rewards
def get_rewards(state: State) -> List[float]:
    if state["winner"] is not None:
        return [1.0, 0.0] if state["winner"] == 1 else [0.0, 1.0]
    elif state["draw"]:
        return [0.5, 0.5]
    else:
        return [0.0, 0.0]

# Get legal actions
def get_legal_actions(state: State) -> List[Action]:
    legal_actions = []
    for row in range(6):
        for col in range(6):
            if state["board"][row][col] == 0:
                legal_actions.append(f"{row},{col}")
    return legal_actions

# Get observations
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_board = [[cell for cell in row] for row in state["board"]]
    player_1_board = [[6 - cell for cell in row] for row in state["board"]]
    return [
        {"board": player_0_board, "legal_actions": get_legal_actions(state)},
        {"board": player_1_board, "legal_actions": get_legal_actions(state)}
    ]

# Example usage
if __name__ == "__main__":
    initial_state = get_initial_state()
    print("Initial State:", initial_state)
    
    # Simulate a few moves
    state = apply_action(initial_state, "0,0")
    print("After Move 1:", state)
    
    state = apply_action(state, "1,1")
    print("After Move 2:", state)
    
    state = apply_action(state, "2,2")
    print("After Move 3:", state)
    
    state = apply_action(state, "3,3")
    print("After Move 4:", state)
    
    state = apply_action(state, "4,4")
    print("After Move 5:", state)
    
    state = apply_action(state, "5,5")
    print("After Move 6:", state)
    
    print("Final State:", state)