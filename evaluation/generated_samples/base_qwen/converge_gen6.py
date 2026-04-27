import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import copy

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to create a new state
def create_new_state(state: State, action: Action) -> State:
    new_state = copy.deepcopy(state)
    return new_state

# Required Functions
def get_initial_state() -> State:
    """
    Returns the initial game state before any actions are taken.
    """
    # Initial positions for Blue (Player 0) and Red (Player 1)
    initial_positions = {
        'blue': [(0, 0), (0, 4)],
        'red': [(4, 0), (4, 4)]
    }
    return {'board': initial_positions}

def apply_action(state: State, action: Action) -> State:
    """
    Returns the new state after an action has been taken.
    Ensure that the previous state is not mutated; always return a new state object.
    """
    new_state = create_new_state(state, action)
    # Extract the player ID from the action string
    player_id = int(action.split(' ')[1])
    
    # Check if the action is to pass
    if action == 'pass':
        return new_state
    
    # Parse the source and destination coordinates
    src = tuple(map(int, action.split()[2].split(',')))
    dest = tuple(map(int, action.split()[4].split(',')))
    
    # Check if the source and destination are within bounds
    if not (0 <= src[0] < 5 and 0 <= src[1] < 5):
        raise ValueError("Source position out of bounds")
    if not (0 <= dest[0] < 5 and 0 <= dest[1] < 5):
        raise ValueError("Destination position out of bounds")
    
    # Check if the source position is occupied by the player's unit
    if src not in state['board'][str(player_id)]:
        raise ValueError("Source position is not occupied by the player's unit")
    
    # Check if the destination position is empty
    if dest in state['board'][str(player_id)]:
        raise ValueError("Destination position is already occupied by the player's unit")
    
    # Check if the destination position is adjacent to an opponent's unit
    opponent_units = state['board'][str(3 - player_id)]
    for opp_unit in opponent_units:
        if abs(src[0] - opp_unit[0]) + abs(src[1] - opp_unit[1]) == 1:
            # Apply stun mechanic
            opponent_units.remove(opp_unit)
            opponent_units.append((opp_unit[0], opp_unit[1]))
            opponent_units.append((opp_unit[0], opp_unit[1]))
            break
    
    # Update the board with the new position
    new_state['board'][str(player_id)].remove(src)
    new_state['board'][str(player_id)].append(dest)
    
    return new_state

def get_current_player(state: State) -> int:
    """
    Returns current player (e.g. 0 or 1), or -4 for terminal state.
    """
    blue_units = state['board']['0']
    red_units = state['board']['1']
    
    # Check if there are units left for either player
    if len(blue_units) > 0:
        return 0
    elif len(red_units) > 0:
        return 1
    else:
        return -4

def get_player_name(player_id: int) -> str:
    """
    Returns the name of the player.
    """
    return ['Blue', 'Red'][player_id]

def get_rewards(state: State) -> list[float]:
    """
    Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards (e.g., current scores or chip stacks); otherwise returns [0.0, 0.0] until meaningful reward information is available.
    """
    # In this simple implementation, we assume a win is worth 1 point and a loss is worth -1 point
    if get_current_player(state) == 0:
        return [1.0, -1.0]
    elif get_current_player(state) == 1:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_legal_actions(state: State) -> list[Action]:
    """
    Returns legal actions for current state. Empty list if terminal.
    """
    legal_actions = []
    player_id = get_current_player(state)
    
    if player_id == -4:
        return []  # Terminal state
    
    for unit in state['board'][str(player_id)]:
        for i in range(5):
            for j in range(5):
                if (i, j) != unit and (abs(i - unit[0]) + abs(j - unit[1]) <= 1):
                    # Generate move action
                    move_action = f'move {unit} to {(i, j)}'
                    legal_actions.append(move_action)
        
        # Generate pass action
        legal_actions.append('pass')
    
    return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """
    Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state.
    """
    observations = []
    player_0_obs = {}
    player_1_obs = {}
    
    for unit in state['board']['0']:
        player_0_obs[unit] = True
    for unit in state['board']['1']:
        player_1_obs[unit] = True
    
    observations.append(player_0_obs)
    observations.append(player_1_obs)
    
    return observations