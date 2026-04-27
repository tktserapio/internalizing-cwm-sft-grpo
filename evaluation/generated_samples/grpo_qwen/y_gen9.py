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

# Helper function to convert coordinates to action string
def coord_to_action(coord: Tuple[int, int]) -> Action:
    return f"{coord[0]},{coord[1]}"

# Initial state of the game
def get_initial_state() -> State:
    # Initialize the board as a dictionary with empty lists for each cell
    return {
        "board": [
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None],
            [None, None, None, None, None]
        ],
        "current_player": 0,
        "winner": None
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Convert the action string to coordinates
    row, col = map(int, action.split(","))
    # Check if the action is valid
    if state["board"][row][col] is not None:
        raise ValueError("Cell already occupied")
    
    # Update the board with the current player's move
    state["board"][row][col] = state["current_player"] + 1
    
    # Switch the current player
    state["current_player"] = 1 - state["current_player"]
    
    # Check for win condition
    check_winner(state)
    
    return state

# Check if there is a winner
def check_winner(state: State) -> None:
    board = state["board"]
    current_player = state["current_player"] + 1
    opponent_player = 2 - current_player
    
    # Define the sides of the board
    sides = {
        "A-B": [(0, 1), (1, 3), (2, 6)],
        "A-C": [(0, 2), (1, 5), (2, 9)],
        "B-C": [(2, 6), (3, 7), (4, 8), (4, 9)]
    }
    
    # Check each side for a connected path
    for side, cells in sides.items():
        for cell in cells:
            if board[cell[0]][cell[1]] == current_player:
                # Find all connected cells
                queue = [cell]
                visited = set()
                while queue:
                    r, c = queue.pop(0)
                    if (r, c) in visited:
                        continue
                    visited.add((r, c))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < len(board) and 0 <= nc < len(board[0]) and board[nr][nc] == current_player and (nr, nc) not in visited:
                            queue.append((nr, nc))
                
                # If the path connects to the other side, declare the current player as the winner
                if (len(visited) > 1 and any(cell in visited for cell in cells)) or (len(visited) == 1 and board[cell[0]][cell[1]] == opponent_player):
                    state["winner"] = current_player
                    return

# Get the current player
def get_current_player(state: State) -> int:
    return state["current_player"]

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return "Black" if player_id == 0 else "White"

# Get the rewards per player
def get_rewards(state: State) -> List[float]:
    if state["winner"] is None:
        return [0.0, 0.0]
    elif state["winner"] == 0:
        return [1.0, 0.0]
    else:
        return [0.0, 1.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    board = state["board"]
    current_player = state["current_player"] + 1
    legal_actions = []
    
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] is None:
                legal_actions.append(coord_to_action((row, col)))
    
    return legal_actions

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    board = state["board"]
    current_player = state["current_player"] + 1
    opponent_player = 2 - current_player
    
    # Create observations for both players
    player_0_obs = {
        "board": [[board[r][c] if c == 0 else None for c in range(len(board[r]))] for r in range(len(board))],
        "current_player": current_player,
        "winner": state["winner"]
    }
    
    player_1_obs = {
        "board": [[board[r][c] if c == 4 else None for c in range(len(board[r]))] for r in range(len(board))],
        "current_player": opponent_player,
        "winner": state["winner"]
    }
    
    return [player_0_obs, player_1_obs]