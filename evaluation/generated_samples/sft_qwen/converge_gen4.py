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

# Helper functions
def is_valid_move(action: Action, state: State) -> bool:
    """Check if the given action is valid in the current state."""
    # Extract source and destination coordinates from the action string
    src_row, src_col = map(int, action.split(' to ')[0].split(','))
    dst_row, dst_col = map(int, action.split(' to ')[1].split(','))
    
    # Check if the source and destination are within the board boundaries
    if not (0 <= src_row < 5 and 0 <= src_col < 5 and 0 <= dst_row < 5 and 0 <= dst_col < 5):
        return False
    
    # Check if the source and destination squares are empty
    if state.get(f'{src_row},{src_col}') == 'occupied':
        return False
    
    # Check if the destination square is already occupied
    if state.get(f'{dst_row},{dst_col}') == 'occupied':
        return False
    
    return True

def apply_action(state: State, action: Action) -> State:
    """Apply the given action to the state and return the new state."""
    new_state = copy.deepcopy(state)
    # Extract source and destination coordinates from the action string
    src_row, src_col = map(int, action.split(' to ')[0].split(','))
    dst_row, dst_col = map(int, action.split(' to ')[1].split(','))
    
    # Update the state with the new position of the unit
    new_state[f'{dst_row},{dst_col}'] = 'occupied'
    new_state.pop(f'{src_row},{src_col}')
    
    # Check if the destination square is adjacent to an opponent's unit
    opponent_units = [f'{row},{col}' for row in range(5) for col in range(5) if state.get(f'{row},{col}') == 'opponent']
    for opp_unit in opponent_units:
        opp_row, opp_col = map(int, opp_unit.split(','))
        if abs(dst_row - opp_row) + abs(dst_col - opp_col) == 1:
            new_state[opp_unit] = 'stunned'
    
    return new_state

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    initial_state = {
        '0,0': 'occupied',  # Player 0 (Blue) unit at (0, 0)
        '0,4': 'occupied',  # Player 0 (Blue) unit at (0, 4)
        '4,0': 'opponent',  # Player 1 (Red) unit at (4, 0)
        '4,4': 'opponent',  # Player 1 (Red) unit at (4, 4)
        '2,2': 'empty'      # Center Square (2, 2) is empty
    }
    return initial_state

def get_current_player(state: State) -> int:
    """Returns current player (e.g. 0 or 1), or -4 for terminal state."""
    blue_units = [pos for pos, unit in state.items() if unit == 'occupied' and pos.startswith('0')]
    red_units = [pos for pos, unit in state.items() if unit == 'occupied' and pos.startswith('4')]
    
    if len(blue_units) > 0 and len(red_units) > 0:
        return 0 if blue_units[0] < red_units[0] else 1
    elif len(blue_units) > 0:
        return 0
    elif len(red_units) > 0:
        return 1
    else:
        return -4  # Terminal state

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return ['Blue', 'Red'][player_id]

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player. May return non-zero values at non-terminal states if the game tracks running rewards."""
    if get_current_player(state) == -4:
        return [0.0, 0.0]  # Terminal state
    else:
        return [0.0, 0.0]  # Non-terminal state

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    current_player = get_current_player(state)
    if current_player == -4:
        return []  # Terminal state
    else:
        legal_actions = []
        for unit_pos, unit_type in state.items():
            if unit_type == 'occupied':
                for adj_pos in [(unit_pos[0]-1, unit_pos[1]-1), (unit_pos[0]-1, unit_pos[1]), (unit_pos[0]-1, unit_pos[1]+1),
                                (unit_pos[0], unit_pos[1]-1), (unit_pos[0], unit_pos[1]+1),
                                (unit_pos[0]+1, unit_pos[1]-1), (unit_pos[0]+1, unit_pos[1]), (unit_pos[0]+1, unit_pos[1]+1)]:
                    if adj_pos in state and state[adj_pos] == 'empty':
                        legal_actions.append(f'move {unit_pos} to {adj_pos}')
        return legal_actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. For perfect info games, both see the same state."""
    player_0_obs = {}
    player_1_obs = {}
    for row in range(5):
        for col in range(5):
            if f'{row},{col}' in state:
                player_0_obs[f'{row},{col}'] = state[f'{row},{col}']
                player_1_obs[f'{row},{col}'] = state[f'{row},{col}']
    return [player_0_obs, player_1_obs]