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
    # Initial state with empty board
    return {
        'board': {},
        'current_player': 0,
        'turn': 0,
        'winner': None
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if state['winner'] is not None:
        raise ValueError("Game is already over.")
    
    # Parse the action
    row, col = map(int, action.split(','))

    # Update the board
    new_state['board'][f"{row},{col}"] = state['current_player']
    new_state['turn'] += 1
    new_state['current_player'] = (state['current_player'] + 1) % 2

    # Check for win condition
    check_win(new_state)
    
    return new_state

def check_win(state: State) -> None:
    """
    Checks if a player has won the game.
    If a player has formed a connected group touching all three sides, set the winner.
    """
    board = state['board']
    current_player = state['current_player']
    sides = ['A', 'B', 'C']

    # Helper function to check if a given side is connected
    def is_side_connected(side: str) -> bool:
        start = board[f"{side[0]},1"]
        end = board[f"{side[-1]},9"]
        return start == end == current_player

    # Check each side
    for side in sides:
        if is_side_connected(side):
            state['winner'] = current_player
            return

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['winner'] is None:
        return [0.0, 0.0]
    elif state['winner'] == 0:
        return [1.0, 0.0]
    else:
        return [0.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    board = state['board']
    current_player = state['current_player']
    legal_actions = []

    # Iterate through the board and check if a move is possible
    for row in range(10):
        for col in range(1, 10):
            if f"{row},{col}" not in board:
                legal_actions.append(f"{row},{col}")
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    current_player = state['current_player']
    observations = []

    # Create observations for each player
    for player_id in range(2):
        observation = {}
        for row in range(10):
            for col in range(1, 10):
                if f"{row},{col}" in board:
                    if board[f"{row},{col}"] == player_id:
                        observation[f"{row},{col}"] = True
                    else:
                        observation[f"{row},{col}"] = False
        observations.append(observation)
    return observations