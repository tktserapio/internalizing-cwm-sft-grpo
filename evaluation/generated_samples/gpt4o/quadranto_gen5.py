import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, List, Tuple, Dict

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
BOARD_SIZE = 4
MAX_TURNS = 20
QUADRANTS = {
    (0, 0): "Top-Left",
    (0, 1): "Top-Left",
    (1, 0): "Top-Left",
    (1, 1): "Top-Left",
    (0, 2): "Top-Right",
    (0, 3): "Top-Right",
    (1, 2): "Top-Right",
    (1, 3): "Top-Right",
    (2, 0): "Bottom-Left",
    (2, 1): "Bottom-Left",
    (3, 0): "Bottom-Left",
    (3, 1): "Bottom-Left",
    (2, 2): "Bottom-Right",
    (2, 3): "Bottom-Right",
    (3, 2): "Bottom-Right",
    (3, 3): "Bottom-Right"
}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    state = {
        'player_positions': {
            0: (random.choice([0, 1]), random.choice([0, 1])),  # Player 0 in Top-Left
            1: (random.choice([2, 3]), random.choice([2, 3]))   # Player 1 in Bottom-Right
        },
        'current_player': 0,
        'turn_count': 0,
        'game_over': False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    new_state['player_positions'] = state['player_positions'].copy()
    
    player = state['current_player']
    row, col = state['player_positions'][player]
    
    if action == "Up":
        row = max(0, row - 1)
    elif action == "Down":
        row = min(BOARD_SIZE - 1, row + 1)
    elif action == "Left":
        col = max(0, col - 1)
    elif action == "Right":
        col = min(BOARD_SIZE - 1, col + 1)
    
    new_state['player_positions'][player] = (row, col)
    
    # Check for win condition
    if new_state['player_positions'][0] == new_state['player_positions'][1]:
        new_state['game_over'] = True
    else:
        new_state['turn_count'] += 1
        if new_state['turn_count'] >= MAX_TURNS:
            new_state['game_over'] = True
        else:
            new_state['current_player'] = 1 - player
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -1 for terminal state."""
    return -1 if state['game_over'] else state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state['game_over']:
        return [0.0, 0.0]
    
    if state['player_positions'][0] == state['player_positions'][1]:
        winner = state['current_player']
        loser = 1 - winner
        return [1.0 if i == winner else -1.0 for i in range(2)]
    else:
        return [0.0, 0.0]  # Draw

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []
    return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    observations = []
    for player in range(2):
        opponent = 1 - player
        player_pos = state['player_positions'][player]
        opponent_pos = state['player_positions'][opponent]
        observations.append({
            "My Loc": player_pos,
            "Opponent Quadrant": QUADRANTS[opponent_pos]
        })
    return observations

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function would require a more complex implementation to fully simulate
    # the stochastic nature of the game. For simplicity, we'll return a random
    # sequence of actions that could have led to the current state.
    actions = []
    state = get_initial_state()
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
            state = apply_action(state, action)
    return actions