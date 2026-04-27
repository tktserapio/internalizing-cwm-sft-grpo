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

# Helper function to create an initial state
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [' ' for _ in range(10)],
        'current_player': 0,
        'winner': None
    }

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    # Convert action string to tuple
    row, col = map(int, action.split(','))

    # Check if the action is valid
    if state['board'][row * 3 + col] != ' ':
        raise ValueError("Invalid move: Cell already occupied")

    # Update the board
    state['board'][row * 3 + col] = 'B' if state['current_player'] == 0 else 'W'

    # Switch the current player
    state['current_player'] = 1 - state['current_player']

    # Check for win condition
    check_winner(state)

    return state

# Check if there's a winner
def check_winner(state: State):
    board = state['board']
    # Check rows, columns, and diagonals
    for i in range(3):
        if board[i*3] == board[i*3+1] == board[i*3+2] != ' ':
            state['winner'] = 1 - state['current_player']
            return
        if board[i] == board[i+3] == board[i+6] != ' ':
            state['winner'] = 1 - state['current_player']
            return
    if board[0] == board[4] == board[8] != ' ':
        state['winner'] = 1 - state['current_player']
    if board[2] == board[4] == board[6] != ' ':
        state['winner'] = 1 - state['current_player']

# Get the current player
def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return 'Black' if player_id == 0 else 'White'

# Get rewards per player
def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['winner'] is not None:
        return [1.0, -1.0] if state['winner'] == 0 else [-1.0, 1.0]
    return [0.0, 0.0]

# Get legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['winner'] is not None:
        return []
    return [f"{i},{j}" for i in range(3) for j in range(3) if state['board'][i*3+j] == ' ']

# Get observations for each player
def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    board = state['board']
    obs_0 = {'board': board[:9], 'legal_moves': get_legal_actions(state)}
    obs_1 = {'board': board[:9], 'legal_moves': get_legal_actions(state)}
    return [obs_0, obs_1]