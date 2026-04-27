import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

import random
from typing import Any, Dict, List, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Helper function to create a random upcard
def create_upcard() -> str:
    return random.choice(list('23456789TJQKA'))

# Helper function to create a random discard card
def create_discard_card(hand: List[str]) -> str:
    return random.choice([card for card in hand if card != 'J'])

# Initial state setup
def get_initial_state() -> State:
    # Standard deck of 52 cards
    deck = ['2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh',
            '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd',
            '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc',
            '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks']
    
    # Shuffle the deck
    random.shuffle(deck)
    
    # Deal the cards
    hand0 = deck[:26]
    hand1 = deck[26:]
    
    # Create the initial state
    state = {
        'phase': 'Draw',
        'upcard': create_upcard(),
        'hand0': hand0,
        'hand1': hand1,
        'knock_card': 10,
        'deadwood0': 0,
        'deadwood1': 0,
        'meld0': [],
        'meld1': []
    }
    
    return state

# Apply an action to the state
def apply_action(state: State, action: Action) -> State:
    new_state = state.copy()
    
    if action == 'Draw stock':
        new_state['upcard'] = create_upcard()
        new_state['hand0'].append(new_state['upcard'])
        new_state['hand1'].append(new_state['upcard'])
        new_state['phase'] = 'Discard'
        return new_state
    
    elif action.startswith('Action: '):
        card_to_discard = action.split(':')[1]
        new_state['hand0'].remove(card_to_discard)
        new_state['hand1'].remove(card_to_discard)
        new_state['phase'] = 'Knock'
        return new_state
    
    elif action == 'Knock':
        new_state['phase'] = 'Knock'
        return new_state
    
    elif action == 'Done':
        new_state['phase'] = 'Knock'
        return new_state
    
    elif action == 'Pass':
        new_state['phase'] = 'Knock'
        return new_state
    
    else:
        raise ValueError(f"Invalid action: {action}")

# Get the current player
def get_current_player(state: State) -> int:
    return 0 if state['phase'] == 'Knock' else 1

# Get the name of the player
def get_player_name(player_id: int) -> str:
    return f"Player {player_id}"

# Get the rewards for the current state
def get_rewards(state: State) -> List[float]:
    if state['phase'] == 'Wall':
        return [0.0, 0.0]
    elif state['phase'] == 'Knock':
        return [0.0, 0.0]
    else:
        return [state['deadwood1'], state['deadwood0']]

# Get the legal actions for the current state
def get_legal_actions(state: State) -> List[Action]:
    if state['phase'] == 'Draw':
        return ['Draw stock', 'Draw upcard']
    elif state['phase'] == 'Knock':
        return ['Knock', 'Done', 'Pass']
    else:
        return []

# Get the observations for the current state
def get_observations(state: State) -> List[PlayerObservation]:
    obs0 = {
        'deadwood': state['deadwood0'],
        'meld': state['meld0'],
        'hand': state['hand0'],
        'upcard': state['upcard'],
        'phase': state['phase']
    }
    obs1 = {
        'deadwood': state['deadwood1'],
        'meld': state['meld1'],
        'hand': state['hand1'],
        'upcard': state['upcard'],
        'phase': state['phase']
    }
    return [obs0, obs1]

# Resample history to generate a valid sequence of actions
def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    if player_id == 0:
        # Player 0's turn
        if obs_action_history[-1][1] == 'Knock':
            # Player 0 just knocked
            return ['Knock', 'Done', 'Pass']
        elif obs_action_history[-1][1] == 'Done':
            # Player 0 just did a knock sequence
            return ['Knock', 'Done', 'Pass']
        elif obs_action_history[-1][1] == 'Pass':
            # Player 0 passed
            return ['Draw stock', 'Draw upcard']
        else:
            # Player 0's turn to draw or discard
            return ['Draw stock', 'Draw upcard', 'Action: {}'.format(create_discard_card(obs_action_history[-1][0]['hand']))]
    else:
        # Player 1's turn
        if obs_action_history[-1][1] == 'Knock':
            # Player 1 just knocked
            return ['Knock', 'Done', 'Pass']
        elif obs_action_history[-1][1] == 'Done':
            # Player 1 just did a knock sequence
            return ['Knock', 'Done', 'Pass']
        elif obs_action_history[-1][1] == 'Pass':
            # Player 1 passed
            return ['Draw stock', 'Draw upcard']
        else:
            # Player 1's turn to draw or discard
            return ['Draw stock', 'Draw upcard', 'Action: {}'.format(create_discard_card(obs_action_history[-1][0]['hand']))]

# Example usage
if __name__ == "__main__":
    state = get_initial_state()
    print("Initial State:", state)
    print("Legal Actions:", get_legal_actions(state))
    print("Current Player:", get_current_player(state))
    print("Player Name:", get_player_name(0))
    print("Rewards:", get_rewards(state))
    print("Observations:", get_observations(state))