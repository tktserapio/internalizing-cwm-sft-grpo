import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import List, Dict, Any

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to initialize the game state
def get_initial_state() -> State:
    # Initial state setup
    deck = ['2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s',
            '5c', '5d', '5h', '5s', '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s',
            '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s', 'tc', 'td', 'th', 'ts',
            'jc', 'jd', 'jh', 'js', 'qc', 'qd', 'qh', 'qs', 'kc', 'kd', 'kh', 'ks']
    random.shuffle(deck)
    state = {
        'deck': deck,
        'upcard': None,
        'dealer': 0,
        'knocked': False,
        'knock_card': 10,
        'player_0_hand': [],
        'player_1_hand': [],
        'player_0_deadwood': 0,
        'player_1_deadwood': 0,
        'phase': 'Draw'
    }
    return state

# Apply an action to the current state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    if action == 'Draw stock':
        new_state['deck'].append(new_state['upcard'])
        new_state['upcard'] = new_state['deck'].pop(0)
        new_state['phase'] = 'Discard'
    elif action == 'Draw upcard':
        new_state['upcard'] = new_state['deck'].pop(0)
        new_state['phase'] = 'Discard'
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        new_state['player_0_hand'].remove(card_to_discard)
        new_state['deck'].append(card_to_discard)
        new_state['phase'] = 'Knock'
    elif action == 'Knock':
        new_state['knocked'] = True
        new_state['phase'] = 'Layoff'
        new_state['player_0_deadwood'] = sum([1 for card in new_state['player_0_hand'] if card not in new_state['player_0_deadwood']])
        new_state['player_1_deadwood'] = sum([1 for card in new_state['player_1_hand'] if card not in new_state['player_1_deadwood']])
    elif action == 'Done':
        new_state['knocked'] = True
        new_state['phase'] = 'Layoff'
        new_state['player_0_deadwood'] = sum([1 for card in new_state['player_0_hand'] if card not in new_state['player_0_deadwood']])
        new_state['player_1_deadwood'] = sum([1 for card in new_state['player_1_hand'] if card not in new_state['player_1_deadwood']])
    elif action == 'Pass':
        new_state['phase'] = 'Layoff'
    else:
        raise ValueError(f"Invalid action: {action}")
    return new_state

# Get the current player
def get_current_player(state: State) -> int:
    return state['dealer']

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards for the current state
def get_rewards(state: State) -> List[float]:
    if state['knocked']:
        return [state['knock_card'] - state['player_0_deadwood'], state['knock_card'] - state['player_1_deadwood']]
    return [0.0, 0.0]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state['phase'] == 'Wall':
        return []
    elif state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Knock':
        return ['Action: ' + card for card in state['player_0_hand']] + ['Knock', 'Done']
    elif state['phase'] == 'Layoff':
        return ['Pass']
    else:
        raise ValueError("Invalid phase")

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    player_0_obs = {
        'deck': state['deck'],
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'knocked': state['knocked'],
        'knock_card': state['knock_card'],
        'player_0_hand': state['player_0_hand'],
        'player_1_hand': state['player_1_hand'],
        'player_0_deadwood': state['player_0_deadwood'],
        'player_1_deadwood': state['player_1_deadwood'],
        'phase': state['phase']
    }
    player_1_obs = {
        'deck': state['deck'],
        'upcard': state['upcard'],
        'dealer': state['dealer'],
        'knocked': state['knocked'],
        'knock_card': state['knock_card'],
        'player_0_hand': state['player_1_hand'],
        'player_1_hand': state['player_0_hand'],
        'player_0_deadwood': state['player_1_deadwood'],
        'player_1_deadwood': state['player_0_deadwood'],
        'phase': state['phase']
    }
    return [player_0_obs, player_1_obs]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    # Placeholder for resampling logic
    # For simplicity, we'll just return a fixed sequence of actions
    # This should be replaced with actual resampling logic
    if player_id == 0:
        return ['Draw stock', 'Action: 2c', 'Knock', 'Done']
    else:
        return ['Draw stock', 'Action: 2c', 'Knock', 'Done']