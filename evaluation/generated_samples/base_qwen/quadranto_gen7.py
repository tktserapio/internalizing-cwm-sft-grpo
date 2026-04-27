import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Helper function to generate a random initial state
def get_initial_state():
    # Randomly place player 0 in the top-left quadrant
    row, col = random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])
    # Randomly place player 1 in the bottom-right quadrant
    opponent_quadrant = random.choice(['Q1', 'Q4'])
    if opponent_quadrant == 'Q1':
        opponent_row, opponent_col = random.choice([(2, 0), (2, 1), (3, 0), (3, 1)])
    else:
        opponent_row, opponent_col = random.choice([(0, 2), (0, 3), (1, 2), (1, 3)])
    return {
        'state': {
            'player_0': {'row': row, 'col': col},
            'player_1': {'row': opponent_row, 'col': opponent_col},
            'turn_count': 0,
            'quadrant': opponent_quadrant
        }
    }

# Function to apply an action to the state
def apply_action(state: State, action: Action) -> State:
    # Get the current player
    current_player = get_current_player(state)
    # Get the current player's position
    player_pos = state['state'][f'player_{current_player}']
    row, col = player_pos['row'], player_pos['col']
    # Update the player's position based on the action
    if action == 'Stay':
        new_pos = {'row': row, 'col': col}
    elif action == 'Up':
        new_pos = {'row': max(0, row - 1), 'col': col}
    elif action == 'Down':
        new_pos = {'row': min(3, row + 1), 'col': col}
    elif action == 'Left':
        new_pos = {'row': row, 'col': max(0, col - 1)}
    elif action == 'Right':
        new_pos = {'row': row, 'col': min(3, col + 1)}
    else:
        raise ValueError(f"Invalid action: {action}")
    # Update the state with the new position
    state['state'][f'player_{current_player}'] = new_pos
    # Check if the game ended
    if new_pos == state['state']['player_1']:
        state['state']['winner'] = f'Player {current_player}'
        state['state']['loser'] = f'Player {1 - current_player}'
        state['state']['reward'] = [1.0, -1.0]
    elif state['state']['turn_count'] >= 20:
        state['state']['winner'] = 'Draw'
        state['state']['loser'] = 'Draw'
        state['state']['reward'] = [0.0, 0.0]
    else:
        state['state']['turn_count'] += 1
    return state

# Function to determine the current player
def get_current_player(state: State) -> int:
    return 0 if state['state']['turn_count'] % 2 == 0 else 1

# Function to get the name of the player
def get_player_name(player_id: int) -> str:
    return f'Player {player_id}'

# Function to get the rewards for the given state
def get_rewards(state: State) -> list[float]:
    return state['state']['reward']

# Function to get the legal actions for the current state
def get_legal_actions(state: State) -> list[Action]:
    current_player = get_current_player(state)
    if state['state']['winner'] != 'Draw':
        return ['Stay']
    else:
        return ['Up', 'Down', 'Left', 'Right', 'Stay']

# Function to get the observations for the current state
def get_observations(state: State) -> list[PlayerObservation]:
    player_0_obs = {
        'my_loc': f'({state["state"]["player_0"]["row"]}, {state["state"]["player_0"]["col"]})',
        'opponent_loc': f'({state["state"]["player_1"]["row"]}, {state["state"]["player_1"]["col"]})',
        'opponent_quadrant': state['state']['quadrant']
    }
    player_1_obs = {
        'my_loc': f'({state["state"]["player_1"]["row"]}, {state["state"]["player_1"]["col"]})',
        'opponent_loc': f'({state["state"]["player_0"]["row"]}, {state["state"]["player_0"]["col"]})',
        'opponent_quadrant': state['state']['quadrant']
    }
    return [player_0_obs, player_1_obs]

# Function to resample history
def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    # This function would need to implement the logic to resample the history.
    # For simplicity, we'll just return a fixed sequence of actions.
    # In a real implementation, this would involve stochastic sampling based on the observed history.
    return ['Right', 'Up', 'Down', 'Left', 'Stay']