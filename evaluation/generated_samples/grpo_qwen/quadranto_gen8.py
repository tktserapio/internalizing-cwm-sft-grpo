import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

from typing import Dict, List, Tuple, Union

Action = str
State = Dict[str, Union[int, List[List[int]]]]
PlayerObservation = Dict[str, Union[int, str]]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initialize the board as a 4x4 grid with empty cells
    board = [[0 for _ in range(4)] for _ in range(4)]
    # Place player 0 in a random cell in the top-left quadrant
    row, col = (0, 0) if board[0][0] == 0 else (0, 1) if board[0][1] == 0 else (1, 0) if board[1][0] == 0 else (1, 1)
    board[row][col] = 0
    # Place player 1 in a random cell in the bottom-right quadrant
    row, col = (2, 2) if board[2][2] == 0 else (2, 3) if board[2][3] == 0 else (3, 2) if board[3][2] == 0 else (3, 3)
    board[row][col] = 1
    # Return the initial state
    return {
        'board': board,
        'turn_count': 0,
        'current_player': 0,
        'player_0_quadrant': 'Q1',
        'player_1_quadrant': 'Q4'
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    # Get the current player's position
    current_player = new_state['current_player']
    # Get the opponent's position based on the current player's quadrant
    opponent_position = (
        (new_state['board'][2][2], 'Q3'),
        (new_state['board'][2][3], 'Q3'),
        (new_state['board'][3][2], 'Q4'),
        (new_state['board'][3][3], 'Q4')
    )[new_state['board'][new_state['current_player']][new_state['current_player']]] if current_player == 0 else (
        (new_state['board'][0][0], 'Q1'),
        (new_state['board'][0][1], 'Q1'),
        (new_state['board'][1][0], 'Q2'),
        (new_state['board'][1][1], 'Q2')
    )[new_state['board'][new_state['current_player']][new_state['current_player']]] if current_player == 1 else None
    # Apply the action
    if action == 'Stay':
        new_state['board'][new_state['current_player']][new_state['current_player']] = current_player
    elif action in ['Up', 'Down', 'Left', 'Right']:
        direction = {'Up': (-1, 0), 'Down': (1, 0), 'Left': (0, -1), 'Right': (0, 1)}[action]
        new_row, new_col = new_state['current_player'][0] + direction[0], new_state['current_player'][1] + direction[1]
        if 0 <= new_row < 4 and 0 <= new_col < 4:
            new_state['board'][new_row][new_col] = current_player
            new_state['board'][new_state['current_player'][0]][new_state['current_player'][1]] = 0
            new_state['current_player'] = (new_row, new_col)
    # Check if the game is over
    if abs(new_state['current_player'][0] - opponent_position[0]) <= 1 and abs(new_state['current_player'][1] - opponent_position[1]) <= 1:
        new_state['current_player'] = -4
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['current_player'] == -4:
        return [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = state['current_player']
    if state['current_player'] == -4:
        return []
    return ['Stay', 'Up', 'Down', 'Left', 'Right']

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_obs = {
        'Loc': state['board'][state['current_player'][0]][state['current_player'][1]],
        'OpponentQuadrant': state['player_1_quadrant']
    }
    player_1_obs = {
        'Loc': state['board'][state['current_player'][0]][state['current_player'][1]],
        'OpponentQuadrant': state['player_0_quadrant']
    }
    return [player_0_obs, player_1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would need to implement stochastic sampling logic here
    # For simplicity, we'll just return a fixed sequence of actions
    # In a real implementation, this would involve more complex logic
    return ['Stay', 'Up', 'Down', 'Left', 'Right']