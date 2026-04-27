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

# Helper function to convert coordinates to algebraic notation
def coord_to_algebraic(coord: str) -> str:
    file, rank = coord
    return f"{file}{rank}"

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial board setup
    initial_board = {
        "a1": "R", "b1": "N", "c1": "B", "d1": "Q", "e1": "K",
        "a2": "P", "b2": "P", "c2": "P", "d2": "P", "e2": "P",
        "a3": ".", "b3": ".", "c3": ".", "d3": ".", "e3": ".",
        "a4": ".", "b4": ".", "c4": ".", "d4": ".", "e4": ".",
        "a5": "r", "b5": "n", "c5": "b", "d5": "q", "e5": "k"
    }
    return {"board": initial_board}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    from_coord, to_coord = action.split("_")
    from_file, from_rank = from_coord
    to_file, to_rank = to_coord
    
    # Convert coordinates to algebraic notation
    from_algebraic = coord_to_algebraic(from_coord)
    to_algebraic = coord_to_algebraic(to_coord)
    
    # Get the piece at the from coordinate
    piece = new_state["board"].pop(from_algebraic)
    
    # Place the piece at the to coordinate
    new_state["board"][to_algebraic] = piece
    
    # Update the board state
    new_state["board"] = new_state["board"]
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    # Determine the current player based on whose turn it is
    if state["board"]["e1"] == "K":
        return 0
    elif state["board"]["e5"] == "K":
        return 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    if player_id == 0:
        return "White"
    elif player_id == 1:
        return "Black"
    else:
        return "Unknown"

def get_rewards(state: State) -> List[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # Determine the winner based on the current state
    if state["board"]["e1"] == "K":
        return [-1.0, 1.0]
    elif state["board"]["e5"] == "K":
        return [1.0, -1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    # Check if the game is over
    if state["board"]["e1"] == "K" or state["board"]["e5"] == "K":
        return []
    
    # Collect all possible actions
    legal_actions = []
    for file in "abcde":
        for rank in "12345":
            from_coord = f"{file}{rank}"
            if state["board"][from_coord] != ".":
                # Pawn movement
                if state["board"][from_coord] == "P":
                    for to_rank in "12345":
                        to_coord = f"{file}{to_rank}"
                        if to_rank != rank and state["board"][to_coord] == ".":
                            legal_actions.append(f"P_{from_coord}_{to_coord}")
                        if to_rank == "1" and state["board"][to_coord] == ".":
                            legal_actions.append(f"P_{from_coord}_{to_coord}_Q")
                            legal_actions.append(f"P_{from_coord}_{to_coord}_R")
                            legal_actions.append(f"P_{from_coord}_{to_coord}_B")
                            legal_actions.append(f"P_{from_coord}_{to_coord}_N")
                # Other pieces movement
                else:
                    for to_file in "abcde":
                        to_coord = f"{to_file}{rank}"
                        if state["board"][to_coord] == ".":
                            legal_actions.append(f"{state['board'][from_coord]}_{from_coord}_{to_coord}")
                        if state["board"][to_coord] != ".":
                            captured_piece = state["board"][to_coord]
                            legal_actions.append(f"{state['board'][from_coord]}_{from_coord}_{to_coord}_{captured_piece}")
    
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    # Get the current board state
    board = state["board"]
    
    # Create observations for each player
    player_0_obs = {coord: piece for coord, piece in board.items() if coord[0] in "abcde"}
    player_1_obs = {coord: piece for coord, piece in board.items() if coord[0] in "abcde"}
    
    return [player_0_obs, player_1_obs]