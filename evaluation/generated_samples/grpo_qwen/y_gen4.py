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

# Helper function to convert coordinates to action string
def coord_to_action(coord: Tuple[int, int]) -> Action:
    return f"{coord[0]},{coord[1]}"

# Required Functions
def get_initial_state() -> State:
    # Initial state with an empty board
    return {
        'board': {},
        'current_player': 0,
        'winner': -4
    }

def apply_action(state: State, action: Action) -> State:
    # Convert action string to coordinate tuple
    coord = tuple(map(int, action.split(',')))
    
    # Check if the action is valid
    if coord not in state['board']:
        state['board'][coord] = state['current_player']
        state['current_player'] = 1 - state['current_player']
        return state
    
    return state

def get_current_player(state: State) -> int:
    return state['current_player']

def get_player_name(player_id: int) -> str:
    return 'Black' if player_id == 0 else 'White'

def get_rewards(state: State) -> List[float]:
    # Determine the winner and calculate rewards
    if state['winner'] != -4:
        return [1.0, 0.0] if state['winner'] == 0 else [0.0, 1.0]
    
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    # Get all empty cells as legal actions
    return [coord_to_action(coord) for coord, player in state['board'].items() if player == -1]

def get_observations(state: State) -> List[PlayerObservation]:
    # Observations are the same for both players in a perfect information game
    board = state['board']
    observations = []
    for player_id in range(2):
        observation = {}
        for coord, player in board.items():
            if player == player_id:
                observation[coord_to_action(coord)] = 1
            else:
                observation[coord_to_action(coord)] = 0
        observations.append(observation)
    return observations