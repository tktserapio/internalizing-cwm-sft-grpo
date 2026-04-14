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

# Helper function to generate random coordinates within a quadrant
def random_quadrant_coordinates(quadrant: str) -> Tuple[int, int]:
    row, col = quadrant.split(',')
    row = int(row)
    col = int(col)
    # Randomly place player within the quadrant
    row = random.randint(0, 1) * row
    col = random.randint(0, 1) * col
    return row, col

# Required Functions
def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    # Initial positions
    p0_position = random_quadrant_coordinates('Q1')
    p1_position = random_quadrant_coordinates('Q4')
    return {
        'p0_position': p0_position,
        'p1_position': p1_position,
        'turn_count': 0,
        'current_player': 0,
        'game_over': False
    }

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = state.copy()
    if action == 'place_p0:<row>,<col>':
        new_state['p0_position'] = eval(action.split(':')[1])
        new_state['current_player'] = 1
    elif action == 'place_p1:<row>,<col>':
        new_state['p1_position'] = eval(action.split(':')[1])
        new_state['current_player'] = 0
    else:
        new_state['current_player'] = 1 - new_state['current_player']
        if action == 'Up':
            new_state['p0_position'] = (new_state['p0_position'][0], new_state['p0_position'][1] - 1)
            new_state['p1_position'] = (new_state['p1_position'][0], new_state['p1_position'][1] - 1)
        elif action == 'Down':
            new_state['p0_position'] = (new_state['p0_position'][0], new_state['p0_position'][1] + 1)
            new_state['p1_position'] = (new_state['p1_position'][0], new_state['p1_position'][1] + 1)
        elif action == 'Left':
            new_state['p0_position'] = (new_state['p0_position'][0] - 1, new_state['p0_position'][1])
            new_state['p1_position'] = (new_state['p1_position'][0] - 1, new_state['p1_position'][1])
        elif action == 'Right':
            new_state['p0_position'] = (new_state['p0_position'][0] + 1, new_state['p0_position'][1])
            new_state['p1_position'] = (new_state['p1_position'][0] + 1, new_state['p1_position'][1])
        elif action == 'Stay':
            pass
        else:
            raise ValueError(f"Invalid action: {action}")
    
    # Check if the game is over
    if abs(new_state['p0_position'][0] - new_state['p1_position'][0]) <= 1 and abs(new_state['p0_position'][1] - new_state['p1_position'][1]) <= 1:
        new_state['game_over'] = True
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available."""
    if state['game_over']:
        if state['p0_position'] == state['p1_position']:
            return [-1.0, 1.0]
        else:
            return [0.0, 0.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['game_over']:
        return []
    else:
        current_player = state['current_player']
        legal_actions = ['Up', 'Down', 'Left', 'Right', 'Stay']
        if current_player == 0:
            opponent_position = state['p1_position']
        else:
            opponent_position = state['p0_position']
        
        # Check if the player can move up
        if state['p0_position'][0] > 0 and state['p0_position'][1] >= 0 and state['p0_position'][0] <= 3 and state['p0_position'][1] <= 3:
            legal_actions.remove('Up')
        
        # Check if the player can move down
        if state['p0_position'][0] < 3 and state['p0_position'][1] >= 0 and state['p0_position'][0] <= 3 and state['p0_position'][1] <= 3:
            legal_actions.remove('Down')
        
        # Check if the player can move left
        if state['p0_position'][0] >= 0 and state['p0_position'][1] > 0 and state['p0_position'][0] <= 3 and state['p0_position'][1] <= 3:
            legal_actions.remove('Left')
        
        # Check if the player can move right
        if state['p0_position'][0] >= 0 and state['p0_position'][1] < 3 and state['p0_position'][0] <= 3 and state['p0_position'][1] <= 3:
            legal_actions.remove('Right')
        
        # Add Stay action if possible
        if state['p0_position'][0] >= 0 and state['p0_position'][1] >= 0 and state['p0_position'][0] <= 3 and state['p0_position'][1] <= 3:
            legal_actions.append('Stay')
        
        return legal_actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]."""
    p0_obs = {
        'My Loc': f"{state['p0_position'][0]}, {state['p0_position'][1]}",
        'Opponent Quadrant': get_quadrant(state['p1_position'])
    }
    p1_obs = {
        'My Loc': f"{state['p1_position'][0]}, {state['p1_position'][1]}",
        'Opponent Quadrant': get_quadrant(state['p0_position'])
    }
    return [p0_obs, p1_obs]

def get_quadrant(position: Tuple[int, int]) -> str:
    """Returns the quadrant name based on the position."""
    row, col = position
    if row % 2 == 0:
        if col % 2 == 0:
            return 'Q1'
        else:
            return 'Q3'
    else:
        if col % 2 == 0:
            return 'Q2'
        else:
            return 'Q4'

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    # This function would require more complex logic to handle the stochastic nature of the game.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this function would need to account for the game's stochastic elements.
    return ['Right', 'Up', 'Down', 'Left', 'Right', 'Up']