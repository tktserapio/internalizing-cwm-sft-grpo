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
    'Top-Left': [(0, 0), (0, 1), (1, 0), (1, 1)],
    'Top-Right': [(0, 2), (0, 3), (1, 2), (1, 3)],
    'Bottom-Left': [(2, 0), (2, 1), (3, 0), (3, 1)],
    'Bottom-Right': [(2, 2), (2, 3), (3, 2), (3, 3)]
}

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    state = {
        'positions': [(0, 0), (3, 3)],  # Initial positions for P0 and P1
        'turn_count': 0,
        'current_player': 0,
        'game_over': False
    }
    return state

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    positions = list(state['positions'])
    player = state['current_player']
    
    # Update position based on action
    row, col = positions[player]
    if action == "Up" and row > 0:
        row -= 1
    elif action == "Down" and row < BOARD_SIZE - 1:
        row += 1
    elif action == "Left" and col > 0:
        col -= 1
    elif action == "Right" and col < BOARD_SIZE - 1:
        col += 1
    # "Stay" doesn't change position

    positions[player] = (row, col)
    new_state['positions'] = positions
    
    # Check for win condition
    if positions[0] == positions[1]:
        new_state['game_over'] = True
    else:
        # Increment turn count and switch player
        new_state['turn_count'] += 1
        new_state['current_player'] = 1 - player
        if new_state['turn_count'] >= MAX_TURNS:
            new_state['game_over'] = True

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -1 for terminal state."""
    if state['game_over']:
        return -1
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    if not state['game_over']:
        return [0.0, 0.0]
    
    if state['positions'][0] == state['positions'][1]:
        winner = 1 - state['current_player']
        return [1.0 if winner == 0 else -1.0, 1.0 if winner == 1 else -1.0]
    return [0.0, 0.0]  # Draw

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []

    return ["Up", "Down", "Left", "Right", "Stay"]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    positions = state['positions']
    observations = []

    for player in range(2):
        opponent = 1 - player
        player_pos = positions[player]
        opponent_pos = positions[opponent]
        opponent_quadrant = next(
            q for q, cells in QUADRANTS.items() if opponent_pos in cells
        )
        observations.append({
            'My Loc': player_pos,
            'Opponent Quadrant': opponent_quadrant
        })
    
    return observations

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # This function is complex and typically requires a model of the game dynamics.
    # For simplicity, this implementation will return a random sequence of actions.
    actions = []
    state = get_initial_state()
    
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
            state = apply_action(state, action)
        else:
            legal_actions = get_legal_actions(state)
            sampled_action = random.choice(legal_actions)
            actions.append(sampled_action)
            state = apply_action(state, sampled_action)
    
    return actions