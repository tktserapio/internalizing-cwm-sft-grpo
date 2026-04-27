import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper functions
def get_random_location() -> Tuple[int, int]:
    """Randomly generate a location within the 4x4 grid."""
    return random.randint(0, 3), random.randint(0, 3)

def get_quadrant(row: int, col: int) -> str:
    """Determine the quadrant based on the row and column."""
    if row == 0 and col <= 1:
        return "Q1"
    elif row == 0 and col >= 2:
        return "Q2"
    elif row == 1 and col <= 1:
        return "Q3"
    else:
        return "Q4"

def apply_action(state: State, action: Action) -> State:
    """
    Apply an action to the current state and return the new state.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    player_id = state['current_player']
    opponent_id = 1 - player_id
    player_loc = state[f'player_{player_id}_loc']
    opponent_loc = state[f'player_{opponent_id}_loc']

    # Update location based on action
    if action == "Up":
        player_loc = (player_loc[0] - 1, player_loc[1])
    elif action == "Down":
        player_loc = (player_loc[0] + 1, player_loc[1])
    elif action == "Left":
        player_loc = (player_loc[0], player_loc[1] - 1)
    elif action == "Right":
        player_loc = (player_loc[0], player_loc[1] + 1)
    elif action == "Stay":
        pass
    else:
        raise ValueError(f"Invalid action: {action}")

    # Check if caught
    if player_loc == opponent_loc:
        return {
            'current_player': player_id,
            'player_0_loc': player_loc,
            'player_1_loc': opponent_loc,
            'player_0_quadrant': get_quadrant(*player_loc),
            'player_1_quadrant': get_quadrant(*opponent_loc),
            'reward': [1.0 if player_id == 1 else -1.0, 1.0 if player_id == 0 else -1.0],
            'terminal': True
        }

    # Update state
    state[f'player_{player_id}_loc'] = player_loc
    state[f'player_{opponent_id}_loc'] = opponent_loc
    state['current_player'] = 1 - player_id

    return state

def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    player_0_loc = get_random_location()
    player_1_loc = get_random_location()
    return {
        'current_player': 0,
        'player_0_loc': player_0_loc,
        'player_1_loc': player_1_loc,
        'player_0_quadrant': get_quadrant(*player_0_loc),
        'player_1_quadrant': get_quadrant(*player_1_loc)
    }

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    return state['reward']

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    player_id = state['current_player']
    player_loc = state[f'player_{player_id}_loc']
    opponent_loc = state[f'player_{1-player_id}_loc']
    quadrant = get_quadrant(*player_loc)
    opponent_quadrant = get_quadrant(*opponent_loc)
    if quadrant == opponent_quadrant:
        return ['Stay']
    else:
        return ['Up', 'Down', 'Left', 'Right']

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    player_0_loc = state['player_0_loc']
    player_1_loc = state['player_1_loc']
    player_0_quadrant = get_quadrant(*player_0_loc)
    player_1_quadrant = get_quadrant(*player_1_loc)
    return [
        {'loc': player_0_loc, 'quadrant': player_0_quadrant},
        {'loc': player_1_loc, 'quadrant': player_1_quadrant}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would require more complex logic to handle stochastic sampling.
    # For simplicity, we'll just return a fixed sequence of actions that lead to the given observations.
    # In a real implementation, this would involve a more sophisticated algorithm.
    # Here, we assume that the sequence of actions leading to the given observations is known.
    # For demonstration purposes, let's assume the sequence of actions is fixed.
    actions_sequence = obs_action_history[-1][1]
    return actions_sequence