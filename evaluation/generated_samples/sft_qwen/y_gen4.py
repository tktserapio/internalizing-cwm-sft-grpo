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

# Helper function to check if a move connects all three sides
def is_winner(state: State, player: int) -> bool:
    # Extracting the board state from the state dictionary
    board = state['board']
    # Checking if the player's stones form a connected path across all three sides
    for side in ['A', 'B', 'C']:
        for cell in board[side]:
            if board[cell][player] == 1:  # 1 indicates a stone of the given player
                if all(board[cell][opponent] == 1 for opponent in ['A', 'B', 'C'] if opponent != side):
                    return True
    return False

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': {
            'A': {'1': 0, '2': 0, '3': 0, '6': 0},
            'B': {'4': 0, '7': 0, '8': 0, '9': 0},
            'C': {'5': 0, '9': 0}
        },
        'current_player': 0,
        'turn': 0,
        'size': 4
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    # Convert action string to tuple
    row, col = map(int, action.split(','))
    # Check if the action is valid
    if state['board'][f'{state["current_player"]}{row + 1}'][col] == 0:
        new_state['board'][f'{state["current_player"]}{row + 1}'][col] = 1
        new_state['turn'] += 1
        new_state['current_player'] = (new_state['current_player'] + 1) % 2
        # Check if the move makes the player a winner
        if is_winner(new_state, new_state['current_player']):
            new_state['game_over'] = True
            new_state['winner'] = new_state['current_player']
        else:
            new_state['game_over'] = False
    else:
        raise ValueError("Invalid move: Cell is already occupied.")
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f'Player {player_id}' if player_id >= 0 else 'Game Over'

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['game_over']:
        return [-1.0, 1.0] if state['winner'] == 0 else [1.0, -1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    legal_actions = []
    for row in range(state['size']):
        for col in range(state['size']):
            if state['board'][f'{state["current_player"]}{row + 1}'][col] == 0:
                legal_actions.append(f'{row},{col}')
    return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    observations = []
    for player in [0, 1]:
        obs = {}
        for side in ['A', 'B', 'C']:
            obs[side] = {}
            for cell in state['board'][side]:
                obs[side][cell] = state['board'][side][cell]
        observations.append(obs)
    return observations